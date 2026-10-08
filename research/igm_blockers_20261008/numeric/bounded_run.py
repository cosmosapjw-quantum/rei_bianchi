#!/usr/bin/env python3
"""One CPU, per-command900 CPU/1200wall, append-only local numeric receipts."""
import json,os,resource,subprocess,sys,time
from pathlib import Path
root=Path(__file__).resolve().parent
name=sys.argv[1];cmd=sys.argv[2:];start=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN)
existing=[]
for p in (root/'receipts').glob('*.json') if (root/'receipts').exists() else []:existing.append(json.loads(p.read_text()))
if sum(x['wall_s'] for x in existing)>=7200:raise SystemExit('AGGREGATE_WALL_LIMIT')
(root/'receipts').mkdir(exist_ok=True)
if (root/'receipts'/f'{name}.json').exists():raise SystemExit('DO_NOT_RESET_RECEIPT')
def limits():
 os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_CPU,(900,900));resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
with (root/f'{name}.log').open('wb') as f:
 p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,preexec_fn=limits,env={**os.environ,'CARGO_BUILD_JOBS':'1'})
 try:exitcode=p.wait(timeout=1200)
 except subprocess.TimeoutExpired:p.kill();p.wait();exitcode=-9
usage=resource.getrusage(resource.RUSAGE_CHILDREN);receipt={'command':cmd,'exit':exitcode,'cpu_s':usage.ru_utime+usage.ru_stime-before.ru_utime-before.ru_stime,'wall_s':time.monotonic()-start,'one_cpu':True,'CPU_cap_s':900,'wall_cap_s':1200,'additional_provider_counts':'IN_CHILD_RECEIPT','historical_costs':'UNCHANGED_EXTERNAL_RAW_EVIDENCE'}
(root/'receipts'/f'{name}.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));sys.exit(exitcode)
