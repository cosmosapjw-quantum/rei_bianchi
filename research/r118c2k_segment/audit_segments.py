"""Audit unchanged-controller continuations and separate refinement controls."""
import argparse,csv,hashlib,json,gzip,re,subprocess
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--old',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--donor',type=Path,required=True);a=p.parse_args()
D=a.out;R=a.root;H=a.old
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def kv(p):return dict(l.split('=',1) for l in p.read_text().splitlines() if '=' in l)
d=json.loads(a.donor.read_text());fhe=d['background']['f_He'];q=d['initial'];dig=sha(a.donor)
old=json.loads(Path('research/r118c2j_error_control/RUNS.json').read_text())
for v in old:
 if v['variant']=='reduced':
  for f in ('checkpoint.txt','config.cfg','source_identity.txt','history.csv'):assert sha(Path(v['raw_path'])/f)==v['hashes'][f]
identity=sha(H/'long32/source_identity.txt')
names=['resume16','resume32','extend16','fresh64','fresh32tight','late32tight']
parents={'resume16':H/'long16','resume32':H/'long32','extend16':R/'resume16','late32tight':H/'long32'}
rows=[];states={}
for n in names:
 root=R/n;ret=kv(root/'RETURN.txt');cfg=kv(root/'config.cfg')
 if n in parents:
  parent=parents[n]
  assert (root/'initial_checkpoint.txt').read_bytes()==(parent/'checkpoint.txt').read_bytes()
  assert sha(root/'source_identity.txt')==sha(parent/'source_identity.txt')==identity
  if n!='late32tight':assert (root/'config.cfg').read_bytes()==(parent/'config.cfg').read_bytes()
  else:
   c=kv(parent/'config.cfg');assert float(cfg['local_target'])==float(c['local_target'])/2
   assert all(cfg[k]==v for k,v in c.items() if k!='local_target')
 else:assert sha(root/'source_identity.txt')==identity
 assert cfg['initial_state_id']=='REC_HMLA_'+dig
 t=np.genfromtxt(root/'history.csv',names=True,delimiter=',')
 assert len(t)==int(ret['additional_accepted'])+1 and t['accepted'][-1]==int(ret['accepted'])
 assert np.all(np.diff(t['accepted'])==1) and np.all(np.diff(t['a'])>0) and np.all(np.diff(t['time_s'])>0)
 assert np.min(t['temperature_K'])>0 and np.all((t['x_HII']>=0)&(t['x_HII']<=1)&(t['x_HeII']>=0)&(t['x_HeIII']>=0)&(t['x_HeII']+t['x_HeIII']<=1))
 for k in ('active_N','active_U','passive_N','passive_U'):assert np.min(t[k])>=0
 ne=t['ne_proper_cm3']/t['nH_proper_cm3'];charge=float(np.max(abs(ne-(t['x_HII']+fhe*(t['x_HeII']+2*t['x_HeIII'])))))
 rn=float(np.max(abs(t['number_defect'])/(1e-8*np.maximum(t['source_N'],1.))))
 ru=float(np.max(abs(t['energy_defect'])/(1e-8*np.maximum(t['source_U'],1.))))
 parity=float(np.max(abs(t['J1'])/(1e-12*np.maximum(t['J0'],1e-30))))
 local=float(np.max(t['local_error'][1:]))
 assert max(rn,ru,parity)<=1 and charge<2e-14 and local<float(cfg['local_target'])
 if n=='extend16':
  cap=kv(root/'resource_caps.txt');assert cap['original_steps']=='220000' and cap['effective_steps']=='320000' and cap['effective_attempts']=='1200000'
 else:cap=kv(root/'resource_caps.txt') if (root/'resource_caps.txt').is_file() else None
 status=ret['status'];assert status in ('COMPLETE_REPRESENTED_INTERVAL','STOPPED_SEGMENT_WALL_CAP','STOPPED_ORIGINAL_ABSOLUTE_CAP')
 if status.startswith('COMPLETE'):assert t['zbar'][-1]==4.
 def term(t):return {k:float(t[k][-1]) for k in ('x_HII','x_HeII','x_HeIII','temperature_K','active_N','active_U','passive_N','passive_U')}
 v=dict(case=n,status=status,config=cfg,resources=cap,accepted=int(ret['accepted']),additional_steps=int(ret['additional_accepted']),segment_wall_s=float(ret['segment_wall_s']),start_z=float(t['zbar'][0]),end_z=float(t['zbar'][-1]),max_gate_ratio=max(rn,ru,parity),gate_ratios=dict(N=rn,E=ru,parity=parity),max_local=local,charge_defect=charge,terminal=term(t),raw_path=str(root),hashes={f.name:sha(f) for f in root.iterdir() if f.is_file()})
 states[n]=t;rows.append(v);print(n,status,v['accepted'],v['end_z'],v['terminal'],max(rn,ru,parity),flush=True)
 for f in ['initial_checkpoint.txt','checkpoint.txt','config.cfg','RETURN.txt','source_identity.txt','resource_caps.txt','input_config.cfg','controller_trial.txt']:
  if (root/f).is_file():(D/(n+'_'+f+'.gz')).write_bytes(gzip.compress((root/f).read_bytes(),mtime=0))
# Build common physical histories including exactly one copy of every checkpoint boundary.
keys=['a','zbar','time_s','nH_proper_cm3','ne_proper_cm3','x_HII','x_HeII','x_HeIII','temperature_K']
def oldhist(n):return np.genfromtxt(H/f'long{n}'/'history.csv',names=True,delimiter=',',usecols=keys)
def pack(t):return np.stack([t[k] for k in keys],axis=1)
def concat(*ts):
 out=pack(ts[0])
 for t in ts[1:]:
  b=pack(t);assert np.allclose(out[-1],b[0],rtol=3e-14,atol=1e-30)
  out=np.concatenate((out,b[1:]),axis=0)
 assert np.all(np.diff(out[:,0])>0) and np.all(np.diff(out[:,2])>0)
 return out
hist={'q16':concat(oldhist(16),states['resume16'],states['extend16']),'q32':concat(oldhist(32),states['resume32']),'q64':pack(states['fresh64']),'early32tight':pack(states['fresh32tight']),'late32':pack(states['resume32']),'late32tight':pack(states['late32tight'])}
def interp(t,z):return np.array([np.interp(z,t[::-1,1],t[::-1,j]) for j in range(5,9)]).T
def tau(t):return float(np.trapezoid(t[:,4]*1e6*299792458.*6.6524587051e-29,t[:,2]))
def compare(x,y):
 l=max(x[-1,1],y[-1,1]);u=min(x[0,1],y[0,1]);zz=np.linspace(l,u,20001)
 a=interp(x,zz);b=interp(y,zz);v=np.abs(a-b);rel=v/np.maximum(np.abs(b),[1e-12,1e-12,1e-8,1e-8])
 return dict(z_range=[float(l),float(u)],max_abs=dict(zip(keys[5:],map(float,v.max(axis=0)))),max_relative=dict(zip(keys[5:],map(float,rel.max(axis=0)))),at_end=dict(zip(keys[5:],map(float,(a-b)[0]))))
full={}
for k in ('q16','q32','q64'):
 t=hist[k];assert t[0,1]==20 and t[-1,1]==4
 full[k]=dict(steps=len(t)-1,tau=tau(t),terminal=dict(zip(keys[5:],map(float,t[-1,5:]))))
comparisons={f'{a}_vs_{b}':compare(hist[a],hist[b]) for a,b in [('q16','q32'),('q32','q64'),('early32tight','q32'),('late32tight','late32')]}
zs=[19.98,18,15,14.253743337980149,12,10,9,8,7,6,5.830240858322552,5,4]
common=[]
for z in zs:
 v={'z':z}
 for k,t in hist.items():
  if t[-1,1]<=z<=t[0,1]:v[k]=dict(zip(keys[5:],map(float,interp(t,np.array([z]))[0])))
 common.append(v)
summary=dict(scope='three completed q-resolution histories at same local target; early-only tighter IC and independent late controller trial; no global time convergence theorem',full=full,comparisons=comparisons,common=common,late_tau={k:tau(hist[k]) for k in ('late32','late32tight')},donor_sha256=dig,source_identity_sha256=identity)
(D/'COMPARISON.json').write_text(json.dumps(summary,indent=2)+'\n')
(D/'RUNS.json').write_text(json.dumps(rows,indent=2)+'\n')
# Save thin actual history for plots, NOT as accepted-state replacement.
for k,t in hist.items():
 np.savez_compressed(D/(k+'_THIN.npz'),columns=np.array(keys),history=t[np.unique(np.r_[np.arange(0,len(t),100),len(t)-1])])
print('FULL',json.dumps(full,indent=2));print('COMPARISONS',json.dumps(comparisons,indent=2));print('LATE TAU',summary['late_tau'])
