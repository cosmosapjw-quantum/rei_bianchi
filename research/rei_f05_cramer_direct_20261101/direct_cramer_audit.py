#!/usr/bin/env python3
"""REI original F05 tick160 independent 2x2/3x3 direct-determinant interval audit.
Only new math is interval Cramer's rule, no BLAS inverse or original worker edits.
One user-source original MPRK/SDIRK run, frozen tolerances, 3 identical-source shape lanes.
The inherited directed-rounding interval arithmetic remains a numerical trust base.
"""
from __future__ import annotations
import argparse, importlib.util, json, sys
from itertools import permutations
from pathlib import Path
import numpy as np

def load(path):
    spec=importlib.util.spec_from_file_location("f05_original_increment_for_direct",path)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return mod

def sign(p):
    return -1 if sum(p[i]>p[j] for i in range(len(p)) for j in range(i+1,len(p)))%2 else 1

def det_interval(a,zero):
    k=len(a)
    s=zero
    for perm in permutations(range(k)):
        t=a[0][perm[0]]
        for i in range(1,k):
            t=t*a[i][perm[i]]
        s=s+t if sign(perm)>0 else s-t
    return s

def make_solver(reference):
    def cramer_increment(m,parent,flux,den,dt,nh,nhe):
        a_lo,a_hi=m._matrix_interval(flux,den,dt)
        lo=np.empty_like(parent.lo)
        hi=np.empty_like(parent.hi)
        stats=[]
        for sl in (slice(0,2),slice(2,5)):
            n,k,_=a_lo[:,sl,sl].shape
            p=m._I(parent.lo[:,sl],parent.hi[:,sl])
            rlo,rhi=reference.original_matrix_delta_rhs(
                m,a_lo[:,sl,sl],a_hi[:,sl,sl],p)
            A=[[m._I(a_lo[:,sl,sl][:,i,j],a_hi[:,sl,sl][:,i,j])
                for j in range(k)] for i in range(k)]
            b=[m._I(rlo[:,i],rhi[:,i]) for i in range(k)]
            zero=m._I(np.zeros(n))
            denominator=det_interval(A,zero)
            positives=np.asarray(denominator.lo)>0.0
            count=int(np.count_nonzero(positives))
            if count!=n:
                raise ArithmeticError(f"DIRECT_CRAMER_DETERMINANT_NOT_POSITIVE_{sl.start}:{n-count}")
            for j in range(k):
                Aj=[[b[i] if col==j else A[i][col] for col in range(k)] for i in range(k)]
                q=det_interval(Aj,zero)/denominator
                lo[:,sl.start+j]=q.lo
                hi[:,sl.start+j]=q.hi
            stats.append({
                "block":"H" if sl.start==0 else "He",
                "method":"INTERVAL_CRAMER_IEEE754_NEXTAFTER",
                "determinant_positive_nodes":count,
                "nodes":n,
                "min_det_lower":float(np.min(denominator.lo)),
                "max_component_width":float(np.max(hi[:,sl]-lo[:,sl]))})
        dp=m._I(lo,hi)
        h=m._I(dp.lo[:,0],dp.hi[:,0])+m._I(dp.lo[:,1],dp.hi[:,1])
        he=(m._I(dp.lo[:,2],dp.hi[:,2])
            +m._I(dp.lo[:,3],dp.hi[:,3])
            +m._I(dp.lo[:,4],dp.hi[:,4]))
        if not np.all(reference.zero_contained(h)&reference.zero_contained(he)):
            raise ValueError("DIRECT_CRAMER_NUCLEI_RESIDUAL_NOT_ZERO_ENCLOSED")
        return dp,stats
    return cramer_increment

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,required=True)
    p.add_argument("--lane",required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    repo=args.repo.resolve()
    original=load(repo/"research/rei_f05_common_parent_increments_20261101/increment_certificate.py")
    if args.lane not in original.LANES:
        raise SystemExit("INVALID_ORIGINAL_LANE")
    original.krawczyk_increment=make_solver(original)
    result=original.run(repo,args.lane,args.out)
    for stage in result.get("steps",{}).values():
        if "increment_krawczyk_blocks" in stage:
            stage["independent_interval_cramer_blocks"]=stage.pop("increment_krawczyk_blocks")
    result["independent_linear_method"]="INTERVAL_CRAMER_2x2_3x3_NO_BLAS_INVERSION"
    result["arithmetic_trust"]="INHERITED_IEEE754_NEXTAFTER_NOT_FORMAL_MPFR"
    result["original_native_worker_modified"]=False
    result["original_canonical_tick161"]="NOT_ACCEPTED"
    result["canonical_delta"]=0
    result["production"]="HOLD"
    (args.out/"RESULT.json").write_text(json.dumps(result,indent=2,sort_keys=True,default=str)+"\n")
    print(json.dumps({"status":result.get("status"),"lane":args.lane,
        "four_channel_gate":result.get("all_original_4_channel_local_defects_below_gate"),
        "physics_rows":result.get("source_derived_model_rows",0),
        "max_logT_upper":result.get("increment_defect_coordinates",{}).get("log_T",{}).get("max_correlated_increment_defect_upper"),
        "original_set_ledgers":result.get("original_set_ledgers",{}),
        "original_canonical_tick161":"NOT_ACCEPTED"},sort_keys=True),flush=True)

if __name__=="__main__":
    main()