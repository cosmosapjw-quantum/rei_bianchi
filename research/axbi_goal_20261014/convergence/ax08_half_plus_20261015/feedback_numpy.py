#!/usr/bin/env python3
"""NumPy vectorized, immutable-input AX08 omitted-stress sensitivity diagnostic.

This is an optional high-throughput cross-check. A single file uses O(rows)
RAM instead of the O(1) streaming Rust and Python references.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import time

import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
COEFF=8*np.pi*6.67430e-11/(3*299792458.0**2)
EXPECTED=json.loads((HERE/"feedback_reconstruction.json").read_text())["results"]
N=312238

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def one(case):
    src=EXPECTED[case]
    path=ROOT/src["source_feedback_path"]
    if sha(path)!=src["source_feedback_sha256"]:
        raise AssertionError("FROZEN_FEEDBACK_BYTES_CHANGED")
    t0=time.perf_counter()
    raw=np.loadtxt(path,delimiter=",",skiprows=1,usecols=(1,2,3,4,5,8,9),dtype=np.float64,ndmin=2)
    if raw.shape!=(N,7) or not bool(np.all(np.isfinite(raw))):
        raise AssertionError("HOLD_SHAPE_OR_NONFINITE")
    t,a,H,p0,p1,extra,pt=raw.T
    if t[0]!=0 or abs(a[0]-1/21)>1e-16 or a[-1]!=.2 or np.any(np.diff(t)<=0) or np.any(np.diff(a)<=0) or np.any(H<=0):
        raise AssertionError("HOLD_ORDERED_CLOCK_AND_INTERVAL")
    if np.any(np.abs(p0+p1-pt)>np.maximum(1e-25,1e-12*np.abs(pt))):
        raise AssertionError("HOLD_PRESSURE_LEDGER")
    dt=np.diff(t)
    a3=a**3
    common=COEFF/(a3*H)
    c0=np.empty(N);c1=np.empty(N)
    c0[0]=0;c1[0]=0
    np.cumsum(.5*(a3[:-1]*p0[:-1]+a3[1:]*p0[1:])*dt,out=c0[1:])
    np.cumsum(.5*(a3[:-1]*p1[:-1]+a3[1:]*p1[1:])*dt,out=c1[1:])
    c0*=common;c1*=common
    total=c0+c1
    result={"case":case,"rows":N,"max_abs_delta_s_over_H":float(np.max(np.abs(total))),
       "endpoint_delta_s_over_H":float(total[-1]),
       "max_extra_energy_ratio":float(np.max(np.abs(extra))),
       "endpoint_effective_rad_delta_s_over_H":float(c0[-1]),
       "endpoint_ionizing_delta_s_over_H":float(c1[-1]),
       "wall_s":time.perf_counter()-t0}
    golden={"max_abs_delta_s_over_H":src["max_abs_delta_s_over_H"]["abs_delta_s_over_H"],
       "endpoint_delta_s_over_H":src["endpoint"]["total_delta_s_over_H"],
       "max_extra_energy_ratio":src["max_abs_extra_energy_ratio"]["abs_ratio"],
       "endpoint_effective_rad_delta_s_over_H":src["endpoint"]["effective_radiation_delta_s_over_H"],
       "endpoint_ionizing_delta_s_over_H":src["endpoint"]["ionizing_delta_s_over_H"]}
    for key,val in golden.items():
        err=abs(result[key]-val)
        if err>max(1e-25,1e-12*abs(val)):
            raise AssertionError(f"SCIENTIFIC_NUMERICAL_MISMATCH:{case}:{key}:{result[key]}:{val}")
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--serial",action="store_true")
    args=ap.parse_args()
    start=time.perf_counter()
    cases=("ZERO","SHEAR_HALF_PLUS")
    if args.serial:
        results=list(map(one,cases))
    else:
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(one,cases))
    print(json.dumps({"status":"PASS_NUMPY_VECTORIZED_SAME_INPUT_PARITY",
       "parallel_files":not args.serial,
       "n_cases":len(results),"wall_s":time.perf_counter()-start,
       "results":results,"scientific_admission":"NOT_ISSUED"}))
if __name__=="__main__":
    main()
