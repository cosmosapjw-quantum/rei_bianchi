import json,hashlib,gzip,re
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;I=D.parents[1];H=Path('/home/cosmosapjw/Downloads')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def kv(p):return dict(x.split('=',1) for x in p.read_text().splitlines() if '=' in x)
h,p=(D/'BINARY.sha256').read_text().split(maxsplit=1);assert sha(p.strip())==h
cases={};ids=set();data={}
for name in ('minus32','minus64','plus32','zero32','minustight32'):
 root=H/('rei_r118c2s_'+name);cfg=D/(name+'.cfg');ret=kv(root/'RETURN.txt');c=kv(cfg)
 assert int((D/(name+'.exit')).read_text())==0 and ret['status']=='COMPLETE_REPRESENTED_INTERVAL'
 assert (root/'config.cfg').read_bytes()==cfg.read_bytes()
 ident=(root/'source_identity.txt').read_text()
 for fname in ('axbi_covariant_driver.rs','axbi_covariant_transport.rs','axbi_heii_split.rs','axbi_multithreshold.rs','axbi_reactive_bands.rs'):
  assert (I/'rust/rei_microphysics/src'/fname).read_text() in ident
 ids.add(sha(root/'source_identity.txt'));r=np.genfromtxt(root/'history.csv',names=True,delimiter=',')
 assert len(r)==int(ret['accepted'])+1 and r['accepted'][0]==0 and np.all(np.diff(r['accepted'])==1)
 assert r['zbar'][0]==20 and r['zbar'][-1]==19.8 and np.all(np.diff(r['a'])>0) and np.all(np.diff(r['time_s'])>0) and np.all(np.isfinite(r.view(float)))
 assert np.all(r['temperature_K']>0) and np.all((r['x_HII']>=0)&(r['x_HII']<=1)&(r['x_HeII']>=0)&(r['x_HeIII']>=0)&(r['x_HeII']+r['x_HeIII']<=1))
 for k in ('active_N','active_U','passive_N','passive_U','above_N','middle_N','Gamma_HI','Gamma_HeI','Gamma_HeII','heat_HI_erg','heat_HeI_erg','heat_HeII_erg'):assert np.min(r[k])>=0
 assert np.all(r['above_N']+r['middle_N']<=r['active_N']*(1+1e-12))
 fhe=.2454/(4*(1-.2454));charge=float(np.max(abs(r['ne_proper_cm3']/r['nH_proper_cm3']-r['x_HII']-fhe*(r['x_HeII']+2*r['x_HeIII']))))
 gates=dict(N=float(np.max(abs(r['number_defect'])/(1e-8*np.maximum(r['source_N'],1.)))),E=float(np.max(abs(r['energy_defect'])/(1e-8*np.maximum(r['source_U'],1.)))),parity=float(np.max(abs(r['J1'])/(1e-12*np.maximum(r['J0'],1e-30)))))
 loc=float(np.max(r['local_error'][1:]));assert max(gates.values())<=1 and charge<2e-14 and loc<float(c['local_target'])
 budget=float(c['energy_budget_ev_per_h'])*((1-float(c['energy_budget_count_fraction']))*np.log1p(np.diff(r['a'])/r['a'][:-1])/np.log(21/20.8)+float(c['energy_budget_count_fraction'])/int(c['energy_budget_count_cap']))
 inc=np.diff(r['energy_defect']);ratio=float(np.max(abs(inc)/budget));assert ratio<=1+1e-10 and np.sum(abs(inc))<=np.sum(budget)<=1e-8
 ck=(root/'checkpoint.txt').read_text().splitlines();assert ck[0]=='AXBI_CHECKPOINT_V7' and len(ck)==23
 a,_,b=map(float,ck[1].split()[:3]);assert a==r['a'][-1]
 mu,_=np.polynomial.legendre.leggauss(int(c['n_mu']));sc=(1/21)/a*np.sqrt((1-mu*mu)*np.exp(2*b)+mu*mu*np.exp(-4*b))
 assert abs(sc.max()-r['max_ray_scale'][-1])<2e-14 and abs(sc.min()-r['min_ray_scale'][-1])<2e-14
 sc=np.repeat(sc,int(c['transport_cells']));tol=64*np.finfo(float).eps*54.42
 assert all(np.all(np.fromstring(ck[i],sep=' ')==0) for i in (8,9))
 count=[];energy=[]
 for i,l,h0 in [(19,0,13.6),(4,13.6,24.59),(15,24.59,54.42),(11,54.42,np.inf)]:
  n,u,lo,hi=[np.fromstring(ck[k],sep=' ') for k in range(i,i+4)]
  assert len(n)==len(sc) and np.all(n>=0) and np.all(u>=0) and np.all((n>0)|((u==0)&(lo==0)&(hi==0)))
  assert np.all(u>=lo*n) and np.all(u<=hi*n)
  mask=n>0;assert np.all(lo[mask]*sc[mask]>=l-tol) and np.all(hi[mask]*sc[mask]<=h0+tol)
  count.append(float(n.sum()));energy.append(float(u@sc))
 assert abs(count[0]-r['passive_N'][-1])<1e-13 and abs(sum(count[1:])-r['active_N'][-1])<1e-13
 assert abs(energy[0]-r['passive_U'][-1])<1e-13 and abs(sum(energy[1:])-r['active_U'][-1])<1e-13
 fields=['x_HII','x_HeII','x_HeIII','temperature_K','Gamma_HI','Gamma_HeI','Gamma_HeII','max_ray_scale','min_ray_scale','J0','J2','passive_N','active_N']
 row=dict(q_ref=float(c['q_ref']),q=int(c['transport_cells']),target=float(c['local_target']),accepted=int(ret['accepted']),rhs=int(r['rhs'][-1]),z_end=float(r['zbar'][-1]),gates=gates,charge=charge,max_local=loc,max_increment_ratio=ratio,max_abs_E=float(np.max(abs(r['energy_defect']))),sum_abs_E=float(np.sum(abs(inc))),allocated=float(np.sum(budget)),band_N=count,band_U=energy,terminal={k:float(r[k][-1]) for k in fields},raw_path=str(root),hashes={p.name:sha(p) for p in root.iterdir() if p.is_file()})
 cases[name]=row;data[name]=r
 for f in ('checkpoint.txt','initial_checkpoint.txt','config.cfg','RETURN.txt','source_identity.txt','resource_caps.txt'):
  (D/(name+'_'+f+'.gz')).write_bytes(gzip.compress((root/f).read_bytes(),mtime=0))
 print(name,row['accepted'],row['terminal'],gates,row['sum_abs_E'],flush=True)
assert len(ids)==1 and cases['minus32']['terminal']['max_ray_scale']>1 and cases['plus32']['terminal']['max_ray_scale']<1
comp={}
for n in ('minus64','minustight32'):
 v=cases[n]['terminal'];w=cases['minus32']['terminal']
 comp[n]={k:dict(delta=v[k]-w[k],relative=(v[k]-w[k])/max(abs(w[k]),1e-300)) for k in ('x_HII','x_HeII','x_HeIII','temperature_K','Gamma_HI','Gamma_HeI','Gamma_HeII','passive_N')}
tests=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored',(D/'full_tests.log').read_text());assert sum(int(x[1]) for x in tests)==338 and all(x[0]=='ok' for x in tests)
assert all(int((D/f).read_text())==0 for f in ('green.exit','reactivation.exit','full_tests.exit','build.exit'))
line=next(x for x in (D/'reactivation.log').read_text().splitlines() if x.startswith('reactivated gamma='))
res=dict(status='PASS_SCOPED_V7_REACTIVE_SHORT_LRS_COUPLED',parent='46516fcdaa4abfe5833e5fb503fcab89b9b95a23',cases=cases,comparisons=comp,full_trajectories=5,total_steps=sum(x['accepted'] for x in cases.values()),full_rust_tests=338,source_sha=next(iter(ids)),binary_sha=h,reactivation_fixture=line,production_admission='HOLD_LONG_NONFLRW_TRAJECTORY_AND_FULL_BASS_GEOMETRY',native_subagent='NOT_RUN')
(D/'RESULTS.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n')
print('comparisons',comp,'reactivation',line)
