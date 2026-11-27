#!/usr/bin/env python3
"""R14 one-shot process envelope. Frozen identities are checked before execution."""
import argparse, datetime, decimal, hashlib, json, os, pathlib, platform, resource, subprocess, sys, time

p=argparse.ArgumentParser()
p.add_argument('lane',choices=['primary','reference'])
p.add_argument('--source-commit',required=True)
a=p.parse_args()
root=pathlib.Path(__file__).resolve().parents[1]
raw=root/'raw';raw.mkdir(exist_ok=True)
manifest=json.loads((root/'verification/FROZEN_FILES.json').read_text())
for item in manifest['files']:
    b=(root/item['path']).read_bytes()
    if len(b)!=item['bytes'] or hashlib.sha256(b).hexdigest()!=item['sha256']:
        raise RuntimeError('Frozen input mismatch: '+item['path'])
name=a.lane.upper()
attempt=raw/(name+'_ATTEMPT.json')
output=raw/(name+'_RESULTS.json')
if output.exists():
    raise RuntimeError('Preserve existing scientific output; no implicit rerun')
if a.lane=='reference':
    source=raw/'PRIMARY_RESULTS.json'
    if not source.is_file():
        raise RuntimeError('Reference requires actual saved primary output')
    dependent={'path':str(source.relative_to(root)),'bytes':source.stat().st_size,
               'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
else:
    dependent=None
cmd=[sys.executable,str(root/'verification'/('run_'+a.lane+'.py')),
     '--root',str(root),'--output',str(output)]
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
with attempt.open('x') as f:
    json.dump({'lane':a.lane,'attempt':1,'source_commit':a.source_commit,'command':cmd,
               'started_utc':start,'CPU_limit_s':90,'wall_limit_s':120,
               'memory_limit_bytes':1073741824,'saved_primary_identity':dependent},f,indent=2)

def limits():
    resource.setrlimit(resource.RLIMIT_CPU,(90,90))
    resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824))

env=dict(os.environ);env['PYTHONDONTWRITEBYTECODE']='1'
before=resource.getrusage(resource.RUSAGE_CHILDREN)
t=time.monotonic();timeout=False
proc=subprocess.Popen(cmd,cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,preexec_fn=limits)
try:
    out,err=proc.communicate(timeout=120)
except subprocess.TimeoutExpired:
    timeout=True;proc.kill();out,err=proc.communicate()
wall=time.monotonic()-t
after=resource.getrusage(resource.RUSAGE_CHILDREN)
(raw/(name+'_STDOUT.txt')).write_bytes(out)
(raw/(name+'_STDERR.txt')).write_bytes(err)
user=decimal.Decimal(str(after.ru_utime))-decimal.Decimal(str(before.ru_utime))
system=decimal.Decimal(str(after.ru_stime))-decimal.Decimal(str(before.ru_stime))
result={'schema':'WU_R14_ACTUAL_PROCESS_V1','lane':a.lane,'source_commit':a.source_commit,
        'started_utc':start,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'command':cmd,'attempt':1,'returncode':proc.returncode,'timeout':timeout,
        'OS_user_CPU_s':str(user),'OS_system_CPU_s':str(system),'OS_CPU_s':str(user+system),
        'wall_s':wall,'max_rss_KiB':after.ru_maxrss,'includes_imports_and_serialization':True,
        'CPU_limit_s':90,'wall_limit_s':120,'memory_limit_bytes':1073741824,
        'python':sys.version,'platform':platform.platform(),'old_science_replay':0,'new_ODE_runs':0,
        'saved_primary_identity':dependent}
(raw/(name+'_PROCESS.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result))
sys.exit(0 if proc.returncode==0 and not timeout else 1)
