from fractions import Fraction
from math import factorial

import pytest

flint = pytest.importorskip("flint", reason="PHYS68 requires python-flint")
from flint import acb, arb, ctx

from wu088_hh.phys67_coulomb_certificate import normalized_h_ratio_ball
from wu088_hh.phys68_taylor import (
    TaylorDisk, TaylorEnclosureFailure, coulomb_q_coefficients, coulomb_taylor,
    dyadic_fraction, exact_fraction, inflate_complex, ode_taylor_coefficients,
    rational_ball,
)


def free_outgoing(degree=24):
    """Synthetic exact ODE exp(i*k*z), with a separately known disk bound."""
    with ctx.workprec(384):
        k = rational_ball(Fraction(7,10))
        coefficients = ode_taylor_coefficients(
            [Fraction(49,100)]+[0]*(degree-2), acb(1), acb(0,k), degree)
        bound = (2*k).exp().upper()  # sup |exp(i*k*z)| on |z|<=2
        return TaylorDisk(Fraction(0),Fraction(2),coefficients,bound,384,
                          function="synthetic exp(i*7*z/10)")


@pytest.mark.parametrize("value", [1.0, True, complex(1), float("nan"), arb(1)])
def test_point_inputs_refuse_unannounced_floating_point_or_interval_semantics(value):
    with pytest.raises(TypeError):
        exact_fraction(value)


def test_exact_rational_conversion_preserves_tiny_dyadic_values():
    with ctx.workprec(128):
        tiny = arb((1,-2000))
        assert dyadic_fraction(tiny) == Fraction(1,1<<2000)
        assert rational_ball(dyadic_fraction(tiny)).contains(tiny)
        assert exact_fraction("28.25") == Fraction(113,4)
        with pytest.raises(ValueError):
            dyadic_fraction(arb("1 +/- 0.1"))


def test_exact_coulomb_q_coefficients_match_independent_symbolic_expansion():
    import sympy as sp
    z = sp.Symbol("z")
    center = sp.Rational(111,4)
    ell = 21
    expression = sp.Rational(49,100)+2/(center+z)-ell*(ell+1)/(center+z)**2
    expansion = sp.series(expression,z,0,8).removeO().expand()
    expected = [Fraction(expansion.coeff(z,n)) for n in range(8)]
    assert list(coulomb_q_coefficients(ell,Fraction(111,4),8)) == expected


def test_free_ode_recurrence_matches_exact_exponential_coefficients():
    with ctx.workprec(384):
        disk = free_outgoing(24)
        ik = acb(0,rational_ball(Fraction(7,10)))
        for n,coefficient in enumerate(disk.coefficients):
            assert coefficient.overlaps(ik**n/factorial(n))
        # Odd powers are imaginary with the outgoing sign.
        assert disk.coefficients[1].imag > 0
        assert disk.coefficients[3].imag < 0


@pytest.mark.parametrize("offset", [Fraction(1,4), Fraction(-1,4), "1/3"])
def test_synthetic_exact_function_is_contained_by_polynomial_and_cauchy_tail(offset):
    with ctx.workprec(384):
        disk = free_outgoing(16)
        value = disk.evaluate(offset)
        exact = (acb(0,rational_ball(Fraction(7,10)))*rational_ball(exact_fraction(offset))).exp()
        assert value.contains(exact)
        small = disk.remainder(Fraction(1,8))
        large = disk.remainder(Fraction(1,4))
        assert small.is_exact() and small >= 0 and small < large
        assert disk.remainder(0).is_zero()


def test_complex_offset_ball_uses_its_whole_extent():
    with ctx.workprec(384):
        disk = free_outgoing(24)
        offset = acb(arb("0.125 +/- 0.01"),arb("0.125 +/- 0.01"))
        result = disk.evaluate(offset)
        for x,y in [(Fraction(115,1000),Fraction(135,1000)),
                    (Fraction(135,1000),Fraction(115,1000))]:
            direct = (acb(0,rational_ball(Fraction(7,10)))*
                      acb(rational_ball(x),rational_ball(y))).exp()
            assert result.contains(direct)
        with pytest.raises(ValueError,match="strictly below"):
            disk.evaluate(acb(arb("1.9 +/- 0.2")))


def test_complex_disk_inflation_is_outward_and_never_converts_to_float():
    with ctx.workprec(128):
        error = arb((1,-2000))
        value = inflate_complex(acb(0),error)
        assert value.contains(acb(error,error))
        assert value.contains(acb(-error,-error))
        with pytest.raises(ValueError):
            inflate_complex(acb(0),arb("0 +/- 1"))


def test_zero_free_bound_and_reciprocal_have_a_constructive_gate():
    with ctx.workprec(384):
        disk = free_outgoing(32)
        lower = disk.zero_free_lower(Fraction(1,2))
        assert lower.is_exact() and lower > 0
        reciprocal = disk.reciprocal_disk(Fraction(1,2))
        assert reciprocal.radius == Fraction(1,2)
        exact = acb(0,rational_ball(Fraction(-7,40))).exp()
        assert reciprocal.evaluate(Fraction(1,4)).contains(exact)
        # Cauchy tail for reciprocal uses its smaller certified radius.
        assert reciprocal.remainder(Fraction(1,4)) > disk.remainder(Fraction(1,4))


def test_failed_zero_free_test_does_not_claim_a_zero_or_return_an_inverse_certificate():
    with ctx.workprec(384):
        coefficients = ode_taylor_coefficients([-1]+[0]*30,acb(1),acb(1),32)
        disk = TaylorDisk(Fraction(0),Fraction(2),coefficients,arb(2).exp().upper(),384,
                          function="synthetic exp(z), which actually has no zeros")
        assert disk.zero_free_lower(1) < 0
        with pytest.raises(TaylorEnclosureFailure,match="UNRESOLVED_ZERO_FREE_BOUND"):
            disk.reciprocal_disk(1)
        assert disk.zero_free_lower(Fraction(1,4)) > 0


@pytest.mark.parametrize("ell,center", [(0,28),(21,28),(28,39),(64,39)])
def test_actual_new_radii_agree_with_separate_coulomb_evaluation(ell,center):
    # Targets 28.25 and 39.25 are new; no PHYS67 20-point campaign is rerun.
    with ctx.workprec(384):
        disk = coulomb_taylor(ell,center,degree=64,precision_bits=384)
        target = Fraction(center)+Fraction(1,4)
        enclosure = disk.evaluate(Fraction(1,4))
        direct = normalized_h_ratio_ball(ell,target,precision_bits=512)
        assert enclosure.contains(direct)
        assert disk.remainder(Fraction(1,4)) < arb("1e-48")
        small_radius = Fraction(1,4) if ell==64 else Fraction(1,2)
        assert disk.zero_free_lower(small_radius) > 0


@pytest.mark.parametrize("kwargs", [
    {"ell":True,"center":28}, {"ell":65,"center":28},
    {"ell":0,"center":28.0}, {"ell":0,"center":26},
    {"ell":0,"center":28,"majorant_radius":"27.3"},
    {"ell":0,"center":28,"degree":0},
    {"ell":0,"center":28,"precision_bits":53},
])
def test_coulomb_domain_and_precision_contract(kwargs):
    with pytest.raises((ValueError,TypeError)):
        coulomb_taylor(**kwargs)


def test_recurrence_requires_sufficient_valid_initial_data_and_q_coefficients():
    with pytest.raises(ValueError,match="insufficient"):
        ode_taylor_coefficients([0],acb(1),acb(0),4)
    with pytest.raises(TypeError):
        ode_taylor_coefficients([0],1,acb(0),2)
    with pytest.raises(TaylorEnclosureFailure):
        ode_taylor_coefficients([0],acb("nan"),acb(0),2)


def test_serialized_bounds_remain_dyadic_and_precision_context_is_restored():
    original = ctx.prec
    disk = free_outgoing(8)
    record = disk.as_record()
    assert ctx.prec == original
    assert record["degree"] == 8 and record["HH_R10"] == "OFF"
    assert "mantissa" in record["majorant_upper"]["midpoint"]
    assert len(record["coefficients"]) == 9
