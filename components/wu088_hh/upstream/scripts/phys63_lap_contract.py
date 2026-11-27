from pathlib import Path
import json
from wu088_hh.phys63_lap_contract import applicability
root=Path(__file__).resolve().parents[1]
out=applicability(root/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz')
p=root/'research/hh_phys63_20261018/r5/results/APPLICABILITY.json'
p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
