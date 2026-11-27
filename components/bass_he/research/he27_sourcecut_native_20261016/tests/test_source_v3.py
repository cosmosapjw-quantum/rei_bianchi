"""Focused HE27 v3 regression for short original cutoff intervals.

The source-only test replays the first v2 BirthCell failure without a native
owner, checks v3's one-sided source/rate masks, and preserves the raw input.
"""
from pathlib import Path
import math
import os
import re
import sys
import time

import numpy as np
import pytest

PACKAGE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PACKAGE / 'analysis'),
                str(PACKAGE / 'src'),
                str(PACKAGE.parent / 'he25_proper_birth_20261016/src')]
from source_v2_acceptance import atomic_create, sha256
from sourcecut import SourceCutModel as V1
from sourcecut import SourceProjectionError, BIND_EV
from sourcecut_v2 import SourceCutModel as V2
from sourcecut_v3 import SourceCutModel as V3
from physics import A_BIRTH, C_CM_S, neutral
from transport import BirthCell

FROZEN = {
    'v1': '470ab94200e789ae5241c39eb3d12848613ae49612a1131bb24fd0766e169d1d',
    'v2': 'cc0c077aef4fa0cb11da0142676a91c1bac2d5f630ac38033bf5066a32377ba8',
    'v3': 'ec3496a6df0e63c365801a9f3c4551600f929be3d321940acfe51e9b970484b1',
}
OBSERVATIONS = []


@pytest.fixture(scope='module')
def models():
    paths = {name: PACKAGE / 'src' / ('sourcecut.py' if name == 'v1' else
                                     f'sourcecut_{name}.py') for name in FROZEN}
    start = {name: sha256(path) for name, path in paths.items()}
    assert start == FROZEN
    made = {}
    for label, cls, q in [('v2_q0', V2, 0.), ('v3_q0', V3, 0.),
                         ('v3_qminus', V3, -.005), ('v3_qplus', V3, .005)]:
        began = time.monotonic()
        made[label] = cls(None, m=4, angles=4, q=q, source_table_nodes=512)
        OBSERVATIONS.append({'kind': 'construction', 'label': label, 'q': q,
                             'elapsed_s': time.monotonic()-began,
                             'source_table_sha256': made[label].source_table_sha256,
                             'tiny_intervals': len(made[label]._cut_bounds)-1-
                                               len(made[label]._source_tables)})
    yield made
    output = os.environ.get('HE27_SOURCE_V3_REPORT')
    if output:
        end = {name: sha256(path) for name, path in paths.items()}
        atomic_create(output, {
            'schema': 'bass_he.he27.source_v3_tiny_cut_regression.v1',
            'scope': 'source-only first failed BirthCell, one-sided masks, and exact source bytes; no native gas evolution',
            'source_sha256_at_start': start,
            'source_sha256_at_end': end,
            'source_identity_stable': start == end,
            'test_sha256': sha256(__file__),
            'he25_transport_sha256': sha256(PACKAGE.parent /
                'he25_proper_birth_20261016/src/transport.py'),
            'observations': OBSERVATIONS,
        })


def _moment_vector(model, t, raw):
    energy = model.geometry(t)[0]
    sigma = model.sigma(t)
    return np.r_[raw.sum(), np.dot(raw, energy),
        (raw[:, None]*sigma).sum(axis=0),
        (raw[:, None]*sigma*(energy[:, None]-BIND_EV)).sum(axis=0)]


def test_original_v2_birth_cell_failure_replays_and_v3_passes(models):
    old, repaired = models['v2_q0'], models['v3_q0']
    left, right = map(float, old._cut_bounds[4:6])
    assert abs((right-left)-.0874862671) < 1e-6
    with pytest.raises(SourceProjectionError,
                       match='HE27_V2_SOURCE_MOMENTS') as raised:
        BirthCell(old, left, right, order=16)
    error = str(raised.value)
    value_match = re.search(r'max_relative=([0-9.eE+-]+)', error)
    assert value_match is not None
    observed_defect = float(value_match.group(1))
    assert observed_defect > 3e-13

    # Reconstruct the precise first failed proper-time birth node and source
    # input without touching native gas, the failed transport output, or RHS.
    old.set_interval(left, right)
    z, _ = np.polynomial.legendre.leggauss(16)
    times = left + (right-left)*(z+1)/2
    failed = None
    for index, t in enumerate(times):
        try:
            old.source(float(t))
        except SourceProjectionError as exc:
            direct_raw, donor = V1.source_moments(old, float(t))
            failed = {'node_index': index, 't_birth_s': float(t),
                      'a_birth': float(A_BIRTH*math.exp(old.x(float(t)))),
                      'source_count_per_total_H': old.source_count,
                      'source_per_ln_a_per_total_H': old.source_per_x,
                      'source_direction_cosines': old.mu0.tolist(),
                      'k_perp_ev': old.k_perp.tolist(),
                      'k_parallel_ev': old.k_parallel.tolist(),
                      'physical_energy_ev': old.geometry(float(t))[0].tolist(),
                      'donor_raw_moments': donor['donor_raw'],
                      'direct_raw_number': float(direct_raw.sum()),
                      'v2_exception': str(exc)}
            break
    assert failed is not None
    cell = BirthCell(repaired, left, right, order=16)
    assert np.array_equal(cell.times, times)
    assert np.all(np.isfinite(cell.S)) and np.all(cell.S >= 0)
    assert np.all(np.isfinite(cell.Sinner)) and np.all(cell.Sinner >= 0)
    assert repaired.max_source_moment_error <= 3e-13
    OBSERVATIONS.append({'kind': 'exact_failed_birth_cell',
                         'left_s': left, 'right_s': right,
                         'width_s': right-left,
                         'v2_first_error': error,
                         'v2_first_relative_defect': observed_defect,
                         'first_failed_birth': failed,
                         'v3_source_sample_count': int(cell.S.size+cell.Sinner.size),
                         'v3_max_moment_error': repaired.max_source_moment_error,
                         'v3_min_birth_source_per_H_s': float(min(cell.S.min(), cell.Sinner.min()))})


def test_v3_tiny_interval_source_and_rate_masks_agree(models):
    for label in ('v3_qminus', 'v3_q0', 'v3_qplus'):
        model = models[label]
        tiny = [i for i in range(len(model._cut_bounds)-1)
                if i not in model._source_tables]
        assert len(tiny) >= 16
        selected = sorted(set([tiny[0], tiny[len(tiny)//2], tiny[-1]]))
        for interval in selected:
            left, right = model._cut_bounds[interval:interval+2]
            model.set_interval(float(left), float(right))
            for fraction in (.1, .5, .9):
                t = float(left+fraction*(right-left))
                raw, report = model.source_moments(t)
                actual = _moment_vector(model, t, raw)
                donor = np.array(report['donor_raw'])
                relative = np.abs(actual-donor)/np.maximum(np.abs(donor), 1e-30)
                source = model.source(t)
                sigma = model.sigma(t)
                # Gas RHS receives the same one-sided rate kernel as source
                # admission: no photons in modes excluded by its source mask.
                assert np.all(np.isfinite(raw)) and np.all(raw >= 0)
                assert np.all(raw[~model._source_mask] == 0)
                assert np.all(sigma >= 0)
                assert np.all(sigma[~model._sigma_mask] == 0)
                assert float(relative.max()) <= 3e-13
                assert abs(float(source.sum())/
                           (model.H(t)*model.source_per_x)-1) < 2e-15
                OBSERVATIONS.append({'kind': 'tiny_interior', 'label': label,
                    'q': model.q, 'interval': interval,
                    't_birth_s': t, 'a_birth': float(A_BIRTH*math.exp(model.x(t))),
                    'fraction': fraction, 'min_source': float(raw.min()),
                    'max_moment_relative_defect': float(relative.max()),
                    'positive_sigma_entries': int(np.count_nonzero(sigma))})


def test_original_v1_v2_source_bytes_remain_pinned(models):
    assert sha256(PACKAGE/'src/sourcecut.py') == FROZEN['v1']
    assert sha256(PACKAGE/'src/sourcecut_v2.py') == FROZEN['v2']
    assert sha256(PACKAGE/'src/sourcecut_v3.py') == FROZEN['v3']
    assert models['v3_q0'].K == models['v2_q0'].K
    np.testing.assert_array_equal(models['v3_q0'].k_perp, models['v2_q0'].k_perp)
    np.testing.assert_array_equal(models['v3_q0'].k_parallel, models['v2_q0'].k_parallel)
