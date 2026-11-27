"""Exact rank affinity and fixed dispatcher argv; no remainder command API."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
sys.dont_write_bytecode=True
import launcher as h


def main():
    p=argparse.ArgumentParser(); p.add_argument('--plan',required=True);p.add_argument('--plan-sha256',required=True)
    a=p.parse_args()
    if os.getuid()==0 or os.geteuid()==0: raise h.Refusal('nonroot required')
    plan=h.parse(a.plan)
    if hashlib.sha256(h.canonical({k:v for k,v in plan.items() if k!='plan_payload_sha256'})).hexdigest()!=a.plan_sha256 or plan['plan_payload_sha256']!=a.plan_sha256:
        raise h.Refusal('externally bound plan required')
    if plan['schema']!='WU088_NATIVE_MPI_HOST_PLAN_V1' or plan['status']!='PLAN_READY': raise h.Refusal('host plan required')
    for rec in plan['host_sources']+[plan['preparation'],plan['mpirun'],plan['mpi_binary'],plan['python'],plan['mpi_build']]:
        if h.identity(rec['path'])!=rec: raise h.Refusal('rank source/binary identity changed')
    rank=int(os.environ['OMPI_COMM_WORLD_RANK']); size=int(os.environ['OMPI_COMM_WORLD_SIZE'])
    if size!=plan['rank_count'] or not 0<=rank<size: raise h.Refusal('rank count mismatch')
    cpu=plan['rank_os_cpus'][rank]; before=sorted(os.sched_getaffinity(0))
    if cpu not in before: raise h.Refusal('rank CPU outside available affinity')
    os.sched_setaffinity(0,{cpu}); after=sorted(os.sched_getaffinity(0))
    if after!=[cpu]: raise h.Refusal('rank affinity readback mismatch')
    cap=plan['coordinator_bytes'] if rank==0 and size>1 else plan['worker_bytes']
    resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
    resource.setrlimit(resource.RLIMIT_FSIZE,(plan['file_size_cap_bytes'],plan['file_size_cap_bytes']))
    cmd=h.rank_command(plan)
    rec={'rank':rank,'size':size,'before':before,'after':after,'argv':cmd,
        'plan_payload_sha256':a.plan_sha256,'per_process_address_space_bytes':cap,
        'aggregate_memory_enforcement':'parent_job_cgroup_v2','threads_environment':h.THREAD_ENV}
    with (Path(plan['run_root'])/'bindings'/('rank_%d.json'%rank)).open('xb') as f: f.write(h.canonical(rec)+b'\n')
    env=dict(os.environ);env.update(h.THREAD_ENV)
    os.execve(cmd[0],cmd,env)


if __name__=='__main__': main()
