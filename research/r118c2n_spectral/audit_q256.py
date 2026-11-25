import json,gzip,hashlib
from pathlib import Path
import numpy as np
D=Path(__file__).parent;K=Path('/home/cosmosapjw/Downloads/rei_r118c2k_segments');P=Path('/home/cosmosapjw/Downloads/rei_r118c2n_q256');X=Path('/home/cosmosapjw/Downloads/rei_r118c2n_q256_final')
def j(p):return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def kv(p):return dict(l.split('=',1) for l in p.read_text().splitlines() if '=' in l)
prior=j(D/'Q128.json');k=j(Path('research/r118c2k_segment/ACCEPTANCE.json'))
assert sha(K/'segment_v2')==k['binaries']['v2']==prior['binary_sha']
for line in (D/'q256_prefix.sha256').read_text().splitlines():
    digest,path=line.split(maxsplit=1);assert sha(Path(path))==digest
cfg=kv(P/'config.cfg');assert cfg=={**prior['config'],'transport_cells':'256'} and (P/'config.cfg').read_bytes()==(D/'q256.cfg').read_bytes()
assert sha(P/'source_identity.txt')==k['source_identity_sha256']
def audit(root,exitf):
    r=kv(root/'RETURN.txt');assert int(exitf.read_text())==0 and r['scientific_admission']=='NOT_ISSUED'
    assert r['status'] in ('COMPLETE_REPRESENTED_INTERVAL','STOPPED_SEGMENT_WALL_CAP','STOPPED_ORIGINAL_ABSOLUTE_CAP')
    t=np.genfromtxt(root/'history.csv',names=True,delimiter=',')
    assert len(t)==int(r['additional_accepted'])+1 and t['accepted'][0]==int(r['initial_accepted']) and t['accepted'][-1]==int(r['accepted'])
    assert np.all(np.diff(t['accepted'])==1) and np.all(np.isfinite(t.view(float))) and np.all(np.diff(t['a'])>0) and np.all(np.diff(t['time_s'])>0)
    assert np.all(t['temperature_K']>0) and np.all((t['x_HII']>=0)&(t['x_HII']<=1)&(t['x_HeII']>=0)&(t['x_HeIII']>=0)&(t['x_HeII']+t['x_HeIII']<=1))
    for f in ('active_N','active_U','passive_N','passive_U'):assert np.min(t[f])>=0
    fhe=.2454/(4*(1-.2454));charge=float(np.max(abs(t['ne_proper_cm3']/t['nH_proper_cm3']-t['x_HII']-fhe*(t['x_HeII']+2*t['x_HeIII']))))
    gates=dict(N=float(np.max(abs(t['number_defect'])/(1e-8*np.maximum(t['source_N'],1.)))),E=float(np.max(abs(t['energy_defect'])/(1e-8*np.maximum(t['source_U'],1.)))),parity=float(np.max(abs(t['J1'])/(1e-12*np.maximum(t['J0'],1e-30)))))
    local=float(np.max(t['local_error'][1:]));assert max(gates.values())<=1 and charge<2e-14 and local<float(cfg['local_target'])
    out=dict(status=r['status'],accepted=int(r['accepted']),additional=int(r['additional_accepted']),wall_s=float(r['segment_wall_s']),z_start=float(t['zbar'][0]),z_end=float(t['zbar'][-1]),max_local=local,gates=gates,charge=charge,raw_path=str(root),hashes={p.name:sha(p) for p in root.iterdir() if p.is_file()})
    return t,out
a,pa=audit(P,D/'q256.exit');assert a['accepted'][0]==0 and a['zbar'][0]==20
assert (X/'initial_checkpoint.txt').read_bytes()==(P/'checkpoint.txt').read_bytes() and (X/'config.cfg').read_bytes()==(P/'config.cfg').read_bytes()
assert sha(X/'source_identity.txt')==sha(P/'source_identity.txt')
b,pb=audit(X,D/'q256_final.exit')
# Ignore timing/counter diagnostics in endpoint equality, compare all physical state fields.
keys=['a','zbar','time_s','nH_proper_cm3','ne_proper_cm3','x_HII','x_HeII','x_HeIII','temperature_K','active_N','active_U','passive_N','passive_U']
assert all(np.isclose(a[f][-1],b[f][0],rtol=3e-14,atol=1e-30) for f in keys)
t=np.concatenate((a,b[1:]));assert len(t)==pb['accepted']+1 and np.all(np.diff(t['a'])>0)
q=Path(prior['raw_path']);assert sha(q/'history.csv')==prior['hashes']['history.csv']
u=np.genfromtxt(q/'history.csv',names=True,delimiter=',');zmin=float(t['zbar'][-1]);zz=np.linspace(zmin,20,20001)
def ip(a,key):return np.interp(zz,a['zbar'][::-1],a[key][::-1])
fields=['x_HII','x_HeII','x_HeIII','temperature_K']
diff={f:dict(max_abs=float(np.max(abs(ip(t,f)-ip(u,f)))),terminal_delta=float(ip(t,f)[0]-ip(u,f)[0])) for f in fields}
tau=float(np.trapezoid(t['ne_proper_cm3']*1e6*299792458.*6.6524587051e-29,t['time_s']))
complete=pb['status']=='COMPLETE_REPRESENTED_INTERVAL'
if complete:assert zmin==4.
out=dict(status='PASS_SCOPED_COMPLETE' if complete else 'PASS_SCOPED_CHECKPOINTED',config=cfg,accepted=pb['accepted'],z_end=zmin,wall_s=pa['wall_s']+pb['wall_s'],tau=tau,terminal={f:float(t[f][-1]) for f in fields},comparison128=diff,max_local=max(pa['max_local'],pb['max_local']),max_gate_ratio=max(max(x['gates'].values()) for x in (pa,pb)),max_charge=max(pa['charge'],pb['charge']),segments=[pa,pb],raw_path=str(X),hashes=pb['hashes'],source_sha=sha(X/'source_identity.txt'),binary_sha=sha(K/'segment_v2'))
(D/'Q256.json').write_text(json.dumps(out,indent=2)+'\n')
for name,root in [('prefix',P),('final',X)]:
    for f in ('initial_checkpoint.txt','checkpoint.txt','config.cfg','RETURN.txt','source_identity.txt','resource_caps.txt'):(D/('q256_'+name+'_'+f+'.gz')).write_bytes(gzip.compress((root/f).read_bytes(),mtime=0))
np.savez_compressed(D/'q256_THIN.npz',columns=np.array(keys),history=np.stack([t[f] for f in keys],axis=1)[np.unique(np.r_[np.arange(0,len(t),100),len(t)-1])])
print(json.dumps({k:v for k,v in out.items() if k not in ('hashes','config','segments')},indent=2))
