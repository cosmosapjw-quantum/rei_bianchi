"""Reproduce PHYS60 R5 finite Galerkin positive energy Jost evidence."""
from pathlib import Path
import sys,json
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'src'))
from wu088_hh.phys60_finite_jost import *
source=root/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'
out=make_r5_certificate(source)
out['physical_m0_sample_screen_matrix_ell20_21_r27']=angular_real_block(27.,(20,21),0,192).tolist()
out['central_coulomb_wronskian']=[current_wronskian_check(l,27,75) for l in (0,20,21,28)]
p=root/'research/hh_phys60_20261016/r5/results/JOST_FINITE_CERTIFICATE.json'
p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print('R5 finite-L outgoing Volterra theorem gates source SHA',out['frozen_npz_sha256'])
print('sample positive P/Q coupling',out['physical_m0_sample_screen_matrix_ell20_21_r27'][0][1])
