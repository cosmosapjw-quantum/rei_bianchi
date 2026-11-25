"""Restore the original native AXBI driver on fresh source-generated IC.
Historical AX08 histories are not consumed. The only external input in the
REC-bound lane is a typed initial slice, not a prescribed history."""
import argparse,hashlib,json,pathlib,subprocess,time,concurrent.futures,math
import numpy as np
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--donor',type=P,required=True);p.add_argument('--binary',type=P,required=True);p.add_argument('--scenario',type=P,required=True);p.add_argument('--out',type=P,required=True);p.add_argument('--end',type=float,default=19.98);p.add_argument('--workers',type=int,default=2);p.add_argument('--only',default='');a=p.parse_args()
root=a.out.resolve();root.mkdir(exist_ok=False,parents=True);exe=a.binary.resolve()
sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
donor=json.loads(a.donor.read_text());q=donor['initial'];bg=donor['background']
assert donor['schema']=='rec_bianchi.rei_initial_state/1' and donor['scenario_sha256']==sha(a.scenario)
assert donor['history']['history_owner']=='REC_BIANCHI' and not donor['history']['external_history'] and not donor['history']['external_hyrec_runtime']
assert q['z']==20 and q['ionizing_photon_stock']==0 and bg['inventory']=='REI_AX01_H_4He_mp'
assert bg['f_He']==.2454/(4*(1-.2454)) and bg['T0_K']==2.7255
assert q['x_HeII']==q['x_HeIII']==0 and q['x_HII']>0
digest=sha(a.donor)
cases=[]
for ic in ('AX01','REC'):
 for shear in (0.,.01,-.01):
  for tol in (8e-5,2e-5):
   cases.append(dict(case=f'{ic}_q{shear:+g}_tol{tol:g}',ic=ic,shear=shear,local_target=tol))
# These are new bounded comparison lanes, not the historical AX08 release.
def run(c):
 name=c['case'];dest=root/name;cfg=root/(name+'.cfg');v=dict(q_ref=c['shear'],end_zbar=a.end,energy_subdivisions=8,n_mu=8,background_panels=256,local_target=c['local_target'],initial_dln_a=1e-5,max_steps=30000,max_attempts=100000,max_rhs=5000000,max_wall_s=60,spectra_every_accepted=500,output_budget_mib=256)
 if c['ic']=='REC':v.update(initial_x_hii=q['x_HII'],initial_x_heii=q['x_HeII'],initial_x_heiii=q['x_HeIII'],initial_temperature_k=q['T_m_K'],initial_state_id='REC_HMLA_'+digest)
 cfg.write_text(''.join(f'{k}={v}\n' for k,v in v.items()))
 cmd=[str(exe),'--config',str(cfg),'--output',str(dest),'--case',name]
 t=time.monotonic();proc=subprocess.run(cmd,capture_output=True,text=True,timeout=100)
 r=dict(c,command=cmd,config_sha256=sha(cfg),wall_s=time.monotonic()-t,returncode=proc.returncode)
 if proc.returncode:
  r.update(status='REJECTED',stderr=proc.stderr[-1600:],return_text=(dest/'RETURN.txt').read_text() if (dest/'RETURN.txt').is_file() else None);print(name,r,flush=True);return r
 data=np.genfromtxt(dest/'history.csv',names=True,delimiter=',',dtype=None,encoding='utf8')
 dt=np.diff(data['time_s']);nh=data['nH_proper_cm3']*1e6;ne=data['ne_proper_cm3']*1e6
 assert len(data)>1 and np.all(dt>0) and abs(data['zbar'][-1]-a.end)<2e-12
 assert np.all(data['x_HII']>=0) and np.all(data['x_HII']<=1)
 assert np.all(data['x_HeII']>=0) and np.all(data['x_HeIII']>=0) and np.all(data['x_HeII']+data['x_HeIII']<=1)
 assert np.min(data['temperature_K'])>0 and np.min(data['photon_n_per_H'])>=0
 necheck=nh*(data['x_HII']+bg['f_He']*(data['x_HeII']+2*data['x_HeIII']))
 assert np.max(abs(ne-necheck)/np.maximum(ne,1e-300))<2e-14
 assert abs(nh[0]/q['n_H_m3']-1)<2e-14 and abs(data['H_per_s'][0]/(q['H_s']*math.hypot(1,c['shear']))-1)<2e-14
 if c['ic']=='REC':
  assert abs(data['x_HII'][0]/q['x_HII']-1)<2e-14 and abs(data['temperature_K'][0]/q['T_m_K']-1)<2e-14
  assert (dest/'initial_state_id.txt').read_text()=='REC_HMLA_'+digest
 l=np.genfromtxt(dest/'ledgers.csv',names=True,delimiter=',',dtype=None,encoding='utf8')
 assert set(l['status'])=={'PASS','VALUE'},set(l['status'])
 gate=l[l['status']=='PASS'];assert np.all(np.isfinite(gate['tolerance'])) and np.all(gate['tolerance']>0)
 tau=float(np.dot(dt,(ne[:-1]+ne[1:])*.5)*299792458.*6.6524587051e-29)
 ret=dict(s.split('=',1) for s in (dest/'RETURN.txt').read_text().splitlines() if '=' in s)
 assert ret['status']=='COMPLETE_REPRESENTED_INTERVAL'
 r.update(status='PASS_SCOPED',accepted=int(ret['accepted']),attempts=int(ret['attempts']),rhs=int(ret['rhs_evaluations']),max_newton_residual=float(ret['max_newton_residual']),max_ledger_ratio=float(np.max(abs(gate['residual'])/gate['tolerance'])),initial=dict(x_HII=float(data['x_HII'][0]),Tm=float(data['temperature_K'][0]),nH_m3=float(nh[0]),H_s=float(data['H_per_s'][0])),terminal=dict(x_HII=float(data['x_HII'][-1]),x_HeII=float(data['x_HeII'][-1]),x_HeIII=float(data['x_HeIII'][-1]),xe=float(ne[-1]/nh[-1]),Tm=float(data['temperature_K'][-1]),photon_n_per_H=float(data['photon_n_per_H'][-1]),elapsed_s=float(data['time_s'][-1]),tau=tau),hashes={str(f.relative_to(dest)):sha(f) for f in dest.rglob('*') if f.is_file()})
 print(name,r['status'],r['accepted'],r['terminal'],flush=True);return r
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:rows=list(pool.map(run,[q for q in cases if q['case'].startswith(a.only)]))
(root/'RESULTS.json').write_text(json.dumps(dict(binary_sha256=sha(exe),donor_sha256=digest,scenario_sha256=sha(a.scenario),cases=rows),indent=2,allow_nan=False)+'\n')
