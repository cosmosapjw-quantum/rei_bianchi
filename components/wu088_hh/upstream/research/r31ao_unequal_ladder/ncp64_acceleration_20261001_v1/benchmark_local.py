"""Bounded real integer CPU work. Measures local executor only, not MPI or NCP."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import platform
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE/'host_plan'))
import planner


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cpu-units', type=int, default=500000)
    args = parser.parse_args()
    if not args.output.is_absolute() or args.output.exists() or not args.output.parent.is_dir():
        parser.error('new absolute output directory required')
    host = planner.detect()
    capacity = planner.plan(host, reserve_bytes=0, worker_bytes=256*1024**2, coordinator_bytes=256*1024**2)
    if capacity['status'] != 'PLAN_READY' or capacity['cpu_budget'] < 4 or capacity['job_memory_budget_bytes'] < 1280*1024**2:
        parser.error('bounded four-worker benchmark needs four allowed CPUs and 1.25 GiB remaining')
    args.output.mkdir(mode=0o700)
    report = {'schema':'WU088_LOCAL_INTEGER_CPU_BENCHMARK_V1', 'status':'INCOMPLETE',
              'host':host, 'benchmark_resource_plan':capacity, 'python':sys.version,
              'platform':platform.platform(), 'runs':[], 'NCP_measured':False,
              'MPI_executed':False, 'native_cache_executed':False, 'actual_HH_runs':0,
              'workload':'16 uneven exact integer sum-of-squares subprocess tasks; closed-form expected output hash per task',
              'timing_scope':'fresh run_local process including worker spawn, hash verification, exact payload collection; fixture creation excluded'}
    report['source_sha256']={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted((HERE/'executor').glob('*.py'))}
    try:
        # Rotate run order to expose warm-up/order effects instead of always timing serial first.
        for repetition, order in enumerate(((1,2,4),(4,1,2),(2,4,1)),1):
            for workers in order:
                tag=f'r{repetition}_w{workers}'
                manifest=args.output/(tag+'.json')
                env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
                fixture=subprocess.run([sys.executable,'-B',str(HERE/'executor/make_fixture.py'),
                    '--output-manifest',str(manifest),'--output-root',str(args.output/(tag+'_tasks')),
                    '--task-count','16','--cpu-units',str(args.cpu_units)],env=env,capture_output=True,text=True,timeout=10)
                if fixture.returncode:raise ValueError('fixture failed: '+fixture.stderr[:1000])
                start=time.monotonic()
                run=subprocess.run([sys.executable,'-B',str(HERE/'executor/run_local.py'),
                    '--manifest',str(manifest),'--workers',str(workers)],env=env,capture_output=True,text=True,timeout=60)
                wall=time.monotonic()-start
                (args.output/(tag+'.stdout')).write_text(run.stdout)
                (args.output/(tag+'.stderr')).write_text(run.stderr)
                value=json.loads(run.stdout)
                if run.returncode or value['status']!='COLLECTED' or value['complete_task_count']!=16:
                    raise ValueError('execution failed at '+tag+': '+str(value)[:1000])
                report['runs'].append({'repetition':repetition,'workers':workers,'wall_seconds':wall,
                    'executor_wall_seconds':value['local_execution']['wall_seconds'],
                    'canonical_payload_digest':value['canonical_payload_digest'],
                    'complete_task_count':value['complete_task_count']})
        if len({x['canonical_payload_digest'] for x in report['runs']})!=1:
            raise ValueError('payload identities differ across worker counts/repetitions')
        # Recheck retained runs after all measurements; late/stale records are
        # not accepted solely because an earlier collector returned success.
        for run in report['runs']:
            tag=f"r{run['repetition']}_w{run['workers']}"
            checked=subprocess.run([sys.executable,'-B',str(HERE/'executor/collect.py'),
                '--manifest',str(args.output/(tag+'.json'))],env=env,capture_output=True,text=True,timeout=15)
            value=json.loads(checked.stdout)
            if checked.returncode or value.get('canonical_payload_digest')!=run['canonical_payload_digest']:
                raise ValueError('final retained collection check failed: '+tag)
        if any(hashlib.sha256((HERE/name).read_bytes()).hexdigest()!=digest
               for name,digest in report['source_sha256'].items()):
            raise ValueError('executor source changed during measurement')
        medians={str(w):statistics.median(x['wall_seconds'] for x in report['runs'] if x['workers']==w) for w in (1,2,4)}
        report.update(status='PASS_LOCAL_EXACT_PAYLOAD_BENCHMARK', median_wall_seconds=medians,
                      speedup_vs_one_worker={w:medians['1']/t for w,t in medians.items()},
                      final_retained_collections_reverified=True,
                      extrapolation_to_NCP_or_native_kernel_permitted=False)
    except (OSError,ValueError,KeyError,subprocess.TimeoutExpired) as exc:
        report.update(status='INCONCLUSIVE', reason=str(exc))
    (args.output/'BENCHMARK.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('host','runs','benchmark_resource_plan')},indent=2))
    return 0 if report['status']=='PASS_LOCAL_EXACT_PAYLOAD_BENCHMARK' else 2


if __name__=='__main__':
    raise SystemExit(main())
