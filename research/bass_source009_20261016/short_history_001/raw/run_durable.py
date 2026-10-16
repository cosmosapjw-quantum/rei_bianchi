import os,time,json,hashlib,signal,resource,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent.parent;c=json.loads((root/'CONTRACT.json').read_text());assert not (root/'raw/CONTROLLER_STARTED.json').exists();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();calls=[]
def write(p,x):
 tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(x,indent=2)+'\n');tmp.replace(p)
def fields(p):return dict(line.split('=',1) for line in p.read_text().splitlines() if '=' in line)
def require(ok,msg):
 if not ok:raise ValueError(msg)
def output_bytes(out):return sum(p.stat().st_size for p in out.rglob('*') if p.is_file()) if out.exists() else 0
def live_checkpoint(out):
 paths=list((out/'checkpoints').glob('*.bass-v1')) if (out/'checkpoints').exists() else []
 if not paths:return None
 p=max(paths,key=lambda x:x.stat().st_mtime_ns)
 try:
  with p.open() as f:head=[f.readline().strip() for _ in range(14)]
  return {'path':str(p),'compiled_source':head[4],'state_values':head[12].split(),'counters':head[13].split()}
 except Exception as e:return {'path':str(p),'read_error':str(e)}
write(root/'raw/CONTROLLER_STARTED.json',{'pid':os.getpid(),'start_epoch':time.time(),'contract_sha256':sha(root/'CONTRACT.json'),'authority':'explicit root fresh reviewPASS and two cases','planned_cases':[x['case'] for x in c['case_order']]})
for index,item in enumerate(c['case_order']):
 case=item['case'];out=Path(item['output'])
 try:
  require(sha(c['binary'])==c['binary_sha256'],'BINARY_CHANGED');require(sha(c['scenario']['csv'])==c['scenario']['csv_sha256'],'CSV_CHANGED');require(sha(c['scenario']['manifest'])==c['scenario']['manifest_sha256'],'PRODUCER_JSON_CHANGED');require(sha(item['config_path'])==item['config_sha256'],'CONFIG_CHANGED');require(all(sha(x['path'])==x['sha256'] for x in c['compiled_files']),'COMPILED_SOURCE_CHANGED');require(not out.exists(),'FRESH_OUTPUT_REQUIRED')
  argv=item['argv'];env=os.environ.copy();env.update(c['env_overrides']);prior=sum(x['wall_seconds'] for x in calls);cap=min(600,1200-prior);require(cap>3,'NO_TIME_ALLOWANCE');head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=c['cwd'],text=True).strip();start=time.monotonic();epoch=time.time();pid=os.fork()
  if pid==0:
   os.setsid();os.chdir(c['cwd']);resource.setrlimit(resource.RLIMIT_AS,(8589934592,8589934592))
   for fd,ext in [(1,'stdout'),(2,'stderr')]:f=os.open(str(root/'raw'/(case+'.'+ext)),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o644);os.dup2(f,fd)
   os.execve(argv[0],argv,env)
  rec={'case':case,'pid':pid,'controller_pid':os.getpid(),'argv':argv,'cwd':c['cwd'],'env_overrides':c['env_overrides'],'HEAD_read_immediately_before_fork':head,'start_epoch':epoch,'wall_cap_includingtermination_seconds':cap,'AS_bytes':8589934592,'RSS_cap_bytes':2147483648,'total_output_cap_bytes':268435456,'config_sha256':item['config_sha256']};write(root/'raw'/(case+'.STARTED.json'),rec);print(json.dumps(rec),flush=True);term=None;reason=None;last_progress=0;peak_bytes=0;peak_rss=0
  while True:
   got,status,usage=os.wait4(pid,os.WNOHANG)
   if got:break
   elapsed=time.monotonic()-start;size=output_bytes(out)+sum(p.stat().st_size for p in (root/'raw').glob(case+'.*') if p.is_file());peak_bytes=max(peak_bytes,size);rss=0
   try:
    for line in Path(f'/proc/{pid}/status').read_text().splitlines():
     if line.startswith('VmHWM:'):rss=int(line.split()[1])*1024
   except FileNotFoundError:pass
   peak_rss=max(peak_rss,rss)
   if term is None and (elapsed>=cap-3 or size>=268435456 or rss>2147483648):reason='WALL_LIMIT' if elapsed>=cap-3 else 'OUTPUT_LIMIT' if size>=268435456 else 'RSS_LIMIT';term=time.monotonic();os.killpg(pid,signal.SIGTERM)
   if term is not None and (time.monotonic()-term>=2 or elapsed>=cap-.3):
    try:os.killpg(pid,signal.SIGKILL)
    except ProcessLookupError:pass
   if elapsed-last_progress>=5 or last_progress==0:
    write(root/'raw/LIVE_STATUS.json',{'status':'RUNNING' if reason is None else 'TERMINATING','case':case,'pid':pid,'controller_pid':os.getpid(),'elapsed_seconds':elapsed,'RSS_highwater_bytes':rss,'output_bytes':size,'latest_native_checkpoint':live_checkpoint(out),'termination_reason':reason,'observed_epoch':time.time()});last_progress=max(elapsed,.00001)
   time.sleep(.1)
  rec.update(exit_code=os.waitstatus_to_exitcode(status),wait_status=status,wall_seconds=time.monotonic()-start,cpu_user_seconds=usage.ru_utime,cpu_system_seconds=usage.ru_stime,cpu_seconds=usage.ru_utime+usage.ru_stime,peak_rss_bytes=usage.ru_maxrss*1024,peak_monitored_rss_bytes=peak_rss,peak_observed_output_bytes=peak_bytes,child_reaped=True,termination_reason=reason,end_epoch=time.time(),stdout_path=str(root/'raw'/(case+'.stdout')),stderr_path=str(root/'raw'/(case+'.stderr')));calls.append(rec);write(root/'raw'/(case+'.execution.json'),rec);write(root/'raw/EXECUTIONS.json',calls)
  terminal=fields(out/'RETURN.txt') if (out/'RETURN.txt').exists() else None;write(root/'raw'/(case+'.NATIVE_TERMINAL.json'),terminal)
  require(rec['exit_code']==0 and reason is None,'FIRST_CASE_FAILED_OR_CAPPED');require(terminal is not None and terminal['status']=='COMPLETE_REPRESENTED_INTERVAL','NATIVE_INCOMPLETE');require(terminal['source009_sha256']==c['implementation_compiled_source_sha256'] and terminal['inactive_hi_split']=='true','NATIVE_SOURCE_MODE_MISMATCH');cp=Path(terminal['last_checkpoint']);require(cp.is_file(),'NO_TERMINAL_CHECKPOINT');
  with cp.open() as f:prefix=[f.readline().strip() for _ in range(14)]
  require(prefix[4]==c['implementation_compiled_source_sha256'] and '|inactive_hi_split=true' in prefix[2] and 'CURRENT_PROVIDER=SOURCE009' in prefix[3],'CHECKPOINT_SOURCE_MODE_MISMATCH');require(sha(out/'source_identity.txt')==c['implementation_compiled_source_sha256'],'EMITTED_SOURCE_CHANGED');require(int(terminal['accepted'])<=30000 and int(terminal['attempts'])<=100000 and int(terminal['rhs_evaluations'])<=5000000,'NATIVE_COUNTER_CAP')
  write(root/'raw'/(case+'.SUCCESS.json'),{'status':'NATIVE_COMPLETE_PENDING_RESULT_REVIEW','terminal':terminal,'checkpoint_prefix':prefix[:12],'checkpoint_path':str(cp),'checkpoint_sha256':sha(cp)})
 except Exception as exc:
  stopped={'status':'STOPPED_FIRST_FAILURE_NO_RETRY','case':case,'reason':str(exc),'executions':calls,'remaining_cases':[{'case':x['case'],'status':'NOT_RUN_FIRST_CASE_FAILURE'} for x in c['case_order'][index+1:]],'scientific_admission':'NOT_ISSUED'};write(root/'raw/CONTROLLER_TERMINAL.json',stopped);write(root/'raw/LIVE_STATUS.json',stopped);print(json.dumps(stopped),flush=True);break
else:
 final={'status':'BOTH_NATIVE_SHORT_CASES_COMPLETE_REVIEW_PENDING','executions':calls,'scientific_admission':'NOT_ISSUED'};write(root/'raw/CONTROLLER_TERMINAL.json',final);write(root/'raw/LIVE_STATUS.json',final)
