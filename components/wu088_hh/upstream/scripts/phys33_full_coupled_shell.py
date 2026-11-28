#!/usr/bin/env python3
"""PHYS40: rigorous full-screened coupled ANGULAR shell at exact radii.

One radial point at a time, retaining 21 frozen partial waves and original
source. Distinct from the noncertifying fast NumPy s-Gauss preview.
"""
from __future__ import annotations

import argparse,json,hashlib,time,sys
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from multiprocessing import get_all_start_methods,get_context
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys33_full_coupled_shell import full_coupled_angular_shell


def _one(job):
    return full_coupled_angular_shell(*job)


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    ap.add_argument("--radii",nargs="+",default=["1/2","7/10:left","7/10:right","1","2"])
    ap.add_argument("--order",type=int,default=64)
    ap.add_argument("--terms",type=int,default=192)
    ap.add_argument("--digits",type=int,default=12)
    ap.add_argument("--workers",type=int,choices=[1,2,3,4,5],default=4)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    tags=[]
    for item in a.radii:
        v=item.split(":")
        if len(v)>2:
            raise ValueError("single optional side suffix only")
        radius=F(v[0])
        side=v[1] if len(v)==2 else None
        if side not in (None,"left","right") or radius<=0:
            raise ValueError("invalid exact radius/side")
        tags.append((radius,side))
    if len(set(tags))!=len(tags):
        raise ValueError("duplicate scientific radius-side selection")
    jobs=[(a.input, r, side, a.order, a.terms, a.digits) for r,side in tags]
    start=time.perf_counter()
    if a.workers==1:
        results=list(map(_one,jobs))
    else:
        mode="forkserver" if "forkserver" in get_all_start_methods() else "spawn"
        with ProcessPoolExecutor(
                max_workers=min(a.workers,len(jobs)),mp_context=get_context(mode)) as pool:
            results=list(pool.map(_one,jobs))
    source=(ROOT/"src/wu088_hh/phys33_full_coupled_shell.py")
    result={
       "schema":"WU088_HH_PHYS40_FULL_COUPLED_ANGULAR_SHELL_BATCH_V1",
       "input_sha256":results[0]["source_sha256"],
       "module_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
       "orders":{"angular_Taylor":a.order,"positive_exp_terms":a.terms,"digits":a.digits},
       "results":results,"workers":a.workers,
       "elapsed_s":time.perf_counter()-start,
       "scope":"rigorous full angular physical residual at selected radii, NOT integrated over radial continuum",
       "next":"radial strong whole-cell and Hminus1 dual, origin/outgoing/low Schur",
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("x",encoding="utf-8") as stream:
        json.dump(result,stream,indent=2,ensure_ascii=False)
        stream.write("\n")
    print(json.dumps({"output":str(a.output),"radii":len(results),
                      "seconds":result["elapsed_s"],"workers":a.workers,
                      "shells":[{"r":x["physical_r_a0"],"side":x["one_sided_choice"],
                                 "upper":x["angular_norm_L2_upper"]}
                                for x in results]}))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
