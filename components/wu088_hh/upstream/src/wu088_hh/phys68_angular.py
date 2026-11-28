"""Exact cached m=0 angular kernels and ball Taylor coefficients.

The physical radial potential is V=2(1+1/d)exp(-2d), with R=7/10
and d^2=r^2+R^2-2rR*mu. Radii are numerical r/a0 and V has units
a0^-2. This module retains every angular term in a selected entry.

Only exact Fraction algebra is cached independently of precision. Ball
caches additionally include their precision. Taylor outputs enclose the
coefficients V^(n)(center)/n!, not an unbounded interpolation of samples.
FLINT's process-global precision and series cap are restored on return;
concurrent requests with different contexts must use separate processes.
"""
from __future__ import annotations

from fractions import Fraction as F
from functools import lru_cache
from math import comb

from flint import acb, acb_series, arb, ctx, fmpq

from .phys67_first_born import (
    R, exponential_moment_pair, legendre_coefficients,
)


def _exact(value):
    if isinstance(value, (float, bool, complex)):
        raise ValueError("use exact integer, Fraction or decimal string inputs")
    try:
        return F(value)
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise ValueError("a finite exact real rational input is required") from exc


def _q(value):
    value = F(value)
    return arb(fmpq(value.numerator, value.denominator))


def _ell(value):
    if type(value) is not int or not 0 <= value <= 64:
        raise ValueError("integer ell in 0..64 required")
    return value


def _bits(value):
    if type(value) is not int or not 128 <= value <= 4096:
        raise ValueError("precision_bits in 128..4096 required")
    return value


def _degree(value, maximum=512):
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(f"integer degree in 0..{maximum} required")
    return value


@lru_cache(maxsize=129)
def monomial_laurent_pairs(degree):
    """Endpoint pairs for integral exp(-2t) mu^j[1+(t+1)/r] dt.

    mu=-t/R+(R^2-t^2)/(2Rr), t in [-R,R]. If this function
    returns (A_k,B_k), its integral is exactly
    sum_k (A_k*exp(2R)+B_k*exp(-2R))*r^(-k).
    Each monomial j=0..128 is constructed at most once per cache lifetime.
    """
    _degree(degree, 128)
    pairs = [[F(0), F(0)] for _ in range(degree + 2)]
    for k in range(degree + 1):
        common = comb(degree, k) * (-1/R)**(degree-k) / (2*R)**k
        for s in range(k + 1):
            factor = common * comb(k, s) * R**(2*(k-s)) * (-1)**s
            n = degree-k+2*s
            m0 = exponential_moment_pair(n)
            m1 = exponential_moment_pair(n+1)
            for endpoint in (0, 1):
                pairs[k][endpoint] += factor*m0[endpoint]
                pairs[k+1][endpoint] += factor*(m0[endpoint]+m1[endpoint])
    return tuple(tuple(pair) for pair in pairs)


@lru_cache(maxsize=512)
def _canonical_laurent_pairs(ell, ellprime):
    degree = ell + ellprime
    product = [F(0)] * (degree + 1)
    for i, a in enumerate(legendre_coefficients(ell)):
        if a:
            for j, b in enumerate(legendre_coefficients(ellprime)):
                if b:
                    product[i+j] += a*b
    pairs = [[F(0), F(0)] for _ in range(degree + 2)]
    for j, coefficient in enumerate(product):
        if coefficient:
            for k, endpoints in enumerate(monomial_laurent_pairs(j)):
                pairs[k][0] += coefficient*endpoints[0]
                pairs[k][1] += coefficient*endpoints[1]
    return tuple(tuple(pair) for pair in pairs)


def angular_laurent_pairs(ell, ellprime):
    """Exact PHYS67-compatible Laurent pairs, sharing symmetric entries.

    V_l,p(r)=sqrt((2l+1)(2p+1))/R * exp(-2r)
             * sum_k (A_k exp(2R)+B_k exp(-2R))/r^k.
    The identity is bilinear and introduces no complex conjugation.
    """
    _ell(ell); _ell(ellprime)
    return _canonical_laurent_pairs(*sorted((ell, ellprime)))


@lru_cache(maxsize=512)
def _canonical_coefficients_ball(ell, ellprime, precision_bits):
    pairs = angular_laurent_pairs(ell, ellprime)
    with ctx.workprec(precision_bits):
        positive = (2*_q(R)).exp()
        negative = (-2*_q(R)).exp()
        return tuple(_q(a)*positive + _q(b)*negative for a, b in pairs)


def angular_coefficients_ball(ell, ellprime, precision_bits=1024):
    """Return constant arb coefficients, including endpoint cancellation.

    Ball cache keys contain (min(l,p), max(l,p), precision_bits). A lower
    precision request cannot populate or replace a higher precision key.
    Returning finite balls does not assert any requested relative accuracy.
    """
    _ell(ell); _ell(ellprime); _bits(precision_bits)
    return _canonical_coefficients_ball(*sorted((ell, ellprime)), precision_bits)


def angular_entry_acb(ell, ellprime, radius, coefficients=None):
    """Enclose analytic V_l,p for a complex ball with Re(radius)>R."""
    _ell(ell); _ell(ellprime)
    if isinstance(radius, (float, complex, bool)):
        raise ValueError("pass an exact value or an explicit containing acb ball")
    if isinstance(radius, F):
        radius = acb(_q(radius))
    else:
        radius = acb(radius)
    if not radius.real > _q(R):
        return acb("nan")
    if coefficients is None:
        coefficients = angular_coefficients_ball(ell, ellprime, max(ctx.prec, 1024))
    if len(coefficients) != ell+ellprime+2:
        raise ValueError("coefficient count does not match the angular pair")
    reciprocal = 1/radius
    polynomial = acb(0)
    for coefficient in reversed(coefficients):
        polynomial = polynomial*reciprocal + coefficient
    factor = arb((2*ell+1)*(2*ellprime+1)).sqrt()/_q(R)
    return factor * (-2*radius).exp() * polynomial


def angular_taylor_coefficients(ell, ellprime, center, degree,
                               precision_bits=384, coefficient_bits=1024):
    """Enclose V_l,p(center+x) through degree as a tuple of acb values.

    Center is an exact real rational strictly greater than R. Values are
    Taylor coefficients (derivatives divided by factorial), including
    exp(-2r) and the physical normalization. A separate analytic remainder
    bound is required to evaluate the truncated series away from center.
    """
    _ell(ell); _ell(ellprime); _degree(degree)
    _bits(precision_bits); _bits(coefficient_bits)
    center = _exact(center)
    if center <= R:
        raise ValueError("Taylor center must be strictly greater than R=7/10")
    if coefficient_bits < precision_bits:
        raise ValueError("coefficient_bits must cover precision_bits")
    coefficients = angular_coefficients_ball(ell, ellprime, coefficient_bits)
    previous_cap = ctx.cap
    try:
        ctx.cap = degree+1
        with ctx.workprec(precision_bits):
            radial = acb_series([acb(_q(center)), acb(1)], prec=degree+1)
            reciprocal = radial.inv()
            polynomial = acb_series([acb(0)], prec=degree+1)
            for coefficient in reversed(coefficients):
                polynomial = polynomial*reciprocal + coefficient
            factor = arb((2*ell+1)*(2*ellprime+1)).sqrt()/_q(R)
            series = polynomial * (-2*radial).exp() * factor
            result = tuple(series[j] for j in range(degree+1))
            if not all(value.is_finite() for value in result):
                raise ArithmeticError("nonfinite angular Taylor coefficient")
            return result
    finally:
        ctx.cap = previous_cap


def angular_complex_disk_bound(center, disk_radius, precision_bits=384):
    """Upward point bound for every normalized angular entry on |r-c|<=s.

    For exact real c and s>=0 with a=c-s-R>0, the principal distance has
    Re(d)>=a and |d|>=a for real mu in [-1,1]. The norm of multiplication
    by V bounds every normalized matrix entry, giving
    M_V=2(1+1/a)exp(-2a). The returned exact arb endpoint rounds upward.
    """
    _bits(precision_bits)
    center = _exact(center); disk_radius = _exact(disk_radius)
    a = center-disk_radius-R
    if disk_radius < 0 or a <= 0:
        raise ValueError("nonnegative disk_radius and center-disk_radius>R required")
    with ctx.workprec(precision_bits):
        aa = _q(a)
        bound = 2*(1+1/aa)*(-2*aa).exp()
        if not bound.is_finite() or not bound > 0:
            raise ArithmeticError("positive finite angular disk majorant unresolved")
        return bound.upper()


def angular_taylor_remainder_bound(center, disk_radius, step_radius, degree,
                                  precision_bits=384):
    """Upward Cauchy remainder M*q^(degree+1)/(1-q), q=h/s<1.

    The step_radius bounds |x|. This bounds truncation only; evaluating
    the returned Taylor coefficient balls additionally propagates their
    arithmetic uncertainty. Units are a0^-2.
    """
    _degree(degree); _bits(precision_bits)
    center = _exact(center); disk_radius = _exact(disk_radius)
    step_radius = _exact(step_radius)
    if not 0 <= step_radius < disk_radius:
        raise ValueError("0<=step_radius<disk_radius required")
    majorant = angular_complex_disk_bound(center, disk_radius, precision_bits)
    with ctx.workprec(precision_bits):
        q = _q(step_radius/disk_radius)
        return (majorant * q**(degree+1)/(1-q)).upper()


def angular_cache_info():
    """Bounded cache inventory for reproducible preparation measurements."""
    return {
        "monomials": monomial_laurent_pairs.cache_info()._asdict(),
        "angular_pairs": _canonical_laurent_pairs.cache_info()._asdict(),
        "ball_coefficients": _canonical_coefficients_ball.cache_info()._asdict(),
    }
