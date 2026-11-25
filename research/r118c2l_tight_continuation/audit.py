import gzip,hashlib,json,sys
from pathlib import Path
import numpy as np
D=Path(__file__).parent;R=Path(sys.argv[1]);K=Path(sys.argv[2]);J=Path(sys.argv[3]);P=Path('research/r118c2k_segment/ACCEPTANCE.json')
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def kv(p):return dict(l.split('=',1) for l in p.read_text().splitlines() if '=' in l)
prior=json.loads(P.read_text()); parent=K/'fresh32tight'; old=J/'long32'
assert sha(K/'segment_v2')==prior['binaries']['v2']
assert (R/'initial_checkpoint.txt').read_bytes()==(parent/'checkpoint.txt').read_bytes()
assert (R/'config.cfg').read_bytes()==(parent/'config.cfg').read_bytes()
assert sha(R/'source_identity.txt')==sha(parent/'source_identity.txt')==prior['source_identity_sha256']
pr={v['case']:v for v in json.loads((P.parent/'RUNS.json').read_text())}
for n in ('fresh32tight','resume32','fresh64'):
    for f in ('history.csv','config.cfg','checkpoint.txt','source_identity.txt'):
        assert sha(K/n/f)==pr[n]['hashes'][f]
oldref=next(v for v in json.loads(Path('research/r118c2j_error_control/RUNS.json').read_text()) if v['variant']=='reduced' and v['case']=='long32')
assert sha(old/'history.csv')==oldref['hashes']['history.csv']
ret=kv(R/'RETURN.txt');cfg=kv(R/'config.cfg');cap=kv(R/'resource_caps.txt');assert ret['status']=='STOPPED_SEGMENT_WALL_CAP' and ret['scientific_admission']=='NOT_ISSUED'
t=np.genfromtxt(R/'history.csv',names=True,delimiter=','); assert len(t)==int(ret['additional_accepted'])+1 and t['accepted'][0]==int(ret['initial_accepted']) and t['accepted'][-1]==int(ret['accepted'])
assert np.all(np.isfinite(t.view(float))) and np.all(np.diff(t['accepted'])==1) and np.all(np.diff(t['a'])>0) and np.all(np.diff(t['time_s'])>0)
assert np.all(t['temperature_K']>0) and np.all((t['x_HII']>=0)&(t['x_HII']<=1)&(t['x_HeII']>=0)&(t['x_HeIII']>=0)&(t['x_HeII']+t['x_HeIII']<=1))
for f in ('active_N','active_U','passive_N','passive_U'):assert np.min(t[f])>=0
fhe=.2454/(4*(1-.2454)); charge=float(np.max(abs(t['ne_proper_cm3']/t['nH_proper_cm3']-t['x_HII']-fhe*(t['x_HeII']+2*t['x_HeIII']))))
gates=dict(N=float(np.max(abs(t['number_defect'])/(1e-8*np.maximum(t['source_N'],1.)))),E=float(np.max(abs(t['energy_defect'])/(1e-8*np.maximum(t['source_U'],1.)))),parity=float(np.max(abs(t['J1'])/(1e-12*np.maximum(t['J0'],1e-30)))))
local=float(np.max(t['local_error'][1:]));assert max(gates.values())<=1 and charge<2e-14 and local<float(cfg['local_target'])
keys=['a','zbar','time_s','nH_proper_cm3','ne_proper_cm3','x_HII','x_HeII','x_HeIII','temperature_K']
def read(p):return np.genfromtxt(p,names=True,delimiter=',',usecols=keys)
def pack(t):return np.stack([t[k] for k in keys],axis=1)
def concat(x,y):
    assert np.allclose(x[-1],y[0],rtol=3e-14,atol=1e-30)
    z=np.concatenate((x,y[1:]));assert np.all(np.diff(z[:,0])>0) and np.all(np.diff(z[:,2])>0);return z
tight=concat(pack(read(parent/'history.csv')),pack(t));q32=concat(pack(read(old/'history.csv')),pack(read(K/'resume32/history.csv')));q64=pack(read(K/'fresh64/history.csv'))
def compare(x,y):
    lo=max(x[-1,1],y[-1,1]);hi=min(x[0,1],y[0,1]);zz=np.linspace(lo,hi,20001)
    xx=np.stack([np.interp(zz,x[::-1,1],x[::-1,j]) for j in range(5,9)],axis=1);yy=np.stack([np.interp(zz,y[::-1,1],y[::-1,j]) for j in range(5,9)],axis=1)
    dif=xx-yy;return dict(z_range=[float(lo),float(hi)],max_abs=dict(zip(keys[5:],map(float,abs(dif).max(axis=0)))),end_delta=dict(zip(keys[5:],map(float,dif[0]))))
res=dict(status='PASS_SCOPED_CHECKPOINTED',solver_status=ret['status'],scientific_admission='NOT_ISSUED',parent='e93661d3b83beb4cb2c381339dde6e860c28e7c1',new_steps=int(ret['additional_accepted']),total_steps=int(ret['accepted']),z_start=float(t['zbar'][0]),z_end=float(t['zbar'][-1]),local_target=float(cfg['local_target']),max_local=local,gate_ratios=gates,charge_defect=charge,resources=cap,terminal=dict(zip(keys[5:],map(float,tight[-1,5:]))),tau_prefix=float(np.trapezoid(tight[:,4]*1e6*299792458.*6.6524587051e-29,tight[:,2])),comparisons={'tight32_vs_q32':compare(tight,q32),'q32_vs_q64_common_prefix':compare(q32[q32[:,1]>=tight[-1,1]],q64)},raw_path=str(R),hashes={f.name:sha(f) for f in R.iterdir() if f.is_file()},binary_sha256=sha(K/'segment_v2'),full_time_convergence='UNRESOLVED')
(D/'ACCEPTANCE.json').write_text(json.dumps(res,indent=2)+'\n');np.savez_compressed(D/'tight32_THIN.npz',columns=np.array(keys),history=tight[np.unique(np.r_[np.arange(0,len(tight),100),len(tight)-1])])
for f in ('initial_checkpoint.txt','checkpoint.txt','config.cfg','RETURN.txt','source_identity.txt','resource_caps.txt'):(D/(f+'.gz')).write_bytes(gzip.compress((R/f).read_bytes(),mtime=0))
print(json.dumps({k:v for k,v in res.items() if k not in ('hashes','resources')},indent=2))
