#!/usr/bin/env python3
"""Matched physical state serial/process-parallel speed for 4 signed C15 cases.

Actual original native MD14 spectral grid, real C11 Case-A, independent
concurrent ProcessPool workers on CPUs 2-4. No parallel sharing of mutable
radiation/chemical states, no native AI subagents.
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
import json
import multiprocessing as mp
from pathlib import Path
import statistics
import time
import numpy as np
from study_c15 import solve,subset

HERE=Path(__file__).resolve().parent
CASE_PARAMS=(
    {"q":0.,"kg":.2,"kn":.2,"nstep":64},
    {"q":.005,"kg":.2,"kn":.2,"nstep":64},
    {"q":-.005,"kg":.2,"kn":.2,"nstep":64},
    {"q":.01,"kg":.2,"kn":.2,"nstep":64},
)
FIELDS=("Sigma_end","b_end","xHII","xHeII","xHeIII","Tgas_K","tau_integrated",
        "gammaE2","nuE2","Pi_CMB_neutrinos_Pa","Pi_UV_Pa","photon_NperH")
def worker(kwargs):
    return subset(solve(**kwargs))
def run_serial():
    return [worker(x) for x in CASE_PARAMS]
def run_processes(pool):
    return list(pool.map(worker,CASE_PARAMS))
def equality(a,b):
    for i,(x,y) in enumerate(zip(a,b)):
        for key in FIELDS:
            if float(x[key]).hex()!=float(y[key]).hex():
                raise RuntimeError(f"PARALLEL_FLOAT_IDENTITY_CHANGED:{i}:{key}")
    return True
def main():
    # Spawn avoids a cloned inherited mutable fenv. ProcessPool/independent
    # Python subprocesses are performance workers, NOT native AI subagents.
    ctx=mp.get_context("fork")
    serial_t=[];parallel_t=[]
    with ProcessPoolExecutor(max_workers=3,mp_context=ctx) as pool:
        refs=run_processes(pool)
        expected=run_serial()
        equality(refs,expected)
        for _ in range(4):
            t=time.perf_counter();s=run_serial()
            serial_t.append(time.perf_counter()-t)
            t=time.perf_counter();p=run_processes(pool)
            parallel_t.append(time.perf_counter()-t)
            equality(s,p)
    med_s=statistics.median(serial_t)
    med_p=statistics.median(parallel_t)
    result={
        "schema":"rei.c15.python_case_multiprocessing_benchmark.v1",
        "status":"FOUR_REAL_SOURCE_CASES_FLOAT_HEX_IDENTITY_4_REPEAT",
        "cases":CASE_PARAMS,
        "iterations":4,"cpus_available_via_parent_affinity":"taskset -c 2,3,4",
        "serial_runs_seconds":serial_t,"three_worker_seconds":parallel_t,
        "median_serial_seconds":med_s,"median_three_worker_seconds":med_p,
        "matched_accuracy_speedup":med_s/med_p,
        "numerical_equality":"exact f64 hex for all 12 key science output fields",
        "scientific_results":expected,
        "performance_scope":"4 independent nstep64 source photon+chemical+Einstein short experiments; no single-case solver speedup",
        "native_subagent":"NOT_RUN","scientific_admission":"NOT_ISSUED"}
    (HERE/"results/parallel_C15.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({x:result[x] for x in ("status","median_serial_seconds",
       "median_three_worker_seconds","matched_accuracy_speedup")},indent=2))
if __name__=="__main__":main()
