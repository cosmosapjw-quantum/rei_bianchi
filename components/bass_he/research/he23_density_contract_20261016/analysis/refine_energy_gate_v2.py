import os,sys,json,time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0,'/root/BASS_HE_HE23_DENSITY_20261016/research/he23_density_contract_20261016/src')
from run_native import run_case,atomic_json
from he22_native_client import OWNER_SOURCE_SHA
w=Path('/root/HE23_NCP_DENSITY_20261016');out=w/'refinement_energy_gate_v2';out.mkdir(exist_ok=False)
cases=[(4,8),(8,8),(16,2),(16,4),(16,8)]
jobs=[(str(w/'build/he22_owner_point'),m,n,0.,20.,str(out/f'raw_m{m}_n{n}'),OWNER_SOURCE_SHA) for m,n in cases]
start=time.monotonic()
with ProcessPoolExecutor(max_workers=3) as pool:
 futures=[pool.submit(run_case,j) for j in jobs]
 for (m,n),f in zip(cases,futures):
  try:r=f.result(timeout=600);record={'status':'PASS_SCOPED','result':r}
  except Exception as e:
   atomic_json(out/f'FIRST_FAILURE_m{m}_n{n}.json',{'error':repr(e),'traceback':__import__('traceback').format_exc()});raise
  atomic_json(out/f'q+0.0000_m{m}_n{n}.json',record)
atomic_json(out/'SUMMARY.json',{'all_pass':True,'cases':cases,'wall_s':time.monotonic()-start,'scope':'q0 finite time/energy refinement; fixed angular order 8'})
