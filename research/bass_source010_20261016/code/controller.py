import os,time,json,hashlib,signal,resource,datetime
from pathlib import Path
r=Path('/root/REI_BASS_SOURCE010_20261016_001');c=json.loads((r/'CONTRACT.json').read_text());pre=json.loads((r/'raw/PREFLIGHT.json').read_text());plan=json.loads((r/'LAUNCH_PLAN.json').read_text());deadline=datetime.datetime.fromisoformat(c['limits']['absolute_deadline_utc'].replace('Z','+00:00')).timestamp();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();active={};done=[]
def write(name,obj):
 p=r/'raw'/name;t=p.with_suffix('.tmp');t.write_text(json.dumps(obj,indent=2)+'\n');t.replace(p)
def free():s=os.statvfs(r);return s.f_bavail*s.f_frsize
def fields(p):return dict(l.split('=',1) for l in p.read_text().splitlines() if '=' in l)
def ownsize(out,case):return sum(p.stat().st_size for p in out.rglob('*') if p.is_file())+sum(p.stat().st_size for p in (r/'raw').glob(case+'.*') if p.is_file())
def stop(rec,reason):
 if rec.get('termination_reason') is None:
  rec['termination_reason']=reason;rec['term_monotonic']=time.monotonic()
  try:os.killpg(rec['pid'],signal.SIGTERM)
  except ProcessLookupError:pass
assert not (r/'raw/CONTROLLER_STARTED.json').exists(),'NO_DUPLICATE_CONTROLLER'
assert pre['status']=='ABI_AND_RESOURCE_PREFLIGHT_PASS'
write('CONTROLLER_STARTED.json',{'pid':os.getpid(),'epoch':time.time(),'contract_sha256':sha(r/'CONTRACT.json'),'absolute_deadline_epoch':deadline,'preflight_sha256':sha(r/'raw/PREFLIGHT.json')})
shared_fail=None
try:
 for idx,case in enumerate(c['case_order']):
  assert free()>=10*2**30,'PRELAUNCH_DISK_LT_10GIB'
  for i in c['inputs']:assert sha(r/'inputs'/('bass_adaptive_trial' if i['kind']=='binary' else Path(i['local_path']).name))==i['sha256'],'IMMUTABLE_INPUT_CHANGED'
  cfg=r/'configs'/(case+'.cfg');assert sha(cfg)==plan['cases'][idx]['config_sha256'],'CONFIG_FROZEN_HASH_CHANGED'
  cap=min(900,deadline-time.time());assert cap>=883,'INSUFFICIENT_FROZEN_WALL_WINDOW'
  out=r/'results'/case;assert not out.exists(),'FRESH_OUTPUT_REQUIRED';argv=[str(r/'inputs/bass_adaptive_trial'),str(r/'inputs/pr164_121.csv'),str(r/'inputs/pr164_121.json'),str(cfg),case,str(out),'source010-half-target-001-'+case];assert argv==plan['cases'][idx]['argv'],'ARGV_PLAN_CHANGED';cpu=pre['selected_cpus'][idx];start=time.monotonic();epoch=time.time();env=os.environ.copy();env.update({k:'1' for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']});pid=os.fork()
  if pid==0:
   os.setsid();os.chdir(r);os.sched_setaffinity(0,{cpu});resource.setrlimit(resource.RLIMIT_AS,(8*2**30,8*2**30))
   for fd,ext in [(1,'stdout'),(2,'stderr')]:
    f=os.open(r/'raw'/(case+'.'+ext),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o644);os.dup2(f,fd);os.close(f)
   os.execve(argv[0],argv,env)
  rec={'case':case,'pid':pid,'controller_pid':os.getpid(),'argv':argv,'cwd':str(r),'env_overrides':{k:env[k] for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']},'CPU_affinity':[cpu],'CPU_exclusive':False,'start_epoch':epoch,'start_monotonic':start,'wall_cap_seconds':cap,'AS_bytes':8*2**30,'RSS_cap_bytes':2*2**30,'output_cap_bytes':2*2**30,'config_sha256':sha(cfg),'binary_sha256':sha(r/'inputs/bass_adaptive_trial'),'termination_reason':None,'peak_observed_output_bytes':0,'peak_observed_RSS_bytes':0};active[pid]=rec;write(case+'.STARTED.json',rec)
except Exception as e:
 shared_fail=str(e)
 for rec in active.values():stop(rec,shared_fail)
last=0
while active:
 disk=free();combined=0
 for pid,rec in list(active.items()):
  got,status,usage=os.wait4(pid,os.WNOHANG);out=r/'results'/rec['case'];elapsed=time.monotonic()-rec['start_monotonic']
  if got:
   rec.update(exit_code=os.waitstatus_to_exitcode(status),wall_seconds=elapsed,cpu_user_seconds=usage.ru_utime,cpu_system_seconds=usage.ru_stime,peak_rss_bytes=usage.ru_maxrss*1024,child_reaped=True,end_epoch=time.time());rec.pop('term_monotonic',None);terminal=fields(out/'RETURN.txt') if (out/'RETURN.txt').exists() else None;rec['native_terminal']=terminal;rec['status']='NATIVE_COMPLETE_PENDING_REVIEW' if rec['exit_code']==0 and rec['termination_reason'] is None and terminal and terminal.get('status')=='COMPLETE_REPRESENTED_INTERVAL' else 'FAILED_OR_CAPPED_NO_RETRY';write(rec['case']+'.execution.json',rec);done.append(rec);del active[pid];continue
  size=ownsize(out,rec['case']);combined+=size;rec['peak_observed_output_bytes']=max(rec['peak_observed_output_bytes'],size);rss=0
  try:
   for l in Path('/proc/'+str(pid)+'/status').read_text().splitlines():
    if l.startswith('VmRSS:'):rss=int(l.split()[1])*1024
  except FileNotFoundError:pass
  rec['peak_observed_RSS_bytes']=max(rec['peak_observed_RSS_bytes'],rss);rec['elapsed_seconds']=elapsed;rec['observed_output_bytes']=size;rec['current_RSS_bytes']=rss
  if disk<8*2**30:shared_fail='DISK_FLOOR_LT_8GIB'
  if shared_fail:stop(rec,shared_fail)
  if elapsed>=rec['wall_cap_seconds']-3 or time.time()>=deadline-3:stop(rec,'WALL_OR_ABSOLUTE_DEADLINE')
  if size>=2*2**30:shared_fail='OUTPUT_CAP';stop(rec,shared_fail)
  if rss>2*2**30:shared_fail='RSS_CAP';stop(rec,shared_fail)
  if rec.get('termination_reason') and (time.monotonic()-rec['term_monotonic']>=2 or elapsed>=rec['wall_cap_seconds']-.3):
   try:os.killpg(pid,signal.SIGKILL)
   except ProcessLookupError:pass
 if combined>=4*2**30:shared_fail='COMBINED_OUTPUT_CAP'
 if time.monotonic()-last>=5:write('LIVE_STATUS.json',{'status':'RUNNING','controller_pid':os.getpid(),'disk_free_bytes':disk,'active':list(active.values()),'completed':done,'shared_failure':shared_fail,'epoch':time.time()});last=time.monotonic()
 time.sleep(.1)
terminal={'status':'BOTH_COMPLETE_REVIEW_PENDING' if len(done)==2 and all(x['status']=='NATIVE_COMPLETE_PENDING_REVIEW' for x in done) else 'STOPPED_OR_PARTIAL_REVIEW_PENDING','executions':done,'shared_failure':shared_fail,'unlaunched':[x for x in c['case_order'] if x not in [v['case'] for v in done]],'sum_process_wall_seconds':sum(x['wall_seconds'] for x in done),'scientific_admission':'NOT_ISSUED'};write('CONTROLLER_TERMINAL.json',terminal);write('LIVE_STATUS.json',terminal)
