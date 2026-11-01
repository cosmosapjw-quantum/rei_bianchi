#!/usr/bin/env python3
"""Independent M-matrix residual enclosure for the original REI MPRK increment.

This is NOT a modification of the original interval map. The local 2x2 and
3x3 Patankar corrector has A_ii=1+sum_j r_{ji}, A_ij=-r_{ij} (i != j),
where all r_{ij}>=0 for every original physical realization. Thus
  A^-1 >= 0; 1^T A=1^T; ||A^-1||_1=1.
For b=-(A-I)p and ANY vector z, delta=A^-1*b implies
  ||delta-z||_1 <= ||b-A*z||_1.
Interval residuals yield componentwise enclosures without trusting
a floating BLAS inverse or its computed residual as exact.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np

BASE=Path(__file__).resolve().parents[2]
P348=BASE/"research/rei_f05_common_parent_increments_20261101/increment_certificate.py"

def load_original():
    sp=importlib.util.spec_from_file_location("rei_original_p348_increment",P348)
    module=importlib.util.module_from_spec(sp);sys.modules[sp.name]=module
    sp.loader.exec_module(module)
    return module

def abs_upper(q):
    return np.maximum(np.abs(q.lo),np.abs(q.hi))

def structural_residual_increment(m,parent,flux,den,dt,nh,nhe,original):
    """Use 1-norm contraction to enclose each original physical MPRK block."""
    if not np.isfinite(dt) or dt<=0:
        raise ValueError("NONPOSITIVE_NATIVE_DURATION")
    if not np.all(np.isfinite(parent.lo)) or np.any(parent.lo<=0):
        raise ValueError("NONPOSITIVE_NATIVE_PARENT")
    if not np.all(np.isfinite(den.lo)) or np.any(den.lo<=0):
        raise ValueError("NONPOSITIVE_NATIVE_MPRK_DENOMINATOR")
    if np.any(~np.isfinite(flux.lo)) or np.any(~np.isfinite(flux.hi)):
        raise ValueError("NONFINITE_NATIVE_FLUX")
    # Every original event_box rate is nonnegative by its production/destruction
    # construction. Unassigned 0 entries are expanded to -minsubnormal by
    # _add_flux/Interval; this is a known signed representation of exact zero.
    # Reject any genuinely negative interval lower or upper, rather than
    # silently truncating a physical rate or relaxing a science gate.
    minsub=np.nextafter(0.0,-np.inf)
    if np.any(flux.lo<minsub) or np.any(flux.hi<0):
        raise ArithmeticError("ORIGINAL_RATE_NONNEGATIVITY_STRUCTURAL_PROOF_FAILED")
    if np.any(flux.lo>flux.hi):
        raise ArithmeticError("INVERTED_NATIVE_FLUX")
    alo,ahi=m._matrix_interval(flux,den,dt)
    lo=np.empty_like(parent.lo);hi=np.empty_like(parent.hi)
    stats=[]
    for sl in (slice(0,2),slice(2,5)):
        k=sl.stop-sl.start
        A_lo,A_hi=alo[:,sl,sl],ahi[:,sl,sl]
        p=m._I(parent.lo[:,sl],parent.hi[:,sl])
        blo,bhi=original.original_matrix_delta_rhs(m,A_lo,A_hi,p)
        Amid=0.5*(A_lo+A_hi); bmid=0.5*(blo+bhi)
        # BLAS computes only arbitrary TRIAL z; validity is completely
        # independent of the accuracy of this solve.
        try:
            z=np.linalg.solve(Amid,bmid[...,None])[...,0]
        except np.linalg.LinAlgError as exc:
            raise ArithmeticError("TRIAL_CENTER_NOT_COMPUTED") from exc
        if not np.all(np.isfinite(z)):
            raise ArithmeticError("TRIAL_CENTER_NONFINITE")
        residuals=[]
        for i in range(k):
            residual=m._I(blo[:,i],bhi[:,i])
            for j in range(k):
                residual=residual-m._I(A_lo[:,i,j],A_hi[:,i,j])*m._I(z[:,j])
            residuals.append(residual)
        rho=np.zeros(z.shape[0])
        for r in residuals:
            rho=np.nextafter(rho+abs_upper(r),np.inf)
        if not np.all(np.isfinite(rho)):
            raise ArithmeticError("RESIDUAL_NORM_NONFINITE")
        lo[:,sl]=np.nextafter(z-rho[:,None],-np.inf)
        hi[:,sl]=np.nextafter(z+rho[:,None],np.inf)
        stats.append({
          "block":"H" if sl.start==0 else "He","certified_nodes":int(len(rho)),
          "nodes":int(len(rho)),"method":"EXACT_PHYSICAL_M_MATRIX_1NORM_RESIDUAL",
          "max_residual_l1_radius":float(np.max(rho)),
          "max_relative_residual_l1_radius":float(np.max(rho/
              np.maximum(np.sum(parent.lo[:,sl],axis=1),np.finfo(float).tiny))),
          "outward_zero_flux_elements":int(np.count_nonzero(flux.lo==minsub))
        })
    dp=m._I(lo,hi)
    h=m._I(dp.lo[:,0],dp.hi[:,0])+m._I(dp.lo[:,1],dp.hi[:,1])
    he=(m._I(dp.lo[:,2],dp.hi[:,2])+m._I(dp.lo[:,3],dp.hi[:,3])
         +m._I(dp.lo[:,4],dp.hi[:,4]))
    if not np.all(original.zero_contained(h)&original.zero_contained(he)):
        raise ArithmeticError("RESIDUAL_CERT_NUCLEI_ZERO_NOT_ENCLOSED")
    return dp,stats

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--lane",choices=load_original().LANES,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    original=load_original()
    original_fn=original.krawczyk_increment
    observed=[]
    def wrapper(m,parent,flux,den,dt,nh,nhe):
        dp,st=structural_residual_increment(m,parent,flux,den,dt,nh,nhe,original)
        observed.extend(st)
        return dp,st
    original.krawczyk_increment=wrapper
    try:
        r=original.run(BASE,a.lane,a.out)
    finally:
        original.krawczyk_increment=original_fn
    for entry in r.get("steps",{}).values():
        if "increment_krawczyk_blocks" in entry:
            entry["independent_residual_blocks"]=entry.pop("increment_krawczyk_blocks")
    r["original_native_krawczyk_still_used"]=True
    original_gate_pass=(r.get("status")=="SCOPED_SOURCE_REAL_F05_INCREMENT_GATE_CANDIDATE_PASS")
    r["status"]=("SCOPED_SOURCE_REAL_F05_M_MATRIX_RESIDUAL_GATE_CANDIDATE_PASS"
       if original_gate_pass else "SCOPED_SOURCE_REAL_F05_M_MATRIX_RESIDUAL_HOLD")
    r["independent_certification_method"]="M_MATRIX_1NORM_RESIDUAL_NO_BLAS_INVERSE_VALIDITY_DEPENDENCE"
    r["independent_certifier_status"]="EXPLORATORY_NOT_OWNER_ADMISSION"
    r["structural_residual_block_stats"]=observed
    r["original_accepted_tick"]="160/131072"
    r["canonical_delta"]=0
    (a.out/"RESULT.json").write_text(json.dumps(r,indent=2,sort_keys=True,default=str)+"\n")
    print(json.dumps({"method":r["independent_certification_method"],"status":r["status"],
       "channel_max":{k:v["max_correlated_increment_defect_upper"]
       for k,v in r.get("increment_defect_coordinates",{}).items()},
       "all_original_four_below_gate":r.get("all_original_4_channel_local_defects_below_gate"),
       "stats":observed,"canonical_delta":0},sort_keys=True),flush=True)
if __name__=="__main__":
    main()
