"""Conditional GL2022 Eq.(5)-(7) source-weighted rate feasibility.

Exact rational mathematics ONLY for supplied positive unnormalised Boltzmann
factors. Neither this code nor its fixtures supplies actual HD level energies
or state-resolved rates. Published thermal totals remain AGGREGATE_ONLY.
"""
from __future__ import annotations
from fractions import Fraction
from typing import Sequence

class ContractError(ValueError):
    """A non-physical input or infeasible conditional rate assignment."""


def spin_factor(r: int) -> Fraction:
    if type(r) is not int or not 0 <= r <= 9:
        raise ContractError("H2 product r must be an integer in [0,9]")
    return Fraction(1, 4) if r % 2 == 0 else Fraction(3, 4)


def source_weights(boltzmann_factors: Sequence[Fraction]) -> tuple[Fraction, ...]:
    """Return w[j*10+r]=p_j*s_r in *paper* order.

    Input b_j = (2j+1) exp[-(E_j-E_0)/(k_B T)], j=0..8,
    represented by explicitly ASSUMED rational surrogates / synthetic fixtures.
    Physical claims demand certified interval enclosure, not this exact-value API.
    DO NOT renormalize the final-state s_r factors: sum_(j,r) w_jr = 5.
    """
    b = tuple(boltzmann_factors)
    if len(b) != 9 or any(type(x) is not Fraction or x <= 0 for x in b):
        raise ContractError("exactly 9 positive Fraction Boltzmann factors required")
    z = sum(b)
    return tuple(b[j] / z * spin_factor(r) for j in range(9) for r in range(10))



def target_weight_interval(b_lower: Sequence[Fraction],
                           b_upper: Sequence[Fraction],
                           j: int, r: int) -> tuple[Fraction, Fraction]:
    """Exact enclosure conditional on external b_j interval certificates.

    The function DOES NOT certify the Boltzmann exponentials or source energies.
    Given true b_j in [b_lower[j],b_upper[j]], target w=p_j*s_r
    lies in the returned rational interval (monotone ratio).
    """
    if type(j) is not int or not 0 <= j <= 8:
        raise ContractError("HD initial j must be an integer in [0,8]")
    sl = spin_factor(r)
    low, high = tuple(b_lower), tuple(b_upper)
    if (len(low) != 9 or len(high) != 9 or
        any(type(a) is not Fraction or type(b) is not Fraction or a <= 0 or a > b
            for a,b in zip(low,high))):
        raise ContractError("nine externally certified positive Fraction intervals required")
    sum_other_hi = sum((high[h] for h in range(9) if h != j),Fraction(0))
    sum_other_lo = sum((low[h] for h in range(9) if h != j),Fraction(0))
    return (sl * low[j] / (low[j]+sum_other_hi),
            sl * high[j] / (high[j]+sum_other_lo))


def conservative_target_cap(total_upper: Fraction, w_lower: Fraction) -> Fraction:
    """Conditional K<=K_hi and w_target>=w_lower>0 imply k<=K_hi/w_lower."""
    if (type(total_upper) is not Fraction or total_upper < 0 or
        type(w_lower) is not Fraction or w_lower <= 0):
        raise ContractError("finite nonnegative K_hi and positive exact weight lower bound")
    return total_upper/w_lower

def _checked_weights(weights: Sequence[Fraction]) -> tuple[Fraction, ...]:
    w = tuple(weights)
    if not w or any(type(x) is not Fraction or x <= 0 for x in w):
        raise ContractError("nonempty positive Fraction weights required")
    return w


def exact_aggregate(weights: Sequence[Fraction], rates: Sequence[Fraction]) -> Fraction:
    w = _checked_weights(weights)
    if len(rates) != len(w) or any(type(x) is not Fraction or x < 0 for x in rates):
        raise ContractError("rates must be nonnegative Fraction with same length")
    return sum((wi * ri for wi, ri in zip(w, rates)), Fraction(0))


def sharp_row_interval(weights: Sequence[Fraction],
                       lower: Sequence[Fraction],
                       upper: Sequence[Fraction | None],
                       total_lower: Fraction, total_upper: Fraction,
                       target: int) -> tuple[Fraction, Fraction]:
    """Sharp projection of {l<=rate<=u, Klo<=sum w_i rate_i<=Khi}.

    None upper bound means +infinity. Uses exact rational arithmetic.
    Does not infer source energies, row rates or statistical uncertainty.
    """
    w = _checked_weights(weights)
    n = len(w)
    if type(target) is not int or not 0 <= target < n or len(lower) != n or len(upper) != n:
        raise ContractError("index or box shape mismatch")
    if any(type(x) is not Fraction or x < 0 for x in lower):
        raise ContractError("lower rates must be nonnegative Fraction")
    if any(u is not None and (type(u) is not Fraction or u < l)
           for l, u in zip(lower, upper)):
        raise ContractError("upper rate bounds must be >= lower or None")
    if (type(total_lower) is not Fraction or type(total_upper) is not Fraction
            or total_lower < 0 or total_lower > total_upper):
        raise ContractError("aggregate input must be finite nonnegative Fraction interval")

    all_low = sum((a * b for a, b in zip(w, lower)), Fraction(0))
    finite_high = all(x is not None for x in upper)
    all_high = sum((wi * ui for wi, ui in zip(w, upper) if ui is not None), Fraction(0))
    if all_low > total_upper or (finite_high and all_high < total_lower):
        raise ContractError("empty feasible rate polytope")

    other_low = all_low - w[target] * lower[target]
    other_finite = all(upper[i] is not None for i in range(n) if i != target)
    other_high = (sum((w[i] * upper[i] for i in range(n) if i != target), Fraction(0))
                  if other_finite else None)
    row_lo = lower[target]
    if other_high is not None:
        row_lo = max(row_lo, (total_lower - other_high) / w[target])
    row_hi = (total_upper - other_low) / w[target]
    if upper[target] is not None:
        row_hi = min(row_hi, upper[target])
    if row_hi < row_lo:
        raise ContractError("empty target projection")
    return row_lo, row_hi


def printed_total_in_si(printed: Fraction) -> Fraction:
    """Unit: 10^-10 cm^3/s -> m^3/s; not physical source error bounds."""
    if type(printed) is not Fraction or printed < 0:
        raise ContractError("nonnegative exact printed aggregate expected")
    return printed * Fraction(1, 10**16)
