"""One immutable bounded PHYS07 run with pre/post source identity and raw logs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('run_id')
p.add_argument('script')
p.add_argument('--wall', type=int, default=30)
p.add_argument('--memory-mib', type=int, default=256)
p.add_argument('--output-mib', type=int, default=8)
p.add_argument('--bind', action='append', default=[])
p.add_argument('--script-args', nargs=argparse.REMAINDER, default=[])
a = p.parse_args()
if not a.run_id.replace('_','').isalnum():
    raise ValueError('simple immutable run id')
if not (0 < a.wall <= 45 and 0 < a.memory_mib <= 384 and 0 < a.output_mib <= 16):
    raise ValueError('contract ceiling')
script = (ROOT/a.script).resolve()
if ROOT not in script.parents or not script.is_file():
    raise ValueError('script outside package or absent')
bound = [script, Path(__file__).resolve()] + [(ROOT/s).resolve() for s in a.bind]
bound = list(dict.fromkeys(bound))

def identities():
    rows=[]
    for f in bound:
        d=f.read_bytes()
        rows.append({'path':os.path.relpath(f,ROOT),'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()})
    return rows

before=identities()
dest=ROOT/'evidence'/a.run_id
dest.mkdir(parents=True,exist_ok=False)
started=datetime.now(timezone.utc).isoformat()
start=time.monotonic()

def limits():
    resource.setrlimit(resource.RLIMIT_AS,(a.memory_mib*1024**2,)*2)
    resource.setrlimit(resource.RLIMIT_FSIZE,(a.output_mib*1024**2,)*2)
    resource.setrlimit(resource.RLIMIT_CPU,(a.wall,)*2)

command=[sys.executable,str(script)]+a.script_args
timeout=False
with (dest/'stdout.txt').open('wb') as out,(dest/'stderr.txt').open('wb') as err:
    try:
        proc=subprocess.run(command,cwd=ROOT,stdout=out,stderr=err,timeout=a.wall,
                            preexec_fn=limits,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        code=proc.returncode
    except subprocess.TimeoutExpired:
        code,timeout=124,True
elapsed=time.monotonic()-start
after=identities()
usage=resource.getrusage(resource.RUSAGE_CHILDREN)
record={'schema':'WU088_HH_PHYS07_BOUNDED_EXECUTION_V1','run_id':a.run_id,
        'command':command,'cwd':str(ROOT),'started_utc':started,
        'finished_utc':datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds':elapsed,'exit_code':code,'timeout':timeout,
        'limits':{'wall_seconds':a.wall,'address_space_MiB':a.memory_mib,'log_file_MiB_each':a.output_mib},
        'ru_maxrss_KiB_linux':usage.ru_maxrss,'child_user_seconds':usage.ru_utime,
        'child_system_seconds':usage.ru_stime,'python_version':sys.version,
        'source_and_input_before':before,'source_and_input_after':after,
        'bound_files_unchanged':before==after,
        'logs':{f.name:{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
                for f in sorted(dest.iterdir())},
        'execution_scope':'New Python reference only; no native endpoint/point/root/IVP or historical suite route.'}
(dest/'EXECUTION.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
sys.exit(code if code else (0 if before==after else 97))
