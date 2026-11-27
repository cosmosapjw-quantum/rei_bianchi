#!/usr/bin/env python3
"""PHYS41 original six-panel Bernstein/Coulomb-source broken-bulk certificate."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))

from wu088_hh.phys33_panel_bernstein import whole_panel_certificate

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--frozen",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    ap.add_argument("--pieces",type=int,default=8)
    ap.add_argument("--workers",type=int,choices=[1,2,3,4,6],default=1)
    ap.add_argument("--digits",type=int,default=12)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    report=whole_panel_certificate(args.frozen,args.pieces,args.workers,args.digits)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({
        "schema":report["schema"],"input_sha256":report["input_sha256"],
        "broken_bulk_upper":report["certified_broken_strong_L2_upper"],
        "tiles":report["tiles"],"elapsed_s":report["elapsed_s"],
        "workers":report["workers"],"output":str(args.out)
    },ensure_ascii=False))
if __name__=="__main__":
    main()
