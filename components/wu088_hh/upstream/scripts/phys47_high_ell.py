#!/usr/bin/env python3
"""Source-locked rigorous Bernstein-ellipse high-l direct screened coupling."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys47_high_ell import high_ell_transfer


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--frozen",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
 p.add_argument("--Ns",nargs="*",type=int,default=[0,4,8,12,16,20,24,28,32,40])
 p.add_argument("--rhos",nargs="*",type=int,default=list(range(4,29)))
 p.add_argument("--terms",type=int,default=192)
 p.add_argument("--workers",type=int,choices=[1,2,3,4],default=1)
 p.add_argument("--output",type=Path,required=True)
 a=p.parse_args()
 r=high_ell_transfer(a.frozen,tuple(a.Ns),tuple(a.rhos),a.workers,a.terms)
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n")
 print(json.dumps({"source":r["original_frozen_source_SHA256"],
      "Ns":r["studied_Ns"],"best":r["best_bounds"],
      "candidate_count":len(r["candidate_rhos"]),
      "workers":r["workers"],"elapsed_s":r["elapsed_s"]}))
if __name__=="__main__":
 main()
