import hashlib,json,gzip
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;I=D.parents[1];H=Path('/home/cosmosapjw/Downloads')
P=H/'rei_r118c2p_fresh256';X=H/'rei_r118c2p_fresh256_final'
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def j(p):return json.loads(p.read_text())
def kv(p):return dict(l.split('=',1) for l in p.read_text().splitlines() if '=' in l)
for line in (D/'prefix.sha256').read_text().splitlines()+(D/'BINARY.sha256').read_text().splitlines():
    h,p=line.split(maxsplit=1);assert sha(p)==h
prior=j(I/'research/r118c2o_budget_threshold/BUDGET_RESULTS.json')
assert sha(P/'source_identity.txt')==prior['v2_source_sha']==sha(X/'source_identity.txt')
assert (D/'BINARY.sha256').read_text().split()[0]==prior['v2_segment_binary_sha']
assert (P/'config.cfg').read_bytes()==(X/'config.cfg').read_bytes()==(D/'q256.cfg').read_bytes()==(I/'research/r118c2o_budget_threshold/q256_v2.cfg').read_bytes()
assert (X/'initial_checkpoint.txt').read_bytes()==(P/'checkpoint.txt').read_bytes()
cfg=kv(P/'config.cfg');B=float(cfg['energy_budget_ev_per_h']);f=float(cfg['energy_budget_count_fraction']);cap=int(cfg['energy_budget_count_cap']);L=np.log(21/5)
assert B==1e-8 and f==.75 and cap==80000 and int(cfg['max_steps'])==cap
def audit(root,exitf):
    r=kv(root/'RETURN.txt');assert int((D/exitf).read_text())==0
    t=np.genfromtxt(root/'history.csv',names=True,delimiter=',')
    assert len(t)==int(r['additional_accepted'])+1 and t['accepted'][0]==int(r['initial_accepted']) and t['accepted'][-1]==int(r['accepted'])
    assert np.all(np.isfinite(t.view(float))) and np.all(np.diff(t['accepted'])==1) and np.all(np.diff(t['a'])>0) and np.all(np.diff(t['time_s'])>0)
    assert np.all(t['temperature_K']>0) and np.all((t['x_HII']>=0)&(t['x_HII']<=1)&(t['x_HeII']>=0)&(t['x_HeIII']>=0)&(t['x_HeII']+t['x_HeIII']<=1))
    for s in ('active_N','active_U','passive_N','passive_U'):assert np.min(t[s])>=0
    he=.2454/(4*(1-.2454));charge=float(np.max(abs(t['ne_proper_cm3']/t['nH_proper_cm3']-t['x_HII']-he*(t['x_HeII']+2*t['x_HeIII']))))
    gates=dict(N=float(np.max(abs(t['number_defect'])/(1e-8*np.maximum(t['source_N'],1.)))),E=float(np.max(abs(t['energy_defect'])/(1e-8*np.maximum(t['source_U'],1.)))),parity=float(np.max(abs(t['J1'])/(1e-12*np.maximum(t['J0'],1e-30)))))
    loc=float(np.max(t['local_error'][1:]));assert max(gates.values())<=1 and charge<2e-14 and loc<float(cfg['local_target'])
    budget=B*((1-f)*np.log1p(np.diff(t['a'])/t['a'][:-1])/L+f/cap);inc=np.diff(t['energy_defect'])
    ratio=float(np.max(abs(inc)/budget));assert ratio<=1+1e-10
    out=dict(status=r['status'],additional=int(r['additional_accepted']),accepted=int(r['accepted']),z_end=float(t['zbar'][-1]),wall_s=float(r['segment_wall_s']),gates=gates,max_charge=charge,max_local=loc,max_abs_E=float(np.max(abs(t['energy_defect']))),max_increment_ratio=ratio,allocated=float(np.sum(budget,dtype=np.longdouble)),absolute_increment_sum=float(np.sum(abs(inc),dtype=np.longdouble)),raw_path=str(root),hashes={p.name:sha(p) for p in root.iterdir() if p.is_file()})
    print('segment', {k:v for k,v in out.items() if k!='hashes'},flush=True)
    return t,out
a,pa=audit(P,'first.exit');b,pb=audit(X,'final.exit')
assert pa['status']=='STOPPED_SEGMENT_WALL_CAP' and pb['status']=='COMPLETE_REPRESENTED_INTERVAL'
keys=['a','zbar','time_s','nH_proper_cm3','ne_proper_cm3','x_HII','x_HeII','x_HeIII','temperature_K','active_N','active_U','passive_N','passive_U','source_N','source_U','energy_defect','number_defect']
assert all(a[k][-1]==b[k][0] for k in keys)
t=np.concatenate((a,b[1:]));assert t['zbar'][0]==20 and t['zbar'][-1]==4 and len(t)==pb['accepted']+1 and pb['accepted']<=cap
s=pa['absolute_increment_sum']+pb['absolute_increment_sum'];alloc=pa['allocated']+pb['allocated'];assert s<=alloc<=B*(1+1e-12)
old=j(I/'research/r118c2n_spectral/Q256.json')
r=[]
for x in old['segments']:
    p=Path(x['raw_path'])/'history.csv';assert sha(p)==x['hashes']['history.csv'];r.append(np.genfromtxt(p,names=True,delimiter=','))
r=np.concatenate((r[0],r[1][1:]));z=np.linspace(4,20,20001)
def tau(x):return float(np.trapezoid(x['ne_proper_cm3']*1e6*299792458.*6.6524587051e-29,x['time_s']))
def ip(x,k):return np.interp(z,x['zbar'][::-1],x[k][::-1])
comp={k:dict(max_abs=float(np.max(abs(ip(t,k)-ip(r,k)))),terminal_delta=float(t[k][-1]-r[k][-1])) for k in ('x_HII','x_HeII','x_HeIII','temperature_K')}
out=dict(status='PASS_SCOPED_FRESH_SAME_IDENTITY_BUDGET_V2',source_sha=sha(P/'source_identity.txt'),binary_sha=prior['v2_segment_binary_sha'],config=cfg,segments=[pa,pb],accepted=int(t['accepted'][-1]),z_end=4.,max_E_gate=max(x['gates']['E'] for x in (pa,pb)),baseline_E_gate=old['max_gate_ratio'],max_abs_E=float(np.max(abs(t['energy_defect']))),absolute_increment_sum=s,allocated_sum=alloc,max_increment_ratio=max(pa['max_increment_ratio'],pb['max_increment_ratio']),tau=tau(t),baseline_tau=tau(r),terminal={k:float(t[k][-1]) for k in ('x_HII','x_HeII','x_HeIII','temperature_K')},comparison=comp,baseline_rhs=int(r['rhs'][-1]),rhs=int(t['rhs'][-1]),scope='q256 FLRW frozen source identity and local target; no new spectral closure; original full q convergence unresolved')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
for label,root in [('prefix',P),('final',X)]:
    for file in ('checkpoint.txt','initial_checkpoint.txt','config.cfg','RETURN.txt','source_identity.txt','resource_caps.txt'):
        (D/(label+'_'+file+'.gz')).write_bytes(gzip.compress((root/file).read_bytes(),mtime=0))
np.savez_compressed(D/'THIN.npz',columns=np.array(keys),history=np.stack([t[k] for k in keys],axis=1)[np.unique(np.r_[np.arange(0,len(t),100),len(t)-1])])
print(json.dumps({k:v for k,v in out.items() if k not in ('segments','config')},indent=2))
