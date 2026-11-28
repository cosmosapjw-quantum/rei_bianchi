#!/usr/bin/env python3
"""Exact-rational exploratory controls for the E13C10 Peano derivation.

This file does not import, run, or validate the captured coefficient code.
All polynomial evaluations, ranges, integrals and kernel masses are exact.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import time


def at(p, x):
    result = F(0)
    for c in reversed(p):
        result = result * x + c
    return result


def derivative(p):
    return [F(j) * p[j] for j in range(1, len(p))] or [F(0)]


def integral(p, a=F(0), b=F(1)):
    return sum((c * (b ** (j + 1) - a ** (j + 1)) / (j + 1)
                for j, c in enumerate(p)), F(0))


def multiply(p, q):
    out = [F(0)] * (len(p) + len(q) - 1)
    for i, x in enumerate(p):
        for j, y in enumerate(q):
            out[i + j] += x * y
    return out


def quadratic_range(p, a, b):
    assert len(p) <= 3
    values = [at(p, a), at(p, b)]
    if len(p) == 3 and p[2]:
        vertex = -p[1] / (2 * p[2])
        if a <= vertex <= b:
            values.append(at(p, vertex))
    return min(values), max(values)


def enclosure(p, n, h=F(1)):
    d2 = derivative(derivative(p))
    midpoint, lo, hi, radius = F(0), F(0), F(0), F(0)
    simpson, simpson_radius = F(0), F(0)
    for j in range(n):
        a, b = F(j, n), F(j + 1, n)
        m = (a + b) / 2
        lower, upper = quadratic_range(d2, a, b)
        midpoint += h * at(p, m) / n
        lo += h * lower / (24 * n ** 3)
        hi += h * upper / (24 * n ** 3)
        radius += h * max(abs(lower), abs(upper)) / (24 * n ** 3)
        simpson += h * (at(p, a) + 4 * at(p, m) + at(p, b)) / (6 * n)
        simpson_radius += h * (upper - lower) / (162 * n ** 3)
    return {'signed': (midpoint + lo, midpoint + hi),
            'symmetric': (midpoint - radius, midpoint + radius),
            'simpson_C2': (simpson - simpson_radius, simpson + simpson_radius),
            'signed_remainder': (lo, hi), 'midpoint': midpoint,
            'exact_integral': h * integral(p)}


def inside(x, interval):
    return interval[0] <= x <= interval[1]


def nested(a, b):
    return b[0] <= a[0] <= a[1] <= b[1]


def encode(x):
    if isinstance(x, F):
        return str(x)
    if isinstance(x, dict):
        return {k: encode(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [encode(v) for v in x]
    return x


def main():
    started = time.perf_counter()
    cases = {
        'zero': [F(0)],
        'constant_negative': [F(-3, 7)],
        'affine_sign_change': [F(-1, 2), F(1)],
        'convex_quadratic': [F(0), F(0), F(1)],
        'concave_quadratic': [F(0), F(0), F(-1)],
        'odd_cubic_curvature_sign_change': [F(-1, 8), F(3, 4), F(-3, 2), F(1)],
        'quartic_curvature_stationary_point': [F(1, 16), F(-1, 2), F(3, 2), F(-2), F(1)],
        'noncentered_quartic': [F(0), F(0), F(0), F(0), F(1)],
    }
    rows, checks = [], []
    def check(label, valid):
        checks.append({'label': label, 'passed': bool(valid)})
        if not valid:
            raise AssertionError(label)
    for name, p in cases.items():
        for n in (1, 2, 4, 8, 32):
            row = enclosure(p, n, F(3, 7))
            row.update(case=name, cells=n, h=F(3, 7))
            rows.append(row)
            for method in ('signed', 'symmetric', 'simpson_C2'):
                check(name + ':' + str(n) + ':' + method + ':exact_integral',
                      inside(row['exact_integral'], row[method]))
            check(name + ':' + str(n) + ':equal_grid_nested',
                  nested(row['signed'], row['symmetric']))
            if len(p) <= 3:
                check(name + ':' + str(n) + ':quadratic_exact',
                      row['signed'][0] == row['signed'][1] == row['exact_integral'])
    # Midpoint's positive second-order Peano kernel has mass 1/24.
    km_left, km_right = [F(0), F(0), F(1, 2)], [F(1, 2), F(-1), F(1, 2)]
    check('midpoint_kernel_mass', integral(km_left, F(0), F(1, 2))
          + integral(km_right, F(1, 2), F(1)) == F(1, 24))
    # Simpson's second-order Peano kernel has zero signed mass.
    ks_left = [F(0), F(-1, 6), F(1, 2)]
    ks_right = [F(1, 3), F(-5, 6), F(1, 2)]
    negative_mass = integral(ks_left, F(0), F(1, 3)) + integral(ks_right, F(2, 3), F(1))
    positive_mass = integral(ks_left, F(1, 3), F(1, 2)) + integral(ks_right, F(1, 2), F(2, 3))
    check('simpson_negative_mass', negative_mass == -F(1, 162))
    check('simpson_positive_mass', positive_mass == F(1, 162))
    for name, p in cases.items():
        d2 = derivative(derivative(p))
        em = integral(multiply(km_left, d2), F(0), F(1, 2)) + integral(multiply(km_right, d2), F(1, 2), F(1))
        es = integral(multiply(ks_left, d2), F(0), F(1, 2)) + integral(multiply(ks_right, d2), F(1, 2), F(1))
        check(name + ':midpoint_peano_identity', em == integral(p) - at(p, F(1, 2)))
        check(name + ':simpson_peano_identity', es == integral(p) - (at(p, F(0)) + 4 * at(p, F(1, 2)) + at(p, F(1))) / 6)
    coarse = enclosure(cases['noncentered_quartic'], 32)
    fine = enclosure(cases['noncentered_quartic'], 512)
    check('coarse_signed_has_no_universal_fine_symmetric_nesting',
          not nested(coarse['signed'], fine['symmetric']))
    zero_curvature = enclosure(cases['zero'], 1)
    odd_curvature = enclosure(cases['odd_cubic_curvature_sign_change'], 1)
    check('zero_exact', zero_curvature['signed'] == (F(0), F(0)))
    check('balanced_sign_change_need_not_improve', odd_curvature['signed'] == odd_curvature['symmetric'])
    result = {'schema': 'bass-he-e13c10-theory-exact-rational-controls-v1',
              'status': 'PASS', 'role': 'AUTHOR_THEORY_CONTROL_NOT_INDEPENDENT_DECISION',
              'rows': rows, 'checks': checks, 'check_count': len(checks),
              'failures': [], 'kernel_masses': {'midpoint': F(1, 24),
                  'simpson_positive': positive_mass, 'simpson_negative': negative_mass},
              'cross_resolution_counterexample': {'polynomial': 'x^4',
                  'signed_N32': coarse['signed'], 'symmetric_N512': fine['symmetric'],
                  'exact_integral': F(1, 5), 'nested': False},
              'captured_coefficient_calls': 0, 'NCP_invocations': 0,
              'original_scientific_reruns': 0,
              'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'elapsed_seconds': time.perf_counter() - started}
    out = Path(__file__).with_name('EXACT_POLYNOMIAL_CONTROLS.json')
    out.write_text(json.dumps(encode(result), indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'rows': len(rows),
                      'checks': len(checks), 'elapsed_seconds': result['elapsed_seconds'],
                      'output': str(out)}))


if __name__ == '__main__':
    main()
