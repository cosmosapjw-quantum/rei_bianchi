"""New manufactured problem only. No REI source, atomic or native provider calls.

N'=s_N-k N, U'=s_E-(k+lambda)U; positive absorption, emission and
expansion-work counters provide linear number/energy ledgers. A fresh BDF is
started at every natural boundary in both control and split paths.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from atomic_checkpoint import CheckpointError, load_generation, publish_generation

N0, U0, SN, SE, K, LAMBDA = 2.0, 5.0, 0.3, 0.8, 0.7, 0.2
EDGES = np.linspace(0.0, 1.0, 5)
SCHEDULE = np.linspace(0.0, 1.0, 17)
FIELDS = ['N', 'U', 'emitted_N', 'absorbed_N', 'emitted_E', 'absorbed_E', 'work_E']


def _hash_bytes(data): return hashlib.sha256(data).hexdigest()


def identities():
    return {
        'source': _hash_bytes(b'MANUFACTURED s_N=0.3 s_E=0.8 k=0.7 lambda=0.2'),
        'grid': _hash_bytes(EDGES.tobytes() + SCHEDULE.tobytes()),
        'binary': _hash_bytes(b'NO_NATIVE_BINARY_MANUFACTURED_ONLY'),
        'control': _hash_bytes(Path(__file__).with_name('atomic_checkpoint.py').read_bytes()),
        'physics_contract': _hash_bytes(b'MANUFACTURED_DIMENSIONLESS_NOT_Q1B_PHYSICAL_PROVIDER'),
        'physical_validator': _hash_bytes(Path(__file__).read_bytes()),
    }


def analytic(clock):
    t = np.atleast_1d(clock)
    n = SN / K + (N0 - SN / K) * np.exp(-K * t)
    u = SE / (K + LAMBDA) + (U0 - SE / (K + LAMBDA)) * np.exp(-(K + LAMBDA) * t)
    int_u = SE / (K + LAMBDA) * t + (U0 - SE / (K + LAMBDA)) * (-np.expm1(-(K + LAMBDA) * t)) / (K + LAMBDA)
    return np.column_stack((n, u, SN*t, SN*t + N0 - n, SE*t, K*int_u, LAMBDA*int_u))


def rhs(clock, y):
    n, u = y[:2]
    return np.array([SN-K*n, SE-(K+LAMBDA)*u, SN, K*n, SE, K*u, LAMBDA*u])


def ledger(states):
    y = np.atleast_2d(states)
    return {
        'number': float(np.max(np.abs(y[:,0] - N0 - y[:,2] + y[:,3])) / N0),
        'energy': float(np.max(np.abs(y[:,1] - U0 - y[:,4] + y[:,5] + y[:,6])) / U0),
    }


def manufactured_validator(arrays, metadata):
    # The library validates serialization, shapes and sequencing first.
    # This callback checks only this explicit manufactured model.
    if metadata['physical_binding'] != 'MANUFACTURED_FIXTURE_ONLY_UNBOUND':
        raise CheckpointError('Fixture validator cannot bind production physics')
    if metadata != _metadata(metadata['completed_segments'], metadata['ledger_max']):
        raise CheckpointError('Manufactured metadata/control contract changed')
    if not np.array_equal(arrays['segment_edges'], EDGES) or not np.array_equal(arrays['scheduled_clock'], SCHEDULE):
        raise CheckpointError('Manufactured grid/schedule changed')
    if not np.array_equal(arrays['scales'], np.array([N0,U0,1.,1.,1.,1.,1.])):
        raise CheckpointError('Manufactured scales changed')
    if np.any(arrays['accepted_min'] < 0):
        raise CheckpointError('Manufactured accepted history contains a negative state')
    required = ledger(np.vstack((arrays['prefix_state'], arrays['state'])))
    for key in required:
        if metadata['ledger_max'][key] < required[key] or metadata['ledger_max'][key] >= 1e-9:
            raise CheckpointError('Manufactured preserved ledger insufficient or outside bound')
    if metadata['ledger_origins'] != {'number': N0, 'energy': U0}:
        raise CheckpointError('Manufactured ledger normalization changed')
    if not np.array_equal(arrays['prefix_state'][0], analytic(0.0)[0]):
        raise CheckpointError('Manufactured initial state changed')
    return {'scope': 'NEW_MANUFACTURED_FIXTURE_ONLY', 'domain_checked': True,
            'ledgers_checked': True, 'production_provider_binding': False}


def _metadata(completed, maxima):
    return {
        'state_fields': FIELDS,
        'state_units': ['dimensionless_N','dimensionless_E'] + ['dimensionless_counter'] * 5,
        'counter_indices': [2,3,4,5,6],
        'current_clock': float(EDGES[completed]),
        'completed_segments': completed, 'next_segment_index': completed,
        'next_segment': None if completed == len(EDGES)-1 else EDGES[completed:completed+2].tolist(),
        'accepted_domain_flags': {'finite': True, 'nonnegative': True},
        'ledger_max': maxima,
        'ledger_origins': {'number': N0, 'energy': U0},
        'restart_kind': 'FRESH_BDF_AT_NATURAL_SEGMENT_BOUNDARY',
        'physical_binding': 'MANUFACTURED_FIXTURE_ONLY_UNBOUND',
        'solver': {'method':'BDF', 'rtol':2e-13, 'atol':1e-14,
                   'fresh_initialization_at_each_segment':True},
    }


def make_snapshot():
    """Exact analytic snapshot at t=0.5 for byte/schema corruption tests."""
    prefix = SCHEDULE[SCHEDULE <= 0.5]; history = analytic(prefix)
    arrays = {'state': history[-1].copy(), 'scales': np.array([N0,U0,1.,1.,1.,1.,1.]),
              'counter_origins': np.zeros(5), 'prefix_clock': prefix.copy(),
              'prefix_state': history.copy(), 'scheduled_clock': SCHEDULE.copy(),
              'segment_edges': EDGES.copy(), 'accepted_min': history.min(axis=0),
              'accepted_max': history.max(axis=0)}
    return arrays, _metadata(2, ledger(history))


def initial_snapshot():
    initial = analytic(0.0)[0]
    arrays = {'state': initial.copy(), 'scales': np.array([N0,U0,1.,1.,1.,1.,1.]),
              'counter_origins': np.zeros(5), 'prefix_clock': SCHEDULE[:1].copy(),
              'prefix_state': initial[None,:].copy(), 'scheduled_clock': SCHEDULE.copy(),
              'segment_edges': EDGES.copy(), 'accepted_min': initial.copy(),
              'accepted_max': initial.copy()}
    return arrays, _metadata(0, ledger(initial))


def advance(arrays, meta, end_segment):
    arrays = {key:value.copy() for key,value in arrays.items()}
    for i in range(meta['completed_segments'], end_segment):
        sol = solve_ivp(rhs, EDGES[i:i+2], arrays['state'], method='BDF',
                        rtol=2e-13, atol=1e-14, dense_output=True)
        if not sol.success: raise RuntimeError(sol.message)
        sample = SCHEDULE[(SCHEDULE > EDGES[i]) & (SCHEDULE <= EDGES[i+1])]
        states = sol.sol(sample).T
        # Endpoint is the accepted state, not an independent interpolant.
        if sample[-1] == EDGES[i+1]: states[-1] = sol.y[:,-1]
        arrays['state'] = sol.y[:,-1].copy()
        arrays['prefix_clock'] = np.concatenate((arrays['prefix_clock'], sample))
        arrays['prefix_state'] = np.vstack((arrays['prefix_state'], states))
        all_new = np.vstack((sol.y.T, states))
        arrays['accepted_min'] = np.minimum(arrays['accepted_min'], all_new.min(axis=0))
        arrays['accepted_max'] = np.maximum(arrays['accepted_max'], all_new.max(axis=0))
        new_ledger = ledger(all_new)
        maxima = {key:max(meta['ledger_max'][key],new_ledger[key]) for key in new_ledger}
        meta = _metadata(i+1, maxima)
    return arrays, meta


def split_trial(root):
    full_a, full_m = advance(*initial_snapshot(), end_segment=4)
    first_a, first_m = advance(*initial_snapshot(), end_segment=2)
    path = publish_generation(root, 10, first_a, first_m, identities(), manufactured_validator)
    restored = load_generation(root, 10, identities(), manufactured_validator,
                               expected_manifest_sha256=_hash_bytes((path/'manifest.json').read_bytes()))
    equal_restore = restored['metadata'] == first_m and all(
        np.array_equal(first_a[key], restored['arrays'][key]) for key in first_a)
    second_a, second_m = advance(restored['arrays'], restored['metadata'], end_segment=4)
    publish_generation(root, 11, second_a, second_m, identities(), manufactured_validator)
    exact = analytic(SCHEDULE)
    difference = float(np.max(np.abs(full_a['prefix_state'] - second_a['prefix_state'])))
    error = float(np.max(np.abs(full_a['prefix_state'] - exact)))
    metadata_equal = full_m == second_m
    arrays_equal = all(np.array_equal(full_a[key], second_a[key]) for key in full_a)
    return {
        'schema': 'rei.q1b.checkpoint_manufactured_trial.v1',
        'status': 'PASS' if equal_restore and arrays_equal and metadata_equal and error < 2e-10 else 'FAIL',
        'all_acceptance': bool(equal_restore and arrays_equal and metadata_equal and error < 2e-10),
        'restart_kind': 'FRESH_BDF_AT_NATURAL_SEGMENT_BOUNDARY',
        'internal_bdf_state_restored': False,
        'production_provider_binding': False,
        'scientific_admission': False,
        'restored_all_arrays_and_metadata_exactly': equal_restore,
        'complete_state_prefix_extrema_metadata_equal': arrays_equal and metadata_equal,
        'split_vs_uninterrupted_max_absolute_error': difference,
        'analytic_max_absolute_error': error,
        'analytic_error_bound': 2e-10,
        'ledger_max': full_m['ledger_max'],
        'common_samples':len(SCHEDULE), 'natural_segments':len(EDGES)-1,
        'new_manufactured_segment_integrations':8,
        'old_replays':0, 'native_provider_calls':0, 'physical_q1b_ode_runs':0,
        'generation_10_manifest_sha256':_hash_bytes((path/'manifest.json').read_bytes()),
        'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
    }


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--result', type=Path, required=True)
    args = parser.parse_args()
    result = split_trial(args.root)
    with args.result.open('x') as handle: json.dump(result,handle,indent=2,allow_nan=False);handle.write('\n')
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['all_acceptance'] else 1)
