"""Linux single-process native-job guard, not an authorization mechanism.

RLIMIT_AS limits virtual address space per process, not aggregate tree RSS.
The process group receives SIGKILL on wall timeout. Children that deliberately
escape the group are out of contract. Use from a single-threaded launcher.
Output goes to files with a child file-size cap; parent previews are bounded.
"""
import argparse
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import tempfile
import time


def run_guarded(argv, *, wall_seconds, memory_mib, output_dir=None):
    if (not isinstance(argv,(list,tuple)) or not argv or
            any(type(x) is not str or not x or '\0' in x for x in argv)):
        raise ValueError('nonempty argument vector required; shell commands are not accepted')
    if type(wall_seconds) not in (int,float) or not math.isfinite(wall_seconds) or not 0<wall_seconds<=86400:
        raise ValueError('finite wall budget in (0,86400] seconds required')
    if type(memory_mib) is not int or not 16<=memory_mib<=65536:
        raise ValueError('integer per-process address-space cap 16..65536 MiB required')
    if os.name!='posix' or not hasattr(resource,'RLIMIT_AS'):
        raise RuntimeError('Linux/POSIX RLIMIT_AS required; no unguarded fallback')
    folder=None
    if output_dir is not None:
        folder=Path(output_dir);folder.mkdir(parents=False,exist_ok=False)
    stdout_file=(folder/'stdout.log').open('x+b') if folder else tempfile.TemporaryFile()
    stderr_file=(folder/'stderr.log').open('x+b') if folder else tempfile.TemporaryFile()
    memory_bytes=memory_mib*1024*1024
    cpu_seconds=max(1,math.ceil(wall_seconds))
    file_bytes=8*1024*1024

    def apply_limits():
        resource.setrlimit(resource.RLIMIT_AS,(memory_bytes,memory_bytes))
        resource.setrlimit(resource.RLIMIT_CPU,(cpu_seconds,cpu_seconds))
        resource.setrlimit(resource.RLIMIT_FSIZE,(file_bytes,file_bytes))

    start=time.monotonic()
    timed_out=False
    descendants=False
    process=None
    env=os.environ.copy();env['OMP_NUM_THREADS']='1';env['OPENBLAS_NUM_THREADS']='1'
    try:
        process=subprocess.Popen(list(argv),stdin=subprocess.DEVNULL,stdout=stdout_file,
                                 stderr=stderr_file,start_new_session=True,
                                 preexec_fn=apply_limits,env=env,shell=False)
        try:
            process.wait(timeout=wall_seconds)
        except subprocess.TimeoutExpired:
            timed_out=True
            try:os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            process.wait()
        # A native single-process job must not return while descendants keep
        # running. Kill the remaining group even after a successful leader.
        try:
            os.killpg(process.pid,signal.SIGKILL)
            descendants=not timed_out
        except ProcessLookupError:
            pass
        elapsed=time.monotonic()-start
        captures={}
        for name,stream in (('stdout',stdout_file),('stderr',stderr_file)):
            stream.flush();size=stream.seek(0,2);stream.seek(0)
            captures[name]=stream.read(65536).decode('utf-8',errors='replace')
            captures[name+'_bytes']=size
            captures[name+'_preview_truncated']=size>65536
        result={
            'schema':'WU088_PROCESS_GUARD_RECEIPT_V1','argv':list(argv),
            'status':'CERTIFICATE_INCONCLUSIVE_RESOURCE_LIMIT' if timed_out else
                     ('PROCESS_CONTRACT_VIOLATION' if descendants else
                      ('PROCESS_COMPLETED' if process.returncode==0 else 'PROCESS_NONZERO_EXIT')),
            'reason':'PROCESS_GROUP_WALL_TIMEOUT' if timed_out else
                     ('DESCENDANTS_SURVIVE_LEADER' if descendants else 'CHILD_EXIT_RECORDED'),
            'returncode':process.returncode,'wall_seconds':elapsed,
            'wall_budget_seconds':wall_seconds,'address_space_bytes_per_process':memory_bytes,
            'cpu_seconds_per_process':cpu_seconds,'file_size_cap_bytes_per_file':file_bytes,
            'aggregate_tree_memory_limit':False,'scientific_authorization_granted':False,
            'scientific_validity_inferred_from_exit':False,**captures,
        }
        if folder:
            with (folder/'PROCESS_RECEIPT.json').open('x') as stream:
                json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
        return result
    finally:
        if process is not None:
            try:os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:pass
        stdout_file.close();stderr_file.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wall-seconds',type=float,required=True)
    parser.add_argument('--memory-mib',type=int,required=True)
    parser.add_argument('--output-dir',required=True)
    parser.add_argument('command',nargs=argparse.REMAINDER)
    args=parser.parse_args();cmd=args.command
    if cmd and cmd[0]=='--':cmd=cmd[1:]
    result=run_guarded(cmd,wall_seconds=args.wall_seconds,memory_mib=args.memory_mib,output_dir=args.output_dir)
    print(json.dumps({k:v for k,v in result.items() if k not in ('stdout','stderr')},ensure_ascii=False))
    raise SystemExit(0 if result['status']=='PROCESS_COMPLETED' else 2)


if __name__=='__main__':main()
