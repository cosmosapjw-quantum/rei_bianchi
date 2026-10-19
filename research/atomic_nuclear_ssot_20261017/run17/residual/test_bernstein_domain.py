import unittest
from fractions import Fraction as F
from bernstein_domain import bernstein_coefficients, dop853_power, shifted_cubic_power


class BernsteinTests(unittest.TestCase):
    def test_interior_negative_polynomial_is_not_certified_from_endpoints(self):
        # p(0)=p(1)=1, p(1/2)=-1: a sampled endpoint-only test would miss it.
        self.assertEqual(bernstein_coefficients([1, -8, 8]), [F(1), F(-3), F(1)])

    def test_positive_quadratic_and_nonconverse(self):
        self.assertEqual(bernstein_coefficients([F(5, 4), -1, 1]),
                         [F(5, 4), F(3, 4), F(5, 4)])
        # Positive everywhere, yet a negative Bernstein lower bound; absence
        # of a certificate must not be promoted to a negative-path finding.
        self.assertLess(min(bernstein_coefficients([F(26, 100), -1, 1])), 0)

    def test_clock_and_independent_dense_basis(self):
        self.assertEqual(shifted_cubic_power([1., 0., 0., 0.], F(2), F(3)),
                         [F(8), F(36), F(54), F(27)])
        coeff = [0.]*7; coeff[6] = 1.
        self.assertEqual(dop853_power(0., coeff), [F(0)]*4+[F(1), F(-3), F(3), F(-1)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
