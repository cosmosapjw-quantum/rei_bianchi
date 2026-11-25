"""Read all actual recovered covariant histories, with incomplete cap separate."""
import argparse,csv,json,hashlib
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--binary',type=Path,required=True);p.add_argument('--donor',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
d=json.loads(a.donor.read_text());fhe=d['background']['f_He'];q=d['initial'];dig=sha(a.donor);rows=[]
for cfg in sorted(a.root.glob('*.cfg')):
 name=cfg.stem;root=a.root/name;rc=int((a.root/(name+'.exit')).read_text());r=dict(v.split('=',1) for v in (root/'RETURN.txt').read_text().splitlines() if '=' in v)
 assert (root/'initial_state_id.txt').read_text()=='REC_HMLA_'+dig
 h=np.genfromtxt(root/'history.csv',names=True,delimiter=',',dtype=None,encoding='utf8')
 assert len(h)==int(r['accepted'])+1 and h['zbar'][0]==20 and np.all(np.diff(h['time_s'])>0)
 assert abs(h['x_HII'][0]/q['x_HII']-1)<2e-14 and abs(h['temperature_K'][0]/q['T_m_K']-1)<2e-14
 assert np.all((h['x_HII']>=0)&(h['x_HII']<=1)&(h['x_HeII']>=0)&(h['x_HeIII']>=0)&(h['x_HeII']+h['x_HeIII']<=1))
 assert np.min(h['temperature_K'])>0 and np.min(h['photon_n_per_H'])>=0
 xe=h['ne_proper_cm3']/h['nH_proper_cm3'];assert np.max(abs(xe-(h['x_HII']+fhe*(h['x_HeII']+2*h['x_HeIII']))))<2e-14
 tau=float(np.trapezoid(h['ne_proper_cm3']*1e6*299792458.*6.6524587051e-29,h['time_s']))
 ratios={};gates=0
 with (root/'ledgers.csv').open() as f:
  for v in csv.DictReader(f):
   if v['status']=='VALUE':continue
   assert v['status']=='PASS',v
   ratio=abs(float(v['residual']))/float(v['tolerance'])
   assert ratio<=1
   k=v['ledger_name'];ratios[k]=max(ratios.get(k,0.),ratio);gates+=1
 assert gates==3*len(h)
 if rc==0:assert r['status']=='COMPLETE_REPRESENTED_INTERVAL' and abs(h['zbar'][-1]-19.98)<1e-12;status='PASS_SCOPED'
 else:assert name=='long_q16' and r['status']=='STOPPED_CHECKPOINTED' and 'AXBI_RUNTIME_CAP' in r['result'] and (root/'checkpoint.txt').is_file();status='STOPPED_CHECKPOINTED_RESOURCE'
 row=dict(case=name,status=status,returncode=rc,accepted=int(r['accepted']),wall_s=float(r['wall_s']),max_newton=float(r['max_newton_residual']),final_z=float(h['zbar'][-1]),tau_represented=tau,gate_rows=gates,gate_ratios=ratios,terminal={k:float(h[k][-1]) for k in ('x_HII','x_HeII','x_HeIII','temperature_K','photon_n_per_H','photon_u_eV_per_H')},config=cfg.read_text(),config_sha256=sha(cfg),hashes={str(f.relative_to(root)):sha(f) for f in root.rglob('*') if f.is_file()})
 print(name,status,row['accepted'],row['final_z'],row['terminal'],ratios,flush=True);rows.append(row)
a.out.write_text(json.dumps(dict(scope='recovered historical covariant AXBI driver, neutral He REC IC',binary_sha256=sha(a.binary),donor_sha256=dig,root=str(a.root),cases=rows),indent=2,allow_nan=False)+'\n')
