"""Exact enclosures for a selected recorded finite injection cohort.

h has units 1/time, its primitive G is dimensionless, and F carries the
count or energy-density unit of the result. Recorded cohort selection does
not assert physical source shutoff. Input endpoint bounds are already closed;
this module neither recloses them nor reads any raw physical history.
"""
from dataclasses import dataclass
from fractions import Fraction

Q = Fraction
SCOPE = 'INTERVAL_MONOTONICITY_SELECTED_FINITE_COHORT'


def _fraction(value):
    if type(value) is not Q:
        raise TypeError('all numerical inputs must be exact Fraction values')
    return value


@dataclass(frozen=True)
class AffineSegment:
    start: Q
    end: Q
    intercept: Q
    slope: Q

    def __post_init__(self):
        for value in (self.start, self.end, self.intercept, self.slope):
            _fraction(value)
        if not Q(0) <= self.start < self.end:
            raise ValueError('segment requires 0 <= start < end')
        if min(self.intercept + self.slope * self.start,
               self.intercept + self.slope * self.end) < 0:
            raise ValueError('cohort density must be nonnegative at both endpoints')


@dataclass(frozen=True)
class CellExtremum:
    value: Q
    location: Q
    left_boundary_excluded: bool


@dataclass(frozen=True)
class BoundsResult:
    lower: Q
    upper: Q
    lower_chain: tuple
    upper_chain: tuple
    cell_min: tuple
    cell_max: tuple
    lower_atom_locations: tuple
    upper_atom_locations: tuple
    scope: str = SCOPE
    lower_semantics: str = 'INFIMUM'
    upper_semantics: str = 'SUPREMUM'


def _segments(segments):
    if type(segments) is not tuple:
        raise TypeError('segments must be a tuple')
    previous = Q(0)
    for segment in segments:
        if type(segment) is not AffineSegment:
            raise TypeError('AffineSegment required')
        if segment.start != previous:
            raise ValueError('cohort partition must start at zero without gaps or overlaps')
        previous = segment.end


def _primitive(segments, x):
    total = Q(0)
    for segment in segments:
        stop = min(max(x, segment.start), segment.end)
        total += (segment.intercept * (stop - segment.start)
                  + segment.slope * (stop * stop - segment.start * segment.start) / 2)
    return total


def integrated_cohort(segments, x):
    """G(x), with selected-cohort density zero outside its finite partition."""
    _segments(segments)
    _fraction(x)
    return _primitive(segments, x)


def kernel(segments, A, B, tau):
    """G(B-tau)-G(A-tau); time arguments are exact Fractions."""
    _segments(segments)
    for value in (A, B, tau):
        _fraction(value)
    if not Q(0) <= A <= B:
        raise ValueError('invalid window')
    return _primitive(segments, B - tau) - _primitive(segments, A - tau)


def _validate(grid, lower, upper, cap, segments, windows):
    _segments(segments)
    if any(type(values) is not tuple for values in (grid, lower, upper, windows)):
        raise TypeError('grid, bounds, and windows must be tuples')
    if not grid or len(grid) != len(lower) or len(grid) != len(upper):
        raise ValueError('nonempty equal-length grid and bounds required')
    for value in grid + lower + upper + (cap,):
        _fraction(value)
    if grid[0] != 0 or lower[0] != 0 or upper[0] != 0:
        raise ValueError('grid and both endpoint chains must start at zero')
    if any(a >= b for a, b in zip(grid, grid[1:])):
        raise ValueError('grid must be strictly increasing')
    if any(a > b for values in (lower, upper) for a, b in zip(values, values[1:])):
        raise ValueError('endpoint bounds must already be monotone')
    if any(lo < 0 or lo > hi for lo, hi in zip(lower, upper)) or cap < upper[-1]:
        raise ValueError('invalid endpoint enclosure or cap')
    for window in windows:
        if type(window) is not tuple or len(window) != 3:
            raise TypeError('window must be an (A,B,weight) tuple')
        A, B, weight = window
        for value in window:
            _fraction(value)
        if not Q(0) <= A <= B <= grid[-1]:
            raise ValueError('window must lie within observed grid')


def _density_coefficients(segments, time, shift):
    # On an open piece, h(shift-tau) = intercept + slope*shift - slope*tau.
    for segment in segments:
        if segment.start < time < segment.end:
            return segment.intercept + segment.slope * shift, -segment.slope
    return Q(0), Q(0)


def _ranges(grid, segments, windows):
    def value(tau):
        return sum((weight * (_primitive(segments, B - tau)
                              - _primitive(segments, A - tau))
                    for A, B, weight in windows), Q(0))
    boundaries = {s.start for s in segments} | {s.end for s in segments}
    mins, maxs = [], []
    for left, right in zip(grid, grid[1:]):
        cuts = {left, right}
        for A, B, weight in windows:
            cuts.update(shift - s for shift in (A, B) for s in boundaries
                        if left < shift - s < right)
        cuts = sorted(cuts)
        candidates = set(cuts)
        for a, b in zip(cuts, cuts[1:]):
            midpoint = (a + b) / 2
            p = q = Q(0)
            for A, B, weight in windows:
                pa, qa = _density_coefficients(segments, A - midpoint, A)
                pb, qb = _density_coefficients(segments, B - midpoint, B)
                p += weight * (pa - pb)
                q += weight * (qa - qb)
            if q:
                root = -p / q
                if a < root < b:
                    candidates.add(root)
        evaluated = [(value(tau), tau) for tau in sorted(candidates)]
        lo = min(evaluated, key=lambda item: item[0])
        hi = max(evaluated, key=lambda item: item[0])
        mins.append(CellExtremum(lo[0], lo[1], lo[1] == left))
        maxs.append(CellExtremum(hi[0], hi[1], hi[1] == left))
    return tuple(mins), tuple(maxs)


def _optimize(coefficients, lower, upper, maximize):
    """O(m*|V|) arithmetic; range construction is a separate cost."""
    levels = sorted(set((Q(0),) + lower + upper))
    previous = [Q(0) if level == 0 else None for level in levels]
    parents = []
    better = (lambda a, b: a > b) if maximize else (lambda a, b: a < b)
    for k, coefficient in enumerate(coefficients, 1):
        current = [None] * len(levels)
        parent = [None] * len(levels)
        best = best_index = None
        for index, level in enumerate(levels):
            if previous[index] is not None:
                candidate = previous[index] - coefficient * level
                if best is None or better(candidate, best):
                    best, best_index = candidate, index
            if lower[k] <= level <= upper[k] and best is not None:
                current[index] = coefficient * level + best
                parent[index] = best_index
        previous = current
        parents.append(parent)
    best = best_index = None
    for index, result in enumerate(previous):
        if result is not None and (best is None or better(result, best)):
            best, best_index = result, index
    chain = [levels[best_index]]
    for parent in reversed(parents):
        best_index = parent[best_index]
        chain.append(levels[best_index])
    return best, tuple(reversed(chain))


def combined_cohort_bounds(grid, lower, upper, *, cap, segments, windows):
    """Enclose a signed scalar combination using one shared endpoint chain.

    Kernels are combined before taking cell extrema. Witness locations belong
    to closed cells and describe limiting atom positions, not guaranteed
    attained extrema on the actual half-open cells (t_i,t_{i+1}].
    """
    _validate(grid, lower, upper, cap, segments, windows)
    minima, maxima = _ranges(grid, segments, windows)
    lo, lo_chain = _optimize(tuple(item.value for item in minima), lower, upper, False)
    hi, hi_chain = _optimize(tuple(item.value for item in maxima), lower, upper, True)
    return BoundsResult(lo, hi, lo_chain, hi_chain, minima, maxima,
                        tuple(item.location for item in minima),
                        tuple(item.location for item in maxima))


def cohort_bounds(grid, lower, upper, *, cap, segments, A, B):
    return combined_cohort_bounds(grid, lower, upper, cap=cap, segments=segments,
                                  windows=((A, B, Q(1)),))
