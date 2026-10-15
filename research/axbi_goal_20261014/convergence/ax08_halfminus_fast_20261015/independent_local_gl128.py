#!/usr/bin/env python3
"""Independent local-current-angle GL128 versus CAS rational Taylor candidate.

Reads actual source-locked completed minus b(t) at 1/39 stride.
This is a source-free background kernel test, NOT AX11 coupled solver error.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

ENERGY_COEFF=np.array([
 8/5,-16/21,8/35,16/231,4528/32175,-2656/15015,-254248/3828825,
 25107568/183324141,10458544/195859125,-644335456/5547967425,-732698224/17375502375,4574816/46334673,1570056394912/45853950767625
],float)
QUAD_COEFF=np.array([
 -8/5,8/7,-16/35,-40/231,-4528/10725,1328/2145,1016992/3828825,
 -12553784/20369349,-10458544/39171825,322167728/504360675,1465396448/5791834125,-29736304/46334673,-1570056394912/6550564395375,13886441783391392/21890676096464175
],float)
def digest(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""):
   h.update(chunk)
 return h.hexdigest()

def horner(x,coeff):
 out=np.zeros_like(x)
 for c in coeff[::-1]:
  out=out*x+c
 return out

def analytical_series(b):
 return b*b*horner(b,ENERGY_COEFF), b*horner(b,QUAD_COEFF)

def numerical_gl(b,order=128):
 # current-sky mu, NOT legacy initial mu.
 mu,weights=np.polynomial.legendre.leggauss(order)
 weights=weights/2
 mu2=mu*mu
 p2=(3*mu2-1)/2
 ecorr=[];quad=[]
 for i in range(0,len(b),512):
  block=b[i:i+512,None]
  delta=(1-mu2[None,:])*np.expm1(-2*block)+mu2[None,:]*np.expm1(4*block)
  z=np.expm1(-2*np.log1p(delta))
  ecorr.append(z@weights)
  quad.append((1+z)@(weights*p2))
 return np.concatenate(ecorr),np.concatenate(quad)

def check(owner):
 rel=Path("research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_MINUS_composed_001")
 hist=owner/rel/"history.csv"
 receipt=json.loads((owner/rel/"COMPOSITION_RECEIPT.json").read_text())
 assert receipt["status"]=="COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION"
 assert receipt["row_counts"]["history.csv"]["composed_rows"]==312238
 assert digest(hist)==receipt["output_sha256"]["history.csv"]
 b=np.loadtxt(hist,delimiter=",",skiprows=1,usecols=(6,),dtype=np.float64)[::39]
 assert len(b)==8007 and np.all(np.isfinite(b)) and np.max(abs(b))<.025
 e0,q0=analytical_series(b)
 e1,q1=numerical_gl(b,128)
 err_e=float(np.max(np.abs(e1-e0)))
 err_q=float(np.max(np.abs(q1-q0)))
 if err_e>2e-13 or err_q>2e-13:
  raise AssertionError(f"FULL_REAL_HISTORY_GL128_SHEAR_MISMATCH:{err_e},{err_q}")
 # All exact unit-free source-free scalar moments also have their FLRW limit.
 e_zero,q_zero=analytical_series(np.zeros(4))
 assert np.array_equal(e_zero,np.zeros(4)) and np.array_equal(q_zero,np.zeros(4))
 return {
  "schema":"rei.axbi.halfminus_fast_independent_gl128.v1",
  "status":"PASS_CURRENT_LOCAL_GL128_VS_SERIES14_ON_REAL_MINUS",
  "source_header":"actual immutable SHA-bound SHEAR_MINUS composed history; b column",
  "science_input_sha256":digest(hist),
  "sample_stride":39,
  "n_real_states":len(b),
  "max_abs_b":float(np.max(abs(b))),
  "max_abs_energy_ratio_correction_difference":err_e,
  "max_abs_P2_ratio_difference":err_q,
  "flrw_exact_zero":True,
  "prerequisite":"initially isotropic source-free radiation",
  "scientific_admission":"NOT_ISSUED"
 }

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--owner-root",type=Path,required=True)
 args=p.parse_args()
 receipt=check(args.owner_root)
 out=Path(__file__).resolve().parent/"results"/"independent_gl128.json"
 out.write_text(json.dumps(receipt,indent=2)+"\n")
 print(json.dumps(receipt,indent=2))
