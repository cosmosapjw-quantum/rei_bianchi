#!/usr/bin/env python3
"""One explicit, resumable HH batch for the user's 64 CPU / 128 GiB NCP host.

Default is a read-only plan. --run executes already implemented tasks on the
current host. This program neither SSHs nor publishes nor identifies a hostname
as NCP. Only its own process groups can be stopped. Historical completed panels
and the already returned PHYS70 L64 diagnostic are excluded.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys
import time
import uuid

HERE=Path(__file__).resolve().parent
UNIT=HERE.parent
ROOT=UNIT.parents[1]
SOURCE_SHA='f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d'
PARENT='9d6d7491f26850918d6316ed466e3df35dace570'

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def write_new(path,data):
    from return_capsule import publish_new
    publish_new(path,data)

def utc():
    return datetime.now(timezone.utc).isoformat()

def hardware():
    affinity=len(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else os.cpu_count() or 1
    quota=None;mem_limit=None
    cpu=Path('/sys/fs/cgroup/cpu.max')
    if cpu.exists():
        q,p=cpu.read_text().split()
        if q!='max':quota=max(1,int(q)//int(p))
    memory=Path('/sys/fs/cgroup/memory.max')
    if memory.exists() and memory.read_text().strip()!='max':
        mem_limit=int(memory.read_text())
    physical=os.sysconf('SC_PAGE_SIZE')*os.sysconf('SC_PHYS_PAGES')
    available=physical if mem_limit is None else min(physical,mem_limit)
    return dict(hostname=platform.node(),platform=platform.platform(),machine=platform.machine(),
                cpu_count=os.cpu_count(),affinity_cpus=affinity,cgroup_quota_cpus=quota,
                effective_cpus=min(affinity,quota) if quota else affinity,
                physical_memory_bytes=physical,cgroup_memory_bytes=mem_limit,
                effective_memory_bytes=available,NCP_identity='CURRENT_HOST_NOT_ASSUMED')

def resource_plan(cpus,memory_gib,observed=None):
    if type(cpus) is not int or not 1<=cpus<=64:
        raise ValueError('requested cpus must be 1..64')
    if type(memory_gib) is not int or not 5<=memory_gib<=128:
        raise ValueError('requested memory_gib must be 5..128')
    observed=hardware() if observed is None else observed
    cores=min(cpus,observed['effective_cpus'])
    memory=min(memory_gib,observed['effective_memory_bytes']//2**30)
    if memory<5:raise ValueError('at least 5 GiB observed memory required for the full batch')
    reserve=max(1,min(16,memory//8));usable=memory-reserve
    prepare=min(cores,64,usable)  # <= 1 GiB/process; no competing batch phase.
    longtail=min(6,cores,max(1,usable//6))
    validated=min(28,max(0,cores-longtail),max(0,(usable-4*longtail)//2))
    concurrent=validated>=1
    if not concurrent:
        longtail=min(6,cores,max(1,usable//4))
        validated=min(28,cores,max(1,usable//2))
    result=dict(requested_cpus=cpus,requested_memory_gib=memory_gib,
                effective_cpus=cores,effective_memory_gib=memory,reserve_gib=reserve,
                source_preparation_workers=prepare,source_worker_memory_gib=1,
                native_workers=cores,longtail_workers=longtail,longtail_worker_memory_gib=4,
                validated_workers=validated,validated_worker_memory_gib=2,
                legacy_parallel=concurrent,observed=observed)
    result['legacy_reserved_gib']=(4*longtail+2*validated if concurrent else max(4*longtail,2*validated))
    result['legacy_reserved_cpus']=(longtail+validated if concurrent else max(longtail,validated))
    if result['legacy_reserved_gib']>usable or result['legacy_reserved_cpus']>cores:
        raise ArithmeticError('resource accounting exceeds observed allocation')
    return result

def inventory(plan):
    return [
      dict(id='PHYS66_LONGTAIL6',status='READY_NO_OBSERVED_RETURN',
           cases=[dict(L=L,T=T) for L in (28,64) for T in (55,65,75)],
           workers=plan['longtail_workers'],engine='unchanged PHYS66/64 full-matrix ordered hierarchy'),
      dict(id='PHYS68_VALIDATED_L64',status='REPLACED_BY_REUSE_EQUIVALENT_REQUEST',
           inherited_intermediate_modes=[0,36],new_modes=[37,64],new_independent_jobs=28,
           workers=plan['validated_workers'],target='same finite L64 D1 1e-45 / D2 1e-62 goals'),
      dict(id='PHYS72_HOST_REPRODUCTION',status='READY_OPTIONAL_NOT_SCIENCE_GATE',
           exact_scalar_jobs=3,Fortran_compile_and_scalar_run=1),
      dict(id='PHYS73_ORIGINAL_SOURCE',status='NEW_READY_FINITE_GRID_DIAGNOSTIC',
           L=64,T=44,radial_nodes=[257,513],angular_source='analytic_positive_Yukawa_multipoles',dps=60,
           preparation_workers=plan['source_preparation_workers'],native_workers=plan['native_workers']),
      dict(id='PHYS70_L64',status='COMPLETE_REUSED_PR123_EXCLUDED_FROM_QUEUE'),
      dict(id='PHYS71_D3_AND_INHERITED_PROFILES',status='COMPLETE_REUSED_EXCLUDED_FROM_QUEUE',
           old_panels_to_integrate=0,old_profiles_to_integrate=0),
    ]

def source_binding():
    source=ROOT/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'
    if sha(source)!=SOURCE_SHA:raise ValueError('frozen original source changed')
    paths=list(UNIT.glob('implementation/*.py'))+list(UNIT.glob('native/*.rs'))
    # Bind all inherited computational engines actually reachable by the jobs.
    paths+=list((ROOT/'src/wu088_hh').glob('*.py'))
    paths += [ROOT/'scripts'/name for name in ('phys66_ncp.py','phys68_ncp.py','phys69_band_profiles.py')]
    paths += list((ROOT/'research/hh_phys72_20261020/implementation').glob('*.py'))
    paths += [ROOT/'research/hh_phys72_20261020/native/phys72_bounds.f90',
              ROOT/'research/hh_phys72_20261020/ncp_delivery/run_native.py']
    paths += [source,ROOT/'research/hh_phys68_20261019/profiles/run_l28_t65_completed/CERTIFICATE.json',
              ROOT/'research/hh_phys69_20261019/band/run_j29_36_t65/CERTIFICATE.json']
    paths += [p for p in (ROOT/'research/hh_phys72_20261020/inputs').iterdir() if p.is_file()]
    pins={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))}
    versions={}
    for name in ('numpy','scipy','mpmath','python-flint'):
        try:versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:versions[name]=None
    head=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
    subprocess.run(['git','-C',str(ROOT),'merge-base','--is-ancestor',PARENT,head],check=True)
    return dict(schema='PHYS73_NCP_BINDING_V1',source_head=head,parent=PARENT,
                source_sha256=SOURCE_SHA,files_sha256=pins,
                python=sys.version,versions=versions,HH_R10='OFF')

def succeeded(directory,binding):
    path=Path(directory)/'SUCCESS.json'
    if not path.exists():return None
    saved=json.loads(path.read_text())
    if (saved.get('schema')!='PHYS73_JOB_EXECUTION_V1' or saved.get('status')!='COMPLETE'
            or saved.get('exit_code')!=0 or saved.get('failure') is not None
            or saved.get('HH_R10')!='OFF' or saved.get('binding')!=binding):
        raise ValueError('completed job belongs to different command/source/runtime')
    expected_files=set()
    for name in binding['expected_outputs']:
        target=Path(name)
        if target.is_symlink():raise ValueError('output symlink refused')
        if target.is_dir():
            entries=list(target.rglob('*'))
            if any(item.is_symlink() for item in entries):raise ValueError('nested output symlink refused')
            expected_files.update(str(item) for item in entries if item.is_file())
        else:expected_files.add(str(target))
    if set(saved.get('outputs_sha256',{}))!=expected_files:
        raise ValueError('saved output membership differs')
    for name,digest in saved['outputs_sha256'].items():
        if sha(name)!=digest:raise ValueError('completed output changed; reconcile before running')
    attempt=Path(saved['attempt'])
    if not attempt.resolve().is_relative_to(Path(directory).resolve()):
        raise ValueError('attempt outside job directory')
    for name,digest in saved.get('logs',{}).items():
        if name not in ('stdout.txt','stderr.txt') or sha(attempt/name)!=digest:
            raise ValueError('completed log changed')
    return {**saved,'this_invocation':'REUSED_VERIFIED_NO_CHILD'}

def run_job(out,job_id,command,outputs,identity,timeout,validator=None,environment=None):
    """Immutable attempts; success reuse requires exact argv, identities, and output bytes."""
    directory=Path(out)/'jobs'/job_id
    directory.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,HH_R10='OFF',PYTHONUNBUFFERED='1')
    for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS'):
        env[key]='1'
    if environment:env.update(environment)
    if env.get('HH_R10')!='OFF':raise ValueError('HH_R10 must remain OFF')
    exe=shutil.which(str(command[0])) or str(command[0])
    binding=dict(identity=identity,command=[str(x) for x in command],
                 expected_outputs=sorted(str(Path(p).resolve()) for p in outputs),
                 environment={k:env.get(k) for k in ('HH_R10','PYTHONPATH','LD_LIBRARY_PATH','OMP_NUM_THREADS',
                     'OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS')},
                 explicit_environment=environment or {},
                 executable_sha256=sha(exe) if Path(exe).is_file() else None,
                 driver_sha256=sha(__file__))
    old=succeeded(directory,binding)
    if old is not None:
        if validator:validator()
        return old
    attempt=directory/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'_'+uuid.uuid4().hex[:8])
    attempt.mkdir()
    write_new(attempt/'REQUEST.json',binding)
    started=time.perf_counter();start_utc=utc();code=None;failure=None;pid=None
    try:
        with (attempt/'stdout.txt').open('xb') as stdout,(attempt/'stderr.txt').open('xb') as stderr:
            child=subprocess.Popen([str(x) for x in command],stdout=stdout,stderr=stderr,
                                   env=env,cwd=ROOT,start_new_session=True)
            pid=child.pid
            try:code=child.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                failure='WALL_TIMEOUT'
                os.killpg(child.pid,signal.SIGTERM)
                try:code=child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid,signal.SIGKILL);code=child.wait()
                # The leader may exit before a descendant that ignores TERM.
                # The entire newly created owned group must be stopped.
                try:os.killpg(child.pid,signal.SIGKILL)
                except ProcessLookupError:pass
    except OSError as exc:failure='ENVIRONMENT: '+str(exc)
    if code not in (None,0) and failure is None:failure='CHILD_EXIT_NONZERO'
    payloads={};status='FAILED'
    if code==0 and failure is None:
        try:
            for path in outputs:
                path=Path(path)
                if path.is_symlink():raise ValueError('output symlink refused')
                path=path.resolve()
                if path.is_dir():
                    for item in sorted(path.rglob('*')):
                        if item.is_symlink():raise ValueError('nested output symlink refused')
                        if item.is_file():payloads[str(item)]=sha(item)
                else:payloads[str(path)]=sha(path)
            if validator:validator()
            status='COMPLETE'
        except (ValueError,KeyError,OSError,AssertionError) as exc:
            failure='OUTPUT_VALIDATION: '+str(exc)
    receipt=dict(schema='PHYS73_JOB_EXECUTION_V1',job_id=job_id,status=status,
                 binding=binding,started_utc=start_utc,ended_utc=utc(),child_pid=pid,
                 exit_code=code,failure=failure,wall_seconds=time.perf_counter()-started,
                 timeout_seconds=timeout,outputs_sha256=payloads,
                 logs={n:sha(attempt/n) for n in ('stdout.txt','stderr.txt') if (attempt/n).exists()},
                 attempt=str(attempt),HH_R10='OFF')
    write_new(attempt/'EXECUTION.json',receipt)
    if status=='COMPLETE':write_new(directory/'SUCCESS.json',receipt)
    return {**receipt,'this_invocation':'EXECUTED_CHILD'}

def json_status(path,key,allowed):
    value=json.loads(Path(path).read_text())
    if value.get(key) not in allowed:
        raise ValueError(f'{Path(path).name}: unexpected {key}={value.get(key)}')

def execute(out,plan,rustc,fc,timeout):
    out=Path(out)
    if out.is_symlink():raise ValueError('batch output symlink refused')
    out=out.resolve();out.mkdir(parents=True,exist_ok=True)
    import fcntl
    with (out/'BATCH.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        identity=source_binding();fingerprint=hashlib.sha256(canonical(identity)).hexdigest()
        saved=out/'IDENTITY.json'
        if saved.exists():
            if json.loads(saved.read_text())!=identity:raise ValueError('batch source/runtime changed; use a new output')
        else:write_new(saved,identity)
        invocation_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'_'+uuid.uuid4().hex[:8]
        write_new(out/'invocations'/(invocation_id+'_PLAN.json'),dict(resource_plan=plan,inventory=inventory(plan)))
        work=out/'work';work.mkdir(exist_ok=True)
        records=[]
        def job(name,cmd,outputs,validator=None,limit=timeout):
            result=run_job(out,name,cmd,outputs,fingerprint,limit,validator)
            records.append(result)
            print(json.dumps(dict(job_id=name,status=result['status'],
                                  this_invocation=result['this_invocation'],wall_seconds=result['wall_seconds'])),flush=True)
            return result
        # Phase A: scalar reproduction and native build. Failures are isolated.
        budget=work/'SOURCE_BUDGET.json'
        job('source_budget',[sys.executable,HERE/'source_budget.py','--ell','64','--outer','44','--terms','1','--out',budget],[budget])
        p72=ROOT/'research/hh_phys72_20261020'
        for name,argv in [
          ('bounds',['--terms','3','--lambda-abs','1','--budget','1e-78','--frozen-npz',p72/'inputs/FROZEN_U_SUBSET.npz','--d3-certificate',p72/'inputs/ALL_ANGULAR_CERTIFICATE.json']),
          ('third_and_higher',['--input-root',p72/'inputs']),('angular_weights',[])]:
            target=work/('PHYS72_'+name+'.json')
            job('phys72_'+name,[sys.executable,p72/'implementation'/(name+'.py'),*argv,'--output',target],[target])
        native72=work/'phys72_native'
        job('phys72_native',[sys.executable,p72/'ncp_delivery/run_native.py','--fc',fc,'--out',native72],[native72/'EXECUTION.json',native72/'NATIVE_RESULT.json',native72/'EXACT_AUTHORITY.json'],limit=300)
        binary=work/'green_batch'
        compiler=shutil.which(rustc) or rustc
        version=job('rust_version',[compiler,'--version','--verbose'],[],limit=30)
        built=job('build_green',[compiler,'--edition=2021','-O','-C','target-cpu=x86-64',UNIT/'native/green_batch.rs','-o',binary],[binary],limit=300)
        # Phase B: all CPU resources available for independent Coulomb channels.
        source_outputs=[]
        if built['status']=='COMPLETE':
            for n in (257,513):
                directory=work/f'source_{n}'
                prepared=job(f'prepare_{n}',[sys.executable,HERE/'original_source.py','--out',directory,
                     '--lmax','64','--nodes',str(n),'--outer','44','--dps','60',
                     '--workers',str(plan['source_preparation_workers']),'--coulomb-cache',work/'coulomb_cache'],
                     [directory/'PREPARED.json',directory/'SOURCE_GREEN.bin',directory/'GRID.npz'])
                if prepared['status']!='COMPLETE':continue
                target=work/f'U_{n}.bin'
                acted=job(f'green_{n}',[binary,directory/'SOURCE_GREEN.bin',target,'--workers',str(plan['native_workers']),
                                      '--mode','sweep','--repeat','3'],[target],
                           validator=lambda directory=directory,target=target:check_green(directory,target))
                if acted['status']=='COMPLETE':source_outputs.append((directory,target))
            if len(source_outputs)==2:
                comparison=work/'GREEN_COMPARISON.json'
                job('green_comparison',[sys.executable,HERE/'verify_green.py','--prepared',source_outputs[0][0],
                    '--coarse',source_outputs[0][1],'--fine-prepared',source_outputs[1][0],
                    '--fine',source_outputs[1][1],'--out',comparison],[comparison])
                bench=work/'green_benchmark'
                job('green_benchmark',[sys.executable,HERE/'benchmark_green.py','--binary',binary,
                    '--input',source_outputs[0][0]/'SOURCE_GREEN.bin','--out',bench,
                    '--workers',str(plan['native_workers']),'--blocks','4','--repeat','3'],[bench/'REPORT.json',bench])
        # Phase C: disjoint scientific chains. Same old code/precision; no completed campaign replay.
        longtail=work/'phys66_longtail'
        validated=work/'validated_l64'
        def do_longtail():
            return job('phys66_longtail',[sys.executable,ROOT/'scripts/phys66_ncp.py','--profile','longtail',
                '--workers',str(plan['longtail_workers']),'--memory-gib','4','--timeout','900',
                '--resume','--out',longtail],[longtail/'CAMPAIGN_longtail.json',longtail/'SOURCE_RESULTS.zip'],
                validator=lambda:json_status(longtail/'CAMPAIGN_longtail.json','status',{'NUMERICAL_CASES_COMPLETE'}))
        def do_validated():
            return job('validated_l64',[sys.executable,HERE/'validated_l64.py','--out',validated,
                '--workers',str(plan['validated_workers']),'--worker-memory-gib','2','--run'],
                [validated/'CERTIFICATE.json',validated],
                validator=lambda:check_validated(validated/'CERTIFICATE.json'))
        if plan['legacy_parallel']:
            with ThreadPoolExecutor(max_workers=2) as pool:
                jobs=[pool.submit(do_longtail),pool.submit(do_validated)]
                for item in jobs:item.result()
        else:do_longtail();do_validated()
        final=dict(schema='PHYS73_NCP_BATCH_RESULT_V1',source_binding=identity,
                   fingerprint=fingerprint,resource_plan=plan,invocation_id=invocation_id,
                   status='COMPLETE' if all(r['status']=='COMPLETE' for r in records) else 'PARTIAL_FAILURE',
                   jobs=sorted(records,key=lambda r:r['job_id']),
                   completed_old_panel_integrations=0,completed_old_profile_integrations=0,
                   publication='NOT_PERFORMED_BY_RUNNER',backup='RESULT_ARTIFACTS_READY_ARCHIVE_PENDING',HH_R10='OFF')
        result_path=out/'invocations'/(invocation_id+'_RESULT.json')
        write_new(result_path,final)
        from return_capsule import pack_return
        backup=pack_return(out,ROOT,identity,invocation_id,result_path)
        return {**final,'backup':backup}

def check_green(directory,target):
    from original_source import summarize
    return summarize(directory,target)

def check_validated(path):
    c=json.loads(Path(path).read_text())
    if (c.get('schema')!='PHYS73_VALIDATED_L64_CERTIFICATE_V1'
            or c.get('status')!='CERTIFIED_GOALS_MET'
            or c.get('D1_goal_met') is not True or c.get('D2',{}).get('goal_met') is not True):
        raise ValueError('validated L64 goals or certificate schema not met')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--run',action='store_true')
    p.add_argument('--cpus',type=int,default=64)
    p.add_argument('--memory-gib',type=int,default=128)
    p.add_argument('--rustc',default='rustc')
    p.add_argument('--fc',default='gfortran')
    p.add_argument('--wall-seconds',type=int,default=86400)
    a=p.parse_args()
    if not 60<=a.wall_seconds<=172800:p.error('wall-seconds per job must be60..172800')
    if os.environ.get('HH_R10','OFF')!='OFF':p.error('HH_R10 must remain OFF')
    plan=resource_plan(a.cpus,a.memory_gib)
    if not a.run:
        print(json.dumps(dict(status='PLAN_ONLY_ZERO_SCIENTIFIC_EXECUTIONS',resource_plan=plan,
                              inventory=inventory(plan),HH_R10='OFF'),indent=2,sort_keys=True));return 0
    result=execute(a.out,plan,a.rustc,a.fc,a.wall_seconds)
    print(json.dumps(dict(status=result['status'],jobs=len(result['jobs']),backup=result['backup'],HH_R10='OFF'),indent=2))
    return 0 if result['status']=='COMPLETE' else 2

if __name__=='__main__':
    raise SystemExit(main())
