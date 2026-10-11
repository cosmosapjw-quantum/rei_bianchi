#!/usr/bin/env python3
"""No physics imports; launch isolated changed-C11 worker, create-only evidence."""
import argparse,hashlib,json,os,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[4]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--label',required=True);ap.add_argument('--pilot',default='PILOT02');args=ap.parse_args()
    if not all(x.replace('_','').isalnum() for x in (args.label,args.pilot)):raise ValueError('COLD_LABEL')
    out=HERE/'evidence'/args.label;out.mkdir(parents=True,exist_ok=False)
    pilot=HERE.parent/'integration/evidence'/args.pilot
    paths=[HERE/'cold_adaptive_restart.py',Path(__file__),HERE/'cold_restart.py']
    request=dict(schema='rei.c11.cold_adaptive_request.v1',parent_pid=os.getpid(),output_directory=str(out),
        pilot=str(pilot.relative_to(REPO)),generation=1,
        manifest_sha256=sha(pilot/'CHECKPOINTS/gen-00000001/manifest.json'),
        next_manifest_sha256=sha(pilot/'CHECKPOINTS/gen-00000002/manifest.json'),
        harness_identities={str(p.relative_to(REPO)):sha(p) for p in paths})
    rp=out/'REQUEST.json';rp.write_text(json.dumps(request,indent=2)+'\n')
    cmd=[sys.executable,'-I','-B',str(HERE/'cold_adaptive_restart.py'),'--request',str(rp),'--request-sha256',sha(rp)]
    record=dict(schema='rei.c11.cold_adaptive_launch.v1',parent_pid=os.getpid(),command=cmd,
        created_utc=datetime.now(timezone.utc).isoformat(),cwd=str(REPO),request_sha256=sha(rp))
    (out/'LAUNCH.json').write_text(json.dumps(record,indent=2)+'\n');start=time.monotonic()
    with (out/'STDOUT.log').open('xb') as stdout,(out/'STDERR.log').open('xb') as stderr:
        child=subprocess.Popen(cmd,cwd=REPO,stdout=stdout,stderr=stderr)
        record['child_pid']=child.pid;record['exit_code']=child.wait()
    record.update(elapsed_s=time.monotonic()-start,stdout_sha256=sha(out/'STDOUT.log'),stderr_sha256=sha(out/'STDERR.log'))
    (out/'LAUNCH_COMPLETED.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2),flush=True)
    return record['exit_code']
if __name__=='__main__':raise SystemExit(main())
