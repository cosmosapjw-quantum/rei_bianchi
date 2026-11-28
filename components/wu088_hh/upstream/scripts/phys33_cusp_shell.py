#!/usr/bin/env python3
"""Run fixed-r=R source-coupled angular cusp-shell certificate, one-sided."""
from pathlib import Path
import argparse,json,sys,hashlib,time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context, get_all_start_methods
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys33_cusp_shell import shell_certificate

def _worker(job):
    return shell_certificate(*job)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--side",choices=["left","right","both"],required=True)
    p.add_argument("--workers",type=int,choices=[1,2],default=2)
    p.add_argument("--order",type=int,default=112)
    p.add_argument("--digits",type=int,default=12)
    p.add_argument("--input",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    start=time.perf_counter()
    jobs=[(args.input,side,args.order,args.digits)
          for side in (["left","right"] if args.side=="both" else [args.side])]
    if args.workers==1 or len(jobs)==1:
        entries=[_worker(job) for job in jobs]
    else:
        method="forkserver" if "forkserver" in get_all_start_methods() else "spawn"
        with ProcessPoolExecutor(max_workers=2,mp_context=get_context(method)) as pool:
            entries=list(pool.map(_worker,jobs))
    r={"schema":"WU088_HH_PHYS37_BOTH_RADIAL_TRACES_V1",
       "input_sha256":entries[0]["source_sha256"],
       "order":args.order,"digits":args.digits,
       "results":entries,"elapsed_s":time.perf_counter()-start}
    r["module_sha256"]=hashlib.sha256((ROOT/"src/wu088_hh/phys33_cusp_shell.py").read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x") as f: json.dump(r,f,indent=2);f.write("\n")
    print(json.dumps(r))
if __name__=="__main__":main()
