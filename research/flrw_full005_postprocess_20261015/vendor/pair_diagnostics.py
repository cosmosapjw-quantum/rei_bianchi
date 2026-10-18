"""Streaming binary64 diagnostics of saved PL reconstructions in ln(a).

The integration measure is dimensionless d ln(a). These metrics describe the
saved reconstructions; they supply no solver-error bound or acceptance threshold.
"""
from bisect import bisect_right
import csv
import json
import math
from pathlib import Path


RESULT_CLASS = 'DIAGNOSTIC_PAIR_RECONSTRUCTION_NO_THRESHOLD_OR_ERROR_BOUND'


def _finite(value, cause):
    try:
        valid = math.isfinite(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError('INVALID_NUMERIC_VALUE: ' + cause) from exc
    if not valid:
        raise ValueError('NONFINITE_ARITHMETIC_OR_VALUE: ' + cause)
    return value


class _Sum:
    """Neumaier accumulation using two floats, with explicit range checks."""
    def __init__(self):
        self.total = 0.0
        self.correction = 0.0

    def add(self, value):
        _finite(value, 'segment integral')
        new = _finite(self.total + value, 'integral accumulation')
        if abs(self.total) >= abs(value):
            error = (self.total - new) + value
        else:
            error = (value - new) + self.total
        self.correction = _finite(self.correction + error, 'sum correction')
        self.total = new

    def value(self):
        return _finite(self.total + self.correction, 'corrected integral')


def _validate(series, fields, label):
    try:
        xs = series['L']
        if len(xs) < 2:
            raise ValueError('INVALID_COORDINATE_SHAPE: ' + label)
        previous = None
        for x in xs:
            _finite(x, label + '.L')
            if previous is not None and not x > previous:
                raise ValueError('COORDINATES_NOT_STRICTLY_INCREASING: ' + label)
            previous = x
        for field in fields:
            ys = series[field]
            if len(ys) != len(xs):
                raise ValueError('OBSERVABLE_SHAPE_MISMATCH: ' + label + '.' + field)
            for y in ys:
                _finite(y, label + '.' + field)
    except (KeyError, TypeError) as exc:
        raise ValueError('MISSING_OR_INVALID_SERIES: ' + label + ': ' + str(exc)) from exc
    return xs


def _value(xs, ys, bracket, x):
    a, b = xs[bracket], xs[bracket + 1]
    if x == a:
        return ys[bracket]
    if x == b:
        return ys[bracket + 1]
    if not a < x < b:
        raise ValueError('INTERPOLATION_OUTSIDE_BRACKET')
    width = _finite(b - a, 'interpolation width')
    weight = _finite((x - a) / width, 'interpolation weight')
    return _finite((1.0 - weight) * ys[bracket] + weight * ys[bracket + 1],
                   'convex interpolation')


def _integrals(p, q, width):
    scale = max(abs(p), abs(q))
    if scale == 0:
        return 0.0, 0.0
    a, b = p / scale, q / scale
    if (p < 0 < q) or (q < 0 < p):
        shape1 = (a*a + b*b) / (2.0 * (abs(a) + abs(b)))
    else:
        shape1 = (abs(a) + abs(b)) / 2.0
    shape2 = (a*a + a*b + b*b) / 3.0
    weighted_scale = _finite(width * scale, 'width times difference scale')
    return (_finite(weighted_scale * shape1, 'L1 segment'),
            _finite(weighted_scale * scale * shape2, 'squared segment'))


def _units(field):
    return {'ne_cm3': 'cm^-3', 'Tgas_K': 'K',
            'U0_eV_per_H': 'eV/H', 'U2_eV_per_H': 'eV/H'}.get(field, '1')


def diagnose_pair(reference, candidate, observables=None):
    """Return full-overlap PL metrics with O(k) auxiliary memory.

    Knot equality is exact stored-value equality. Interpolation never
    extrapolates. A strictly larger maximum replaces the earliest witness.
    """
    try:
        rs, cs = reference['series'], candidate['series']
        if observables is None:
            fields = [name for name in rs if name not in ('L', 'time_s')]
            if set(fields) != set(cs) - {'L', 'time_s'}:
                raise ValueError('DEFAULT_OBSERVABLE_SET_MISMATCH')
        else:
            fields = list(observables)
        if (not fields or len(set(fields)) != len(fields)
                or any(not isinstance(f, str) or f in ('L', 'time_s') for f in fields)):
            raise ValueError('INVALID_OBSERVABLE_SELECTION')
        rx = _validate(rs, fields, 'reference')
        cx = _validate(cs, fields, 'candidate')
        lower, upper = max(rx[0], cx[0]), min(rx[-1], cx[-1])
        if not lower < upper:
            raise ValueError('NO_POSITIVE_OVERLAP')
        width = _finite(upper - lower, 'overlap width')
        i = min(bisect_right(rx, lower) - 1, len(rx) - 2)
        j = min(bisect_right(cx, lower) - 1, len(cx) - 2)
        previous = [_finite(_value(cx, cs[f], j, lower) - _value(rx, rs[f], i, lower),
                            'initial difference: ' + f) for f in fields]
        summary = [dict(observable=f, sup_absolute_difference=abs(p), ln_a_at_sup=lower,
                        signed_difference_at_sup=p, initial_difference=p,
                        units=_units(f), result_class=RESULT_CLASS)
                   for f, p in zip(fields, previous)]
        l1, l2 = [_Sum() for _ in fields], [_Sum() for _ in fields]
        x, knots = lower, 1
        while x < upper:
            following = min(rx[i + 1], cx[j + 1], upper)
            h = _finite(following - x, 'merged segment width')
            if h <= 0:
                raise ValueError('INVALID_MERGED_SEGMENT_WIDTH')
            for k, f in enumerate(fields):
                q = _finite(_value(cx, cs[f], j, following)
                            - _value(rx, rs[f], i, following), 'difference: ' + f)
                one, two = _integrals(previous[k], q, h)
                l1[k].add(one)
                l2[k].add(two)
                row = summary[k]
                if abs(q) > row['sup_absolute_difference']:
                    row.update(sup_absolute_difference=abs(q), ln_a_at_sup=following,
                               signed_difference_at_sup=q)
                previous[k] = q
            x, knots = following, knots + 1
            if rx[i + 1] == x and i < len(rx) - 2:
                i += 1
            if cx[j + 1] == x and j < len(cx) - 2:
                j += 1
        for k, row in enumerate(summary):
            one, two = l1[k].value(), l2[k].value()
            row.update(endpoint_difference=previous[k], l1_integral=one,
                       mean_absolute_difference=_finite(one / width, 'mean absolute difference'),
                       l2_squared_integral=two, l2_norm=math.sqrt(two),
                       rms_difference=math.sqrt(_finite(two / width, 'mean square')))
        return dict(schema_version=1, status='PIECEWISE_LINEAR_RECONSTRUCTION_DIAGNOSTICS',
                    coordinate='LN_A_STORED_BINARY64', arithmetic='BINARY64_ANALYTIC_SEGMENTS',
                    reference=reference['id'], candidate=candidate['id'],
                    reference_domain=[rx[0], rx[-1]], candidate_domain=[cx[0], cx[-1]],
                    overlap=[lower, upper], overlap_width=width, union_knots=knots,
                    segments=knots - 1, summary=summary)
    except (KeyError, TypeError, OverflowError) as exc:
        raise ValueError('INVALID_PAIR_INPUT_OR_ARITHMETIC: ' + str(exc)) from exc


def write_diagnostics(result, output):
    """Write the two new files; caller owns fresh output and input validation."""
    output = Path(output)
    (output / 'full_pair_continuous_diagnostics.json').write_text(
        json.dumps(result, indent=2, allow_nan=False) + '\n')
    with (output / 'full_pair_continuous_summary.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(result['summary'][0]))
        writer.writeheader()
        writer.writerows(result['summary'])
