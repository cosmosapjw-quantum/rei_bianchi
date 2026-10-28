"""Bounded command runner with cumulative new-unit costs; preserves failures."""
import argparse
import datetime
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parent
LIMITS = {'science': {'cpu_s':30.0,'wall_s':120.0,'memory_MiB':512},
          'infrastructure': {'cpu_s':60.0,'wall_s':180.0,'memory_MiB':1024}}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--kind',choices=LIMITS,required=True)
    parser.add_argument('--name',required=True)
    parser.add_argument('command',nargs=argparse.REMAINDER)
    args=parser.parse_args()
    cmd=args.command[1:] if args.command and args.command[0]=='--' else args.command
    if not cmd: raise SystemExit('command required')
    receipt_path=ROOT/'RESOURCE_RECEIPT.json'
    record=json.loads(receipt_path.read_text()) if receipt_path.exists() else {
        'unit':'REI-GRID044-ENDPOINT-BINDING-01','limits':LIMITS,'executions':[],
        'legacy_budget_reset':False,'legacy_budget_transfer':False,
        'inspection_remote_and_wrapper_overhead':'not measured; not reported as zero',
        'execution_identity':'inherited completed normalization_review agent reused under documented routing exception',
        'requested_lower_tier':'gpt-6.1-sol; spawn rejected: agent thread limit reached',
        'scientific_admission':'pending independent review'}
    previous=[e for e in record['executions'] if e['kind']==args.kind]
    cpu_left=LIMITS[args.kind]['cpu_s']-sum(e['cpu_s'] for e in previous)
    wall_left=LIMITS[args.kind]['wall_s']-sum(e['wall_s'] for e in previous)
    if cpu_left<=0 or wall_left<=0: raise SystemExit('CUMULATIVE_BUDGET_EXHAUSTED')
    folder=ROOT/'execution'/args.name
    folder.mkdir(parents=True,exist_ok=False)
    env=os.environ.copy()
    env.update({'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1',
                'NUMEXPR_NUM_THREADS':'1','MPLBACKEND':'Agg','PYTHONDONTWRITEBYTECODE':'1',
                'MPLCONFIGDIR':str(ROOT/'execution/matplotlib_config')})
    def cap():
        resource.setrlimit(resource.RLIMIT_CPU,(max(1,math.ceil(cpu_left)),max(1,math.ceil(cpu_left))))
        size=LIMITS[args.kind]['memory_MiB']*1024**2
        resource.setrlimit(resource.RLIMIT_AS,(size,size))
    before=resource.getrusage(resource.RUSAGE_CHILDREN)
    started=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
    timed_out=False
    with (folder/'stdout.log').open('wb') as out,(folder/'stderr.log').open('wb') as err:
        child=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=out,stderr=err,preexec_fn=cap,start_new_session=True)
        try:code=child.wait(timeout=wall_left)
        except subprocess.TimeoutExpired:
            timed_out=True;os.killpg(child.pid,signal.SIGKILL);code=child.wait()
    elapsed=time.monotonic()-started
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime
    item={'name':args.name,'kind':args.kind,'utc_start':utc,'command':cmd,
          'exit_code':code,'timed_out':timed_out,'cpu_s':cpu,'wall_s':elapsed,
          'max_rss_KiB':after.ru_maxrss,'stdout':str((folder/'stdout.log').relative_to(ROOT)),
          'stderr':str((folder/'stderr.log').relative_to(ROOT))}
    record['executions'].append(item)
    record['cumulative']={kind:{'cpu_s':sum(e['cpu_s'] for e in record['executions'] if e['kind']==kind),
                               'wall_s':sum(e['wall_s'] for e in record['executions'] if e['kind']==kind)} for kind in LIMITS}
    receipt_path.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(item,indent=2))
    print((folder/'stdout.log').read_text())
    if code:print((folder/'stderr.log').read_text())
    if cpu>cpu_left or elapsed>wall_left:raise SystemExit('OBSERVED_CUMULATIVE_LIMIT_EXCEEDED')
    raise SystemExit(code)

if __name__=='__main__':main()
