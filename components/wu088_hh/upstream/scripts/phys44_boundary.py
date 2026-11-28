#!/usr/bin/env python3
"""Source-locked WU088_HH central Coulomb boundary references, not full DtN."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys44_boundary import boundary_reference

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--input",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
 p.add_argument("--dps",type=int,default=60)
 p.add_argument("--workers",type=int,choices=(1,2,3,4),default=1)
 p.add_argument("--degree",type=int,default=18)
 p.add_argument("--output",type=Path,required=True)
 a=p.parse_args()
 z=boundary_reference(a.input,a.dps,a.workers,a.degree)
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(z,indent=2,ensure_ascii=False)+"\n")
 print(json.dumps({
 "source_sha256":z["frozen_source_sha256"],
 "outgoing_21_reference_modes":len(z["outer_Coulomb_reference_outgoing"]),
 "coulomb_reference_boundary_mismatch":z["outer_reduced_u20_minus_zc_u20_L2_diagnostic"],
 "screened_tail_upper":z["certified_screened_u_equation_radial_L1_r_ge20_upper"],
 "frozen_to_physical_eta_trace_upper":z["certified_eta_minus_y_surface_L2_upper"],
 "workers":a.workers,"elapsed_s":z["elapsed_s"],
 "status":"COULOMB_REFERENCE_DIAGNOSTIC_NOT_FULL_EXTERIOR_CERTIFICATE"}))
if __name__=="__main__":main()
