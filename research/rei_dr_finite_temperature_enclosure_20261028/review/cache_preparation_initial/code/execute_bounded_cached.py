"""Prepared Linux outer OS supervisor. Never retries; explicit dispatch required.

Commands from unit root, only after root's explicit execution authorization:
 python -B -S code/execute_bounded_cached.py numerical --execute-authorized
 python -B -S code/execute_bounded_cached.py presentation --execute-authorized
Targets are bounded job-family accounting targets, not strict whole-host bounds.
"""
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import signal
import sys
import time

ROOT=Path(__file__).resolve().parents[1]


def identity(p):
    r=p.read_bytes()
    return {'path':str(p.relative_to(ROOT)),'bytes':len(r),'sha256':hashlib.sha256(r).hexdigest()}


def session_ticks(session_id):
    """Sum live family own+waited-child ticks, avoiding live-child double counting.

    Linux cutime/cstime count reaped children. A child still visible during the
    non-atomic scan may overlap its just-updated parent counter; overcount is
    conservative. The final wait4 measurement is the authoritative job cost.
    """
    total=0;processes=[]
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():continue
        try:
            fields=(entry/'stat').read_text().split(') ',1)[1].split()
            if int(fields[3])!=session_id:continue
            ticks=sum(int(fields[i]) for i in (11,12,13,14))
            total+=ticks;processes.append(int(entry.name))
        except (FileNotFoundError,ProcessLookupError,PermissionError,ValueError,IndexError):
            continue
    return total,processes



def proc_identity(path='/proc/self/stat'):
    raw=Path(path).read_text(); head,tail=raw.rsplit(') ',1); fields=tail.split()
    return {'host_pid':int(head.split(' (',1)[0]),'host_sid':int(fields[3]),
            'start_ticks':int(fields[19]),'namespace_pid':os.getpid()}


def send_identity(fd):
    info=proc_identity()
    os.write(fd,(json.dumps(info)+'\n').encode());os.close(fd)


def receive_identity(fd,namespace_pid,expected_host_sid=None):
    import select
    ready,_,_=select.select([fd],[],[],2)
    if not ready:
        os.close(fd);return None,'identity_handshake_timeout'
    raw=os.read(fd,4096);os.close(fd)
    try:
        info=json.loads(raw)
        if info['namespace_pid']!=namespace_pid or info['host_pid']<=0 or info['start_ticks']<=0:
            raise ValueError('invalid child identity')
        if expected_host_sid is not None and info['host_sid']!=expected_host_sid:
            raise ValueError('unexpected host session')
        return info,None
    except (ValueError,KeyError,TypeError):
        return None,'identity_handshake_invalid'


def matched_stat(info):
    try:
        raw=Path(f"/proc/{info['host_pid']}/stat").read_text()
    except FileNotFoundError:
        return None
    head,tail=raw.rsplit(') ',1);fields=tail.split()
    if (int(head.split(' (',1)[0])!=info['host_pid'] or int(fields[3])!=info['host_sid']
            or int(fields[19])!=info['start_ticks']):
        raise ValueError('host PID/session/start-time identity mismatch')
    return fields


def main():
    if len(sys.argv)!=3 or sys.argv[1] not in ('numerical','presentation') or sys.argv[2]!='--execute-authorized':
        raise SystemExit('Prepared supervisor: explicit root dispatch required')
    job=sys.argv[1]
    target,threshold,wall,memory=(.2,.16,12,268435456) if job=='numerical' else (1.5,1.4,15,805306368)
    inner=ROOT/('execution/attempt_03' if job=='numerical' else 'figures/attempt_01')
    if inner.exists():raise SystemExit('Existing inner attempt; no replay permitted')
    output=ROOT/'execution'/('outer_'+job+('_03' if job=='numerical' else '_01'));output.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((ROOT/'CACHED_IDENTITIES.json').read_text())
    for row in manifest['files']:
        actual=identity(ROOT/row['path'])
        if actual['sha256']!=row['sha256']:raise SystemExit('Frozen source mismatch: '+row['path'])
    sources=[identity(ROOT/row['path']) for row in manifest['files']]
    if not any(x['path']=='code/execute_bounded_cached.py' for x in sources):
        sources.append(identity(Path(__file__).resolve()))
    script='code/run_once_cached.py' if job=='numerical' else 'code/plot_saved_cached.py'
    argv=[sys.executable,'-B','-S',script,'--execute-authorized']
    envlimits={'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
    (output/'SOURCE_IDENTITIES_BEFORE.json').write_text(json.dumps(sources,indent=2)+'\n')
    read_fd,write_fd=os.pipe()
    prefix=time.process_time();start=time.perf_counter();pid=os.fork()
    if pid==0:
        os.close(read_fd)
        os.setsid()
        send_identity(write_fd)
        os.chdir(ROOT);os.environ.update(envlimits)
        # Integer-second process backstop; aggregate fractional target is watched below.
        resource.setrlimit(resource.RLIMIT_CPU,(1 if job=='numerical' else 2,)*2)
        resource.setrlimit(resource.RLIMIT_AS,(memory,memory))
        for fd,name in [(1,'STDOUT.txt'),(2,'STDERR.txt')]:
            f=os.open(output/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            os.dup2(f,fd);os.close(f)
        os.execv(argv[0],argv)
    os.close(write_fd)
    host_identity,reason=receive_identity(read_fd,pid)
    if host_identity is not None and host_identity['host_sid']!=host_identity['host_pid']:
        reason='unexpected_session_leader_identity'
    ticks_per_s=os.sysconf('SC_CLK_TCK');maximum_ticks=0;last_members=[]
    while True:
        waited,status,usage=os.wait4(pid,os.WNOHANG)
        if waited:break
        ticks=0
        if reason is None:
            try:
                matched_stat(host_identity)
                ticks,last_members=session_ticks(host_identity['host_sid'])
                maximum_ticks=max(maximum_ticks,ticks)
            except ValueError:
                reason='host_identity_mismatch'
        if reason is not None or ticks/ticks_per_s>=threshold or time.perf_counter()-start>=wall:
            reason=reason or ('aggregate_CPU_watchdog' if ticks/ticks_per_s>=threshold else 'wall_watchdog')
            try:os.killpg(pid,signal.SIGKILL)
            except ProcessLookupError:pass
            waited,status,usage=os.wait4(pid,0);break
        time.sleep(.01)
    elapsed=time.perf_counter()-start
    # In normal completion the runner/plot waits for descendants; aborted orphan
    # usage can be missing from wait4 and is flagged rather than called zero.
    receipt={'host_identity_handshake':host_identity,'schema':'REI_DR_OUTER_OS_RECEIPT_V1','job':job,'argv':argv,'cwd':str(ROOT),
        'raw_wait_status':status,'exit_code':os.waitstatus_to_exitcode(status),
        'user_CPU_s':usage.ru_utime,'system_CPU_s':usage.ru_stime,
        'whole_waited_command_CPU_s':usage.ru_utime+usage.ru_stime,
        'wall_s':elapsed,'maxrss_KiB_Linux':usage.ru_maxrss,
        'supervisor_prefix_CPU_s':time.process_time()-prefix,
        'watchdog_stop':reason,'maximum_observed_family_ticks':maximum_ticks,
        'clock_ticks_per_s':ticks_per_s,'last_observed_family_pids':last_members,
        'targets':{'aggregate_CPU_s':target,'watchdog_CPU_s':threshold,'wall_s':wall,'address_space_bytes_per_process':memory},
        'environment_resource_limits':envlimits,'environment':{'python':sys.version,'platform':platform.platform()},
        'sources':sources,'outputs':[identity(output/n) for n in ('STDOUT.txt','STDERR.txt')],
        'accounting_scope':'wait4 whole command including descendants it waited for; inner/script CPU already included, never add it again; supervisor prefix separate',
        'abort_limit':'On watchdog abort, un-reaped descendant resource usage may be excluded from wait4; live family ticks are retained and unknown remainder is not zero',
        'target_limit':'Tick/poll scheduling and non-atomic process reads mean this is not a strict whole-host CPU bound',
        'authority_record':'Root published RESOURCE_ALLOCATION at26392627868809c443a9b74629691f536af0c09e plus explicit current dispatch',
        'separate_symbolic_identity_CPU_s':'.00341 within separate .05 reserve; not charged again here',
        'unknown_exclusions':'Supervisor startup/import/preparation/final receipt/exit/model/network/tail UNKNOWN_NOT_ZERO',
        'reset_transfer_reopen':False,'stage_admission':'NOT_ISSUED_BY_SUPERVISOR'}
    (output/'PROCESS.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return 0 if receipt['exit_code']==0 and reason is None else 1


if __name__=='__main__':raise SystemExit(main())
