"""Exact helper tests. No canonical thermochemistry or same-parent map is built here."""
from dataclasses import FrozenInstanceError
from fractions import Fraction as Q
import importlib.util
from itertools import product
from pathlib import Path
import sys

import pytest

SOURCE = Path(__file__).resolve().parents[1] / 'paired_budget.py'
SPEC = importlib.util.spec_from_file_location('rei_followthrough_paired_budget', SOURCE)
pb = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = pb
SPEC.loader.exec_module(pb)


def test_shared_affine_input_cancels_but_cartesian_width_does_not():
    a = pb.AffineBudget(9, {'parent/log_T': Q(11, 100000)}, 0)
    out = pb.compare_declared_budget(a, a, 2e-4)
    assert out['paired_bound'] == 0
    assert out['cartesian_bound'] == Q(22, 100000)
    assert out['strict_declared_bound_below_limit'] is True
    assert out['scope'] == 'CONDITIONAL_ON_SUPPLIED_MAP_ENCLOSURES_NOT_CANONICAL_ACCEPTANCE'


def test_equal_bounds_with_independent_ids_do_not_cancel():
    a = pb.AffineBudget(1, {'site/full': Q(1, 1000)}, 0)
    b = pb.AffineBudget(1, {'site/half': Q(1, 1000)}, 0)
    out = pb.compare_declared_budget(a, b, 2e-4)
    assert out['paired_bound'] == Q(2, 1000)
    assert out['strict_declared_bound_below_limit'] is False


def test_nonlinear_remainders_are_summed_not_erased():
    a = pb.AffineBudget(1, {'shared': Q(1, 1000)}, Q(3, 10000))
    b = pb.AffineBudget(1, {'shared': Q(1, 1000)}, Q(4, 10000))
    delta = pb.paired_difference(a, b)
    assert delta.remainder_radius == Q(7, 10000)
    assert delta.bound == Q(7, 10000)
    assert not pb.compare_declared_budget(a, b, 2e-4)['strict_declared_bound_below_limit']


def test_difference_sign_and_all_corners_agree_with_direct_rationals():
    a = pb.AffineBudget(Q(1, 3), {'shared': Q(2, 7), 'full': Q(-3, 5)}, Q(1, 19))
    b = pb.AffineBudget(Q(5, 4), {'shared': Q(-1, 7), 'half': Q(2, 9)}, Q(2, 23))
    d = pb.paired_difference(a, b)
    assert d.center == Q(11, 12)
    ids = sorted(set(a.coefficients) | set(b.coefficients))
    differences = []
    for signs in product((-1, 1), repeat=len(ids)):
        theta = dict(zip(ids, signs))
        for ef, eh in product((-1, 1), repeat=2):
            f = a.center + sum(v*theta[k] for k, v in a.coefficients.items()) + ef*a.remainder_radius
            h = b.center + sum(v*theta[k] for k, v in b.coefficients.items()) + eh*b.remainder_radius
            differences.append(h-f)
    assert min(differences) == d.center-d.radius
    assert max(differences) == d.center+d.radius
    assert max(map(abs, differences)) == d.bound


def test_source_binary64_strict_threshold_is_not_replaced_or_relaxed():
    limit = Q.from_float(2e-4)
    a = pb.AffineBudget(0, {}, 0)
    b = pb.AffineBudget(limit, {}, 0)
    assert pb.exact(2e-4) == limit
    assert pb.compare_declared_budget(a, b, 2e-4)['strict_declared_bound_below_limit'] is False
    inside = pb.AffineBudget(limit-Q(1, 10**20), {}, 0)
    assert pb.compare_declared_budget(a, inside, 2e-4)['strict_declared_bound_below_limit'] is True


def test_caller_dictionary_and_budget_are_immutable():
    data = {'shared': Q(1, 7)}
    a = pb.AffineBudget(1, data, 0)
    data['shared'] = 99
    assert a.coefficients['shared'] == Q(1, 7)
    with pytest.raises(TypeError):
        a.coefficients['shared'] = 2
    with pytest.raises(FrozenInstanceError):
        a.center = 0


@pytest.mark.parametrize('value', [float('nan'), float('inf'), -float('inf'), True])
def test_nonfinite_and_boolean_coefficients_fail(value):
    with pytest.raises((ValueError, TypeError)):
        pb.AffineBudget(0, {'x': value}, 0)


def test_bad_remainder_and_empty_source_identity_fail():
    with pytest.raises(ValueError):
        pb.AffineBudget(0, {}, -1)
    with pytest.raises(ValueError):
        pb.AffineBudget(0, {'': 1}, 0)
    with pytest.raises(ValueError):
        pb.compare_declared_budget(pb.AffineBudget(0, {}, 0), pb.AffineBudget(0, {}, 0), 0)


def test_valid_affine_bound_never_exceeds_cartesian_bound():
    for i in range(-3, 4):
        a = pb.AffineBudget(i, {'a': Q(i, 7), 'common': Q(1, 3)}, Q(1, 19))
        b = pb.AffineBudget(2-i, {'b': Q(i, 9), 'common': Q(-2, 5)}, Q(1, 23))
        out = pb.compare_declared_budget(a, b, Q(1))
        assert out['paired_bound'] <= out['cartesian_bound']
