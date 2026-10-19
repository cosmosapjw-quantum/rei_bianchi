#!/usr/bin/env python3
"""Capture exact native run inputs and outputs before executing bounded cases."""
import datetime,hashlib,json,os,pathlib,subprocess,sys,time,tarfile
ROOT=pathlib.Path(__file__).resolve().parents[2]
IMPL=ROOT/'v16_work/implementation'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def capture(label,command,timeout=40):
 out=IMPL/'receipts'/label;out.mkdir(exist_ok=True)
 files=[]
 for source in [ROOT/'v15_work/native_owner/rust/rei_microphysics',ROOT/'v16_work/vigilode_intake/native_source_closure',IMPL]:
  files.extend(p for p in source.rglob('*') if p.is_file() and not any(part in ('target','.git','receipts','__pycache__') for part in p.relative_to(source).parts))
 manifest={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(files))}
 # Freeze exact source bytes before the process starts, including adapter/native additions.
 with tarfile.open(out/'sources.tar.gz','w:gz') as archive:
  for p in sorted(set(files)):archive.add(p,arcname=str(p.relative_to(ROOT)),recursive=False)
 env=os.environ.copy();env.update({'CARGO_HOME':str(ROOT/'v16_work/vigilode_intake/cargo_home'),'RUSTC':str(ROOT/'v15_work/toolchain/bin/rustc'),'CARGO_BUILD_JOBS':'1'})
 pre={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cwd':str(ROOT),'command':command,'timeout_s':timeout,'source_sha256':manifest,'source_archive_sha256':sha(out/'sources.tar.gz'),'environment':{k:env[k] for k in ('CARGO_HOME','RUSTC','CARGO_BUILD_JOBS')}}
 for arg in command:
  p=ROOT/arg
  if p.is_file() and os.access(p,os.X_OK):pre.setdefault('executables_sha256',{})[str(p.relative_to(ROOT))]=sha(p)
 (out/'inputs.json').write_text(json.dumps(pre,indent=2)+'\n')
 start=time.monotonic();truncated=False
 with (out/'stdout.txt').open('wb') as stdout,(out/'stderr.txt').open('wb') as stderr:
  try:result=subprocess.run(command,cwd=ROOT,env=env,stdout=stdout,stderr=stderr,timeout=timeout);code=result.returncode
  except subprocess.TimeoutExpired:truncated=True;code=None
 receipt={'label':label,'exit_code':code,'truncated':truncated,'wall_s':time.monotonic()-start,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stdout_sha256':sha(out/'stdout.txt'),'stderr_sha256':sha(out/'stderr.txt')}
 (out/'outcome.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
 return 1 if truncated or code!=0 else 0
if __name__=='__main__':
 if len(sys.argv)<4:raise SystemExit('usage run_captured.py label timeout_s command...')
 raise SystemExit(capture(sys.argv[1],sys.argv[3:],float(sys.argv[2])))
