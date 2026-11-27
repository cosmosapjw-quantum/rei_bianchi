#!/usr/bin/env python3
"""Exact-rational enclosing references, independent of Decimal transcendental code.

All returned endpoints are fractions.Fraction values. Decimal is deliberately
not imported. The functions are finite mathematical enclosures, not a heuristic
precision comparison. Their proof is summarized in RATIONAL_REFERENCE.md.
"""
from fractions import Fraction
from math import isqrt


def enclose_grid(value, digits):
    """Outward rounding of an exact rational onto multiples of 10**(-digits)."""
    value = Fraction(value)
    scale = 10 ** digits
    q, rem = divmod(value.numerator * scale, value.denominator)
    return Fraction(q, scale), Fraction(q + bool(rem), scale)


def exp_bounds(x, digits=110):
    """Enclose exp(x) by positive series, geometric tail, and rational squaring."""
    x = Fraction(x)
    if x == 0:
        return Fraction(1), Fraction(1)
    if x < 0:
        lo, hi = exp_bounds(-x, digits)
        return Fraction(1, 1) / hi, Fraction(1, 1) / lo
    work_digits = digits + 20
    y, squarings = x, 0
    while y > Fraction(1, 8):
        y /= 2
        squarings += 1
    if squarings > 16:
        raise ValueError("independent reference intentionally limited to x <= 8192")
    tol = Fraction(1, 10 ** work_digits)
    term = total = Fraction(1)
    for n in range(1, 4000):
        term *= y / n
        total += term
        # First omitted term is y**(n+1)/(n+1)!; every later ratio <= y/(n+2).
        first_omitted = term * y / (n + 1)
        ratio_ceiling = y / (n + 2)
        tail = first_omitted / (1 - ratio_ceiling)
        if tail <= tol:
            lo, hi = total, total + tail
            break
    else:
        raise ArithmeticError("independent exp series budget exceeded")
    lo = enclose_grid(lo, work_digits)[0]
    hi = enclose_grid(hi, work_digits)[1]
    for _ in range(squarings):
        lo = enclose_grid(lo * lo, work_digits)[0]
        hi = enclose_grid(hi * hi, work_digits)[1]
    assert 0 < lo <= hi
    return lo, hi


def _ln_reduced_bounds(m, digits):
    """Enclose ln(m), 1 <= m <= 2, with the positive atanh series."""
    m = Fraction(m)
    if not 1 <= m <= 2:
        raise ValueError("log range-reduced argument outside [1,2]")
    z = (m - 1) / (m + 1)
    if z == 0:
        return Fraction(0), Fraction(0)
    z2 = z * z
    total, zpower = Fraction(0), z
    tol = Fraction(1, 10 ** (digits + 20))
    for j in range(4000):
        total += 2 * zpower / (2 * j + 1)
        zpower *= z2
        # Denominators after 2*j+3 only increase; bound their reciprocals by first.
        tail = 2 * zpower / ((2 * j + 3) * (1 - z2))
        if tail <= tol:
            return (enclose_grid(total, digits + 20)[0],
                    enclose_grid(total + tail, digits + 20)[1])
    raise ArithmeticError("independent log series budget exceeded")


def ln_bounds(x, digits=110):
    """Enclose ln(x) via x = m*2**k, m in [1,2), and bounded ln(2)."""
    x = Fraction(x)
    if x <= 0:
        raise ValueError("log reference requires positive argument")
    m, k = x, 0
    while m < 1:
        m *= 2
        k -= 1
    while m >= 2:
        m /= 2
        k += 1
    lm_lo, lm_hi = _ln_reduced_bounds(m, digits)
    l2_lo, l2_hi = _ln_reduced_bounds(Fraction(2), digits)
    if k >= 0:
        return lm_lo + k * l2_lo, lm_hi + k * l2_hi
    return lm_lo + k * l2_hi, lm_hi + k * l2_lo


def sqrt_bounds(x, digits=110):
    """Integer bracketing proof: k**2 <= x*10**(2*digits) < (k+1)**2."""
    x = Fraction(x)
    if x < 0:
        raise ValueError("square-root reference requires nonnegative argument")
    scale = 10 ** digits
    num, den = x.numerator * scale * scale, x.denominator
    k = isqrt(num // den)
    assert k * k * den <= num < (k + 1) * (k + 1) * den
    lo = Fraction(k, scale)
    hi = lo if k * k * den == num else Fraction(k + 1, scale)
    return lo, hi


def power_bounds(base, exponent, digits=110):
    """Positive-base rational exponent via independent bounded log then exp."""
    base, exponent = Fraction(base), Fraction(exponent)
    if base <= 0:
        raise ValueError("power reference requires positive base")
    if exponent == 0 or base == 1:
        return Fraction(1), Fraction(1)
    ll, lu = ln_bounds(base, digits)
    a, b = exponent * ll, exponent * lu
    loarg, hiarg = min(a, b), max(a, b)
    lo = exp_bounds(loarg, digits)[0]
    hi = exp_bounds(hiarg, digits)[1]
    return lo, hi


def j_bounds(rate, h, digits=110):
    """Enclose integral_0^h exp(-rate*u) du, including exact rate=0 limit."""
    rate, h = Fraction(rate), Fraction(h)
    if rate < 0 or h < 0:
        raise ValueError("J reference limited to nonnegative rate and extent")
    if rate == 0 or h == 0:
        return h, h
    el, eu = exp_bounds(-rate * h, digits)
    return (1 - eu) / rate, (1 - el) / rate
