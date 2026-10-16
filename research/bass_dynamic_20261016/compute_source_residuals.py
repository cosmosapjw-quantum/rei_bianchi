#!/usr/bin/env python3
"""Row-level raw BASS source constraints; no interpolation or chemistry."""
import csv,json,math,sys
from pathlib import Path
root=Path(sys.argv[1])
source=root/"research/bass_dynamic_20261016/source_grids/matched_n121_241_481_retry"
h0=2.1842852410855026e-18;om=.315;orad=.000092;ol=.6849080000000001
out={"schema":"bass.rei.source_row_raw_residuals.v1","units":{"hamiltonian_raw":"s^-2","hamiltonian_denominator":"s^-2","raychaudhuri_raw":"s^-1","raychaudhuri_denominator":"s^-1","signed_shear_raw":"dimensionless"},"rows":[]}
for grid in (121,241,481):
  csvpath=source/f"n{grid:04d}"/"PROPOSED_REI_BACKGROUND.csv"
  for case in ("COLD_FLRW","SIGNED_MINUS"):
    fm=0.0 if case=="COLD_FLRW" else .1
    rows=list(r for r in csv.DictReader(csvpath.open()) if r["case"]==case)
    max_h=max_r=max_sh=0.0; max_hden=max_rden=0.0; max_hnorm=max_rnorm=0.0
    for r in rows:
      a=float(r["a"]);h=float(r["H_mean_per_s"]);s=float(r["s_per_s"]);rho=float(r["massive_rho_norm"]);p=float(r["massive_pbar_norm"]);hp=float(r["dH_dln_a_per_s"])
      expected=h0*h0*(om*(1-fm)/a**3+orad/a**4+ol+rho)+s*s
      actual=h*h; hden=max(abs(actual),abs(expected));hr=abs(actual-expected)
      pred=(h0*h0*(-3*om*(1-fm)/a**3-4*orad/a**4-3*(rho+p))-6*s*s)/(2*h)
      rr=abs(hp-pred);rden=max(abs(pred),1e-300)
      if hr>max_h:max_h,max_hden=hr,hden
      if rr>max_r:max_r,max_rden=rr,rden
      max_hnorm=max(max_hnorm,hr/hden);max_rnorm=max(max_rnorm,rr/rden)
      max_sh=max(max_sh,abs(float(r["signed_s_over_H"])-s/h))
    out["rows"].append({"case":case,"grid":grid,"row_count":len(rows),"hamiltonian_max_raw":max_h,"hamiltonian_denominator_at_max_raw":max_hden,"hamiltonian_max_normalized":max_hnorm,"hamiltonian_tolerance_normalized":3e-12,"raychaudhuri_max_raw":max_r,"raychaudhuri_denominator_at_max_raw":max_rden,"raychaudhuri_max_normalized":max_rnorm,"raychaudhuri_acceptance":"raw <= 1e-26 s^-1 + 3e-12*|predicted|","signed_shear_max_raw":max_sh})
out["global_max_hamiltonian_raw"]=max(x["hamiltonian_max_raw"] for x in out["rows"])
out["global_max_raychaudhuri_raw"]=max(x["raychaudhuri_max_raw"] for x in out["rows"])
out["global_max_signed_shear_raw"]=max(x["signed_shear_max_raw"] for x in out["rows"])
print(json.dumps(out,indent=2,sort_keys=True))
