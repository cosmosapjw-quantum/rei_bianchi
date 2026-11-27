"""Reference exposure measures for prescribed homogeneous expansion.

n0: initial proper H density [cm^-3]; k: fixed rate [cm^3/s];
trace: H1+H2+H3 [s^-1]; duration: proper time [s].
No rate source is evaluated, activated, clamped, or inferred here.
The mpmath results are finite-precision references; only phi_enclosure returns
exact rational endpoints with the alternating-series proof in REPORT_KO.md.
"""
from __future__ import annotations
from fractions import Fraction
import math
import mpmath as mp


def _precision(dps: int) -> None:
    if isinstance(dps, bool) or not isinstance(dps, int) or dps < 30:
        raise ValueError('reference precision must be an integer >= 30')


def _nonnegative(*values):
    if any(isinstance(v, bool) for v in values):
        raise ValueError('boolean is not a physical scalar')
    out = tuple(mp.mpf(v) for v in values)
    if any(not mp.isfinite(v) or v < 0 for v in out):
        raise ValueError('finite nonnegative input required')
    return out


def _phi(x):
    return -mp.expm1(-x)/x if x else mp.mpf(1)


def exposure(n0, k, trace, duration, dps: int = 80):
    """Theta = integral k*nH dt, dimensionless; constant nonnegative trace."""
    _precision(dps)
    with mp.workdps(dps):
        n0, k, trace, duration = _nonnegative(n0, k, trace, duration)
        return +(n0*k*duration*_phi(trace*duration))


def phi_enclosure(x: Fraction, even_degree: int = 20) -> tuple[Fraction, Fraction]:
    """Exact lower/upper bounds for (1-exp(-x))/x on rational 0<=x<=1.

    The degree-2m partial sum is upper, degree-(2m+1) is lower.
    Outside this declared domain raise; no hidden approximation fallback.
    """
    if not isinstance(x, Fraction) or not 0 <= x <= 1:
        raise ValueError('require an exact Fraction in [0,1]')
    if (isinstance(even_degree, bool) or not isinstance(even_degree, int)
            or even_degree < 0 or even_degree % 2):
        raise ValueError('require a nonnegative even degree')
    hi = sum(((-x)**j/Fraction(math.factorial(j+1))
              for j in range(even_degree+1)), Fraction(0))
    lo = hi + (-x)**(even_degree+1)/math.factorial(even_degree+2)
    return lo, hi


def endpoint_exposure(n0, k, trace, duration, steps: int, side: str, dps: int = 80):
    """Uniform positive endpoint quadrature of Theta, not reaction dynamics.

    Right endpoints undercount the continuum density exposure for expansion;
    left endpoints overcount. A native adaptive trace must use its own nodes.
    """
    _precision(dps)
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 1:
        raise ValueError('steps must be a positive integer')
    if side not in ('left', 'right'):
        raise ValueError('side must be left or right')
    with mp.workdps(dps):
        n0, k, trace, duration = _nonnegative(n0, k, trace, duration)
        theta = exposure(n0, k, trace, duration, dps)
        z = trace*duration/steps
        if not z:
            return +theta
        factor = z/mp.expm1(z) if side == 'right' else -z/mp.expm1(-z)
        return +(theta*factor)


def thermal_exposure(n0, k, fhe, trace, duration, dps: int = 80):
    """Upper forcing-kernel coefficient in w [eV/H] per |Q-Ebar| [eV].

    Integral exp(-2*Hmean*(t-s))*fHe*k*nH(s) ds. This is not the
    total temperature/thermal-energy difference of two coupled trajectories.
    """
    _precision(dps)
    with mp.workdps(dps):
        n0, k, fhe, trace, duration = _nonnegative(n0, k, fhe, trace, duration)
        z = trace*duration/3
        return +(fhe*n0*k*duration*mp.exp(-2*z)*_phi(z))
