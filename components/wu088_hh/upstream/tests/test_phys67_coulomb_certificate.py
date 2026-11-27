from fractions import Fraction
from pathlib import Path

import pytest

flint = pytest.importorskip("flint", reason="PHYS67 requires optional python-flint")
from flint import acb, arb, ctx, fmpq
from wu088_hh.phys67_coulomb_certificate import (
    binary64_error_bound, certify_points, complex_ball_record, coulomb_point,
    exact_radius, normalized_h_ratio_ball, outgoing_h_acb, restore_complex_ball,
)


@pytest.mark.parametrize("value", [27.0, 27.1, True, float("nan"), acb(27)])
def test_exact_point_input_rejects_implicit_binary64_and_ball_points(value):
    with pytest.raises(TypeError):
        exact_radius(value)


def test_decimal_and_rational_inputs_have_identical_exact_meaning():
    assert exact_radius("27.1") == Fraction(271, 10)
    assert exact_radius("271/10") == Fraction(271, 10)
    decimal = normalized_h_ratio_ball(20, "27.1", precision_bits=256)
    rational = normalized_h_ratio_ball(20, Fraction(271, 10), precision_bits=256)
    assert decimal.contains(rational) and rational.contains(decimal)


@pytest.mark.parametrize("ell,radius", [(0, 27), (20, 55), (21, 65), (28, 75), (64, 27)])
def test_recurrence_definition_ode_and_outgoing_sign(ell, radius):
    point = coulomb_point(ell, radius)
    with ctx.workprec(point.precision_bits):
        z = point.impedance
        assert z.is_finite() and z.imag > 0
        assert point.impedance_tricomi.is_finite()
        assert z.overlaps(point.impedance_tricomi)
        assert point.wronskian_rho.contains(1)
        assert point.ode_residual_f.contains(0) and point.ode_residual_g.contains(0)
        # This exact Wronskian identity checks the derivative's r versus rho
        # scale and the outgoing sign without a stored approximate value.
        norm2 = point.h_plus.real**2 + point.h_plus.imag**2
        assert (z.imag * norm2).contains(arb(fmpq(7, 10)))
        incoming = point.h_prime_r.conjugate() / point.h_plus.conjugate()
        assert incoming.imag < 0
        assert not incoming.overlaps(z)


def test_high_barrier_tiny_outgoing_flux_remains_resolved():
    point = coulomb_point(64, 27)
    with ctx.workprec(512):
        assert point.impedance.real < -2
        assert arb("1e-51") < point.impedance.imag < arb("2e-51")
        assert point.impedance.imag.rad() < arb("1e-170")


def test_dyadic_serialization_preserves_the_full_ball():
    point = coulomb_point(21, 65)
    with ctx.workprec(512):
        record = complex_ball_record(point.impedance)
        for key, value in (("real", point.impedance.real), ("imag", point.impedance.imag)):
            mm, me = value.mid().man_exp()
            rm, re = value.rad().man_exp()
            assert record[key]["midpoint"] == {"mantissa": str(mm), "exponent2": int(me)}
            assert record[key]["radius"] == {"mantissa": str(rm), "exponent2": int(re)}
        restored = restore_complex_ball(record)
        # Arb may add a radius ulp on construction; the correct contract is
        # containment of the original exact dyadic rectangle, not equality.
        assert restored.contains(point.impedance)
    # A lower precision consumer can widen, but cannot shrink the certificate.
    with ctx.workprec(128):
        restored_low = restore_complex_ball(complex_ball_record(point.impedance))
        assert restored_low.contains(point.impedance)


def test_binary64_error_uses_exact_stored_bits():
    with ctx.workprec(512):
        value = complex(1 / 3, -1 / 7)
        exact = acb(arb(fmpq(1, 3)), arb(fmpq(-1, 7)))
        upper = binary64_error_bound(exact, value)
        dr = Fraction.from_float(value.real) - Fraction(1, 3)
        di = Fraction.from_float(value.imag) + Fraction(1, 7)
        exact_error_squared = fmpq((dr * dr + di * di).numerator,
                                  (dr * dr + di * di).denominator)
        assert upper.is_exact() and upper > 0
        assert upper**2 >= arb(exact_error_squared)
        assert upper < arb("1e-16")


def test_ratio_identity_and_composition_without_conjugation():
    with ctx.workprec(512):
        assert normalized_h_ratio_ball(64, 27).is_exact()
        assert normalized_h_ratio_ball(64, 27).contains(1)
        ab = normalized_h_ratio_ball(28, 55, 27)
        bc = normalized_h_ratio_ball(28, 75, 55)
        ac = normalized_h_ratio_ball(28, 75, 27)
        assert (ab * bc).overlaps(ac)
        assert not (ab.conjugate() * bc).overlaps(ac)


def test_precision_refinement_overlaps_and_reduces_radius():
    low = coulomb_point(64, 75, 384)
    high = coulomb_point(64, 75, 512)
    assert low.impedance.overlaps(high.impedance)
    with ctx.workprec(512):
        assert high.impedance.rad() < low.impedance.rad()


def test_complex_helper_has_an_explicit_analytic_domain_guard():
    with ctx.workprec(256):
        assert outgoing_h_acb(20, acb(65, "0.01")).is_finite()
        assert not outgoing_h_acb(20, acb(arb("0 +/- 1"), 0)).is_finite()
        with pytest.raises(TypeError):
            outgoing_h_acb(20, 65)


def test_source_binding_and_receipt_scope(tmp_path):
    fake = tmp_path / "source.npz"
    fake.write_bytes(b"different source")
    with pytest.raises(ValueError, match="SHA256"):
        certify_points(fake, ells=(0,), radii=(27,))
    source = Path(__file__).parents[1] / "research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"
    receipt = certify_points(source, ells=(21,), radii=(65,))
    assert receipt["point_count"] == 1
    assert receipt["source_sha256"] == "f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
    assert receipt["HH_R10"] == "OFF"
    assert receipt["total_numerical_integration_certified"] is False
    assert receipt["points"][0]["existing_binary64"]["central_impedance_dps"] == 55


@pytest.mark.parametrize("ell,radius,bits", [(-1, 27, 512), (65, 27, 512),
                                            (True, 27, 512), (0, "26.99", 512),
                                            (0, 101, 512), (0, 27, 53)])
def test_contract_scope_is_enforced(ell, radius, bits):
    with pytest.raises(ValueError):
        coulomb_point(ell, radius, bits)
