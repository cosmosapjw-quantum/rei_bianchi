"""Exact-input refusal regression; scientific payloads are never opened."""
import unittest
from fractions import Fraction as F
from .engine import (Interval, ResourceLimit, positive_power, half_power,
    radial_gaussian_moment, hermite_coefficient, lower_mass_bound,
    interior_mass_bound, exp_neg_bounds, gamma_half_bounds)


class ExactInputContract(unittest.TestCase):
    def test_interval_rejects_host_float_bool_and_string(self):
        for value in (0.1, True, False, '1/3'):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    Interval(value, 1)

    def test_interval_integer_growth_cap(self):
        with self.assertRaises(ResourceLimit):
            Interval(1 << 17000, 1 << 17000)

    def test_boolean_degrees_rejected(self):
        calls = [lambda: positive_power(1, True), lambda: half_power(1, True),
                 lambda: radial_gaussian_moment(True),
                 lambda: hermite_coefficient(True, 0, F(1)),
                 lambda: hermite_coefficient(0, False, F(1)),
                 lambda: lower_mass_bound(True, F(1), F(1), F(1)),
                 lambda: gamma_half_bounds(True, F(1))]
        for call in calls:
            with self.subTest(call=call):
                with self.assertRaises((TypeError, ValueError, ResourceLimit)):
                    call()

    def test_caps_checked_before_trivial_return(self):
        for params in ({'max_terms': True}, {'max_terms': 1},
                       {'max_squarings': -1}, {'max_squarings': True},
                       {'max_squarings': 10**6}):
            with self.subTest(params=params):
                with self.assertRaises(ResourceLimit):
                    exp_neg_bounds(F(0), **params)

    def test_boolean_panel_count_rejected(self):
        with self.assertRaises(ResourceLimit):
            interior_mass_bound(0,F(1),F(1),F(1),F(2),panels=True)


if __name__ == '__main__':
    unittest.main()
