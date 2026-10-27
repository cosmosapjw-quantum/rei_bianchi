"""Root GO + frozen hash review required; exactly one bounded attempt."""
import time
WALL_START=time.perf_counter()
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys

HERE=Path(__file__).resolve().parent
UNIT=HERE.parent
OUT=HERE/'attempt01'
CHILD_CAP=.75
WRAPPER_CAP=.10
TAIL_RESERVE=.05
RESERVE=.90
CEILING=14.9
MEMORY=512*1024*1024
child=None
stop_reason=None


def stop(sig,frame):
    global stop_reason
    stop_reason='WRAPPER_CPU_LIMIT' if sig==signal.SIGPROF else 'WALL_LIMIT'
    if child is not None and child.poll() is None: child.kill()
    raise RuntimeError(stop_reason)


def limits():
    resource.setrlimit(resource.RLIMIT_AS,(MEMORY,MEMORY))
    resource.setrlimit(resource.RLIMIT_CPU,(1,1))


def main():
    global child,stop_reason
    # No output mutation before concrete root authorization and identity checks.
    go=json.loads((HERE/'EXECUTION_GO.json').read_text())
    manifest_path=HERE/'PREEXEC_MANIFEST.json'
    manifest_raw=manifest_path.read_bytes()
    if go.get('authorization')!='ROOT_C5_REVIEW_GO': raise ValueError('root C5 GO required')
    if go.get('manifest_sha256')!=hashlib.sha256(manifest_raw).hexdigest(): raise ValueError('GO manifest identity')
    prior=go['prior_planning_known_CPU_s']
    if isinstance(prior,bool) or not isinstance(prior,(int,float)) or prior<13.297430367: raise ValueError('preserve cumulative planning')
    if go.get('authorized_reserve_CPU_s')!=RESERVE or prior+RESERVE>CEILING: raise ValueError('cumulative reserve exceeds ceiling')
    for entry in json.loads(manifest_raw)['inputs']:
        p=UNIT/entry['path']; raw=p.read_bytes()
        if len(raw)!=entry['bytes'] or hashlib.sha256(raw).hexdigest()!=entry['sha256']: raise ValueError('frozen input changed: '+entry['path'])
    if OUT.exists(): raise FileExistsError('attempt01 preserved; no automatic retry')
    OUT.mkdir()
    command=[sys.executable,'-B',str(HERE/'check_integrated_return.py')]
    start={'status':'STARTED_PENDING_REVIEW','command':command,'prior_planning_known_CPU_s':prior,
        'limits':{'child_CPU_s':CHILD_CAP,'wrapper_CPU_s':WRAPPER_CAP,'tail_reserve_s':TAIL_RESERVE,
            'combined_reserve_s':RESERVE,'wall_s':8,'memory_MiB':512,'workers':1},
        'manifest_sha256':hashlib.sha256(manifest_raw).hexdigest(),'scientific_admission':'PENDING'}
    (OUT/'START_RECEIPT.json').write_text(json.dumps(start,indent=2)+'\n')
    before=resource.getrusage(resource.RUSAGE_CHILDREN)
    code=None; failure=None; status=None
    signal.signal(signal.SIGPROF,stop); signal.signal(signal.SIGALRM,stop)
    try:
        left=WRAPPER_CAP-time.process_time()
        if left<=0: raise RuntimeError('wrapper startup CPU limit')
        signal.setitimer(signal.ITIMER_PROF,left)
        remaining=7.8-(time.perf_counter()-WALL_START)
        if remaining<=0: raise RuntimeError('wrapper startup wall limit')
        signal.setitimer(signal.ITIMER_REAL,remaining)
        env=os.environ.copy()
        for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','GOTO_NUM_THREADS'): env[key]='1'
        env.update(PYTHONHASHSEED='0',PYTHONDONTWRITEBYTECODE='1')
        with (OUT/'stdout.json').open('wb') as out,(OUT/'stderr.log').open('wb') as err:
            child=subprocess.Popen(command,cwd=HERE,env=env,stdout=out,stderr=err,preexec_fn=limits)
            code=child.wait()
        if code<0: stop_reason='CHILD_SIGNAL_'+str(-code)
        if code==0: status=json.loads((OUT/'stdout.json').read_text()).get('status')
    except BaseException as exc:
        failure={'type':type(exc).__name__,'message':str(exc)}
        if child is not None:
            if child.poll() is None: child.kill()
            code=child.wait()
    finally:
        signal.setitimer(signal.ITIMER_PROF,0); signal.setitimer(signal.ITIMER_REAL,0)
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    child_cpu=(after.ru_utime-before.ru_utime)+(after.ru_stime-before.ru_stime)
    wrapper_cpu=time.process_time(); elapsed=time.perf_counter()-WALL_START
    charged=child_cpu+wrapper_cpu+TAIL_RESERVE
    within=(child_cpu<=CHILD_CAP and wrapper_cpu<=WRAPPER_CAP and charged<=RESERVE and elapsed<=8 and prior+charged<=CEILING)
    passed=code==0 and status=='PASS_PENDING_INDEPENDENT_REVIEW' and failure is None and stop_reason is None and within
    receipt={**start,'status':'COMPLETED_PENDING_INDEPENDENT_REVIEW' if passed else 'FAILED_STOP_NO_AUTOMATIC_RETRY',
        'exit_code':code,'failure':failure,'stop_reason':stop_reason,'stdout_status':status,
        'child_CPU_s':child_cpu,'wrapper_CPU_before_tail_s':wrapper_cpu,'tail_reserved_CPU_s':TAIL_RESERVE,
        'charged_new_CPU_s':charged,'planning_known_plus_tail_CPU_s':prior+charged,
        'wall_s':elapsed,'child_max_RSS_KiB':after.ru_maxrss,'within_limits':within,
        'temporary_ceiling_CPU_s':CEILING,'restore_policy_ceiling_CPU_s':10,
        'unknown_historical_startup_remote_LLM':'UNKNOWN_NOT_ZERO',
        'requested_executor':'lower-tier mechanical executor','requested_executor_model':'gpt-6.1-sol',
        'requested_reasoning':'high','spawn_override_accepted':True,
        'observed_executor':'/root/bounded_executor; runtime model not independently attested',
        'main_campaign':'595.225063/600; NO_MORE_IVPs unchanged','physical_update_applied':False}
    (OUT/'RESOURCE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2),flush=True)
    return 0 if passed else 1

if __name__=='__main__': raise SystemExit(main())
