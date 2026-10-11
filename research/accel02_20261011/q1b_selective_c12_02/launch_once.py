"""Mechanical one-shot bounded launch receipt; no scientific decision."""
import hashlib,json,os,resource,subprocess,time
from pathlib import Path
ROOT=Path('/tmp/Q1A_C08B_G1_SAVED_MOMENTS01.wfEB0a/repos/rei_bianchi')
UNIT=ROOT/'research/accel02_20261011/q1b_selective_c12_02'
EV=UNIT/'evidence/attempt1'
EV.mkdir(parents=True,exist_ok=False)
cmd=['env','OPENBLAS_NUM_THREADS=1','OMP_NUM_THREADS=1','MKL_NUM_THREADS=1','NUMEXPR_NUM_THREADS=1','timeout','--signal=KILL','180s','prlimit','--as=2147483648','--cpu=180','--fsize=33554432','/usr/bin/python3','-B','research/accel02_20261011/q1b_selective_c12_02/validate_selective.py','--root',str(ROOT),'--output','research/accel02_20261011/q1b_selective_c12_02/evidence/attempt1/RESULT.json']
with (EV/'STARTED.json').open('x') as f:json.dump({'unit':'Q1B_SELECTIVE_C12_02','attempt':1,'command':cmd,'cwd':str(ROOT),'unix_time':time.time()},f,indent=2)
start=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN)
with (EV/'stdout.txt').open('xb') as out,(EV/'stderr.txt').open('xb') as err:
    run=subprocess.run(cmd,cwd=ROOT,stdout=out,stderr=err)
after=resource.getrusage(resource.RUSAGE_CHILDREN);wall=time.monotonic()-start
files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in EV.iterdir() if p.is_file()}
size=sum(p.stat().st_size for p in UNIT.rglob('*') if p.is_file())
receipt={'unit':'Q1B_SELECTIVE_C12_02','attempt':1,'command':cmd,'cwd':str(ROOT),'exit':run.returncode,'wall_s':wall,'cpu_s':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,'output_bytes':size,'output_cap_pass':size<=67108864,'sha256':files,'retry':0,'publication':False,'root_checkout_mutated':False,'prior_attempt_costs':'retained in RESULT; never reset'}
with (EV/'EXECUTION_RECEIPT.json').open('x') as f:json.dump(receipt,f,indent=2)
print(json.dumps(receipt,indent=2))

