"""Bounded, append-only, max-two-process native execution with live disk cap."""
from pathlib import Path
import sys,json,subprocess,os,time,signal,hashlib,argparse
HERE=Path(__file__).resolve().parent;PYTHON='/root/HE25_NCP_BIRTH_20261016/venv/bin/python'
def bytes_used(root):return sum(p.stat().st_size for p in root.rglob('*') if p.is_file())
def main():
 parser=argparse.ArgumentParser();parser.add_argument('plan');a=parser.parse_args();planpath=Path(a.plan);plan=json.loads(planpath.read_text());w=Path(plan['runtime']);jobs=plan['jobs'];active=[];done=[];halt=False
 log=w/(planpath.stem+'_EXECUTION.json');assert not log.exists()
 env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 while jobs or active:
  used=bytes_used(w)
  if used>2*1024**3:halt=True
  while jobs and len(active)<2 and not halt:
   job=jobs.pop(0);out=w/job['name'];assert not out.exists();args=[PYTHON,str(HERE/'run_native_fast.py'),'--out',str(out)]
   for k,v in job['args'].items():args += ['--'+k.replace('_','-'),str(v)]
   f=(w/'logs'/(job['name']+'.log')).open('x');p=subprocess.Popen(args,stdout=f,stderr=subprocess.STDOUT,env=env)
   active.append(dict(process=p,logfile=f,command=args,started=time.monotonic(),name=job['name']))
  for rec in active[:]:
   p=rec['process'];elapsed=time.monotonic()-rec['started']
   if p.poll() is None and (elapsed>600 or used>2*1024**3):
    p.send_signal(signal.SIGINT)
    try:p.wait(timeout=15)
    except subprocess.TimeoutExpired:p.kill();p.wait()
    halt=True
   if p.poll() is not None:
    rec['logfile'].close();done.append(dict(name=rec['name'],command=rec['command'],exit_code=p.returncode,elapsed_s=elapsed,disk_bytes=used));active.remove(rec)
    if p.returncode!=0:halt=True
  if halt and not active:break
  if jobs or active:time.sleep(.5)
 with log.open('x') as f:json.dump({'plan_sha256':hashlib.sha256(planpath.read_bytes()).hexdigest(),'completed':done,'unstarted':[r['name'] for r in jobs],'halted':halt,'workers_max':2,'disk_cap_bytes':2*1024**3},f,indent=2);f.flush();os.fsync(f.fileno())
 print(json.dumps({'completed':len(done),'halted':halt,'unstarted':len(jobs)}))
 if halt:raise SystemExit(1)
if __name__=='__main__':main()
