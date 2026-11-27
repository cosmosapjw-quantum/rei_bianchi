#!/usr/bin/env python3
"""Certify original Coulomb centrifugal forbidden ACTION, not actual wave tunneling."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys48_barrier import source_barrier_actions

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--frozen",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
 p.add_argument("--ells",nargs="+",type=int,default=[14,15,20,21,24,28,33,41,61,80,120])
 p.add_argument("--steps",type=int,default=256)
 p.add_argument("--grading",choices=["uniform","quadratic","cubic","adaptive"],default="quadratic")
 p.add_argument("--workers",type=int,choices=[1,2,3,4],default=1)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 x=source_barrier_actions(a.frozen,tuple(a.ells),a.steps,a.grading,workers=a.workers)
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(x,indent=2)+"\n")
 print(json.dumps({"source":x["original_source_sha256"],"n":a.steps,
  "graded":a.grading,"workers":a.workers,"elapsed":x["elapsed_s"],
  "actions":[{"ell":v["ell"],"lo":v["action_lower"],"hi":v["action_upper"],
             "width":v["interval_width"]} for v in x["action_enclosures"]]}))

if __name__=="__main__":main()
