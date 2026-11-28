#!/usr/bin/env python3
"""Bounded z=2 H-foreign same-host bridge; no full pair or provider promotion."""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import time

for key in ('LD_PRELOAD', 'LD_LIBRARY_PATH'):
    os.environ.pop(key, None)

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
import numpy as np
from wu088_hh.native_candidate import ForeignKernel
from wu088_hh.scheduler import predict_costs, verify_profile


def classify_pairs(costs: dict) -> list[tuple[str, tuple[int, int], float]]:
    if len(costs) < 3:
        raise ValueError('need cheap, median and expensive pair classes')
    rows = sorted((float(value), tuple(pair)) for pair, value in costs.items())
    if any(not math.isfinite(v) or v <= 0 for v, _ in rows):
        raise ValueError('invalid cost')
    return [(label, rows[i][1], rows[i][0]) for label, i in
            [('cheap', 0), ('median', len(rows)//2), ('expensive', len(rows)-1)]]


def exact_pair(reference: tuple, candidate: tuple) -> bool:
    return bool(np.array_equal(reference[0], candidate[0]) and
                np.array_equal(reference[1], candidate[1]))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    spec = importlib.util.spec_from_file_location('grid_seed', ROOT/'research/r31s_ncp/authority_seed/grid_seed.py')
    seed = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(seed)
    authority = seed.verify_authority()
    profile = json.loads((ROOT/'data/pair_cost_profile.json').read_text())
    import hashlib
    driver = ROOT/'vendor/orchestration/wide_hybrid_run.py'
    verify_profile(profile, driver_sha=hashlib.sha256(driver.read_bytes()).hexdigest(),
                   model_sha=authority['source_frozen_inputs_sha256'], g=80, gamma_scale='unit')
    built = json.loads(args.build.read_text())
    if tuple(built['identity']['flags'])[-3:] != ('-fno-fast-math', '-ffp-contract=off', '-fopenmp'):
        raise ValueError('strict build flags absent')
    reference = ForeignKernel(Path(built['libraries']['reference']['path']))
    candidate = ForeignKernel(Path(built['libraries']['candidate']['path']))
    candidate.set_threads(1)
    affinity = sorted(os.sched_getaffinity(0))
    if not affinity:
        raise RuntimeError('no allowed CPU')
    os.sched_setaffinity(0, {affinity[0]})
    rows = []
    for n in (160, 192):
        d, t, W, gs, gw = seed.grid(n, 80)
        costs, prediction = predict_costs(profile, n=n, z=2.0)
        for label, (i, j), predicted in classify_pairs(costs):
            pars = np.array([d['exponents'][i], d['exponents'][j], 2.0, d['v']], dtype=np.float64)
            inputs = (t, gs, gw, W[0], pars)
            wall = time.perf_counter(); cpu = time.process_time()
            rv, ra = reference(*inputs)
            reference_wall = time.perf_counter()-wall; reference_cpu = time.process_time()-cpu
            wall = time.perf_counter(); cpu = time.process_time()
            cv, ca = candidate(*inputs)
            candidate_wall = time.perf_counter()-wall; candidate_cpu = time.process_time()-cpu
            row = {'n': n, 'g': 80, 'z': 2.0, 'class': label, 'pair': [i, j],
                   'predicted_full_pair_cost_seconds': predicted,
                   'cost_prediction_source': prediction,
                   'output_exact': bool(np.array_equal(rv, cv)),
                   'sumabs_exact': bool(np.array_equal(ra, ca)),
                   'max_abs_output_delta': float(np.max(np.abs(rv-cv))),
                   'max_abs_sumabs_delta': float(np.max(np.abs(ra-ca))),
                   'output_dtype': str(rv.dtype), 'sumabs_dtype': str(ra.dtype),
                   'reference_wall_seconds': reference_wall, 'reference_cpu_seconds': reference_cpu,
                   'candidate_wall_seconds': candidate_wall, 'candidate_cpu_seconds': candidate_cpu,
                   'candidate_observed_team': candidate.observed_threads,
                   'observed_affinity': sorted(os.sched_getaffinity(0))}
            rows.append(row)
            print(json.dumps(row), flush=True)
            if not exact_pair((rv, ra), (cv, ca)) or candidate.observed_threads != 1:
                raise RuntimeError('same-host exactness or OpenMP team failed')
    result = {'schema': 'WU088_R31S_NCP_M2_EQUIVALENCE_V1',
              'status': 'PASS_BOUNDED_FOREIGN_ONLY_NOT_PROMOTED',
              'authority': authority, 'build_key': built['build_key'],
              'rows': rows, 'full_144_pair_node_executed': False,
              'production_admitted': False, 'selected_configuration': None}
    with args.out.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
