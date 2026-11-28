#!/usr/bin/env python3
"""Preserve pre-run identity, stdout/stderr, limits and actual process accounting."""
import argparse
import datetime
import hashlib
import json
import pathlib
import resource
import subprocess
import sys
import time

root = pathlib.Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--attempt', required=True)
a = p.parse_args()
ev = root / 'evidence' / a.attempt
ev.mkdir(exist_ok=False)
output = root / 'results' / a.attempt
assert not output.exists()
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
identity = {str(f.relative_to(root)): sha(f) for f in [root/'src/phys14_advance.py',root/'src/run_bounded.py',root/'SCIENTIFIC_CONTRACT.md',root/'VALIDATION_MATRIX.md',root/'inputs/INPUT_MANIFEST.json']}
limits = {'wall_seconds':90,'cpu_seconds':90,'address_space_bytes':768*1024**2,'file_size_bytes':32*1024**2}
start = datetime.datetime.now(datetime.timezone.utc).isoformat()
(ev/'PRE_RUN.json').write_text(json.dumps({'started_utc':start,'identity':identity,'limits':limits,'command':['python3','src/phys14_advance.py','--output-dir',str(output)]},indent=2)+'\n')
def preexec():
    resource.setrlimit(resource.RLIMIT_CPU,(90,90))
    resource.setrlimit(resource.RLIMIT_AS,(768*1024**2,768*1024**2))
    resource.setrlimit(resource.RLIMIT_FSIZE,(32*1024**2,32*1024**2))
before=resource.getrusage(resource.RUSAGE_CHILDREN)
clock=time.monotonic()
timed_out=False
with (ev/'stdout.log').open('w') as so, (ev/'stderr.log').open('w') as se:
    try:
        proc=subprocess.run([sys.executable,str(root/'src/phys14_advance.py'),'--output-dir',str(output)],cwd=root,stdout=so,stderr=se,timeout=90,preexec_fn=preexec)
        code=proc.returncode
    except subprocess.TimeoutExpired:
        code=-999
        timed_out=True
after=resource.getrusage(resource.RUSAGE_CHILDREN)
result={'attempt':a.attempt,'started_utc':start,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'exit_code':code,'timed_out':timed_out,'wall_seconds':time.monotonic()-clock,
        'user_cpu_seconds':after.ru_utime-before.ru_utime,'system_cpu_seconds':after.ru_stime-before.ru_stime,
        'max_rss_KiB':after.ru_maxrss,'limits':limits,
        'source_identity_after':{k:sha(root/k) for k in identity},
        'source_unchanged':all(sha(root/k)==v for k,v in identity.items()),
        'outputs':{str(f.relative_to(root)):{'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(output.rglob('*')) if f.is_file()} if output.exists() else {}}
(ev/'RUN_RECORD.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
if code:
    print((ev/'stderr.log').read_text())
else:
    print((output/'SUMMARY.json').read_text())
sys.exit(0 if code==0 else 1)
