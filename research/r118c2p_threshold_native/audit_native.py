import json,hashlib
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;I=D.parents[1];H=Path('/home/cosmosapjw/Downloads')
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def j(p):return json.loads(p.read_text())
def kv(p):return dict(l.split('=',1) for l in p.read_text().splitlines() if '=' in l)
for b in ('V1_BINARY.sha256','V2_BINARY.sha256'):
    h,p=(D/b).read_text().split(maxsplit=1);assert sha(p.strip())==h
names=('q64_full_n512','q64_split_n512','q256_split_n512','q512_split_n512','q1024_split_n512','q64_split_n256','q64_split_n1024','q1024_split_n1024','q256_full_n512')
rr={};raw={};ids=set()
for name in names:
    e=D/(name+'_v2.exit');assert int(e.read_text())==0
    root=H/('rei_r118c2p_'+name+'_v2');ret=kv(root/'RETURN.txt')
    assert ret['status']=='COMPLETE_PRESCRIBED_GAS'
    n=int(ret['steps']);q=int(ret['q']);mode=ret['mode'];assert name==f'q{q}_{mode}_n{n}'
    assert sha(root/'schedule.csv')==sha(D/f'schedule{n}.csv')
    a=np.genfromtxt(root/'history.csv',names=True,delimiter=',')
    assert len(a)==n and a['a'][-1]==.2 and a['z'][-1]==4 and np.all(np.diff(a['a'])>0)
    assert np.all(np.isfinite(a.view(float))) and all(np.min(a[k])>=0 for k in ('N','U','above_N','Gamma_HI','Gamma_HeI','Gamma_HeII','heat_HI','heat_HeI','heat_HeII'))
    assert np.all(a['above_N']<=a['N']*(1+1e-12))
    ne=a['N']+a['absorbed_HI']+a['absorbed_HeI']+a['absorbed_HeII']-a['source_N']
    ee=a['U']+a['absorbed_U']+a['redshift_work']-a['source_U']
    assert np.max(abs(ne-a['N_defect']))<1e-14 and np.max(abs(ee-a['E_defect']))<1e-12
    assert max(abs(ne)/np.maximum(a['source_N'],1.))<1e-10 and max(abs(ee)/np.maximum(a['source_U'],1.))<1e-10
    identity=(root/'source_identity.txt').read_text();assert (I/'rust/rei_microphysics/src/axbi_heii_split.rs').read_text() in identity
    ids.add(sha(root/'source_identity.txt'))
    # Output-only launcher change: histories from initial version and v2 should be byte-identical.
    old=H/('rei_r118c2p_'+name)
    if old.is_dir():assert sha(old/'history.csv')==sha(root/'history.csv')
    rr[name]=dict(q=q,mode=mode,steps=n,wall_s=float(ret['wall_s']),terminal={k:float(a[k][-1]) for k in ('Gamma_HI','Gamma_HeI','Gamma_HeII','heat_HI','heat_HeI','heat_HeII','absorbed_HeII','above_N','source_U')},max_N_defect=float(np.max(abs(ne))),max_E_defect=float(np.max(abs(ee))),raw_path=str(root),hashes={x.name:sha(x) for x in root.iterdir() if x.is_file()})
    raw[name]=a
assert len(ids)==1
def compare(name,ref):
    a=raw[name];b=raw[ref];assert np.array_equal(a['a'],b['a'])
    v={}
    for k in ('Gamma_HI','Gamma_HeI','Gamma_HeII','heat_HI','heat_HeI','heat_HeII','absorbed_HeII','above_N'):
        scale=max(abs(b[k][-1]),1e-300);v[k]=dict(terminal_relative=float((a[k][-1]-b[k][-1])/scale),max_absolute_over_ref_peak=float(np.max(abs(a[k]-b[k]))/max(np.max(abs(b[k])),1e-300)))
    return v
cmp={n:compare(n,'q1024_split_n512') for n in names if rr[n]['steps']==512}
cmp['q64_split_n1024']=compare('q64_split_n1024','q1024_split_n1024')
assert abs(cmp['q64_split_n512']['Gamma_HeII']['terminal_relative'])<1e-5
assert abs(cmp['q64_split_n1024']['Gamma_HeII']['terminal_relative'])<1e-5
assert abs(cmp['q64_full_n512']['Gamma_HeII']['terminal_relative'])>1.
# Different time schedules: terminal comparisons only, no asymptotic order claim.
time={k:float(rr['q64_split_n1024']['terminal'][k]/rr['q64_split_n512']['terminal'][k]-1) for k in ('Gamma_HeII','heat_HeII','absorbed_HeII')}
out=dict(status='PASS_SCOPED_NATIVE_SOURCE_TRANSPORT_PRESCRIBED_GAS',scope='native actual source, all H/He frozen opacities and actual C2N gas history; not nonlinear gas owner',cases=rr,comparisons=cmp,time512_to1024=time,max_N_defect=max(x['max_N_defect'] for x in rr.values()),max_E_defect=max(x['max_E_defect'] for x in rr.values()),source_sha=next(iter(ids)),example_sha=sha(I/'rust/rei_microphysics/examples/axbi_c2p_heii_source.rs'),v2_binary_sha=(D/'V2_BINARY.sha256').read_text().split()[0])
(D/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print('max E',out['max_E_defect'],'max N',out['max_N_defect'])
for n in ('q64_full_n512','q64_split_n512','q256_full_n512','q256_split_n512','q64_split_n1024'):
 print(n,cmp[n]['Gamma_HeII'],cmp[n]['heat_HeII'],cmp[n]['absorbed_HeII'])
print('time',time)
