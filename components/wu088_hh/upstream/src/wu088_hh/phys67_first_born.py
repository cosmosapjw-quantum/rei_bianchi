"""Certified original m=0 first Born entry by elementary angular integration.

The angular integral is reduced exactly to a Laurent polynomial in r and
exp(-2r). FLINT's complex-ball quadrature encloses the remaining radial
integral. Radii are numerical r/a0 and the result is in a0^-1. No original
source-driven xi or higher Born coefficient is computed by this module.
"""
from __future__ import annotations

from fractions import Fraction as F
from functools import lru_cache
from math import comb, factorial
from pathlib import Path
from time import perf_counter
import hashlib
import importlib.metadata

from flint import acb, arb, ctx, fmpq

from .phys63_lap_contract import source_guard
from .phys66_radial_budget import coefficient_bounds

R = F(7, 10)
B = F(27)


def _exact(value):
    if isinstance(value, (float, bool)):
        raise ValueError("use an exact rational, integer or decimal string")
    return F(value)


def _q(value):
    value = F(value)
    return arb(fmpq(value.numerator, value.denominator))


def _ell(value):
    if type(value) is not int or not 0 <= value <= 64:
        raise ValueError("integer ell in 0..64 required")
    return value


@lru_cache(maxsize=65)
def legendre_coefficients(ell):
    """Exact monomial coefficients of the ordinary Legendre polynomial."""
    _ell(ell)
    out = [F(0)] * (ell + 1)
    for j in range(ell // 2 + 1):
        out[ell - 2*j] = F((-1)**j * factorial(2*ell - 2*j),
            2**ell * factorial(j) * factorial(ell-j) * factorial(ell-2*j))
    return tuple(out)


@lru_cache(maxsize=260)
def exponential_moment_pair(degree):
    """Exact A,B with integral[-R,R] t^degree exp(-2t)dt=A exp(2R)+B exp(-2R)."""
    if type(degree) is not int or not 0 <= degree <= 260:
        raise ValueError("bounded nonnegative polynomial degree required")
    def primitive(t):
        return sum((F(factorial(degree), factorial(degree-j)*2**(j+1))
                    * t**(degree-j) for j in range(degree+1)), F(0))
    return primitive(-R), -primitive(R)


@lru_cache(maxsize=128)
def angular_laurent_pairs(ell, ellprime):
    """Exact pairs C_k for V_l,l'(r)=sqrt((2l+1)(2l'+1))/R * exp(-2r) sum C_k/r^k.

    C_k=A_k exp(2R)+B_k exp(-2R). Substitute d=r+t,
    mu=-t/R+(R^2-t^2)/(2Rr), and integrate (r+t+1)P_l(mu)P_l'(mu).
    The two factors 2 in V=2S and normalized m=0 basis cancel exactly.
    """
    _ell(ell); _ell(ellprime)
    pl = legendre_coefficients(ell); pp = legendre_coefficients(ellprime)
    degree = ell + ellprime
    product = [F(0)] * (degree + 1)
    for i, a in enumerate(pl):
        for j, b in enumerate(pp):
            product[i+j] += a*b
    pairs = [[F(0), F(0)] for _ in range(degree + 2)]
    # mu^j: coefficient of r^-k has degree j-k+2s in t.
    for j, coefficient in enumerate(product):
        if not coefficient:
            continue
        for k in range(j + 1):
            common = coefficient * comb(j, k) * (-1/R)**(j-k) / (2*R)**k
            for s in range(k + 1):
                factor = common * comb(k, s) * R**(2*(k-s)) * (-1)**s
                n = j-k+2*s
                m0 = exponential_moment_pair(n)
                m1 = exponential_moment_pair(n+1)
                for endpoint in (0, 1):
                    pairs[k][endpoint] += factor*m0[endpoint]
                    pairs[k+1][endpoint] += factor*(m0[endpoint]+m1[endpoint])
    return tuple(tuple(x) for x in pairs)


def angular_coefficients_ball(ell, ellprime, precision_bits=768):
    """Prepare constant ball coefficients; all endpoint cancellations are enclosed."""
    if type(precision_bits) is not int or not 128 <= precision_bits <= 4096:
        raise ValueError("precision_bits in 128..4096 required")
    pairs = angular_laurent_pairs(ell, ellprime)
    with ctx.workprec(precision_bits):
        ep = (2*_q(R)).exp(); em = (-2*_q(R)).exp()
        return tuple(_q(a)*ep + _q(b)*em for a, b in pairs)


def angular_entry_acb(ell, ellprime, radius, coefficients=None):
    """Analytic physical V entry for m=0 on Re(r)>R, including every angular term."""
    _ell(ell); _ell(ellprime)
    radius = acb(radius)
    if not radius.real > _q(R):
        return acb("nan")
    if coefficients is None:
        coefficients = angular_coefficients_ball(ell, ellprime, max(ctx.prec, 768))
    reciprocal = 1/radius
    poly = acb(0)
    for value in reversed(coefficients):
        poly = poly*reciprocal + value
    return arb((2*ell+1)*(2*ellprime+1)).sqrt()/_q(R) * (-2*radius).exp()*poly


def _dyadic(value):
    mantissa, exponent = value.man_exp()
    return {"mantissa": str(mantissa), "exponent2": int(exponent)}


def serialize_ball(value):
    """Exact binary midpoint/radius encoding; decimal strings are display only."""
    value = acb(value)
    if not value.is_finite():
        raise ArithmeticError("nonfinite enclosure")
    return {"real": {"mid": _dyadic(value.real.mid()), "rad": _dyadic(value.real.rad())},
            "imag": {"mid": _dyadic(value.imag.mid()), "rad": _dyadic(value.imag.rad())}}


def dyadic_fraction(item):
    m = int(item["mantissa"]); e = item["exponent2"]
    return F(m * 2**e) if e >= 0 else F(m, 2**(-e))


def component_radii(value):
    return dyadic_fraction(_dyadic(value.real.rad())), dyadic_fraction(_dyadic(value.imag.rad()))


def integrate_first_born(source: str | Path, ell=21, ellprime=20, outer=65,
                         precision_bits=384, coefficient_bits=1024,
                         absolute_goal="1e-42", relative_goal="1e-18",
                         eval_limit=20000, panel_width=4):
    """Enclose the full-radial original first Born entry with a separate tail bound.

    The FLINT callback explicitly verifies its analytic domain for complex
    test balls. The actual returned radius, not a requested tolerance, is
    used to decide numerical acceptance. All internal ball radii are retained.
    """
    from .phys67_coulomb_certificate import outgoing_h_acb
    digest = source_guard(source)
    _ell(ell); _ell(ellprime)
    outer = _exact(outer); goal = _exact(absolute_goal); rel = _exact(relative_goal)
    width = _exact(panel_width)
    if not B < outer <= 80 or goal <= 0 or not 0 < rel < 1 or width <= 0:
        raise ValueError("bounded exact radius, panel width and positive accuracy goals required")
    if type(eval_limit) is not int or not 100 <= eval_limit <= 200000:
        raise ValueError("bounded evaluation limit required")
    if type(precision_bits) is not int or not 128 <= precision_bits <= 2048:
        raise ValueError("precision_bits in 128..2048 required")
    if type(coefficient_bits) is not int or not precision_bits <= coefficient_bits <= 4096:
        raise ValueError("coefficient precision must cover integration precision")
    begin = perf_counter(); count = 0; rejected = 0
    coefficients = angular_coefficients_ball(ell, ellprime, coefficient_bits)
    panels = []
    left = B
    while left < outer:
        right = min(left+width, outer); panels.append((left, right)); left = right
    with ctx.workprec(precision_bits):
        hB = outgoing_h_acb(ell, acb(_q(B)))
        hpB = outgoing_h_acb(ellprime, acb(_q(B)))
        if hB.contains(0) or hpB.contains(0):
            raise ArithmeticError("Coulomb reference denominator not separated from zero")
        denominator = hB*hpB
        def callback(radius, analytic):
            nonlocal count, rejected
            count += 1
            if not radius.real > _q(R):
                rejected += 1
                return acb("nan")
            return (outgoing_h_acb(ell, radius)*outgoing_h_acb(ellprime, radius)/denominator
                    * angular_entry_acb(ell, ellprime, radius, coefficients))
        total = acb(0); panel_records = []
        for left, right in panels:
            value = acb.integral(callback, acb(_q(left)), acb(_q(right)),
                # Reserve a factor eight for Cartesian-ball L1 conversion,
                # panel summation and conservative enclosure inflation. The
                # measured returned radius remains the acceptance authority.
                abs_tol=_q(goal/(8*len(panels))), rel_tol=_q(rel),
                eval_limit=eval_limit, depth_limit=30, deg_limit=100)
            if not value.is_finite():
                raise ArithmeticError(f"nonfinite radial enclosure on [{left},{right}]")
            total += value
            panel_records.append({"left": str(left), "right": str(right),
                                  "enclosure": serialize_ball(value)})
        radial = coefficient_bounds(max(ell,ellprime), outer, 1)["terms"][0]["radial_cutoff_bound"]
        real_radius, imag_radius = component_radii(total)
        # L1 radius bounds the complex Euclidean error; no binary-float rounding enters.
        numerical_upper = real_radius + imag_radius
        exact_serialized = serialize_ball(total)
        # Widen each Cartesian component by the proved complex-norm tail.
        error_ball = acb(arb(0, _q(radial)), arb(0, _q(radial)))
        full = total + error_ball
        return {"schema": "PHYS67_FIRST_BORN_CERTIFICATE_V1", "source_sha256": digest,
            "ell": ell, "ellprime": ellprime, "m": 0, "B": "27", "outer": str(outer),
            "k": "7/10", "eta_C": "-10/7", "energy_Hartree": "49/200",
            "unit": "a0^-1", "precision_bits": precision_bits,
            "coefficient_bits": coefficient_bits, "absolute_goal": str(goal),
            "relative_goal": str(rel), "function_evaluations": count,
            "nonanalytic_ball_rejections": rejected, "wall_seconds": perf_counter()-begin,
            "versions": {n: importlib.metadata.version(n) for n in ("python-flint", "numpy", "scipy")},
            "cutoff_enclosure": exact_serialized, "full_radial_enclosure": serialize_ball(full),
            "cutoff_display": str(total), "full_radial_display": str(full),
            "numerical_complex_error_upper": {"numerator": str(numerical_upper.numerator), "denominator_hex": format(numerical_upper.denominator,'x')},
            "analytic_radial_tail_upper": {"numerator_hex": format(radial.numerator,'x'), "denominator_hex": format(radial.denominator,'x')},
            "actual_numerical_goal_met": numerical_upper <= goal,
            "angular_integration": "EXACT_ELEMENTARY_POLYNOMIAL_IDENTITY_M0",
            "panels": panel_records,
            "scope": "ONE_EXACT_ORIGINAL_FIRST_BORN_ENTRY;NO_SOURCE_DRIVEN_XI;NO_D2_D3_CERTIFICATE",
            "all_angular_first_order_entry": True,
            "higher_order_and_driven_obligations": "OPEN", "HH_R10": "OFF"}
