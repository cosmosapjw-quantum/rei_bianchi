"""Pointwise Coulomb wave/impedance enclosures for the original HH exterior.

Coordinates are r/a0, k=7/10, E=49/200 Hartree, eta_C=-10/7.
H+=G+iF and Z=+d_r H+/H+ (in a0^-1).  This module certifies special
function evaluation, including a supplied binary64 value's error, at exact
points.  PHYS65's full-radial analytic bound and PHYS63's existence result
are unchanged.  A point certificate does not certify a numerical ODE path.

Optional dependency: python-flint (validated with 0.8.0 / FLINT 3.3.1).
The FLINT precision/cap context is process-global; use separate processes,
not threads with different precision contexts.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable
import hashlib
import math
import platform
import sys

import flint
from flint import acb, arb, arb_series, ctx, fmpq

from .phys65_exterior_bounds import source_guard

K = Fraction(7, 10)
ETA_C = Fraction(-10, 7)
B = Fraction(27)
ExactRadius = int | Fraction | str


class CoulombEnclosureFailure(ArithmeticError):
    """The requested precision did not resolve a finite certified value."""


def exact_radius(value: ExactRadius) -> Fraction:
    """A decimal string denotes that exact decimal, never a rounded float."""
    if type(value) not in (int, Fraction, str):
        raise TypeError("radius requires int, Fraction, or exact decimal/rational string")
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError("radius must be a finite exact rational") from exc
    if not B <= result <= 100:
        raise ValueError("point-certificate radius scope is 27 <= r <= 100")
    return result


def _ell(ell: int) -> int:
    if type(ell) is not int or not 0 <= ell <= 64:
        raise ValueError("ell must be an integer in 0..64")
    return ell


def _precision(bits: int) -> int:
    if type(bits) is not int or not 128 <= bits <= 4096:
        raise ValueError("precision_bits must be an integer in 128..4096")
    return bits


def _ball(q: Fraction) -> arb:
    return arb(fmpq(q.numerator, q.denominator))


def outgoing_h_acb(ell: int, radius: acb) -> acb:
    """H+ on Re(r)>0, at the caller's precision, for validated integration.

    radius must already be an acb ball.  Returning indeterminate outside
    the right half-plane forces the integrator to subdivide or fail, so
    branch-cut/origin crossings cannot be silently treated as analytic.
    The exact rational physical parameters are enclosed at current prec.
    """
    _ell(ell)
    if not isinstance(radius, acb):
        raise TypeError("radius must already be an acb ball")
    if not radius.is_finite() or not radius.real > 0:
        return acb("nan")
    return (radius * _ball(K)).coulomb(ell, _ball(ETA_C))[2]


def dyadic_ball(value: arb) -> dict:
    """Exact binary midpoint/radius; decimal display is informational only."""
    if not value.is_finite():
        raise CoulombEnclosureFailure("cannot serialize a nonfinite ball")
    mm, me = value.mid().man_exp()
    rm, re = value.rad().man_exp()
    return {"midpoint": {"mantissa": str(mm), "exponent2": int(me)},
            "radius": {"mantissa": str(rm), "exponent2": int(re)},
            "display": value.str(24)}


def restore_ball(data: dict) -> arb:
    """Restore the stored dyadic enclosure, rounding outward if necessary."""
    def pair(key):
        return int(data[key]["mantissa"]), int(data[key]["exponent2"])
    return arb(pair("midpoint"), pair("radius"))


def complex_ball_record(value: acb) -> dict:
    return {"real": dyadic_ball(value.real), "imag": dyadic_ball(value.imag)}


def restore_complex_ball(data: dict) -> acb:
    return acb(restore_ball(data["real"]), restore_ball(data["imag"]))


def _exact_binary64(value: complex) -> acb:
    if type(value) is not complex or not all(map(math.isfinite, (value.real, value.imag))):
        raise ValueError("a finite Python complex (two binary64 values) is required")
    nr, dr = value.real.as_integer_ratio()
    ni, di = value.imag.as_integer_ratio()
    return acb(arb(fmpq(nr, dr)), arb(fmpq(ni, di)))


def binary64_error_bound(enclosure: acb, approximation: complex,
                         precision_bits: int = 512) -> arb:
    """Exact dyadic upward bound on |approximation - mathematical value|.

    The central value may come from any implementation.  No accuracy
    claim about that implementation is used to prove this error bound.
    """
    with ctx.workprec(_precision(precision_bits)):
        if not enclosure.is_finite():
            raise CoulombEnclosureFailure("nonfinite reference enclosure")
        return (_exact_binary64(approximation) - enclosure).abs_upper()


def _tricomi_impedance(ell: int, rho: arb) -> acb:
    """DLMF 33.2.8 + 13.3.22; differentiate the defining U expression."""
    eta = _ball(ETA_C)
    aa = acb(ell + 1, eta)
    zz = acb(0, -2 * rho)
    uu = zz.hypgeom_u(aa, 2 * ell + 2)
    if not uu.is_finite() or uu.contains(0):
        raise CoulombEnclosureFailure("Tricomi U denominator unresolved; increase precision")
    u1 = zz.hypgeom_u(aa + 1, 2 * ell + 3)
    answer = _ball(K) * ((ell + 1) / rho + acb(0, 1) + 2 * acb(0, 1) * aa * u1 / uu)
    if not answer.is_finite():
        raise CoulombEnclosureFailure("Tricomi derivative enclosure is nonfinite")
    return answer


@dataclass(frozen=True)
class CoulombPoint:
    ell: int
    radius: Fraction
    precision_bits: int
    h_plus: acb
    h_prime_r: acb
    impedance: acb
    impedance_tricomi: acb
    wronskian_rho: arb
    ode_residual_f: arb
    ode_residual_g: arb

    def as_record(self) -> dict:
        with ctx.workprec(self.precision_bits):
            return {
                "ell": self.ell, "r_over_a0": str(self.radius),
                "precision_bits": self.precision_bits,
                "h_plus": complex_ball_record(self.h_plus),
                "d_r_h_plus": complex_ball_record(self.h_prime_r),
                "impedance_a0_inverse": complex_ball_record(self.impedance),
                "impedance_definition_check": complex_ball_record(self.impedance_tricomi),
                "wronskian_rho": dyadic_ball(self.wronskian_rho),
                "ode_residual_f": dyadic_ball(self.ode_residual_f),
                "ode_residual_g": dyadic_ball(self.ode_residual_g),
                "impedance_radius_upper": dyadic_ball(self.impedance.rad()),
                "outgoing_imag_strictly_positive": bool(self.impedance.imag > 0),
                "definition_overlap": bool(self.impedance.overlaps(self.impedance_tricomi)),
            }


def coulomb_point(ell: int, radius: ExactRadius,
                 precision_bits: int = 512) -> CoulombPoint:
    """Enclose H+, d_r H+, Z and check Wronskian/ODE/defining derivative."""
    ell, rr, bits = _ell(ell), exact_radius(radius), _precision(precision_bits)
    with ctx.workprec(bits):
        k, eta = _ball(K), _ball(ETA_C)
        rho = k * _ball(rr)
        ff, gg = rho.coulomb(ell, eta)
        f1, g1 = rho.coulomb(ell + 1, eta)
        ss = (ell + 1) / rho + eta / (ell + 1)
        rt = (1 + (eta / (ell + 1))**2).sqrt()
        fp, gp = ss * ff - rt * f1, ss * gg - rt * g1
        hh, hp = acb(gg, ff), k * acb(gp, fp)
        if not hh.is_finite() or hh.contains(0):
            raise CoulombEnclosureFailure("H+ denominator unresolved; increase precision")
        zz = hp / hh
        ww = gg * fp - ff * gp  # rho derivative: G F' - F G' = +1
        cap = ctx.cap
        try:
            ctx.cap = 3
            fs, gs = arb_series([rho, 1]).coulomb(ell, eta)
        finally:
            ctx.cap = cap
        qq = 1 - 2 * eta / rho - ell * (ell + 1) / rho**2
        rf, rg = 2 * fs[2] + qq * fs[0], 2 * gs[2] + qq * gs[0]
        # Series jets and recurrence can share FLINT internals.  They are
        # consistency checks, not independent software implementations.
        zjet = k * acb(gs[1], fs[1]) / acb(gs[0], fs[0])
        zdef = _tricomi_impedance(ell, rho)
        checks = (zz.is_finite(), zz.imag > 0, ww.contains(1), ww > 0,
                  rf.contains(0), rg.contains(0), zz.overlaps(zjet),
                  zjet.is_finite(), zz.overlaps(zdef))
        if not all(checks):
            raise CoulombEnclosureFailure("Coulomb sign/normalization/definition check failed")
        return CoulombPoint(ell, rr, bits, hh, hp, zz, zdef, ww, rf, rg)


def normalized_h_ratio_ball(ell: int, radius: ExactRadius,
                            reference_radius: ExactRadius = 27,
                            precision_bits: int = 512) -> acb:
    """Enclose H+(r)/H+(reference), dimensionless, at two exact points."""
    ell = _ell(ell)
    rr, rb = exact_radius(radius), exact_radius(reference_radius)
    with ctx.workprec(_precision(precision_bits)):
        if rr == rb:
            return acb(1)  # analytic same-argument identity; no lost correlation
        hh = outgoing_h_acb(ell, acb(_ball(rr)))
        hb = outgoing_h_acb(ell, acb(_ball(rb)))
        if not hb.is_finite() or hb.contains(0):
            raise CoulombEnclosureFailure("normalizing H+ unresolved")
        ratio = hh / hb
        if not ratio.is_finite():
            raise CoulombEnclosureFailure("normalized H+ ratio unresolved")
        return ratio


def certify_points(source: str | Path, ells: Iterable[int] = (0, 20, 21, 28, 64),
                   radii: Iterable[ExactRadius] = (27, 55, 65, 75),
                   precision_bits: int = 512, compare_existing_binary64: bool = True) -> dict:
    """Source-locked receipt.  No PHYS64/PHYS66 campaign is executed."""
    digest = source_guard(source)
    ells, radii = tuple(map(_ell, ells)), tuple(map(exact_radius, radii))
    if not ells or not radii or len(set(ells)) != len(ells) or len(set(radii)) != len(radii):
        raise ValueError("nonempty distinct ell and radius lists required")
    bits = _precision(precision_bits)
    rows = []
    if compare_existing_binary64:
        from .phys63_scaled_riccati import central_impedance
    for ell in ells:
        for rr in radii:
            point = coulomb_point(ell, rr, bits)
            row = point.as_record()
            with ctx.workprec(bits):
                ratio = normalized_h_ratio_ball(ell, rr, B, bits)
                row["h_over_h_B"] = complex_ball_record(ratio)
                row["ratio_radius_upper"] = dyadic_ball(ratio.rad())
                if compare_existing_binary64:
                    # The legacy API converts str(radius) back to mpmath.
                    # Restrict comparison to exactly representable integer
                    # inputs here, avoiding a silently altered decimal radius.
                    if rr.denominator != 1:
                        raise ValueError("legacy binary64 comparison currently requires integer radii")
                    approx = central_impedance(ell, float(rr), dps=55)
                    error = binary64_error_bound(point.impedance, approx, bits)
                    row["existing_binary64"] = {
                        "real_hex": approx.real.hex(), "imag_hex": approx.imag.hex(),
                        "absolute_error_upper": dyadic_ball(error),
                        "central_impedance_dps": 55,
                    }
            rows.append(row)
    return {
        "schema": "PHYS67_COULOMB_POINT_CERTIFICATE_V1",
        "status": "IMPLEMENTATION_VERIFIED_POINTWISE_BALL_ENCLOSURES",
        "source_sha256": digest,
        "physical_contract": {"coordinates": "r/a0", "k": "7/10", "E_Hartree": "49/200",
                              "eta_C": "-10/7", "H_plus": "G+iF", "Z": "+d_r H_plus/H_plus",
                              "eta_source": "Fy", "xi_source": "Fy-phi"},
        "environment": {"python": sys.version, "platform": platform.platform(),
                        "python_flint": flint.__version__,
                        "flint": getattr(flint, "__FLINT_VERSION__", "unknown")},
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "legacy_code_sha256": hashlib.sha256(Path(__file__).with_name("phys63_scaled_riccati.py").read_bytes()).hexdigest(),
        "precision_bits": bits, "point_count": len(rows), "points": rows,
        "serialization": "exact dyadic midpoint/radius; display strings are not certificate endpoints",
        "total_numerical_integration_certified": False,
        "excluded_angular_error_certified": False,
        "HH_R10": "OFF",
    }
