#!/usr/bin/env python3
"""Run optimized analytic-root SDIRK2 matrix and verify science parity."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np
import pandas as pd

STAGE = Path(__file__).resolve().parents[1]
REPO = STAGE.parents[1]
ATTEMPT = STAGE / 'attempts/ATTEMPT_3_ANALYTIC_THERMAL_NEWTON_OPTIMIZATION'
REFERENCE_ATTEMPT = STAGE / 'attempts/ATTEMPT_1_MPRK22_ALPHA1_LSTABLE_SDIRK2_THERMAL'
PARITY_REFERENCE = 'ATTEMPT_1_MPRK22_ALPHA1_LSTABLE_SDIRK2_THERMAL'
LANES = (
    'LOCAL_NEUTRAL_HAZARD_PRIMARY',
    'RECOMBINATION_WEIGHTED_AUDITOR',
    'SCRIPT_SELF_SHIELDING_AUDITOR',
)
PARTITIONS = (512, 1024, 2048)
LOCAL_ERROR_TOL = 2.0e-4
SCIENCE_PARITY_TOL = 1.0e-10
CANDIDATE_METHOD = 'NONAUTONOMOUS_MPRK22_ALPHA1_PLUS_LSTABLE_ALEXANDER_SDIRK2_ANALYTIC_ROOT'


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def classify(rows: list[dict[str, Any]]) -> dict[str, Any]:
    lane_pass: dict[str, bool] = {}
    for lane in LANES:
        candidates = [
            row for row in rows
            if row['lane'] == lane and int(row['partition']) in (1024, 2048)
        ]
        lane_pass[lane] = any(
            bool(row['candidate_converged'])
            and bool(row['all_gates_pass'])
            and row['local_error'] is not None
            and float(row['local_error']) < LOCAL_ERROR_TOL
            for row in candidates
        )
    return {'lane_pass': lane_pass, 'science_pass': all(lane_pass.values())}


def block_errors(full, half) -> dict[str, float]:
    a = full.values
    b = half.values
    nh = a[0] + a[1]
    nhe = a[2] + a[3] + a[4]
    return {
        'x_HII': float(np.max(np.abs(a[1] / nh - b[1] / nh))),
        'x_HeII': float(np.max(np.abs(a[3] / nhe - b[3] / nhe))),
        'x_HeIII': float(np.max(np.abs(a[4] / nhe - b[4] / nhe))),
        'log_T': float(np.max(np.abs(np.log(full.temperature_K) - np.log(half.temperature_K)))),
    }


def trial_gates(*trials) -> tuple[bool, dict[str, float]]:
    metrics = {
        'max_H_residual': max(t.hydrogen_residual for t in trials),
        'max_He_residual': max(t.helium_residual for t in trials),
        'max_owner_residual': max(t.owner_residual for t in trials),
        'max_photon_residual': max(t.photon_residual for t in trials),
        'max_thermal_residual': max(t.thermal_residual for t in trials),
        'max_PDS_residual': max(t.pds_reconstruction_residual for t in trials),
        'minimum_species': min(t.minimum_species for t in trials),
    }
    passed = (
        all(t.converged for t in trials)
        and metrics['max_H_residual'] <= 1.0e-11
        and metrics['max_He_residual'] <= 1.0e-11
        and metrics['max_owner_residual'] <= 1.0e-11
        and metrics['max_photon_residual'] <= 1.0e-8
        and metrics['max_thermal_residual'] <= 1.0e-10
        and metrics['max_PDS_residual'] <= 1.0e-11
        and metrics['minimum_species'] > 0.0
    )
    return passed, metrics


def candidate_rows() -> list[dict[str, Any]]:
    trialmod = _load(
        'r2b_r2a_r1_fast_preflight_trial',
        STAGE / 'analysis/second_order_sdirk_fast_trial.py',
    )
    rows: list[dict[str, Any]] = []
    for lane in LANES:
        solver = trialmod.SecondOrderSDIRKFastTrial.from_repo(repo_root=REPO, lane=lane)
        parent = solver.inputs.state0.mutable_copy()
        duration = solver.forcing.duration_seconds(0)
        parent_bytes = (parent.values.tobytes(), parent.temperature_K.tobytes())
        for partition in PARTITIONS:
            t0 = 0.0
            t1 = duration / partition
            mid = 0.5 * t1
            started = time.perf_counter()
            full = solver.solve(state=parent, t0=t0, t1=t1, partition=partition, trial_kind='FULL')
            half1 = solver.solve(state=parent, t0=t0, t1=mid, partition=2 * partition, trial_kind='FIRST_HALF')
            half2 = (
                solver.solve(state=half1.state, t0=mid, t1=t1, partition=2 * partition, trial_kind='SECOND_HALF')
                if half1.converged else half1
            )
            elapsed = time.perf_counter() - started
            converged = full.converged and half1.converged and half2.converged
            errors = (
                block_errors(full.state, half2.state)
                if converged
                else {key: None for key in ('x_HII', 'x_HeII', 'x_HeIII', 'log_T')}
            )
            local_error = (
                max(value for value in errors.values() if value is not None)
                if converged else None
            )
            gates, metrics = trial_gates(full, half1, half2)
            rows.append({
                'lane': lane,
                'partition': partition,
                'candidate_converged': converged,
                'local_error': local_error,
                'passes_local_error': bool(local_error is not None and local_error < LOCAL_ERROR_TOL),
                'all_gates_pass': gates,
                'elapsed_s': elapsed,
                **{f'error_{key}': value for key, value in errors.items()},
                **metrics,
                'full_certificate': json.dumps(full.certificate, sort_keys=True),
                'half1_certificate': json.dumps(half1.certificate, sort_keys=True),
                'half2_certificate': json.dumps(half2.certificate, sort_keys=True),
            })
            if parent_bytes != (parent.values.tobytes(), parent.temperature_K.tobytes()):
                raise RuntimeError('optimized candidate trials mutated the parent state')
    return rows


def parity_against_reference(rows: list[dict[str, Any]]) -> dict[str, Any]:
    reference = json.loads((REFERENCE_ATTEMPT / 'results.json').read_text(encoding='utf-8'))
    ref = {(r['lane'], int(r['partition'])): r for r in reference['rows']}
    maximum = 0.0
    fields = ('local_error', 'error_x_HII', 'error_x_HeII', 'error_x_HeIII', 'error_log_T')
    per_row: list[dict[str, Any]] = []
    for row in rows:
        key = (row['lane'], int(row['partition']))
        other = ref[key]
        differences = {}
        for field in fields:
            a = float(row[field])
            b = float(other[field])
            diff = abs(a - b)
            differences[field] = diff
            maximum = max(maximum, diff)
        per_row.append({'lane': key[0], 'partition': key[1], **differences})
    return {
        'reference': PARITY_REFERENCE,
        'maximum_absolute_science_metric_difference': maximum,
        'tolerance': SCIENCE_PARITY_TOL,
        'pass': maximum <= SCIENCE_PARITY_TOL,
        'rows': per_row,
    }


def main() -> int:
    argparse.ArgumentParser().parse_args()
    rows = candidate_rows()
    disposition = classify(rows)
    parity = parity_against_reference(rows)
    ATTEMPT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(ATTEMPT / 'optimized_preflight_results.csv', index=False)
    result = {
        'classification': 'R2B_R2A_R1_ATTEMPT_3_ANALYTIC_ROOT_OPTIMIZATION',
        'candidate_method': CANDIDATE_METHOD,
        'partitions': list(PARTITIONS),
        'rows': rows,
        'science_parity': parity,
        **disposition,
        'performance_promotion_pending': True,
        'production_history_integrated': False,
    }
    (ATTEMPT / 'results.json').write_text(
        json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8'
    )
    print(json.dumps({
        'science_pass': disposition['science_pass'],
        'science_parity_pass': parity['pass'],
        'maximum_science_metric_difference': parity['maximum_absolute_science_metric_difference'],
        'lane_pass': disposition['lane_pass'],
        'elapsed_s': {f"{r['lane']}:{r['partition']}": r['elapsed_s'] for r in rows},
    }, indent=2, sort_keys=True))
    return 0 if disposition['science_pass'] and parity['pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
