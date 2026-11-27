"""Run one bounded PHYS84 child under pinned cooperative lease and hard caps."""
from pathlib import Path
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import resource
import subprocess
import sys
import time

UNIT=Path(__file__).resolve().parents[1]
LEASE_SHA='76ff57ba687fd9830b84c3fcff69eb8ed0e9f6ceab4551e61c67c84d3ea65124'


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--label',required=True)
    p.add_argument('--receipt',type=Path,required=True)
    p.add_argument('--kind',choices=('verification','application','resume'),required=True)
    p.add_argument('command',nargs=argparse.REMAINDER)
    a=p.parse_args()
    cmd=a.command[1:] if a.command and a.command[0]=='--' else a.command
    if not cmd: raise ValueError('COMMAND_REQUIRED')
    if a.receipt.exists(): raise FileExistsError('ATTEMPT_RECEIPT_EXISTS')
    src=UNIT.parent/'hh_phys83_ce_completion_20261023/source/vendor/phys78_run_pilot.py'
    if hashlib.sha256(src.read_bytes()).hexdigest()!=LEASE_SHA:raise ValueError('LEASE_SOURCE_PIN_MISMATCH')
    spec=importlib.util.spec_from_file_location('_phys84_inherited_lease_only',src)
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    pool=module.LeasePool('/tmp/rei-bianchi-cooperative-leases',site='local')
    lease,observation=pool.acquire('PHYS84:'+a.label)
    now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
    cpu,wall=(30,60) if a.kind=='verification' else (10,20)
    rec={'schema':'PHYS84_BOUNDED_ATTEMPT_V1','label':a.label,'kind':a.kind,'command':cmd,
         'started_utc':now(),'lease_source_SHA256':LEASE_SHA,'lease':lease,'observation':observation,
         'cpu_limit_s':cpu,'wall_limit_s':wall,'workers':1,'threads':1,'memory_lease_GiB':0.5,
         'old_science_runner_called':False,'old_rate_callbacks':0,'old_population_callbacks':0,
         'old_ODE_callbacks':0,'other_processes_terminated':0,
         'budget':{'inherited_spend':None,'remaining':None,'currency':None}}
    a.receipt.parent.mkdir(parents=True,exist_ok=True)
    start=time.monotonic()
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU,(cpu,cpu))
    if lease is None:
        rec['status']='WAITING_FOR_SHARED_LEASE'
        with a.receipt.open('x') as f:json.dump(rec,f,indent=2)
        print(json.dumps({'status':rec['status']}))
        return 75
    env=os.environ.copy()
    for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS',
                 'VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS'):env[name]='1'
    env['PYTHONDONTWRITEBYTECODE']='1'
    try:
        try:
            result=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=wall,preexec_fn=limits)
            rec.update(exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr,
                       status='COMMAND_COMPLETED' if result.returncode==0 else 'COMMAND_FAILED')
        except subprocess.TimeoutExpired as error:
            rec.update(exit_code=124,stdout=(error.stdout or b'').decode() if isinstance(error.stdout,bytes) else error.stdout or '',
                       stderr=(error.stderr or b'').decode() if isinstance(error.stderr,bytes) else error.stderr or '',status='WALL_LIMIT_EXCEEDED')
        rec.update(completed_utc=now(),wall_seconds=time.monotonic()-start,
                   child_cpu_seconds=resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime+
                                     resource.getrusage(resource.RUSAGE_CHILDREN).ru_stime)
        with a.receipt.open('x') as f:json.dump(rec,f,indent=2);f.write('\n')
        print(rec['stdout'],end='')
        print(rec['stderr'],end='',file=sys.stderr)
        return rec['exit_code']
    finally:
        module.release_lease(lease)


if __name__=='__main__':sys.exit(main())
