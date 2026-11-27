#!/usr/bin/env python3
"""PHYS42 deterministic adaptive angular interval certificate with exact heap."""
import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys42_adaptive import adaptive_strip

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--frozen",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    p.add_argument("--center",type=F,default=F(1))
    p.add_argument("--delta",type=F,default=F(1,1000))
    p.add_argument("--radial-bins",type=int,default=4)
    p.add_argument("--initial-mu",type=int,default=8)
    p.add_argument("--target-mu",type=int,default=96)
    p.add_argument("--workers",type=int,default=4,choices=(1,2,3,4,6))
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    z=adaptive_strip(a.frozen,a.center,a.delta,
                     a.radial_bins,a.initial_mu,a.target_mu,a.workers)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(z,indent=2)+"\n")
    print(json.dumps({
        "source_sha256":z["source_sha256"],
        "physical_strip":z["physical_domain_a0"],
        "certified_upper":z["certified_signed_broken_L2_upper"],
        "chosen_best_partition_cells":[p["best_partition_cells"] for p in z["radial_partitions"]],
        "evaluated_exact_cells":sum(p["angular_seeds"]+2*p["split_count"] for p in z["radial_partitions"]),
        "elapsed_s":z["elapsed_s"],"workers":z["workers"],
        "output":str(a.output)
    }))
if __name__=="__main__":
    main()
