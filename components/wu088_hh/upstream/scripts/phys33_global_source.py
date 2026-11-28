#!/usr/bin/env python3
"""Certify a global two-centre source correction and fixed-r angular kernels.

Original frozen-direct H+H model only; this executable does NOT solve the
complete continuum Schrödinger boundary value problem or thermal rate.
"""
from __future__ import annotations

import argparse,json,time,sys,hashlib
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from multiprocessing import get_all_start_methods,get_context
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys33_source_global import (
    improved_existing_broken_bound)
from wu088_hh.phys33_angular_kernel import angular_multipole_matrix


def one_radius(job):
    return angular_multipole_matrix(*job)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bulk-parent",type=Path,default=ROOT/"research/hh_phys36_20261015/results/C7_W4.json")
    ap.add_argument("--radii",nargs="+",default=["1/2","7/10","1","2"])
    ap.add_argument("--angular-power",type=int,default=2)
    ap.add_argument("--lmax",type=int,default=5)
    ap.add_argument("--nmax",type=int,default=32)
    ap.add_argument("--terms",type=int,default=192)
    ap.add_argument("--digits",type=int,default=15)
    ap.add_argument("--workers",type=int,choices=(1,2,4),default=1)
    ap.add_argument("--output",required=True,type=Path)
    a=ap.parse_args()
    radii=[F(s) for s in a.radii]
    if len(set(radii))!=len(radii):
        raise ValueError("duplicate radii")
    start=time.perf_counter()
    globalcert=improved_existing_broken_bound(
        a.bulk_parent,a.nmax,a.terms,a.digits)
    work=[(r,a.angular_power,a.lmax,a.terms,a.digits) for r in radii]
    if a.workers==1:
        matrices=list(map(one_radius,work))
    else:
        method="forkserver" if "forkserver" in get_all_start_methods() else "spawn"
        with ProcessPoolExecutor(max_workers=min(a.workers,len(work)),
                                 mp_context=get_context(method)) as pool:
            matrices=list(pool.map(one_radius,work))
    result={
       "schema":"WU088_HH_PHYS39_GLOBAL_SOURCE_AND_FIXED_R_KERNEL_BATCH_V1",
       "global_source_correction":globalcert,
       "fixed_radius_angular_matrices":matrices,
       "input_phys36_sha256":globalcert["parent_phys36_sha256"],
       "source_modules_sha256":{
          n:hashlib.sha256((ROOT/f"src/wu088_hh/{n}.py").read_bytes()).hexdigest()
          for n in ("phys33_source_global","phys33_angular_kernel")},
       "workers":a.workers,"time_s":time.perf_counter()-start,
       "scientific_scope":"all-space source correction; each angular kernel is one fixed-radius exact integral",
       "open":["generic radial continuum angular kernel integration over all panels",
               "cusp radial/outgoing interface response",
               "continuous low-Schur inverse","scattering amplitude and rate"],
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("x",encoding="utf-8") as z:
        json.dump(result,z,ensure_ascii=False,indent=2);z.write("\n")
    print(json.dumps({"output":str(a.output),
        "new_bound":globalcert["new_broken_bulk_bound"],
        "source_norm":globalcert["new_source"]["norm_L2_upper"],
        "matrix_radius_count":len(matrices),"workers":a.workers,
        "elapsed_s":result["time_s"]}))
if __name__=="__main__":
    main()
