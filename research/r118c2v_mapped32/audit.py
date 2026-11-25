import hashlib,json,gzip,re
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;I=D.parents[1];H=Path('/home/cosmosapjw/Downloads')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def kv(p):return dict(x.split('=',1) for x in p.read_text().splitlines() if '=' in x)
def j(p):return json.loads(p.read_text())
prior=j(D.parent/'r118c2u_angular/RESULTS.json')
oldid=prior['cases']['map16']['segments'][0]['source_identity']
ids=set()
for f in ('BINARY.sha256','ANGLE_INPUT.sha256'):
 for line in (D/f).read_text().splitlines():
  h,p=line.split(maxsplit=1);assert sha(p)==h
cases={};data={}
for name,suffixes in [('map32',[str(i) for i in range(4) if (D/f'map32_{i}.sha256').exists()])]:
 cfg=D/(name+'.cfg');c=kv(cfg);nmu=int(c['n_mu']);ne=int(c['transport_cells'])+int(c['reactive_extra_high_cells']);rmap=float(c.get('angular_map_ratio',1))
 ss=[];arr=[];last=None
 for i,suf in enumerate(suffixes):
  root=H/('rei_r118c2v_'+name+'_'+suf);ret=kv(root/'RETURN.txt')
  assert int((D/f'{name}_{suf}.exit').read_text())==0
  for line in (D/f'{name}_{suf}.sha256').read_text().splitlines():
   hh,p=line.split(maxsplit=1);assert sha(p)==hh
  assert (root/'config.cfg').read_bytes()==cfg.read_bytes()
  ident=sha(root/'source_identity.txt')
  assert ident==oldid;ids.add(ident)
  if last:assert (last/'checkpoint.txt').read_bytes()==(root/'initial_checkpoint.txt').read_bytes()
  a=np.genfromtxt(root/'history.csv',names=True,delimiter=',')
  assert len(a)==int(ret['additional_accepted'])+1 and int(a['accepted'][0])==int(ret['initial_accepted']) and int(a['accepted'][-1])==int(ret['accepted'])
  assert np.all(np.diff(a['a'])>0) and np.all(np.diff(a['time_s'])>0) and np.all(np.diff(a['accepted'])==1) and np.all(np.isfinite(a.view(float)))
  assert np.all(a['temperature_K']>0) and np.all((a['x_HII']>=0)&(a['x_HII']<=1)&(a['x_HeII']>=0)&(a['x_HeIII']>=0)&(a['x_HeII']+a['x_HeIII']<=1))
  for k in ('active_N','active_U','passive_N','passive_U','above_N','middle_N','Gamma_HI','Gamma_HeI','Gamma_HeII','heat_HI_erg','heat_HeI_erg','heat_HeII_erg'):assert np.min(a[k])>=0
  assert np.all(a['above_N']+a['middle_N']<=a['active_N']*(1+1e-12))
  he=.2454/(4*(1-.2454));charge=float(np.max(abs(a['ne_proper_cm3']/a['nH_proper_cm3']-a['x_HII']-he*(a['x_HeII']+2*a['x_HeIII']))))
  gates=dict(N=float(np.max(abs(a['number_defect'])/(1e-8*np.maximum(a['source_N'],1.)))),E=float(np.max(abs(a['energy_defect'])/(1e-8*np.maximum(a['source_U'],1.)))),parity=float(np.max(abs(a['J1'])/(1e-12*np.maximum(a['J0'],1e-30)))))
  loc=float(np.max(a['local_error'][1:]));assert max(gates.values())<=1 and charge<2e-14 and loc<float(c['local_target'])
  budget=float(c['energy_budget_ev_per_h'])*((1-float(c['energy_budget_count_fraction']))*np.log1p(np.diff(a['a'])/a['a'][:-1])/np.log(21/5)+float(c['energy_budget_count_fraction'])/int(c['energy_budget_count_cap']))
  inc=np.diff(a['energy_defect']);ratio=float(np.max(abs(inc)/budget));assert ratio<=1+1e-10 and np.sum(abs(inc))<=np.sum(budget)
  ck=(root/'checkpoint.txt').read_text().splitlines();assert ck[0]=='AXBI_CHECKPOINT_V7' and len(ck)==23
  aa,_,b=map(float,ck[1].split()[:3]);assert aa==a['a'][-1]
  xi,w=np.polynomial.legendre.leggauss(nmu);den=np.sqrt(1-xi*xi+rmap*rmap*xi*xi);mu=rmap*xi/den
  sc=(1/21)/aa*np.sqrt((1-mu*mu)*np.exp(2*b)+mu*mu*np.exp(-4*b));m=mu*np.exp(-2*b)*(1/21)/aa/sc
  assert abs(sc.max()-a['max_ray_scale'][-1])<2e-14 and abs(sc.min()-a['min_ray_scale'][-1])<2e-14
  rep=np.repeat(sc,ne);tol=64*np.finfo(float).eps*54.42
  assert all(np.all(np.fromstring(ck[k],sep=' ')==0) for k in (8,9))
  count=[];energy=[]
  for k,l,hh in [(19,0,13.6),(4,13.6,24.59),(15,24.59,54.42),(11,54.42,np.inf)]:
   n,u,lo,hi=[np.fromstring(ck[q],sep=' ') for q in range(k,k+4)]
   assert len(n)==nmu*ne and np.all(n>=0) and np.all(u>=0) and np.all((n>0)|((u==0)&(lo==0)&(hi==0)))
   assert np.all(u>=lo*n) and np.all(u<=hi*n)
   mask=n>0;assert np.all(lo[mask]*rep[mask]>=l-tol) and np.all(hi[mask]*rep[mask]<=hh+tol)
   count.append(float(n.sum()));energy.append(float(u@rep))
  assert abs(count[0]-a['passive_N'][-1])<1e-12 and abs(sum(count[1:])-a['active_N'][-1])<1e-12
  U=sum(np.fromstring(ck[k],sep=' ').reshape(nmu,ne).sum(axis=1) for k in (5,9,12,16,20))*sc
  J0=float(U.sum());J2=float(U@((3*m*m-1)/2))
  assert abs(J0-a['J0'][-1])<1e-11 and abs(J2-a['J2'][-1])<1e-11
  if arr:
   keys=['a','zbar','time_s','x_HII','x_HeII','x_HeIII','temperature_K','active_N','active_U','passive_N','passive_U','energy_defect','number_defect','above_N','middle_N']
   assert all(arr[-1][k][-1]==a[k][0] for k in keys)
  arr.append(a);last=root
  ss.append(dict(status=ret['status'],accepted=int(ret['accepted']),additional=int(ret['additional_accepted']),z_end=float(a['zbar'][-1]),wall=float(ret['segment_wall_s']),source_identity=ident,gates=gates,charge=charge,max_local=loc,max_increment_ratio=ratio,sum_abs_E=float(np.sum(abs(inc))),allocated=float(np.sum(budget)),band_N=count,band_U=energy,J0=J0,J2=J2,raw_path=str(root),hashes={f.name:sha(f) for f in root.iterdir() if f.is_file()}))
  for f in ('checkpoint.txt','initial_checkpoint.txt','config.cfg','RETURN.txt','source_identity.txt','resource_caps.txt'):
   (D/(name+'_'+str(i)+'_'+f+'.gz')).write_bytes(gzip.compress((root/f).read_bytes(),mtime=0))
 t=np.concatenate([arr[0]]+[x[1:] for x in arr[1:]])
 assert len(t)==int(t['accepted'][-1])+1 and t['zbar'][0]==20 and sum(x['sum_abs_E'] for x in ss)<=sum(x['allocated'] for x in ss)<=1e-8
 assert t['accepted'][-1]<=80000 and sum(x['wall'] for x in ss)<1081
 assert (t['zbar'][-1]==4)==(ss[-1]['status']=='COMPLETE_REPRESENTED_INTERVAL')
 fields=('x_HII','x_HeII','x_HeIII','temperature_K','Gamma_HI','Gamma_HeI','Gamma_HeII','J0','J2','passive_N','active_N')
 cases[name]=dict(status=ss[-1]['status'],accepted=int(t['accepted'][-1]),z_end=float(t['zbar'][-1]),tau=float(np.trapezoid(t['ne_proper_cm3']*1e6*299792458.*6.6524587051e-29,t['time_s'])),terminal={k:float(t[k][-1]) for k in fields},sum_abs_E=sum(x['sum_abs_E'] for x in ss),max_E_gate=max(x['gates']['E'] for x in ss),segments=ss)
 data[name]=t
 print(name,cases[name]['accepted'],cases[name]['z_end'],cases[name]['terminal'],cases[name]['tau'],flush=True)

assert len(ids)==1
assert int((D/'campaign.exit').read_text())==0 and int((D/'supplement.exit').read_text())==0
old=prior['cases']['map16'];parts=[]
for seg in old['segments']:
 p=Path(seg['raw_path'])/'history.csv';assert sha(p)==seg['hashes']['history.csv'];parts.append(np.genfromtxt(p,names=True,delimiter=','))
oldhist=np.concatenate([parts[0]]+[x[1:] for x in parts[1:]])
new=data['map32'];zmin=float(new['zbar'][-1]);zz=np.linspace(zmin,20,20001)
comp={}
for k in ('J0','J2','x_HII','x_HeIII','temperature_K','Gamma_HI','Gamma_HeI','Gamma_HeII','passive_N'):
 a=np.interp(zz,oldhist['zbar'][::-1],oldhist[k][::-1]);b=np.interp(zz,new['zbar'][::-1],new[k][::-1])
 comp[k]=dict(terminal_delta=float(b[0]-a[0]),terminal_relative=float((b[0]-a[0])/max(abs(a[0]),1e-300)),max_peak_normalized=float(max(abs(a-b))/max(max(abs(b)),1e-300)))
ang=np.genfromtxt(D/'GENERAL_ANGULAR.csv',names=True,delimiter=',',dtype=None,encoding='utf8')
assert len(ang)==12 and max(ang['max_dipole'])<1e-12
q=ang[(ang['case']=='strong_lrs')&(ang['mode']=='balanced')];assert q[-1]['max_stf_pressure']<2e-11
tests=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored',(D/'full_tests.log').read_text());assert sum(int(x[1]) for x in tests)==342 and all(x[0]=='ok' for x in tests)
assert all(int((D/f).read_text())==0 for f in ('angle_green.exit','angle_build.exit','angle_run.exit','full_tests.exit'))
out=dict(status='SCOPED_MAPPED32_COMPLETE' if zmin==4 else 'SCOPED_MAPPED32_RESOURCE_STOP',parent='7d81bd20dedbc1efcef5e411f0dc991340ef9b46',case=cases['map32'],comparison=comp,prior_map16=old,full_rust_tests=342,angular=[{k:r[k].item() for k in ang.dtype.names} for r in ang],source_identity=oldid,production_admission='HOLD_GENERAL_COFRAME_GAS_AND_MATCHED_TIME_FREQUENCY',native_subagent='NOT_RUN')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print('comparison',comp,'angular',q)
