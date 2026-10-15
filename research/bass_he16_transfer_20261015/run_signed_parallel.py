"""Bounded parallel, source-scoped, read-only signed-prefix diagnostics.

Distinct processes are data-parallel, NOT native model subagents or solver workers.
"""
from concurrent.futures import ThreadPoolExecutor
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from signed_prefix_tau import EXPECTED_Q

CASES=("SHEAR_MINUS","SHEAR_HALF_MINUS","ZERO","SHEAR_HALF_PLUS","SHEAR_PLUS")

def history_path(root,case):
    return root/("flrw" if case=="ZERO" else "paired")/"32d11e733155"/case/"history.csv"

def run_source(case,root,out_dir):
    out=out_dir/(case+".json")
    cmd=[sys.executable,str(Path(__file__).with_name("signed_prefix_tau.py")),
         "single","--history",str(history_path(root,case)),"--out",str(out)]
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",OPENBLAS_NUM_THREADS="1")
    started=time.perf_counter()
    result=subprocess.run(cmd,env=env,text=True,capture_output=True)
    if result.returncode!=0:
        raise RuntimeError(f"{case} exit {result.returncode}: {result.stderr[-800:]}")
    return {"case":case,"exit":result.returncode,"elapsed_s":time.perf_counter()-started,
            "output":out.name}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    p.add_argument("--jobs",type=int,default=2)
    args=p.parse_args()
    if not 1<=args.jobs<=5:p.error("--jobs must be 1..5")
    args.out_dir.mkdir(parents=True,exist_ok=True)
    begin=time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures=[executor.submit(run_source,case,args.root,args.out_dir) for case in CASES]
        results=[f.result() for f in futures]
    result={
        "schema":"he18.axbi.signed_prefix_parallel.v1",
        "jobs":args.jobs,"completed_cases":len(results),
        "elapsed_wall_s":time.perf_counter()-begin,
        "children":results,
        "status":"READ_ONLY_SOURCE_SCOPED_SUCCESS",
        "model_subagents":"NOT_RUN"
    }
    (args.out_dir/"PARALLEL_EXECUTION.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":
    main()
