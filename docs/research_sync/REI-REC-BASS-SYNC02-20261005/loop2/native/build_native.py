#!/usr/bin/env python3
"""Compile the bounded harness only. Does NOT execute the registered histories."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

parser=argparse.ArgumentParser()
parser.add_argument('--rustc',required=True)
args=parser.parse_args()
root=Path(__file__).resolve().parent
project=root.parent.parent
runtime=root/'runtime'
runtime.mkdir(exist_ok=True)
pb=project/'loop1/peebles_consumer/runtime'
rei=project/'source_rei'
commands=[
 [args.rustc,'--edition=2021','--crate-name','rei_microphysics','--crate-type','rlib',str(rei/'src/lib.rs'),'-o',str(runtime/'librei_microphysics.rlib')],
 [args.rustc,'--edition=2024',str(root/'peebles_bass_history.rs'),'-L',str(pb),'-L',str(runtime),
  '--extern','rei_peebles_reference='+str(pb/'librei_peebles_reference.rlib'),
  '--extern','rei_microphysics='+str(runtime/'librei_microphysics.rlib'),'-o',str(runtime/'peebles_bass_history')],
]
records=[]
for command in commands:
    process=subprocess.run(command,capture_output=True,text=True)
    records.append(dict(command=command,exit_code=process.returncode,stdout=process.stdout,stderr=process.stderr))
    if process.returncode:break
sources=list((rei/'src').glob('*.rs'))+[root/'peebles_bass_history.rs',
    project/'loop1/peebles_consumer/crate/src/lib.rs',
    project/'loop1/bass_clock/bass/_rustcore/src/microphysics/visibility_clock.rs']
sources.extend(project/('loop1/bass_clock/baseline_bass/_rustcore/src/microphysics/'+name)
    for name in ['frame.rs','visibility.rs','rei_visibility.rs'])
result=dict(status='PASS' if all(x['exit_code']==0 for x in records) else 'FAIL',
    commands=records,history_executed=False,identities=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sources])
binary=runtime/'peebles_bass_history'
if result['status']=='PASS':result['binary']=dict(path=str(binary),sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),bytes=binary.stat().st_size)
(root/'BUILD_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
raise SystemExit(0 if result['status']=='PASS' else 1)
