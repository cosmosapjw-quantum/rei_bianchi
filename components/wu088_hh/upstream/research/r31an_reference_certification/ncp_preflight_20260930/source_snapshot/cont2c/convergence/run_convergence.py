#!/usr/bin/env python3
"""Fresh B160/B192 O/D and fixed-smallstep FD. Heavy calls are shared API only."""
from __future__ import annotations
import os,sys
sys.dont_write_bytecode=True
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
os.environ['OMP_DYNAMIC']='FALSE';os.environ['OMP_WAIT_POLICY']='PASSIVE';os.environ['OMP_MAX_ACTIVE_LEVELS']='1'
from pathlib import Path
import json,time,hashlib,datetime,argparse,platform
from concurrent.futures import ProcessPoolExecutor,as_completed,wait,FIRST_COMPLETED
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[1];A=R/'cont2c/all94'
sys.path.insert(0,str(A))
import run_all94 as api
mp=api.mp;mp.mp.dps=80
STANDARD_FIELDS=api.fields

def negative_fields(*args,**kwargs):
 import negative_hybrid as neg
 return STANDARD_FIELDS(*args,radial=neg.radial_moments,**kwargs)

def reuse_fields(*args,**kwargs):
 import reuse_radial as reuse
 return STANDARD_FIELDS(*args,radial=reuse.radial_moments,**kwargs)

def init_worker(grid,threads,backend):
 api.init_worker(grid,threads)
 if backend=='negative_hybrid':
  sys.path.insert(0,str(R/'cont2c/analytic_negative'))
  import negative_hybrid as neg
  neg._library();api.fields=negative_fields
 elif backend=='reuse_radial':
  sys.path.insert(0,str(R/'cont2c/analytic_negative/moment_reuse'))
  import reuse_radial as reuse
  reuse._library();api.fields=reuse_fields
 elif backend!='original':raise ValueError('Unknown backend')


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(path,obj):Path(path).write_text(json.dumps(obj,indent=2)+'\n')
def event(name,**kw):
 d={'event':name,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),**kw}
 with (H/'events.jsonl').open('a') as f:f.write(json.dumps(d)+'\n')
 print(json.dumps(d),flush=True)
def snapshot(backend='original'):
 files=[H/'CONTRACT.json',H/'RUNTIME_ADDENDUM.json',Path(__file__),R/'recovered/CP2.md']
 out={'driver_sources':{str(p.relative_to(R)):sha(p) for p in files},'shared_api_sources':api.identity(),'backend':backend}
 if backend=='negative_hybrid':
  extra=[H/'NEGATIVE_BACKEND_ADDENDUM.json',R/'cont2c/analytic_negative/negative_hybrid.py',R/'cont2c/analytic_negative/negative_hybrid.cpp',R/'cont2c/analytic_negative/CONTRACT.json',R/'cont2c/analytic_negative/RESULTS.json']
  out['candidate_sources']={str(p.relative_to(R)):sha(p) for p in extra}
 if backend=='reuse_radial':
  folder=R/'cont2c/analytic_negative/moment_reuse'
  extra=[H/'REUSE_BACKEND_ADDENDUM.json',folder/'reuse_radial.py',folder/'reuse_radial.cpp',folder/'CONTRACT.json',folder/'RESULTS.json']
  out['candidate_sources']={str(p.relative_to(R)):sha(p) for p in extra}
 return out
def cases(n,inp,cfg):return api.make_cases({'z_values':cfg['z_values'],'tau_steps':cfg['n192_tau_steps'] if n==192 else []},inp)
def plan(cfg,backend='original'):
 inp=api.inputs();tim=json.loads((A/'TIMING.json').read_text())
 tb=next(x['total_seconds'] for x in tim['timings'] if x['case']['grad']);to=next(x['total_seconds'] for x in tim['timings'] if not x['case']['grad'])
 parts=[]
 for n in ([128]+cfg['fresh_n_levels'] if backend!='original' else cfg['fresh_n_levels']):
  cs=cases(n,inp,cfg);nb=sum(x['grad'] for x in cs);no=len(cs)-nb;factor=(n/128)**2
  parts.append({'n':n,'base_tables':nb,'overlap_only_tables':no,'base_rows':nb*12,'overlap_rows':no*12,'n_squared_ratio':factor,'estimated_serial_seconds':12*factor*(nb*tb+no*to),'cases':cs})
 serial=sum(x['estimated_serial_seconds'] for x in parts)
 obj={'status':'PREPARED_NO_HEAVY_TARGETS_EXECUTED','contract_sha256':sha(H/'CONTRACT.json'),'timing_source':str((A/'TIMING.json').relative_to(R)),'timing_source_sha256':sha(A/'TIMING.json'),'actual_reference_base_row_seconds':tb,'actual_reference_offset_row_seconds':to,'estimate_method':'Measured ia3 B128 row wall * count * (n/128)^2; excludes overhead, scheduling, cache and concurrent contention; not a measured fullmatrix runtime','levels':parts,'estimated_serial_seconds':serial,'estimated_ideal_wall_by_workers':{str(w):serial/w for w in (4,8)},'source_identity_at_preparation':snapshot(backend),'backend':backend}
 dump(H/({'negative_hybrid':'PLANNING_NEGATIVE_OPTION.json','reuse_radial':'PLANNING_REUSE_OPTION.json'}.get(backend,'PLANNING.json')),obj);return obj

def check_release():
 p=H/'ROOT_RELEASE.json'
 if not p.exists():raise RuntimeError('Operational root release missing; preparation only. No heavy target launched.')
 rel=json.loads(p.read_text())
 if rel.get('authorized') is not True:raise RuntimeError('root release not authorized')
 rp=R/rel.get('n128_evidence_path','cont2c/all94/RESULTS.json')
 if not rp.exists():raise RuntimeError('n128 all94 result missing')
 if sha(rp)!=rel['n128_result_sha256']:raise RuntimeError('n128 result identity differs from root release')
 prior=json.loads(rp.read_text());zs=prior['z_cases']
 for z in (0,3):
  rows=[q for x in zs if x['z']==z for q in x['comparisons'] if q['h_tau']==1e-5]
  if len(rows)!=1 or rows[0]['total']!=94 or rows[0]['failed_count']!=0:raise RuntimeError(f'n128 smallstep gate not passed atz{z}')
 for p,h in prior['execution_identity']['source_hashes'].items():
  if sha(R/p)!=h:raise RuntimeError(f'API source differs from passed n128: {p}')
 for p,h in prior['raw_hashes'].items():
  if sha(A/p)!=h:raise RuntimeError(f'n128 raw identity mismatch: {p}')
 backend=rel.get('backend','original')
 if backend not in ('original','negative_hybrid','reuse_radial'):raise RuntimeError('Unknown released backend')
 if backend!='original':
  if rel.get('candidate_decision')!='APPROVED_FOR_SCOPED_CONVERGENCE':raise RuntimeError('Negative candidate lacks root scoped decision')
  if rel.get('candidate_addendum_sha256')!=sha(H/('REUSE_BACKEND_ADDENDUM.json' if backend=='reuse_radial' else 'NEGATIVE_BACKEND_ADDENDUM.json')):raise RuntimeError('Candidate addendum identity mismatch')
 return rel,prior

def prepare_grid(n,inp):
 # Exact same definitions imported from shared API; only target directory differs.
 t,w=api.nodes(n);U,V=api.exact_weights(t,w);W=api.contract(U,V,inp['C'])[0]
 p=H/f'frozen_grid_n{n}.npz'
 vals=dict(t=t,w=w,W=W,U=U,V=V,**inp)
 if n==128:
  with np.load(A/'frozen_grid_n128.npz',allow_pickle=False) as prior_grid:
   if set(prior_grid.files)!=set(vals) or any(not np.array_equal(prior_grid[k],v) for k,v in vals.items()):raise RuntimeError('Rebuilt n128 bridge grid differs from original n128 grid')
 if p.exists():
  with np.load(p,allow_pickle=False) as d:
   if set(d.files)!=set(vals) or any(not np.array_equal(d[k],v) for k,v in vals.items()):raise RuntimeError(f'Preserved grid differs: {p}')
 else:np.savez_compressed(p,**vals)
 return p

def allocation(default,threads):
 p=H/'WORKER_ALLOCATION.json'
 workers=int(json.loads(p.read_text())['workers']) if p.exists() else default
 if workers<1 or workers*threads>8:raise ValueError('Dynamicworkerallocationexceeds8CPUquota')
 return workers

def row_hash(case,ia,gridhash,source):
 return hashlib.sha256(json.dumps({'case':case,'row':ia,'grid':gridhash,'api':source},sort_keys=True).encode()).hexdigest()

def evaluate_level(n,cases0,inp,workers,threads,source,backend='original'):
 folder=H/(f'n{n}_bridge' if n==128 else f'n{n}');folder.mkdir(exist_ok=True);rd=folder/'rows';rd.mkdir(exist_ok=True)
 grid=prepare_grid(n,inp);gh=sha(grid);api.nr.library('portable_omp');api.hr._library()
 if backend=='negative_hybrid':
  sys.path.insert(0,str(R/'cont2c/analytic_negative'));import negative_hybrid as neg;neg._library()
 elif backend=='reuse_radial':
  sys.path.insert(0,str(R/'cont2c/analytic_negative/moment_reuse'));import reuse_radial as reuse;reuse._library()
 st=time.perf_counter()
 pending=[];timings=[]
 for c in cases0:
  for ia in range(12):
   p=rd/f"{c['label']}_row{ia:02d}.npz";rh=row_hash(c,ia,gh,source)
   if p.exists():
    with np.load(p,allow_pickle=False) as d:
     if str(d['identity'])!=rh:raise RuntimeError(f'Checkpoint identity mismatch {p}')
     timings.append(json.loads(str(d['timing'])))
   else:pending.append((c,ia,p,rh))
 event('level_start',n=n,workers=workers,threads=threads,pending_rows=len(pending),reused_rows=len(cases0)*12-len(pending))
 if pending:
  queued=list(pending)
  while queued:
   allocated=allocation(workers,threads)
   event('worker_pool_start',n=n,workers=allocated,threads=threads,queued_rows=len(queued))
   with ProcessPoolExecutor(max_workers=allocated,initializer=init_worker,initargs=(grid,threads,backend)) as pool:
    jobs={};draining=False
    while queued or jobs:
     if not draining:
      while queued and len(jobs)<allocated:
       item=queued.pop(0);c,ia,p,rh=item;jobs[pool.submit(api.compute_row,(c,ia))]=item
     if not jobs:break
     done,_=wait(jobs,timeout=10,return_when=FIRST_COMPLETED)
     for future in done:
      c,ia,p,rh=jobs.pop(future);label,actualia,raw,sa,timing=future.result()
      if label!=c['label'] or actualia!=ia:raise RuntimeError('Shared API row labeling mismatch')
      timing={'n':n,'case':label,'row':ia,'workers':allocated,'threads':threads,'backend':backend,**timing};timings.append(timing)
      np.savez_compressed(p,raw_long=raw,sumabs=sa,identity=np.array(rh),timing=np.array(json.dumps(timing)))
      event('row_complete',n=n,case=label,row=ia,seconds=timing['total_seconds'],elapsed=time.perf_counter()-st)
     if not draining and allocation(workers,threads)!=allocated:
      draining=True;event('allocation_change_pending',n=n,old_workers=allocated,new_workers=allocation(workers,threads),active_rows=len(jobs))
     if draining and not jobs:break
 vals={}
 for c in cases0:
  shape=(4,2 if c['grad'] else 1,3 if c['grad'] else 1,3,12,12);raw=np.zeros(shape,np.clongdouble);sa=np.zeros(shape,np.longdouble)
  for ia in range(12):
   with np.load(rd/f"{c['label']}_row{ia:02d}.npz",allow_pickle=False) as d:raw[...,ia,:]=d['raw_long'];sa[...,ia,:]=d['sumabs']
  p=folder/f"primitive_tables_{c['label']}.npz"
  np.savez_compressed(p,raw_long=raw,sumabs=sa,z_longdouble=np.longdouble(c['z_longdouble']),z_exact=np.array(c['z_exact']),tau_offset_exact=np.array(c['tau_offset_exact']),orientations=np.array([1,-1] if c['grad'] else [1]),fields=np.array(['O','G1','G2'] if c['grad'] else ['O']),assignment_order=np.array([[0,0],[0,1],[1,0],[1,1]]))
  val=api.assemble(raw,c,inp);vals[c['label']]=val
  dump(folder/f"assembled_{c['label']}.json",{k:api.mpa(a) for k,a in val.items() if k!='orbital_sumabs'})
  np.savez_compressed(folder/f"orbital_condition_{c['label']}.npz",sumabs=val['orbital_sumabs'])
 event('level_complete',n=n,seconds=time.perf_counter()-st)
 return vals,{'elapsed_this_invocation_seconds':time.perf_counter()-st,'rows':timings,'grid_sha256':gh}

def base128(inp,cfg):
 vals={}
 for c in api.make_cases({'z_values':cfg['z_values'],'tau_steps':[]},inp):
  with np.load(A/f"primitive_tables_{c['label']}.npz",allow_pickle=False) as d:raw=d['raw_long']
  vals[c['label']]=api.assemble(raw,c,inp)
 return vals

def frob(a):return mp.sqrt(mp.fsum(abs(x)**2 for x in a.flat))
def hermiticity(v):
 O=v['O'];Or=v['O_row'].T;gap=O-np.vectorize(mp.conj)(Or);den=max(frob(O),frob(Or));rel=frob(gap)/den if den else mp.mpf(0)
 return {'scope':'Independently evaluated mixed rectangular block only, not full49 matrix gate','max_abs':float(max(abs(x) for x in gap.flat)),'frobenius_relative':float(rel),'entry_abs':[[float(abs(x)) for x in row] for row in gap]}
def increment(a,b,criterion=None):
 rows=[]
 for ch,c in np.ndindex(47,2):
  delta=a[ch,c]-b[ch,c];e=abs(delta)
  row={'channel':ch,'cusp':c,'abs_increment':float(e),'complex_increment':api.pair(delta)}
  if criterion is not None:row.update(threshold=criterion,passed=bool(e<=mp.mpf(str(criterion))))
  rows.append(row)
 out={'max_abs_increment':max(r['abs_increment'] for r in rows),'entries':rows}
 if criterion is not None:out.update(failed_count=sum(not r['passed'] for r in rows),criterion=criterion)
 else:out['status']='DIAGNOSTIC_ONLY_NO_D_CONVERGENCE_THRESHOLD'
 return out

def analyze(vals,cfg,cases192):
 conv=[];herm=[];metric=[]
 for z in cfg['z_values']:
  label=f'z{z:g}_base';v={n:vals[n][label] for n in cfg['n_levels']}
  for n in cfg['n_levels']:herm.append({'n':n,'z':z,**hermiticity(v[n])})
  obs={}
  for field in ('O','O_row','D_col','D_row','Dsum'):
   arrays={n:v[n][field].T if field in ('O_row','D_row') else v[n][field] for n in v};tol=2e-7 if field in ('O','O_row') else None
   inc1=increment(arrays[160],arrays[128],tol);inc2=increment(arrays[192],arrays[160],tol)
   monotone=[abs(mp.mpc(b['complex_increment']['real'],b['complex_increment']['imag']))<abs(mp.mpc(a['complex_increment']['real'],a['complex_increment']['imag'])) for a,b in zip(inc1['entries'],inc2['entries'])]
   obs[field]={'128_to_160':inc1,'160_to_192':inc2,'strict_increment_magnitude_decrease_count':sum(monotone),'decrease_by_entry':monotone}
  conv.append({'z':z,'observables':obs})
  byoff={mp.mpf(c['tau_offset_exact']):vals[192][c['label']] for c in cases192 if c['z_base']==z};h=api.mr(1e-5)
  fd=(-byoff[2*h]['O']+8*byoff[h]['O']-8*byoff[-h]['O']+byoff[-2*h]['O'])/(12*h)
  metric.append({'z':z,'n':192,'h_tau':1e-5,**api.audit(fd,byoff[mp.mpf(0)]['Dsum'])})
 return {'convergence':conv,'mixed_O_hermiticity':herm,'n192_smallstep_metric':metric,'O_forward_final_increment_all_passed':all(x['observables']['O']['160_to_192']['failed_count']==0 for x in conv),'O_reverse_final_increment_all_passed':all(x['observables']['O_row']['160_to_192']['failed_count']==0 for x in conv),'n192_smallstep_all_passed':all(x['failed_count']==0 for x in metric),'Q2_status':'NOT_CLOSED_H_NOT_EVALUATED','full49_matrix_gate':'NOT_EVALUATED'}

def bridge_report(old,new,cfg):
 rows=[]
 for z in cfg['z_values']:
  label=f'z{z:g}_base';obs={}
  for field in ('O','O_row','D_col','D_row','Dsum'):
   a=new[label][field];b=old[label][field]
   if field in ('O_row','D_row'):a=a.T;b=b.T
   q=increment(a,b);q['status']='REPRESENTATION_BRIDGE_DIAGNOSTIC_ONLY_NO_NEW_THRESHOLD';obs[field]=q
  rows.append({'z':z,'observables':obs,'candidate_O_hermiticity':hermiticity(new[label]),'original_O_hermiticity':hermiticity(old[label])})
 return rows

def seal_early(cfg):
 path=H/'N128_EARLY_EVIDENCE.json'
 if path.exists():raise RuntimeError('Earlyevidencepacket alreadyexists; immutable, donotoverwrite')
 ep=A/'EARLY_COMPARISONS.json';raw=ep.read_bytes();early=json.loads(raw);run=json.loads((A/'EXECUTION_IDENTITY.json').read_text())
 zs=[]
 for z in cfg['z_values']:
  items=[x for x in early if x['z']==z and x['h_tau']==1e-5]
  if len(items)!=1 or items[0]['total']!=94 or items[0]['failed_count']!=0:raise RuntimeError('Bothz earlysmallstepPASSrequired')
  item={k:v for k,v in items[0].items() if k!='z'};zs.append({'z':z,'comparisons':[item]})
 for p,h in run['source_hashes'].items():
  if sha(R/p)!=h:raise RuntimeError('Early API source changed')
 inp=api.inputs();cs=cases(192,inp,cfg);hashes={}
 for c in cs:
  p=A/f"primitive_tables_{c['label']}.npz"
  hashes[p.name]=sha(p)
 obj={'status':'SEALED_EARLY_FIXED_SMALLSTEP_PASS_WIDER_LADDER_PENDING','execution_identity':run,'z_cases':zs,'raw_hashes':hashes,'source_early_comparisons_sha256':hashlib.sha256(raw).hexdigest(),'source_execution_identity_sha256':sha(A/'EXECUTION_IDENTITY.json'),'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'limitations':['Onlyn128h1e-5atbothzclosedhere;wide-stepdiagnosticsmayremainrunning.','Hashidentitydoesnotcertifyscientificvalidity.']}
 dump(path,obj);print(json.dumps({'path':str(path.relative_to(R)),'sha256':sha(path),'raw_files':len(hashes)},indent=2))

def main():
 p=argparse.ArgumentParser();p.add_argument('--plan',action='store_true');p.add_argument('--run',action='store_true');p.add_argument('--backend',choices=['original','negative_hybrid','reuse_radial'],default=None);p.add_argument('--seal-early',action='store_true');args=p.parse_args();cfg=json.loads((H/'CONTRACT.json').read_text())
 if args.seal_early:
  seal_early(cfg)
  if not args.run:return
 if args.plan or not args.run:
  d=plan(cfg,args.backend or 'original');print(json.dumps({k:d[k] for k in ('status','estimated_serial_seconds','estimated_ideal_wall_by_workers')},indent=2))
 if not args.run:return
 rel,prior=check_release();backend=rel.get('backend','original');workers=int(rel['workers']);threads=int(rel['threads'])
 if args.backend is not None and args.backend!=backend:raise RuntimeError('CLI backend differs from root release')
 if min(workers,threads)<1 or workers*threads>8:raise ValueError('Workers*threads must fit quota8')
 identity=snapshot(backend);identity.update(root_release_sha256=sha(H/'ROOT_RELEASE.json'),n128_result_sha256=rel['n128_result_sha256'],n128_evidence_path=rel.get('n128_evidence_path','cont2c/all94/RESULTS.json'),workers=workers,threads=threads,python=platform.python_version(),numpy=np.__version__,longdouble_significand_bits=np.finfo(np.longdouble).nmant+1,actual_model='MODEL_UNRESOLVED')
 ip=H/'EXECUTION_IDENTITY.json'
 if ip.exists():
  old=json.loads(ip.read_text())
  if any(old.get(k)!=identity.get(k) for k in ('driver_sources','shared_api_sources','candidate_sources','backend')):raise RuntimeError('Execution source identity changed; preserve and make explicit in-scope repair before resume')
 else:dump(ip,identity)
 event('run_start',identity_sha256=sha(ip),workers=workers,threads=threads);st=time.perf_counter();inp=api.inputs();vals={128:base128(inp,cfg)};timings={};c192=None;bridge=None
 runtime_sources={**identity['shared_api_sources'],**identity.get('candidate_sources',{})}
 if backend!='original':
  cs=cases(128,inp,cfg);dump(H/'CASES_n128_bridge.json',cs)
  candidate,timing=evaluate_level(128,cs,inp,workers,threads,runtime_sources,backend);timings['128_bridge']=timing;bridge=bridge_report(vals[128],candidate,cfg);vals[128]=candidate;dump(H/'N128_REPRESENTATION_BRIDGE.json',bridge)
 for n in cfg['fresh_n_levels']:
  cs=cases(n,inp,cfg);dump(H/f'CASES_n{n}.json',cs);vals[n],timings[n]=evaluate_level(n,cs,inp,workers,threads,runtime_sources,backend)
  if n==192:c192=cs
 result={'status':'COMPLETE_O_D_SCOPE_ONLY','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'execution_identity':identity,**analyze(vals,cfg,c192),'timings':timings,'n128_representation_bridge':bridge,'elapsed_this_invocation_seconds':time.perf_counter()-st,'shared_sources_unchanged':all(sha(R/p)==h for p,h in runtime_sources.items()),'raw_hashes':{str(p.relative_to(H)):sha(p) for p in H.glob('n*/primitive_tables_*.npz')},'limitations':['O/D only; H missing so full Q2 remains unevaluated.','Historical Q1 representative ladder and Nstar selection not independently reproduced here.','Mixed-block O hermiticity is not full49 matrix hermiticity.','No physical admission, propagation, cusp-cusp certification or gamma changes.','N-squared planning estimate is not measured speedup.']}
 dump(H/'RESULTS.json',result);event('run_complete',O_passed=result['O_forward_final_increment_all_passed'],metric_passed=result['n192_smallstep_all_passed'],Q2=result['Q2_status'],seconds=result['elapsed_this_invocation_seconds'])
 files=[p for p in H.rglob('*') if p.is_file() and p.name!='MANIFEST.json' and '__pycache__' not in str(p)];dump(H/'MANIFEST.json',{'files':[{'path':str(p.relative_to(H)),'size':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)]})
if __name__=='__main__':main()
