import json,gzip,hashlib
from pathlib import Path
import numpy as np
D=Path(__file__).parent;K=Path('/home/cosmosapjw/Downloads/rei_r118c2k_segments');X=Path('/home/cosmosapjw/Downloads/rei_r118c2n_q128')
def j(p):return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def kv(p):return dict(l.split('=',1) for l in p.read_text().splitlines() if '=' in l)
k=j(Path('research/r118c2k_segment/ACCEPTANCE.json'))
assert sha(K/'segment_v2')==k['binaries']['v2']==(D/'BINARY.sha256').read_text().split()[0]
cfg=kv(X/'config.cfg');base=kv(K/'fresh64/config.cfg');assert cfg=={**base,'transport_cells':'128'} and (X/'config.cfg').read_bytes()==(D/'q128.cfg').read_bytes()
assert sha(X/'source_identity.txt')==sha(K/'fresh64/source_identity.txt')==k['source_identity_sha256']
r=kv(X/'RETURN.txt');assert r['status']=='COMPLETE_REPRESENTED_INTERVAL' and r['scientific_admission']=='NOT_ISSUED' and int((D/'q128.exit').read_text())==0
t=np.genfromtxt(X/'history.csv',names=True,delimiter=',')
assert len(t)==int(r['accepted'])+1 and t['accepted'][0]==0 and np.all(np.diff(t['accepted'])==1) and t['zbar'][0]==20 and t['zbar'][-1]==4
assert np.all(np.isfinite(t.view(float))) and np.all(np.diff(t['a'])>0) and np.all(np.diff(t['time_s'])>0)
assert np.all(t['temperature_K']>0) and np.all((t['x_HII']>=0)&(t['x_HII']<=1)&(t['x_HeII']>=0)&(t['x_HeIII']>=0)&(t['x_HeII']+t['x_HeIII']<=1))
for f in ('active_N','active_U','passive_N','passive_U'):assert np.min(t[f])>=0
fhe=.2454/(4*(1-.2454));charge=float(np.max(abs(t['ne_proper_cm3']/t['nH_proper_cm3']-t['x_HII']-fhe*(t['x_HeII']+2*t['x_HeIII']))))
gates=dict(N=float(np.max(abs(t['number_defect'])/(1e-8*np.maximum(t['source_N'],1.)))),E=float(np.max(abs(t['energy_defect'])/(1e-8*np.maximum(t['source_U'],1.)))),parity=float(np.max(abs(t['J1'])/(1e-12*np.maximum(t['J0'],1e-30)))))
local=float(np.max(t['local_error'][1:]));assert max(gates.values())<=1 and charge<2e-14 and local<float(cfg['local_target'])
old=next(x for x in j(Path('research/r118c2k_segment/RUNS.json')) if x['case']=='fresh64')
assert sha(K/'fresh64/history.csv')==old['hashes']['history.csv']
u=np.genfromtxt(K/'fresh64/history.csv',names=True,delimiter=',');zz=np.linspace(4,20,20001)
keys=['x_HII','x_HeII','x_HeIII','temperature_K']
def ip(a,key):return np.interp(zz,a['zbar'][::-1],a[key][::-1])
diff={f:dict(max_abs=float(np.max(abs(ip(t,f)-ip(u,f)))),terminal_delta=float(t[f][-1]-u[f][-1])) for f in keys}
tau=float(np.trapezoid(t['ne_proper_cm3']*1e6*299792458.*6.6524587051e-29,t['time_s']))
out=dict(status='PASS_SCOPED_COMPLETE',config=cfg,accepted=int(r['accepted']),wall_s=float(r['segment_wall_s']),tau=tau,terminal={f:float(t[f][-1]) for f in keys},max_local=local,gates=gates,charge=charge,comparison64=diff,raw_path=str(X),hashes={p.name:sha(p) for p in X.iterdir() if p.is_file()},source_sha=sha(X/'source_identity.txt'),binary_sha=sha(K/'segment_v2'))
(D/'Q128.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ('hashes','config')},indent=2))
for f in ('initial_checkpoint.txt','checkpoint.txt','config.cfg','RETURN.txt','source_identity.txt','resource_caps.txt'):(D/('q128_'+f+'.gz')).write_bytes(gzip.compress((X/f).read_bytes(),mtime=0))
np.savez_compressed(D/'q128_THIN.npz',columns=np.array(['zbar','a','time_s','nH_proper_cm3','ne_proper_cm3']+keys),history=np.stack([t[f] for f in ['zbar','a','time_s','nH_proper_cm3','ne_proper_cm3']+keys],axis=1)[np.unique(np.r_[np.arange(0,len(t),100),len(t)-1])])
