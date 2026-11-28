#!/usr/bin/env python3
"""Bounded persistent-worker full-H0+foreign throughput screen; no assembly."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import importlib.util
import json
import multiprocessing as mp
import os
from pathlib import Path
import resource
import statistics
import sys
import time

for key in ('LD_PRELOAD', 'LD_LIBRARY_PATH'):
    os.environ.pop(key, None)
for key in ('OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
os.environ['OMP_DYNAMIC'] = 'FALSE'

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
import numpy as np
from wu088_hh.native_candidate import ForeignKernel
from wu088_hh.scheduler import predict_costs, verify_profile

STATE = None


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def select_pairs(costs: dict, count: int = 12) -> list[tuple[int, int]]:
    rows = sorted((float(v), tuple(k)) for k, v in costs.items())
    if count < 2 or len(rows) < count or any(not np.isfinite(v) or v <= 0 for v, _ in rows):
        raise ValueError('invalid cost profile or pair count')
    indices = [round(i*(len(rows)-1)/(count-1)) for i in range(count)]
    return [rows[i][1] for i in indices]


def affinity_groups(allowed: list[int], processes: int, threads: int) -> list[list[int]]:
    if processes < 1 or threads < 1 or processes*threads > len(allowed):
        raise ValueError('layout exceeds CPU budget')
    return [allowed[i*threads:(i+1)*threads] for i in range(processes)]


def memory_safe(processes: int, private_bytes: int, available_bytes: int) -> bool:
    return processes > 0 and private_bytes > 0 and available_bytes > 0 and 2*processes*private_bytes <= available_bytes


def measured_task_count(processes: int) -> int:
    if processes < 1:
        raise ValueError('processes must be positive')
    return max(24, 2*processes)


def smaps():
    try:
        lines = Path('/proc/self/smaps_rollup').read_text().splitlines()
    except FileNotFoundError:
        return {'rss_bytes': None, 'pss_bytes': None}
    vals = {}
    for line in lines:
        fields = line.split()
        if len(fields) == 3 and fields[0] in ('Rss:', 'Pss:') and fields[2] == 'kB':
            vals[fields[0][:-1]] = int(fields[1])*1024
    return {'rss_bytes': vals.get('Rss'), 'pss_bytes': vals.get('Pss')}


def cgroup_snapshot(path: Path):
    def number(name):
        p = path/name
        return int(p.read_text()) if p.exists() else None
    def kv(name):
        p = path/name
        return {k:int(v) for k,v in (line.split()[:2] for line in p.read_text().splitlines())} if p.exists() else None
    return {'cpu_stat':kv('cpu.stat'), 'memory_current':number('memory.current'),
            'memory_high':(path/'memory.high').read_text().strip() if (path/'memory.high').exists() else None,
            'memory_events':kv('memory.events'), 'memory_swap_current':number('memory.swap.current')}


def delta(a, b):
    if a is None or b is None:
        return None
    return {k:b[k]-v for k,v in a.items() if k in b}


def init_worker(groups, counter, lock, barrier, h0_cache, candidate_path, model, grid, n):
    global STATE
    with lock:
        slot = counter.value
        counter.value += 1
    if slot >= len(groups):
        raise RuntimeError('worker slot overflow')
    cpus = groups[slot]
    os.sched_setaffinity(0, set(cpus))
    h0mod = load_module(ROOT/'research/r31s_ncp/authority_m3/m3_h0_authority.py', 'm3_h0_worker')
    pairmod = load_module(ROOT/'research/r31s_ncp/m3_full_pair_screen.py', 'm3_pair_worker')
    h0 = h0mod.H0Authority(Path(h0_cache))
    foreign = ForeignKernel(Path(candidate_path))
    foreign.set_threads(len(cpus))
    STATE = (slot, cpus, h0, foreign, model, grid, n, pairmod, barrier)
    barrier.wait(timeout=240)


def worker(task):
    slot, planned, h0, foreign, model, grid, n, pairmod, _ = STATE
    faults_before = resource.getrusage(resource.RUSAGE_SELF).ru_majflt
    started = time.perf_counter(); cpu = time.process_time()
    result = pairmod.full_pair(h0, foreign, model, *grid, task)
    wall, cpu_seconds = time.perf_counter()-started, time.process_time()-cpu
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return {'pair':list(task), 'output':result, 'wall_seconds':wall, 'cpu_seconds':cpu_seconds,
            'pid':os.getpid(), 'slot':slot, 'team':foreign.observed_threads,
            'planned_affinity':planned, 'observed_affinity':sorted(os.sched_getaffinity(0)),
            **smaps(), 'major_faults':usage.ru_majflt,
            'major_faults_delta':usage.ru_majflt-faults_before}


def worker_info(_):
    slot, planned, _, _, _, _, _, _, barrier = STATE
    barrier.wait(timeout=240)
    return {'pid':os.getpid(), 'slot':slot, 'planned_affinity':planned,
            'observed_affinity':sorted(os.sched_getaffinity(0)), **smaps()}


def batch(pool, tasks, expected, groups, threads, cgpath):
    before = cgroup_snapshot(cgpath)
    wall = time.perf_counter()
    rows = list(pool.map(worker, tasks, chunksize=1))
    elapsed = time.perf_counter()-wall
    after = cgroup_snapshot(cgpath)
    exact = []
    for row in rows:
        check = expected['pairmod'].compare_full_pair(expected[tuple(row['pair'])], row['output'])
        exact.append(check['all_exact'])
        if not check['all_exact'] or row['team'] != threads or row['observed_affinity'] != groups[row['slot']]:
            raise RuntimeError('M3 task exactness, team, or affinity failed')
    latest = {r['pid']:r for r in rows}
    workers = {}
    for row in rows:
        pid = str(row['pid'])
        if pid not in workers:
            workers[pid] = {'pid':row['pid'], 'process_index':row['slot'],
                            'planned_affinity':row['planned_affinity'],
                            'observed_affinity':row['observed_affinity'],
                            'kernel_threads':threads, 'observed_openmp_team':row['team'],
                            'tasks_completed':0, 'cpu_seconds':0.0,
                            'major_faults_delta':0}
        workers[pid]['tasks_completed'] += 1
        workers[pid]['cpu_seconds'] += row['cpu_seconds']
        workers[pid]['major_faults_delta'] += row['major_faults_delta']
        workers[pid]['rss_bytes'] = row['rss_bytes']
        workers[pid]['pss_bytes'] = row['pss_bytes']
    rss = sum(r['rss_bytes'] for r in latest.values()) if all(r['rss_bytes'] is not None for r in latest.values()) else None
    pss = sum(r['pss_bytes'] for r in latest.values()) if all(r['pss_bytes'] is not None for r in latest.values()) else None
    cpu = sum(r['cpu_seconds'] for r in rows)
    cpu_delta = delta(before['cpu_stat'],after['cpu_stat'])
    cgroup_cpu = cpu_delta['usage_usec']/1e6 if cpu_delta and 'usage_usec' in cpu_delta else None
    counts = [w['tasks_completed'] for w in workers.values()]
    return {'tasks_completed':len(rows), 'batch_wall_seconds':elapsed,
            'steady_state_pairs_per_second':len(rows)/elapsed, 'cpu_seconds':cpu,
            'cpu_seconds_per_pair':cpu/len(rows), 'all_exact':all(exact),
            'processes':len(groups),'threads_per_process':threads,'logical_slots':len(groups)*threads,
            'unique_pair_count':len(set(tasks)), 'active_worker_count':len(workers),
            'worker_pids':sorted(int(pid) for pid in workers), 'workers':workers,
            'tasks_per_active_worker':{'min':min(counts),'median':statistics.median(counts),'max':max(counts)},
            'sum_worker_cpu_seconds':cpu,'worker_cpu_parallelism':cpu/elapsed,
            'cgroup_cpu_seconds':cgroup_cpu,
            'effective_cpu_parallelism':cgroup_cpu/elapsed if cgroup_cpu is not None else None,
            'observed_teams':sorted(set(r['team'] for r in rows)),
            'observed_affinities':sorted({tuple(r['observed_affinity']) for r in rows}),
            'worker_count_observed':len(latest), 'sum_rss_bytes':rss, 'sum_pss_bytes':pss,
            'cpu_stat_delta':cpu_delta,
            'nr_throttled_delta':cpu_delta.get('nr_throttled') if cpu_delta else None,
            'throttled_usec_delta':cpu_delta.get('throttled_usec') if cpu_delta else None,
            'memory_current_before':before['memory_current'], 'memory_current_after':after['memory_current'],
            'memory_high':after['memory_high'], 'memory_events_delta':delta(before['memory_events'],after['memory_events']),
            'swap_before':before['memory_swap_current'], 'swap_after':after['memory_swap_current'],
            'major_faults_delta':sum(r['major_faults_delta'] for r in rows),
            'major_faults_max_by_pid':{str(pid):r['major_faults'] for pid,r in latest.items()}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--stage', choices=('pilot', 'm3a', 'm3b'), required=True)
    ap.add_argument('--build', type=Path, required=True)
    ap.add_argument('--h0-cache', type=Path, required=True)
    ap.add_argument('--probe', type=Path, required=True)
    ap.add_argument('--configs', default='')
    ap.add_argument('--pilot-private', type=int)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    if args.stage=='m3b' and (args.pilot_private is None or args.pilot_private <= 0):
        raise ValueError('B192 pilot private-worker memory is required before M3B')
    probe = json.loads(args.probe.read_text())
    if probe['warnings'] or probe['planning_cpu_budget'] < 64 or len(probe['allowed_logical_cpus']) != 64:
        raise RuntimeError('M3 host drift')
    allowed = probe['allowed_logical_cpus']
    budget = probe['planning_cpu_budget']
    available = probe['cgroup']['memory_available_upper_bytes']
    cgpath = Path(probe['cgroup']['ancestors'][0]['path'])
    stage_n = 192 if args.stage in ('pilot','m3b') else 160
    h0mod = load_module(ROOT/'research/r31s_ncp/authority_m3/m3_h0_authority.py', 'm3_h0_main')
    seed = load_module(ROOT/'research/r31s_ncp/authority_seed/grid_seed.py', 'm3_seed_main')
    pairmod = load_module(ROOT/'research/r31s_ncp/m3_full_pair_screen.py', 'm3_pair_main')
    model = h0mod.inputs()
    grid_model,t,W,gs,gw = seed.grid(stage_n,80)
    for key in ('C','exponents','v'):
        if not np.array_equal(np.asarray(model[key]),np.asarray(grid_model[key])):
            raise RuntimeError('full model and grid seed drift')
    grid = (t,W,gs,gw)
    built = json.loads(args.build.read_text())
    if built['identity']['flags'][-3:] != ['-fno-fast-math','-ffp-contract=off','-fopenmp']:
        raise RuntimeError('strict foreign build flags absent')
    profile = json.loads((ROOT/'data/pair_cost_profile.json').read_text())
    verify_profile(profile, driver_sha=hashlib.sha256((ROOT/'vendor/orchestration/wide_hybrid_run.py').read_bytes()).hexdigest(),
                   model_sha=hashlib.sha256(h0mod.FROZEN.read_bytes()).hexdigest(), g=80, gamma_scale='unit')
    costs,prediction = predict_costs(profile,n=stage_n,z=2.0)
    pairs = select_pairs(costs,12)
    if args.stage == 'pilot':
        pairs = pairs[:1]
        configs = [(1,1)]
    else:
        configs = [tuple(map(int,item.split('x'))) for item in args.configs.split(',')]
        if not configs or len(configs)!=len(set(configs)):
            raise ValueError('explicit unique configurations required')
    reference_kernel = ForeignKernel(Path(built['libraries']['reference']['path']))
    h0 = h0mod.H0Authority(args.h0_cache)
    expected = {'pairmod':pairmod}
    reference_started = time.perf_counter()
    for pair in pairs:
        expected[pair] = pairmod.full_pair(h0,reference_kernel,model,*grid,pair)
    reference_seconds = time.perf_counter()-reference_started
    candidate_path = built['libraries']['candidate']['path']
    ctx = mp.get_context('spawn')
    result = {'schema':'WU088_R31T_M3_PERSISTENT_WORKER_SCREEN_V1','status':'IN_PROGRESS',
              'stage':args.stage,'n':stage_n,'g':80,'z':2.0,
              'pair_set':[list(p) for p in pairs],'pair_cost_prediction_scope':prediction,
              'pair_set_semantics':'PERFORMANCE_REPETITION_ONLY__NOT_NEW_SCIENTIFIC_PAIR_STATE',
              'reference_precompute_wall_seconds':reference_seconds,'configurations':[],
              'full_144_pair_node_executed':False,'production_admitted':False}
    pilot_private = None
    for processes,threads in configs:
        if processes*threads > budget:
            raise ValueError('configuration exceeds host budget')
        groups = affinity_groups(allowed,processes,threads)
        counter,lock,barrier = ctx.Value('i',0),ctx.Lock(),ctx.Barrier(processes)
        begin = time.perf_counter()
        with ProcessPoolExecutor(max_workers=processes,mp_context=ctx,initializer=init_worker,
                initargs=(groups,counter,lock,barrier,str(args.h0_cache),candidate_path,model,grid,stage_n)) as pool:
            infos = list(pool.map(worker_info,range(processes),chunksize=1))
            startup = time.perf_counter()-begin
            if len({r['pid'] for r in infos}) != processes or any(r['observed_affinity']!=groups[r['slot']] for r in infos):
                raise RuntimeError('pool startup affinity or worker count failed')
            private = max(max(r['pss_bytes'] or r['rss_bytes'] or 0 for r in infos),args.pilot_private or 0)
            if not memory_safe(processes,private,available):
                result['configurations'].append({'processes':processes,'threads':threads,'status':'SKIPPED_MEMORY_GATE','private_worker_bytes':private})
                continue
            warmup_tasks = [pairs[i%len(pairs)] for i in range(processes)]
            warmup = batch(pool,warmup_tasks,expected,groups,threads,cgpath)
            if args.stage == 'pilot':
                pilot_private = max((warmup['sum_pss_bytes'] or warmup['sum_rss_bytes'] or 0),private)
                measured=[]
            else:
                taskset = [pairs[i%len(pairs)] for i in range(measured_task_count(processes))]
                repetitions = 2 if args.stage=='m3a' else 3
                measured = [batch(pool,taskset,expected,groups,threads,cgpath) for _ in range(repetitions)]
                if processes >= 16:
                    for sample in measured:
                        sample['parallelism_engaged'] = (sample['active_worker_count'] >= max(8,int(.75*processes))
                              and sample['worker_cpu_parallelism'] > 4
                              and sample['effective_cpu_parallelism'] is not None
                              and sample['effective_cpu_parallelism'] > 4
                              and sample['nr_throttled_delta'] == 0)
                else:
                    for sample in measured:
                        sample['parallelism_engaged'] = None
            record = {'processes':processes,'threads_per_process':threads,'logical_slots':processes*threads,
                      'status':'PASS_EXACT_RESOURCE_GATES','pool_startup_seconds':startup,
                      'first_batch_wall_seconds':warmup['batch_wall_seconds'],
                      'warmup':warmup,'repetitions':measured,
                      'median_pairs_per_second':statistics.median(r['steady_state_pairs_per_second'] for r in measured) if measured else None,
                      'planned_affinity':groups,'startup_workers':infos,'private_worker_bytes':private,
                      'memory_gate_available_bytes':available,'memory_gate_pass':True}
            result['configurations'].append(record)
            print(json.dumps({'stage':args.stage,'configuration':[processes,threads],
                              'startup_seconds':startup,'warmup_seconds':warmup['batch_wall_seconds'],
                              'medians_pairs_per_second':record['median_pairs_per_second']}),flush=True)
        args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        if any(r.get('parallelism_engaged') is False for r in measured):
            result['status']='BLOCKED_M3_PARALLELISM_NOT_ENGAGED'
            args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
            raise RuntimeError('BLOCKED_M3_PARALLELISM_NOT_ENGAGED')
    result['status']='PASS_BOUNDED_PERSISTENT_WORKER_SCREEN'
    if args.stage=='pilot':
        result['pilot_private_worker_bytes']=pilot_private
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':
    main()
