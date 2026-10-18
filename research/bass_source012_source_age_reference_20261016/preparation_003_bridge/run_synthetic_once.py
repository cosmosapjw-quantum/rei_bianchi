"""ONE bounded synthetic unittest command. Never runs the real candidate ELF."""
from pathlib import Path
import hashlib,json,os,resource,signal,subprocess,time
p=Path(__file__).resolve().parent;code_dir=p/'code'
argv=['/usr/bin/python3','-m','unittest','-v','test_setup_bridge']
freeze={'argv':argv,'cwd':str(code_dir),'files':{str(f.relative_to(p)):{'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size} for f in sorted(code_dir.glob('*.py'))},'decoder_sha256':'87c85841e12b4265984a75fd5e82f7164a466b88800e51aa992029376bf0577a','real_helper_launches_authorized':0,'fake_helper_processes_expected':1,'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}
(p/'CODE_FREEZE.json').open('x').write(json.dumps(freeze,indent=2)+'\n')
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
def limits():
    resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824))
    resource.setrlimit(resource.RLIMIT_FSIZE,(8388608,8388608))
start=time.monotonic();reason=None
with (p/'raw/stdout').open('xb') as out,(p/'raw/stderr').open('xb') as err:
    child=subprocess.Popen(argv,cwd=code_dir,env=env,stdout=out,stderr=err,preexec_fn=limits,start_new_session=True)
    (p/'raw/STARTED.json').open('x').write(json.dumps({'pid':child.pid,'argv':argv,'cwd':str(code_dir),'start_epoch':time.time(),'AS_bytes':1073741824,'output_bytes':8388608,'wall_cap_s':20},indent=2)+'\n')
    print(json.dumps({'synthetic_PID':child.pid,'argv':argv}),flush=True)
    term=False;kill=False
    while True:
        pid,status,usage=os.wait4(child.pid,os.WNOHANG)
        if pid:break
        now=time.monotonic();used=sum(f.stat().st_size for f in p.rglob('*') if f.is_file())
        if (now-start>=17 or used>=8300000) and not term:
            reason='OUTPUT_CAP' if used>=8300000 else 'WALL_CAP';os.killpg(child.pid,signal.SIGTERM);term=True
        if now-start>=19 and not kill:os.killpg(child.pid,signal.SIGKILL);kill=True
        time.sleep(.01)
exit_code=os.waitstatus_to_exitcode(status);child.returncode=exit_code
receipt={'status':'SYNTHETIC_BRIDGE_PASS_REVIEW_PENDING' if exit_code==0 and reason is None else 'FAIL_STOP_NO_RETRY','argv':argv,'cwd':str(code_dir),'exit_code':exit_code,'wall_seconds':time.monotonic()-start,'user_seconds':usage.ru_utime,'system_seconds':usage.ru_stime,'peak_RSS_bytes':usage.ru_maxrss*1024,'termination_reason':reason,'synthetic_invocations':1,'synthetic_fake_processes':1 if (p/'raw/fake_process_001/STARTED.json').exists() else 0,'real_helper_launches':0,'physical_RHS_calls':0,'derivative_requests':0,'Rust_builds':0,'requested_model':'gpt-6.1-sol','requested_effort':'high','observed_runtime_model':'NOT_INDEPENDENTLY_OBSERVED'}
(p/'WRAPPER_RECEIPT.json').open('x').write(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt),flush=True)
raise SystemExit(0 if receipt['status'].startswith('SYNTHETIC_BRIDGE_PASS') else 1)
