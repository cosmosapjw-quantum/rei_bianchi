#!/usr/bin/env python3
"""Discriminating tests for the new crossed-grid analysis algebra."""
import unittest
from decimal import Decimal as D

import analyze_time_age as a


class TimeAgeAnalysisTests(unittest.TestCase):
    def test_additive_time_and_birth_errors_cancel(self):
        def f(h, e):
            return D(7) + D(3)*h**2 + D(5)*e**3
        corners = [f(h, e) for e in (D(1), D('0.5')) for h in (D(1), D('0.5'))]
        self.assertEqual(a.mixed(*corners)['D_tr'], 0)

    def test_bilinear_mixed_error_and_conditional_h_order(self):
        def f(h, e):
            return D(7) + D(3)*h**2 + D(5)*e**3 + D(11)*h**2*e**3
        results = []
        for h0 in (D(1), D('0.5')):
            corners = [f(h, e) for e in (D(1), D('0.5')) for h in (h0, h0/2)]
            results.append(a.mixed(*corners)['D_tr'])
        self.assertEqual(results[0], D(11)*D('-0.75')*D('-0.875'))
        self.assertEqual(a.order(*results)['value'], 2.0)

    def test_near_equal_corners_retain_native_text_difference(self):
        values = [D('1.0000000000000000000000000000000000000000'),
                  D('1.0000000000000000000000000000000000000100'),
                  D('1.0000000000000000000000000000000000000001'),
                  D('1.0000000000000000000000000000000000000103')]
        self.assertEqual(a.mixed(*values)['D_tr'], D('2e-40'))
        self.assertEqual(len({float(x) for x in values}), 1)

    def test_sign_change_and_zero_do_not_receive_orders(self):
        self.assertEqual(a.order(D(1), D(-1)), {'value': None, 'status': 'SIGN_CHANGE'})
        self.assertEqual(a.order(D(1), D(0)), {'value': None, 'status': 'ZERO_DIFFERENCE'})

    def test_only_complete_physical_rectangles_count(self):
        baseline = set(a.BASE_GRID)
        self.assertEqual(a.complete_rectangles(baseline), [])
        self.assertEqual(a.complete_rectangles(baseline | {(16, 4)}), [(16, 2)])
        self.assertEqual(a.complete_rectangles(baseline | set(a.EXTRA_GRID)), [(16, 2), (32, 2)])

    def test_mean_age_uses_survivor_count_and_raw_moments(self):
        row = {key: '1' for key in a.FIELDS if key not in
               ('mean_age_s', 'second_age_s2', 'age_variance_s2', 'energy_P2_numerator_com3')}
        row.update(photons_com3='2', survivor_age_com_s='10', survivor_age2_com_s2='58',
                   q2='0.25', photon_energy_com3='12')
        result = a.observables(row)
        self.assertEqual(result['mean_age_s'], D(5))
        self.assertEqual(result['second_age_s2'], D(29))
        self.assertEqual(result['age_variance_s2'], D(4))
        self.assertEqual(result['energy_P2_numerator_com3'], D(3))
        row['photons_com3'] = '0'
        with self.assertRaises(ValueError):
            a.observables(row)

    def test_ratio_observable_can_create_mixed_defect(self):
        # Numerator and denominator are individually additive in h and epsilon.
        # Their ratio need not be additive; a nonzero D does not identify a
        # mixed defect in the transport operator by itself.
        corners = [(D(1)+h)/(D(2)+e) for e in (D(1), D('0.5')) for h in (D(1), D('0.5'))]
        self.assertLess(a.mixed(*corners)['D_tr'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
