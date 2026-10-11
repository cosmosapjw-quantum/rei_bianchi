"""Create-only launcher for the single Astra-approved caller validation."""
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import time

unit=Path(__file__).resolve().parent;root=unit.parents[2];out=unit/'evidence/attempt1'
out.mkdir(parents=True,exist_ok=False)
def save(name,obj):
    with (out/name).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False)
command=['env','OPENBLAS_NUM_THREADS=1','OMP_NUM_THREADS=1','MKL_NUM_THREADS=1','NUMEXPR_NUM_THREADS=1',
         'timeout','--signal=KILL','180s','prlimit','--as=2147483648','--cpu=180','--fsize=33554432',
         '/usr/bin/python3','-B',str(unit/'validate_binding.py'),'--root',str(root),'--output',str(out/'RESULT.json')]
source_sha={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in unit.iterdir() if p.is_file()}
save('STARTED.json',{'command':command,'cwd':str(root),'source_sha256':source_sha,'started_unix_s':time.time(),
                     'executor':'controller_direct_owner_authorized','prior_native_processes':3,'prior_SIGMA':26,'prior_energies':98448})
cpu0=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.monotonic()
with (out/'stdout.txt').open('x') as stdout,(out/'stderr.txt').open('x') as stderr:
    proc=subprocess.run(command,cwd=root,stdout=stdout,stderr=stderr)
cpu1=resource.getrusage(resource.RUSAGE_CHILDREN)
receipt={'exit':proc.returncode,'wall_s':time.monotonic()-start,
         'child_CPU_s':cpu1.ru_utime+cpu1.ru_stime-cpu0.ru_utime-cpu0.ru_stime,
         'limits':'CPU/address/file per process; separate child CPU measurement; no aggregate limit claim',
         'files':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in out.iterdir() if p.is_file()},
         'unmeasured_overhead':'UNKNOWN_NOT_ZERO'}
receipt['output_bytes']=sum(v['bytes'] for v in receipt['files'].values())
receipt['output_cap_pass']=receipt['output_bytes']<=67108864
save('EXECUTION_RECEIPT.json',receipt)
print(json.dumps(receipt,indent=2))
raise SystemExit(proc.returncode)
