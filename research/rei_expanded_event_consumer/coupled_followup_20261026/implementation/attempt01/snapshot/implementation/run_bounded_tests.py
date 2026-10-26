"""One root-authorized stdlib child; retains raw output and measured debit."""
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent; UNIT=HERE.parent


def write(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    wrapper_start=time.monotonic()
    authorization=HERE/'RUN_AUTHORIZATION.json'
    auth=json.loads(authorization.read_text())
    if auth.get('authorized') is not True:
        raise SystemExit('ROOT_AUTHORIZATION_REQUIRED')
    if auth['limits']!={'CPU_soft_s':.05,'wall_s':2.,'memory_bytes':134217728,'workers':1}:
        raise SystemExit('FROZEN_LIMITS_MISMATCH')
    if 10.-auth['campaign_prior_planning_CPU_s'] < .1:
        raise SystemExit('INSUFFICIENT_CUMULATIVE_BUDGET_FOR_FROZEN_ATTEMPT')
    attempt=HERE/'attempt01';attempt.mkdir(exist_ok=False)
    bindings=auth['sha256_bindings']
    for relative,expected in bindings.items():
        path=UNIT/relative
        if sha(path)!=expected:raise SystemExit('INPUT_BYTE_IDENTITY_MISMATCH: '+relative)
        destination=attempt/'snapshot'/relative;destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(path.read_bytes())
    (attempt/'RUN_AUTHORIZATION.json').write_bytes(authorization.read_bytes())
    env=os.environ.copy();env['FOLLOWUP_OUTPUT_DIR']=str(attempt)
    env['PYTHONDONTWRITEBYTECODE']='1'
    for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        env[key]='1'
    def caps():
        os.setsid();resource.setrlimit(resource.RLIMIT_CPU,(1,1))
        resource.setrlimit(resource.RLIMIT_AS,(134217728,134217728))
        signal.signal(signal.SIGPROF,signal.SIG_DFL);signal.setitimer(signal.ITIMER_PROF,.05)
    command=[sys.executable,str(HERE/'test_combined.py')]
    start=time.monotonic();timed_out=False
    with (attempt/'stdout.log').open('wb') as out,(attempt/'stderr.log').open('wb') as err:
        child=subprocess.Popen(command,cwd=HERE,env=env,stdout=out,stderr=err,preexec_fn=caps)
        while True:
            pid,status,usage=os.wait4(child.pid,os.WNOHANG)
            if pid:break
            if time.monotonic()-start>=2.:
                timed_out=True;os.killpg(child.pid,signal.SIGKILL)
                pid,status,usage=os.wait4(child.pid,0);break
            time.sleep(.002)
        exit_code=os.waitstatus_to_exitcode(status);child.returncode=exit_code
    wall=time.monotonic()-start
    outputs={str(f.relative_to(attempt)):sha(f) for f in attempt.rglob('*') if f.is_file()}
    receipt={'attempt':1,'command':command,'exit_code':exit_code,'timed_out':timed_out,
      'whole_child_CPU_s':usage.ru_utime+usage.ru_stime,'whole_child_wall_s':wall,
      'wait4_rusage':{k:getattr(usage,k) for k in dir(usage) if k.startswith('ru_')},
      'CPU_soft_s':.05,'hard_RLIMIT_CPU_s':1,'wall_cap_s':2.,'memory_bytes':134217728,
      'workers':1,'BLAS_threads':1,'scientific_imports_in_child':True,
      'authorization_sha256':sha(authorization),'input_sha256':bindings,
      'post_run_input_sha256':{r:sha(UNIT/r) for r in bindings},'output_sha256':outputs,
      'campaign_prior_planning_CPU_s':auth['campaign_prior_planning_CPU_s'],
      'campaign_CPU_cap_s':10.,'budget_reset':False,'automatic_retry':False,
      'new_IVPs':0,'old_source_quadrature_replays':0,'Git_writes':0,
      'requested_executor':'gpt-6.1-sol/high','observed_runtime_model':'UNEXPOSED'}
    receipt['wrapper_CPU_s_separate']=time.process_time()
    receipt['final_receipt_write_print_tail_CPU']='UNKNOWN_NOT_ZERO'
    receipt['conservative_final_tail_CPU_debit_s']=.01
    receipt['wrapper_wall_s_excluding_child']=time.monotonic()-wrapper_start-wall
    receipt['new_child_plus_wrapper_CPU_s']=receipt['whole_child_CPU_s']+receipt['wrapper_CPU_s_separate']
    receipt['new_execution_planning_CPU_debit_s']=receipt['new_child_plus_wrapper_CPU_s']+.01
    receipt['new_execution_total_within_010CPU']=receipt['new_execution_planning_CPU_debit_s']<=.1
    receipt['wrapper_CPU_within_004CPU_estimate']=receipt['wrapper_CPU_s_separate']<=.04
    write(attempt/'RECEIPT.json',receipt)
    print(json.dumps(receipt,indent=2))
    return 0 if exit_code==0 and receipt['new_execution_total_within_010CPU'] else 1


if __name__=='__main__':raise SystemExit(main())
