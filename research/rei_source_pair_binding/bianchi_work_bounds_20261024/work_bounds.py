"""Exact snapshot stress/work bounds for a supplied massive positive measure.

Physical-volume moments and prescribed diagonal rates are caller input. No
history, isotropy, stopping, EOS, or Einstein evolution is inferred here.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isfinite

Number = int | float | Fraction
Interval = tuple[Fraction, Fraction]
Rates = tuple[Fraction, Fraction, Fraction]


def _fraction(value: Number, name: str, *, signed: bool = False,
              positive: bool = False) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, float, Fraction)):
        raise ValueError(f'{name}: int, Fraction or finite float required')
    if isinstance(value, float) and not isfinite(value):
        raise ValueError(f'{name}: finite input required')
    result = Fraction(value)
    if positive and result <= 0:
        raise ValueError(f'{name}: strictly positive input required')
    if not signed and result < 0:
        raise ValueError(f'{name}: nonnegative input required')
    return result


def _rates(values: tuple[Number, Number, Number] | list[Number]) -> Rates:
    if not isinstance(values, (tuple, list)) or len(values) != 3:
        raise ValueError('rates: tuple/list of exactly 3 finite signed values required')
    return tuple(_fraction(value, f'rates[{index}]', signed=True)
                 for index, value in enumerate(values))


@dataclass(frozen=True)
class WorkBounds:
    number_density: Fraction
    energy_interval: Interval
    support_upper: Fraction
    rest_energy: Fraction
    rates: Rates
    theta: Fraction
    shear_rates: Rates
    trace_interval: Interval
    work_interval: Interval
    shear_work_interval: Interval
    energy_derivative_interval: Interval
    anisotropy_norm_squared_upper: Fraction
    claim: str


def _contract(trace: Interval, rates: Rates) -> Interval:
    lower, upper = trace
    a, b = min(rates), max(rates)
    return a*(lower if a >= 0 else upper), b*(upper if b >= 0 else lower)


def _bounds(n: Fraction, energy: Interval, limit: Fraction, rest: Fraction,
            rates: Rates, claim: str) -> WorkBounds:
    ulo, uhi = energy
    theta = sum(rates, Fraction(0))
    shear = tuple(rate-theta/3 for rate in rates)
    if n == 0 or uhi == 0:
        trace = (Fraction(0), Fraction(0))
    else:
        trace = (ulo*(limit+2*rest)/(limit+rest),
                 uhi*(uhi+2*rest*n)/(uhi+rest*n))
    work = _contract(trace, rates)
    shear_work = _contract(trace, shear)
    alo, ahi = sorted((-theta*ulo, -theta*uhi))
    derivative = alo-work[1], ahi-work[0]
    return WorkBounds(number_density=n, energy_interval=energy,
                      support_upper=limit, rest_energy=rest, rates=rates,
                      theta=theta, shear_rates=shear, trace_interval=trace,
                      work_interval=work, shear_work_interval=shear_work,
                      energy_derivative_interval=derivative,
                      anisotropy_norm_squared_upper=Fraction(2, 3)*trace[1]**2,
                      claim=claim)


def diagonal_work_bounds(N: Number, U: Number, L: Number, M: Number,
                         rates: tuple[Number, Number, Number] | list[Number]) -> WorkBounds:
    """Sharp snapshot bounds over angularly unrestricted exact N/U/L moments."""
    n, u, limit, rest = (_fraction(N, 'N'), _fraction(U, 'U'),
                          _fraction(L, 'L'), _fraction(M, 'M', positive=True))
    rates = _rates(rates)
    if u > n*limit:
        raise ValueError('U: must not exceed N*L')
    return _bounds(n, (u, u), limit, rest, rates, 'sharp_given_exact_moments')


def enclosure_work_bounds(N: Number, energy_interval: tuple[Number, Number] | list[Number],
                          L: Number, M: Number,
                          rates: tuple[Number, Number, Number] | list[Number]) -> WorkBounds:
    """Conservative outer bounds from supplied energy and support enclosures."""
    n, limit, rest = (_fraction(N, 'N'), _fraction(L, 'L'),
                      _fraction(M, 'M', positive=True))
    rates = _rates(rates)
    if not isinstance(energy_interval, (tuple, list)) or len(energy_interval) != 2:
        raise ValueError('energy_interval: tuple/list of exactly 2 endpoints required')
    lower, upper = (_fraction(value, f'energy_interval[{index}]')
                    for index, value in enumerate(energy_interval))
    if lower > upper:
        raise ValueError('energy_interval: lower endpoint must not exceed upper')
    if upper > n*limit:
        raise ValueError('energy_interval: upper endpoint must not exceed N*L')
    return _bounds(n, (lower, upper), limit, rest, rates,
                   'conservative_given_energy_enclosure')
