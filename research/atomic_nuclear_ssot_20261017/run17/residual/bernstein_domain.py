"""Exact-rational domain certificates for the stored reconstruction polynomials.

Binary64 input coefficients are interpreted as exact rational numbers.  This
certifies their ideal real polynomials and the affine gas lift, not the exact
ODE solution or all floating evaluation roundoff.  No native RHS is called.
"""
from __future__ import annotations

from fractions import Fraction
from math import comb


def rational(value):
    return Fraction.from_float(float(value))


def bernstein_coefficients(power):
    """Power coefficients in ascending order -> same-degree Bernstein form."""
    power = [Fraction(value) for value in power]
    degree = len(power)-1
    if degree < 0:
        raise ValueError("at least a constant coefficient required")
    return [sum((power[k]*Fraction(comb(j, k), comb(degree, k))
                 for k in range(j+1)), Fraction(0)) for j in range(degree+1)]


def dop853_power(y_old, coefficients, x_scale=Fraction(1)):
    """Independent basis expansion of the seven-term stored polynomial.

    F_k multiplies x^(1+floor(k/2)) (1-x)^ceil(k/2). ``x_scale``
    maps the exact accepted endpoint interval to the saved normalized clock.
    """
    if len(coefficients) != 7:
        raise ValueError("seven saved coefficient rows required")
    power = [Fraction(0) for _ in range(8)]
    power[0] = rational(y_old)
    for k, value in enumerate(coefficients):
        p, q = 1+k//2, (k+1)//2
        for j in range(q+1):
            power[p+j] += rational(value)*comb(q, j)*(-1)**j*x_scale**(p+j)
    return power


def shifted_cubic_power(descending, origin_offset, width):
    if len(descending) != 4:
        raise ValueError("four cubic coefficients required")
    power = [Fraction(0) for _ in range(4)]
    for index, value in enumerate(descending):
        degree = 3-index
        for j in range(degree+1):
            power[j] += rational(value)*comb(degree, j)*origin_offset**(degree-j)*width**j
    return power


def affine_gas_power(q_power, gas0, lift, q0):
    degree = len(q_power[0])-1
    if len(q_power) != 5 or any(len(p) != degree+1 for p in q_power):
        raise ValueError("five equal-degree gas-coordinate polynomials required")
    output = [[Fraction(0) for _ in range(degree+1)] for _ in range(14)]
    for species in range(14):
        output[species][0] = rational(gas0[species])
        for coordinate in range(5):
            multiplier = rational(lift[species][coordinate])
            output[species][0] -= multiplier*rational(q0[coordinate])
            for order in range(degree+1):
                output[species][order] += multiplier*q_power[coordinate][order]
    return output


def minimum_record(power):
    lower = min(bernstein_coefficients(power))
    return {"lower_bound_rational": str(lower), "lower_bound_float_for_display": float(lower),
            "exact_nonnegative": lower >= 0, "exact_positive": lower > 0}
