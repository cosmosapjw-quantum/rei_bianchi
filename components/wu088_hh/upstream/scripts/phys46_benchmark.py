#!/usr/bin/env python3
"""PHYS46 exact rational radial energy envelope search vs selected T=31 microbench."""
from __future__ import annotations
import argparse,copy,json,statistics,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys46_volterra import finite21_volterra_certificate


def runs(frozen,patches,workers,iterations):
    arr=[]
    ref=None
    for _ in range(iterations):
        a=time.perf_counter()
        x=finite21_volterra_certificate(frozen,candidate_T=patches,workers=workers)
        dur=time.perf_counter()-a
        if ref is None:
            ref=x
        else:
            y=copy.deepcopy(x);z=copy.deepcopy(ref)
            for w in (y,z):
                w.pop("workers");w.pop("elapsed_s")
            if y!=z:raise ArithmeticError("same science differs by repeated execution")
        arr.append(dur)
    return arr,ref


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--reps",type=int,default=30)
    a=p.parse_args()
    if not 3<=a.reps<=250:raise ValueError("bounded benchmark repeats")
    cases=[("search_all_12_serial",tuple(range(29,41)),1,a.reps),
           ("accepted_T31_serial",(31,),1,a.reps),
           ("all_12_two_worker",tuple(range(29,41)),2,3)]
    results={}
    reference=None
    for name,patch,w,n in cases:
        times,x=runs(a.source,patch,w,n)
        results[name]={"workers":w,"T_candidates":list(patch),"repeats":n,
            "median_wall_s":statistics.median(times),"all_times_s":times,
            "scoped_result_q_upper":x["selected_q_strict_upper"]}
        if reference is None:reference=x
        else:
            assert x["selected_q_strict_upper"]==reference["selected_q_strict_upper"]
            assert x["T_energy_patch_a0"]==31
            assert x["M_state_bound_integer"]==28
    p1=results["search_all_12_serial"]["median_wall_s"]
    p2=results["accepted_T31_serial"]["median_wall_s"]
    result={"schema":"WU088_HH_PHYS46_EXACT_RATIONAL_CPU_BENCH_V1",
            "source_SHA":reference["source_sha256"],
            "same_science_all_modes_exact_rational":True,
            "global_certified_optimum_patch_T":31,
            "global_certified_optimum_M":28,
            "scoped_q_upper":reference["selected_q_strict_upper"],
            "cases":results,
            "cold_search_over_locked_patch_speedup":p1/p2,
            "batch_CPU_comment":"12-candidate discovery vs one already-proven optimal T; 2-worker startup can dominate this tiny exact-rational kernel; no REI solver claim"}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"speedup_search_vs_locked":result["cold_search_over_locked_patch_speedup"],
        "medians":{k:v["median_wall_s"] for k,v in results.items()},
        "original_source_SHA":result["source_SHA"],"result":str(a.out)}))
if __name__=="__main__":main()
