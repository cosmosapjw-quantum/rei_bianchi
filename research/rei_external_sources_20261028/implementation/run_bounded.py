"""One attempt per authorized bounded phase; root closes cumulative accounting."""
import argparse
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

UNIT=Path(__file__).resolve().parents[1]
LIMITS={'tests':(4,20,4.5,'planning'),'evaluation':(3,20,3.5,'planning'),'plots':(3,30,3.5,'presentation')}


def main():
    start_self=resource.getrusage(resource.RUSAGE_SELF);parser=argparse.ArgumentParser()
    parser.add_argument('phase',choices=LIMITS);args=parser.parse_args()
    cpu,wall,reserve,ledger=LIMITS[args.phase];out=UNIT/'outputs';out.mkdir(exist_ok=True)
    command={'tests':[sys.executable,'-m','unittest','discover','-s',str(Path(__file__).parent),'-p','test_model.py','-v'],
             'evaluation':[sys.executable,str(Path(__file__).with_name('evaluate.py'))],
             'plots':[sys.executable,str(Path(__file__).with_name('plot.py'))]}[args.phase]
    marker=out/(args.phase.upper()+'_ATTEMPT_STARTED.json')
    with marker.open('x') as f:json.dump({'command':command,'cpu_limit_s':cpu,'wall_limit_s':wall,'reserve_cpu_s':reserve,'ledger':ledger,'address_space_limit_bytes':3*1024**3,'workers':1,'automatic_retries':0},f,indent=2)
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU,(cpu,cpu));resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,3*1024**3))
    env=os.environ.copy()
    for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):env[key]='1'
    before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.monotonic()
    status='COMPLETED';code=None
    try:
        result=subprocess.run(command,cwd=UNIT,env=env,text=True,capture_output=True,timeout=wall,preexec_fn=limits)
        code=result.returncode;stdout=result.stdout;stderr=result.stderr
        if code:status='FAILED'
    except subprocess.TimeoutExpired as exc:
        status='WALL_LIMIT';stdout=exc.stdout or '';stderr=exc.stderr or ''
        if isinstance(stdout,bytes):stdout=stdout.decode(errors='replace')
        if isinstance(stderr,bytes):stderr=stderr.decode(errors='replace')
    except Exception as exc:status='LAUNCH_ERROR';stdout='';stderr=repr(exc)
    after=resource.getrusage(resource.RUSAGE_CHILDREN);own=resource.getrusage(resource.RUSAGE_SELF)
    receipt={'phase':args.phase,'status':status,'returncode':code,'command':command,'python_executable':sys.executable,
             'child_cpu_s':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
             'wrapper_cpu_s_observed':own.ru_utime+own.ru_stime-start_self.ru_utime-start_self.ru_stime,
             'wall_s':time.monotonic()-start,'cpu_limit_s':cpu,'wall_limit_s':wall,'reserve_cpu_s':reserve,'ledger':ledger,
             'address_space_limit_bytes':3*1024**3,'workers':1,'automatic_retries':0,
             'requested_executor_identity':'SOL lower-tier coding agent','observed_runtime_model_identity':'UNKNOWN',
             'unknown_overhead':'UNKNOWN_NOT_ZERO: tool/host, intake, authoring, wrapper before start and receipt serialization'}
    (out/(args.phase.upper()+'_stdout.txt')).write_text(stdout);(out/(args.phase.upper()+'_stderr.txt')).write_text(stderr)
    (out/(args.phase.upper()+'_ATTEMPT_RESULT.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
    if status!='COMPLETED':raise SystemExit(1)


if __name__=='__main__':main()
