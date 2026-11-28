"""HH-F1C exact source-cutoff predicates in the seven F03 coordinates.

These predicates do not solve a root, choose a timestep, advance a state, or
admit any physical model. A rectangular input box must lie inside the physical
population simplex. Its provenance/consumer authority is not inferred here.
"""
from __future__ import annotations
from decimal import Decimal
from fractions import Fraction
from typing import Sequence

Exact = int | str | Decimal | Fraction
CUT_K = Fraction(3000)


def exact(value: Exact) -> Fraction:
    """Use the declared exact value, never an implicit binary64 conversion."""
    if isinstance(value, bool) or not isinstance(value, (int, str, Decimal, Fraction)):
        raise ValueError('EXACT_RATIONAL_OR_DECIMAL_REQUIRED')
    try:
        return Fraction(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError('FINITE_EXACT_VALUE_REQUIRED') from exc


def cutoff_box(n_h: Exact, n_he: Exact, kb: Exact,
               bounds: Sequence[Sequence[Exact]]) -> tuple[Fraction, Fraction, str]:
    """Return exact min/max of S=2u-3*kB*3000*P and a source branch label.

    Coordinate order: (h, y1, y2, u, N0, N1, N2), proper CGS.
    Densities and kB are fixed across this box. Extrema are sharp on the supplied
    rectangular box, not on an unknown consumer trajectory or state enclosure.
    """
    nh, nhe, k = map(exact, (n_h, n_he, kb))
    if nh < 0 or nhe < 0 or nh + nhe <= 0 or k <= 0:
        raise ValueError('POSITIVE_DENSITY_SUM_AND_KB_REQUIRED')
    if len(bounds) != 7 or any(len(b) != 2 for b in bounds):
        raise ValueError('SEVEN_ORDERED_COORDINATE_INTERVALS_REQUIRED')
    b = [(exact(lo), exact(hi)) for lo, hi in bounds]
    if any(lo > hi for lo, hi in b):
        raise ValueError('REVERSED_INTERVAL')
    if b[0][0] < 0 or b[0][1] > 1 or b[1][0] < 0 or b[2][0] < 0 or b[1][1]+b[2][1] > 1:
        raise ValueError('ENTIRE_RECTANGLE_MUST_BE_IN_POPULATION_SIMPLEX')
    if b[3][0] <= 0 or any(lo < 0 for lo, hi in b[4:]):
        raise ValueError('POSITIVE_THERMAL_ENERGY_AND_NONNEGATIVE_PHOTONS_REQUIRED')
    p_lo = nh*(1+b[0][0]) + nhe*(1+b[1][0]+2*b[2][0])
    p_hi = nh*(1+b[0][1]) + nhe*(1+b[1][1]+2*b[2][1])
    lo = 2*b[3][0] - 3*k*CUT_K*p_hi
    hi = 2*b[3][1] - 3*k*CUT_K*p_lo
    if nh == 0:
        branch = 'ZERO_HH_SOURCE'
    elif lo > 0:
        branch = 'SMOOTH_ANALYTIC'
    elif hi < 0:
        branch = 'SMOOTH_FLOOR'
    elif lo == hi == 0:
        branch = 'EXACT_CUTOFF'
    else:
        branch = 'CUTOFF_INTERSECTING'
    return lo, hi, branch


def cutoff_displacement(n_h: Exact, kb: Exact, chi: Exact,
                        p0: Exact, u0: Exact) -> Fraction:
    """Algebraic h*-h0 along the HH-only energy invariant, not a state step.

    A nonpositive result does not place a hot-to-cold crossing ahead of h0.
    A positive result still requires checking the thermal and population ends.
    """
    nh, k, binding, p, u = map(exact, (n_h, kb, chi, p0, u0))
    if min(nh, k, binding, p, u) <= 0:
        raise ValueError('POSITIVE_INVARIANT_PARAMETERS_REQUIRED')
    return (2*u-3*k*CUT_K*p)/(nh*(2*binding+3*k*CUT_K))
