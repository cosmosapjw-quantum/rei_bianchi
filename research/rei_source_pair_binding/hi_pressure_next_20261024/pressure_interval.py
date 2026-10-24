"""Exact conditional pressure moments of a supplied finite positive measure.

Static preparation only. Caller units distinguish inventory from injection rate.
This module does not qualify a provider or select a physical equation of state.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from typing import Iterable

Number = int | float | Fraction
INTERPRETATION = 'conditional_positive_measure_interval'


class DomainError(ValueError):
    """Input is outside the stated finite positive-measure domain."""


def _fraction(value: Number, name: str, *, positive: bool = False) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, float, Fraction)):
        raise DomainError(f'{name}: int, Fraction or finite float required')
    if isinstance(value, float) and not math.isfinite(value):
        raise DomainError(f'{name}: nonfinite input')
    exact = Fraction(value)
    if exact < 0 or (positive and exact == 0):
        condition = 'positive' if positive else 'nonnegative'
        raise DomainError(f'{name}: {condition} input required')
    return exact


@dataclass(frozen=True)
class PressureInterval:
    N: Fraction
    U: Fraction
    L: Fraction
    M: Fraction
    lower: Fraction
    upper: Fraction
    width: Fraction
    nr_pressure: Fraction
    nr_error_upper: Fraction
    interpretation: str = INTERPRETATION


def pressure_interval_from_moments(N: Number, U: Number, L: Number,
                                    M: Number) -> PressureInterval:
    """Sharp isotropic pressure interval conditional on N/U/support/rest energy.

    Require N,U,L >= 0, M > 0, U <= N*L exactly. Every numerical output is a
    Fraction of the represented operands, without a hidden tolerance. At N=0,
    admissibility requires U=0 and the upper denominator is not evaluated.
    """
    n, u, limit, rest = (_fraction(N, 'N'), _fraction(U, 'U'),
                          _fraction(L, 'L'), _fraction(M, 'M', positive=True))
    if u > n * limit:
        raise DomainError('U must not exceed N*L for a positive measure on [0,L]')
    lower = u * (limit + 2 * rest) / (3 * (limit + rest))
    upper = u * (u + 2 * rest * n) / (3 * (u + rest * n)) if n else Fraction(0)
    return PressureInterval(N=n, U=u, L=limit, M=rest,
                            lower=lower, upper=upper, width=upper-lower,
                            nr_pressure=2*u/3,
                            nr_error_upper=u*limit/(3*(limit+rest)))


@dataclass(frozen=True)
class AtomMoments:
    N: Fraction
    U: Fraction
    pressure: Fraction
    M: Fraction
    L: Fraction
    interpretation: str = 'caller_supplied_atoms; not a qualified source provider'


def pressure_moment_from_atoms(atoms: Iterable[tuple[Number, Number]],
                               M: Number, L: Number) -> AtomMoments:
    """Exact sum of weight*k*(k+2*M)/(k+M)/3 on supplied positive atoms.

    Weights and k must be finite and nonnegative, with k <= L; M > 0 and L >= 0.
    Empty atoms are a valid zero measure. No fetch, quadrature or unit conversion.
    """
    rest = _fraction(M, 'M', positive=True)
    limit = _fraction(L, 'L')
    try:
        iterator = iter(atoms)
    except TypeError as exc:
        raise DomainError('atoms: iterable of (weight, k) pairs required') from exc
    n = u = pressure = Fraction(0)
    for index, atom in enumerate(iterator):
        try:
            weight, energy = atom
        except (TypeError, ValueError) as exc:
            raise DomainError(f'atom[{index}]: exactly (weight, k) required') from exc
        weight = _fraction(weight, f'atom[{index}].weight')
        energy = _fraction(energy, f'atom[{index}].k')
        if energy > limit:
            raise DomainError(f'atom[{index}].k: outside [0,L]')
        n += weight
        u += weight * energy
        pressure += weight * energy * (energy + 2*rest) / (energy + rest) / 3
    return AtomMoments(N=n, U=u, pressure=pressure, M=rest, L=limit)
