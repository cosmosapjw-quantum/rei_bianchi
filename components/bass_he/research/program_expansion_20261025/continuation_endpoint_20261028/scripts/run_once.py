"""Exclusive one-shot launcher. Limits cover runner plus waited process group."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

UNIT=Path(__file__).resolve().parents[1]

def write(path,obj):
    tmp=path.with_suffix('.json.tmp')
    with tmp.open('w') as f:
        json.dump(obj,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    tmp.replace(path)

def namespace_record(path):
    fields={}
    for line in path.read_text().splitlines():
        key,_,value=line.partition(':')
        if key in ('Pid','PPid','NSpid','NSpgid'):
            fields[key]=[int(v) for v in value.split()]
    return fields

def write_monitor_identity(path):
    """Single-threaded preexec handshake, after the child's new session starts."""
    raw=Path('/proc/self/stat').read_text()
    fields=raw[raw.rfind(')')+2:].split()
    identity={'child_local_pid':os.getpid(),'child_local_pgrp':os.getpgrp(),
              'child_host_pid':int(raw.split()[0]),'child_host_pgrp':int(fields[2]),
              'child_namespace':namespace_record(Path('/proc/self/status')),
              'identity_method':'child preexec /proc/self handshake after setsid'}
    write(path,identity)

def resolve_host_group(local_child_pid,identity_path):
    """Read the executed child's own handshake, never index /proc by local PID."""
    identity=json.loads(identity_path.read_text())
    if not (identity['child_local_pid']==local_child_pid and
            identity['child_local_pgrp']==local_child_pid and
            identity['child_host_pid']==identity['child_host_pgrp'] and
            identity['child_namespace']['NSpid'][-1]==local_child_pid):
        raise RuntimeError('monitor namespace handshake does not identify the new-session child')
    identity.update({'parent_local_pid':os.getpid(),
                     'parent_host_pid':int(Path('/proc/self/stat').read_text().split()[0]),
                     'parent_namespace':namespace_record(Path('/proc/self/status'))})
    return identity

def group_cpu(host_pgid):
    ticks=os.sysconf('SC_CLK_TCK');total=0
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():continue
        try:
            raw=(entry/'stat').read_text();fields=raw[raw.rfind(')')+2:].split()
            if int(fields[2])==host_pgid:
                total+=sum(int(fields[i]) for i in (11,12,13,14))/ticks
        except (OSError,ValueError,IndexError):pass
    return total

def main():
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['validation','plot'],required=True);p.add_argument('--saved',required=True,type=Path);p.add_argument('--official',type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--cpu-limit',type=int);p.add_argument('--wall-limit',type=int);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    cpu_cap,wall_cap=(120,300) if a.mode=='validation' else (10,30)
    cpu_limit=a.cpu_limit if a.cpu_limit is not None else cpu_cap
    wall_limit=a.wall_limit if a.wall_limit is not None else wall_cap
    if not (0<cpu_limit<=cpu_cap and 0<wall_limit<=wall_cap):
        raise ValueError('limit overrides must be positive and no larger than original mode caps')
    os.environ.update({k:'1' for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS']})
    resource.setrlimit(resource.RLIMIT_AS,(768*1024**2,768*1024**2))
    resource.setrlimit(resource.RLIMIT_CPU,(cpu_limit,cpu_limit))
    cmd=[sys.executable,str(UNIT/'scripts'/('campaign.py' if a.mode=='validation' else 'plot_saved.py')),'--saved',str(a.saved.resolve()),'--output',str(a.output.resolve())]
    if a.mode=='validation':
        if a.official is None:raise ValueError('--official required for validation')
        cmd+=['--official',str(a.official.resolve())]
    started=time.monotonic();children0=resource.getrusage(resource.RUSAGE_CHILDREN)
    start_record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':cmd,'mode':a.mode,'CPU_seconds':cpu_limit,'wall_seconds':wall_limit,'AS_bytes':768*1024**2,'threads':1,'inputs':{'saved':str(a.saved.resolve()),'saved_sha256':hashlib.sha256(a.saved.read_bytes()).hexdigest(),'official':str(a.official.resolve()) if a.official else None},'source_files_sha256':{str(f.relative_to(UNIT)):hashlib.sha256(f.read_bytes()).hexdigest() for folder in ('src','tests','scripts') for f in (UNIT/folder).glob('*.py')}}
    write(a.output/'START.json',start_record)
    reason=None;peak=0;namespace=None
    with (a.output/'stdout.log').open('w') as out,(a.output/'stderr.log').open('w') as err:
        identity_path=a.output/'MONITOR_IDENTITY.json'
        child=subprocess.Popen(cmd,stdout=out,stderr=err,start_new_session=True,preexec_fn=lambda:write_monitor_identity(identity_path))
        try:
            namespace=resolve_host_group(child.pid,identity_path)
            start_record['monitor_namespace']=namespace
            write(a.output/'START.json',start_record)
        except Exception as exc:
            reason='explicit monitor error: '+str(exc)
            os.killpg(child.pid,signal.SIGKILL)
        while reason is None and child.poll() is None:
            own=resource.getrusage(resource.RUSAGE_SELF);used=own.ru_utime+own.ru_stime+group_cpu(namespace['child_host_pgrp']);peak=max(peak,used)
            if used>=cpu_limit or time.monotonic()-started>=wall_limit:
                reason='whole process group CPU cap' if used>=cpu_limit else 'whole process group wall cap'
                os.killpg(child.pid,signal.SIGKILL);break
            time.sleep(.05)
        code=child.wait()
    s=resource.getrusage(resource.RUSAGE_SELF);r=resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu=s.ru_utime+s.ru_stime+r.ru_utime+r.ru_stime-children0.ru_utime-children0.ru_stime
    elapsed=time.monotonic()-started
    passed=code==0 and reason is None and cpu<=cpu_limit and elapsed<=wall_limit
    write(a.output/'RESOURCE_RESULT.json',{'status':'PASS' if passed else 'FAIL','exit_code':code,'termination_reason':reason,'monitor_namespace':namespace,'whole_runner_waited_children_CPU_seconds':cpu,'wall_seconds':elapsed,'max_child_rss_KiB':r.ru_maxrss,'max_observed_group_plus_runner_CPU_seconds':peak,'limits':{'CPU_seconds':cpu_limit,'wall_seconds':wall_limit,'AS_bytes':768*1024**2,'threads':1},'rerun_count':0})
    return 0 if passed else 1

if __name__=='__main__':sys.exit(main())
