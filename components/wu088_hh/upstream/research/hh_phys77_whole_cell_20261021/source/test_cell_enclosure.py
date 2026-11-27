"""Independent analytic controls for PHYS77's generic cell inclusion.

No ODE solver, scientific trajectory replay, benchmark or massive packet run.
The toy systems have closed-form solutions; Fraction provides independent
exact arithmetic controls for exp and squared sqrt bounds.
"""
from __future__ import annotations

from decimal import Context, Decimal, localcontext
from fractions import Fraction
from pathlib import Path
import os
import sys
import unittest

SOURCE = Path(os.environ['PHYS77_SOURCE']).resolve() if 'PHYS77_SOURCE' in os.environ else Path(__file__).resolve().parent
sys.path.insert(0, str(SOURCE))
from cell_enclosure import certify_cell, exact_difference
from owner_interval import Arithmetic, Interval


def dec(value):
    return Decimal(str(value))


def interval(lo, hi=None):
    return Interval(dec(lo), dec(lo if hi is None else hi))


def unpack(value):
    return Interval(Decimal(value[0]), Decimal(value[1]))


def fraction_exp_enclosure(x, terms=100):
    """Exact rational Taylor bound; never calls Decimal.exp or binary math."""
    x = Fraction(x)
    u = abs(x)
    if u > 1:
        raise ValueError('reference bounded to |x|<=1')
    total, term = Fraction(1), Fraction(1)
    for k in range(1, terms + 1):
        term *= u / k
        total += term
    first_omitted = term * u / (terms + 1)
    tail = first_omitted / (1 - u / (terms + 2))
    if x >= 0:
        return total, total + tail
    return 1 / (total + tail), 1 / total


class ToyOwner:
    def __init__(self, rhs, precision=50, domain=None):
        self.a = Arithmetic(precision)
        self.rhs = rhs
        self.domain = domain

    def evaluate(self, x, y):
        if self.domain is not None:
            self.domain(x, y)
        return {'rhs': self.rhs(self.a, x, y)}


class CellAnalyticTests(unittest.TestCase):
    def assertContains(self, bound, value):
        if isinstance(bound, list):
            bound = unpack(bound)
        lo, hi = Fraction(bound.lo), Fraction(bound.hi)
        value = Fraction(value)
        self.assertLessEqual(lo, value)
        self.assertLessEqual(value, hi)

    def test_linear_signed_growth_and_decay_closed_form(self):
        reference = Context(prec=180)
        for lam in ('-2', '0', '2'):
            with self.subTest(lam=lam):
                owner = ToyOwner(lambda a, x, y, ll=lam: [a.multiply(a.point(ll), y[0])])
                h = dec('0.05')
                target = reference.exp(reference.multiply(dec(lam), h))
                result = certify_cell(owner, dec(0), h, [dec(1)], [target],
                                      [interval(1)], radius_floor=dec('1e-16'))
                self.assertEqual(result['status'], 'FINITE_OWNER_CELL_ENCLOSED')
                for k in range(11):
                    t = reference.divide(reference.multiply(h, Decimal(k)), Decimal(10))
                    truth = reference.exp(reference.multiply(dec(lam), t))
                    self.assertContains(result['whole_cell_state_box'][0], truth)
                self.assertContains(result['endpoint_state_box'][0], target)

    def test_nonlinear_square_closed_form_initial_family(self):
        owner = ToyOwner(lambda a, x, y: [a.square(y[0])])
        reference = Context(prec=180)
        h = dec('0.125')
        target = reference.divide(Decimal(8), Decimal(39))
        result = certify_cell(owner, dec(0), h, [dec('.2')], [target],
                              [interval('.19', '.21')], radius_floor=dec('1e-15'))
        self.assertEqual(result['status'], 'FINITE_OWNER_CELL_ENCLOSED')
        for initial in (Fraction(19, 100), Fraction(1, 5), Fraction(21, 100)):
            for k in range(9):
                t = Fraction(k, 64)
                truth = initial / (1 - initial * t)
                self.assertContains(result['whole_cell_state_box'][0], truth)
            truth_end = initial / (1 - initial * Fraction(1, 8))
            self.assertContains(result['endpoint_state_box'][0], truth_end)

    def test_nonzero_initial_error_is_carried_across_cells(self):
        owner = ToyOwner(lambda a, x, y: [a.one])
        first = certify_cell(owner, dec(0), dec('.1'), [dec(0)], [dec('.1')],
                             [interval('-.01', '.01')])
        self.assertEqual(first['status'], 'FINITE_OWNER_CELL_ENCLOSED')
        carried = [unpack(v) for v in first['endpoint_state_box']]
        second = certify_cell(owner, dec('.1'), dec('.2'), [dec('.1')], [dec('.2')], carried)
        self.assertEqual(second['status'], 'FINITE_OWNER_CELL_ENCLOSED')
        self.assertEqual(unpack(second['initial_error_box'][0]), interval('-.01', '.01'))
        self.assertEqual(unpack(second['endpoint_state_box'][0]), interval('.19', '.21'))
        self.assertContains(second['endpoint_state_box'][0], Fraction(19, 100))
        self.assertContains(second['endpoint_state_box'][0], Fraction(21, 100))

    def test_signed_endpoint_h_defect_differs_from_whole_time_hull(self):
        owner = ToyOwner(lambda a, x, y: [a.integer(-2), a.integer(3)])
        result = certify_cell(owner, dec(0), dec('.1'), [dec(1), dec(1)],
                              [dec(1), dec(1)], [interval(1), interval(1)],
                              radius_floor=dec('.01'), max_inflations=3)
        self.assertEqual(result['status'], 'FINITE_OWNER_CELL_ENCLOSED')
        image = [unpack(v) for v in result['attempts'][-1]['image']]
        endpoint_error = [unpack(v) for v in result['endpoint_error_box']]
        self.assertEqual(image, [interval('-.2', 0), interval(0, '.3')])
        self.assertEqual(endpoint_error, [interval('-.2'), interval('.3')])
        self.assertEqual([unpack(v) for v in result['endpoint_state_box']],
                         [interval('.8'), interval('1.3')])

    def test_captured_rounded_affine_slope_uses_its_actual_endpoint(self):
        owner = ToyOwner(lambda a, x, y: [a.point('0.3333333333333333')], precision=16)
        result = certify_cell(owner, dec(0), dec(3), [dec(0)], [dec(1)],
                              [interval(0)], radius_floor=dec('1e-18'))
        self.assertEqual(result['status'], 'FINITE_OWNER_CELL_ENCLOSED')
        actual = Fraction(3333333333333333, 10**16) * 3
        self.assertContains(result['endpoint_state_box'][0], actual)
        endpoint = unpack(result['predictor_actual_endpoint'][0])
        self.assertEqual(endpoint, interval('0.9999999999999999'))
        self.assertLess(endpoint.hi, dec(1))

    def test_regular_triangular_family_does_not_chase_valid_component(self):
        # y1=c, y2=20*c*t. The full-step unweighted Lipschitz factor is 2,
        # yet a strict box inclusion exists; the source dimension is only two.
        owner = ToyOwner(lambda a, x, y: [a.zero, a.scale(20, y[0])])
        result = certify_cell(owner, dec(0), dec('.1'), [dec(0), dec(0)],
                              [dec(0), dec(0)], [interval(-1, 1), interval(0)],
                              radius_floor=dec('.001'), max_inflations=3)
        self.assertEqual(result['status'], 'FINITE_OWNER_CELL_ENCLOSED')
        for c in (Fraction(-1), Fraction(0), Fraction(1)):
            self.assertContains(result['endpoint_state_box'][0], c)
            self.assertContains(result['endpoint_state_box'][1], 2*c)

    def test_interior_forcing_peak_has_nonzero_whole_cell_defect(self):
        # y'=4t(1-t), y(0)=0; forcing vanishes at both nodes 0 and 1.
        # Deliberately choose a zero predictor. True y(1)=2/3.
        owner = ToyOwner(lambda a, x, y: [a.scale(4, a.multiply(x, a.subtract(a.one, x)))])
        result = certify_cell(owner, dec(0), dec(1), [dec(0)], [dec(0)], [interval(0)],
                              radius_floor=dec('.001'), max_inflations=3)
        self.assertEqual(result['status'], 'FINITE_OWNER_CELL_ENCLOSED')
        self.assertContains(result['endpoint_state_box'][0], Fraction(2, 3))
        self.assertGreater(unpack(result['defect_box'][0]).hi, dec(0))
        self.assertContains(result['whole_cell_state_box'][0], Fraction(1, 3))

    def test_failed_inclusion_stays_noncertificate_with_attempt_record(self):
        owner = ToyOwner(lambda a, x, y: [a.one])
        result = certify_cell(owner, dec(0), dec('.1'), [dec(0)], [dec(0)], [interval(0)],
                              radius_floor=dec('.001'), max_inflations=1)
        self.assertEqual(result['status'], 'NOT_CERTIFIED')
        self.assertEqual(len(result['attempts']), 1)
        self.assertEqual(result['attempts'][0]['strict_inclusion'], [False])
        self.assertNotIn('endpoint_state_box', result)

    def test_singular_domain_candidate_is_rejected(self):
        def domain(x, y):
            if y[0].hi >= 1:
                raise ValueError('TOY_REGULAR_DOMAIN_Y_LT_ONE')
        owner = ToyOwner(lambda a, x, y: [a.divide(a.one, a.subtract(a.one, y[0]))], domain=domain)
        result = certify_cell(owner, dec(0), dec('.1'), [dec('.9')], [dec('1.1')], [interval('.9')])
        self.assertEqual(result['status'], 'NOT_CERTIFIED')
        self.assertEqual(result['attempts'][0]['status'], 'DOMAIN_OR_ARITHMETIC_REJECTED')
        self.assertIn('TOY_REGULAR_DOMAIN_Y_LT_ONE', result['attempts'][0]['reason'])

    def test_invalid_cell_controls_are_rejected(self):
        owner = ToyOwner(lambda a, x, y: [a.zero])
        for x0, x1 in ((dec(0), dec(0)), (dec(-1), dec(1)), (dec(1), dec(0))):
            with self.subTest(x0=x0, x1=x1), self.assertRaises(ValueError):
                certify_cell(owner, x0, x1, [dec(0)], [dec(0)], [interval(0)])
        for kwargs in ({'max_inflations':0}, {'max_inflations':True},
                       {'radius_floor':dec(0)}, {'inflation_factor':dec(1)}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                certify_cell(owner, dec(0), dec(1), [dec(0)], [dec(0)], [interval(0)], **kwargs)

    def test_reversed_initial_box_is_rejected(self):
        owner = ToyOwner(lambda a, x, y: [a.zero])
        with self.assertRaises(ValueError):
            certify_cell(owner, dec(0), dec('.1'), [dec(0)], [dec(0)], [interval(2, 1)])

    def test_ambient_decimal_context_does_not_round_cell_width(self):
        left = dec('1.000000000000000000000000000001')
        right = dec('1.000000000000000000000000000002')
        owner = ToyOwner(lambda a, x, y: [a.zero])
        with localcontext() as ambient:
            ambient.prec = 6
            self.assertEqual(exact_difference(right, left), dec('1e-30'))
            result = certify_cell(owner, left, right, [dec(0)], [dec(0)], [interval(0)],
                                  radius_floor=dec('1e-40'))
        self.assertEqual(result['status'], 'FINITE_OWNER_CELL_ENCLOSED')
        self.assertEqual(Decimal(result['h']), dec('1e-30'))


class ArithmeticIndependentTests(unittest.TestCase):
    def test_square_crossing_zero_and_endpoint_exact_rationals(self):
        a = Arithmetic(40)
        for x in (interval('-2', '3'), interval('-3', '-2'), interval('.1', '.3'),
                  interval('-1e30', '3e-30'), interval(0)):
            with self.subTest(x=x):
                out = a.square(x)
                ends = [Fraction(x.lo)**2, Fraction(x.hi)**2]
                true_lo = Fraction(0) if x.lo <= 0 <= x.hi else min(ends)
                self.assertLessEqual(Fraction(out.lo), true_lo)
                self.assertGreaterEqual(Fraction(out.hi), max(ends))
                self.assertGreaterEqual(out.lo, dec(0))

    def test_sqrt_exact_squared_endpoint_bounds_and_180_digit_reference(self):
        a, reference = Arithmetic(40), Context(prec=180)
        for x in (interval(0), interval(2), interval('1e-100', '3e-99'),
                  interval('1e100', '9e100'), interval('0', '0.000000000000000000000002')):
            with self.subTest(x=x):
                out = a.sqrt(x)
                self.assertGreaterEqual(out.lo, dec(0))
                self.assertLessEqual(Fraction(out.lo)**2, Fraction(x.lo))
                self.assertGreaterEqual(Fraction(out.hi)**2, Fraction(x.hi))
                self.assertLessEqual(out.lo, reference.sqrt(x.lo))
                self.assertGreaterEqual(out.hi, reference.sqrt(x.hi))

    def test_exp_independent_exact_series_endpoint_enclosures(self):
        a = Arithmetic(40)
        for x in (interval(0), interval('-1'), interval('.75'), interval('-.8', '.2'), interval('1e-38')):
            with self.subTest(x=x):
                out = a.exp(x)
                lower, _ = fraction_exp_enclosure(Fraction(x.lo))
                _, upper = fraction_exp_enclosure(Fraction(x.hi))
                self.assertLessEqual(Fraction(out.lo), lower)
                self.assertGreaterEqual(Fraction(out.hi), upper)
                self.assertGreater(out.lo, dec(0))

    def test_elementary_domain_and_quiet_subnormal_neighbors_are_rejected(self):
        a = Arithmetic(40)
        with self.assertRaises(ValueError):
            a.sqrt(interval('-0.01', '1'))
        with self.assertRaises(ArithmeticError):
            a.sqrt(interval('1e-1999998'))
        reference = Context(prec=180)
        exp_input = reference.multiply(reference.ln(Decimal(10)), Decimal(-999999))
        with self.assertRaises(ArithmeticError):
            a.exp(Interval(exp_input, exp_input))


if __name__ == '__main__':
    unittest.main(verbosity=2)
