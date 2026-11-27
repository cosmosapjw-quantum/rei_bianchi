"""Exact reuse, physical normalization and Taylor remainder contracts."""
from fractions import Fraction as F
from math import comb, factorial

import pytest

pytest.importorskip("flint", reason="PHYS68 angular certification needs python-flint")
from flint import acb, arb, ctx, fmpq

from wu088_hh.phys67_first_born import (
    R, angular_laurent_pairs as prior_pairs,
)
from wu088_hh.phys68_angular import (
    angular_cache_info, angular_coefficients_ball, angular_complex_disk_bound,
    angular_entry_acb, angular_laurent_pairs, angular_taylor_coefficients,
    angular_taylor_remainder_bound, monomial_laurent_pairs,
)


def q(value):
    value = F(value)
    return arb(fmpq(value.numerator, value.denominator))


@pytest.mark.parametrize("ell,ellprime", [(0, 0), (4, 3), (21, 20), (20, 28)])
def test_cached_monomial_combination_equals_prior_exact_fraction_formula(ell, ellprime):
    actual = angular_laurent_pairs(ell, ellprime)
    assert actual == prior_pairs(ell, ellprime)
    assert len(actual) == ell+ellprime+2
    assert all(type(x) is F for pair in actual for x in pair)


def test_constant_monomial_has_independent_elementary_endpoint_coefficients():
    # int exp(-2t)dt=(exp(2R)-exp(-2R))/2; its (t+1) moment
    # has primitive -(t/2+3/4)exp(-2t).
    assert monomial_laurent_pairs(0) == (
        (F(1, 2), -F(1, 2)),
        (F(3, 4)-R/2, -F(3, 4)-R/2),
    )


@pytest.mark.parametrize("radius", [29, F(61, 2), 73])
def test_s_wave_physical_normalization_at_new_radii(radius):
    with ctx.workprec(384):
        rr, shift = q(radius), q(R)
        lo, hi = rr-shift, rr+shift
        expected = ((lo/2+q(F(3, 4)))*(-2*lo).exp()
                    -(hi/2+q(F(3, 4)))*(-2*hi).exp())/(rr*shift)
        actual = angular_entry_acb(0, 0, F(radius))
        assert actual.imag.is_zero()
        assert actual.real > 0
        assert actual.real.overlaps(expected)


def test_symmetric_pair_reuses_exact_and_precision_qualified_ball_cache():
    direct = angular_laurent_pairs(9, 6)
    assert direct is angular_laurent_pairs(6, 9)
    high = angular_coefficients_ball(9, 6, 768)
    assert high is angular_coefficients_ball(6, 9, 768)
    low = angular_coefficients_ball(6, 9, 192)
    assert low is not high
    assert all(a.overlaps(b) for a, b in zip(low, high))
    assert angular_cache_info()["monomials"]["maxsize"] == 129


def test_complex_symmetry_has_no_conjugation():
    with ctx.workprec(384):
        radius = acb(q(F(59, 2)), q(F(1, 8)))
        left = angular_entry_acb(21, 20, radius)
        right = angular_entry_acb(20, 21, radius)
        assert left.overlaps(right)
        assert not left.overlaps(right.conjugate())


@pytest.mark.parametrize("degree", [0, 1, 8])
def test_taylor_coefficients_equal_independent_finite_binomial_sum(degree):
    center = F(63, 2)
    actual = angular_taylor_coefficients(4, 3, center, degree)
    assert len(actual) == degree+1
    with ctx.workprec(384):
        coefficients = angular_coefficients_ball(4, 3)
        factor = arb(9*7).sqrt()/q(R)*(-2*q(center)).exp()
        for n, value in enumerate(actual):
            expected = arb(0)
            for j, coefficient in enumerate(coefficients):
                inner = F(0)
                for v in range(n+1):
                    if j == 0 and v:
                        continue
                    choose = 1 if v == 0 else comb(j+v-1, v)
                    inner += F((-2)**(n-v), factorial(n-v))*(-1)**v*choose/center**v
                expected += coefficient*q(inner/center**j)
            assert value.real.overlaps(expected*factor)
            assert value.imag.is_zero()


@pytest.mark.parametrize("ell,ellprime,center,step", [
    (0, 0, F(61, 2), F(1, 7)),
    (4, 3, F(73, 2), F(-2, 9)),
    (21, 20, F(87, 2), F(1, 4)),
])
def test_taylor_subpoints_are_contained_after_proved_cauchy_remainder(ell, ellprime, center, step):
    degree, disk = 18, F(4)
    coefficients = angular_taylor_coefficients(ell, ellprime, center, degree)
    remainder = angular_taylor_remainder_bound(center, disk, abs(step), degree)
    assert remainder.is_exact() and remainder > 0
    with ctx.workprec(384):
        polynomial = acb(0)
        for value in reversed(coefficients):
            polynomial = polynomial*q(step)+value
        error = arb(0, remainder)
        enclosure = polynomial+acb(error, error)
        direct = angular_entry_acb(ell, ellprime, center+step)
        assert enclosure.contains(direct)
        assert remainder < arb("1e-38")


def test_complex_subpoint_is_contained_by_same_disk_remainder():
    center, step_bound = F(67, 2), F(1, 4)
    coefficients = angular_taylor_coefficients(3, 2, center, 20)
    remainder = angular_taylor_remainder_bound(center, 4, step_bound, 20)
    with ctx.workprec(384):
        step = acb(q(F(3, 20)), q(F(1, 5)))  # modulus exactly 1/4
        polynomial = acb(0)
        for value in reversed(coefficients):
            polynomial = polynomial*step+value
        error = arb(0, remainder)
        enclosure = polynomial+acb(error, error)
        direct = angular_entry_acb(3, 2, acb(q(center))+step)
        assert enclosure.contains(direct)


@pytest.mark.parametrize("ell,ellprime", [(0, 0), (5, 2), (21, 20), (20, 28)])
def test_complex_disk_norm_majorant_contains_new_samples(ell, ellprime):
    center, disk = F(71, 2), F(3)
    majorant = angular_complex_disk_bound(center, disk)
    assert majorant.is_exact()
    with ctx.workprec(384):
        for offset in (acb(3), acb(-3), acb(0, 3), acb(q(F(9, 5)), q(F(12, 5)))):
            value = angular_entry_acb(ell, ellprime, acb(q(center))+offset)
            assert abs(value) < majorant


def test_taylor_context_is_restored_for_nested_precision_and_nondefault_cap():
    saved_cap = ctx.cap
    try:
        ctx.cap = 7
        with ctx.workprec(211):
            coefficients = angular_taylor_coefficients(2, 1, 32, 16, 384, 1024)
            assert len(coefficients) == 17
            assert ctx.prec == 211 and ctx.cap == 7
        assert ctx.cap == 7
    finally:
        ctx.cap = saved_cap


@pytest.mark.parametrize("call", [
    lambda: angular_laurent_pairs(-1, 0),
    lambda: angular_laurent_pairs(0, 65),
    lambda: monomial_laurent_pairs(129),
    lambda: angular_coefficients_ball(0, 0, 127),
    lambda: angular_taylor_coefficients(0, 0, 31.0, 2),
    lambda: angular_taylor_coefficients(0, 0, True, 2),
    lambda: angular_taylor_coefficients(0, 0, R, 2),
    lambda: angular_taylor_coefficients(0, 0, 31, -1),
    lambda: angular_taylor_coefficients(0, 0, 31, 4, 512, 256),
    lambda: angular_complex_disk_bound(31, 31),
    lambda: angular_complex_disk_bound(31, -1),
    lambda: angular_taylor_remainder_bound(31, 4, 4, 10),
])
def test_invalid_inputs_are_rejected_without_changing_context(call):
    precision, cap = ctx.prec, ctx.cap
    with pytest.raises(ValueError):
        call()
    assert (ctx.prec, ctx.cap) == (precision, cap)


def test_analytic_domain_guard_applies_to_entire_input_ball():
    with ctx.workprec(192):
        assert not angular_entry_acb(0, 0, acb(arb(1, 1))).is_finite()
        assert angular_entry_acb(0, 0, acb(arb(2, 1))).is_finite()

