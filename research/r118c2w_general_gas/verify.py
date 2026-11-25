import json,hashlib,gzip,re
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def kv(p):return dict(x.split('=',1) for x in p.read_text().splitlines() if '=' in x)
def j(p):return json.loads(p.read_text())
for f in ('green.exit','green_final.exit','build.exit','external_green.exit','continuity_green.exit','full_tests.exit','frozen_prepare.exit'):assert int((D/f).read_text())==0
for file in ('INPUT.sha256','PRESCRIBED_BINARY.sha256','FROZEN_BINARY.sha256','BRIDGE_V1.sha256'):
 for l in (D/file).read_text().splitlines():
  h,p=l.split(maxsplit=1);assert sha(p)==h
cases={};data={}
for n in (4,8):
 p=H/f'rei_r118c2w_g{n}';assert int((D/f'g{n}.exit').read_text())==0
 ret=kv(p/'RETURN.txt');assert ret['status']=='COMPLETE'
 r=np.genfromtxt(p/'history.csv',names=True,delimiter=',');s=np.genfromtxt(p/'stocks.csv',names=True,delimiter=',');a=np.genfromtxt(p/'rays.csv',names=True,delimiter=',')
 assert len(r)==int(ret['accepted'])+1 and r['z'][0]==20 and r['z'][-1]==19.8 and len(a)==2*n*n
 assert np.all(np.isfinite(r.view(float))) and np.all(np.diff(r['a'])>0) and np.all(np.diff(r['time_s'])>0)
 assert len(s)==len(a)*35*4 and min(s['N'])>=0 and np.all(s['Uref']>=s['lo']*s['N']) and np.all(s['Uref']<=s['hi']*s['N'])
 ray=s['ray'].astype(int);energy=s['Uref']*a['scale'][ray];direction=np.stack([a[k][ray] for k in ('nx','ny','nz')],axis=1)
 flux=energy@direction;pressure=np.einsum('a,ai,aj->ij',energy,direction,direction)
 assert abs(energy.sum()-r['J0'][-1])<1e-14 and np.max(abs(flux))<1e-12*energy.sum()
 assert max(abs(pressure[i,k]-r[v][-1]) for i,k,v in [(0,0,'Pxx'),(1,1,'Pyy'),(2,2,'Pzz'),(0,1,'Pxy'),(0,2,'Pxz'),(1,2,'Pyz')])<1e-14
 assert max(abs(r['J0']-r['Pxx']-r['Pyy']-r['Pzz']))<1e-12*max(r['J0'])
 assert max(np.linalg.norm(np.stack([r[k] for k in ('Fx','Fy','Fz')],axis=1),axis=1))<2e-12*max(r['J0'])
 assert max(abs(r['Ndef']))<1e-8 and max(abs(r['Edef']))<1e-8 and max(r['local_error'])<1.6e-4
 c=kv(p/'config.cfg');budget=float(c['energy_budget_ev_per_h'])*((1-float(c['energy_budget_count_fraction']))*np.diff(np.log(r['a']))/np.log(21/(1+float(c['end_zbar'])))+float(c['energy_budget_count_fraction'])/int(c['energy_budget_count_cap']))
 inc=np.diff(r['Edef']);assert max(abs(inc)/budget)<1+1e-9 and np.sum(abs(inc))<=np.sum(budget)
 for b,(lo,hi) in enumerate([(0,13.6),(13.6,24.59),(24.59,54.42),(54.42,np.inf)]):
  q=(s['band']==b)&(s['N']>0);assert np.all(s['lo'][q]*a['scale'][ray[q]]>=lo-1e-12) and np.all(s['hi'][q]*a['scale'][ray[q]]<=hi+1e-12)
 files={f.name:sha(f) for f in p.iterdir() if f.is_file()}
 for f in p.iterdir():
  if f.is_file():(D/f'g{n}_{f.name}.gz').write_bytes(gzip.compress(f.read_bytes(),mtime=0))
 row=dict(accepted=int(ret['accepted']),wall=float(ret['wall_s']),source_identity=files['source_identity.txt'],raw=str(p),hashes=files,max_E=float(max(abs(r['Edef']))),sum_abs_E=float(np.sum(abs(inc))),allocated=float(np.sum(budget)),terminal={k:float(r[k][-1]) for k in ('z','T','xHII','xHeIII','J0','Pxx','Pyy','Pzz','Pxy','Pxz','Pyz','source_U')})
 cases[str(n)]=row;data[n]=r
assert cases['4']['source_identity']==cases['8']['source_identity']
fg=[];g=j(D/'gas_map32.json')
for p,h in g['sources'].items():assert sha(p)==h
for p in sorted(D.glob('frozen_*.csv')):
 assert int(p.with_suffix('.exit').read_text())==0
 r=np.genfromtxt(p,names=True,delimiter=',');row={k:r[k].item() for k in r.dtype.names};assert abs(row['source_N']/g['terminal']['source_N']-1)<1e-12;row['sha']=sha(p);fg.append(row)
assert len(fg)==6
tests=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored',(D/'full_tests.log').read_text());assert sum(int(x[1]) for x in tests)==346 and all(x[0]=='ok' for x in tests)
out=dict(status='PASS_SCOPED_GENERAL_GAS_AND_FROZEN_REFINEMENT',parent='f1e849d9a9384a9f150a3196c2da3c1aa5205bfa',cases=cases,frozen=fg,frozen_gas=g,full_rust_tests=346,production_admission='HOLD_GENERAL_FULL_INTERVAL_CHECKPOINT_AND_JOINT_RESOLUTION',native_subagent='NOT_RUN')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print('cases',cases,'frozen',fg)
