"""One bounded main-ledger saved-array diagnostics and tests attempt."""
import json,os,resource,subprocess,sys,time
from pathlib import Path
UNIT=Path(__file__).resolve().parents[1]

def main():
    start_self=resource.getrusage(resource.RUSAGE_SELF)
    out=UNIT/'outputs';out.mkdir(exist_ok=True)
    command=[sys.executable,str(Path(__file__).with_name('diagnostics.py')),'--test-and-run']
    policy={'command':command,'child_cpu_limit_s':4,'wall_limit_s':30,'reserve_cpu_s':5,
            'ledger':'main','workers':1,'memory_bytes':1024**3,'automatic_retries':0}
    with (out/'DIAGNOSTICS_ATTEMPT_STARTED.json').open('x') as f:json.dump(policy,f,indent=2)
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU,(4,4));resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
    env=os.environ.copy()
    for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):env[key]='1'
    before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.monotonic();code=None;status='COMPLETED';stdout='';stderr=''
    try:
        result=subprocess.run(command,cwd=UNIT,env=env,text=True,capture_output=True,timeout=30,preexec_fn=limits)
        code=result.returncode;stdout=result.stdout;stderr=result.stderr
        if code:status='FAILED'
    except subprocess.TimeoutExpired as exc:
        status='WALL_LIMIT';stdout=exc.stdout or '';stderr=exc.stderr or ''
        if isinstance(stdout,bytes):stdout=stdout.decode(errors='replace')
        if isinstance(stderr,bytes):stderr=stderr.decode(errors='replace')
    except Exception as exc:status='LAUNCH_ERROR';stderr=repr(exc)
    child=resource.getrusage(resource.RUSAGE_CHILDREN);own=resource.getrusage(resource.RUSAGE_SELF)
    receipt=dict(policy,status=status,returncode=code,phase='saved_array_diagnostics_and_tests',
        child_cpu_s=child.ru_utime+child.ru_stime-before.ru_utime-before.ru_stime,
        wrapper_cpu_s_observed=own.ru_utime+own.ru_stime-start_self.ru_utime-start_self.ru_stime,
        wall_s=time.monotonic()-start,requested_executor_identity='lower-tier coding agent',
        observed_runtime_model_identity='UNKNOWN',unknown_overhead='UNKNOWN_NOT_ZERO: intake, authoring, host/tool, pre-timer and receipt serialization')
    (out/'DIAGNOSTICS_stdout.txt').write_text(stdout);(out/'DIAGNOSTICS_stderr.txt').write_text(stderr)
    (out/'DIAGNOSTICS_ATTEMPT_RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
    if status!='COMPLETED':raise SystemExit(1)

if __name__=='__main__':main()
