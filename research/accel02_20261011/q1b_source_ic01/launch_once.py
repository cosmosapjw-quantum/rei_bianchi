import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import time

root=Path('/tmp/Q1A_C08B_G1_SAVED_MOMENTS01.wfEB0a/repos/rei_bianchi')
unit=root/'research/accel02_20261011/q1b_source_ic01'
evidence=unit/'evidence'
evidence.mkdir(exist_ok=True)
marker=evidence/'STARTED.json'
with marker.open('x') as f: json.dump({'unit':'Q1B_SOURCE_IC01','started_unix_s':time.time()},f)
cmd=['timeout','--signal=KILL','300s','prlimit','--as=2147483648','--cpu=300','--fsize=33554432','/usr/bin/python3','-B','research/accel02_20261011/q1b_source_ic01/check_source_ic.py','--root',str(root),'--output','research/accel02_20261011/q1b_source_ic01/evidence/RESULT.json']
env=dict(os.environ)
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']: env[key]='1'
before=resource.getrusage(resource.RUSAGE_CHILDREN)
start=time.monotonic()
with (evidence/'stdout.txt').open('xb') as out,(evidence/'stderr.txt').open('xb') as err:
    completed=subprocess.run(cmd,cwd=root,env=env,stdout=out,stderr=err)
after=resource.getrusage(resource.RUSAGE_CHILDREN)
files=[p for p in unit.rglob('*') if p.is_file()]
receipt={'unit':'Q1B_SOURCE_IC01','command':cmd,'env':{k:env[k] for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']},'exit':completed.returncode,'wall_s':time.monotonic()-start,'cpu_s':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,'output_bytes':sum(p.stat().st_size for p in evidence.rglob('*') if p.is_file()),'file_sha256':{str(p.relative_to(unit)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'requested_worker':'gpt-6.1-sol medium','observed_runtime_identity':'UNKNOWN_NOT_INDEPENDENTLY_OBSERVED','attempts':1,'native':0,'SIGMA':0,'RHS':0,'JAC':0,'ODE':0,'build':0,'history_replay':0}
with (evidence/'EXECUTION_RECEIPT.json').open('x') as f: json.dump(receipt,f,indent=2)
print(json.dumps(receipt,indent=2))
