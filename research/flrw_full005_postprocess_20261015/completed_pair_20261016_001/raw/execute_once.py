import os,time,json,resource,signal,sys
from pathlib import Path
owned=Path(__file__).resolve().parent.parent
c=json.loads((owned/'EXECUTION_CONTRACT.json').read_text()); fresh=Path(c['cwd']); logs=owned/'raw'; limit=c['limits']; env=os.environ.copy();env.update(c['env_overrides']);env['PYTHONDONTWRITEBYTECODE']='1'
start=time.monotonic();epoch=time.time();cap=min(limit['wall_seconds_including_termination'],limit['absolute_deadline_epoch']-epoch)
assert cap>3
pid=os.fork()
if pid==0:
 os.setsid();os.chdir(fresh);resource.setrlimit(resource.RLIMIT_AS,(limit['address_space_bytes'],limit['address_space_bytes']))
 out=os.open(str(logs/'render.stdout'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o644);err=os.open(str(logs/'render.stderr'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o644)
 os.dup2(out,1);os.dup2(err,2)
 os.execve(c['argv'][0],c['argv'],env)
started={'pid':pid,'start_epoch':epoch,'start_monotonic':start,'argv':c['argv'],'cwd':c['cwd'],'env_overrides':{**c['env_overrides'],'PYTHONDONTWRITEBYTECODE':'1'},'wall_cap_seconds':cap}
(logs/'STARTED.json').write_text(json.dumps(started,indent=2)+'\n'); print(json.dumps(started),flush=True)
reason=None;term=None;peak_output=0
while True:
 got,status,usage=os.wait4(pid,os.WNOHANG)
 if got:break
 elapsed=time.monotonic()-start
 total=sum(p.stat().st_size for p in fresh.rglob('*') if p.is_file())+sum(p.stat().st_size for p in logs.glob('render.*') if p.is_file());peak_output=max(peak_output,total)
 if reason is None and (elapsed>=cap-3 or total>=limit['aggregate_output_bytes']):
  reason='WALL_LIMIT' if elapsed>=cap-3 else 'AGGREGATE_OUTPUT_LIMIT';term=time.monotonic();os.killpg(pid,signal.SIGTERM)
 if reason and (time.monotonic()-term>=2 or elapsed>=cap-0.3):
  try:os.killpg(pid,signal.SIGKILL)
  except ProcessLookupError:pass
 time.sleep(.03)
end=time.monotonic();record={**started,'wait_status':status,'exit_code':os.waitstatus_to_exitcode(status),'wall_seconds':end-start,'cpu_user_seconds':usage.ru_utime,'cpu_system_seconds':usage.ru_stime,'cpu_seconds':usage.ru_utime+usage.ru_stime,'peak_rss_bytes':usage.ru_maxrss*1024,'termination_reason':reason,'aggregate_output_peak_observed_bytes':peak_output,'end_epoch':time.time(),'child_reaped':True,'cumulative_postprocess_seconds':limit['prior_postprocess_debit_seconds']+end-start,'stdout_path':str(logs/'render.stdout'),'stderr_path':str(logs/'render.stderr')}
(logs/'execution.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
