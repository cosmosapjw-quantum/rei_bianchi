"""Validated local Taylor disks for the original normalized outgoing Coulomb H.

All radii are dimensionless atomic coordinates r/a0.  In particular the
first-order majorant compares (H/H(B), d_(r/a0)H/H(B)); it does not compare
quantities of unequal physical dimension.  The physical derivative is the
second component divided by a0.  k*a0=7/10 and eta_C=-10/7 are fixed.

Only a disk with positive zero-free lower bound produces a reciprocal
certificate.  A failed lower-bound test is unresolved at this disk size;
it is not evidence of a zero.  PHYS63 and PHYS65/66 claims are unchanged.
FLINT precision is process-global: use processes, not concurrent threads.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from typing import Sequence

from flint import acb, arb, ctx, fmpq

from .phys67_coulomb_certificate import (
    B, K, CoulombEnclosureFailure, complex_ball_record, coulomb_point,
    dyadic_ball, exact_radius, outgoing_h_acb,
)

Exact = int | Fraction | str
SHIFT = Fraction(7, 10)


class TaylorEnclosureFailure(CoulombEnclosureFailure):
    """Finite coefficient arithmetic or a requested analytic gate failed."""


def exact_fraction(value: Exact, name: str = "value") -> Fraction:
    """Parse an exact rational input; implicit floating-point input is refused."""
    if type(value) not in (int, Fraction, str):
        raise TypeError(f"{name} requires int, Fraction, or an exact string")
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"{name} must be a finite exact rational") from exc


def rational_ball(value: Fraction | int) -> arb:
    """Enclose an exact rational at the current precision, without a float."""
    if type(value) not in (int, Fraction):
        raise TypeError("rational_ball requires an int or Fraction")
    value = Fraction(value)
    return arb(fmpq(value.numerator, value.denominator))


def dyadic_fraction(value: arb) -> Fraction:
    """Convert an exact finite Arb endpoint to its exact rational value."""
    if not isinstance(value, arb) or not value.is_finite() or not value.is_exact():
        raise ValueError("an exact finite arb endpoint is required")
    mantissa, exponent = value.man_exp()
    mantissa, exponent = int(mantissa), int(exponent)
    if exponent >= 0:
        return Fraction(mantissa << exponent)
    return Fraction(mantissa, 1 << (-exponent))


def _positive(value: Exact, name: str, allow_zero: bool = False) -> Fraction:
    result = exact_fraction(value, name)
    if result < 0 or (not allow_zero and result == 0):
        raise ValueError(f"{name} must be {'nonnegative' if allow_zero else 'positive'}")
    return result


def _integer(value: int, name: str, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} must be an integer in {low}..{high}")
    return value


def inflate_complex(value: acb, absolute_error: arb) -> acb:
    """Add a complex disk via an enclosing dyadic Cartesian error square."""
    if not isinstance(value, acb) or not value.is_finite():
        raise TaylorEnclosureFailure("finite acb required")
    if not isinstance(absolute_error, arb) or not absolute_error.is_finite():
        raise TaylorEnclosureFailure("finite absolute error required")
    upper = absolute_error.upper()
    if absolute_error < 0 or upper < 0:
        raise ValueError("absolute error must be nonnegative")
    if not absolute_error >= 0:
        raise ValueError("absolute error ball must be entirely nonnegative")
    mantissa, exponent = upper.man_exp()
    error = arb(0, (int(mantissa), int(exponent)))
    return value + acb(error, error)


def ode_taylor_coefficients(q_coefficients: Sequence[arb | acb | Exact],
                            h0: acb, h1: acb, degree: int) -> tuple[acb, ...]:
    """Enclose coefficients of h''+Qh=0 for enclosed Q coefficients.

    This algebraic routine alone has no remainder claim.  Its caller must
    supply a justified analytic domain and majorant before making one.
    Q[0] through Q[degree-2] are required; higher entries are ignored.
    """
    degree = _integer(degree, "degree", 1, 256)
    if not isinstance(h0, acb) or not isinstance(h1, acb):
        raise TypeError("initial data must be explicit acb enclosures")
    if not h0.is_finite() or not h1.is_finite():
        raise TaylorEnclosureFailure("initial data are nonfinite")
    if len(q_coefficients) < degree - 1:
        raise ValueError("insufficient Q coefficients")
    qq = []
    for value in q_coefficients[:degree-1]:
        if isinstance(value, acb):
            item = value
        elif isinstance(value, arb):
            item = acb(value)
        else:
            item = acb(rational_ball(exact_fraction(value, "Q coefficient")))
        if not item.is_finite():
            raise TaylorEnclosureFailure("nonfinite Q coefficient")
        qq.append(item)
    coefficients = [h0, h1]
    for n in range(degree - 1):
        convolution = sum((qq[s] * coefficients[n-s] for s in range(n+1)), acb(0))
        coefficients.append(-convolution / ((n+1)*(n+2)))
    if any(not value.is_finite() for value in coefficients):
        raise TaylorEnclosureFailure("Taylor recurrence produced nonfinite coefficients")
    return tuple(coefficients)


def coulomb_q_coefficients(ell: int, center: Exact, count: int) -> tuple[Fraction, ...]:
    """Exact expansion of k^2+2/r-ell(ell+1)/r^2 around center."""
    ell = _integer(ell, "ell", 0, 64)
    count = _integer(count, "count", 0, 255)
    cc = _positive(center, "center")
    return tuple((K*K if n == 0 else Fraction(0))
                 + 2*(-1)**n/cc**(n+1)
                 - ell*(ell+1)*(n+1)*(-1)**n/cc**(n+2)
                 for n in range(count))


@dataclass(frozen=True)
class TaylorDisk:
    """Coefficient enclosures plus a proved sup-norm bound on a closed disk.

    Instances from coulomb_taylor and reciprocal_disk have the derivation
    in research/hh_phys68_20261019/taylor/PROOF.md.  A manually constructed
    instance is conditional on its caller supplying a valid majorant for
    the represented analytic function; validation of that premise is not
    implied by this data container.
    """
    center: Fraction
    radius: Fraction
    coefficients: tuple[acb, ...]
    majorant: arb
    precision_bits: int
    ell: int | None = None
    function: str = "conditional analytic Taylor disk"

    @property
    def degree(self) -> int:
        return len(self.coefficients)-1

    def remainder(self, x: Exact) -> arb:
        """Exact upward endpoint of M (x/R)^(N+1)/(1-x/R), 0<=x<R."""
        xx = _positive(x, "evaluation radius", allow_zero=True)
        if xx >= self.radius:
            raise ValueError("evaluation radius must be strictly below the majorant radius")
        with ctx.workprec(self.precision_bits):
            ratio = rational_ball(xx/self.radius)
            result = self.majorant * ratio**(self.degree+1)/(1-ratio)
            if not result.is_finite():
                raise TaylorEnclosureFailure("nonfinite Cauchy remainder")
            return result.upper()

    def evaluate(self, offset: Exact | arb | acb) -> acb:
        """Enclose the full function for every point in an explicit offset ball."""
        with ctx.workprec(self.precision_bits):
            if isinstance(offset, acb):
                zz = offset
            elif isinstance(offset, arb):
                zz = acb(offset)
            else:
                zz = acb(rational_ball(exact_fraction(offset, "offset")))
            if not zz.is_finite():
                raise ValueError("offset must be finite")
            extent = dyadic_fraction(zz.abs_upper())
            error = self.remainder(extent)
            value = acb(0)
            for coefficient in reversed(self.coefficients):
                value = value * zz + coefficient
            return inflate_complex(value, error)

    def zero_free_lower(self, rho: Exact) -> arb:
        """Signed exact lower endpoint for |function| on |z-center|<=rho.

        Only a strictly positive return proves a zero-free closed disk.
        Zero or a negative result means that this estimate is unresolved.
        """
        rr = _positive(rho, "zero-free radius", allow_zero=True)
        if rr >= self.radius:
            raise ValueError("zero-free radius must be below the majorant radius")
        with ctx.workprec(self.precision_bits):
            rball = rational_ball(rr)
            variation = arb(0)
            power = rball
            for coefficient in self.coefficients[1:]:
                variation += coefficient.abs_upper() * power
                power *= rball
            lower = self.coefficients[0].abs_lower() - variation - self.remainder(rr)
            if not lower.is_finite():
                raise TaylorEnclosureFailure("nonfinite zero-free bound")
            return lower.lower()

    def reciprocal_majorant(self, rho: Exact) -> arb:
        """Prove |1/function|<=1/lower on the requested zero-free disk."""
        with ctx.workprec(self.precision_bits):
            lower = self.zero_free_lower(rho)
            if not lower > 0:
                raise TaylorEnclosureFailure("UNRESOLVED_ZERO_FREE_BOUND: reduce the disk radius")
            return (1/lower).upper()

    def reciprocal_disk(self, rho: Exact) -> TaylorDisk:
        """Return enclosed reciprocal coefficients and their justified Cauchy bound."""
        rr = _positive(rho, "reciprocal radius")
        with ctx.workprec(self.precision_bits):
            bound = self.reciprocal_majorant(rr)
            h0 = self.coefficients[0]
            if h0.contains(0):
                raise TaylorEnclosureFailure("reciprocal coefficient denominator unresolved")
            inverse = [1/h0]
            for n in range(1, self.degree+1):
                inverse.append(-sum((self.coefficients[j]*inverse[n-j]
                                     for j in range(1,n+1)), acb(0))/h0)
            if any(not value.is_finite() for value in inverse):
                raise TaylorEnclosureFailure("reciprocal recurrence is nonfinite")
            return TaylorDisk(self.center, rr, tuple(inverse), bound,
                              self.precision_bits, self.ell, f"1/({self.function})")

    def as_record(self, include_coefficients: bool = True) -> dict:
        with ctx.workprec(self.precision_bits):
            record = {
                "function": self.function, "ell": self.ell,
                "center_r_over_a0": str(self.center),
                "majorant_disk_radius_over_a0": str(self.radius),
                "degree": self.degree, "precision_bits": self.precision_bits,
                "majorant_upper": dyadic_ball(self.majorant),
                "coordinate_derivative": "d_(r/a0); physical d_r=(1/a0)*d_(r/a0)",
                "HH_R10": "OFF",
            }
            if include_coefficients:
                record["coefficients"] = [complex_ball_record(x) for x in self.coefficients]
            return record


CoulombTaylor = TaylorDisk


@lru_cache(maxsize=130)
def _normalizer(ell: int, bits: int) -> acb:
    with ctx.workprec(bits):
        value = outgoing_h_acb(ell, acb(rational_ball(B)))
        if not value.is_finite() or value.contains(0):
            raise TaylorEnclosureFailure("normalizing H+(B) is unresolved")
        return value


@lru_cache(maxsize=256)
def _center_data(ell: int, center: Fraction, bits: int) -> tuple[acb, acb]:
    point = coulomb_point(ell, center, bits)
    with ctx.workprec(bits):
        normalizer = _normalizer(ell, bits)
        h0 = acb(1) if center == B else point.h_plus/normalizer
        h1 = point.h_prime_r/normalizer
        return h0, h1


def coulomb_taylor(ell: int, center: Exact, degree: int = 64,
                   majorant_radius: Exact = 2,
                   precision_bits: int = 384) -> TaylorDisk:
    """Certified H_l^+(r)/H_l^+(27) Taylor disk for the fixed original Coulomb model.

    Initial H and d_r H are supplied by the unchanged PHYS67 point routine.
    The closed majorant disk must satisfy center-radius>7/10.  Its ODE
    sup bound is max(|h0|,|h1|)*exp(R*max(1,k^2+2/(c-R)+l(l+1)/(c-R)^2)).
    """
    ell = _integer(ell, "ell", 0, 64)
    cc = exact_radius(center)
    degree = _integer(degree, "degree", 1, 256)
    rr = _positive(majorant_radius, "majorant radius")
    bits = _integer(precision_bits, "precision_bits", 128, 4096)
    if cc-rr <= SHIFT:
        raise ValueError("the whole majorant disk must obey Re(r)>7/10")
    with ctx.workprec(bits):
        h0, h1 = _center_data(ell, cc, bits)
        coefficients = ode_taylor_coefficients(
            coulomb_q_coefficients(ell, cc, degree-1), h0, h1, degree)
        gap = cc-rr
        q_upper = K*K + 2/gap + ell*(ell+1)/gap**2
        matrix_upper = max(Fraction(1), q_upper)
        initial_upper = max(h0.abs_upper(), h1.abs_upper())
        majorant = (initial_upper * rational_ball(rr*matrix_upper).exp()).upper()
        if not majorant.is_finite() or not majorant >= 0:
            raise TaylorEnclosureFailure("nonfinite ODE disk majorant")
        return TaylorDisk(cc, rr, coefficients, majorant, bits, ell,
                          "H_l^+(r)/H_l^+(27), k=7/10, eta_C=-10/7")
