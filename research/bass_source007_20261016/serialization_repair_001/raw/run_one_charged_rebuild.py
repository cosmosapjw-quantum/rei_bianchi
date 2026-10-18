import os,time,json,resource,signal,sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent;repo=root.parent.parent.parent;original=json.loads((root.parent/'CONTRACT.json').read_text());repair=json.loads((root/'CONTRACT.json').read_text());contract={**original,'target_dir':repair['target_dir']};kind='build';ledger=root/'raw/INVOCATIONS.json';history=json.loads(ledger.read_text()) if ledger.exists() else []
assert len(history)<1
assert not (root/'raw'/(kind+'.execution.json')).exists()
argv=contract['commands'][kind];env=os.environ.copy();env.update({'CARGO_TARGET_DIR':contract['target_dir'],'CARGO_BUILD_JOBS':'2','RUSTC':contract['toolchain']['rustc'],'RUSTDOC':str(Path(contract['toolchain']['rustc']).with_name('rustdoc')),'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
prior=repair['original_test_build_wall_seconds'];cap=180;assert cap>3
start=time.monotonic();epoch=time.time();pid=os.fork()
if pid==0:
 os.setsid();os.chdir(repo);resource.setrlimit(resource.RLIMIT_AS,(8589934592,8589934592))
 for fd,name in [(1,kind+'.stdout'),(2,kind+'.stderr')]:
  f=os.open(str(root/'raw'/name),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o644);os.dup2(f,fd)
 os.execve(argv[0],argv,env)
record={'kind':kind,'argv':argv,'cwd':str(repo),'pid':pid,'start_epoch':epoch,'wall_cap_seconds':cap,'address_space_bytes':8589934592,'env_overrides':{k:env[k] for k in ['CARGO_TARGET_DIR','CARGO_BUILD_JOBS','RUSTC','RUSTDOC','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS']}}
(root/'raw'/(kind+'.STARTED.json')).write_text(json.dumps(record,indent=2)+'\n');history.append({**record,'exit_code':None,'wall_seconds':0});ledger.write_text(json.dumps(history,indent=2)+'\n');print(json.dumps(record),flush=True)
reason=None;term=None
while True:
 got,status,usage=os.wait4(pid,os.WNOHANG)
 if got:break
 elapsed=time.monotonic()-start
 if elapsed>=cap-3 and term is None:reason='WALL_LIMIT';term=time.monotonic();os.killpg(pid,signal.SIGTERM)
 if term is not None and (time.monotonic()-term>=2 or elapsed>=cap-.3):
  try:os.killpg(pid,signal.SIGKILL)
  except ProcessLookupError:pass
 time.sleep(.03)
wall=time.monotonic()-start;record.update(wait_status=status,exit_code=os.waitstatus_to_exitcode(status),wall_seconds=wall,cpu_user_seconds=usage.ru_utime,cpu_system_seconds=usage.ru_stime,cpu_seconds=usage.ru_utime+usage.ru_stime,peak_rss_bytes=usage.ru_maxrss*1024,termination_reason=reason,child_reaped=True,end_epoch=time.time(),cumulative_wall_seconds=prior+wall,stdout_path=str(root/'raw'/(kind+'.stdout')),stderr_path=str(root/'raw'/(kind+'.stderr')))
(root/'raw'/(kind+'.execution.json')).write_text(json.dumps(record,indent=2)+'\n');history[-1]=record;ledger.write_text(json.dumps(history,indent=2)+'\n');print(json.dumps(record),flush=True)
sys.exit(0 if record['exit_code']==0 else 1)
