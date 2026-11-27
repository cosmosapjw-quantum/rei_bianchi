"""New exact-sum and normalization checks; no old physics execution is replayed."""
from fractions import Fraction as F
from math import comb
import unittest

from wu088_hh import phys71_angular_d3 as d3


class ThirdBornAngularTests(unittest.TestCase):
    def test_screen_and_ratio_constants(self):
        self.assertEqual(d3.DELTA, F(3, 10**23))
        self.assertEqual(d3.ANGULAR_C, F(1, 9*10**18))
        self.assertEqual(d3.angular_majorant(3), d3.DELTA)
        self.assertEqual(d3.angular_majorant(4), F(1, 9*10**22))
        self.assertEqual(d3.mode_majorant(28), 77)
        self.assertEqual(d3.mode_majorant(29), F(800*30, 189))

    def test_radial_factor_and_no_factorial(self):
        # Independent scalar Green identity: f=1, V=d exp(-2x),
        # U=d(1-exp(-2x))/4, hence integral U^2 V=d^3/96.
        integral = sum((F((-1)**i*comb(2, i), 2*(i+1)) for i in range(3)), F(0)) / 16
        self.assertEqual(integral, F(1, 96))
        self.assertEqual(d3.RADIAL_FACTOR, integral)

    def test_geometric_moments_satisfy_translation_identity(self):
        # q sum(n+1)^d q^n = sum n^d q^n (d>0), independent
        # finite binomial shift; checks every rational moment used by D3.
        q = F(1, 100)
        self.assertEqual(d3.geometric_moment(0, q), 1/(1-q))
        for degree in range(1, 6):
            shifted = sum((comb(degree, k)*d3.geometric_moment(k, q)
                           for k in range(degree+1)), F(0))
            self.assertEqual(q*shifted, d3.geometric_moment(degree, q))

    def test_polynomial_tail_difference(self):
        coefficients = (7, -5, 0, 3, -2, 1)
        for start in (0, 28, 35, 64):
            value = sum((F(c)*start**n for n, c in enumerate(coefficients)), F(0))
            self.assertEqual(d3.polynomial_geometric_tail(coefficients, start)
                             - d3.polynomial_geometric_tail(coefficients, start+1),
                             value*F(1, 100)**start)

    def test_asymptotic_convolution_matches_finite_plus_exact_tail(self):
        for b in (0, 20, 21, 28):
            coefficients = d3.asymptotic_inner_polynomial(b)
            for j in (max(32, b+7), 36, 65):
                polynomial = sum((value*j**degree for degree, value in enumerate(coefficients)), F(0))
                self.assertEqual(d3.inner_convolution(j, b), d3.power10(-j)*polynomial)

    def test_one_sided_tail_difference_all_transition_cases(self):
        for a, b in ((21, 20), (20, 21), (28, 28), (0, 28)):
            for cutoff in (28, 29, 30, 31, 32, 34, 36, 64):
                j = cutoff+1
                exact_row = (d3.mode_majorant(j)**2*d3.angular_majorant(abs(a-j))
                             *d3.inner_convolution(j, b))
                self.assertEqual(d3.one_sided_tail(cutoff, a, b)-d3.one_sided_tail(cutoff+1, a, b),
                                 exact_row)

    def test_symmetry_monotonicity_and_goal(self):
        old = None
        for cutoff in (28, 36, 64):
            value = d3.excluded_third_born_bound(cutoff)
            self.assertGreater(value, 0)
            self.assertEqual(value, d3.excluded_third_born_bound(cutoff, 20, 21))
            self.assertEqual(value, d3.excluded_third_born_bound(cutoff, m=-20))
            if old is not None:
                self.assertLess(value, old)
            old = value
        goal = d3.excluded_third_born_bound(36)
        self.assertEqual(d3.minimum_cutoff_for_goal(goal), 36)
        self.assertIsNone(d3.minimum_cutoff_for_goal(goal/10**200))

    def test_complete_double_sum_symmetry_and_finite_block(self):
        full = d3.full_third_born_bound()
        self.assertEqual(full, d3.full_third_born_bound(20, 21))
        block = sum((d3.mode_majorant(j)**2*d3.mode_majorant(k)**2
                     *d3.angular_majorant(abs(21-j))*d3.angular_majorant(abs(j-k))
                     *d3.angular_majorant(abs(20-k)) for j in range(37) for k in range(37)), F(0))
        block *= d3.EXTERNAL_RATIO_PRODUCT*d3.RADIAL_FACTOR
        self.assertGreater(full, block)
        self.assertLessEqual(full-block, d3.excluded_third_born_bound(36))

    def test_exact_certificate(self):
        record = d3.certificate()
        self.assertEqual(record["target"]["coefficient"], "D3=Z'''(0)/6")
        self.assertTrue(record["angular_overlap_double_counted"])
        self.assertFalse(record["angular_sum_truncation"])
        for row in record["angular_rows"]:
            exact = row["absolute_angular_tail_bound"]
            value = F(int(exact["numerator"]), int(exact["denominator"]))
            self.assertEqual(value, d3.excluded_third_born_bound(row["L"]))
            self.assertGreaterEqual(F(row["upper_decimal"]), value)

    def test_invalid_inputs(self):
        calls = (
            lambda: d3.angular_majorant(True), lambda: d3.mode_majorant(-1),
            lambda: d3.excluded_third_born_bound(27), lambda: d3.excluded_third_born_bound(28.0),
            lambda: d3.excluded_third_born_bound(28, 29, 20),
            lambda: d3.excluded_third_born_bound(28, m=21),
            lambda: d3.minimum_cutoff_for_goal(1e-80), lambda: d3.minimum_cutoff_for_goal("0"),
            lambda: d3.polynomial_geometric_tail([1.0], 0),
            lambda: d3.geometric_moment(2, F(1)), lambda: d3.certificate(()),
        )
        for call in calls:
            with self.assertRaises(ValueError):
                call()


if __name__ == "__main__":
    unittest.main()
