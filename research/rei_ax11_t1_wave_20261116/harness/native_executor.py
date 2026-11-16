#!/usr/bin/env python3
"""Cloud-authored finite T1 executor. New owned root only; no process retry.

prepare: verify/reuse source, compile, test new entry against saved native T1.
launch: consume the exact prepared binding, execute the two finite full cases.
All setup/preflight debit remains in the same cumulative allocation.
"""
from pathlib import Path
import concurrent.futures, csv, hashlib, json, math, os, shutil, signal
import struct, subprocess, sys, threading, time, traceback, resource

ROOT=Path(sys.argv[1]).resolve(); PHASE=sys.argv[2]
PHASE_START=time.monotonic()
SELF_START=resource.getrusage(resource.RUSAGE_SELF)
ALLOC=json.loads((ROOT/'ALLOCATION.json').read_text()); C=ALLOC['caps']
OLD=Path(ALLOC['source']['old_native_root'])
LOCK=threading.RLock()
class ResourceCensor(RuntimeError):pass
LEDGER_PATH=ROOT/'RUN_LEDGER.json'
LEDGER=json.loads(LEDGER_PATH.read_text()) if LEDGER_PATH.exists() else {
 'schema':'REI_AX11_T1_NATIVE_LEDGER_V1','allocation_sha256':hashlib.sha256((ROOT/'ALLOCATION.json').read_bytes()).hexdigest(),
 'prior_debit':ALLOC['prior_debit'],'records':[],'cases':{},'historical_accumulated_cost':'UNKNOWN retained',
 'original_DAG':'10/17','expansion_DAG':'28/88'}

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def save_json(path,value):
 path=Path(path);tmp=path.with_suffix(path.suffix+'.tmp')
 tmp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');os.replace(tmp,path)
def save():
 with LOCK:save_json(LEDGER_PATH,LEDGER)
def bytes_in(path):return sum(p.stat().st_size for p in Path(path).rglob('*') if p.is_file())
def debit():
 with LOCK:
  return {k:sum(r.get(k,0) for r in LEDGER['records']) for k in ['CPU_s','wall_s','accepted','trials','RHS']}
def checkpoint(path):
 lines=Path(path).read_text().splitlines();assert len(lines)==6 and lines[0]=='AXBI_CHECKPOINT_V2'
 v=list(map(float,lines[1].split()));n=list(map(int,lines[2].split()))
 return {'a':v[0],'time_s':v[1],'b':v[2],'x_HII':v[3],'x_HeII':v[4],'x_HeIII':v[5],
  'w_erg_per_H':v[6],'next_dln_a':v[7],'last_error':v[9],'wall_s':v[10],
  'accepted':n[0],'trials':n[1],'RHS':n[4],'comparisons':n[5],'sha256':sha(path)}

def job(name,command,cwd,wall,cpu,memory,kind,out=None):
 """GNU time records exact child usage; prlimit applies inside its child."""
 assert wall>2 and cpu>=1
 with LOCK:
  assert not any(x['name']==name for x in LEDGER['records']), 'duplicate job forbidden'
  if kind=='segment':
   if sum(x['kind']=='segment' for x in LEDGER['records'])>=C['all_segment_starts_including_preflight']:raise ResourceCensor('shared segment-start cap')
  elif kind=='build':assert sum(x['kind']=='build' for x in LEDGER['records'])<C['build_starts']
  record={'name':name,'kind':kind,'command':command,'status':'STARTED','CPU_cap_s':cpu,'wall_cap_s':wall,'memory_cap_bytes':memory}
  LEDGER['records'].append(record);save()
 log=ROOT/'logs'/f'{name}.log';usage=ROOT/'logs'/f'{name}.usage.json'
 env=os.environ.copy();env.update(AX11_CACHE='1',AX11_LAZY='1',CARGO_BUILD_JOBS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',
   CARGO_TARGET_DIR=str(ROOT/'build'),RUSTFLAGS='--cfg ax11_profile -C codegen-units=1')
 fmt='{"user_s":%U,"system_s":%S,"elapsed_s":%e,"max_RSS_kB":%M,"exit":%x}'
 cmd=['/usr/bin/time','-q','-f',fmt,'-o',str(usage),'prlimit',f'--cpu={int(cpu)}:{int(cpu)+1}',
   f'--as={memory}:{memory}',f'--fsize={2*1024**3}:{2*1024**3}','--',*command]
 started=time.monotonic();reason=None
 with log.open('wb') as f:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  with LOCK:record['pid']=p.pid;save()
  while p.poll() is None:
   if time.monotonic()-started>=wall-3:reason='EXTERNAL_WALL_CAP'
   if reason:
    os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(timeout=2)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
    break
   time.sleep(.5)
  code=p.wait()
 wall_used=time.monotonic()-started
 metrics=json.loads(usage.read_text()) if usage.exists() and usage.stat().st_size else None
 with LOCK:
  record.update(returncode=code,status=reason or 'FINISHED',wall_s=wall_used,usage=metrics,
   CPU_s=(metrics['user_s']+metrics['system_s']) if metrics else cpu,
   cost_complete=metrics is not None,log_sha256=sha(log))
  if out is not None:
   record['output_directory']=str(out)
   summary=Path(out)/'segment_summary.json'
   if summary.exists():
    s=json.loads(summary.read_text());n=s['delta_counts']
    record.update(accepted=n['accepted'],trials=n['trials'],RHS=n['rhs_evaluations'],summary=s,
      checkpoint_sha256=sha(Path(out)/'checkpoint.txt'),source_sha256=sha(Path(out)/'source_identity.txt'))
   else:
    record['unfinished_native_work']='UNKNOWN; retain checkpoint and orphan rows; no continuation'
   record['output_bytes']=bytes_in(out) if Path(out).exists() else 0
  save()
 print(json.dumps({'job':name,'returncode':code,'wall_s':wall_used,'CPU_s':record['CPU_s'],
                   'accepted':record.get('accepted'),'status':record['status']}),flush=True)
 if reason or metrics is None:raise RuntimeError(f'{name}: {reason or "missing usage"}; no retry')
 return record

def verify_source():
 b=json.loads((ROOT/'SOURCE_BINDING.json').read_text())
 for rel,v in b['files'].items():
  p=ROOT/'source'/rel;assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],rel
 return b

def compare_preflight():
 """Compare changed entry + resume at256 against existing exact native T1 data."""
 result={}
 for case in ['ZERO','PLUS']:
  dirs=[ROOT/'preflight'/f'{case}_0']+([ROOT/'preflight/PLUS_1'] if case=='PLUS' else [])
  reference=OLD/'time_preflight_results'/f'{case}_T1_ORIGINAL_START'
  summary=json.loads((dirs[-1]/'segment_summary.json').read_text());assert summary['end_counts']['accepted']==256
  checks={}
  # These four tables have a row (or rows) at every accepted state.
  for filename,tcol in [('history.csv','time_s'),('abundances.csv','time_s'),('ledgers.csv','time_s'),('feedback.csv','time_s')]:
   actual=[]
   for i,d in enumerate(dirs):
    rows=list(csv.DictReader((d/filename).open()))
    start=float(rows[0][tcol]);actual.extend(x for x in rows if not(i and float(x[tcol])==start))
   end=float(actual[-1][tcol]);expected=[]
   with (reference/filename).open() as f:
    for x in csv.DictReader(f):
     if float(x[tcol])>end:break
     expected.append(x)
   assert actual==expected,(case,filename)
   checks[filename]={'rows':len(actual),'exact_formatted_fields_equal':True}
  # Full gas, adaptive, ledger, count and photon state compared bitwise.
  cp=(dirs[-1]/'checkpoint.end.txt').read_text().splitlines();v=list(map(float,cp[1].split()));n=list(map(int,cp[2].split()))
  vals=[v[0],*v[3:10],*map(float,cp[3].split())]
  counts=[n[0],n[1],n[5],n[2],n[3],n[4]];photons=list(map(float,cp[4].split()))
  with (reference/'raw/state_trace.bin').open('rb') as f:
   header=f.read(56);assert header[:8]==b'AX11TRC1'
   _,_,_,record_bytes,records,_=struct.unpack('<6Q',header[8:]);assert records>256
   f.seek(56+256*record_bytes);saved=f.read(record_bytes)
  rebuilt=struct.pack('<32d6Q',*vals,*counts)+struct.pack('<'+'d'*len(photons),*photons)
  assert rebuilt==saved,case+' full state mismatch'
  expected_spectra={}
  with (reference/'spectra.csv').open() as f:
   for row in csv.DictReader(f):expected_spectra.setdefault(row['time_s'],[]).append(row)
  matched=0
  for d in dirs:
   got={}
   with (d/'spectra.csv').open() as f:
    for row in csv.DictReader(f):got.setdefault(row['time_s'],[]).append(row)
   for t,rows in got.items():
    if t in expected_spectra:assert rows==expected_spectra[t],(case,t);matched+=1
  result[case]={'four_every_step_tables':checks,'full_state_at256_bit_identical':True,'common_spectrum_snapshots_equal':matched,
    'new_segment_boundary_snapshots':'retained; expected additional terminal/start snapshots at128/256'}
 result.update(status='PASS_SCOPED_PRODUCTION_ENTRY_AND_CONTINUATION',no_full_history_error_claim=True)
 save_json(ROOT/'PREFLIGHT_VALIDATION.json',result)
 return result

def prepare():
 assert not (ROOT/'PREPARE_STARTED.json').exists(), 'prepare already started; inspect failure instead of retry'
 save_json(ROOT/'PREPARE_STARTED.json',{'UTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
 (ROOT/'logs').mkdir();(ROOT/'preflight').mkdir();(ROOT/'cases').mkdir();save()
 manifest_path=OLD/'source/SOURCE_PACKAGE_MANIFEST.json';assert sha(manifest_path)==ALLOC['source']['old_package_manifest_sha256']
 manifest=json.loads(manifest_path.read_text())
 for rel,v in manifest['files'].items():
  if rel.startswith('instrumented/'):
   path=OLD/'source'/rel;assert path.stat().st_size==v['bytes'] and sha(path)==v['sha256'],rel
 shutil.copytree(OLD/'source/instrumented',ROOT/'source',ignore=shutil.ignore_patterns('target','__pycache__'))
 wrapper=ROOT/'harness/ax11_production_segment.rs';assert sha(wrapper)==ALLOC['source']['new_entry_sha256']
 shutil.copyfile(wrapper,ROOT/'source/rust/rei_microphysics/examples/ax11_production_segment.rs')
 files={str(p.relative_to(ROOT/'source')):{'sha256':sha(p),'bytes':p.stat().st_size} for p in (ROOT/'source').rglob('*') if p.is_file()}
 old_source_identity=OLD/'time_preflight_results/PLUS_T1_ORIGINAL_START/source_identity.txt'
 binding={'files':files,'reused_compiled_library_identity_sha256':sha(old_source_identity),'new_entry_sha256':sha(wrapper),
   'compiler':subprocess.check_output(['/home/cosmosapjw/.cargo/bin/rustc','--version'],text=True).strip(),
   'original_compiled_corpus_sha256':ALLOC['source']['original_17_file_corpus_sha256']}
 save_json(ROOT/'SOURCE_BINDING.json',binding)
 rec=job('build_production',['/home/cosmosapjw/.cargo/bin/cargo','build','--release','--offline','--locked','--example','ax11_production_segment'],
   ROOT/'source/rust/rei_microphysics',C['preparation_CPU_and_wall_cap_s']-10,C['preparation_CPU_and_wall_cap_s']-10,C['per_build_memory_bytes'],'build')
 assert rec['returncode']==0,'build failed; preserve log'
 binary=ROOT/'build/release/examples/ax11_production_segment'
 binding['binary']={'path':str(binary),'sha256':sha(binary),'bytes':binary.stat().st_size};save_json(ROOT/'SOURCE_BINDING.json',binding)
 for case,index,previous,steps in [('PLUS',0,'IC',128),('PLUS',1,str(ROOT/'preflight/PLUS_0/checkpoint.txt'),128),('ZERO',0,'IC',256)]:
  cfg=ROOT/ALLOC['configs'][case]['path'];assert sha(cfg)==ALLOC['configs'][case]['sha256'];verify_source()
  assert sha(binary)==binding['binary']['sha256']
  if previous!='IC':
   previous_record=next(r for r in LEDGER['records'] if r['name']=='preflight_PLUS0')
   assert sha(previous)==previous_record['checkpoint_sha256']
   assert sha(Path(previous).parent/'source_identity.txt')==binding['reused_compiled_library_identity_sha256']
   assert sha(Path(previous).parent/'config.cfg')==ALLOC['configs'][case]['sha256']
  spent=debit();wall=min(65,C['preparation_CPU_and_wall_cap_s']-spent['wall_s']-3);cpu=min(60,C['preparation_CPU_and_wall_cap_s']-spent['CPU_s']-3)
  out=ROOT/'preflight'/f'{case}_{index}';command=[str(binary),str(cfg),previous,str(out),case,str(steps),str(max(1,wall-5))]
  rec=job('preflight_'+case+str(index),command,ROOT,wall,math.floor(cpu),C['per_process_memory_bytes'],'segment',out)
  assert rec['returncode']==10 and rec['summary']['status']=='SEGMENT_ACCEPTED_BOUNDARY'
  assert rec['source_sha256']==binding['reused_compiled_library_identity_sha256']
  if previous!='IC':assert sha(out/'input_checkpoint.txt')==sha(previous)
 compare_preflight()
 # Charge controller work as well as child execution, with an explicit small
 # reservation for the remaining binding/receipt writes (not measured CPU).
 r=resource.getrusage(resource.RUSAGE_SELF);self_cpu=r.ru_utime+r.ru_stime-SELF_START.ru_utime-SELF_START.ru_stime
 controller_wall=max(0,time.monotonic()-PHASE_START-debit()['wall_s'])
 LEDGER['records'].append({'name':'prepare_controller','kind':'controller','status':'MEASURED_PLUS_TERMINAL_RESERVE',
  'actual_CPU_s_at_measurement':self_cpu,'actual_nonchild_wall_s_at_measurement':controller_wall,
  'CPU_s':math.ceil(self_cpu)+1,'wall_s':math.ceil(controller_wall)+1,
  'debit_semantics':'conservative charged amounts include terminal receipt writes; exact child usage remains separate'})
 save();spent=debit()
 assert spent['CPU_s']<=C['preparation_CPU_and_wall_cap_s'] and spent['wall_s']<=C['preparation_CPU_and_wall_cap_s']
 plan={'status':'EXACT_BOUND_AFTER_PREFLIGHT','source_binding_sha256':sha(ROOT/'SOURCE_BINDING.json'),
       'preflight_sha256':sha(ROOT/'PREFLIGHT_VALIDATION.json'),'preparation_debit':spent,
       'full_segment_pool_remaining':C['all_segment_starts_including_preflight']-sum(r['kind']=='segment' for r in LEDGER['records']),
       'pool_rule':'Shared13 full starts after3 preflight starts; at most8 percase, exhaustion is censored, never retried',
       'launch_controller_reservation':{'CPU_s':60,'wall_s':60},'cases':{}}
 for case in ['ZERO','PLUS']:
  caps={'accepted':min(C['per_case_accepted'],(C['aggregate_accepted']-spent['accepted'])//2),
   'trials':min(C['per_case_trials'],(C['aggregate_trials']-spent['trials'])//2),
   'RHS':min(C['per_case_RHS'],(C['aggregate_RHS']-spent['RHS'])//2),
   'CPU_s':math.floor(min(C['per_case_CPU_s'],(C['aggregate_CPU_s']-spent['CPU_s']-60)/2)),
   'wall_s':math.floor(min(C['per_case_wall_s'],(C['aggregate_sum_job_wall_s']-spent['wall_s']-60)/2))}
  d=dict(x.split('=',1) for x in (ROOT/ALLOC['configs'][case]['path']).read_text().splitlines())
  d.update(max_steps=str(caps['accepted']),max_attempts=str(caps['trials']),max_rhs=str(caps['RHS']),max_wall_s=str(caps['wall_s']))
  cfg=ROOT/'inputs'/f'{case}_T1_BOUND.cfg';cfg.write_text(''.join(f'{k}={v}\n' for k,v in d.items()))
  plan['cases'][case]={'caps':caps,'config_path':str(cfg),'config_sha256':sha(cfg)}
 save_json(ROOT/'FULL_EXECUTION_BINDING.json',plan);LEDGER['status']='PREPARED_NOT_LAUNCHED';save()
 print('PREPARED_NOT_LAUNCHED',flush=True)

def launch():
 assert not (ROOT/'FULL_LAUNCH_STARTED.json').exists(), 'duplicate full launch forbidden'
 plan=json.loads((ROOT/'FULL_EXECUTION_BINDING.json').read_text());assert plan['status']=='EXACT_BOUND_AFTER_PREFLIGHT'
 assert sha(ROOT/'SOURCE_BINDING.json')==plan['source_binding_sha256'] and sha(ROOT/'PREFLIGHT_VALIDATION.json')==plan['preflight_sha256']
 source=verify_source();binary=source['binary'];assert sha(binary['path'])==binary['sha256']
 assert shutil.disk_usage(ROOT).free>=C['aggregate_scientific_output_bytes']+C['backup_copy_reserve_bytes']
 save_json(ROOT/'FULL_LAUNCH_STARTED.json',{'binding_sha256':sha(ROOT/'FULL_EXECUTION_BINDING.json'),'UTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
 # Keep the hard ceiling high enough for child prlimit to set its reviewed
 # case ceiling; only the controller's soft CPU limit is60 seconds.
 resource.setrlimit(resource.RLIMIT_CPU,(60,C['aggregate_CPU_s']))
 LEDGER['records'].append({'name':'launch_controller_reservation','kind':'controller','status':'RESERVED',
  'CPU_s':60,'wall_s':60,'debit_semantics':'conservative controller reservation, not measured child usage'})
 LEDGER['status']='FULL_T1_RUNNING';save()
 def case_worker(case):
  b=plan['cases'][case];caps=b['caps'];cfg=Path(b['config_path']);assert sha(cfg)==b['config_sha256']
  (ROOT/'cases'/case).mkdir();records=[];previous='IC';used_wall=used_cpu=0.;accepted=0
  try:
   for index in range(C['per_case_full_segments']):
    verify_source();assert sha(binary['path'])==binary['sha256'] and sha(cfg)==b['config_sha256']
    if previous!='IC':
     cp=Path(previous);assert sha(cp)==records[-1]['checkpoint_sha256'];assert sha(cp.parent/'source_identity.txt')==source['reused_compiled_library_identity_sha256']
     assert sha(cp.parent/'config.cfg')==b['config_sha256']
    wall=caps['wall_s']-used_wall;cpu=caps['CPU_s']-used_cpu
    if wall<=12 or cpu<=2 or accepted>=caps['accepted']:break
    count=min(C['segment_accepted'],caps['accepted']-accepted)
    out=ROOT/'cases'/case/f'segment_{index:03d}'
    command=[binary['path'],str(cfg),previous,str(out),case,str(count),str(max(1,wall-10))]
    rec=job(case+f'_segment_{index:03d}',command,ROOT,wall,math.floor(cpu),C['per_process_memory_bytes'],'segment',out)
    records.append(rec);used_wall+=rec['wall_s'];used_cpu+=rec['CPU_s'];s=rec.get('summary')
    if s is None:raise RuntimeError('missing native terminal summary')
    assert s['error']=='NONE' and s['finalization_error']=='NONE',s
    assert rec['source_sha256']==source['reused_compiled_library_identity_sha256']
    if previous!='IC':assert sha(out/'input_checkpoint.txt')==sha(previous)
    accepted=s['end_counts']['accepted'];previous=str(out/'checkpoint.txt')
    assert bytes_in(ROOT/'cases'/case)<=C['per_case_output_bytes']
    with LOCK:
     LEDGER['cases'][case]={'status':s['status'],'segments':len(records),'last_output':str(out),'endpoint':checkpoint(out/'checkpoint.txt'),
       'CPU_s':used_cpu,'wall_s':used_wall,'output_bytes':bytes_in(ROOT/'cases'/case)};save()
    if rec['returncode']==0:assert s['a_end']==.2 and s['scientific_endpoint_reached'];return
    if rec['returncode']!=10 or s['status']!='SEGMENT_ACCEPTED_BOUNDARY':return
   with LOCK:LEDGER['cases'].setdefault(case,{})['status']='CENSORED_FINITE_RESOURCE_OR_SEGMENT_CAP';save()
  except ResourceCensor as e:
   with LOCK:LEDGER['cases'].setdefault(case,{}).update(status='CENSORED_SHARED_SEGMENT_CAP',reason=str(e));save()
  except BaseException as e:
   with LOCK:
    LEDGER['cases'].setdefault(case,{}).update(status='FAILED_PRESERVED_NO_RETRY',error=repr(e),traceback=traceback.format_exc());save()
   print(case+' FAILURE '+repr(e),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(case_worker,['ZERO','PLUS']))
 with LOCK:
  r=resource.getrusage(resource.RUSAGE_SELF);self_cpu=r.ru_utime+r.ru_stime-SELF_START.ru_utime-SELF_START.ru_stime
  controller=next(r for r in LEDGER['records'] if r['name']=='launch_controller_reservation')
  controller.update(status='FINISHED_WITH_RESERVATION_RETAINED',actual_CPU_s=self_cpu,phase_elapsed_wall_s=time.monotonic()-PHASE_START)
  assert self_cpu<60
  spent=debit();LEDGER['current_allocation_debit']=spent
  LEDGER['status']='T1_WAVE_FINISHED_WITH_RETAINED_OUTCOMES'
  assert spent['accepted']<=C['aggregate_accepted'] and spent['trials']<=C['aggregate_trials'] and spent['RHS']<=C['aggregate_RHS']
  assert spent['CPU_s']<=C['aggregate_CPU_s'] and spent['wall_s']<=C['aggregate_sum_job_wall_s']
  assert bytes_in(ROOT/'cases')+bytes_in(ROOT/'preflight')<=C['aggregate_scientific_output_bytes']
  save()
 print(json.dumps({'status':LEDGER['status'],'cases':LEDGER['cases'],'debit':spent}),flush=True)

try:
 assert LEDGER['allocation_sha256']==sha(ROOT/'ALLOCATION.json')
 if PHASE=='prepare':prepare()
 elif PHASE=='launch':launch()
 else:raise ValueError('phase must be prepare or launch')
except BaseException as e:
 save_json(ROOT/(PHASE+'_FAILURE.json'),{'error':repr(e),'traceback':traceback.format_exc(),'no_automatic_retry':True})
 save();traceback.print_exc();sys.exit(1)
