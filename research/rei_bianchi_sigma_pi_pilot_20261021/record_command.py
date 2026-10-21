#!/usr/bin/env python3
"""Run a command once and preserve argv, actual stdout/stderr, exit and environment."""
import argparse,json,os,platform,subprocess,sys,time
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--receipt-dir',type=Path,required=True);ap.add_argument('command',nargs=argparse.REMAINDER);a=ap.parse_args()
    cmd=a.command[1:] if a.command and a.command[0]=='--' else a.command
    if not cmd:ap.error('command required')
    a.receipt_dir.mkdir(parents=True,exist_ok=False)
    env={k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')}
    for k in env:os.environ[k]='1'
    import numpy,scipy
    receipt={'argv':cmd,'cwd':str(Path.cwd()),'start_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'python':sys.version,'platform':platform.platform(),'numpy':numpy.__version__,'scipy':scipy.__version__,'thread_env_before':env,'child_thread_env':{k:'1' for k in env}}
    start=time.monotonic()
    with (a.receipt_dir/'stdout.log').open('x') as out,(a.receipt_dir/'stderr.log').open('x') as err:
        p=subprocess.run(cmd,stdout=out,stderr=err)
    receipt.update({'exit_status':p.returncode,'elapsed_wall_s':time.monotonic()-start,'end_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
    (a.receipt_dir/'command.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2));sys.exit(p.returncode)
if __name__=='__main__':main()
