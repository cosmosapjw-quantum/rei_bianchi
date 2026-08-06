#!/usr/bin/env python3
"""Build Verner gray-opacity and optical-depth-dependent heating moments."""
from __future__ import annotations
import argparse, importlib.util, json, math, sys
from pathlib import Path
import numpy as np
import pandas as pd
from numpy.polynomial.legendre import leggauss

GROUPS={"G1":(13.6,24.59),"G2a":(24.59,39.5),"G2b":(39.5,54.42),"G3":(54.42,100.0)}
THRESH={"HI":13.6,"HeI":24.59,"HeII":54.42}
SUPPORT={"HI":{"G1","G2a","G2b","G3"},"HeI":{"G2a","G2b","G3"},"HeII":{"G3"}}
TAU_GRID=[0.0,1e-6,1e-4,1e-2,0.1,1.0,10.0,100.0,math.inf]


def load_module(path:Path):
    sys.path.insert(0,str(path.parent))
    spec=importlib.util.spec_from_file_location("r1b_r1_multigroup",path)
    mod=importlib.util.module_from_spec(spec); sys.modules[spec.name]=mod; spec.loader.exec_module(mod); return mod


def quadrature(lo:float,hi:float,n:int=512):
    x,w=leggauss(n); e=0.5*(hi-lo)*x+0.5*(hi+lo); return e,0.5*(hi-lo)*w


def compute(mod,species,group,n=512):
    lo,hi=GROUPS[group]; eth=THRESH[species]
    if group not in SUPPORT[species]:
        return {"supported":False,"gray_sigma_cm2":0.0,"thin_excess_eV":0.0,"thick_excess_eV":0.0,"rows":[{"tau":t,"absorbed_fraction":0.0,"excess_eV":0.0} for t in TAU_GRID]}
    e,w=quadrature(lo,hi,n); phi=e**(-2.5); sig=np.asarray(mod.verner_sigma(species,e),float)
    # Enforce exact threshold zeros rather than relying on roundoff.
    sig=np.where(e>=eth,sig,0.0)
    den_source=float(np.dot(w,phi)); gray=float(np.dot(w,phi*sig)/den_source)
    thin_den=float(np.dot(w,phi*sig)); thin=float(np.dot(w,phi*sig*(e-eth))/thin_den)
    thick_den=float(np.dot(w,phi*(sig>0))); thick=float(np.dot(w,phi*(sig>0)*(e-eth))/thick_den)
    rows=[]
    for tau in TAU_GRID:
        if tau==0.0:
            # Limit tau -> 0: absorption probability proportional to sigma.
            prob=sig/max(gray,1e-300)
        elif math.isinf(tau):
            prob=(sig>0).astype(float)
        else:
            prob=-np.expm1(-tau*sig/max(gray,1e-300))
        denom=float(np.dot(w,phi*prob))
        excess=float(np.dot(w,phi*prob*(e-eth))/denom) if denom>0 else 0.0
        absorbed=float(denom/den_source)
        rows.append({"tau":tau,"absorbed_fraction":absorbed,"excess_eV":excess})
    return {"supported":True,"gray_sigma_cm2":gray,"thin_excess_eV":thin,"thick_excess_eV":thick,"rows":rows}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); a.output.mkdir(parents=True,exist_ok=True)
    mod=load_module(a.source)
    summary=[]; curves=[]; supports=[]
    for s in ("HI","HeI","HeII"):
        for g in GROUPS:
            r=compute(mod,s,g)
            summary.append({"species":s,"group":g,"supported":r['supported'],"gray_sigma_cm2":r['gray_sigma_cm2'],"thin_excess_eV":r['thin_excess_eV'],"thick_excess_eV":r['thick_excess_eV'],"group_lo_eV":GROUPS[g][0],"group_hi_eV":GROUPS[g][1],"threshold_eV":THRESH[s]})
            supports.append({"species":s,"group":g,"support_exact":int(r['supported']),"below_threshold_exact_zero":int(not r['supported'])})
            for row in r['rows']:
                curves.append({"species":s,"group":g,**row})
    sdf=pd.DataFrame(summary); cdf=pd.DataFrame(curves); spdf=pd.DataFrame(supports)
    sdf.to_csv(a.output/'verner_gray_and_limit_moments.csv',index=False)
    cdf.to_csv(a.output/'optical_depth_heating_moments.csv',index=False)
    spdf.to_csv(a.output/'species_group_support_matrix.csv',index=False)
    occ=mod.source_occupation('MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD',n=256)
    (a.output/'primary_group_source_occupation.json').write_text(json.dumps({k:float(v) for k,v in occ.items()},indent=2,sort_keys=True)+'\n')
    supported=sdf[sdf.supported]
    exact_zero=bool((sdf[~sdf.supported][['gray_sigma_cm2','thin_excess_eV','thick_excess_eV']].to_numpy()==0.0).all())
    monotonic=True
    for (s,g),q in cdf.groupby(['species','group']):
        if g not in SUPPORT[s]: continue
        vals=q.excess_eV.to_numpy(); monotonic &= bool(np.all(np.diff(vals)>=-1e-10))
    result={"classification":"ATOMIC_MOMENT_LOCK_SUMMARY","supported_pairs":int(len(supported)),"unsupported_exact_zero":exact_zero,"heating_hardening_monotone":monotonic,"primary_G3_source_occupation_exact_zero":float(occ['G3'])==0.0,"gray_sigma_min_supported_cm2":float(supported.gray_sigma_cm2.min()),"gray_sigma_max_supported_cm2":float(supported.gray_sigma_cm2.max()),"thin_excess_range_eV":[float(supported.thin_excess_eV.min()),float(supported.thin_excess_eV.max())],"thick_excess_range_eV":[float(supported.thick_excess_eV.min()),float(supported.thick_excess_eV.max())]}
    (a.output/'atomic_moment_summary.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n'); print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__': main()
