#!/usr/bin/env python3
"""Actual saved Bianchi-I q=-.01 and +.005 source-free radiation moment shapes.

No coupling to ionizing photon source or ODE runtime. SHA-bound saved history.
"""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from independent_local_gl128 import analytical_series
BASE=Path("research/axbi_goal_20261014/runs/paired/32d11e733155")
INPUTS={"SHEAR_MINUS":"SHEAR_MINUS_composed_001",
        "SHEAR_HALF_PLUS":"SHEAR_HALF_PLUS_composed_002"}
def digest(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""):
   h.update(chunk)
 return h.hexdigest()
def main(root):
 histories={}
 for label,rel in INPUTS.items():
  d=root/BASE/rel
  r=json.loads((d/"COMPOSITION_RECEIPT.json").read_text())
  assert r["status"]=="COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION"
  assert r["row_counts"]["history.csv"]["composed_rows"]==312238
  hist=d/"history.csv"
  assert digest(hist)==r["output_sha256"]["history.csv"]
  source=np.loadtxt(hist,delimiter=",",skiprows=1,usecols=(5,6),dtype=np.float64)[::110]
  z,b=source.T
  assert np.all(np.isfinite(z)) and np.max(np.abs(b))<.025
  e,q=analytical_series(b)
  histories[label]=(z,e,q)
 fig,(ax0,ax1)=plt.subplots(2,1,figsize=(9,7.4),constrained_layout=True)
 for label,(z,e,q) in histories.items():
  ax0.plot(z,e,label=label)
  ax1.plot(z,q,label=label)
 for ax in (ax0,ax1):
  ax.set_xlabel("Mean redshift (source reference)")
  ax.invert_xaxis()
  ax.grid(alpha=.25)
  ax.legend(fontsize=8)
 ax0.set_ylabel(r"$(\rho_{r}/\rho_{\mathrm{iso}})-1$")
 ax1.set_ylabel(r"$\Delta P_{r}/\rho_{\mathrm{iso}}$")
 ax0.set_title("Source-free initially isotropic background: scalar energy correction")
 ax1.set_title("Source-free normalized radiation quadrupole: signed leading response")
 fig.suptitle("AX08 actual frozen Bianchi-I geometry; Taylor14 analytic moments, NOT ionizing radiation")
 out=Path(__file__).resolve().parent/"results"/"real_saved_shear_moments.png"
 fig.savefig(out,dpi=185)
 plt.close(fig)
 return str(out)
if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--owner-root",type=Path,required=True)
 args=ap.parse_args()
 print(main(args.owner_root))
