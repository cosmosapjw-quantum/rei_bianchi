"""Matched source-I/O wall-time comparison: sequential vs two independent processes.

Only reads frozen source histories. No source solver execution or modification.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import statistics

def execute(script, history, dest):
    return subprocess.run([sys.executable,str(script),"--history",str(history),
                           "--out",str(dest),"--reps","1"],
                          stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,
                          check=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--history",type=Path,action="append",required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if len(args.history)!=2:
        p.error("Requires exactly two independent histories")
    script=Path(__file__).with_name("cold_history_tau.py")
    measurements={}
    with tempfile.TemporaryDirectory(prefix="axbi_tau_perf_") as tmp:
        tmp=Path(tmp)
        for mode in ("sequential","parallel","parallel","sequential"):
            index=len(measurements.get(mode,[]))
            folder=tmp/(mode+str(index))
            folder.mkdir()
            start=time.perf_counter()
            if mode=="sequential":
                for h in args.history:
                    execute(script,h,folder)
            else:
                with ThreadPoolExecutor(max_workers=2) as pool:
                    futures=[pool.submit(execute,script,h,folder) for h in args.history]
                    for f in futures:f.result()
            measurements.setdefault(mode,[]).append(time.perf_counter()-start)
    report={"schema":"axbi.he18.perf.v1",
            "histories":[str(p) for p in args.history],
            "steps":"source CSV SHA256 + read + census + tau and samples; external process overhead included",
            "sequential_seconds":measurements["sequential"],
            "parallel_two_workers_seconds":measurements["parallel"],
            "median_sequential_seconds":statistics.median(measurements["sequential"]),
            "median_parallel_seconds":statistics.median(measurements["parallel"])}
    report["observed_speed_ratio"]=report["median_sequential_seconds"]/report["median_parallel_seconds"]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

if __name__=="__main__":main()
