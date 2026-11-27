#!/usr/bin/env python3
"""Execute rigorous finite-width cusp radial-strip certificates in parallel.

Exact Fraction widths, exact archived dyadic source, 2-sided shell parent SHA.
The independent fast NumPy s-coordinate preview is deliberately excluded from
scientific acceptance here.
"""
from __future__ import annotations
import argparse,hashlib,json,sys,time
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from multiprocessing import get_all_start_methods,get_context
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys33_cusp_strip import strip_certificate

def _one(job):
    return strip_certificate(*job)

def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    p.add_argument("--parent",type=Path,default=ROOT/"research/hh_phys37_20261015/results/SHELL_BOTH_N96_18.json")
    p.add_argument("--deltas",nargs="+",default=["1/100","1/1000","1/10000"])
    p.add_argument("--workers",type=int,choices=(1,2,3,4),default=2)
    p.add_argument("--digits",type=int,default=12)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    widths=[Fraction(s) for s in a.deltas]
    if len(set(widths))!=len(widths):raise ValueError("duplicate width")
    tasks=[(a.input,a.parent,d,a.digits) for d in widths]
    begin=time.perf_counter()
    if a.workers==1:
        out=list(map(_one,tasks))
    else:
        method="forkserver" if "forkserver" in get_all_start_methods() else "spawn"
        with ProcessPoolExecutor(max_workers=min(a.workers,len(tasks)),
                                 mp_context=get_context(method)) as pool:
            out=list(pool.map(_one,tasks))
    z={
      "schema":"WU088_HH_PHYS38_BATCH_FINITE_RADIAL_STRIP_V1",
      "input_sha256":out[0]["input_sha256"],
      "parent_shell_json_sha256":hashlib.sha256(a.parent.read_bytes()).hexdigest(),
      "module_sha256":hashlib.sha256((ROOT/"src/wu088_hh/phys33_cusp_strip.py").read_bytes()).hexdigest(),
      "workers":a.workers,"digits":a.digits,"runtime_s":time.perf_counter()-begin,
      "strips":out,
      "global_3D_scattering_certified":False,
      "code_used":"python Fraction, Wolfram/exact parent shell and certified log",
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("x") as f:
        json.dump(z,f,ensure_ascii=False,indent=2)
        f.write("\n")
    print(json.dumps({"workers":a.workers,"elapsed_s":z["runtime_s"],
       "results":{x["delta_a0"]:x["total_3D_broken_strong_residual_L2_upper"] for x in out}}))

if __name__=="__main__":main()
