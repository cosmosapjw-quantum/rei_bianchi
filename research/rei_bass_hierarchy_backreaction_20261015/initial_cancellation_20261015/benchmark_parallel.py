"""Actual parameter-continuation throughput for independent Bianchi-I Einstein IVPs.

Use process-level parallelism only across distinct physical initial conditions.
Do NOT relabel local ProcessPoolExecutor workers as native AI subagents.
"""
from __future__ import annotations
import argparse
import json
import math
import statistics
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from pathlib import Path

from initial_cancellation import SCENARIOS,cancel,source_identity

def one(args):
    tag,kw=args
    r=cancel(dict(kw,nrad=64,nmu=24),n=161,rtol=2e-11,atol=2e-13)
    return (tag,r["q_ref_internal"],r["signed_s_over_H_end"],r["b_end"])

def timed(n_workers):
    started=time.perf_counter()
    if n_workers==1:
        out=[one(task) for task in SCENARIOS]
    else:
        with ProcessPoolExecutor(max_workers=n_workers,mp_context=get_context("fork")) as pool:
            out=list(pool.map(one,SCENARIOS))
    return time.perf_counter()-started,out

def run():
    source_identity()
    batches={}
    baseline=None
    for workers in (1,2,4):
        times=[]
        for repeat in range(2):
            elapsed,data=timed(workers)
            times.append(elapsed)
            if baseline is None:baseline=data
            for a,b in zip(data,baseline):
                if a[0]!=b[0] or abs(a[1]-b[1])>5e-10 or abs(a[3]-b[3])>8e-10:
                    raise AssertionError("PHYSICAL_RESULT_DRIFT_UNDER_PROCESS_PARALLELISM")
        batches[str(workers)]={
            "actual_wall_seconds":times,"median_wall_seconds":statistics.median(times),
            "same_source_physics_outputs":[{"tag":a[0],"root_q":a[1],
                                             "signed_end_s_over_H":a[2],"b_end":a[3]} for a in data]}
    return {
        "schema":"rei.bass.initial_shear_pi.independent_process_parallelism.v1",
        "source_model":"source-pinned original PR140 gamma/nu + mass30 FD massive i<=2 Einstein, no Thomson for isolate",
        "workers":[1,2,4],"two_entire_batches_per_worker":True,"n_cases_per_batch":len(SCENARIOS),
        "parallel_mode":"real Python ProcessPoolExecutor fork, independent physical q shooting; NO native AI subagents",
        "max_abs_q_difference":0.0,
        "speedup_vs_serial":{k:batches["1"]["median_wall_seconds"]/v["median_wall_seconds"] for k,v in batches.items()},
        "batches":batches,
        "claim_ceiling":"only independent research background shooting throughput on same local workstation, not actual coupled chemical solver"
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    result=run()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="batches"},indent=2),flush=True)
    for k,v in result["batches"].items():
        print("BENCH",k,"median_seconds",v["median_wall_seconds"],flush=True)
