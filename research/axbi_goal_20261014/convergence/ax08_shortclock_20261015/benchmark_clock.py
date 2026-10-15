#!/usr/bin/env python3
"""Matched-accuracy AX08 actual source interval benchmark: scalar vs batched GL4.

Original full saved q=-.01 already completed, 312238 states. Per-interval
proper-time/shear values are the same physical GL4 source evaluator.
No source RT solver, no fusion with AX03 production AX08 native pipeline.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
import time
import numpy as np
from actual_clock_gl4 import load_one
from shortstep import Background,Family,gauss_batch,gauss_increment

HERE=Path(__file__).resolve().parent
def median_benchmark(fn,n=5):
    fn() # warm
    runs=[]
    output=None
    for _ in range(n):
        t=time.perf_counter()
        output=fn()
        runs.append(time.perf_counter()-t)
    return statistics.median(runs),runs,output
def evaluate(owner):
    arr,meta=load_one(owner,"SHEAR_MINUS")
    sampled=arr[np.unique(np.r_[np.arange(0,len(arr),39),len(arr)-1])]
    a=sampled[:,1]
    bg=Background(Family(-.01))
    start,end=a[:-1],a[1:]
    def scalar():
        vals=[gauss_increment(bg,float(x),float(y),order=4) for x,y in zip(start,end)]
        return np.asarray(vals,dtype=float).T
    def grouped():
        return gauss_batch(bg,start,end,order=4)
    def threads2(pool):
        mid=len(start)//2
        chunks=[(start[:mid],end[:mid]),(start[mid:],end[mid:])]
        vals=list(pool.map(lambda pair:gauss_batch(bg,*pair,order=4),chunks))
        return (np.r_[vals[0][0],vals[1][0]],np.r_[vals[0][1],vals[1][1]])
    reference=grouped()
    chk=scalar()
    assert np.allclose(reference[0],chk[0],rtol=5e-13,atol=0)
    assert np.allclose(reference[1],chk[1],rtol=5e-13,atol=1e-20)
    tm_scalar,rs,source=median_benchmark(scalar,5)
    tm_batch,rb,result=median_benchmark(grouped,5)
    assert np.allclose(reference[0],result[0],rtol=0,atol=0)
    with ThreadPoolExecutor(max_workers=2) as pool:
        tm_threads,rt,tres=median_benchmark(lambda:threads2(pool),5)
    assert np.allclose(reference[0],tres[0],rtol=5e-13,atol=0)
    assert np.allclose(reference[1],tres[1],rtol=5e-13,atol=1e-20)
    t_rel=np.max(np.abs(reference[0]-source[0])/reference[0])
    b_rel=np.max(np.abs(reference[1]-source[1])/np.maximum(np.abs(reference[1]),1e-25))
    out={
      "schema":"rei.axbi.real_saved_interval_clock_benchmark.v1",
      "status":"MATCHED_PHYSICAL_GL4_SCALAR_BATCH_THREAD_PARITY_PASS",
      "physics_source":"AX03 C8 PR123 source lock 46f818c2...; original AX08 completed minus geometry",
      "source_history_sha256":meta["source_sha256"],
      "mean_background":"physical density fixed, signed q_ref=-0.01",
      "actual_sampled_states":len(a),
      "actual_intervals":len(start),
      "matched_method":"Gauss-Legendre order4, same interval physical rates H,s; serial Python scalar vs batched NumPy vs two independent interval threads",
      "max_rel_scalar_vs_batch_dt":float(t_rel),
      "max_rel_scalar_vs_batch_db":float(b_rel),
      "median_s":{"scalar":tm_scalar,"batch_1":tm_batch,"batch_2thread":tm_threads},
      "repeat_seconds":{"scalar":rs,"batch_1":rb,"batch_2thread":rt},
      "speedup_scalar_over_batch_1":tm_scalar/tm_batch,
      "speedup_batch_1_over_2thread":tm_batch/tm_threads,
      "recommendation":"BATCH_SINGLE_THREAD" if tm_batch<tm_threads else "BATCH_TWO_THREADS",
      "not_claimed":"whole coupled AX08 astrophysical solver speedup, AX11 energy/angle/time convergence",
      "scientific_admission":"NOT_ISSUED"}
    (HERE/"results/benchmark_clock.json").write_text(json.dumps(out,indent=2)+"\n")
    return out
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--owner-root",type=Path,required=True)
    args=ap.parse_args()
    z=evaluate(args.owner_root)
    print(json.dumps({k:z[k] for k in
      ("status","actual_intervals","max_rel_scalar_vs_batch_dt","max_rel_scalar_vs_batch_db",
       "median_s","speedup_scalar_over_batch_1","speedup_batch_1_over_2thread","recommendation")},indent=2))
