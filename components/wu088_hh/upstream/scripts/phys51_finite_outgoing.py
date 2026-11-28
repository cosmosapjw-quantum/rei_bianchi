"""Generate PHYS51 source-locked proof and reference diagnostics."""
import argparse,json
from pathlib import Path
from wu088_hh.phys51_finite_outgoing import finite_band_screened_jost,coulomb_impedance_rows
p=argparse.ArgumentParser()
root=Path(__file__).resolve().parents[1]
p.add_argument("--original",default=str(root/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"))
p.add_argument("--out",default=str(root/"research/hh_phys51_20261015/results/FINITE_HIGH_OUTGOING.json"))
a=p.parse_args()
out=finite_band_screened_jost(a.original)
out["coulomb_reference_noncert"]=coulomb_impedance_rows()
target=Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({k:out[k] for k in ["schema","source_sha256","n_channels","certified_patch_T_Bohr","screened_Volt_q_outward","status"]},indent=2))
