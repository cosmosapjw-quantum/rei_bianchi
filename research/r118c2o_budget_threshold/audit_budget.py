import json,hashlib,gzip,re
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;I=D.parents[1];H=Path('/home/cosmosapjw/Downloads')
P=H/'rei_r118c2o_q256';X=H/'rei_r118c2o_q256_final';Y=H/'rei_r118c2o_q256_late_v2'
def j(p):return json.loads(p.read_text())
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def kv(p):return dict(l.split('=',1) for l in p.read_text().splitlines() if '=' in l)
for line in (D/'q256_prefix.sha256').read_text().splitlines():
    digest,p=line.split(maxsplit=1);assert sha(p)==digest
v1=(D/'BINARY.sha256').read_text().splitlines()[-1].split(maxsplit=1);assert sha(v1[1])==v1[0]
for line in (D/'V2_BINARIES.sha256').read_text().splitlines():
    h,p=line.split(maxsplit=1);assert sha(p)==h
cfg=kv(P/'config.cfg');base=j(I/'research/r118c2n_spectral/Q256.json')
assert cfg=={**base['config'],'energy_budget_ev_per_h':'1e-8'}
assert (P/'config.cfg').read_bytes()==(X/'config.cfg').read_bytes()==(D/'q256_budget.cfg').read_bytes()
assert (P/'source_identity.txt').read_bytes()==(X/'source_identity.txt').read_bytes()
assert (D/'covariant_budget_v1.rs.txt').read_text() in (P/'source_identity.txt').read_text()
assert (I/'rust/rei_microphysics/src/axbi_covariant_driver.rs').read_text() in (Y/'source_identity.txt').read_text()
assert sha(P/'source_identity.txt')!=sha(Y/'source_identity.txt')
assert (X/'initial_checkpoint.txt').read_bytes()==(P/'checkpoint.txt').read_bytes()
c2=kv(Y/'config.cfg')
assert c2=={**cfg,'max_steps':'80000','energy_budget_count_fraction':'0.75','energy_budget_count_cap':'80000','energy_budget_chemical_fraction':'0.25'}
assert (Y/'config.cfg').read_bytes()==(D/'q256_v2.cfg').read_bytes()
assert (Y/'identity_status.txt').read_text().strip()=='NEW_IDENTITY_DONOR_STATE_DIAGNOSTIC_NOT_RESUME'
bind=j(D/'diagnostic_binding.json');assert sha(X/'checkpoint.txt')==bind['source_sha'] and sha(D/'diagnostic_checkpoint.txt')==bind['diagnostic_sha']
assert (Y/'donor_checkpoint.txt').read_bytes()==(D/'diagnostic_checkpoint.txt').read_bytes()
old=(X/'checkpoint.txt').read_text().splitlines();new=(Y/'donor_checkpoint.txt').read_text().splitlines()
assert old[0]==new[0] and old[2:]==new[2:]
x=old[1].split();y=new[1].split();assert len(x)==len(y) and [i for i,(a,b) in enumerate(zip(x,y)) if a!=b]==[7]
assert float(x[7])<1e-10 and float(y[7])==2e-5
assert (Y/'initial_checkpoint.txt').read_bytes()==(Y/'donor_checkpoint.txt').read_bytes()
def audit(root,exitf,variant):
    r=kv(root/'RETURN.txt');assert int((D/exitf).read_text())==0
    t=np.genfromtxt(root/'history.csv',names=True,delimiter=',')
    assert len(t)==int(r['additional_accepted'])+1 and t['accepted'][0]==int(r['initial_accepted']) and t['accepted'][-1]==int(r['accepted'])
    assert np.all(np.isfinite(t.view(float))) and np.all(np.diff(t['accepted'])==1) and np.all(np.diff(t['a'])>0) and np.all(np.diff(t['time_s'])>0)
    assert np.all(t['temperature_K']>0) and np.all((t['x_HII']>=0)&(t['x_HII']<=1)&(t['x_HeII']>=0)&(t['x_HeIII']>=0)&(t['x_HeII']+t['x_HeIII']<=1))
    for f in ('active_N','active_U','passive_N','passive_U'):assert np.min(t[f])>=0
    f=.2454/(4*(1-.2454));charge=float(np.max(abs(t['ne_proper_cm3']/t['nH_proper_cm3']-t['x_HII']-f*(t['x_HeII']+2*t['x_HeIII']))))
    gates=dict(N=float(np.max(abs(t['number_defect'])/(1e-8*np.maximum(t['source_N'],1.)))),E=float(np.max(abs(t['energy_defect'])/(1e-8*np.maximum(t['source_U'],1.)))),parity=float(np.max(abs(t['J1'])/(1e-12*np.maximum(t['J0'],1e-30)))))
    local=float(np.max(t['local_error'][1:]));assert max(gates.values())<=1 and charge<2e-14 and local<.00016
    h=np.log1p(np.diff(t['a'])/t['a'][:-1]);delta=np.diff(t['energy_defect'])
    budget=1e-8*h/np.log(21/5) if variant=='v1' else 1e-8*(.25*h/np.log(21/5)+.75/80000)
    ratio=float(np.max(abs(delta)/budget));assert ratio<=1+1e-10
    out=dict(variant=variant,status=r['status'],accepted=int(r['accepted']),additional=int(r['additional_accepted']),z_end=float(t['zbar'][-1]),wall_s=float(r['segment_wall_s']),gates=gates,charge=charge,max_local=local,max_abs_E=float(np.max(abs(t['energy_defect']))),max_increment_ratio=ratio,abs_increment_sum=float(np.sum(abs(delta),dtype=np.longdouble)),allocated_sum=float(np.sum(budget,dtype=np.longdouble)),raw_path=str(root),hashes={p.name:sha(p) for p in root.iterdir() if p.is_file()})
    print('segment',variant,{k:v for k,v in out.items() if k!='hashes'},flush=True);return t,out
a,pa=audit(P,'q256_run.exit','v1');b,pb=audit(X,'q256_final.exit','v1');c,pc=audit(Y,'v2_late.exit','v2_late_donor')
assert pa['status']=='STOPPED_SEGMENT_WALL_CAP' and pb['status'].startswith('STOPPED_NUMERICAL:') and pc['status']=='COMPLETE_REPRESENTED_INTERVAL'
keys=['a','zbar','time_s','nH_proper_cm3','ne_proper_cm3','x_HII','x_HeII','x_HeIII','temperature_K','active_N','active_U','passive_N','passive_U','source_N','source_U','energy_defect','number_defect']
for v,w in [(a,b),(b,c)]:assert all(v[f][-1]==w[f][0] for f in keys)
t=np.concatenate([a,b[1:],c[1:]])
assert t['zbar'][0]==20 and t['zbar'][-1]==4 and len(t)==int(pc['accepted'])+1
ref=[]
for x in base['segments']:
    p=Path(x['raw_path'])/'history.csv';assert sha(p)==x['hashes']['history.csv'];ref.append(np.genfromtxt(p,names=True,delimiter=','))
ref=np.concatenate((ref[0],ref[1][1:]))
zz=np.linspace(4,20,20001)
def interp(x,k):return np.interp(zz,x['zbar'][::-1],x[k][::-1])
def tau(x):return float(np.trapezoid(x['ne_proper_cm3']*1e6*299792458.*6.6524587051e-29,x['time_s']))
changes={f:dict(max_abs=float(np.max(abs(interp(t,f)-interp(ref,f)))),terminal_delta=float(t[f][-1]-ref[f][-1])) for f in ('x_HII','x_HeII','x_HeIII','temperature_K')}
abs_sum=sum(x['abs_increment_sum'] for x in (pa,pb,pc));alloc=sum(x['allocated_sum'] for x in (pa,pb,pc))
# Prefix v1 measured consumption plus worst-case remaining v2 allocation.
remaining_bound=1e-8*(.25*np.log(.2/b['a'][-1])/np.log(21/5)+.75*(80000-int(b['accepted'][-1]))/80000)
assert abs_sum<=alloc and pa['abs_increment_sum']+pb['abs_increment_sum']+remaining_bound<=1e-8
assert all(int((D/f).read_text())==0 for f in ('v2_green.exit','v2_full_tests.exit','threshold_run.exit','threshold_green.exit','diagnostic.exit'))
tests=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored',(D/'v2_full_tests.log').read_text());assert sum(int(x[1]) for x in tests)==328 and all(x[0]=='ok' for x in tests)
q=j(D/'THRESHOLD_RESULTS.json');assert len(q['static'])==3 and len(q['moving'])==5
assert all(max(x[m]['N_defect'],x[m]['U_defect'])<2e-10 for x in q['moving'] for m in ('full','split'))
r64=next(x for x in q['moving'] if x['steps']==64)
assert abs(r64['split']['absorbed_N_relative'])<abs(r64['full']['absorbed_N_relative'])
assert abs(r64['split']['heating_relative'])<abs(r64['full']['heating_relative'])
out=dict(status='PASS_SCOPED_MIXED_IDENTITY_BUDGET_DONOR_REPAIR',scope='v1 fresh prefix then v2 late donor experiment (not same-source resume); no full fresh v2 claim',segments=[pa,pb,pc],v1_binary_sha=v1[0],v2_late_binary_sha=sha(H/'rei_r118c2o_budget_late'),v2_segment_binary_sha=sha(H/'rei_r118c2o_budget_segment_v2'),v1_source_sha=sha(P/'source_identity.txt'),v2_source_sha=sha(Y/'source_identity.txt'),accepted=int(t['accepted'][-1]),end_z=4.,tau=tau(t),baseline_tau=tau(ref),terminal={f:float(t[f][-1]) for f in ('x_HII','x_HeII','x_HeIII','temperature_K')},changes_from_legacy=changes,max_legacy_gate=max(x['gates']['E'] for x in (pa,pb,pc)),legacy_q256_max_gate=base['max_gate_ratio'],max_abs_E=float(np.max(abs(t['energy_defect']))),absolute_increment_sum=abs_sum,allocated_actual=alloc,global_bound_prefix_measured_plus_remaining_cap=pa['abs_increment_sum']+pb['abs_increment_sum']+remaining_bound,max_increment_ratio=max(x['max_increment_ratio'] for x in (pa,pb,pc)),full_rust_tests=328,threshold_static_runs=15,threshold_moving_runs=5,production_admission='HOLD_FRESH_V2_REQUIRED',native_subagent='NOT_RUN')
(D/'BUDGET_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
np.savez_compressed(D/'MIXED_HISTORY_THIN.npz',columns=np.array(keys),history=np.stack([t[k] for k in keys],axis=1)[np.unique(np.r_[np.arange(0,len(t),100),len(t)-1])])
for name,root in [('v1_prefix',P),('v1_failure',X),('v2_donor',Y)]:
    for file in ('checkpoint.txt','initial_checkpoint.txt','config.cfg','RETURN.txt','source_identity.txt','resource_caps.txt'):
        (D/(name+'_'+file+'.gz')).write_bytes(gzip.compress((root/file).read_bytes(),mtime=0))
print(json.dumps({k:v for k,v in out.items() if k!='segments'},indent=2))
