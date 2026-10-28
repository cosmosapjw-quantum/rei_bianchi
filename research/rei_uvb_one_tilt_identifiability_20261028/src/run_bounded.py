"""Single-use child process with measured usage, limits and preserved raw logs."""
import sys, subprocess,resource,time,json,os
from pathlib import Path
R=Path(__file__).resolve().parents[1]

def limiter():
 resource.setrlimit(resource.RLIMIT_CPU,(10,11))
 resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,512*1024*1024))

def main():
 if len(sys.argv)!=2 or sys.argv[1]!='--once':raise SystemExit('run once only')
 cmd=[sys.executable,'-I','-S',str(R/'src/suite.py')]
 start=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN)
 environmental=dict(os.environ);environmental['OPENBLAS_NUM_THREADS']='1';environmental['OMP_NUM_THREADS']='1'
 timeout=False
 try:
  child=subprocess.run(cmd,capture_output=True,text=True,timeout=30,preexec_fn=limiter,env=environmental)
  exit_code=child.returncode;stdout=child.stdout;stderr=child.stderr
 except subprocess.TimeoutExpired as e:
  timeout=True;exit_code=124;stdout=(e.stdout or b'').decode() if isinstance(e.stdout,bytes) else e.stdout or '';stderr=(e.stderr or b'').decode() if isinstance(e.stderr,bytes) else e.stderr or ''
 after=resource.getrusage(resource.RUSAGE_CHILDREN)
 cpu=(after.ru_utime+after.ru_stime)-(before.ru_utime+before.ru_stime)
 wall=time.monotonic()-start
 (R/'results').mkdir(parents=True,exist_ok=True)
 (R/'results/RUN.stdout').write_text(stdout);(R/'results/RUN.stderr').write_text(stderr)
 receipt=dict(exit=exit_code,timeout=timeout,command=cmd,measured_child_CPU_seconds=cpu,measured_child_wall_seconds=wall,child_CPU_limit=10,child_wall_limit=30,wrapper_CPU_seconds='NOT_MEASURED',root_reserve_CPU_seconds=1,old_budget='CLOSED',total_session_model_network_overheads='UNKNOWN_NOT_ZERO',new_IVPs=0)
 (R/'results/RUN_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt,indent=2))
 print(stdout[:1900])
 if exit_code!=0:print(stderr[-2500:],file=sys.stderr)
 if exit_code!=0:raise SystemExit(exit_code)
if __name__=='__main__':main()
