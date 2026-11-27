"""Exact all-angular third Born coefficient majorants for the original HH screen.

The all-radial D3=Z'''(0)/6 coefficient has two intermediate angular indices.
The infinite double sum is evaluated by polynomial-geometric identities, not
by truncation or binary floating-point arithmetic.  The excluded-angular
bound is the sum of two one-sided tails; their positive overlap is knowingly
counted twice.  No all-order or lambda=1 convergence claim is made here.

All constants are for B=27, k=7/10, eta_C=-10/7, V=2(1+1/d)exp(-2d).
The physical result has units a0^-1.  See PHYS71 theory/ANGULAR_D3.md.
"""
from __future__ import annotations

from fractions import Fraction as F
from math import comb, factorial

from .phys69_angular_tail import (
    MODE_SLOPE, SCREEN_ELLIPSE_M, rational_record, upward_decimal,
)

DELTA = F(3, 10**23)
ANGULAR_C = 40 * SCREEN_ELLIPSE_M / 9
LOW_MODE_RATIO = F(77)
EXTERNAL_RATIO_PRODUCT = LOW_MODE_RATIO**2
DECAY = F(1, 10)
DOUBLE_DECAY = DECAY**2
RADIAL_FACTOR = F(1, 96)


def _integer(value, name, minimum=0, maximum=None):
    if type(value) is not int or value < minimum or (maximum is not None and value > maximum):
        raise ValueError(f"{name}: exact integer in the stated domain required")
    return value


def _external(a, b, m=0):
    _integer(a, "ell", 0, 28)
    _integer(b, "ellprime", 0, 28)
    if type(m) is not int or abs(m) > min(a, b):
        raise ValueError("a common allowed signed m is required")


def power10(exponent):
    _integer(abs(exponent) if type(exponent) is int else exponent, "integer exponent")
    return F(10**exponent) if exponent >= 0 else F(1, 10**(-exponent))


def angular_majorant(distance):
    """Whole-exterior |V_ij(r)| <= v_|i-j| exp[-2(r-B)]."""
    _integer(distance, "angular distance")
    return min(DELTA, ANGULAR_C * power10(-distance))


def mode_majorant(j):
    """Modewise ratio C_j; its linear growth is retained in every sum."""
    _integer(j, "angular mode")
    return LOW_MODE_RATIO if j <= 28 else MODE_SLOPE * (j + 1)


def _add(*polynomials):
    out = [F(0)] * max(map(len, polynomials))
    for p in polynomials:
        for i, value in enumerate(p):
            out[i] += value
    return tuple(out)


def _scale(p, scalar):
    return tuple(F(scalar) * value for value in p)


def _mul(p, q):
    out = [F(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            out[i+j] += a*b
    return tuple(out)


def _square_shift(shift):
    return (F(shift*shift), F(2*shift), F(1))


def geometric_moment(degree, ratio=DOUBLE_DECAY):
    """Exact sum n^degree ratio^n, n>=0; 0^0 is interpreted as one."""
    _integer(degree, "moment degree", 0, 20)
    if type(ratio) not in (F, int) or not 0 < ratio < 1:
        raise ValueError("an exact rational ratio strictly between zero and one is required")
    ratio = F(ratio)
    # n^d = sum_k S(d,k) n(n-1)...(n-k+1).
    stirling = [1]
    for _ in range(degree):
        next_row = [0] * (len(stirling) + 1)
        for k in range(1, len(next_row)):
            next_row[k] = (k*stirling[k] if k < len(stirling) else 0) + stirling[k-1]
        stirling = next_row
    return sum((F(value*factorial(k)) * ratio**k / (1-ratio)**(k+1)
                for k, value in enumerate(stirling)), F(0))


def polynomial_geometric_tail(coefficients, start, ratio=DOUBLE_DECAY):
    """Exact sum_{j=start}^infinity p(j) ratio^j, p in ascending powers."""
    _integer(start, "tail start")
    if not coefficients or len(coefficients) > 21:
        raise ValueError("one through 21 polynomial coefficients required")
    if any(type(x) not in (F, int) for x in coefficients):
        raise ValueError("polynomial coefficients must be exact rationals")
    if type(ratio) not in (F, int) or not 0 < ratio < 1:
        raise ValueError("an exact rational ratio strictly between zero and one is required")
    ratio = F(ratio)
    moments = [geometric_moment(d, ratio) for d in range(len(coefficients))]
    total = F(0)
    for degree, coefficient in enumerate(coefficients):
        total += coefficient * sum((F(comb(degree, d) * start**(degree-d)) * moments[d]
                                    for d in range(degree+1)), F(0))
    return ratio**start * total


def inner_convolution(j, b):
    """Exact B_b(j)=sum_{k>=0} C_k^2 v_|j-k| v_|b-k|.

    Its finite part covers every non-geometric/constant-C exception; the
    remaining k tail uses an exact quadratic-geometric sum.
    """
    _integer(j, "angular mode")
    _integer(b, "external mode", 0, 28)
    stop = max(28, j+3, b+3)
    finite = sum((mode_majorant(k)**2 * angular_majorant(abs(j-k))
                  * angular_majorant(abs(b-k)) for k in range(stop+1)), F(0))
    tail = (MODE_SLOPE**2 * ANGULAR_C**2 * power10(j+b)
            * polynomial_geometric_tail((1, 2, 1), stop+1))
    return finite + tail


def asymptotic_inner_polynomial(b):
    """P_b(j) with B_b(j)=10^-j P_b(j), j>=max(32,b+7).

    A polynomial can have signed monomial coefficients even though its value
    on this entire stated range is positive.  Every operation is exact.
    """
    _integer(b, "external mode", 0, 28)
    stop = max(28, b+3)
    low = ANGULAR_C * sum((mode_majorant(k)**2 * power10(k)
                           * angular_majorant(abs(b-k)) for k in range(stop+1)), F(0))
    # Sum_{k=stop+1}^{j-4}(k+1)^2 = Q2(j-3)-Q2(stop+1).
    # For b>=26 the three central-potential exceptions extend above mode28.
    left = _add(_scale(_mul(_mul((-3, 1), (-2, 1)), (-5, 2)), F(1, 6)),
                (-F((stop+1)*(stop+2)*(2*stop+3), 6),))
    left = _scale(left, ANGULAR_C**2 * power10(b) * MODE_SLOPE**2)
    middle = _add(*[_scale(_square_shift(d+1), power10(-d)) for d in range(-3, 4)])
    middle = _scale(middle, DELTA * ANGULAR_C * power10(b) * MODE_SLOPE**2)
    x = DOUBLE_DECAY
    right = _add(_scale(_square_shift(5), 1/(1-x)),
                 _scale((5, 1), 2*x/(1-x)**2),
                 (x*(1+x)/(1-x)**3,))
    right = _scale(right, ANGULAR_C**2 * power10(b-8) * MODE_SLOPE**2)
    return _add((low,), left, middle, right)


def one_sided_tail(cutoff, a=21, b=20):
    """Exact sum_{j>L,k>=0} C_j^2 C_k^2 v_aj v_jk v_bk."""
    _external(a, b)
    _integer(cutoff, "angular cutoff", 28)
    start = max(cutoff+1, 32, a+4, b+7)
    finite = sum((mode_majorant(j)**2 * angular_majorant(abs(a-j))
                  * inner_convolution(j, b) for j in range(cutoff+1, start)), F(0))
    polynomial = _mul((1, 2, 1), asymptotic_inner_polynomial(b))
    tail = MODE_SLOPE**2 * ANGULAR_C * power10(a) * polynomial_geometric_tail(polynomial, start)
    result = finite + tail
    if result < 0:
        raise ArithmeticError("positive angular sum evaluated negative")
    return result


def excluded_third_born_bound(cutoff, ell=21, ellprime=20, m=0):
    """Rigorous all-radial |D3_infinite-D3_L| bound, a0^-1.

    For m!=0 the nonnegative majorant includes the extra indices below |m|,
    so the same bound remains valid.  It is not a full-map operator norm.
    """
    _external(ell, ellprime, m)
    _integer(cutoff, "angular cutoff", 28)
    return EXTERNAL_RATIO_PRODUCT * RADIAL_FACTOR * (
        one_sided_tail(cutoff, ell, ellprime) + one_sided_tail(cutoff, ellprime, ell))


def full_third_born_bound(ell=21, ellprime=20, m=0):
    """Zero-centered bound on the entire coefficient, without any integration."""
    _external(ell, ellprime, m)
    finite_rows = sum((mode_majorant(j)**2 * angular_majorant(abs(ell-j))
                       * inner_convolution(j, ellprime) for j in range(29)), F(0))
    return EXTERNAL_RATIO_PRODUCT * RADIAL_FACTOR * (finite_rows + one_sided_tail(28, ell, ellprime))


def minimum_cutoff_for_goal(goal, ell=21, ellprime=20, m=0, maximum=64):
    if type(goal) not in (F, int, str):
        raise ValueError("exact rational goal required")
    goal = F(goal)
    if goal <= 0:
        raise ValueError("positive angular goal required")
    _external(ell, ellprime, m)
    _integer(maximum, "maximum cutoff", 28)
    for cutoff in range(28, maximum+1):
        if excluded_third_born_bound(cutoff, ell, ellprime, m) <= goal:
            return cutoff
    return None


def certificate(cutoffs=(28, 36, 64), ell=21, ellprime=20, m=0):
    _external(ell, ellprime, m)
    if not cutoffs:
        raise ValueError("at least one cutoff required")
    rows = []
    for cutoff in cutoffs:
        value = excluded_third_born_bound(cutoff, ell, ellprime, m)
        rows.append({"L": cutoff, "absolute_angular_tail_bound": rational_record(value),
                     "upper_decimal": upward_decimal(value),
                     "one_sided_ab": rational_record(one_sided_tail(cutoff, ell, ellprime)),
                     "one_sided_ba": rational_record(one_sided_tail(cutoff, ellprime, ell))})
    full = full_third_born_bound(ell, ellprime, m)
    return {
        "schema": "PHYS71_EXACT_ALL_ANGULAR_D3_MAJORANT_V1",
        "status": "ANALYTIC_INFINITE_SUM_WITH_EXACT_RATIONAL_APPLICATION",
        "target": {"ell": ell, "ellprime": ellprime, "m": m, "coefficient": "D3=Z'''(0)/6"},
        "physics": {"B": "27", "k": "7/10", "E_Hartree": "49/200", "eta_C": "-10/7",
                    "shift": "7/10", "V": "2(1+1/d)exp(-2d)", "DtN": "+u' u^-1"},
        "units": "a0^-1", "radial_domain": "all real r>=27",
        "radial_factor": rational_record(RADIAL_FACTOR),
        "external_ratio_product": rational_record(EXTERNAL_RATIO_PRODUCT),
        "angular_overlap_double_counted": True,
        "angular_rows": rows,
        "whole_D3_zero_centered_bound": rational_record(full),
        "whole_D3_upper_decimal": upward_decimal(full),
        "angular_sum_truncation": False, "binary64_arithmetic": False,
        "radial_integrations": 0, "Coulomb_evaluations": 0,
        "full_nonlinear_remainder_certified": False, "original_driven_xi_certified": False,
        "PHYS63_qualitative_existence": "ESTABLISHED_REUSED", "HH_R10": "OFF",
    }
