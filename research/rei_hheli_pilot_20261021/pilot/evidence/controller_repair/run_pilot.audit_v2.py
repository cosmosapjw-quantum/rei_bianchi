#!/usr/bin/env python3
"""Complete bounded H/He/Li sandbox campaign; --audit-existing makes no IVP calls."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[key]='1'
import argparse,concurrent.futures,hashlib,io,json,math,multiprocessing as mp,pathlib,resource,time,traceback
import numpy as np
import scipy
from scipy.integrate import solve_ivp
import atomic as at
from model import CoupledModel
ROOT=pathlib.Path(__file__).resolve().parents[1]

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def js(p,v):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp');tmp.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n');os.replace(tmp,p)
def identity():
 source=json.loads((ROOT/'evidence/PREPARATION_SOURCE_MANIFEST.json').read_text())
 for row in source['files']:
  if sha(ROOT/row['path'])!=row['sha256']:raise ValueError('PINNED_SOURCE_CHANGED:'+row['path'])
 names=['code/atomic.py','code/model.py','code/compact_transport.py','evidence/PHYSICAL_CONTRACT.md']
 core={n:sha(ROOT/n) for n in names};core.update({r['path']:r['sha256'] for r in source['files']})
 return {'core_files_sha256':core,'core_identity':digest(core),'runner_sha256':sha(__file__),'numpy':np.__version__,'scipy':scipy.__version__}
def admission_guard(base):
 unresolved=sorted(str(p.parent.name) for p in (pathlib.Path(base)/'cases').glob('*/ATTEMPT.json') if not (p.parent/'RESULT.json').exists())
 if unresolved:raise RuntimeError('UNRESOLVED_ATTEMPT_NO_RESULT: refuse new admissions; preserve attempts and unknown CPU debit until explicit reconciliation: '+','.join(unresolved))
 return unresolved

def resolve_manifest(base,current):
 path=base/'MANIFEST.json'
 if not path.exists():js(path,current);return current
 historical=json.loads(path.read_text());old=historical['source'];new=current['source']
 if old!=new:
  record=json.loads((ROOT/'evidence/controller_repair/REPAIR.json').read_text())
  assert old['runner_sha256']==record['historical_runner_sha256'] and new['runner_sha256']==record['current_runner_sha256'],'UNRECORDED_RUNNER_CHANGE'
  assert sha(ROOT/record['historical_runner_path'])==old['runner_sha256'],'HISTORICAL_RUNNER_BYTES_CHANGED'
  assert {k:v for k,v in old.items() if k!='runner_sha256'}=={k:v for k,v in new.items() if k!='runner_sha256'},'CORE_OR_ENVIRONMENT_CHANGED'
 assert {k:v for k,v in historical.items() if k!='source'}=={k:v for k,v in current.items() if k!='source'},'CONFIGURATION_CHANGED'
 return historical

def plan(ident):
 configs=[]
 def add(s,m,r,orientation=1,kind='grid'):
  configs.append(dict(Sigma_F0=s,A_m=m,A_r=r,orientation=orientation,L=16,rtol=2e-8,atol=2e-11,max_step=.04,samples=257,kind=kind,source_identity=ident['core_identity']))
 for s in (0.,.01,.05,.2,.6):
  for m in (-.8,0.,1.6):
   for r in (-.8,-.4,0.,.4,1.6):add(s,m,r)
 for m in (1.6,-.8):
  mod=CoupledModel(dict(Sigma_F0=0.,A_m=m,A_r=1.,orientation=1,L=16));r=-mod.axes[1]/mod.axes[2]
  assert -1<=r<=2;add(0.,m,r,kind='cancellation')
 add(.6,0.,0.,-1,'negative_shear');add(.6,1.6,-.8,-1,'negative_shear')
 cases=[{'id':digest(c),'config':c} for c in configs]
 selected=[next(c for c in cases if c['config']['Sigma_F0']==0 and c['config']['A_m']==0 and c['config']['A_r']==0),next(c for c in cases if c['config']['Sigma_F0']==.6 and c['config']['A_m']==1.6 and c['config']['A_r']==-.8 and c['config']['orientation']==1),next(c for c in cases if c['config']['kind']=='cancellation' and c['config']['A_m']==1.6)]
 for original in selected:
  c={**original['config'],'L':24,'rtol':2e-9,'atol':2e-12,'kind':'combined_refinement','nominal_id':original['id']};cases.append({'id':digest(c),'config':c})
 assert len(cases)==82;return {'schema':'rei.hheli.campaign.v1','cases':cases,'nominal':79,'combined_controls':3,'source':ident,'new_physics':'Prescribed UV and T atomic test fluid with dynamic electron-dependent photon Thomson scattering','model':'ElementalElectronicEquality','abundances_per_baryon':at.ABUNDANCES,'state_names':at.NAMES}
def worker(case,base,cpu_cap,wall_cap):
 start=time.monotonic();cpu=time.process_time();p=pathlib.Path(base)/'cases'/case['id'];p.mkdir(parents=True,exist_ok=True)
 if (p/'RESULT.json').exists():raise RuntimeError('IMMUTABLE_COMPLETED_CASE_ALREADY_EXISTS')
 with (p/'ATTEMPT.json').open('x') as f:json.dump({'status':'LAUNCHED','config':case['config'],'pid':os.getpid(),'wall_cap_s':wall_cap,'cpu_cap_s':cpu_cap},f,indent=2)
 with (p/'INPUT.json').open('x') as f:json.dump(case,f,indent=2)
 result={'id':case['id'],'config':case['config'],'status':'FAILED','new_IVPs':1}
 try:
  cfg=case['config'];model=CoupledModel(cfg);calls=0
  def fun(x,y):
   nonlocal calls
   calls+=1
   if time.monotonic()-start>wall_cap or time.process_time()-cpu>cpu_cap:raise TimeoutError('TASK_CASE_BUDGET')
   return model.rhs(x,y)
  x=np.linspace(0.,math.log(7.),257);sol=solve_ivp(fun,(0.,math.log(7.)),model.initial(),method='Radau',rtol=cfg['rtol'],atol=cfg['atol'],max_step=.04,t_eval=x)
  if not sol.success or sol.t.shape!=(257,):raise RuntimeError('IVP_INCOMPLETE:'+sol.message)
  obs=[model.diagnostics(float(t),sol.y[:,i]) for i,t in enumerate(x)];data={k:np.array([r[k] for r in obs]) for k in obs[0]};f=sol.y[model.offset:model.offset+21]
  data.update(x=x,raw_y=sol.y,conditional_f=f,Y_Aq=at.Y[:,None]*f,n_Aq_m3=at.Y[:,None]*f*data['n_B_m3'][None,:])
  sums=max(float(np.max(abs(f[at.SLICES[n]].sum(axis=0)-1))) for n in at.POPULATED)
  number={name:float(np.max(abs(data[name]/data[name][0]-1))) for name in ('N_gamma_0','N_nu_0','matter_number_comoving')}
  axeserr=float(np.max(abs(np.array([data['signed_Sigma'][0],data['P_m'][0],data['P_r'][0]])-model.axes)))
  bright=model.brightness_minimum(sol.y[:model.offset]);minimum=float(f.min());cells=float(data['min_canonical_cell'].min())
  gates={'solver_success':bool(sol.success),'exact_endpoints':bool(x[0]==0. and x[-1]==math.log(7.)),'all_finite':all(np.isfinite(v).all() for v in data.values()),'fractions_lower_bound':minimum>=-2e-9,'isotope_sum':sums<=2e-9,'initial_axes':axeserr<=2e-10,'conserved_number':max(number.values())<=2e-9,'canonical_cells':cells>=0,'sampled_angular_positivity':bright>=-2e-8,'absent_T_n_exact':bool(np.all(f[at.SLICES['T']]==0) and np.all(f[at.SLICES['n']]==0))}
  with (p/'raw.tmp').open('wb') as fh:np.savez_compressed(fh,**data)
  os.replace(p/'raw.tmp',p/'raw.npz')
  result.update(status='COMPLETED' if all(gates.values()) else 'COMPUTED_GATE_FAILURE',checks=gates,diagnostics={'minimum_fraction':minimum,'isotope_sum_max':sums,'number_relative_drift':number,'initial_axes_max_abs_error':axeserr,'sampled_brightness_minimum':bright,'minimum_canonical_cell':cells,'max_baryon_relative_residual':float(np.max(abs(data['baryon_relative_residual']))),'max_Friedmann_algebraic_relative_residual':float(np.max(abs(data['Friedmann_algebraic_relative_residual']))),'max_test_fluid_energy_ratio':float(data['test_fluid_energy_ratio'].max())},raw_sha256=sha(p/'raw.npz'),raw_bytes=(p/'raw.npz').stat().st_size,nfev=sol.nfev,njev=sol.njev,nlu=sol.nlu,actual_rhs_calls=calls,solver_message=sol.message,initial_axes=model.axes)
 except Exception as exc:result.update(error=type(exc).__name__+': '+str(exc),traceback=traceback.format_exc())
 result.update(worker_cpu_s=time.process_time()-cpu,worker_wall_s=time.monotonic()-start);js(p/'RESULT.json',result);return result

def audit(base,manifest):
 rows=[];comparisons=[]
 for case in manifest['cases']:
  p=base/'cases'/case['id'];result=p/'RESULT.json'
  if not result.exists():continue
  r=json.loads(result.read_text());assert r['config']==case['config'] and r['id']==case['id']
  if 'raw_sha256' in r:assert sha(p/'raw.npz')==r['raw_sha256']
  rows.append(r)
 byid={r['id']:r for r in rows}
 for case in manifest['cases']:
  cfg=case['config']
  if cfg['kind']!='combined_refinement' or case['id'] not in byid or cfg['nominal_id'] not in byid:continue
  if byid[case['id']]['status']!='COMPLETED' or byid[cfg['nominal_id']]['status']!='COMPLETED':continue
  with np.load(base/'cases'/case['id']/'raw.npz') as refined,np.load(base/'cases'/cfg['nominal_id']/'raw.npz') as nominal:
   differences={k:float(np.max(abs(refined[k]-nominal[k]))) for k in ('signed_Sigma','P_m','P_r','conditional_f')};comparisons.append({'nominal_id':cfg['nominal_id'],'refined_id':case['id'],'max_abs_differences':differences,'pass':max(differences.values())<=2e-5})
 report={'schema':'rei.hheli.execution_summary.v1','planned':82,'nominal_planned':79,'combined_control_planned':3,'computed':len(rows),'completed':sum(r['status']=='COMPLETED' for r in rows),'failed_or_gate_failure':[{'id':r['id'],'status':r['status'],'error':r.get('error'),'checks':r.get('checks')} for r in rows if r['status']!='COMPLETED'],'aggregate_child_cpu_s':sum(r['worker_cpu_s'] for r in rows),'aggregate_child_wall_s':sum(r['worker_wall_s'] for r in rows),'new_IVP_attempts':len(list((base/'cases').glob('*/ATTEMPT.json'))),'refinement':comparisons,'scoped_gate_observation':'PASS_ALL_FIXED_GATES' if len(rows)==82 and all(r['status']=='COMPLETED' for r in rows) and len(comparisons)==3 and all(r['pass'] for r in comparisons) else 'INCOMPLETE_OR_HOLD','scientific_admission':'ROOT_REVIEW_REQUIRED','native_production':'NOT_ISSUED','nuclear19_target':'NOT_ESTABLISHED'}
 js(base/'SUMMARY.json',report);return report

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=ROOT/'results');ap.add_argument('--audit-existing',action='store_true');ap.add_argument('--workers',type=int,default=4);ap.add_argument('--no-plots',action='store_true');args=ap.parse_args();base=args.out.resolve();base.mkdir(exist_ok=True)
 ident=identity();manifest=resolve_manifest(base,plan(ident))
 if not args.audit_existing:
  admission_guard(base)
  prior_wall=json.loads((base/'CONTROLLER_RECEIPT.json').read_text())['wall_s'] if (base/'CONTROLLER_RECEIPT.json').exists() else 0.
  prior_wall+=sum(json.loads(p.read_text())['wall_s'] for p in base.glob('CONTROLLER_RESUME_*.json'))
  start=time.monotonic();existing=audit(base,manifest);charged=existing['aggregate_child_cpu_s'];attempts=existing['new_IVP_attempts'];halt=bool(existing['failed_or_gate_failure']);cases=[c for c in manifest['cases'] if not (base/'cases'/c['id']/'RESULT.json').exists()];active={};cursor=0
  affinity=len(os.sched_getaffinity(0));quota=pathlib.Path('/sys/fs/cgroup/cpu.max').read_text().split();cores=affinity if quota[0]=='max' else min(affinity,int(quota[0])/int(quota[1]));available=int(next(s.split()[1] for s in pathlib.Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:')))*1024
  cgcap=pathlib.Path('/sys/fs/cgroup/memory.max').read_text().strip();cgused=int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text());available=min(available,(int(cgcap)-cgused) if cgcap!='max' else available);workers=max(1,min(4,args.workers,int(cores),int(available/(400*1024**2))))
  js(base/'CONTROLLER_RESOURCES.json',{'effective_cores':cores,'affinity':affinity,'available_memory_bytes':available,'workers':workers,'threads_per_worker':1,'wall_cap_s':900,'child_cpu_cap_s':2400,'max_attempts':90})
  with concurrent.futures.ProcessPoolExecutor(max_workers=workers,mp_context=mp.get_context('fork')) as pool:
   while cursor<len(cases) or active:
    remaining=900-prior_wall-(time.monotonic()-start);reserved=sum(v[1] for v in active.values())
    while not halt and cursor<len(cases) and len(active)<workers and remaining>3 and attempts<90 and charged+reserved+2<2400:
     cap=min(120.,2400-charged-reserved-1);wall=min(180.,remaining-1);case=cases[cursor];cursor+=1;attempts+=1;future=pool.submit(worker,case,base,cap,wall);active[future]=(case,cap);reserved+=cap
    if not active:break
    done,_=concurrent.futures.wait(active,timeout=1,return_when=concurrent.futures.FIRST_COMPLETED)
    for future in done:
     case,cap=active.pop(future);r=future.result();charged+=r['worker_cpu_s'];print(json.dumps({'case':case['id'][:12],'kind':case['config']['kind'],'status':r['status'],'cpu_s':r['worker_cpu_s'],'completed_this_command':cursor-len(active),'elapsed_wall_s':time.monotonic()-start}),flush=True)
     if r['status']!='COMPLETED':halt=True
    if remaining<=1:halt=True
  controller_path=base/'CONTROLLER_RECEIPT.json'
  if controller_path.exists():controller_path=base/('CONTROLLER_RESUME_'+str(time.time_ns())+'.json')
  js(controller_path,{'wall_s':time.monotonic()-start,'aggregate_child_cpu_s':charged,'attempts_total':attempts,'halted_on_failure_or_budget':halt,'task_processes_only':True})
 report=audit(base,manifest)
 if not args.no_plots:
  from plots import render
  render(base,manifest)
 print(json.dumps({k:v for k,v in report.items() if k!='refinement'},indent=2));return 0 if report['scoped_gate_observation']=='PASS_ALL_FIXED_GATES' else 2
if __name__=='__main__':raise SystemExit(main())
