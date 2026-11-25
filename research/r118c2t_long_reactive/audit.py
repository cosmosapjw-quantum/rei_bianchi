import hashlib,json,gzip,re
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;I=D.parents[1];H=Path('/home/cosmosapjw/Downloads');B=Path('/home/cosmosapjw/worktrees/bass-r109-native-20261124/research/r118c2t_thomson_sky')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def kv(p):return dict(x.split('=',1) for x in p.read_text().splitlines() if '=' in x)
def j(p):return json.loads(p.read_text())
for file in ('BINARY.sha256','EXT_BINARY.sha256'):
 for line in (D/file).read_text().splitlines():
  h,p=line.split(maxsplit=1);assert sha(p)==h
prior=j(I/'research/r118c2s_reactive/RESULTS.json');old_id=prior['source_sha'];new_ids=set()
def segment(root,cfg,ext):
 ret=kv(root/'RETURN.txt');c=kv(cfg);r=np.genfromtxt(root/'history.csv',names=True,delimiter=',')
 assert (root/'config.cfg').read_bytes()==cfg.read_bytes()
 ident=sha(root/'source_identity.txt')
 if ext:
  new_ids.add(ident);assert ident!=old_id and (I/'rust/rei_microphysics/src/axbi_covariant_driver.rs').read_text() in (root/'source_identity.txt').read_text()
 else:assert ident==old_id
 assert len(r)==int(ret['additional_accepted'])+1 and int(r['accepted'][0])==int(ret['initial_accepted']) and int(r['accepted'][-1])==int(ret['accepted'])
 assert np.all(np.diff(r['a'])>0) and np.all(np.diff(r['time_s'])>0) and np.all(np.diff(r['accepted'])==1) and np.all(np.isfinite(r.view(float)))
 assert np.all(r['temperature_K']>0) and np.all((r['x_HII']>=0)&(r['x_HII']<=1)&(r['x_HeII']>=0)&(r['x_HeIII']>=0)&(r['x_HeII']+r['x_HeIII']<=1))
 for k in ('active_N','active_U','passive_N','passive_U','above_N','middle_N','Gamma_HI','Gamma_HeI','Gamma_HeII','heat_HI_erg','heat_HeI_erg','heat_HeII_erg'):assert np.min(r[k])>=0
 assert np.all(r['above_N']+r['middle_N']<=r['active_N']*(1+1e-12))
 he=.2454/(4*(1-.2454));charge=float(np.max(abs(r['ne_proper_cm3']/r['nH_proper_cm3']-r['x_HII']-he*(r['x_HeII']+2*r['x_HeIII']))))
 gates=dict(N=float(np.max(abs(r['number_defect'])/(1e-8*np.maximum(r['source_N'],1.)))),E=float(np.max(abs(r['energy_defect'])/(1e-8*np.maximum(r['source_U'],1.)))),parity=float(np.max(abs(r['J1'])/(1e-12*np.maximum(r['J0'],1e-30)))))
 loc=float(np.max(r['local_error'][1:]));assert max(gates.values())<=1 and charge<2e-14 and loc<float(c['local_target'])
 budget=float(c['energy_budget_ev_per_h'])*((1-float(c['energy_budget_count_fraction']))*np.log1p(np.diff(r['a'])/r['a'][:-1])/np.log(21/5)+float(c['energy_budget_count_fraction'])/int(c['energy_budget_count_cap']))
 inc=np.diff(r['energy_defect']);ratio=float(np.max(abs(inc)/budget));assert ratio<=1+1e-10 and np.sum(abs(inc))<=np.sum(budget)
 ck=(root/'checkpoint.txt').read_text().splitlines();assert ck[0]=='AXBI_CHECKPOINT_V7' and len(ck)==23
 a,_,b=map(float,ck[1].split()[:3]);assert a==r['a'][-1]
 nbase=int(c['transport_cells']);ne=nbase+int(c.get('reactive_extra_high_cells',0));mu,_=np.polynomial.legendre.leggauss(int(c['n_mu']));sc=(1/21)/a*np.sqrt((1-mu*mu)*np.exp(2*b)+mu*mu*np.exp(-4*b))
 assert abs(sc.max()-r['max_ray_scale'][-1])<2e-14 and abs(sc.min()-r['min_ray_scale'][-1])<2e-14
 sc=np.repeat(sc,ne);tol=64*np.finfo(float).eps*54.42
 assert all(np.all(np.fromstring(ck[i],sep=' ')==0) for i in (8,9))
 count=[];energy=[]
 for i,l,h0 in [(19,0,13.6),(4,13.6,24.59),(15,24.59,54.42),(11,54.42,np.inf)]:
  n,u,lo,hi=[np.fromstring(ck[k],sep=' ') for k in range(i,i+4)]
  assert len(n)==len(sc) and np.all(n>=0) and np.all(u>=0) and np.all((n>0)|((u==0)&(lo==0)&(hi==0)))
  assert np.all(u>=lo*n) and np.all(u<=hi*n)
  mask=n>0;assert np.all(lo[mask]*sc[mask]>=l-tol) and np.all(hi[mask]*sc[mask]<=h0+tol)
  count.append(float(n.sum()));energy.append(float(u@sc))
 assert abs(count[0]-r['passive_N'][-1])<1e-12 and abs(sum(count[1:])-r['active_N'][-1])<1e-12
 assert abs(energy[0]-r['passive_U'][-1])<1e-11 and abs(sum(energy[1:])-r['active_U'][-1])<1e-11
 row=dict(status=ret['status'],accepted=int(ret['accepted']),additional=int(ret['additional_accepted']),z_end=float(r['zbar'][-1]),source_identity=ident,wall=float(ret['segment_wall_s']),gates=gates,charge=charge,max_local=loc,max_increment_ratio=ratio,max_abs_E=float(np.max(abs(r['energy_defect']))),sum_abs_E=float(np.sum(abs(inc))),allocated=float(np.sum(budget)),band_N=count,band_U=energy,raw_path=str(root),hashes={p.name:sha(p) for p in root.iterdir() if p.is_file()})
 return r,row
cases={};data={}
for name in ('strong8','strong16','weak8'):
 base=H/('rei_r118c2t_'+name);cont=H/('rei_r118c2t_'+name+'_cont');cfg=D/(name+'.cfg')
 for f in (name+'.exit',name+'.cont.exit'):assert int((D/f).read_text())==0
 for line in (D/(name+'.prefix.sha256')).read_text().splitlines():
  h,p=line.split(maxsplit=1);assert sha(p)==h
 assert (cont/'initial_checkpoint.txt').read_bytes()==(base/'checkpoint.txt').read_bytes()
 a,pa=segment(base,cfg,False);b,pb=segment(cont,cfg,False);assert pa['status']=='STOPPED_SEGMENT_WALL_CAP'
 keys=['a','zbar','time_s','x_HII','x_HeII','x_HeIII','temperature_K','active_N','active_U','passive_N','passive_U','energy_defect','number_defect','above_N','middle_N']
 assert all(a[k][-1]==b[k][0] for k in keys)
 t=np.concatenate((a,b[1:]));ss=[pa,pb];migration=None
 if name.startswith('strong'):
  ex=H/('rei_r118c2t_'+name+'_extended');mig=H/('rei_r118c2t_'+name+'_migrated')
  assert int((D/(name+'.extended.exit')).read_text())==int((D/(name+'.migrate.exit')).read_text())==0
  rec=j(D/(name+'.migration_input.json'))
  for f,h in rec['source_hashes'].items():assert sha(cont/f)==h
  assert sha(D/(name+'.adjusted.ck'))==rec['adjusted_checkpoint_sha'] and sha(D/(name+'.extended.cfg'))==rec['new_config_sha']
  assert (ex/'initial_checkpoint.txt').read_bytes()==(mig/'checkpoint.txt').read_bytes()
  original=(cont/'checkpoint.txt').read_text().splitlines();adjusted=(D/(name+'.adjusted.ck')).read_text().splitlines();new=(mig/'checkpoint.txt').read_text().splitlines()
  assert original[0]==adjusted[0]==new[0]=='AXBI_CHECKPOINT_V7'
  assert original[3:]==adjusted[3:] and original[1].split()[:7]==adjusted[1].split()[:7] and original[2].split()[:3]==adjusted[2].split()[:3]
  assert np.array_equal(np.fromstring(adjusted[1],sep=" ").view(np.uint64),np.fromstring(new[1],sep=" ").view(np.uint64)) and adjusted[2].split()==new[2].split() and adjusted[3]==new[3] and adjusted[10]==new[10]
  for k in list(range(4,10))+list(range(11,23)):
   x=np.fromstring(adjusted[k],sep=' ').reshape(-1,32);y=np.fromstring(new[k],sep=' ').reshape(-1,35)
   assert np.array_equal(x,y[:,:32]) and np.all(y[:,32:]==0)
  z,pz=segment(ex,D/(name+'.extended.cfg'),True)
  assert all(abs(t[k][-1]-z[k][0])<=1e-13*max(abs(t[k][-1]),1.) for k in keys)
  t=np.concatenate((t,z[1:]));ss.append(pz);migration=dict(input=rec,migrated_path=str(mig),migrated_hashes={p.name:sha(p) for p in mig.iterdir() if p.is_file()},envelope=kv(mig/'MIGRATION.txt'))
  assert migration['envelope']['old_inventory']==migration['envelope']['new_inventory'] and migration['envelope']['old_residual']==migration['envelope']['new_residual']
 assert ss[-1]['status']=='COMPLETE_REPRESENTED_INTERVAL' and t['zbar'][0]==20 and t['zbar'][-1]==4 and len(t)==int(t['accepted'][-1])+1
 allocated=sum(x['allocated'] for x in ss);defect=sum(x['sum_abs_E'] for x in ss);assert defect<=allocated<=1e-8
 fields=('x_HII','x_HeII','x_HeIII','temperature_K','Gamma_HI','Gamma_HeI','Gamma_HeII','J0','J2','passive_N','active_N')
 cases[name]=dict(accepted=int(t['accepted'][-1]),z_end=4.,tau=float(np.trapezoid(t['ne_proper_cm3']*1e6*299792458.*6.6524587051e-29,t['time_s'])),terminal={k:float(t[k][-1]) for k in fields},max_E_gate=max(x['gates']['E'] for x in ss),sum_abs_E=defect,allocated=allocated,segments=ss,migration=migration)
 data[name]=t
 for i,s in enumerate(ss):
  root=Path(s['raw_path'])
  for f in ('checkpoint.txt','initial_checkpoint.txt','config.cfg','RETURN.txt','source_identity.txt','resource_caps.txt'):
   (D/(name+'_'+str(i)+'_'+f+'.gz')).write_bytes(gzip.compress((root/f).read_bytes(),mtime=0))
 print(name,cases[name]['accepted'],cases[name]['terminal'],cases[name]['tau'],defect,flush=True)
assert len(new_ids)==1
a=data['strong8'];b=data['strong16'];zz=np.linspace(4,20,20001);comp={}
for k in ('x_HII','x_HeII','x_HeIII','temperature_K','Gamma_HI','Gamma_HeI','Gamma_HeII','passive_N','J2'):
 x=np.interp(zz,a['zbar'][::-1],a[k][::-1]);y=np.interp(zz,b['zbar'][::-1],b[k][::-1]);comp[k]=dict(terminal_relative=float((x[0]-y[0])/max(abs(y[0]),1e-300)),max_peak_normalized=float(np.max(abs(x-y))/max(np.max(abs(y)),1e-300)))
# Bridge: independently integrated BASS ray vs general REI canonical coframe map.
bridge=[]
for n in (128,256,512):
 p=B/f'handoff_{n}_bass.csv';q=D/f'handoff_{n}_rei.csv';inp=B/f'handoff_{n}_input.csv'
 x=np.genfromtxt(p,names=True,delimiter=',');y=np.genfromtxt(q,names=True,delimiter=',');assert len(x)==len(y)==64
 for k in ('id','case','u'):assert np.array_equal(x[k],y[k])
 row=dict(n=n,energy=float(np.max(abs(x['energy_scale']/y['energy_scale']-1))),jacobian=float(np.max(abs(x['jacobian']/y['jacobian']-1))),direction=float(max(np.max(abs(x[k]-y[k])) for k in ('nx','ny','nz'))),input_sha=sha(inp),bass_sha=sha(p),rei_sha=sha(q))
 bridge.append(row)
assert bridge[-1]['energy']<3e-8 and bridge[-1]['jacobian']<1e-7 and bridge[0]['energy']/bridge[-1]['energy']>15
tests=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored',(D/'full_tests.log').read_text());assert sum(int(x[1]) for x in tests)==340 and all(x[0]=='ok' for x in tests)
assert all(int((D/f).read_text())==0 for f in ('green.exit','build_extended.exit','ray_green.exit','ray_build.exit','handoff.exit','full_tests.exit'))
out=dict(status='PASS_SCOPED_V7_LONG_WITH_EXPLICIT_PREFIX_EXTENSION',parent='8d38e28feeb76e39730f16ac3b54fde6ab40092f',cases=cases,angular_comparison=comp,bridge=bridge,full_rust_tests=340,full_trajectories=3,total_steps=sum(r['accepted'] for r in cases.values()),max_E_gate=max(r['max_E_gate'] for r in cases.values()),old_source=old_id,new_source=next(iter(new_ids)),production_admission='HOLD_FRESH_EXTENDED_CONTROL_AND_FULL_GENERAL_ANGLE_GAS_DRIVER',native_subagent='NOT_RUN')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print('angular',comp,'bridge',bridge,flush=True)
