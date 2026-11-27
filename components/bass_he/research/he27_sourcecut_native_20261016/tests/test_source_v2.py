"""Affected C6/C7 tests for event-segmented HE27 source admission.

Only the new opt-in source is exercised here.  Native ODE evolution and old
HE25/HE26 scientific suites belong to separate, already preserved gates.
"""
from pathlib import Path
import os
import sys
import time

import numpy as np
import pytest

PACKAGE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PACKAGE / 'analysis'), str(PACKAGE / 'src')]
from source_acceptance import BIND_EV, birth_frame_reference, sigma_cm2
from sourcecut import SourceCutModel as DirectSourceCutModel
from sourcecut_v2 import SourceCutModel
from source_v2_acceptance import record_snapshot, sha256

OBSERVATIONS = []


@pytest.fixture(scope='module')
def models():
    # Four finite, source-only constructions: three signed-q checks and one
    # refinement.  Cached within this module so no table is rebuilt per test.
    source_sha_at_start = sha256(PACKAGE / 'src/sourcecut_v2.py')
    made = {}
    for q in (-.005, 0., .005):
        started = time.monotonic()
        made[q] = SourceCutModel(None, m=4, angles=4, q=q,
                                 source_table_nodes=512)
        OBSERVATIONS.append({'kind': 'construction', 'q': q, 'nodes': 512,
                             'elapsed_s': time.monotonic()-started})
    started = time.monotonic()
    made['q0_1024'] = SourceCutModel(None, m=4, angles=4, q=0.,
                                     source_table_nodes=1024)
    OBSERVATIONS.append({'kind': 'construction', 'q': 0., 'nodes': 1024,
                         'elapsed_s': time.monotonic()-started})
    yield made
    output = os.environ.get('HE27_SOURCE_V2_REPORT')
    if output:
        record_snapshot(output, PACKAGE, source_sha_at_start, OBSERVATIONS, made)


def physical_moments(model, t, raw):
    energy = model.geometry(t)[0]
    sigma = sigma_cm2(energy)
    return np.r_[float(raw.sum()), float(np.dot(raw, energy)),
                 (raw[:, None]*sigma).sum(axis=0),
                 (raw[:, None]*sigma*(energy[:, None]-BIND_EV)).sum(axis=0)]


def test_arbitrary_birth_times_keep_eight_independent_moments(models):
    reference = birth_frame_reference()
    expected = np.array([reference['raw_n'], reference['raw_u_ev'],
                         *reference['photo_cm2'], *reference['heat_ev_cm2']])
    fractions = (0., .0001273786026739819, .0009449402471520216,
                 .071, .37, .763, .997, 1.)
    for q in (-.005, 0., .005):
        model = models[q]
        assert model.source_table_diagnostics['nodes_per_long_interval'] == 512
        for fraction in fractions:
            t = fraction*model.t_end
            raw, report = model.source_moments(t)
            actual = physical_moments(model, t, raw)
            donor = np.array(report['donor_raw'])
            OBSERVATIONS.append({'kind': 'source_moments', 'q': q,
                'nodes': 512, 'proper_time_fraction': fraction,
                'raw_n_relative_error': float(donor[0]/expected[0]-1),
                'mean_energy_error_ev': float(donor[1]/donor[0]-reference['mean_ev']),
                'max_species_relative_error': float(np.max(np.abs(donor[2:]/expected[2:]-1))),
                'max_admission_relative_error': float(np.max(
                    np.abs(actual-donor)/np.maximum(np.abs(donor), 1e-30))),
                'min_mode': float(raw.min())})
            np.testing.assert_allclose(actual, np.array(report['admitted_raw']),
                                       rtol=3e-15, atol=0.)
            assert np.all(np.isfinite(raw)) and np.all(raw >= 0)
            assert abs(donor[0]/expected[0]-1) < 1e-13
            assert abs(donor[1]/donor[0]-reference['mean_ev']) < 1e-11
            np.testing.assert_allclose(donor[2:], expected[2:],
                                       rtol=2e-12, atol=0.)
            assert np.max(np.abs(actual-donor)/np.maximum(np.abs(donor), 1e-30)) <= 3e-13
            source = model.source(t)
            assert np.all(source >= 0)
            assert abs(float(source.sum())/
                       (model.H(t)*model.source_per_x)-1) < 2e-15
            energy = model.geometry(t)[0]
            assert np.all(raw[(energy < 13.6-2e-12) |
                              (energy > 100.+2e-12)] == 0)


def test_cut_crossing_has_correct_one_sided_source_and_sigma(models):
    model = models[0.]
    # Several original breakpoints cluster within subsecond gaps at a proper
    # time ~5e10 s.  Their left/right energy can round to the same binary64
    # value.  Select an actually representable Verner crossing by inspecting
    # the inherited HE25 interval masks on both adjacent open intervals.
    crossing = delta = selected_index = None
    for i, candidate in enumerate(model.breakpoints):
        previous = 0. if i == 0 else model.breakpoints[i-1]
        following = model.t_end if i+1 == len(model.breakpoints) else model.breakpoints[i+1]
        side = .2*min(candidate-previous, following-candidate)
        model.set_interval(candidate-side, candidate)
        sigma_left_mask = model._sigma_mask.copy()
        source_left_mask = model._source_mask.copy()
        model.set_interval(candidate, candidate+side)
        if (np.count_nonzero(sigma_left_mask != model._sigma_mask) > 0 and
                np.count_nonzero(source_left_mask != model._source_mask) > 0):
            crossing, delta, selected_index = candidate, side, i
            break
    assert crossing is not None, 'NO_REPRESENTABLE_DUAL_CUTOFF_EVENT'
    model.set_interval(crossing-delta, crossing)
    left_source = model.source(crossing)
    left_sigma = model.sigma(crossing)
    model.set_interval(crossing, crossing+delta)
    right_source = model.source(crossing)
    right_sigma = model.sigma(crossing)
    assert np.all(left_source >= 0) and np.all(right_source >= 0)
    assert abs(left_source.sum()/right_source.sum()-1) < 2e-15
    assert np.count_nonzero(left_sigma != right_sigma) > 0
    # An event changes a discrete mode's active threshold band.  The original
    # v1 endpoint selection returned the same vector on both sides.
    relative_l1 = float(np.abs(left_source-right_source).sum()/left_source.sum())
    OBSERVATIONS.append({'kind': 'one_sided_cut', 'q': 0., 'crossing_t': crossing,
        'breakpoint_index': selected_index,
        'relative_source_l1_jump': relative_l1,
        'sigma_changed_modes': int(np.count_nonzero(left_sigma != right_sigma))})
    assert relative_l1 > 1e-8


def test_source_vector_is_regular_inside_stall_time_segment(models):
    model = models[0.]
    for fraction in (.0001273786026739819, .0009449402471520216):
        t = fraction*model.t_end
        table = model._source_tables[model._locate(t)]
        times = table[0]
        index = int(np.clip(np.searchsorted(times, t)-1, 0, len(times)-2))
        left, right = times[index:index+2]
        a = model._raw_source(.25*left+.75*right)
        b = model._raw_source(.5*left+.5*right)
        c = model._raw_source(.75*left+.25*right)
        # The raw vector in one physical interval must have no short-scale
        # active-set jitter; this is a local ODE regularity test, not proof
        # that an independent stiff solver will finish the full domain.
        defect = np.abs(a+c-2*b).sum()/max(float(b.sum()), 1e-30)
        OBSERVATIONS.append({'kind': 'stall_local_regularity',
            'proper_time_fraction': fraction, 'relative_second_difference': float(defect),
            'table_interval': model._locate(t)})
        assert defect < 1e-13


def test_1024_nested_knot_refines_source_vector_near_stall(models):
    coarse = models[0.]
    refined = models['q0_1024']
    direct = DirectSourceCutModel(None, m=4, angles=4, q=0.)
    assert np.array_equal(coarse.Eref, refined.Eref)
    assert np.array_equal(coarse.k_perp, refined.k_perp)
    assert np.array_equal(coarse.k_parallel, refined.k_parallel)
    for fraction in (.0001273786026739819, .0009449402471520216):
        t = fraction*coarse.t_end
        times = coarse._source_tables[coarse._locate(t)][0]
        index = int(np.clip(np.searchsorted(times, t)-1, 0, len(times)-2))
        midpoint = float((times[index]+times[index+1])/2)
        truth, _ = direct.source_moments(midpoint)
        slow, _ = coarse.source_moments(midpoint)
        fine, _ = refined.source_moments(midpoint)
        e512 = np.abs(slow-truth).sum()/truth.sum()
        e1024 = np.abs(fine-truth).sum()/truth.sum()
        OBSERVATIONS.append({'kind': 'nested_refinement',
            'proper_time_fraction': fraction, 't_mid_s': midpoint,
            'source_vector_l1_error_512': float(e512),
            'source_vector_l1_error_1024': float(e1024)})
        assert e1024 <= max(1e-13, e512*0.01)
