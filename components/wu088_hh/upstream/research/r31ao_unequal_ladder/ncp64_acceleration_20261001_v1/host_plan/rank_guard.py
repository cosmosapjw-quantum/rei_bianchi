"""Pin an OpenMPI rank by Linux OS CPU ID before entering the Fortran program."""
import argparse,json,os,resource
from pathlib import Path

THREAD_ENV={k:'1' for k in ('OMP_NUM_THREADS','OMP_THREAD_LIMIT','OPENBLAS_NUM_THREADS',
    'MKL_NUM_THREADS','BLIS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS','FLINT_NUM_THREADS')}


def main():
    p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('command',nargs=argparse.REMAINDER)
    a=p.parse_args();cmd=a.command[1:] if a.command[:1]==['--'] else a.command
    plan=json.loads(Path(a.plan).read_text())
    if plan['status']!='PLAN_READY' or not cmd or not Path(cmd[0]).is_absolute():raise ValueError('admitted absolute command required')
    rank=int(os.environ['OMPI_COMM_WORLD_RANK']);size=int(os.environ['OMPI_COMM_WORLD_SIZE'])
    if size!=plan['rank_count'] or not 0<=rank<size:raise ValueError('MPI rank/plan mismatch')
    before=sorted(os.sched_getaffinity(0));cpu=plan['rank_os_cpus'][rank]
    if cpu not in plan['host']['affinity_os_cpus'] or cpu not in before:raise ValueError('planned OS CPU unavailable')
    os.sched_setaffinity(0,{cpu});after=sorted(os.sched_getaffinity(0))
    if after!=[cpu]:raise ValueError('affinity readback mismatch')
    cap=plan['coordinator_bytes'] if rank==0 and size>1 else plan['worker_bytes']
    resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
    resource.setrlimit(resource.RLIMIT_FSIZE,(plan['file_size_cap_bytes'],plan['file_size_cap_bytes']))
    env=dict(os.environ);env.update(THREAD_ENV)
    rec={'rank':rank,'size':size,'os_cpu':cpu,'before':before,'after':after,
         'address_space_bytes_per_process':cap,'aggregate_tree_memory_hard_cap':False,
         'threads_environment':THREAD_ENV,'argv':cmd}
    with (Path(plan['run_root'])/'bindings'/('rank_'+str(rank)+'.json')).open('x') as f:json.dump(rec,f,indent=2)
    os.execve(cmd[0],cmd,env)


if __name__=='__main__':main()
