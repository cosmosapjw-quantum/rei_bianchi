"""Produce actual screened off-shell Born+remainder diagnostics."""
import json
from pathlib import Path
from wu088_hh.phys59_offshell_born import numerical_witness
root=Path(__file__).resolve().parents[1]
src=root/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'
out=root/'research/hh_phys59_20261016/c5c8/results/BORN_WITNESS.json'
out.parent.mkdir(parents=True,exist_ok=True)
a=numerical_witness(src)
out.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'source':a['original_SHA256'],'born_last':a['GL_radial_angular_noncertifying_rows'][-1]['born_GL_noncertifying'],'relative_refinement':a['finest_refinement_relative'],'Born_omission_upper':a['rigorous_Born_remainder']['allangular_Born_operator_remainder_exact_upper'],'HH_R10':a['HH_R10']}))
