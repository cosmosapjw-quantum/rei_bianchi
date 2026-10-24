"""Conditional free-streaming outer bounds on a supplied Bianchi I cohort.

Exact represented inputs; no provider fetch, history, unit conversion or EOS.
The pressure field is Tr(P)/3 and does not assert angular isotropy.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isfinite, isqrt

Number = int | float | Fraction
Interval = tuple[Fraction, Fraction]


def _fraction(value: Number, name: str, *, positive: bool = False) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, float, Fraction)):
        raise ValueError(f'{name}: int, Fraction or finite float required')
    if isinstance(value, float) and not isfinite(value):
        raise ValueError(f'{name}: finite input required')
    result = Fraction(value)
    if result < 0 or (positive and result == 0):
        condition = 'strictly positive' if positive else 'nonnegative'
        raise ValueError(f'{name}: {condition} input required')
    return result


def _bits(bits: int) -> int:
    if isinstance(bits, bool) or not isinstance(bits, int) or not 1 <= bits <= 4096:
        raise ValueError('bits: integer in 1..4096 required')
    return bits


def _sqrt_interval(Q: Fraction, bits: int = 128) -> Interval:
    """Enclose sqrt(Q) on the exact absolute grid 2**(-bits)."""
    bits = _bits(bits)
    Q = _fraction(Q, 'Q')
    scale = 1 << bits
    p, q = Q.numerator, Q.denominator
    scaled_p = p * scale * scale
    n = isqrt(scaled_p // q)
    lower = Fraction(n, scale)
    upper = lower if n*n*q == scaled_p else Fraction(n+1, scale)
    return lower, upper


def kinetic_map_interval(k: Number, M: Number, r: Number,
                         bits: int = 128) -> Interval:
    """Enclose sqrt(M*M+r*r*k*(k+2*M))-M without subtraction."""
    bits = _bits(bits)
    energy = _fraction(k, 'k')
    rest = _fraction(M, 'M', positive=True)
    ratio = _fraction(r, 'r', positive=True)
    x = ratio*ratio*energy*(energy+2*rest)
    if x == 0:
        return Fraction(0), Fraction(0)
    if ratio == 1:
        return energy, energy
    sqrt_lower, sqrt_upper = _sqrt_interval(rest*rest+x, bits)
    return x/(sqrt_upper+rest), x/(sqrt_lower+rest)


@dataclass(frozen=True)
class StockBounds:
    number_density: Fraction
    dilution: Fraction
    energy_interval: Interval
    support_upper_enclosure: Interval
    lower_energy_bound_enclosure: Interval
    upper_energy_bound_enclosure: Interval
    pressure_trace_interval: Interval
    sqrt_bits: int
    claim: str = 'conditional_free_streaming_outer_bounds'


def _scale(interval: Interval, factor: Fraction) -> Interval:
    return factor*interval[0], factor*interval[1]


def stock_bounds(N: Number, U: Number, L: Number, M: Number,
                 ratios: tuple[Number, Number, Number] | list[Number],
                 bits: int = 128) -> StockBounds:
    """Bounds over unrestricted angular positive measures on energy [0,L].

    Energy endpoints are mathematically sharp; their rational enclosures record
    arithmetic width separately. The composed pressure-trace interval is an
    outer bound, without a sharpness or isotropy assertion. Density units and
    the supplied externally prescribed scale ratios remain caller input.
    """
    bits = _bits(bits)
    n = _fraction(N, 'N')
    u = _fraction(U, 'U')
    limit = _fraction(L, 'L')
    rest = _fraction(M, 'M', positive=True)
    if not isinstance(ratios, (tuple, list)) or len(ratios) != 3:
        raise ValueError('ratios: tuple/list of exactly 3 positive values required')
    rs = tuple(_fraction(value, f'ratios[{index}]', positive=True)
               for index, value in enumerate(ratios))
    if u > n*limit:
        raise ValueError('U: must not exceed N*L')
    dilution = rs[0]*rs[1]*rs[2]
    nt = dilution*n
    rmin, rmax = min(rs), max(rs)
    support = kinetic_map_interval(limit, rest, rmax, bits)
    zero = (Fraction(0), Fraction(0))
    if n == 0 or u == 0 or limit == 0:
        lower = upper = energy = pressure = zero
    else:
        mean = u/n
        if rmin <= 1:
            lower = _scale(kinetic_map_interval(mean, rest, rmin, bits), dilution*n)
        else:
            lower = _scale(kinetic_map_interval(limit, rest, rmin, bits), dilution*u/limit)
        if rmax <= 1:
            upper = _scale(kinetic_map_interval(limit, rest, rmax, bits), dilution*u/limit)
        else:
            upper = _scale(kinetic_map_interval(mean, rest, rmax, bits), dilution*n)
        ulower = lower[0]
        uupper = min(upper[1], nt*support[1])
        energy = ulower, uupper
        lupper = support[1]
        pressure = (ulower*(lupper+2*rest)/(3*(lupper+rest)),
                    uupper*(uupper+2*rest*nt)/(3*(uupper+rest*nt)))
    return StockBounds(number_density=nt, dilution=dilution,
                       energy_interval=energy, support_upper_enclosure=support,
                       lower_energy_bound_enclosure=lower,
                       upper_energy_bound_enclosure=upper,
                       pressure_trace_interval=pressure, sqrt_bits=bits)
