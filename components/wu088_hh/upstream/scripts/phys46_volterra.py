#!/usr/bin/env python3
"""PHYS46 rigorous all 21 retained modes exterior outgoing Volterra contraction."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys46_volterra import finite21_volterra_certificate


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--frozen",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
 p.add_argument("--patch-T",nargs="*",type=int,default=list(range(29,41)))
 p.add_argument("--workers",type=int,default=1,choices=(1,2,3,4))
 p.add_argument("--terms",type=int,default=72)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 d=finite21_volterra_certificate(a.frozen,tuple(a.patch_T),a.workers,a.terms)
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(d,indent=2)+"\n")
 print(json.dumps({
  "source_SHA":d["source_sha256"],"best_T":d["T_energy_patch_a0"],
  "M":d["M_state_bound_integer"],
  "rigorous_volterra_norm_upper":d["selected_q_strict_upper"],
  "relative_Jost_matrix_error_upper":d["selected_alpha_Jost_relative_error_upper"],
  "similarity_DtN_multiplier":d["similarity_normalized_DtN_multiplier_upper"],
  "finite21_Jost_invertible":d["outgoing_Jost_B_invertible"],
  "sci_scope":d["scientific_status"],"workers":d["workers"],
  "seconds":d["elapsed_s"]}))
if __name__=="__main__":main()
