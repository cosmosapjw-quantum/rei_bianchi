import json,hashlib,gzip
from pathlib import Path
import numpy as np
D=Path(__file__).parent;K=Path('/home/cosmosapjw/Downloads/rei_r118c2k_segments');L=Path('/home/cosmosapjw/Downloads/rei_r118c2l_tight');M=Path('/home/cosmosapjw/Downloads/rei_r118c2m_tight')
J=Path('/home/cosmosapjw/Downloads/rei_r118c2j_reduced');P=Path('research/r118c2k_segment')
prior=json.loads((D.parent/'r118c2l_tight_continuation/ACCEPTANCE.json').read_text());k=json.loads((P/'ACCEPTANCE.json').read_text())
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def kv(p):return dict(l.split('=',1) for l in p.read_text().splitlines() if '=' in l)
assert sha(K/'segment_v2')==k['binaries']['v2']==prior['binary_sha256']
for f in ['history.csv','config.cfg','checkpoint.txt','source_identity.txt']:
    assert sha(L/f)==prior['hashes'][f]
assert (M/'initial_checkpoint.txt').read_bytes()==(L/'checkpoint.txt').read_bytes()
assert (M/'config.cfg').read_bytes()==(L/'config.cfg').read_bytes()
assert sha(M/'source_identity.txt')==sha(L/'source_identity.txt')==k['source_identity_sha256']
cfg=kv(M/'config.cfg');ret=kv(M/'RETURN.txt');cap=kv(M/'resource_caps.txt')
assert cfg['local_target']=='8e-05' and ret['scientific_admission']=='NOT_ISSUED'
assert ret['status'] in ('STOPPED_SEGMENT_WALL_CAP','STOPPED_ORIGINAL_ABSOLUTE_CAP','COMPLETE_REPRESENTED_INTERVAL')
assert cap['effective_steps']==cap['original_steps'] and cap['effective_attempts']==cap['original_attempts']
t=np.genfromtxt(M/'history.csv',names=True,delimiter=',');assert len(t)==int(ret['additional_accepted'])+1 and t['accepted'][0]==int(ret['initial_accepted']) and t['accepted'][-1]==int(ret['accepted'])
assert np.all(np.isfinite(t.view(float))) and np.all(np.diff(t['accepted'])==1) and np.all(np.diff(t['a'])>0) and np.all(np.diff(t['time_s'])>0)
assert np.all(t['temperature_K']>0) and np.all((t['x_HII']>=0)&(t['x_HII']<=1)&(t['x_HeII']>=0)&(t['x_HeIII']>=0)&(t['x_HeII']+t['x_HeIII']<=1))
for f in ('active_N','active_U','passive_N','passive_U'):assert np.min(t[f])>=0
fhe=.2454/(4*(1-.2454));charge=float(np.max(abs(t['ne_proper_cm3']/t['nH_proper_cm3']-t['x_HII']-fhe*(t['x_HeII']+2*t['x_HeIII']))))
gates=dict(N=float(np.max(abs(t['number_defect'])/(1e-8*np.maximum(t['source_N'],1.)))),E=float(np.max(abs(t['energy_defect'])/(1e-8*np.maximum(t['source_U'],1.)))),parity=float(np.max(abs(t['J1'])/(1e-12*np.maximum(t['J0'],1e-30)))))
local=float(np.max(t['local_error'][1:]));assert max(gates.values())<=1 and charge<2e-14 and local<float(cfg['local_target'])
runs={v['case']:v for v in json.loads((P/'RUNS.json').read_text())}
for case in ('fresh32tight','resume32','fresh64'):
    assert sha(K/case/'history.csv')==runs[case]['hashes']['history.csv']
old=next(v for v in json.loads(Path('research/r118c2j_error_control/RUNS.json').read_text()) if v['variant']=='reduced' and v['case']=='long32')
assert sha(J/'long32/history.csv')==old['hashes']['history.csv']
keys=['a','zbar','time_s','nH_proper_cm3','ne_proper_cm3','x_HII','x_HeII','x_HeIII','temperature_K']
def read(p):return np.genfromtxt(p,names=True,delimiter=',',usecols=keys)
def pack(x):return np.stack([x[k] for k in keys],axis=1)
def concat(*ts):
    a=pack(ts[0])
    for x in ts[1:]:
        b=pack(x);assert np.allclose(a[-1],b[0],rtol=3e-14,atol=1e-30);a=np.concatenate((a,b[1:]))
    assert np.all(np.diff(a[:,0])>0) and np.all(np.diff(a[:,2])>0)
    return a
tight=concat(read(K/'fresh32tight/history.csv'),read(L/'history.csv'),t)
q32=concat(read(J/'long32/history.csv'),read(K/'resume32/history.csv'));q64=pack(read(K/'fresh64/history.csv'))
assert len(tight)==int(ret['accepted'])+1
def interp(x,z):return np.array([np.interp(z,x[::-1,1],x[::-1,j]) for j in range(5,9)]).T
zmin=tight[-1,1];zz=np.linspace(zmin,20.,20001);ref=interp(q32,zz);u=interp(tight,zz);v=interp(q64,zz)
def diff(x,y):
    return dict(max_abs=dict(zip(keys[5:],map(float,np.max(abs(x-y),axis=0)))),end_delta=dict(zip(keys[5:],map(float,(x-y)[0]))))
r=dict(status='PASS_SCOPED_COMPLETE' if ret['status']=='COMPLETE_REPRESENTED_INTERVAL' else 'PASS_SCOPED_CHECKPOINTED',solver_status=ret['status'],initial_accepted=int(ret['initial_accepted']),new_accepted=int(ret['additional_accepted']),total_accepted=int(ret['accepted']),z_start=float(t['zbar'][0]),z_end=float(zmin),max_local=local,gates=gates,charge=charge,tau_prefix=float(np.trapezoid(tight[:,4]*1e6*299792458.*6.6524587051e-29,tight[:,2])),terminal=dict(zip(keys[5:],map(float,tight[-1,5:]))),comparisons={'tight32_vs_q32':diff(u,ref),'q32_vs_q64':diff(ref,v)},resources=cap,source_sha=sha(M/'source_identity.txt'),binary_sha=sha(K/'segment_v2'),raw_path=str(M),hashes={f.name:sha(f) for f in M.iterdir() if f.is_file()})
(D/'CONTINUATION.json').write_text(json.dumps(r,indent=2)+'\n')
np.savez_compressed(D/'tight32_THIN.npz',columns=np.array(keys),history=tight[np.unique(np.r_[np.arange(0,len(tight),100),len(tight)-1])])
for f in ('initial_checkpoint.txt','checkpoint.txt','config.cfg','RETURN.txt','source_identity.txt','resource_caps.txt'):
    (D/('continuation_'+f+'.gz')).write_bytes(gzip.compress((M/f).read_bytes(),mtime=0))
print(json.dumps({k:v for k,v in r.items() if k not in ('hashes','resources')},indent=2))
