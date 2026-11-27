"""Physical normalization, independent angular quadrature and enclosure contracts."""
from fractions import Fraction as F
from pathlib import Path

import pytest

pytest.importorskip("flint", reason="PHYS67 requires optional python-flint")
from flint import acb, arb, ctx, fmpq

from wu088_hh.phys67_first_born import (
    R, angular_entry_acb, angular_laurent_pairs, component_radii,
    dyadic_fraction, integrate_first_born, serialize_ball,
)

SOURCE = Path(__file__).parents[1] / "research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"


def rational(q):
    q = F(q)
    return arb(fmpq(q.numerator, q.denominator))


@pytest.mark.parametrize("radius", [27, 39, 65])
def test_s_wave_matches_direct_elementary_antiderivative(radius):
    # Integral of (d+1)e^-2d is -(d/2+3/4)e^-2d. This checks
    # the physical factor two, normalized P0 basis and the Jacobian.
    with ctx.workprec(384):
        r = arb(radius); shift = rational(R)
        lo, hi = r-shift, r+shift
        expected = ((lo/2+rational(F(3, 4)))*(-2*lo).exp()
                    -(hi/2+rational(F(3, 4)))*(-2*hi).exp())/(r*shift)
        actual = angular_entry_acb(0, 0, acb(r))
        assert actual.real.overlaps(expected)
        assert actual.imag.is_zero()
        assert actual.real > 0


@pytest.mark.parametrize("ell,ellprime,radius", [(1, 0, 27), (3, 2, 65)])
def test_angular_identity_matches_independent_validated_mu_integral(ell, ellprime, radius):
    # Recurrence and direct mu integration do not use the Laurent expansion
    # or factorial exponential-moment formula of the implementation.
    with ctx.workprec(384):
        r, shift = acb(radius), acb(rational(R))
        def legendre(n, x):
            if n == 0:
                return acb(1)
            p0, p1 = acb(1), x
            for j in range(1, n):
                p0, p1 = p1, ((2*j+1)*x*p1-j*p0)/(j+1)
            return p1
        def integrand(mu, analytic):
            distance_squared = r*r+shift*shift-2*r*shift*mu
            if not distance_squared.real > 0:
                return acb("nan")
            d = distance_squared.sqrt()
            return (arb((2*ell+1)*(2*ellprime+1)).sqrt()
                    * legendre(ell, mu)*legendre(ellprime, mu)
                    * (1+1/d)*(-2*d).exp())
        direct = acb.integral(integrand, -1, 1, abs_tol=arb("1e-90"),
                              rel_tol=arb("1e-40"), eval_limit=2000)
        expanded = angular_entry_acb(ell, ellprime, r)
        assert direct.is_finite() and direct.overlaps(expanded)
        assert direct.rad() < arb("1e-85")


def test_original_high_order_entry_is_symmetric_without_complex_conjugation():
    with ctx.workprec(384):
        assert angular_laurent_pairs(21, 20) == angular_laurent_pairs(20, 21)
        x = acb(27, "0.01")
        left = angular_entry_acb(21, 20, x)
        right = angular_entry_acb(20, 21, x)
        assert left.overlaps(right)
        assert not left.overlaps(right.conjugate())


@pytest.mark.parametrize("radius", [acb(0), acb("0.7"), acb(arb("1 +/- 1"))])
def test_angular_analytic_guard_excludes_shifted_singularity(radius):
    assert not angular_entry_acb(0, 0, radius).is_finite()


def test_serialized_dyadics_preserve_rectangle_even_below_binary64_underflow():
    with ctx.workprec(384):
        z = acb(arb("1.25", "1e-400"), arb("-0.125", "1e-410"))
        record = serialize_ball(z)
        radii = component_radii(z)
        for name, value, radius in zip(("real", "imag"), (z.real, z.imag), radii):
            midpoint = dyadic_fraction(record[name]["mid"])
            assert rational(midpoint) == value.mid()
            assert dyadic_fraction(record[name]["rad"]) == radius > 0
            assert float(radius) == 0.0  # Exact output, not this conversion, is authoritative.


@pytest.mark.parametrize("kwargs", [
    {"ell": 65}, {"ellprime": -1}, {"outer": 27}, {"outer": 81},
    {"outer": 65.0}, {"absolute_goal": 0}, {"relative_goal": 1},
    {"precision_bits": 53}, {"coefficient_bits": 128}, {"eval_limit": 99},
])
def test_integrator_rejects_out_of_contract_requests(kwargs):
    with pytest.raises(ValueError):
        integrate_first_born(SOURCE, **kwargs)


def test_frozen_source_guard_precedes_numerical_work(tmp_path):
    fake = tmp_path / "changed.npz"
    fake.write_bytes(b"changed source")
    with pytest.raises(ValueError, match="SHA256"):
        integrate_first_born(fake)


def test_small_first_born_run_reports_actual_ball_radius_and_separate_tail():
    # A new-kernel one-panel integration; this is not any completed PHYS66 case.
    result = integrate_first_born(SOURCE, ell=0, ellprime=0, outer=28,
        precision_bits=192, coefficient_bits=384, absolute_goal="1e-36",
        relative_goal="1e-20", eval_limit=1000, panel_width=1)
    q = result["cutoff_enclosure"]
    radius = sum((dyadic_fraction(q[axis]["rad"]) for axis in ("real", "imag")), F(0))
    recorded = result["numerical_complex_error_upper"]
    assert radius == F(int(recorded["numerator"]), int(recorded["denominator_hex"], 16))
    assert result["actual_numerical_goal_met"] == (radius <= F("1e-36"))
    assert result["actual_numerical_goal_met"]
    for axis in ("real", "imag"):
        assert dyadic_fraction(result["full_radial_enclosure"][axis]["rad"]) >= dyadic_fraction(q[axis]["rad"])
    assert result["angular_integration"] == "EXACT_ELEMENTARY_POLYNOMIAL_IDENTITY_M0"
    assert result["higher_order_and_driven_obligations"] == "OPEN"
    assert result["HH_R10"] == "OFF"
