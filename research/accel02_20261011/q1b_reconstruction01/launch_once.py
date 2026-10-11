"""Mechanical one-attempt launcher and raw execution receipt."""
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import time

ROOT=Path('/tmp/Q1A_C08B_G1_SAVED_MOMENTS01.wfEB0a/repos/rei_bianchi')
UNIT=ROOT/'research/accel02_20261011/q1b_reconstruction01'
OUT=UNIT/'evidence/attempt1'
OUT.mkdir(parents=True,exist_ok=False)
command=['env','OPENBLAS_NUM_THREADS=1','OMP_NUM_THREADS=1','MKL_NUM_THREADS=1','NUMEXPR_NUM_THREADS=1',
 'timeout','--signal=KILL','180s','prlimit','--as=2147483648','--cpu=180','--fsize=33554432',
 '/usr/bin/python3','-B','research/accel02_20261011/q1b_reconstruction01/validate_reconstruction.py',
 '--root',str(ROOT),'--output','research/accel02_20261011/q1b_reconstruction01/evidence/attempt1/RESULT.json']
with (OUT/'STARTED.json').open('x') as f:
    json.dump({'unit':'Q1B_RECONSTRUCTION01','attempt':1,'command':command,'cwd':str(ROOT),
      'unix_time':time.time(),'requested_worker':'gpt-6.1-sol medium','observed_runtime_identity':'UNKNOWN_NOT_INFERRED_FROM_REQUEST'},f,indent=2)
before=resource.getrusage(resource.RUSAGE_CHILDREN);started=time.monotonic()
with (OUT/'stdout.txt').open('x') as stdout,(OUT/'stderr.txt').open('x') as stderr:
    run=subprocess.run(command,cwd=ROOT,stdout=stdout,stderr=stderr)
after=resource.getrusage(resource.RUSAGE_CHILDREN)
result=OUT/'RESULT.json'
if not result.exists():
    with result.open('x') as f:json.dump({'outcome':'HOLD_EXECUTION_RESOURCE_OR_CAP','exit':run.returncode,'first_failure_preserved':True},f,indent=2)
size=sum(p.stat().st_size for p in UNIT.rglob('*') if p.is_file())
receipt={'unit':'Q1B_RECONSTRUCTION01','attempt':1,'exit':run.returncode,'command':command,'cwd':str(ROOT),
  'wall_s':time.monotonic()-started,'cpu_s':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
  'output_bytes':size,'output_cap_pass':size<=67108864,
  'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file()},
  'retry':0,'publication':False,'root_checkout_mutated':False}
with (OUT/'EXECUTION_RECEIPT.json').open('x') as f:json.dump(receipt,f,indent=2)
print(json.dumps(receipt,indent=2))
