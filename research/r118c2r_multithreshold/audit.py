import json,hashlib,gzip,re
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;I=D.parents[1];H=Path('/home/cosmosapjw/Downloads');B=Path('/home/cosmosapjw/worktrees/bass-r109-native-20261124')
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def j(p):return json.loads(p.read_text())
def kv(p):return dict(l.split('=',1) for l in p.read_text().splitlines() if '=' in l)
h,p=(D/'BINARY.sha256').read_text().split(maxsplit=1);assert sha(p.strip())==h
base=j(I/'research/r118c2p_fresh_budget/RESULTS.json')
ref=[]
for x in base['segments']:
    p=Path(x['raw_path'])/'history.csv';assert sha(p)==x['hashes']['history.csv'];ref.append(np.genfromtxt(p,names=True,delimiter=','))
ref=np.concatenate((ref[0],ref[1][1:]))
bass=j(B/'research/r118c2m_energy_budget/RESULTS.json')
b=next(x for x in bass['results'] if x['name']=='cross');bp=Path(bass['raw'])/'cross'/'history.tsv';assert sha(bp)==b['hashes']['history.tsv']
# Original fit binding constant from C2N model, convert erg to eV.
ev=1.602176634e-12
names=['q64','q128','q64tight','q128tight'];rr={};raw={};ids=set()
def one(root,exitfile,cfg):
    r=kv(root/'RETURN.txt');assert int(exitfile.read_text())==0
    assert (root/'config.cfg').read_bytes()==cfg.read_bytes()
    ident=(root/'source_identity.txt').read_text()
    assert (I/'rust/rei_microphysics/src/axbi_covariant_driver.rs').read_text() in ident
    assert (I/'rust/rei_microphysics/src/axbi_heii_split.rs').read_text() in ident
    assert (I/'rust/rei_microphysics/src/axbi_multithreshold.rs').read_text() in ident
    ids.add(sha(root/'source_identity.txt'))
    a=np.genfromtxt(root/'history.csv',names=True,delimiter=',')
    assert len(a)==int(r['additional_accepted'])+1 and a['accepted'][0]==int(r['initial_accepted']) and a['accepted'][-1]==int(r['accepted'])
    assert np.all(np.diff(a['a'])>0) and np.all(np.diff(a['time_s'])>0) and np.all(np.diff(a['accepted'])==1) and np.all(np.isfinite(a.view(float)))
    assert np.all(a['temperature_K']>0) and np.all((a['x_HII']>=0)&(a['x_HII']<=1)&(a['x_HeII']>=0)&(a['x_HeIII']>=0)&(a['x_HeII']+a['x_HeIII']<=1))
    for k in ('active_N','active_U','passive_N','passive_U','above_N','middle_N','Gamma_HI','Gamma_HeI','Gamma_HeII','heat_HI_erg','heat_HeI_erg','heat_HeII_erg','absorbed_HeII'):assert np.min(a[k])>=0
    assert np.all(a['above_N']+a['middle_N']<=a['active_N']*(1+1e-12))
    fhe=.2454/(4*(1-.2454));charge=float(np.max(abs(a['ne_proper_cm3']/a['nH_proper_cm3']-a['x_HII']-fhe*(a['x_HeII']+2*a['x_HeIII']))))
    c=kv(cfg);target=float(c['local_target'])
    gates=dict(N=float(np.max(abs(a['number_defect'])/(1e-8*np.maximum(a['source_N'],1.)))),E=float(np.max(abs(a['energy_defect'])/(1e-8*np.maximum(a['source_U'],1.)))),parity=float(np.max(abs(a['J1'])/(1e-12*np.maximum(a['J0'],1e-30)))))
    loc=float(np.max(a['local_error'][1:]));assert max(gates.values())<=1 and charge<2e-14 and loc<target
    B0=float(c['energy_budget_ev_per_h']);f=float(c['energy_budget_count_fraction']);cap=int(c['energy_budget_count_cap'])
    budget=B0*((1-f)*np.log1p(np.diff(a['a'])/a['a'][:-1])/np.log(21/5)+f/cap)
    inc=np.diff(a['energy_defect']);ratio=float(np.max(abs(inc)/budget));assert ratio<=1+1e-10 and a['accepted'][-1]<=cap
    ck=(root/'checkpoint.txt').read_text().splitlines();assert ck[0]=='AXBI_CHECKPOINT_V6' and len(ck)==19
    assert float(ck[1].split()[0])==a['a'][-1]
    for i in (4,11,15):
        n,u,lo,hi=[np.fromstring(ck[k],sep=' ') for k in range(i,i+4)]
        assert len(n)==2*int(c['transport_cells']) and np.all(n>=0) and np.all(u>=0)
        assert np.all((n>0)|((u==0)&(lo==0)&(hi==0)))
        assert np.all(u>=lo*n) and np.all(u<=hi*n)
        scale=(1/21)/a['a'][-1];tol=32*np.finfo(float).eps*54.42
        if i==4:assert np.all(hi[n>0]*scale<=24.59+tol) and np.all(lo[n>0]*scale>=13.6-tol)
        elif i==11:assert np.all(lo[n>0]*scale>=54.42-tol)
        else:assert np.all(lo[n>0]*scale>=24.59-tol) and np.all(hi[n>0]*scale<=54.42+tol)
        if i==11:assert abs(n.sum()-a['above_N'][-1])<1e-13
        if i==15:assert abs(n.sum()-a['middle_N'][-1])<1e-13
    row=dict(status=r['status'],accepted=int(r['accepted']),additional=int(r['additional_accepted']),z_end=float(a['zbar'][-1]),wall_s=float(r['segment_wall_s']),gates=gates,charge=charge,max_local=loc,max_abs_E=float(np.max(abs(a['energy_defect']))),sum_abs_E=float(np.sum(abs(inc),dtype=np.longdouble)),allocated=float(np.sum(budget,dtype=np.longdouble)),max_increment_ratio=ratio,raw_path=str(root),hashes={x.name:sha(x) for x in root.iterdir() if x.is_file()})
    return a,row
for name in names:
    cfg=D/(name+'.cfg')
    if not (D/(name+'.exit')).exists():continue
    p=H/('rei_r118c2r_'+name);a,pa=one(p,D/(name+'.exit'),cfg);rows=[pa];t=a
    if (D/(name+'_final.exit')).exists():
        for line in (D/(name+'_prefix.sha256')).read_text().splitlines():
            hh,pp=line.split(maxsplit=1);assert sha(pp)==hh
        x=H/('rei_r118c2r_'+name+'_final')
        assert (x/'initial_checkpoint.txt').read_bytes()==(p/'checkpoint.txt').read_bytes()
        v,pb=one(x,D/(name+'_final.exit'),cfg);rows.append(pb)
        keys=['a','zbar','time_s','x_HII','x_HeII','x_HeIII','temperature_K','active_N','active_U','passive_N','passive_U','energy_defect','number_defect','above_N','middle_N']
        assert all(a[k][-1]==v[k][0] for k in keys)
        t=np.concatenate((a,v[1:]))
    assert t['zbar'][0]==20 and len(t)==int(t['accepted'][-1])+1
    complete=rows[-1]['status']=='COMPLETE_REPRESENTED_INTERVAL'
    if complete:assert t['zbar'][-1]==4
    budget=sum(x['allocated'] for x in rows);defect=sum(x['sum_abs_E'] for x in rows);assert defect<=budget<=1e-8*(1+1e-12)
    f=['x_HII','x_HeII','x_HeIII','temperature_K','Gamma_HI','Gamma_HeI','Gamma_HeII','heat_HeII_erg','above_N','middle_N','absorbed_HeII']
    rr[name]=dict(status='COMPLETE' if complete else 'CHECKPOINTED',q=int(kv(cfg)['transport_cells']),local_target=float(kv(cfg)['local_target']),accepted=int(t['accepted'][-1]),z_end=float(t['zbar'][-1]),tau=float(np.trapezoid(t['ne_proper_cm3']*1e6*299792458.*6.6524587051e-29,t['time_s'])),terminal={k:float(t[k][-1]) for k in f},max_gate=max(x['gates']['E'] for x in rows),abs_increment_sum=defect,allocated_sum=budget,max_increment_ratio=max(x['max_increment_ratio'] for x in rows),rhs=int(t['rhs'][-1]),segments=rows)
    raw[name]=t
    print(name,rr[name]['status'],rr[name]['z_end'],rr[name]['accepted'],rr[name]['terminal'],flush=True)
    for idx,s in enumerate(rows):
        root=Path(s['raw_path'])
        for fname in ('checkpoint.txt','initial_checkpoint.txt','config.cfg','RETURN.txt','source_identity.txt','resource_caps.txt'):
            (D/(name+'_'+str(idx)+'_'+fname+'.gz')).write_bytes(gzip.compress((root/fname).read_bytes(),mtime=0))
assert len(ids)==1
def comp(a,b):
    zmin=max(a['zbar'][-1],b['zbar'][-1]);zz=np.linspace(zmin,20,20001)
    def ip(x,k):return np.interp(zz,x['zbar'][::-1],x[k][::-1])
    keys=['x_HII','x_HeII','x_HeIII','temperature_K','Gamma_HI','Gamma_HeI','Gamma_HeII','heat_HeII_erg','above_N','middle_N','absorbed_HeII']
    out={}
    for k in keys:
        if k not in a.dtype.names or k not in b.dtype.names:continue
        x=ip(a,k);y=ip(b,k)
        out[k]=dict(max_abs=float(np.max(abs(x-y))),max_peak_normalized=float(np.max(abs(x-y))/max(np.max(abs(y)),1e-300)),terminal_delta=float(x[0]-y[0]),terminal_relative=float((x[0]-y[0])/max(abs(y[0]),1e-300)))
    return dict(z_min=float(zmin),fields=out)
comparisons={n:comp(t,raw['q128']) for n,t in raw.items() if n!='q128'}
time_refinement=comp(raw['q64tight'],raw['q64']) if 'q64tight' in raw else None
legacy={n:comp(t,ref) for n,t in raw.items()}
bass_comp={}
for n,r in rr.items():
    if r['status']!='COMPLETE':continue
    t=r['terminal'];bass_comp[n]=dict(HeIII_relative=t['x_HeIII']/b['terminal']['x_HeIII']-1,Gamma_HeII_relative=t['Gamma_HeII']/b['gamma'][2]-1,heat_HeII_relative=(t['heat_HeII_erg']/ev)/b['heat'][2]-1,T_delta=t['temperature_K']-b['terminal']['Tm_K'])
matched_tight=comp(raw['q128tight'],raw['q64tight']) if 'q128tight' in raw else None
time128=comp(raw['q128tight'],raw['q128']) if 'q128tight' in raw else None
# C2Q q64 standard/strict actual history comparison at common redshift
old=j(I/'research/r118c2q_coupled_split/RESULTS.json')
oldcmp={}
for name in ('q64','q128','q64tight'):
    prev=old['cases'][name];pv=[]
    for x in prev['segments']:
        pp=Path(x['raw_path'])/'history.csv';assert sha(pp)==x['hashes']['history.csv'];pv.append(np.genfromtxt(pp,names=True,delimiter=','))
    prev_t=np.concatenate([pv[0]]+[x[1:] for x in pv[1:]])
    oldcmp[name]=comp(raw[name],prev_t)
out=dict(status='SCOPED_COUPLED_MULTITHRESHOLD',matched_tight=matched_tight,time128=time128,c2q_comparison=oldcmp,source_sha=next(iter(ids)),binary_sha=h,example_sha=sha(I/'rust/rei_microphysics/examples/axbi_c2r_multithreshold_segment.rs'),cases=rr,comparisons_to_q128=comparisons,time_refinement=time_refinement,legacy=legacy,bass=bass_comp,scope='FLRW, same actual nonlinear source+gas owner, optional three active pools V6; q/time convergence only represented configurations')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print('BASS comparison',bass_comp)
print('comparisons',json.dumps(comparisons))
