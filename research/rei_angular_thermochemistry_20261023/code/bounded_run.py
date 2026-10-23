"""Resource-accounted child supervisor. No scientific library imports here."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import resource
import signal
import subprocess
import sys
import time

BASE=Path(__file__).resolve().parents[1]
RESULTS=BASE/'results'


def limits(cpu_limit):
    resource.setrlimit(resource.RLIMIT_CPU,(cpu_limit,cpu_limit))
    resource.setrlimit(resource.RLIMIT_AS,(int(1.5*1024**3),int(1.5*1024**3)))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--prepare-only',action='store_true')
    parser.add_argument('--batch',type=int,choices=[1,2,3,4,5])
    args=parser.parse_args()
    RESULTS.mkdir(exist_ok=True)
    if args.prepare_only:
        manifest=json.loads((BASE/'inputs/COPY_MANIFEST.json').read_text())
        for e in manifest['copies']:
            assert hashlib.sha256((BASE/e['destination']).read_bytes()).hexdigest()==e['sha256']
        print(json.dumps({'status':'PREPARED','verified_copies':len(manifest['copies']),'IVPs':0}))
        return
    if args.batch is None:
        parser.error('choose --prepare-only or one --batch')
    ledger=RESULTS/'execution_budget.json'
    history=json.loads(ledger.read_text()) if ledger.exists() else {'batches':[],'cpu_limit_s':300,'wall_limit_s':420,'maximum_IVPs':11}
    if any(x['batch']==args.batch for x in history['batches']):
        raise RuntimeError('BATCH_ALREADY_ATTEMPTED; resume only explicitly unexecuted cases with owner authorization')
    history['preflight_conservative_charge']={'CPU_s':20,'wall_s':30,'basis':'enforced original check-process caps; body time not substituted for whole child'}
    history['manual_raw_inspection_charge']={'CPU_s':1,'wall_s':2,'basis':'conservative charge for one thread1 saved-array inspection after oracle assertion; observed command wall0.243908s, no IVP'}
    cpu=21+sum(x['child_cpu_s'] for x in history['batches'])+sum(x['whole_child_cpu_s'] for x in history.get('postprocessing',[]))
    wall=32+sum(x['child_wall_s'] for x in history['batches'])+sum(x['whole_child_wall_s'] for x in history.get('postprocessing',[]))
    if cpu>=300 or wall>=420:
        raise RuntimeError('CUMULATIVE_BUDGET_EXHAUSTED')
    groups={1:['--checks','--cases','1','2','3'],
            2:['--repair-regression','--resume-case1','--cases','1','2','3','4','5','6','7'],
            3:['--finalize-oracle-saved','--cases','5','6','7','8','9'],
            4:['--finalize-oracle-saved','--cases','5','6','7','8','9'],
            5:['--cases','10']}
    command=[sys.executable,str(BASE/'code/run_cases.py')]+groups[args.batch]
    env=os.environ.copy()
    for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:
        env[k]='1'
    started=time.perf_counter()
    before=resource.getrusage(resource.RUSAGE_CHILDREN)
    with (RESULTS/f'batch{args.batch}_stdout.log').open('w') as out,(RESULTS/f'batch{args.batch}_stderr.log').open('w') as err:
        proc=subprocess.Popen(command,env=env,cwd=BASE,stdout=out,stderr=err,
                              preexec_fn=lambda:limits(min(120,max(1,int(300-cpu)))),start_new_session=True)
        try:
            code=proc.wait(timeout=min(180,420-wall))
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid,signal.SIGTERM)
            code=proc.wait(timeout=5)
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    record={'batch':args.batch,'command':command,'returncode':code,'child_wall_s':time.perf_counter()-started,
            'child_cpu_s':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
            'child_maxrss_kib':after.ru_maxrss,'cpu_before_s':cpu,'wall_before_s':wall,
            'address_space_limit_bytes':int(1.5*1024**3),'per_invocation_cpu_limit_s':120,'per_invocation_wall_limit_s':180}
    history['batches'].append(record)
    history['cumulative_child_cpu_s']=cpu+record['child_cpu_s']
    history['cumulative_child_wall_s']=wall+record['child_wall_s']
    ledger.write_text(json.dumps(history,indent=2)+'\n')
    print(json.dumps(record,indent=2))
    sys.exit(0 if code==0 else 1)


if __name__=='__main__':
    main()
