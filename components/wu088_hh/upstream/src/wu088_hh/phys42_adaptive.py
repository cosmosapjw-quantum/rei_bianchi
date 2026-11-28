"""PHYS42 adaptive signed interval coupling with deterministic positive-cell heap.

The heap chooses computational effort only, never the validity of the bound:
each leaf has a mathematical interval certificate and covers a rational
angular partition. Whenever splitting a cell, the previous complete
partition remains a valid alternative. Return the smallest certified
partition sum encountered, not an unproved monotone estimate.
"""
from __future__ import annotations
from fractions import Fraction as F
from heapq import heappop,heappush
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from time import perf_counter

from .phys33_residual import load_frozen,dyadic,ceil_sqrt_fixed
from .phys33_coupled_source import outward_decimal
from .phys42_joint_interval import (
    R,prepare_radial_panel,_radial_ranges,certify_cell,
)

SCHEMA="WU088_HH_PHYS42_ADAPTIVE_SIGNED_ANGULAR_INTERVAL_V1"


def _adaptive_one(job:tuple)->dict:
    source,j,ra,rb,seed,target=job
    prep=prepare_radial_panel(source,j)
    rad=_radial_ranges(prep,ra,rb)
    heap=[]
    s=0
    total=F(0)
    for k in range(seed):
        a=-F(1)+F(2*k,seed)
        b=-F(1)+F(2*(k+1),seed)
        q=certify_cell(prep,ra,rb,a,b,rad)["_sq_exact"]
        heappush(heap,(-q,s,a,b,q))
        s+=1
        total+=q
    best=total
    best_count=len(heap)
    best_partition=sorted((a,b,q) for _,_,a,b,q in heap)
    while len(heap)<target:
        negative,_,a,b,old=heappop(heap)
        m=(a+b)/2
        left=certify_cell(prep,ra,rb,a,m,rad)["_sq_exact"]
        right=certify_cell(prep,ra,rb,m,b,rad)["_sq_exact"]
        total+=left+right-old
        heappush(heap,(-left,s,a,m,left));s+=1
        heappush(heap,(-right,s,m,b,right));s+=1
        if total<best:
            best=total
            best_count=len(heap)
            best_partition=sorted((a,b,q) for _,_,a,b,q in heap)
    # Conservation of angular measure of the *final* actual partition
    intervals=sorted((a,b) for _,_,a,b,_ in heap)
    assert intervals[0][0]==-F(1) and intervals[-1][1]==F(1)
    assert all(v[1]==w[0] for v,w in zip(intervals,intervals[1:]))
    assert sum((q for _,_,_,_,q in heap),F(0))==total
    return {
        "panel":j,"radial_interval_a0":[str(ra),str(rb)],
        "source_sha256":prep["source_sha256"],
        "angular_target":target,
        "angular_seeds":seed,
        "final_partition_cells":len(heap),
        "best_partition_cells":best_count,
        "best_exact_sq":str(best),
        "best_sq_decimal":outward_decimal(best,18,True),
        "last_exact_sq":str(total),
        "last_sq_decimal":outward_decimal(total,18,True),
        "best_rational_partition":[[str(a),str(b),str(q)]
                                   for a,b,q in best_partition],
        "split_count":target-seed,
        "final_rational_partition":[[str(a),str(b)] for a,b in intervals],
    }


def adaptive_strip(filename:str|Path,center:F,delta:F,radial_bins:int=4,
                   initial_mu_bins:int=8,target_mu_bins:int=96,
                   workers:int=1,digits:int=12)->dict:
    if not isinstance(center,F) or not isinstance(delta,F) or not center>delta>0:
        raise ValueError("positive exact Fraction input")
    if not 1<=radial_bins<=128 or not 4<=initial_mu_bins<=target_mu_bins<=1024:
        raise ValueError("bounded radial and adaptive angular budgets")
    if workers not in (1,2,3,4,6):
        raise ValueError("bounded safe 1..6 process counts")
    t=perf_counter()
    rr,_,sha=load_frozen(filename,True)
    a,b=center-delta,center+delta
    if a<=R<=b:raise ValueError("cusp requires PHYS38 log strip certificate")
    js=[j for j in range(6) if dyadic(rr[j,0])<=a and b<=dyadic(rr[j,-1])]
    if len(js)!=1:raise ValueError("one actual frozen radial panel required")
    rcuts=[a+(b-a)*F(k,radial_bins) for k in range(radial_bins+1)]
    jobs=[(str(filename),js[0],ra,rb,initial_mu_bins,target_mu_bins)
          for ra,rb in zip(rcuts,rcuts[1:])]
    if workers==1:
        rows=list(map(_adaptive_one,jobs))
    else:
        with ProcessPoolExecutor(max_workers=workers,
                                 mp_context=get_context("forkserver")) as pool:
            rows=list(pool.map(_adaptive_one,jobs))
    if any(x["source_sha256"]!=sha for x in rows):
        raise ArithmeticError("original source mismatch")
    sq=sum((F(x["best_exact_sq"]) for x in rows),F(0))
    return {
        "schema":SCHEMA,"source_sha256":sha,
        "center_a0":str(center),"delta_a0":str(delta),
        "physical_domain_a0":[str(a),str(b)],
        "actual_panel":js[0],"radial_bins":radial_bins,
        "initial_mu_bins":initial_mu_bins,"target_mu_bins":target_mu_bins,
        "workers":workers,"final_partition_cells":radial_bins*target_mu_bins,
        "evaluated_exact_cell_certifications":
            radial_bins*(initial_mu_bins+2*(target_mu_bins-initial_mu_bins)),
        "certified_signed_broken_L2_upper":ceil_sqrt_fixed(sq,digits),
        "proof":"positive exact r² dr dmu/2 tiling, each signed original PDE interval; minimum over complete historical validated partitions",
        "radial_partitions":rows,
        "elapsed_s":perf_counter()-t,
        "unresolved":["origin","exterior","distributional interface sheets",
                      "continuous outgoing low-Schur inverse",
                      "incoming adjoint/scattering intensity and HH thermal rate"],
    }
