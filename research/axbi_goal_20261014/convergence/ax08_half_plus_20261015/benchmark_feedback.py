#!/usr/bin/env python3
"""Matched-input performance and numerical parity; actual AX08 saved files.
Only analysis kernels, not astrophysical solver, are benchmarked.
"""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import statistics
import subprocess
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
REFERENCE=json.loads((HERE/"feedback_reconstruction.json").read_text())["results"]
RUST="/tmp/rei_ax08_feedback_fast_20261015"
PY=ROOT/"research/axbi_goal_20261014/convergence/ax08_half_plus_20261015/reconstruct_feedback.py"

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def run(mode):
    args=(["python3",str(PY)] if mode=="python_reference" else
          [RUST,str(ROOT)]+(["--serial"] if mode=="rust_serial" else []))
    begin=time.perf_counter()
    cp=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,check=False)
    elapsed=time.perf_counter()-begin
    if cp.returncode!=0:raise RuntimeError(mode+" FAILED "+cp.stderr[-1000:])
    if mode!="python_reference":
        rows=list(csv.DictReader(io.StringIO(cp.stdout)))
        if len(rows)!=2:raise AssertionError("WRONG_CASE_COUNT")
        for row in rows:
            actual=REFERENCE[row["case"]]
            ref={"max_abs_delta_s_over_H": actual["max_abs_delta_s_over_H"]["abs_delta_s_over_H"],
                 "endpoint_delta_s_over_H":actual["endpoint"]["total_delta_s_over_H"],
                 "max_extra_energy_ratio":actual["max_abs_extra_energy_ratio"]["abs_ratio"],
                 "endpoint_effective_rad_delta_s_over_H":actual["endpoint"]["effective_radiation_delta_s_over_H"],
                 "endpoint_ionizing_delta_s_over_H":actual["endpoint"]["ionizing_delta_s_over_H"]}
            for key,value in ref.items():
                calculated=float(row[key])
                if abs(value-calculated)>max(1e-25,1e-12*abs(value)):
                    raise AssertionError(f"SCIENTIFIC_MISMATCH:{row['case']}:{key}:{value}:{calculated}")
            if int(row["rows"])!=312238:raise AssertionError("ROW_COUNT")
    return elapsed

if __name__=="__main__":
    timings={}
    for mode in ("python_reference","rust_serial","rust_parallel"):
        timings[mode]=[run(mode) for _ in range(3)]
    med={k:statistics.median(v) for k,v in timings.items()}
    inputs={
      case:{"path":value["source_feedback_path"],"sha256":sha(ROOT/value["source_feedback_path"])}
      for case,value in REFERENCE.items()
    }
    output={"schema":"rei.axbi.real_feedback_benchmark.v1",
            "status":"PASS_MATCHED_SAVED_DATA_NUMERICAL_PARITY",
            "kernel":"stored feedback reconstruction, 312238 rows per actual case, 2 cases",
            "timings_s":timings,"median_s":med,
            "python_to_rust_parallel_speedup":med["python_reference"]/med["rust_parallel"],
            "rust_serial_over_parallel_ratio":med["rust_serial"]/med["rust_parallel"],
            "compilers":subprocess.run(["rustc","--version"],capture_output=True,text=True).stdout.strip(),
            "input":inputs,"rust_source_sha256":sha(HERE/"feedback_fast.rs"),
            "scientific_admission":"NOT_ISSUED",
            "scope":"No evolution solver, no numerical resolution certification, no throughput extrapolation beyond these two files."
    }
    (HERE/"feedback_benchmark.json").write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps({k:output[k] for k in ("status","median_s","python_to_rust_parallel_speedup","rust_serial_over_parallel_ratio")},indent=2))
