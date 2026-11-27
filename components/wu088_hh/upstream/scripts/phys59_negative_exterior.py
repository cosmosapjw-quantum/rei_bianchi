"""Run source-locked PHYS59 negative-energy infinite angular theorem producer."""
import json
from pathlib import Path
from wu088_hh.phys59_negative_exterior import certificate
root=Path(__file__).resolve().parents[1]
src=root/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'
out=root/'research/hh_phys59_20261016/r5/results/CERTIFICATE.json'
out.parent.mkdir(parents=True,exist_ok=True)
c=certificate(src)
out.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'schema':c['schema'],'source':c['original_sha256'],'E':c['bounds']['real_negative_energy_Hartree'],'difference_bound':c['bounds']['dtn_diff_full_angular_upper_exact'],'PQ_strict_lower':c['strict_m0_P20_Q21']['strict_full_original_screened_Zminus_PQ_lower_exact'],'HH_R10':c['production_HH_R10']}))
