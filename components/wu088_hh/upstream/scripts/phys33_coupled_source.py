#!/usr/bin/env python3
"""Certify the frozen two-centre cusp-trial *broken bulk* source-cancelled residual.

Mathematical scope: R=kappa=0.7, lambda=1, r0<=r<=20, all angles,
original H(1s) source. This is NOT a continuum scattering amplitude bound.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import argparse, json,sys,time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys33_coupled_source import bound_coupled_source


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input",type=Path,
        default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    ap.add_argument("--workers",type=int,choices=[1,2,3,4,6],default=4)
    ap.add_argument("--screen-cells",type=int,choices=[1,2,4,8,16],default=8)
    ap.add_argument("--exp-terms",type=int,default=256)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    started=time.perf_counter()
    x=bound_coupled_source(args.input,workers=args.workers,
        screen_cells=args.screen_cells,exp_terms=args.exp_terms)
    x["elapsed_s"]=time.perf_counter()-started
    x["implementation_sha256"]=sha256((ROOT/"src/wu088_hh/phys33_coupled_source.py").read_bytes()).hexdigest()
    x["command"]=["python3","scripts/phys33_coupled_source.py",
        "--input",str(args.input),"--workers",str(args.workers),
        "--screen-cells",str(args.screen_cells),"--exp-terms",str(args.exp_terms),
        "--output",str(args.output)]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as f:
        json.dump(x,f,indent=2,ensure_ascii=False)
        f.write("\n")
    print(json.dumps({"file":str(args.output),"elapsed_s":x["elapsed_s"],
                      "input_sha256":x["input_sha256"],"norm_upper":x["norm_upper"]}))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
