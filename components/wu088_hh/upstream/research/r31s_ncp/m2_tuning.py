#!/usr/bin/env python3
"""Bounded seed-grid component layout screen; never select production settings."""
from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing as mp
import os
from pathlib import Path
import resource
import sys
import time
from concurrent.futures import ProcessPoolExecutor

for key in ('LD_PRELOAD', 'LD_LIBRARY_PATH'):
    os.environ.pop(key, None)
for key in ('OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'OMP_NUM_THREADS'):
    os.environ[key] = '1'
os.environ['OMP_DYNAMIC'] = 'FALSE'

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
import numpy as np
from wu088_hh.native_candidate import ForeignKernel

_BARRIER = None


def init_barrier(barrier):
    global _BARRIER
    _BARRIER = barrier


def barrier_probe(value):
    _BARRIER.wait(timeout=30)
    return value


def legal_configurations(budget: int) -> list[tuple[int, int]]:
    if not isinstance(budget, int) or budget < 1:
        raise ValueError('invalid CPU budget')
    cap = 1 << (budget.bit_length()-1)
    out = []
    for slots in dict.fromkeys((cap, max(1, cap//2))):
        threads = 1
        while threads <= slots:
            out.append((slots//threads, threads))
            threads *= 2
    return out


def memory_safe(processes: int, private_bytes: int, available_bytes: int) -> bool:
    return (processes > 0 and private_bytes > 0 and available_bytes > 0 and
            2*processes*private_bytes <= available_bytes)


def _read_number(path: Path):
    try:
        return int(path.read_text().strip())
    except (FileNotFoundError, ValueError):
        return None


def _read_kv(path: Path):
    try:
        return {k: int(v) for k, v in (line.split()[:2] for line in path.read_text().splitlines())}
    except (FileNotFoundError, ValueError):
        return None


def cgroup_snapshot(path: Path) -> dict:
    return {'cpu_stat': _read_kv(path/'cpu.stat'),
            'memory_current': _read_number(path/'memory.current'),
            'memory_high': (path/'memory.high').read_text().strip() if (path/'memory.high').exists() else None,
            'memory_events': _read_kv(path/'memory.events'),
            'memory_swap_current': _read_number(path/'memory.swap.current')}


def _delta(before, after):
    if before is None or after is None:
        return None
    return {k: after[k]-v for k, v in before.items() if k in after}


def _smaps():
    try:
        lines = Path('/proc/self/smaps_rollup').read_text().splitlines()
    except FileNotFoundError:
        return {'rss_bytes': None, 'pss_bytes': None}
    rows = {}
    for line in lines:
        fields = line.split()
        if len(fields) == 3 and fields[0] in ('Rss:', 'Pss:') and fields[2] == 'kB':
            rows[fields[0][:-1]] = int(fields[1])*1024
    return {'rss_bytes': rows.get('Rss'), 'pss_bytes': rows.get('Pss')}


def worker(task):
    path, threads, cpus, grid, pars = task
    os.sched_setaffinity(0, set(cpus))
    kernel = ForeignKernel(Path(path))
    kernel.set_threads(threads)
    _BARRIER.wait(timeout=120)
    started = time.perf_counter(); cpu = time.process_time()
    output, sumabs = kernel(*grid, pars)
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return {'output': output, 'sumabs': sumabs,
            'wall_seconds': time.perf_counter()-started,
            'cpu_seconds': time.process_time()-cpu,
            'observed_team': kernel.observed_threads,
            'observed_affinity': sorted(os.sched_getaffinity(0)),
            'rss_bytes': _smaps()['rss_bytes'], 'pss_bytes': _smaps()['pss_bytes'],
            'major_faults': usage.ru_majflt}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build', type=Path, required=True)
    ap.add_argument('--probe', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--repeats', type=int, default=3)
    args = ap.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    if not 1 <= args.repeats <= 3:
        raise ValueError('repeats must be 1..3')
    spec = importlib.util.spec_from_file_location('grid_seed', ROOT/'research/r31s_ncp/authority_seed/grid_seed.py')
    seed = importlib.util.module_from_spec(spec); spec.loader.exec_module(seed)
    authority = seed.verify_authority()
    probe_spec = importlib.util.spec_from_file_location('ncp_probe', ROOT/'research/r31s_ncp/probe/ncp_probe.py')
    probe_module = importlib.util.module_from_spec(probe_spec); probe_spec.loader.exec_module(probe_module)
    original = json.loads(args.probe.read_text())
    current = probe_module.probe(ROOT)
    if current['warnings'] or current['status'] != 'PROBED_NOT_BENCHMARKED':
        raise RuntimeError('current cgroup mapping ambiguous')
    if current['allowed_logical_cpus'] != original['allowed_logical_cpus']:
        raise RuntimeError('affinity changed since ingested probe')
    budget = min(current['planning_cpu_budget'], original['planning_cpu_budget'])
    allowed = current['allowed_logical_cpus'][:budget]
    cgpath = Path(current['cgroup']['ancestors'][0]['path'])
    built = json.loads(args.build.read_text())
    d, t, W, gs, gw = seed.grid(32, 20)
    pars = np.array([d['exponents'][3], d['exponents'][7], 2.0, d['v']], dtype=np.float64)
    grid = (t, gs, gw, W[0])
    ref = ForeignKernel(Path(built['libraries']['reference']['path']))
    reference_output, reference_sumabs = ref(*grid, pars)
    configurations = legal_configurations(budget)
    rows = []
    ctx = mp.get_context('spawn')
    pilot_barrier = ctx.Barrier(1)
    pilot_task = (built['libraries']['candidate']['path'], 1, [allowed[0]], grid, pars)
    with ProcessPoolExecutor(max_workers=1, mp_context=ctx,
                             initializer=init_barrier, initargs=(pilot_barrier,)) as pool:
        pilot = pool.submit(worker, pilot_task).result()
    pilot_private = pilot['pss_bytes'] or pilot['rss_bytes']
    available_memory = current['cgroup']['memory_available_upper_bytes']
    if pilot_private is None or not memory_safe(max(p for p, _ in configurations), pilot_private, available_memory):
        raise RuntimeError('pilot memory estimate exceeds observed available memory')
    for rep in range(args.repeats):
        order = configurations[rep % len(configurations):] + configurations[:rep % len(configurations)]
        for processes, threads in order:
            slots = processes*threads
            groups = [allowed[i*threads:(i+1)*threads] for i in range(processes)]
            if any(len(g) != threads for g in groups) or slots > budget:
                raise RuntimeError('invalid affinity partition')
            barrier = ctx.Barrier(processes)
            tasks = [(built['libraries']['candidate']['path'], threads, group, grid, pars)
                     for group in groups]
            before = cgroup_snapshot(cgpath)
            t0 = time.perf_counter()
            with ProcessPoolExecutor(max_workers=processes, mp_context=ctx,
                                     initializer=init_barrier, initargs=(barrier,)) as pool:
                results = list(pool.map(worker, tasks, chunksize=1))
            wall = time.perf_counter()-t0
            after = cgroup_snapshot(cgpath)
            exact = all(np.array_equal(r['output'], reference_output) and
                        np.array_equal(r['sumabs'], reference_sumabs) for r in results)
            valid = all(r['observed_team'] == threads and r['observed_affinity'] == groups[i]
                        for i, r in enumerate(results))
            row = {'repetition': rep, 'processes': processes, 'kernel_threads': threads,
                   'logical_slots': slots, 'batch_wall_seconds': wall,
                   'sum_worker_cpu_seconds': sum(r['cpu_seconds'] for r in results),
                   'max_worker_wall_seconds': max(r['wall_seconds'] for r in results),
                   'observed_teams': sorted({r['observed_team'] for r in results}),
                   'planned_affinity_groups': groups,
                   'observed_affinity_groups': [r['observed_affinity'] for r in results],
                   'output_and_sumabs_exact': bool(exact), 'team_and_affinity_valid': bool(valid),
                   'sum_rss_bytes': sum(r['rss_bytes'] for r in results) if all(r['rss_bytes'] is not None for r in results) else None,
                   'sum_pss_bytes': sum(r['pss_bytes'] for r in results) if all(r['pss_bytes'] is not None for r in results) else None,
                   'major_faults': sum(r['major_faults'] for r in results),
                   'cgroup_cpu_stat_delta': _delta(before['cpu_stat'], after['cpu_stat']),
                   'memory_current_before': before['memory_current'],
                   'memory_current_after': after['memory_current'],
                   'memory_high': after['memory_high'],
                   'memory_events_delta': _delta(before['memory_events'], after['memory_events']),
                   'swap_current_before': before['memory_swap_current'],
                   'swap_current_after': after['memory_swap_current']}
            rows.append(row)
            print(json.dumps({k: v for k, v in row.items() if k not in ('planned_affinity_groups', 'observed_affinity_groups')}), flush=True)
            if not exact or not valid:
                raise RuntimeError('candidate exactness/team/affinity failed')
    result = {'schema': 'WU088_R31S_NCP_M2_TUNING_V1',
              'status': 'BOUNDED_COMPONENT_SCREEN_NOT_SELECTED',
              'workload': {'n': 32, 'g': 20, 'z': 2.0, 'pair': [3, 7],
                           'one_identical_primitive_per_process': True,
                           'not_full_science_resolution': True},
              'authority': authority, 'build_key': built['build_key'],
              'effective_budget': budget, 'candidate_order': configurations,
              'allowed_logical_cpus': allowed, 'cgroup_measurement_path': str(cgpath),
              'pilot_worker_pss_bytes': pilot['pss_bytes'],
              'pilot_worker_rss_bytes': pilot['rss_bytes'],
              'memory_available_upper_bytes': available_memory,
              'rows': rows, 'selected_configuration': None,
              'production_admitted': False}
    with args.out.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
