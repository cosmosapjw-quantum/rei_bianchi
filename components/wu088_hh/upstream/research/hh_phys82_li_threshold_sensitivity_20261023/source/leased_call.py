"""Run one new bounded command with the byte-pinned PHYS78 cooperative lease."""
from pathlib import Path
import argparse, datetime, hashlib, importlib.util, json, os, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
LEASE_SHA='76ff57ba687fd9830b84c3fcff69eb8ed0e9f6ceab4551e61c67c84d3ea65124'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--label',required=True);ap.add_argument('--receipt',type=Path,required=True);ap.add_argument('command',nargs=argparse.REMAINDER);a=ap.parse_args()
    cmd=a.command[1:] if a.command and a.command[0]=='--' else a.command
    if not cmd:raise ValueError('COMMAND_REQUIRED')
    if a.receipt.exists():raise FileExistsError('COMPLETED_OR_ATTEMPTED_RECEIPT_EXISTS; inspect identity instead of replay')
    p=ROOT/'source/vendor/phys78_run_pilot.py'
    if hashlib.sha256(p.read_bytes()).hexdigest()!=LEASE_SHA:raise ValueError('LEASE_SOURCE_PIN_MISMATCH')
    spec=importlib.util.spec_from_file_location('phys82_inherited_lease',p);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    pool=m.LeasePool(path='/tmp/rei-bianchi-cooperative-leases',site='local');lease,obs=pool.acquire('PHYS82:'+a.label)
    stamp=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
    rec={'label':a.label,'command':cmd,'started_utc':stamp(),'observation':obs,'lease':lease,'lease_source_SHA256':LEASE_SHA,'old_science_runner_called':False,'threads':1,'other_processes_terminated':0}
    a.receipt.parent.mkdir(parents=True,exist_ok=True)
    if lease is None:
        rec['status']='WAITING_FOR_SHARED_LEASE';a.receipt.write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec));return 75
    env=os.environ.copy()
    for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS'):env[name]='1'
    env['PYTHONDONTWRITEBYTECODE']='1'
    try:
        r=subprocess.run(cmd,text=True,capture_output=True,env=env)
        rec.update(exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr,status='COMMAND_COMPLETED' if r.returncode==0 else 'COMMAND_FAILED',completed_utc=stamp())
        a.receipt.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
        print(r.stdout,end='');print(r.stderr,end='',file=sys.stderr)
        return r.returncode
    finally:m.release_lease(lease)

if __name__=='__main__':sys.exit(main())
