#!/usr/bin/env python3
"""Record exactly one authorized PHYS30 cached-algebra first execution."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,platform,subprocess,sys,time,stat
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'contributions/numerics'
def utc():return datetime.now(timezone.utc).isoformat()
def sha(b):return hashlib.sha256(b).hexdigest()
def rec(p):
    b=p.read_bytes();return {'path':p.relative_to(ROOT).as_posix(),'bytes':len(b),'sha256':sha(b)}
def write(p,d):
    with p.open('x') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
freeze_path=OUT/'PREEXECUTION_FROZEN.json'
freeze=json.loads(freeze_path.read_bytes())
assert freeze['task']=='REI-PHYS30-20261011' and freeze['owner_actual_read_gate']=='READY_FOR_ONE_FIRST_MAIN'
assert freeze['file_count']==len(freeze['files'])
for row in freeze['files']:
    p=ROOT/row['path'];r=rec(p)
    assert r['bytes']==row['bytes'] and r['sha256']==row['sha256']
    assert format(stat.S_IMODE(p.stat().st_mode),'04o')==row['mode']
raw=OUT/'PROFILE_SECOND_ORDER_FIRST.json'
started=OUT/'EXECUTION_STARTED.json'
receipt=OUT/'EXECUTION.json'
assert not any(p.exists() for p in [raw,started,receipt,OUT/'FIRST_STDOUT.txt',OUT/'FIRST_STDERR.txt'])
argv=[sys.executable,'-B',str(ROOT/freeze['entrypoint']),'--output',str(raw)]
start=utc(); t=time.perf_counter()
write(started,{'task':freeze['task'],'status':'ONE_FIRST_MAIN_STARTED','started_utc':start,'command':argv,'cwd':str(ROOT),'freeze':rec(freeze_path),'timeout_seconds':30,'planned_scientific_mains':1,'retries_permitted':0})
timed_out=False
try:
    process=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=30,check=False)
    stdout=process.stdout;stderr=process.stderr;code=process.returncode
except subprocess.TimeoutExpired as e:
    timed_out=True;stdout=e.stdout or b'';stderr=e.stderr or b'';code=None
wall=time.perf_counter()-t;end=utc()
with (OUT/'FIRST_STDOUT.txt').open('xb') as f:f.write(stdout)
with (OUT/'FIRST_STDERR.txt').open('xb') as f:f.write(stderr)
after=[]
for row in freeze['files']:
    p=ROOT/row['path'];r=rec(p)
    after.append({'path':row['path'],'sha256_size_equal':r['bytes']==row['bytes'] and r['sha256']==row['sha256'],'mode_equal':format(stat.S_IMODE(p.stat().st_mode),'04o')==row['mode']})
result={'task':freeze['task'],'kind':'ONE_FIRST_CACHED_ALGEBRA_MAIN','actual_command':argv,'cwd':str(ROOT),'started_utc':start,'ended_utc':end,'wall_seconds':wall,'timeout_seconds':30,'timed_out':timed_out,'exit_code':code,'python':{'executable':sys.executable,'version':sys.version,'platform':platform.platform()},'freeze':rec(freeze_path),'stdout':rec(OUT/'FIRST_STDOUT.txt'),'stderr':rec(OUT/'FIRST_STDERR.txt'),'raw':rec(raw) if raw.exists() else None,'post_execution_frozen_identity':after,'all_frozen_files_unchanged':all(r['sha256_size_equal'] and r['mode_equal'] for r in after),'actual_main_invocations':1,'new_physical_kernel_or_derivative_evaluations':0,'new_physical_root_searches':0,'old_program_invocations':0,'retries':0,'counter_basis':'Main invocation observed by this controller. Physical/old-program zero ceiling additionally requires static source review and actual raw counters; this receipt does not replace either.'}
write(receipt,result)
print(json.dumps({k:v for k,v in result.items() if k not in ['post_execution_frozen_identity','python']},ensure_ascii=False))
if code!=0 or timed_out or not result['all_frozen_files_unchanged']:sys.exit(1)
