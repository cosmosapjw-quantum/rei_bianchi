import os,sys,time,signal,resource,json,subprocess,datetime,hashlib
from pathlib import Path
r=Path(__file__).resolve().parent.parent;label=sys.argv[1];requested=float(sys.argv[2]);as_bytes=int(sys.argv[3]);argv=sys.argv[4:];raw=r/'raw';deadline=datetime.datetime.fromisoformat('2026-10-16T02:50:17.774070+00:00').timestamp();cap=min(requested,deadline-time.time());assert cap>3;assert not (raw/(label+'.STARTED.json')).exists();is_build=label.startswith('build_test');prior=list(raw.glob('build_test*.STARTED.json'));
if is_build and len(prior)>=2:
 repair=r/'REPAIR_AUTHORITY.json';assert hashlib.sha256(repair.read_bytes()).hexdigest()=='c981e632ce7ea3814f1c69b06ba34878e2ea93854d324aab2cf5004fce12bdbb';assert len(prior)<4 and requested<=150
 if list(raw.glob('build_test*.execution.json')):
  charged=sum(json.loads(x.read_text())['wall_seconds'] for x in raw.glob('build_test*.execution.json'));cap=min(cap,600-charged)
else:assert not is_build or len(prior)<2

if label=='probe':
 identities=json.loads((r/'SOURCE_IDENTITIES.json').read_text());assert all(hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()==x['sha256'] for x in identities['compiled_files']);assert hashlib.sha256(Path(argv[0]).read_bytes()).hexdigest()==identities['binary_sha256']
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();env=os.environ.copy();tc='/home/cosmosapjw/.rustup/toolchains/1.94.1-x86_64-unknown-linux-gnu/bin';env.update(PATH=tc+':'+env['PATH'],RUSTC=tc+'/rustc',CARGO_BUILD_JOBS='2',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',SOURCE011_BUILD_HEAD=head,PYTHONDONTWRITEBYTECODE='1');start=time.monotonic();epoch=time.time();pid=os.fork()
if pid==0:
 os.setsid();resource.setrlimit(resource.RLIMIT_AS,(as_bytes,as_bytes))
 for fd,ext in [(1,'stdout'),(2,'stderr')]:
  f=os.open(raw/(label+'.'+ext),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o644);os.dup2(f,fd);os.close(f)
 os.execvpe(argv[0],argv,env)
rec={'argv':argv,'cwd':os.getcwd(),'HEAD':head,'pid':pid,'start_epoch':epoch,'AS_bytes':as_bytes,'wall_cap_including_termination':cap,'build_test_invocation':len(prior)+1 if is_build else None,'env_overrides':{k:env[k] for k in ['RUSTC','CARGO_BUILD_JOBS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','SOURCE011_BUILD_HEAD','PYTHONDONTWRITEBYTECODE']}};(raw/(label+'.STARTED.json')).write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec),flush=True);term=None
while True:
 got,status,usage=os.wait4(pid,os.WNOHANG)
 if got:break
 elapsed=time.monotonic()-start
 size=sum(p.stat().st_size for p in Path(argv[-1]).rglob('*') if p.is_file()) if label=='probe' and Path(argv[-1]).exists() else 0
 if (elapsed>=cap-3 or (label=='probe' and size>=67108864)) and term is None:
  term=time.monotonic()
  try:os.killpg(pid,signal.SIGTERM)
  except ProcessLookupError:pass
 if term and (time.monotonic()-term>=2 or elapsed>=cap-.3):
  try:os.killpg(pid,signal.SIGKILL)
  except ProcessLookupError:pass
 time.sleep(.05)
rec.update(exit_code=os.waitstatus_to_exitcode(status),wall_seconds=time.monotonic()-start,cpu_user_seconds=usage.ru_utime,cpu_system_seconds=usage.ru_stime,peak_rss_bytes=usage.ru_maxrss*1024,child_reaped=True,termination_reason='WALL_OR_ABSOLUTE_DEADLINE' if term else None);(raw/(label+'.execution.json')).write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec),flush=True);sys.exit(0 if rec['exit_code']==0 else 1)
