#!/usr/bin/env python3
"""Certified infinite ell>=21 original screened Dirichlet-collar Schur gain."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys49_dirichlet_collar import high_l_dirichlet_collar


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    p.add_argument("--Ns",type=int,nargs="+",default=[0,4,8,12,16,20,24,28,32,40])
    p.add_argument("--workers",type=int,choices=(1,2,3,4),default=1)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    d=high_l_dirichlet_collar(a.source,tuple(a.Ns),workers=a.workers)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
    dshow=[{"ell_from":x["output_minimum_l"],"upper":x["high_l_conditional_response_L2_gain_upper"],
            "ellipse_rho":x["selected_ellipse_rho"]} for x in d["exact_outward_tail_rows"]]
    print(json.dumps({
      "original_source_SHA256":d["original_source_sha256"],
      "interval_a0":d["radius_interval_a0"],
      "screening_perturbation_max":d["original_screening_plus2S_sup_upper"],
      "exact_dirichlet_lambda_floor":d["unperturbed_high_Dirichlet_eigen_floor_exact"],
      "infinite_high_block_Schur_q":d["infinite_high_ell_neumann_q_upper"],
      "high_response_gain":d["whole_high_response_gain_to_low_u_P_upper"],
      "tails":dshow,"workers":a.workers,"elapsed_s":d["elapsed_s"],
      "status":d["scientific_status"]}))
if __name__=="__main__":main()
