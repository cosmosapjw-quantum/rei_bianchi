"""One authorized pilot postprocess attempt; never runs a physical IVP."""
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

UNIT=Path(__file__).resolve().parents[1]


def main():
    own_start=resource.getrusage(resource.RUSAGE_SELF)
    out=UNIT/'outputs';out.mkdir(exist_ok=True)
    command=[sys.executable,str(Path(__file__).with_name('postprocess_cases.py'))]
    with (out/'PILOT_POSTPROCESS_ATTEMPT_STARTED.json').open('x') as f:
        json.dump({'command':command,'child_cpu_limit_s':3,'wall_limit_s':30,
                   'reserve_cpu_s':3.5,'ledger':'presentation','workers':1,
                   'memory_bytes':3*1024**3,'automatic_retries':0},f,indent=2)
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU,(3,3));resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,3*1024**3))
    env=os.environ.copy()
    for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):env[key]='1'
    before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.monotonic();code=None;status='COMPLETED'
    try:
        result=subprocess.run(command,cwd=UNIT,env=env,text=True,capture_output=True,timeout=30,preexec_fn=limits)
        code=result.returncode;stdout=result.stdout;stderr=result.stderr
        if code:status='FAILED'
    except subprocess.TimeoutExpired as exc:
        status='WALL_LIMIT';stdout=exc.stdout or '';stderr=exc.stderr or ''
        if isinstance(stdout,bytes):stdout=stdout.decode(errors='replace')
        if isinstance(stderr,bytes):stderr=stderr.decode(errors='replace')
    except Exception as exc:status='LAUNCH_ERROR';stdout='';stderr=repr(exc)
    child=resource.getrusage(resource.RUSAGE_CHILDREN);own=resource.getrusage(resource.RUSAGE_SELF)
    receipt={'phase':'pilot_postprocess','status':status,'returncode':code,'command':command,
             'child_cpu_s':child.ru_utime+child.ru_stime-before.ru_utime-before.ru_stime,
             'wrapper_cpu_s_observed':own.ru_utime+own.ru_stime-own_start.ru_utime-own_start.ru_stime,
             'wall_s':time.monotonic()-start,'child_cpu_limit_s':3,'wall_limit_s':30,
             'reserve_cpu_s':3.5,'ledger':'presentation','workers':1,'memory_bytes':3*1024**3,
             'automatic_retries':0,'requested_executor_identity':'SOL lower-tier coding agent',
             'observed_runtime_model_identity':'UNKNOWN',
             'unknown_overhead':'UNKNOWN_NOT_ZERO: intake, authoring, tool/host, wrapper before timer and receipt serialization'}
    (out/'PILOT_POSTPROCESS_stdout.txt').write_text(stdout);(out/'PILOT_POSTPROCESS_stderr.txt').write_text(stderr)
    (out/'PILOT_POSTPROCESS_ATTEMPT_RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
    if status!='COMPLETED':raise SystemExit(1)


if __name__=='__main__':main()
