from pathlib import Path
import hashlib,json,os,resource,signal,subprocess,time
p=Path(__file__).resolve().parent;argv=['/usr/bin/python3',str(p/'code/plot_pr171.py'),'--contract',str(p/'CONTRACT.json'),'--output',str(p/'results')]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',MPLCONFIGDIR=str(p/'raw/matplotlib_config'))
(p/'EXECUTION_FREEZE.json').open('x').write(json.dumps({'argv':argv,'cwd':str(Path.cwd()),'source_HEAD':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'script_sha256':hashlib.sha256((p/'code/plot_pr171.py').read_bytes()).hexdigest(),'contract_sha256':hashlib.sha256((p/'CONTRACT.json').read_bytes()).hexdigest(),'env_overrides':{k:env[k] for k in ('PYTHONDONTWRITEBYTECODE','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','MPLCONFIGDIR')}},indent=2)+'\n')
def limits():
    resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824));resource.setrlimit(resource.RLIMIT_FSIZE,(16777216,16777216))
start=time.monotonic();reason=None;term=False;kill=False
with (p/'raw/stdout').open('xb') as out,(p/'raw/stderr').open('xb') as err:
    child=subprocess.Popen(argv,stdout=out,stderr=err,env=env,preexec_fn=limits,start_new_session=True)
    (p/'raw/STARTED.json').open('x').write(json.dumps({'pid':child.pid,'epoch':time.time(),'argv':argv,'AS_bytes':1073741824,'wall_cap_s':30,'output_cap_bytes':16777216},indent=2)+'\n')
    print(json.dumps({'plot_PID':child.pid,'start_epoch':time.time()}),flush=True)
    while True:
        pid,status,usage=os.wait4(child.pid,os.WNOHANG)
        if pid:break
        now=time.monotonic();used=sum(f.stat().st_size for f in p.rglob('*') if f.is_file())
        if (now-start>=27 or used>=16600000) and not term:
            reason='OUTPUT_CAP' if used>=16600000 else 'WALL_CAP';os.killpg(child.pid,signal.SIGTERM);term=True
        if now-start>=29 and not kill:os.killpg(child.pid,signal.SIGKILL);kill=True
        time.sleep(.02)
exit_code=os.waitstatus_to_exitcode(status);child.returncode=exit_code
rec={'status':'PRESENTATION_COMPLETE' if exit_code==0 and reason is None else 'FAIL_STOP_NO_RETRY','argv':argv,'cwd':str(Path.cwd()),'exit_code':exit_code,'wall_seconds':time.monotonic()-start,'user_seconds':usage.ru_utime,'system_seconds':usage.ru_stime,'peak_RSS_bytes':usage.ru_maxrss*1024,'termination_reason':reason,'plotting_invocations':1,'physical_runs':0,'helper_runs':0,'tests':0,'builds':0,'review_policy':'existing PR171 C9 review reused; no duplicate scientific review requested','requested_model':'gpt-6.1-sol','requested_effort':'high','observed_runtime_model':'NOT_INDEPENDENTLY_OBSERVED'}
(p/'WRAPPER_RECEIPT.json').open('x').write(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec),flush=True)
raise SystemExit(0 if rec['status']=='PRESENTATION_COMPLETE' else 1)
