"""Fixed single-host native MPI admission, cgroup containment and collection.

Uses the immutable native_execution_20261001_v1 adapter/native_driver only.
No refined/log driver, arbitrary executable task, resume, root or oversubscription.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import sys
import re

sys.dont_write_bytecode = True
HERE=Path(__file__).resolve().parent
LADDER=HERE.parent.parent
OLD=LADDER/'native_execution_20261001_v1'
ADAPTER=OLD/'mpi_native_tasks/worker.py'
PLANNER=LADDER/'ncp64_acceleration_20261001_v1/host_plan/planner.py'
from cgroup_guard import Refusal, JobCgroup, parent_check, execute_contained

THREAD_ENV={k:'1' for k in ('OMP_NUM_THREADS','OMP_THREAD_LIMIT','OPENBLAS_NUM_THREADS',
    'MKL_NUM_THREADS','BLIS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS','FLINT_NUM_THREADS')}


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m


def identity(path):
    p=Path(path)
    if not p.is_absolute() or p.resolve(strict=True)!=p or not p.is_file() or p.stat().st_size>64*1024**2:
        raise Refusal('bounded canonical regular file required')
    data=p.read_bytes()
    return {'path':str(p),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}


def pinned(path, expected):
    rec=identity(path)
    if rec['sha256']!=expected: raise Refusal('external file identity mismatch: '+str(path))
    return rec


def canonical(obj): return json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def parse(path):
    w=module('_native_host_adapter_parse',ADAPTER)
    return w.parse(w.read(path))


def bundle_check(preparation, expected_sha, require_empty=True):
    pinned(preparation,expected_sha)
    w=module('_native_host_adapter',ADAPTER); p=w.parse(w.read(preparation))
    if p.get('schema')!='WU088_NATIVE_DISPATCH_PREPARATION_V1' or p.get('status')!='PREPARED_NOT_EXECUTED':
        raise Refusal('exact native task preparation required')
    bundle=Path(preparation).parent
    for key,name in [('manifest','MANIFEST.json'),('worklist','WORKLIST.txt'),('bound_worker','bound_worker.py')]:
        if p[key]['path']!=str(bundle/name): raise Refusal('preparation bundle path mismatch')
        w.check_identity(p[key])
    m,context=w.load_manifest(p['manifest']['path'],p['manifest']['sha256'])
    if p['selected_native_indices']!=[t['native_index'] for t in m['tasks']]: raise Refusal('selected indices mismatch')
    expected_worklist=('%d\n'%len(m['tasks']))+''.join('%d %d\n'%(i,m['native_limits']['wall_seconds']+10) for i in range(len(m['tasks'])))
    if (bundle/'WORKLIST.txt').read_bytes()!=expected_worklist.encode(): raise Refusal('exact worklist required')
    # Reconstruct immutable generator output: a pinned arbitrary script is not
    # accepted as a substitute for the fixed native adapter.
    bound=f'''"""Generated fixed-manifest worker; no arbitrary command arguments."""
import hashlib, importlib.util, pathlib, sys
sys.dont_write_bytecode = True
p = pathlib.Path({str(ADAPTER)!r})
if hashlib.sha256(p.read_bytes()).hexdigest() != {m['core_worker_sha256']!r}:
    raise SystemExit('CORE_WORKER_CHANGED')
spec = importlib.util.spec_from_file_location('_bound_native_worker', p)
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)
raise SystemExit(worker.main({p['manifest']['sha256']!r}, {p['manifest']['path']!r}))
'''
    if (bundle/'bound_worker.py').read_bytes()!=bound.encode(): raise Refusal('fixed bound worker differs from immutable generator')
    results=Path(m['output_root'])
    if results!=bundle/'results': raise Refusal('results must be within prepared bundle')
    if require_empty and any(results.iterdir()): raise Refusal('existing output/claim refused; no automatic reuse')
    return p,m,w,context


def mpi_build_check(path,expected):
    pinned(path,expected); b=parse(path)
    if b.get('schema')!='WU088_MPI_FORTRAN_BUILD_V1' or b.get('Fortran_compiled') is not True:
        raise Refusal('native Fortran build receipt required')
    for name,rec in b['sources'].items():
        if Path(rec['resolved_path'])!=LADDER/'ncp64_acceleration_20261001_v1/mpi_fortran'/name:
            raise Refusal('unexpected MPI source path')
        pinned(rec['resolved_path'],rec['sha256'])
    if set(b['sources'])!={'dispatcher.f90','worker_spawn.c','worker_spawn.h'}:
        raise Refusal('exact MPI source set required')
    binary=b['binary']; pinned(binary['resolved_path'],binary['sha256'])
    if not os.access(binary['resolved_path'],os.X_OK): raise Refusal('MPI binary not executable')
    return b


def fixed_argv(plan):
    n=str(plan['rank_count'])
    return [plan['mpirun']['path'],'-np',n,'--host','localhost:'+n,'--map-by','slot',
        '--bind-to','none','--nooversubscribe','--report-bindings',
        plan['python']['path'],str(HERE/'rank_guard.py'),'--plan',str(Path(plan['run_root'])/'HOST_PLAN.json'),
        '--plan-sha256',plan['plan_payload_sha256']]


def rank_command(plan):
    return [plan['mpi_binary']['path'],plan['python']['path'],plan['bound_worker']['path'],
        plan['manifest']['path'],plan['worklist']['path']]


def target_resources(planner,host,parent):
    """Include target ancestry, which may differ from the launcher's cgroup."""
    parent=Path(parent); mounts=[]
    unescape=lambda s:re.sub(r'\\([0-7]{3})',lambda m:chr(int(m[1],8)),s)
    for line in Path('/proc/self/mountinfo').read_text().splitlines():
        left,right=line.split(' - ',1)
        if right.split()[0]=='cgroup2':
            mount=Path(unescape(left.split()[4]))
            if parent.is_relative_to(mount): mounts.append(mount)
    if not mounts: raise Refusal('target cgroup mount not observable')
    mount=max(mounts,key=lambda p:len(p.parts))
    records=planner.ancestor_limits(parent,mount,2)
    host=dict(host);host['cgroup']=dict(host['cgroup'])
    host['cgroup']['ancestors']=[*host['cgroup']['ancestors'],*records]
    host['target_cgroup_ancestors']=records
    effective=parent/'cpuset.cpus.effective'
    if effective.exists():
        allowed=set(planner.cpulist(planner.read(effective)))&set(host['affinity_os_cpus'])
        if not allowed: raise Refusal('no CPU in both launcher affinity and target cpuset')
        host['affinity_os_cpus']=sorted(allowed)
        host['cpus']=[c for c in host['cpus'] if c['os_cpu'] in allowed]
        host['logical_cpu_count']=len(allowed)
        host['physical_cores_in_affinity']=len({(c['package'],c['core']) for c in host['cpus']})
    return host


def collect(preparation,expected,plan):
    p,m,w,context=bundle_check(preparation,expected,require_empty=False)
    results=Path(m['output_root']); expected_names={'primitive_%04d.json'%t['native_index'] for t in m['tasks']}
    actual={x.name for x in results.iterdir()}
    # The immutable driver's finally block removes its claim; a remaining
    # claim never becomes a successful collection merely because a JSON exists.
    if actual!=expected_names: raise Refusal('incomplete/unexpected native output or claim set')
    entries=[]
    for ordinal,task in enumerate(m['tasks']):
        path=results/('primitive_%04d.json'%task['native_index'])
        result=w.validate_envelope(w.parse(w.read(path)),m,ordinal,context)
        entries.append({'ordinal':ordinal,'native_index':task['native_index'],'output':w.identity(path),
            'result_sha256':result['result_sha256']})
    bindings=[]
    for rank in range(plan['rank_count']):
        path=Path(plan['run_root'])/'bindings'/('rank_%d.json'%rank)
        rec=parse(path)
        if (rec['rank']!=rank or rec['size']!=plan['rank_count'] or rec['after']!=[plan['rank_os_cpus'][rank]]
                or rec['argv']!=rank_command(plan) or rec['plan_payload_sha256']!=plan['plan_payload_sha256']):
            raise Refusal('rank binding receipt mismatch')
        bindings.append(identity(path))
    if len(list((Path(plan['run_root'])/'bindings').iterdir()))!=plan['rank_count']: raise Refusal('unexpected rank receipts')
    return {'status':'CONDITIONAL_NATIVE_INTERIOR_COLLECTION','entries':entries,'rank_bindings':bindings,
        'selected_task_count':len(entries),'canonical_payload_sha256':hashlib.sha256(canonical(entries)).hexdigest(),
        'scientific_admission':False,'production_admission':False,'whole_domain':False}


def prepare_plan(a):
    p,m,_,_=bundle_check(a.preparation,a.preparation_sha256)
    if m['native_limits']['memory_mib']>1024:
        raise Refusal('native per-process memory cap exceeds fixed 1024 MiB rank reservation')
    b=mpi_build_check(a.mpi_build,a.mpi_build_sha256)
    mpirun=pinned(a.mpirun,a.mpirun_sha256)
    if not os.access(a.mpirun,os.X_OK): raise Refusal('mpirun executable required')
    planner=module('_native_host_planner',PLANNER)
    host=target_resources(planner,planner.detect(),a.cgroup_parent)
    resource_plan=planner.plan(host,reserve_bytes=a.reserve_mib*1024**2,
        worker_bytes=1024**3,coordinator_bytes=1024**3,requested_ranks=a.ranks)
    if resource_plan['status']!='PLAN_READY': raise Refusal('resource admission: '+','.join(resource_plan['blocked_reasons']))
    if not 1<=a.wall_seconds<=86400: raise Refusal('wall bound required')
    output=Path(a.output)
    if not output.is_absolute() or output!=output.resolve() or output.exists() or not output.parent.is_dir():
        raise Refusal('new canonical run directory under existing parent required')
    result={**resource_plan,'schema':'WU088_NATIVE_MPI_HOST_PLAN_V1','status':'PLAN_READY',
        'job_memory_budget_bytes':resource_plan['rank_count']*1024**3,
        'run_root':str(output),'mpirun':mpirun,'mpi_binary':identity(b['binary']['resolved_path']),
        'python':identity(Path(sys.executable).resolve()),'preparation':identity(a.preparation),
        **{k:p[k] for k in ('manifest','bound_worker','worklist')},
        'wall_cap_seconds':a.wall_seconds,'file_size_cap_bytes':64*1024**2,
        'delegated_cgroup_parent':str(Path(a.cgroup_parent)),'pids_cap':min(4096,32+16*resource_plan['rank_count']),
        'host_sources':[identity(x) for x in (HERE/'launcher.py',HERE/'rank_guard.py',HERE/'cgroup_guard.py',HERE/'containment_probe.py',PLANNER,ADAPTER)],
        'mpi_build':identity(a.mpi_build),'aggregate_memory_enforcement':'cgroup_v2_memory.max_swap_zero',
        'task_driver':'native_execution_20261001_v1/native_driver; NOT refined/log driver',
        'scientific_admission':False,'production_admission':False}
    result['plan_payload_sha256']=hashlib.sha256(canonical(result)).hexdigest()
    return result


def run(a):
    # Refuse root before even reading a scientific plan or launching mpirun.
    if os.getuid()==0 or os.geteuid()==0: raise Refusal('NONROOT_REQUIRED_NO_BYPASS')
    parent_check(a.cgroup_parent)
    plan=prepare_plan(a)
    if not a.execute: return plan
    # Memory availability naturally changes; require sufficient fresh capacity,
    # identical rank placement and unchanged input identities, not byte equality
    # of volatile observations.
    fresh=prepare_plan(a)
    stable=('rank_count','rank_os_cpus','mpirun','mpi_binary','python','preparation',
            'manifest','bound_worker','worklist','host_sources','mpi_build')
    if any(fresh[k]!=plan[k] for k in stable) or fresh['observed_available_memory_bytes']-fresh['reserve_bytes']<plan['job_memory_budget_bytes']:
        raise Refusal('host/input state changed; replan')
    root=Path(plan['run_root']); root.mkdir(mode=0o700); (root/'bindings').mkdir(mode=0o700)
    (root/'HOST_PLAN.json').write_bytes(canonical(plan)+b'\n')
    env={'PATH':'/usr/local/bin:/usr/bin:/bin','LC_ALL':'C','LANG':'C',
        'PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1',**THREAD_ENV}
    result={'status':'BLOCKED','MPI_execution_started':False,'scientific_admission':False,'production_admission':False}
    group=None
    def stopped(signum,frame): raise KeyboardInterrupt('host received signal '+str(signum))
    oldterm=signal.signal(signal.SIGTERM,stopped)
    try:
        from containment_probe import probe
        result['containment_probe']=probe(a.cgroup_parent,root/'containment_probe',plan['rank_os_cpus'])
        group=JobCgroup(a.cgroup_parent,memory_bytes=plan['job_memory_budget_bytes'],ranks=plan['rank_count'],pids=plan['pids_cap'])
        result['MPI_execution_attempted']=True
        result['MPI_execution_started']=None  # until Popen evidence returns
        result.update(execute_contained(fixed_argv(plan),group=group,output=root,seconds=plan['wall_cap_seconds'],
            cpus=plan['rank_os_cpus'],env=env,file_cap=plan['file_size_cap_bytes']))
        result['MPI_execution_started']=result.pop('process_started')
        for rec in plan['host_sources']+[plan['preparation'],plan['mpirun'],plan['mpi_binary'],plan['python'],plan['mpi_build']]:
            if identity(rec['path'])!=rec: raise Refusal('post-run immutable file changed')
        if result['status']=='COMPLETED':
            result['collection']=collect(a.preparation,a.preparation_sha256,plan)
            result['status']='CONDITIONAL_NATIVE_MPI_COMPLETE'
    except BaseException as exc:
        result.update(status='INCONCLUSIVE',reason=type(exc).__name__+': '+str(exc))
    finally:
        if group is not None:
            try:
                group.kill_and_empty(); result['cleanup_populated_zero']=True; group.close()
            except BaseException as exc:
                result.update(status='CLEANUP_UNCONFIRMED',cleanup_error=str(exc),cleanup_populated_zero=False)
        signal.signal(signal.SIGTERM,oldterm)
        # Inventory is evidence of files left by a partial job, never successful
        # envelope collection or authorization to retry them.
        try:
            directory=Path(plan['manifest']['path']).parent/'results'
            names=sorted(directory.iterdir())
            if len(names)>5184: raise Refusal('partial output inventory file cap')
            result['durable_output_inventory']=[identity(x) for x in names]
        except (ValueError,OSError) as exc:
            result['inventory_error']=str(exc)
        (root/'HOST_RUN.json').write_bytes(canonical(result)+b'\n')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('preparation','preparation-sha256','mpi-build','mpi-build-sha256','mpirun','mpirun-sha256','cgroup-parent','output'):
        p.add_argument('--'+name,required=True)
    p.add_argument('--ranks',type=int,required=True); p.add_argument('--reserve-mib',type=int,default=1024)
    p.add_argument('--wall-seconds',type=int,default=300); p.add_argument('--execute',action='store_true')
    a=p.parse_args()
    try: result=run(a)
    except (ValueError,OSError,KeyError,TypeError) as exc:
        result={'status':'BLOCKED','reason':str(exc),'MPI_execution_started':False,'actual_HH_runs':0,
            'scientific_admission':False,'production_admission':False}
    print(json.dumps(result,indent=2))
    return 0 if result['status'] in ('PLAN_READY','CONDITIONAL_NATIVE_MPI_COMPLETE') else 2


if __name__=='__main__': raise SystemExit(main())
