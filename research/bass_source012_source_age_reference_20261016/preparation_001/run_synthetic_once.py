"""Bounded single synthetic test invocation; never starts a native helper."""
from pathlib import Path
import hashlib,json,os,resource,signal,subprocess,time
p=Path(__file__).resolve().parent
argv=['/usr/bin/python3','-m','unittest','-v','test_positive_reference']
files={str(f.relative_to(p)):{'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}
       for f in sorted((p/'code').glob('*')) if f.is_file()}
(p/'CODE_FREEZE.json').open('x').write(json.dumps({'files':files,'argv':argv,'cwd':str(p/'code'),'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'helper':'UNBUILT_UNRUN','physical_RHS_calls':0},indent=2)+'\n')
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
def limit():
    resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824))
    resource.setrlimit(resource.RLIMIT_FSIZE,(16777216,16777216))
start=time.monotonic();epoch=time.time();reason=None
with (p/'raw/stdout').open('xb') as out,(p/'raw/stderr').open('xb') as err:
    child=subprocess.Popen(argv,cwd=p/'code',env=env,stdout=out,stderr=err,start_new_session=True,preexec_fn=limit)
    (p/'raw/STARTED.json').open('x').write(json.dumps({'pid':child.pid,'start_epoch':epoch,'argv':argv,'cwd':str(p/'code'),'AS_bytes':1073741824,'output_bytes':16777216,'wall_cap_s':30},indent=2)+'\n')
    print(json.dumps({'pid':child.pid,'start_epoch':epoch,'argv':argv}),flush=True)
    term=False;kill=False
    while True:
        pid,status,usage=os.wait4(child.pid,os.WNOHANG)
        if pid:break
        elapsed=time.monotonic()-start
        total=sum(f.stat().st_size for f in (p/'raw').glob('*') if f.is_file())
        if (elapsed>=27 or total>=16700000) and not term:
            reason='WALL_LIMIT' if elapsed>=27 else 'OUTPUT_LIMIT';os.killpg(child.pid,signal.SIGTERM);term=True
        if elapsed>=28 and not kill:
            os.killpg(child.pid,signal.SIGKILL);kill=True
        time.sleep(.01)
wall=time.monotonic()-start;code=os.waitstatus_to_exitcode(status);child.returncode=code
receipt={'status':'SYNTHETIC_TESTS_PASS_PENDING_INDEPENDENT_REVIEW' if code==0 and reason is None else 'FAIL_STOP_NO_RETRY','argv':argv,'cwd':str(p/'code'),'env_overrides':{k:env[k] for k in ('PYTHONDONTWRITEBYTECODE','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')},'exit_code':code,'wall_seconds':wall,'user_seconds':usage.ru_utime,'system_seconds':usage.ru_stime,'peak_RSS_bytes':usage.ru_maxrss*1024,'termination_reason':reason,'test_invocations':1,'native_helper_processes':0,'Rust_builds':0,'physical_RHS_calls':0,'runtime_helper':'UNBUILT_UNRUN','requested_model':'gpt-6.1-sol','requested_effort':'high','observed_runtime_model':'NOT_INDEPENDENTLY_OBSERVED'}
(p/'WRAPPER_RECEIPT.json').open('x').write(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt),flush=True)
raise SystemExit(0 if receipt['status'].startswith('SYNTHETIC_TESTS_PASS') else 1)
