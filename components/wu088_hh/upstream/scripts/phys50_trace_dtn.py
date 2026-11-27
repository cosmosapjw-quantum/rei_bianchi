#!/usr/bin/env python3
"""Original H-H screened all-ell nonzero trace energy/DtN certificate."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys50_trace_dtn import verified_high_trace_lifting


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    p.add_argument("--ells",nargs="+",type=int,default=[21,28,41,61,120,300])
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    r=verified_high_trace_lifting(a.source,examples=tuple(a.ells))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({
        "source":r["source_sha256"],
        "exact_trace_energy_C":r["exact_trace_energy_coefficient"],
        "trace_L2_gain":r["trace_to_high_homogeneous_L2_gain_upper"],
        "low_source_particular_L2_gain":r["original_PHYS49_zero_trace_force_gain_upper"],
        "trace_to_low_feedback":r["screened_high_to_low_feedback_from_unknown_traces_upper"],
        "all_high_modes":r["angular_space"],
        "status":r["scientific_scope"]}))
if __name__=="__main__":main()
