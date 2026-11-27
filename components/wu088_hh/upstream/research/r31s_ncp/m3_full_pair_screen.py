#!/usr/bin/env python3
"""Bounded same-host H0+foreign pair equality gate; no scientific assembly."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

for key in ('LD_PRELOAD', 'LD_LIBRARY_PATH'):
    os.environ.pop(key, None)
for key in ('OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
import numpy as np
from wu088_hh.native_candidate import ForeignKernel

COMPONENTS = ('H0', 'H0_sumabs', 'foreign', 'foreign_sumabs')
SAMPLES = {160: ((3, 7), (5, 11), (10, 11)),
           192: ((3, 7), (4, 10), (10, 11))}


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def full_pair(h0, foreign, d, t, W, gs, gw, pair, z=2.0):
    """Apply the pair arithmetic and normalization in wide_hybrid_run.py::pair."""
    i, j = pair
    a, b, q = float(d['exponents'][i]), float(d['exponents'][j]), float(d['v'])
    H0, H0sa = [], []
    for active in (0, 1):
        value, sumabs = h0.h0(a, b, t, W, z, q, active)
        H0.append(value)
        H0sa.append(sumabs)
    pars = np.array([a, b, z, q], dtype=np.float64)
    fv, fa = foreign(t, gs, gw, W[0], pars)
    norm0 = np.sqrt(2)*float(d['pref'])*(2*a/np.pi)**.75*(2*b/np.pi)**.75
    norm = norm0*np.array([[1, 2*np.sqrt(a), 2*np.sqrt(a)],
                           [1, 2*np.sqrt(b), 2*np.sqrt(b)]])
    fv *= norm[None]
    fa *= abs(norm[None])
    return {'H0': np.array(H0), 'H0_sumabs': np.array(H0sa),
            'foreign': fv, 'foreign_sumabs': fa}


def compare_full_pair(reference: dict, candidate: dict) -> dict:
    rows = {}
    for key in COMPONENTS:
        left, right = reference[key], candidate[key]
        rows[key] = {'exact': bool(np.array_equal(left, right)),
                     'shape': list(left.shape), 'dtype': str(left.dtype),
                     'max_abs_delta': float(np.max(np.abs(left-right)))}
    return {'components': rows, 'all_exact': all(v['exact'] for v in rows.values())}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--h0-cache', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    h0mod = load_module(ROOT/'research/r31s_ncp/authority_m3/m3_h0_authority.py', 'm3_h0_authority')
    seed = load_module(ROOT/'research/r31s_ncp/authority_seed/grid_seed.py', 'm3_grid_seed')
    seed.verify_authority()
    model = h0mod.inputs()
    built = json.loads(args.build.read_text())
    if built['identity']['flags'][-3:] != ['-fno-fast-math', '-ffp-contract=off', '-fopenmp']:
        raise RuntimeError('foreign build flags drift')
    h0 = h0mod.H0Authority(args.h0_cache)
    reference = ForeignKernel(Path(built['libraries']['reference']['path']))
    candidate = ForeignKernel(Path(built['libraries']['candidate']['path']))
    candidate.set_threads(1)
    affinity = sorted(os.sched_getaffinity(0))
    os.sched_setaffinity(0, {affinity[0]})
    rows = []
    for n, pairs in SAMPLES.items():
        d, t, W, gs, gw = seed.grid(n, 80)
        for key in ('C', 'exponents', 'v'):
            if not np.array_equal(np.asarray(d[key]), np.asarray(model[key])):
                raise RuntimeError('seed/full-model identity drift: '+key)
        d = model
        for pair in pairs:
            wall, cpu = time.perf_counter(), time.process_time()
            rv = full_pair(h0, reference, d, t, W, gs, gw, pair)
            ref_wall, ref_cpu = time.perf_counter()-wall, time.process_time()-cpu
            wall, cpu = time.perf_counter(), time.process_time()
            cv = full_pair(h0, candidate, d, t, W, gs, gw, pair)
            cand_wall, cand_cpu = time.perf_counter()-wall, time.process_time()-cpu
            check = compare_full_pair(rv, cv)
            row = {'n': n, 'g': 80, 'z': 2.0, 'pair': list(pair), **check,
                   'reference_wall_seconds': ref_wall, 'reference_cpu_seconds': ref_cpu,
                   'candidate_wall_seconds': cand_wall, 'candidate_cpu_seconds': cand_cpu,
                   'candidate_observed_team': candidate.observed_threads,
                   'observed_affinity': sorted(os.sched_getaffinity(0))}
            rows.append(row)
            print(json.dumps(row), flush=True)
            if not check['all_exact'] or row['candidate_observed_team'] != 1:
                raise RuntimeError('BLOCKED_M3_FULL_PAIR_EQUIVALENCE')
    result = {'schema': 'WU088_R31T_M3_FULL_PAIR_EQUIVALENCE_V1',
              'status': 'PASS_SAME_HOST_FULL_PAIR_EXACT_NOT_PRODUCTION',
              'rows': rows, 'all_exact': True,
              'h0_source_sha256': h0mod.verify_sources(),
              'h0_binary_sha256': h0.manifest['binary_sha256'],
              'foreign_build_key': built['build_key'],
              'grid_seed_sha256': hashlib.sha256(Path(seed.__file__).read_bytes()).hexdigest(),
              'full_144_pair_node_executed': False, 'production_admitted': False}
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
