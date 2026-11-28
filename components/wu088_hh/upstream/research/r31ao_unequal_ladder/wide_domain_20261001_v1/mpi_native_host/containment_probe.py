"""Required supported-host synthetic setsid-grandchild containment check; no MPI."""
import argparse
import json
import os
from pathlib import Path
import sys
from cgroup_guard import JobCgroup, Refusal, execute_contained

PROBE_CODE='''import json,os,subprocess,sys
p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'],start_new_session=True)
print(json.dumps({'leader':os.getpid(),'grandchild':p.pid,'detached_session':os.getsid(p.pid)}),flush=True)
'''


def probe(parent,output,cpus):
    if os.getuid()==0 or os.geteuid()==0: raise Refusal('nonroot probe required; no bypass')
    output=Path(output); output.mkdir(mode=0o700)
    group=JobCgroup(parent,memory_bytes=128*1024**2,ranks=1,pids=32)
    try:
        result=execute_contained([str(Path(sys.executable).resolve()),'-I','-c',PROBE_CODE],
            group=group,output=output,seconds=3,cpus=cpus[:1],
            env={'PATH':'/usr/bin:/bin','LC_ALL':'C'},file_cap=4096)
        process=json.loads((output/'stdout.log').read_text())
        if (result['status']!='SURVIVING_JOB_DESCENDANTS' or not result['cleanup_populated_zero']
                or process['grandchild']!=process['detached_session'] or process['leader']==process['grandchild']):
            raise Refusal('detached-session containment probe failed')
        result.update(status='SYNTHETIC_DETACHED_SESSION_CONTAINMENT_VERIFIED',process=process,
            MPI_executed=False,actual_HH_runs=0,scientific_admission=False)
        (output/'PROBE.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
        return result
    finally:
        group.kill_and_empty(); group.close()


def main():
    p=argparse.ArgumentParser();p.add_argument('--cgroup-parent',required=True);p.add_argument('--output',required=True)
    a=p.parse_args()
    try: result=probe(a.cgroup_parent,a.output,sorted(os.sched_getaffinity(0))); code=0
    except (ValueError,OSError) as exc: result={'status':'BLOCKED','reason':str(exc),'MPI_executed':False,'actual_HH_runs':0};code=2
    print(json.dumps(result,indent=2));return code


if __name__=='__main__':raise SystemExit(main())
