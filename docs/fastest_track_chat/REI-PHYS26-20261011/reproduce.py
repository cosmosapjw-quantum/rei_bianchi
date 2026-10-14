#!/usr/bin/env python3
"""Verify a PHYS26 payload and optionally replay only its new bounded program.

Verification does not execute any science. The explicit replay executes one
PHYS26 main exactly once; old PHYS19--25 programs are never imported or run.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
PROGRAM = 'contributions/numerics/fixed_variance_envelope.py'
ORIGINAL = 'contributions/numerics/FIXED_VARIANCE_ENVELOPE_FIRST.json'

def identity(path):
    data=path.read_bytes()
    return {'sha256':sha256(data).hexdigest(),'bytes':len(data)}

def verify():
    manifest=json.loads((ROOT/'MANIFEST.json').read_text())
    failures=[]
    entries=manifest['files']
    for rel,expected in entries.items():
        path=ROOT/rel
        if not path.is_file() or path.is_symlink():
            failures.append({'path':rel,'reason':'missing, nonregular or symlink'})
            continue
        actual=identity(path)
        if actual!=expected:
            failures.append({'path':rel,'expected':expected,'actual':actual})
    observed={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()}
    extra=sorted(observed-set(entries)-{'MANIFEST.json'})
    if extra: failures.append({'extra_files':extra})
    return {'status':'PASS' if not failures else 'FAIL','files_checked':len(entries),
            'manifest':identity(ROOT/'MANIFEST.json'),'failures':failures,
            'scientific_main_invocations':0}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-only',action='store_true')
    parser.add_argument('--replay-new-scope',action='store_true')
    parser.add_argument('--output-dir',type=Path)
    args=parser.parse_args()
    if args.verify_only and args.replay_new_scope:
        parser.error('Choose one mode')
    result=verify()
    if result['status']!='PASS' or not args.replay_new_scope:
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0 if result['status']=='PASS' else 1
    if args.output_dir is None: parser.error('--replay-new-scope requires --output-dir')
    out=args.output_dir.resolve()
    if out==ROOT or ROOT in out.parents:
        parser.error('Replay output must be outside the immutable input bundle')
    out.mkdir(parents=True,exist_ok=False)
    target=out/'FIXED_VARIANCE_ENVELOPE_REPLAY.json'
    command=[sys.executable,'-B',str(ROOT/PROGRAM),'--output',str(target)]
    started=datetime.now(timezone.utc).isoformat()
    before=time.monotonic()
    process=subprocess.run(command,cwd=ROOT,capture_output=True,check=False)
    elapsed=time.monotonic()-before
    (out/'stdout.log').write_bytes(process.stdout)
    (out/'stderr.log').write_bytes(process.stderr)
    same_bytes=False; same_json=False
    if target.is_file():
        same_bytes=target.read_bytes()==(ROOT/ORIGINAL).read_bytes()
        same_json=json.loads(target.read_text())==json.loads((ROOT/ORIGINAL).read_text())
    receipt={'task':'REI-PHYS26-20261011','kind':'portability replay, not independent physics validation',
             'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),
             'elapsed_seconds':elapsed,'python':platform.python_version(),
             'input_verification':result,'program':{'path':PROGRAM,**identity(ROOT/PROGRAM)},
             'original':{'path':ORIGINAL,**identity(ROOT/ORIGINAL)},'command':command,
             'exit_code':process.returncode,'raw_bytes_equal':same_bytes,'full_json_equal':same_json,
             'comparison_excluded_fields':[],
             'output':identity(target) if target.is_file() else None,
             'stdout':identity(out/'stdout.log'),'stderr':identity(out/'stderr.log'),
             'new_science_main_invocations':1,'old_science_main_invocations':0,
             'native_runs':0,'gas_IVP_runs':0,'independent_physics_credit':0,
             'status':'PASS' if process.returncode==0 and same_bytes and same_json else 'FAIL'}
    (out/'REPLAY_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(receipt,ensure_ascii=False,indent=2))
    return 0 if receipt['status']=='PASS' else 1

if __name__=='__main__':
    raise SystemExit(main())
