from pathlib import Path
import json,sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'src'))
from wu088_hh.phys60_positive_born import make_witness
p=root/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'
out=make_witness(p)
dest=root/'research/hh_phys60_20261016/c5c8/results/POSITIVE_BORN_WITNESS.json'
dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
for row in out['original_P20_Q21_m_grid']:
 if row['signed_m']==0:print(row['signed_m'],row['radial_nodes'],row['angular_nodes'],row['real_Born'],row['imag_Born'])
