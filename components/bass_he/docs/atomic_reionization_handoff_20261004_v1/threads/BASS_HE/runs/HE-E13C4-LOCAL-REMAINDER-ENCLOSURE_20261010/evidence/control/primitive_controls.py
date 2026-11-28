#!/usr/bin/env python3
"""Independent exact-rational diagnostics of IV and actual Jet2 derivatives."""
import argparse
from decimal import Decimal as D, localcontext, ROUND_UP
import decimal
from fractions import Fraction as F
import importlib.util
import json
import math
from pathlib import Path
import sys

from rational_reference import exp_bounds, ln_bounds, sqrt_bounds, power_bounds, j_bounds
from run_control import atomic_bytes


def scale(pair, factor):
    a, b = pair[0] * factor, pair[1] * factor
    return min(a, b), max(a, b)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def serialize_fraction(value):
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('owner_interval_control', args.interval)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    mod.configure(60)
    IV, Jet = mod.IV, mod.Jet2
    records = []

    def check(identifier, passed, **detail):
        records.append({'check_id': identifier, 'passed': bool(passed), **detail})

    def enclosure(identifier, candidate, lo, hi, kind='EXACT_RATIONAL_REFERENCE'):
        lo, hi = F(lo), F(hi)
        check(identifier, F(candidate.lo) <= lo <= hi <= F(candidate.hi),
              kind=kind, owner_interval=candidate.json(),
              reference={'lo': serialize_fraction(lo), 'hi': serialize_fraction(hi)})

    def reject(identifier, function):
        try:
            returned = function()
        except (ArithmeticError, ValueError, TypeError) as error:
            check(identifier, True, observed_exception=type(error).__name__, message=str(error))
        else:
            check(identifier, False, observed_return=repr(returned), expected='explicit domain error')

    # Exact input images; these operations have simple corner extrema.
    intervals = [IV('-3.125', '-0.0625'), IV('0.125', '7.75'), IV('-1e-40', '1e-40'),
                 IV('1.23456789012345678901234567890123456789012345678901234567890123456789',
                    '1.23456789012345678901234567890123456789012345678901234567890123456799'),
                 IV('-1e-30', '-9e-31'), IV(0)]
    for i, a in enumerate(intervals):
        al, ah = F(a.lo), F(a.hi)
        enclosure(f'NEGATE_{i}', -a, -ah, -al)
        abslo = 0 if al <= 0 <= ah else min(abs(al), abs(ah))
        enclosure(f'ABS_{i}', abs(a), abslo, max(abs(al), abs(ah)))
        sqlo = 0 if al <= 0 <= ah else min(al * al, ah * ah)
        enclosure(f'SQUARE_{i}', a.square(), sqlo, max(al * al, ah * ah))
        for j, b in enumerate(intervals):
            bl, bh = F(b.lo), F(b.hi)
            enclosure(f'ADD_{i}_{j}', a + b, al + bl, ah + bh)
            enclosure(f'SUBTRACT_{i}_{j}', a - b, al - bh, ah - bl)
            products = [x * y for x in (al, ah) for y in (bl, bh)]
            enclosure(f'MULTIPLY_{i}_{j}', a * b, min(products), max(products))
            if not bl <= 0 <= bh:
                quotients = [x / y for x in (al, ah) for y in (bl, bh)]
                enclosure(f'DIVIDE_{i}_{j}', a / b, min(quotients), max(quotients))

    for i, number in enumerate((0.1, math.pi, 1e-18, 2.963, 13.6, 24.59, 54.42, -1e-30)):
        image = IV.from_binary64(number)
        exact = F(*number.as_integer_ratio())
        check(f'BINARY64_LIFT_{i}', F(image.lo) == exact == F(image.hi),
              binary64_hex=number.hex(), owner_interval=image.json(),
              exact_ratio=serialize_fraction(exact))
    check('BINARY64_LIFT_DISTINCT_FROM_DECIMAL_TEXT', IV.from_binary64(0.1).lo != D('0.1'))
    reject('IMPLICIT_FLOAT_REJECTED', lambda: IV(0.1))
    reject('REVERSED_INTERVAL_REJECTED', lambda: IV(2, 1))
    reject('NAN_REJECTED', lambda: IV('NaN'))
    reject('INFINITY_REJECTED', lambda: IV('Infinity'))
    reject('RECIPROCAL_ZERO_CROSSING_REJECTED', lambda: IV(-1, 1).reciprocal())
    reject('LOG_ZERO_REJECTED', lambda: IV(0).ln())
    reject('LOG_NEGATIVE_RANGE_REJECTED', lambda: IV(-1, 2).ln())
    reject('SQRT_NEGATIVE_RANGE_REJECTED', lambda: IV(-1, 2).sqrt())
    reject('JET_SQRT_ZERO_NONSMOOTH_REJECTED', lambda: Jet.variable(IV(0, 1)).sqrt())
    reject('POWER_NONPOSITIVE_BASE_REJECTED', lambda: IV(0, 1).positive_power(IV('0.5')))
    reject('J_ZERO_RATE_NEGATIVE_WIDTH_REJECTED', lambda: mod.response_j(IV(0), IV(-1)))
    reject('J_POSITIVE_RATE_NEGATIVE_WIDTH_REJECTED', lambda: mod.response_j(IV(2), IV(-1)))
    reject('J_NEGATIVE_RATE_REJECTED', lambda: mod.response_j(IV(-2), IV(1)))
    reject('J_RATE_INTERVAL_ZERO_CROSSING_REJECTED', lambda: mod.response_j(IV(0, 2), IV(1)))

    functions = [
        ('EXP', 'exp', exp_bounds,
         ['-52', '-39', '-12', '-0.001', '-1e-35', '0', '1e-35', '0.125', '2', '12', '50'],
         [('-52', '-39'), ('-1e-6', '0'), ('0', '1e-6'), ('-2', '2')]),
        ('LOG', 'ln', ln_bounds,
         ['1e-18', '0.4298', '0.999999999999999999999999999999', '1',
          '1.000000000000000000000000000001', '2', '32.88', '54750'],
         [('1e-18', '1e-15'), ('0.5', '2'), ('1', '1.000001'), ('13.6', '100')]),
        ('SQRT', 'sqrt', sqrt_bounds,
         ['0', '1e-40', '2e-80', '0.125', '2', '7.75', '1024', '1e8'],
         [('0', '1e-40'), ('0.125', '2'), ('1', '1.000001'), ('13.6', '100')]),
    ]
    for label, operation, reference, points, ranges in functions:
        for i, point in enumerate(points):
            val = IV(point)
            lo, hi = reference(F(D(point)))
            enclosure(f'{label}_POINT_{i}', getattr(val, operation)(), lo, hi,
                      kind='PROVED_RATIONAL_TRANSCENDENTAL_REFERENCE')
        for i, (left, right) in enumerate(ranges):
            val = IV(left, right)
            lo = reference(F(D(left)))[0]
            hi = reference(F(D(right)))[1]
            enclosure(f'{label}_RANGE_{i}', getattr(val, operation)(), lo, hi,
                      kind='MONOTONE_ENDPOINT_REFERENCE_ENCLOSURE')

    for i, base in enumerate(('0.4298', '1', '32.88', '1e-18')):
        for j, exponent in enumerate((-2.963, -4.0185, 3.188)):
            p = IV.from_binary64(exponent)
            lo, hi = power_bounds(F(D(base)), F(p.lo))
            enclosure(f'POWER_{i}_{j}', IV(base).positive_power(p), lo, hi,
                      kind='PROVED_RATIONAL_TRANSCENDENTAL_REFERENCE')
    power_domain = IV('0.4298', '32.88')
    exponent_domain = IV('-4.0185', '-2.963')
    all_corners = [power_bounds(F(x), F(p)) for x in (power_domain.lo, power_domain.hi)
                   for p in (exponent_domain.lo, exponent_domain.hi)]
    enclosure('POWER_RECTANGLE_RANGE', power_domain.positive_power(exponent_domain),
              min(x[0] for x in all_corners), max(x[1] for x in all_corners),
              kind='BILINEAR_LOG_DOMAIN_EXTREMA')

    for i, (rate, h) in enumerate((('2', '1e-5'), ('1e-6', '2'), ('0', '0.5'),
                                  ('157', '0'), ('1e-12', '1e-7'))):
        lo, hi = j_bounds(F(D(rate)), F(D(h)))
        enclosure(f'J_POINT_{i}', mod.response_j(IV(rate), IV(h)), lo, hi,
                  kind='PROVED_RATIONAL_TRANSCENDENTAL_REFERENCE')
    enclosure('J_RECTANGLE_RANGE', mod.response_j(IV(100, 125), IV(0, '0.001')),
              j_bounds(F(125), F(0))[0], j_bounds(F(100), F(1, 1000))[1],
              kind='MONOTONICITY_RATE_DECREASE_WIDTH_INCREASE')

    p = F(D.from_float(-3.188))
    def jet_images(x):
        g = 3 * x.square() + 2
        return {
            'CUBIC': x * x * x + 2 * x.square() - 7 * x + 11,
            'RECIPROCAL_QUADRATIC': g.reciprocal(),
            'LOG_QUADRATIC': g.ln(),
            'SQRT_QUADRATIC': g.sqrt(),
            'EXP_QUADRATIC': (2 * x.square() - 3 * x).exp(),
            'POWER_QUADRATIC': g.positive_power(IV(D.from_float(-3.188))),
        }

    def expected_jets(t):
        g, gp, gpp = 3 * t * t + 2, 6 * t, F(6)
        root = sqrt_bounds(g)
        exponential = exp_bounds(2 * t * t - 3 * t)
        power, power1, power2 = power_bounds(g, p), power_bounds(g, p - 1), power_bounds(g, p - 2)
        cubic = t ** 3 + 2 * t * t - 7 * t + 11
        recip_d2 = (54 * t * t - 12) / (g ** 3)
        log_d1, log_d2 = gp / g, (12 - 18 * t * t) / (g * g)
        sqrt_d1 = scale((1 / root[1], 1 / root[0]), 3 * t)
        sqrt_d2 = (6 / root[1] ** 3, 6 / root[0] ** 3)
        return {
            'CUBIC': [(cubic, cubic), (3 * t * t + 4 * t - 7,) * 2, (6 * t + 4,) * 2],
            'RECIPROCAL_QUADRATIC': [(1 / g,) * 2, (-gp / (g * g),) * 2, (recip_d2,) * 2],
            'LOG_QUADRATIC': [ln_bounds(g), (log_d1,) * 2, (log_d2,) * 2],
            'SQRT_QUADRATIC': [root, sqrt_d1, sqrt_d2],
            'EXP_QUADRATIC': [exponential, scale(exponential, 4 * t - 3),
                              scale(exponential, 4 + (4 * t - 3) ** 2)],
            'POWER_QUADRATIC': [power, scale(power1, p * gp),
                                add(scale(power2, p * (p - 1) * gp * gp), scale(power1, p * gpp))],
        }

    for i, point in enumerate(('-0.5', '0', '0.25', '0.875')):
        actual = jet_images(Jet.variable(IV(point)))
        reference = expected_jets(F(D(point)))
        for label, jet in actual.items():
            for order, field in enumerate(('v', 'd1', 'd2')):
                enclosure(f'JET_{label}_{i}_ORDER_{order}', getattr(jet, field),
                          *reference[label][order], kind='CLOSED_FORM_DERIVATIVE_AT_POINT')
    # The full-cell derivative image must contain independent values at endpoints
    # and interior points. This is an implementation diagnostic, not a continuum proof.
    actual = jet_images(Jet.variable(IV('-0.25', '0.75')))
    for i, point in enumerate(('-0.25', '0', '0.5', '0.75')):
        reference = expected_jets(F(D(point)))
        for label, jet in actual.items():
            for order, field in enumerate(('v', 'd1', 'd2')):
                enclosure(f'JET_CELL_{label}_{i}_ORDER_{order}', getattr(jet, field),
                          *reference[label][order], kind='CELL_RANGE_POINT_DIAGNOSTIC')

    for i, (rate_text, h_text, t_text) in enumerate((('0', '0.001', '0.25'),
                                                  ('2', '0.001', '0.25'),
                                                  ('137.4', '1e-6', '0.75'))):
        rate, h, t = map(lambda x: F(D(x)), (rate_text, h_text, t_text))
        actual = mod.response_j(IV(rate_text), IV(h_text) * Jet.variable(IV(t_text)))
        exponential = exp_bounds(-rate * h * t)
        expected = [j_bounds(rate, h * t), scale(exponential, h), scale(exponential, -rate * h * h)]
        for order, field in enumerate(('v', 'd1', 'd2')):
            enclosure(f'J_JET_{i}_ORDER_{order}', getattr(actual, field), *expected[order],
                      kind='CLOSED_FORM_J_DERIVATIVE')

    def ambient_image():
        x = IV('1.23456789012345678901234567890123456789012345678901234567890123456789')
        y = IV('-0.12345678901234567890123456789012345678901234567890123456789')
        jet = ((Jet.variable(x).square() + 2).ln() / (3 + Jet.variable(x))).exp()
        outputs = [-x, abs(y), x + y, x * y, x / y, x.sqrt(), x.ln(), y.exp(),
                   x.positive_power(IV('-2.963')), mod.response_j(IV('2.3'), IV('0.00001')),
                   jet.v, jet.d1, jet.d2]
        return [v.json() for v in outputs]
    with localcontext() as context:
        context.prec = 110
        normal = ambient_image()
    with localcontext() as context:
        context.prec = 3
        context.rounding = ROUND_UP
        context.Emax = 28
        context.Emin = -28
        hostile = ambient_image()
    check('AMBIENT_PRECISION_AND_ROUNDING_INDEPENDENCE', normal == hostile,
          normal=normal, hostile=hostile)

    # A deliberately inward interval must be rejected by the containment test.
    true_lo, true_hi = exp_bounds(F(1))
    shrunken_lo = true_hi + F(1, 10 ** 60)
    check('NEGATIVE_CONTROL_INWARD_EXP_ENDPOINT_DETECTED',
          not (shrunken_lo <= true_lo <= true_hi <= shrunken_lo + 1),
          kind='CHECKER_SENSITIVITY')
    failed = [r['check_id'] for r in records if not r['passed']]
    result = {'schema': 'BASS_HE_E13C4_PRIMITIVE_CONTROL_V1',
              'role': 'independent numerical contributor; not final decision reviewer',
              'precision': 60, 'rational_reference_fractional_digits': 110,
              'rational_reference_guard_digits': 20,
              'libmpdec_version': decimal.__libmpdec_version__,
              'check_count': len(records), 'passed_count': len(records) - len(failed),
              'failed_check_ids': failed, 'checks': records,
              'claim_ceiling': 'Finite independent implementation diagnostics. The rational reference bounds are mathematical enclosures; tests do not prove all owner inputs.',
              'old_collocation_or_oracle_executed': False}
    atomic_bytes(args.output, (json.dumps(result, indent=2) + '\n').encode())
    print(json.dumps({k: result[k] for k in ('check_count', 'passed_count', 'failed_check_ids', 'libmpdec_version')}))
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
