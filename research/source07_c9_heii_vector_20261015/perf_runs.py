#!/usr/bin/env python3
"""Whole-process repeat benchmark of serial versus 3-worker independent-q evaluation."""
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time

script=Path(__file__).with_name("experiment.py")
output=Path(__file__).with_name("parallel_benchmark.json")
env=dict(os.environ,OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1",MKL_NUM_THREADS="1")
runs={}
with tempfile.TemporaryDirectory(prefix="rei_source07_perf_") as temp:
    for workers in (1,3):
        cases=[]
        for repeat in range(5):
            temp_json=Path(temp)/(f"workers_{workers}_{repeat}.json")
            t0=time.perf_counter()
            cp=subprocess.run([sys.executable,str(script),"--workers",str(workers),
                              "--output",str(temp_json)],
                              stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                              text=True,env=env,check=False)
            elapsed=time.perf_counter()-t0
            if cp.returncode!=0:
                raise RuntimeError(f"run failed workers={workers}: {cp.stderr}")
            data=json.loads(temp_json.read_text())
            cases.append({"wall_s":elapsed,"algorithm_wall_s":data["total_wall_s"],
                          "data":data})
        runs[str(workers)]=cases
    s0=runs["1"][0]["data"]["cases"]
    for count in ("1","3"):
        for trial in runs[count]:
            for left,right in zip(s0,trial["data"]["cases"]):
                assert left["q"] == right["q"]
                assert left["ledger"] == right["ledger"]
                assert left["age_weights"] == right["age_weights"]
                for d in ("1","3","5"):
                    assert left["designs"][d] == right["designs"][d], (
                           d,left["designs"][d],right["designs"][d])
times={k:[trial["wall_s"] for trial in v] for k,v in runs.items()}
algorithm={k:[trial["algorithm_wall_s"] for trial in v] for k,v in runs.items()}
m0=statistics.median(times["1"]); m3=statistics.median(times["3"])
report={"schema":"rei.source07.c9.parallel.whole-process.v1",
        "repeat_count":5,"threads_per_BLAS":1,"q_values":[-.01,0.,.01],
        "whole_process_wall_samples":times,
        "internal_algorithm_wall_samples":algorithm,
        "whole_process_median_s":{"1":m0,"3":m3},
        "whole_process_speedup_serial_over_three_workers":m0/m3,
        "parallel_science_identical":True,
        "scope":"measured standalone three-q frozen-receiver experiment, not production RT runtime"}
output.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
