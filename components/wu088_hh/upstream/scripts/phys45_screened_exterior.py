#!/usr/bin/env python3
"""Run exact rational screened two-centre m=0 angular coupling at r=20."""
from __future__ import annotations
import argparse,json,sys
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys45_screened_exterior import screened_coupling_matrix

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--source",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
 p.add_argument("--radius",type=Q,default=Q(20))
 p.add_argument("--lmax",type=int,default=20)
 p.add_argument("--terms",type=int,default=320)
 p.add_argument("--digits",type=int,default=24)
 p.add_argument("--workers",type=int,choices=[1,2,3,4],default=1)
 p.add_argument("--output",type=Path,required=True)
 a=p.parse_args()
 d=screened_coupling_matrix(a.source,a.radius,a.lmax,a.terms,a.digits,a.workers)
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 print(json.dumps({
  "frozen":d["original_source_sha256"],
  "radius":d["radius_a0"],"lmax":d["lmax"],
  "evaluated_distinct_pairs":d["evaluated_distinct_pairs"],
  "matrix_00":d["certified_V_matrix_interval"][0][0],
  "matrix_01":d["certified_V_matrix_interval"][0][1] if d["lmax"]>=1 else None,
  "all_angular_operator_norm_upper":d["all_angular_operator_norm_upper"],
  "external_offcentral_L1_upper":d["tails"]["full_plus_2V_off_central_diagonal_radial_L1_upper"],
  "workers":d["workers"],"elapsed_s":d["elapsed_s"]
 }))
if __name__=="__main__":main()
