"""Three owned native cases; resource-bounded resumable subprocess scheduler."""
from pathlib import Path
import argparse,datetime,hashlib,json,math,os,platform,resource,signal,subprocess,sys,time,zipfile,tarfile,io
HERE=Path(__file__).resolve().parent;TASK=HERE.parent;sys.path.insert(0,str(TASK/'src'))
from run_refinement import sha,save,validate_outputs,plan
from prepare import restore,generate
from analyze import postprocess
GIB=1024**3;CASES=['time8','time16','time32']
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def host():
 cpus=min(os.cpu_count() or 1,len(os.sched_getaffinity(0)))
 cpu=Path('/sys/fs/cgroup/cpu.max');memory=Path('/sys/fs/cgroup/memory.max')
 if cpu.exists():
  maximum,period=cpu.read_text().split()
  if maximum!='max':cpus=min(cpus,max(1,int(maximum)//int(period)))
 values={line.split(':')[0]:int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith(('MemTotal:','MemAvailable:'))}
 mem=min(values.values())
 if memory.exists() and memory.read_text().strip()!='max':
  current=memory.with_name('memory.current');used=int(current.read_text()) if current.exists() else 0
  mem=min(mem,max(0,int(memory.read_text())-used))
 return dict(cpus=cpus,memory_bytes=mem,affinity=sorted(os.sched_getaffinity(0)),cpu_max=cpu.read_text().strip() if cpu.exists() else None,utc=utc(),load_average=os.getloadavg())
def allocation(h,cpus=None,memory=None):
 c=min(h['cpus'],cpus if cpus is not None else h['cpus'],63);m=min(h['memory_bytes'],memory if memory is not None else h['memory_bytes'])
 reserve=min(16*GIB,m//4);jobs=min(3,c//2,max(0,(m-reserve)//GIB))
 if jobs<1:raise ValueError('INSUFFICIENT_DECLARED_RESOURCES')
 workers=min(20,c//jobs-1);case_mem=min(24*GIB,(m-reserve)//jobs)
 return dict(jobs=jobs,workers=workers,slots_per_case=workers+1,total_slots=jobs*(workers+1),case_memory_bytes=case_mem,reserve_bytes=reserve,available_cpus=c,available_memory_bytes=m)
def hashes(path):return {str(p.relative_to(path)):sha(p) for p in sorted(path.rglob('*')) if p.is_file()}
def reusable(row,identity):
 return row.get('status')=='COMPLETE' and row['identity']==identity and bool(row.get('outputs')) and all((Path(row['data'])/n).is_file() and sha(Path(row['data'])/n)==v for n,v in row['outputs'].items())
def restore_reference(c10,out):
 # Restore the original returned native32 archive automatically, never launch it.
 if c10 is None:return None
 raw=out/'raw_reference';receipt=out/'RAW_INPUTS.json'
 if receipt.exists():
  cached=json.loads(receipt.read_text());path=Path(cached['age32_data'])
  if cached.get('archive_sha256')!='8c4579811faefbf3738c2dcd3c5105300a9aedec0b08c930bee032e094ef0cde' or not cached.get('outputs') or not all((path.parent/n).is_file() and sha(path.parent/n)==v for n,v in cached['outputs'].items()):raise ValueError('CACHED_REFERENCE_OUTPUT_IDENTITY_MISMATCH')
  return path
 name='archive_only/native_age32/REI_AGE32_BLOCKMAX_DIAGNOSTICS_NCP_20261020T112800Z.tar.gz'
 with zipfile.ZipFile(c10) as z:data=z.read(name)
 digest=hashlib.sha256(data).hexdigest()
 if digest!='8c4579811faefbf3738c2dcd3c5105300a9aedec0b08c930bee032e094ef0cde':raise ValueError('REFERENCE_TAR_IDENTITY')
 with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as t:
  for member in t.getmembers():
   if member.name.startswith('run_corrected/results/age32/attempt001/'):
    p=Path(member.name)
    if p.is_absolute() or '..' in p.parts or not(member.isfile() or member.isdir()):raise ValueError('REFERENCE_LAYOUT')
    t.extract(member,raw,filter='data')
 path=raw/'run_corrected/results/age32/attempt001/data';save(receipt,dict(age32_data=str(path.resolve()),archive_sha256=digest,outputs=hashes(path.parent),source=str(c10),scope='STORED_POSITIVE_DOP853_REFERENCE; distinct operator from native BE; no native rerun'))
 return path

def _proc_identity(path):
 try:
  namespace=os.readlink(path/'ns/pid')
  if namespace!=os.readlink('/proc/self/ns/pid'):return None
  status={r.split(':',1)[0]:r.split(':',1)[1].strip() for r in (path/'status').read_text().splitlines() if ':' in r}
  logical=int(status.get('NSpid',status['Pid']).split()[-1]);pgid=int(status.get('NSpgid','0').split()[-1])
  text=(path/'stat').read_text();fields=text[text.rfind(')')+2:].split()
  return dict(pid=logical,proc_pid=int(status['Pid']),state=fields[0],pgid=pgid or int(fields[2]),start_ticks=fields[19],namespace=namespace)
 except (OSError,ValueError,KeyError):return None

def prior_child_live(row):
 identity=row.get('child_identity')
 if not identity:raise RuntimeError('PRIOR_LAUNCH_IDENTITY_UNCERTAIN_NO_NEW_LAUNCH')
 path=Path('/proc')/str(identity['proc_pid']);current=_proc_identity(path)
 if current is None:
  if path.exists():raise RuntimeError('PRIOR_PROC_IDENTITY_UNCERTAIN_NO_NEW_LAUNCH')
  return False
 return current['state']!='Z' and current['start_ticks']==identity['start_ticks'] and current['namespace']==identity['namespace']

def run_scheduler(binary,out,identity,a,*,case_wall=1800,total_wall=5400,elapsed_cap=2000,command_factory=None):
 out.mkdir(parents=True,exist_ok=True);lock=out/'.scheduler.lock'
 if lock.exists():
  pid=int(lock.read_text())
  try:os.kill(pid,0)
  except ProcessLookupError:lock.unlink()
  else:raise RuntimeError('OWN_CAMPAIGN_ALREADY_RUNNING')
 fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
 ledger_path=out/'CAMPAIGN.json';ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else dict(attempts=[],elapsed_used=0.,PRODUCTION_SCIENTIFIC_ADMISSION='NOT_ISSUED')
 recovered=[]
 try:
  for r in ledger['attempts']:
   if r.get('status') in ['RUNNING','STARTING']:
    if prior_child_live(r):raise RuntimeError('LIVE_OWN_ORPHAN_NO_NEW_LAUNCH')
    r.update(status='INCOMPLETE',failure='PRIOR_CHILD_EXIT_CONFIRMED',wall_seconds=r['cap_seconds'])
    r['outputs']=hashes(Path(r['data']));save(Path(r['data']).parent/'RECEIPT.json',r);recovered.append(r['cap_seconds'])
 except Exception:
  lock.unlink();raise
 if recovered:ledger['elapsed_used']+=sum(recovered)
 ledger['current_identity']=identity
 active={};start=time.monotonic();previous_elapsed=ledger['elapsed_used'];queue=[]
 try:
  for name in CASES:
   prior=[r for r in ledger['attempts'] if r['case']==name]
   if any(reusable(r,identity) for r in prior):continue
   if prior:continue # Never replay failed, interrupted, mismatched or corrupted attempts automatically.
   queue.append(name)
  def persist():
   ledger['elapsed_used']=previous_elapsed+time.monotonic()-start;save(ledger_path,ledger)
  while queue or active:
   consumed=sum(r.get('wall_seconds',0.) for r in ledger['attempts'] if r.get('status')!='RUNNING')
   remaining_elapsed=elapsed_cap-previous_elapsed-(time.monotonic()-start)
   if remaining_elapsed<=0:queue=[]
   while queue and len(active)<a['jobs'] and remaining_elapsed>0:
    # Reserve full wall allowance of every launched child; never oversubscribe aggregate budget.
    reservations=sum(r['cap_seconds'] for _,r,_,_,_ in active.values())
    cap=min(case_wall,total_wall-consumed-reservations,remaining_elapsed)
    if cap<=0:queue=[];break
    name=queue.pop(0);attempt=name+'_attempt001';directory=out/name/'attempt001';directory.mkdir(parents=True,exist_ok=False);data=directory/'data';data.mkdir()
    argv=command_factory(name,data) if command_factory else [str(binary),'native_refine','0.0',str(data),'32','8','8','16','8,16,32,64',name[4:]]
    env=dict(os.environ,REI_TRANSPORT_THREADS=str(a['workers']),REI_SUBNORMAL_REPAIR='subnormal-barycenter',REI_BE_TRACE=str(data/'be_trace.jsonl'),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    env.pop('REI_FULL_TRACE',None)
    row=dict(case=name,attempt=attempt,status='STARTING',data=str(data.resolve()),identity=identity,command=argv,env={k:env[k] for k in ['REI_TRANSPORT_THREADS','REI_SUBNORMAL_REPAIR','REI_BE_TRACE','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']},started_utc=utc(),cap_seconds=cap,address_space_bytes=a['case_memory_bytes'])
    ledger['attempts'].append(row);persist()
    stdout=(directory/'stdout.log').open('xb');stderr=(directory/'stderr.log').open('xb')
    def limit():
     child=_proc_identity(Path('/proc/self'))
     if child is None:raise RuntimeError('OWN_CHILD_IDENTITY_UNAVAILABLE')
     save(directory/'CHILD_IDENTITY.json',child)
     resource.setrlimit(resource.RLIMIT_AS,(a['case_memory_bytes'],a['case_memory_bytes']))
    launch_start=time.monotonic()
    try:proc=subprocess.Popen(argv,env=env,stdout=stdout,stderr=stderr,start_new_session=True,preexec_fn=limit)
    except (OSError,subprocess.SubprocessError) as e:
     stdout.close();stderr.close();row.update(status='FAILED',failure='LAUNCH_EXCEPTION:'+repr(e),exit_code=None,wall_seconds=time.monotonic()-launch_start,ended_utc=utc(),outputs=hashes(data))
     save(directory/'RECEIPT.json',row);persist();continue
    active[proc.pid]=(proc,row,launch_start,stdout,stderr)
    try:
     child=json.loads((directory/'CHILD_IDENTITY.json').read_text())
     if child['pid']!=proc.pid:raise ValueError('OWN_CHILD_PID_HANDOFF_MISMATCH')
    except (OSError,ValueError) as e:
     row['failure']='OWN_CHILD_IDENTITY_HANDOFF_UNCERTAIN:'+repr(e);persist();raise RuntimeError(row['failure'])
    row.update(status='RUNNING',child_identity=child);persist()
   for pid,(proc,row,t0,stdout,stderr) in list(active.items()):
    waited,wait_status,usage=os.wait4(pid,os.WNOHANG)
    timed=time.monotonic()-t0>=row['cap_seconds'] or previous_elapsed+time.monotonic()-start>=elapsed_cap
    if not waited and timed:
     os.killpg(pid,signal.SIGTERM)
     # Bound cleanup of an owned child even if SIGTERM is ignored.
     until=time.monotonic()+.5
     while time.monotonic()<until:
      waited,wait_status,usage=os.wait4(pid,os.WNOHANG)
      if waited:break
      time.sleep(.01)
     if not waited:os.killpg(pid,signal.SIGKILL)
     try:
      if not waited:waited,wait_status,usage=os.wait4(pid,0)
     except ChildProcessError:raise RuntimeError('CHILD_RESOURCE_RECEIPT_MISSING')
    if waited:
     proc.returncode=os.waitstatus_to_exitcode(wait_status);stdout.close();stderr.close()
     row.update(exit_code=124 if timed else proc.returncode,wall_seconds=time.monotonic()-t0,ended_utc=utc(),usage=dict(user_seconds=usage.ru_utime,system_seconds=usage.ru_stime,max_rss_kib=usage.ru_maxrss),status='INCOMPLETE' if timed else 'FAILED')
     if row['exit_code']==0:
      try:
       if command_factory is None:validate_outputs(plan()[row['case']],Path(row['data']))
       row['status']='COMPLETE'
      except Exception as e:row['failure']=repr(e)
     if row['status']!='COMPLETE':
      try:os.killpg(pid,signal.SIGKILL)
      except ProcessLookupError:pass
     row['outputs']=hashes(Path(row['data']));save(Path(row['data']).parent/'RECEIPT.json',row);del active[pid];persist()
   if active:time.sleep(.02)
   elif not queue:break
  persist();ledger['missing_cases']=[n for n in CASES if not any(r['case']==n and reusable(r,identity) for r in ledger['attempts'])];save(ledger_path,ledger);return ledger
 finally:
  for proc,row,t0,stdout,stderr in active.values():
   if proc.returncode is None:
    try:os.killpg(proc.pid,signal.SIGKILL);os.wait4(proc.pid,0)
    except ProcessLookupError:pass
   stdout.close();stderr.close()
   row.update(status='INCOMPLETE',failure=row.get('failure','CONTROLLER_EXIT_OWN_CHILD_TERMINATED'),wall_seconds=row['cap_seconds'],outputs=hashes(Path(row['data'])),ended_utc=utc())
   save(Path(row['data']).parent/'RECEIPT.json',row)
  if active:
   ledger['elapsed_used']=previous_elapsed+time.monotonic()-start+sum(r['cap_seconds'] for _,r,_,_,_ in active.values());save(ledger_path,ledger)
  lock.unlink()

def baseline_reference_identity():
 path=TASK/'evidence/ncp_blockmax_20261019T084150Z/run/native/BUILD_RECEIPT.json'
 if sha(path)!='d81a3fe76f3a5d4f140cfa522224c2bea7bc67f4bc50be6bed8c83b67debff3e':raise ValueError('B1_BASELINE_RECEIPT_CHANGED')
 value=json.loads(path.read_text())
 if value['binary_sha256']!='89c646db1de80c6e85fe34f7c3eaae2f10904810a8a6c3acc3426a7e7c1dd7a4' or value['prepared_identity_sha256']!='e376b58ee3ef2b14cda70bc8d966d686db52aabc0a832cab0b8cc0ea8a430bfd':raise ValueError('B1_BASELINE_BINDING')
 return dict(receipt=str(path),receipt_sha256=sha(path),binary_sha256=value['binary_sha256'],prepared_identity_sha256=value['prepared_identity_sha256'],relation='ORIGINAL_B1_REFERENCE; V10_BE_BINARY_IS_DISTINCT')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--c10',type=Path);p.add_argument('--repo',type=Path);p.add_argument('--rust-prefix',type=Path);p.add_argument('--available-cpus',type=int);p.add_argument('--available-memory-gib',type=float);p.add_argument('--plan-only',action='store_true')
 a=p.parse_args();h=host();alloc=allocation(h,a.available_cpus,int(a.available_memory_gib*GIB) if a.available_memory_gib else None)
 if a.plan_only:print(json.dumps(dict(host=h,allocation=alloc,cases=CASES,case_wall_s=1800,total_child_wall_s=5400,elapsed_cap_s=min(5600,math.ceil(3/alloc['jobs'])*1800+200),compile_cap_s=300,CPU_upper_core_s=113400),indent=2));return
 if bool(a.repo)==bool(a.c10):p.error('choose one offline --repo or --c10')
 if a.rust_prefix is None:p.error('--rust-prefix required')
 a.out.mkdir(parents=True,exist_ok=True);save(a.out/('HOST_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json'),dict(host=h,allocation=alloc))
 prepared=a.runtime/'prepared'
 if not prepared.exists():generate(restore(a.runtime/'native153',a.repo,a.c10),prepared)
 prepared_identity=json.loads((prepared/'PREPARED_IDENTITY.json').read_text())
 expected_overlay={p.name:sha(p) for p in [HERE/'prepare.py',HERE/'accessors.rs',HERE/'observer.rs']}
 if prepared_identity.get('source_files')!=expected_overlay:raise ValueError('STALE_V10_PREPARED_OVERLAY')
 for name,digest in prepared_identity['outputs'].items():
  if sha(prepared/name)!=digest:raise ValueError('PREPARED_SOURCE_CHANGED:'+name)
 env=dict(os.environ,PATH=str(a.rust_prefix/'bin')+os.pathsep+os.environ['PATH'])
 subprocess.run([sys.executable,str(TASK/'src/build_native.py'),'--prepared',str(prepared),'--wall-s','300'],env=env,check=True)
 binary=prepared/'rust/rei_microphysics/target/release/examples/positive_native'
 import numpy,scipy
 identity=dict(baseline_reference_identity=baseline_reference_identity(),binary_sha256=sha(binary),prepared_sha256=sha(prepared/'PREPARED_IDENTITY.json'),source_sha256={p.name:sha(p) for p in HERE.iterdir() if p.is_file() and p.suffix in ['.py','.rs']},python=platform.python_version(),numpy=numpy.__version__,scipy=scipy.__version__,workers=alloc['workers'])
 preflight=a.runtime/'preflight'
 if not (preflight/'PREFLIGHT.json').is_file():
  subprocess.run([sys.executable,str(HERE/'verify.py'),'--prepared',str(prepared),'--out',str(preflight),'--rust-prefix',str(a.rust_prefix),'--tiny-only'],env=env,check=True)
  save(preflight/'PREFLIGHT.json',identity)
 elif json.loads((preflight/'PREFLIGHT.json').read_text())!=identity:raise ValueError('PREFLIGHT_IDENTITY_CHANGED')
 elapsed_cap=min(5600,math.ceil(3/alloc['jobs'])*1800+200)
 ledger=run_scheduler(binary,a.out,identity,alloc,elapsed_cap=elapsed_cap);reference=None
 try:reference=restore_reference(a.c10,a.out)
 except ValueError as e:save(a.out/'REFERENCE_REFUSAL.json',dict(status='INELIGIBLE_REFERENCE',reason=str(e)))
 postprocess(a.out,ledger,reference);print(json.dumps(dict(status='CAMPAIGN_RECORDED',missing=ledger['missing_cases'],PRODUCTION_SCIENTIFIC_ADMISSION='NOT_ISSUED')))
if __name__=='__main__':main()
