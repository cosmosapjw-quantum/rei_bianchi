import os,time,signal,json,resource
from pathlib import Path
r=Path(__file__).resolve().parent;private=Path('/home/cosmosapjw/REI_PRIVATE_SOURCE012_INPUTS_20261016/static_supplement_001/repair_001');assert not (r/'raw/STARTED.json').exists();assert not private.exists();script=r/'collect_static_blobs_once.py';argv=['/usr/bin/time','-v','-o',str(r/'raw/time.txt'),'/usr/bin/timeout','--signal=TERM','--kill-after=1s','8s','/usr/bin/python3',str(script)];start=time.monotonic();epoch=time.time();pid=os.fork()
if pid==0:
 os.setsid();resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824))
 for fd,name in [(1,'stdout'),(2,'stderr')]:
  f=os.open(r/'raw'/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o644);os.dup2(f,fd);os.close(f)
 os.execv(argv[0],argv)
rec={'argv':argv,'verified_collector_argv':['/usr/bin/python3',str(script)],'cwd':os.getcwd(),'pid':pid,'start_epoch':epoch,'AS_bytes':1073741824,'native_seconds':8,'kill_after_seconds':1,'overall_remaining_seconds':9.65,'attempt_ordinal_in_new_unit':3,'authorized_repair_invocation':1};(r/'raw/STARTED.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec),flush=True);reason=None
while True:
 got,status,usage=os.wait4(pid,os.WNOHANG)
 if got:break
 elapsed=time.monotonic()-start;new_bytes=sum(p.stat().st_size for root in [r,private] if root.exists() for p in root.rglob('*') if p.is_file())
 if reason is None and (elapsed>=9.1 or new_bytes>1048576):
  reason='OUTER_WALL_OR_NEW_OUTPUT_CAP'
  try:os.killpg(pid,signal.SIGTERM)
  except ProcessLookupError:pass
 if reason and elapsed>=9.35:
  try:os.killpg(pid,signal.SIGKILL)
  except ProcessLookupError:pass
 time.sleep(.01)
rec.update(exit_code=os.waitstatus_to_exitcode(status),wall_seconds=time.monotonic()-start,cpu_user_seconds=usage.ru_utime,cpu_system_seconds=usage.ru_stime,peak_rss_bytes=usage.ru_maxrss*1024,child_reaped=True,termination_reason=reason);(r/'WRAPPER_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec),flush=True)
