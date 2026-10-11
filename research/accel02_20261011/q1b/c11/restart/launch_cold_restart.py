#!/usr/bin/env python3
"""Launch new isolated Python interpreter; the launcher imports no C10 code."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[4]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--label',required=True);args=ap.parse_args()
    if not args.label.replace('_','').isalnum():raise ValueError('LABEL')
    out=HERE/'evidence'/args.label;out.mkdir(parents=True,exist_ok=False)
    evidence=HERE.parents[1]/'c10/evidence'; checkpoints=evidence/'NATIVE_ENTRY_C2_T1E11_N4_HEAT_CHECKPOINTS'
    expected=evidence/'NATIVE_ENTRY_C2_T1E11_N4_HEAT_BOUNDARY_002.npz'
    request=dict(schema='rei.c11.cold_restart.request.v1',parent_pid=os.getpid(),
        output_directory=str(out),checkpoint_directory=str(checkpoints.relative_to(REPO)),generation=1,
        checkpoint_manifest_sha256=sha(checkpoints/'gen-00000001/manifest.json'),
        next_checkpoint_manifest_sha256=sha(checkpoints/'gen-00000002/manifest.json'),
        expected_next_t_s=5e10,expected_boundary=str(expected.relative_to(REPO)),expected_boundary_sha256=sha(expected),
        harness_identities={str(p.relative_to(REPO)):sha(p) for p in (HERE/'cold_restart.py',Path(__file__),HERE.parent/'CONTRACT.json')})
    rp=out/'REQUEST.json';rp.write_text(json.dumps(request,indent=2)+'\n')
    cmd=[sys.executable,'-I','-B',str(HERE/'cold_restart.py'),'--request',str(rp),'--request-sha256',sha(rp)]
    record=dict(schema='rei.c11.cold_restart.launch.v1',created_utc=datetime.now(timezone.utc).isoformat(),
        parent_pid=os.getpid(),command=cmd,cwd=str(REPO),request_sha256=sha(rp),
        environment_policy='inherited environment; isolated Python (-I) ignores PYTHON* vars/user site; no preloaded solver state',
        launcher_sha256=sha(__file__))
    (out/'LAUNCH.json').write_text(json.dumps(record,indent=2)+'\n')
    start=time.monotonic()
    with (out/'STDOUT.log').open('xb') as stdout,(out/'STDERR.log').open('xb') as stderr:
        child=subprocess.Popen(cmd,cwd=REPO,stdout=stdout,stderr=stderr)
        record['child_pid']=child.pid
        record['exit_code']=child.wait()
    record['elapsed_s']=time.monotonic()-start
    record['stdout_sha256']=sha(out/'STDOUT.log');record['stderr_sha256']=sha(out/'STDERR.log')
    (out/'LAUNCH_COMPLETED.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2),flush=True)
    return record['exit_code']
if __name__=='__main__':raise SystemExit(main())
