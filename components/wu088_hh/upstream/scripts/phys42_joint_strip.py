#!/usr/bin/env python3
"""PHYS42 exact radial-angular signed interval strip; original source pinned."""
from __future__ import annotations

import argparse,json,sys
from fractions import Fraction as F
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys42_joint_interval import joint_strip

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--frozen",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    p.add_argument("--center",type=F,default=F(1))
    p.add_argument("--delta",type=F,default=F(1,1000))
    p.add_argument("--radial-bins",type=int,default=4)
    p.add_argument("--mu-bins",type=int,default=192)
    p.add_argument("--workers",type=int,choices=(1,2,3,4,6),default=1)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    ans=joint_strip(a.frozen,a.center,a.delta,a.radial_bins,a.mu_bins,
                    workers=a.workers)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(ans,indent=2)+"\n")
    print(json.dumps({"original_SHA256":ans["source_sha256"],
        "center":ans["center_a0"],"delta":ans["delta_a0"],
        "certified_L2":ans["full_3D_broken_L2_upper"],
        "cells":ans["cells"],"workers":ans["workers"],
        "elapsed_s":ans["elapsed_s"],"output":str(a.output)}))
if __name__=="__main__":
    main()
