"""Execute one new bounded task using the preserved shared cooperative lease."""
from pathlib import Path
import argparse, datetime, hashlib, importlib.util, json, os, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
LEASE_SHA = '76ff57ba687fd9830b84c3fcff69eb8ed0e9f6ceab4551e61c67c84d3ea65124'

def main():
    p=argparse.ArgumentParser();p.add_argument('--label',required=True)
    p.add_argument('--receipt',type=Path,required=True)
    p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    cmd=a.command[1:] if a.command and a.command[0]=='--' else a.command
    if not cmd: raise ValueError('COMMAND_REQUIRED')
    if a.receipt.exists(): raise FileExistsError('ATTEMPT_RECEIPT_EXISTS; inspect before retry')
    src=ROOT/'source/vendor/phys78_run_pilot.py'
    if hashlib.sha256(src.read_bytes()).hexdigest()!=LEASE_SHA:raise ValueError('LEASE_SOURCE_PIN_MISMATCH')
    spec=importlib.util.spec_from_file_location('_phys83_inherited_lease',src)
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    pool=m.LeasePool(path='/tmp/rei-bianchi-cooperative-leases',site='local')
    lease,obs=pool.acquire('PHYS83_CONT:'+a.label)
    now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
    rec={'label':a.label,'command':cmd,'started_utc':now(),'observation':obs,
         'lease':lease,'lease_source_SHA256':LEASE_SHA,'old_science_runner_called':False,
         'workers':1,'threads':1,'other_processes_terminated':0}
    a.receipt.parent.mkdir(parents=True,exist_ok=True)
    if lease is None:
        rec['status']='WAITING_FOR_SHARED_LEASE'
        with a.receipt.open('x') as f:json.dump(rec,f,indent=2)
        print(json.dumps({'status':rec['status'],'receipt':str(a.receipt)}));return 75
    env=os.environ.copy()
    for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS'):env[name]='1'
    env['PYTHONDONTWRITEBYTECODE']='1'
    try:
        run=subprocess.run(cmd,text=True,capture_output=True,env=env)
        rec.update(exit_code=run.returncode,stdout=run.stdout,stderr=run.stderr,
            status='COMMAND_COMPLETED' if run.returncode==0 else 'COMMAND_FAILED',completed_utc=now())
        with a.receipt.open('x') as f:json.dump(rec,f,ensure_ascii=False,indent=2);f.write('\n')
        print(run.stdout,end='');print(run.stderr,end='',file=sys.stderr)
        return run.returncode
    finally:m.release_lease(lease)

if __name__=='__main__':sys.exit(main())
