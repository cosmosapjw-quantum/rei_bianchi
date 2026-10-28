"""Exact conditional bounds for a nonnegative affine injection history.

Inputs are already-closed cumulative-prefix intervals.  This module neither
closes those intervals nor qualifies a fixed physical response model.  Its
sharpness statement concerns only the interval-and-monotonicity information
class, with one cumulative function shared by all observation windows.

No SI conversion, particle-density factor, or additional time factor is applied.
The caller is responsible for physical qualification and its existing once-only
projection.  Importing this module performs no calculation or I/O.
"""

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Optional, Sequence, Tuple


@dataclass(frozen=True)
class HistoryBoundsResult:
    """Exact lower endpoint, upper supremum, and interval coefficients."""

    lower: Fraction
    upper: Fraction
    weights: Tuple[Fraction, ...]
    scope: str = field(
        default="INTERVAL_MONOTONICITY_AFFINE_HISTORY", init=False
    )
    upper_attainment: str = field(
        default="SUPREMUM_NOT_GENERALLY_ATTAINED", init=False
    )


def _require_fraction(name: str, value: object) -> None:
    # Exact type checking also rejects bool, int, float, and string coercions.
    if type(value) is not Fraction:
        raise TypeError(name + " must be a fractions.Fraction")


def _positive_part(value: Fraction) -> Fraction:
    return value if value > 0 else Fraction(0)


def history_bounds(
    grid: Sequence[Fraction],
    lower: Sequence[Fraction],
    upper: Sequence[Fraction],
    *,
    cap: Fraction,
    A: Fraction,
    B: Fraction,
    alpha: Fraction,
    beta: Fraction,
) -> HistoryBoundsResult:
    """Bound C(B)-C(A) in O(m) exact rational arithmetic operations.

    Bit complexity depends on numerator/denominator lengths.  The grid, A, B,
    alpha, and beta use one global time origin, never restarted per window.

    Here C(T) = integral_0^T h(s) F(T-s) ds, and F is nonnegative,
    nondecreasing, right-continuous, with F(0)=0 and
    lower[i] <= F(grid[i]) <= upper[i].  The supplied bounds must already be
    nonnegative, nondecreasing, consistent, and closed; no closure is inferred.
    ``cap`` explicitly retains the original global cap and must cover upper[-1].

    The lower staircase attains the returned lower bound.  Upper staircases
    with jumps just after grid knots approach the upper bound, which need not
    be attained.  For a finite collection of windows on the same grid with the
    same alpha and beta, the common lower staircase and a common sequence of
    upper staircases realize the respective endpoints simultaneously in this
    information class.  In particular, weights and both endpoints add over
    adjacent observation windows.  This is not a fixed-response physics claim.

    Every numeric input must be a Fraction; integers are not implicitly
    converted.  A singleton grid [Fraction(0)] permits only the zero window.
    Negative source coefficients and extrapolation are refused.
    """

    times = tuple(grid)
    lows = tuple(lower)
    highs = tuple(upper)
    if not times:
        raise ValueError("grid must contain its initial zero")
    if len(lows) != len(times) or len(highs) != len(times):
        raise ValueError("grid, lower, and upper must have equal lengths")

    for name, values in (("grid", times), ("lower", lows), ("upper", highs)):
        for index, value in enumerate(values):
            _require_fraction(name + "[" + str(index) + "]", value)
    for name, value in (
        ("cap", cap), ("A", A), ("B", B), ("alpha", alpha), ("beta", beta)
    ):
        _require_fraction(name, value)

    if times[0] != 0:
        raise ValueError("grid must start at zero")
    if lows[0] != 0 or highs[0] != 0:
        raise ValueError("lower and upper must both start at zero")
    if any(left >= right for left, right in zip(times, times[1:])):
        raise ValueError("grid must be strictly increasing")
    if any(value < 0 for value in lows) or any(value < 0 for value in highs):
        raise ValueError("bounds must be nonnegative")
    if any(left > right for left, right in zip(lows, lows[1:])):
        raise ValueError("lower must be nondecreasing")
    if any(left > right for left, right in zip(highs, highs[1:])):
        raise ValueError("upper must be nondecreasing")
    if any(low > high for low, high in zip(lows, highs)):
        raise ValueError("each lower bound must not exceed its upper bound")
    if cap < highs[-1]:
        raise ValueError("cap must be at least the final closed upper bound")
    if alpha < 0 or beta < 0:
        raise ValueError("alpha and beta must be nonnegative")
    if A < 0 or A > B or B > times[-1]:
        raise ValueError("window must satisfy 0 <= A <= B <= grid[-1]")

    weights = []
    lower_total = Fraction(0)
    upper_total = Fraction(0)
    half_alpha = alpha / 2
    for index, (left, right) in enumerate(zip(times, times[1:])):
        b_left = _positive_part(B - left)
        b_right = _positive_part(B - right)
        a_left = _positive_part(A - left)
        a_right = _positive_part(A - right)
        weight = beta * (b_left - b_right - a_left + a_right)
        weight += half_alpha * (
            b_left * b_left - b_right * b_right
            - a_left * a_left + a_right * a_right
        )
        weights.append(weight)
        lower_total += weight * lows[index]
        upper_total += weight * highs[index + 1]

    return HistoryBoundsResult(lower_total, upper_total, tuple(weights))


@dataclass(frozen=True)
class SourceIdentity:
    """Explicit binding identifiers; None records an unknown identifier."""

    state_id: Optional[str] = None
    spectral_template_id: Optional[str] = None
    frame_id: Optional[str] = None
    volume_convention_id: Optional[str] = None
    proper_clock_id: Optional[str] = None


def binding_issues(
    source: SourceIdentity,
    response: SourceIdentity,
    *,
    frozen_linear_stationary_response: Optional[bool] = None,
) -> Tuple[str, ...]:
    """Report unknown, invalid, or mismatched bindings without inferring IDs.

    An empty result requires explicit, equal nonblank strings for every field
    and an explicit True declaration for frozen linear stationary response.
    This metadata check does not establish that the declaration is physically
    correct, and it does not create a physically projected output.
    """

    if not isinstance(source, SourceIdentity) or not isinstance(response, SourceIdentity):
        raise TypeError("source and response must be SourceIdentity instances")
    issues = []
    for name in (
        "state_id", "spectral_template_id", "frame_id",
        "volume_convention_id", "proper_clock_id",
    ):
        source_value = getattr(source, name)
        response_value = getattr(response, name)
        valid = True
        for side, value in (("source", source_value), ("response", response_value)):
            if value is None or (isinstance(value, str) and not value.strip()):
                issues.append("missing:" + side + "." + name)
                valid = False
            elif type(value) is not str:
                issues.append("invalid:" + side + "." + name)
                valid = False
        if valid and source_value != response_value:
            issues.append("mismatch:" + name)
    if frozen_linear_stationary_response is None:
        issues.append("missing:frozen_linear_stationary_response")
    elif frozen_linear_stationary_response is False:
        issues.append("not_declared:frozen_linear_stationary_response")
    elif frozen_linear_stationary_response is not True:
        issues.append("invalid:frozen_linear_stationary_response")
    return tuple(issues)
