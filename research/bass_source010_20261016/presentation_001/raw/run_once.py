import os,sys,json,time,signal,resource,hashlib,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent.parent
argv=['/usr/bin/python3',str(r/'code/plot_native_Y.py'),'--contract',str(r/'CONTRACT.json'),'--output',str(r/'results')]
env=os.environ.copy();overrides={k:'1' for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']};env.update(overrides);env['PYTHONDONTWRITEBYTECODE']='1'
def write(name,obj):(r/'raw'/name).write_text(json.dumps(obj,indent=2)+'\n')
start=time.monotonic();epoch=time.time();pid=os.fork()
if pid==0:
 os.setsid();resource.setrlimit(resource.RLIMIT_AS,(2**31,2**31))
 for fd,name in [(1,'stdout'),(2,'stderr')]:
  out=os.open(r/'raw'/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o644);os.dup2(out,fd);os.close(out)
 os.execve(argv[0],argv,env)
rec={'argv':argv,'cwd':os.getcwd(),'env_overrides':overrides,'pid':pid,'start_epoch':epoch,'contract_sha256':hashlib.sha256((r/'CONTRACT.json').read_bytes()).hexdigest(),'limits':{'wall_including_termination_seconds':30,'AS_bytes':2**31,'output_bytes':128*2**20},'HEAD_at_launch':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()};write('STARTED.json',rec);print(json.dumps(rec),flush=True);term=None
while True:
 done,status,usage=os.wait4(pid,os.WNOHANG)
 if done:break
 elapsed=time.monotonic()-start;size=sum(p.stat().st_size for p in r.rglob('*') if p.is_file())
 if term is None and (elapsed>=27 or size>128*2**20):
  term='WALL_OR_OUTPUT_CAP';os.killpg(pid,signal.SIGTERM)
 if elapsed>=29:
  try:os.killpg(pid,signal.SIGKILL)
  except ProcessLookupError:pass
 time.sleep(.05)
rec.update(exit_code=os.waitstatus_to_exitcode(status),wall_seconds=time.monotonic()-start,cpu_user_seconds=usage.ru_utime,cpu_system_seconds=usage.ru_stime,peak_rss_bytes=usage.ru_maxrss*1024,termination_reason=term,child_reaped=True,status='EXIT_ZERO_REVIEW_PENDING' if status==0 else 'TYPED_PRESENTATION_FAIL_NO_RETRY');write('execution.json',rec);print(json.dumps(rec),flush=True)
