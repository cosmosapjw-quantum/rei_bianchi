"""Prepared future pilot wrapper. AUTHORING_ONLY; no authorization implied.

Each case has one exclusive attempt marker, CPU30s/wall120s/3GiB. This module
must not be invoked under the current NO_MORE_IVPs policy.
"""
import argparse
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

UNIT=Path(__file__).resolve().parents[1]
CASES=('OFF_base','ON_base','ON_refined')
CPU_LIMIT=30
WALL_LIMIT=120
MEMORY_LIMIT=3*1024**3


def main():
    own_start=resource.getrusage(resource.RUSAGE_SELF)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',choices=CASES,required=True)
    parser.add_argument('--user-override-receipt',type=Path,required=True)
    args=parser.parse_args()
    # This is an explicit evidence-bearing owner override of NO_MORE_IVPs,
    # not the existing non-IVP budget receipt or a self-issued boolean flag.
    authority=json.loads(args.user_override_receipt.read_text())
    required={'schema':'REI_SOURCE_HISTORY_IVP_OWNER_OVERRIDE_V1',
              'explicit_NO_MORE_IVPs_exception':True,'status':'OWNER_AUTHORIZED'}
    for key,value in required.items():
        if authority.get(key)!=value:raise SystemExit('Missing explicit owner IVP override: '+key)
    if not authority.get('owner_authorization_quote') or args.case not in authority.get('authorized_cases',[]):
        raise SystemExit('Override must quote owner authorization and include the selected fixed case')
    if authority.get('cpu_s_per_case_max',0)<CPU_LIMIT or authority.get('wall_s_per_case_max',0)<WALL_LIMIT:
        raise SystemExit('Owner receipt does not cover the prepared CPU/wall limits')
    if authority.get('workers')!=1 or authority.get('memory_bytes_max',0)<MEMORY_LIMIT:
        raise SystemExit('Owner receipt does not cover single-worker/3GiB limits')
    out=UNIT/'outputs';out.mkdir(exist_ok=True)
    # Any earlier failed fixed case stops this three-case proposal. An explicit
    # new authorization/repair is required; this wrapper never retries it.
    for name in CASES:
        previous=out/(name+'_ATTEMPT_RESULT.json')
        if previous.exists() and json.loads(previous.read_text()).get('status')!='COMPLETED':
            raise SystemExit('Earlier fixed case failed; stop proposal without automatic retry')
    predecessors=CASES[:CASES.index(args.case)]
    for name in predecessors:
        previous=out/(name+'_ATTEMPT_RESULT.json')
        if not previous.exists() or json.loads(previous.read_text()).get('status')!='COMPLETED':
            raise SystemExit('Run fixed predecessors successfully first: '+name)
    command=[sys.executable,str(Path(__file__).with_name('coupled.py')),'--execute-authorized','--case',args.case]
    marker=out/(args.case+'_ATTEMPT_STARTED.json')
    with marker.open('x') as f:
        json.dump({'command':command,'cpu_limit_s':CPU_LIMIT,'wall_limit_s':WALL_LIMIT,
                   'memory_bytes':MEMORY_LIMIT,'workers':1,'automatic_retries':0,
                   'owner_override_receipt':str(args.user_override_receipt.resolve()),
                   'owner_authorization_quote':authority['owner_authorization_quote']},f,indent=2)
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU,(CPU_LIMIT,CPU_LIMIT))
        resource.setrlimit(resource.RLIMIT_AS,(MEMORY_LIMIT,MEMORY_LIMIT))
    env=os.environ.copy()
    for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):env[key]='1'
    before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.monotonic();code=None;status='COMPLETED'
    try:
        result=subprocess.run(command,cwd=UNIT,env=env,text=True,capture_output=True,
                              timeout=WALL_LIMIT,preexec_fn=limits)
        code=result.returncode;stdout=result.stdout;stderr=result.stderr
        if code:status='FAILED'
    except subprocess.TimeoutExpired as exc:
        status='WALL_LIMIT';stdout=exc.stdout or '';stderr=exc.stderr or ''
        if isinstance(stdout,bytes):stdout=stdout.decode(errors='replace')
        if isinstance(stderr,bytes):stderr=stderr.decode(errors='replace')
    except Exception as exc:status='LAUNCH_ERROR';stdout='';stderr=repr(exc)
    after=resource.getrusage(resource.RUSAGE_CHILDREN);own=resource.getrusage(resource.RUSAGE_SELF)
    receipt={'case':args.case,'status':status,'returncode':code,'command':command,
        'child_cpu_s':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
        'wrapper_cpu_s_observed':own.ru_utime+own.ru_stime-own_start.ru_utime-own_start.ru_stime,
        'wall_s':time.monotonic()-start,'cpu_limit_s':CPU_LIMIT,'wall_limit_s':WALL_LIMIT,
        'memory_bytes':MEMORY_LIMIT,'workers':1,'automatic_retries':0,
        'owner_override_receipt':str(args.user_override_receipt.resolve()),
        'unknown_overhead':'UNKNOWN_NOT_ZERO: tool/host, receipt serialization, wrapper before timer',
        'requested_executor_identity':'SOL lower-tier coding agent','observed_runtime_model_identity':'UNKNOWN'}
    (out/(args.case+'_stdout.txt')).write_text(stdout);(out/(args.case+'_stderr.txt')).write_text(stderr)
    (out/(args.case+'_ATTEMPT_RESULT.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
    if status!='COMPLETED':raise SystemExit(1)


if __name__=='__main__':main()
