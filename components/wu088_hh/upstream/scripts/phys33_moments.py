#!/usr/bin/env python3
"""C6/C8 exact rational/log whole-cell residual certificate.

Use an immutable archived IEEE-binary64 nodal file. All polynomial moments
are computed exactly with Fraction; the sole logarithm is enclosed by a
positive rational atanh series. Parallel execution partitions SIX radial
panels and always reduces in panel index order. Not a continuum inverse.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

from wu088_hh.phys33_moments import bound_weighted_moments


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input",type=Path,
        default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    ap.add_argument("--workers",type=int,choices=(1,2,3,4,6),default=4)
    ap.add_argument("--digits",type=int,default=12)
    ap.add_argument("--screen-cells",type=int,choices=(1,2,4,8,16),default=8)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    data=bound_weighted_moments(args.input,workers=args.workers,digits=args.digits,
                                screen_cells=args.screen_cells)
    data["implementation_sha256"]=sha256(
        (ROOT/"src/wu088_hh/phys33_moments.py").read_bytes()).hexdigest()
    data["cli_sha256"]=sha256(Path(__file__).read_bytes()).hexdigest()
    data["command"]=[
        "python3","scripts/phys33_moments.py","--input",str(args.input),
        "--workers",str(args.workers),"--digits",str(args.digits),
        "--screen-cells",str(args.screen_cells),
        "--output",str(args.output)]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as f:
        json.dump(data,f,indent=2,ensure_ascii=False)
        f.write("\n")
    print(json.dumps({"elapsed_s":data["elapsed_s"],
                      "workers":args.workers,"output":str(args.output),
                      "norm_upper":data["norm_upper"],
                      "source_sha256":data["input_sha256"]}))


if __name__=="__main__":
    main()
