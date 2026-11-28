#!/usr/bin/env python3
"""Certify original six frozen radial panels + PHYS38 cusp and five H^-1 sheets."""
from __future__ import annotations
import argparse,json,sys
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys43_global_hybrid import global_hybrid


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--frozen",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    p.add_argument("--cusp-parent",type=Path,default=ROOT/"research/hh_phys37_20261015/results/SHELL_BOTH_N96_18.json")
    p.add_argument("--interfaces",type=Path,default=ROOT/"research/hh_phys38_20261015/results/INTERFACE_HMINUS1.json")
    p.add_argument("--delta",type=F,default=F(1,100))
    p.add_argument("--pieces",nargs=6,type=int,default=[8,16,16,8,8,8])
    p.add_argument("--mu-bins",type=int,default=16)
    p.add_argument("--radial-strategy",choices=["uniform","cusp_graded"],
                   default="uniform")
    p.add_argument("--signed-panels",nargs="*",type=int,default=[1,2])
    p.add_argument("--workers",type=int,choices=[1,2,3,4,6],default=2)
    p.add_argument("--digits",type=int,default=12)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    d=global_hybrid(args.frozen,args.cusp_parent,args.interfaces,
                    args.delta,tuple(args.pieces),args.mu_bins,
                    tuple(args.signed_panels),args.workers,args.digits,
                    args.radial_strategy)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({
        "input_sha256":d["source_sha256"],
        "broken_L2_upper":d["broken_strong_L2_upper"],
        "annulus_full_H1_dual_upper":d["complete_truncated_annulus_Hminus1_upper"],
        "PHYS39_stronger":not d["tighter_than_PHYS39"],
        "CUSP":d["cusp_log_strip_upper"],
        "signed_selected":[z["signed_selected_cells"] for z in d["radial_panels"]],
        "time_seconds":d["elapsed_s"],"output":str(args.output)
    }))
if __name__=="__main__":main()
