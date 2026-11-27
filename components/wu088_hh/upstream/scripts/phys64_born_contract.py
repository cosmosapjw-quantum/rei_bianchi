"""Reproduce the exact PHYS64 R5 low-block certificate."""
import json
from pathlib import Path
from wu088_hh.phys63_lap_contract import source_guard
from wu088_hh.phys64_born_contract import low_mode_certificate
root=Path(__file__).resolve().parents[1]
source=root/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'
data=low_mode_certificate()
data['source_sha256']=source_guard(source)
print(json.dumps(data,default=str,indent=2))
