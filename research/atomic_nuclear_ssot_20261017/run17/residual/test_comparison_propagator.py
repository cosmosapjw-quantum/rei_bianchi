"""Singular and signed-diagonal controls for the actual comparison map."""
import unittest
import numpy as np
from comparison_propagator import propagate_comparison


class ComparisonTests(unittest.TestCase):
    def test_zero_matrix_finite_forcing(self):
        result = propagate_comparison(0., 0., 0., [2., 3.], [.5, .7], .125)
        np.testing.assert_array_equal(result["endpoint"], [.75, 1.075])

    def test_triangular_feedback_polynomial(self):
        # M^2=0: u=u0+rho_u*h, v=v0+c*u0*h+c*rho_u*h^2/2+rho_v*h.
        result = propagate_comparison(0., 0., 4., [.3, .2], [.7, .1], .125)
        np.testing.assert_allclose(result["endpoint"], [.7375, .484375], rtol=0, atol=2e-16)

    def test_negative_gas_log_norm_and_decoupled_depth(self):
        a, duration = -16.7, .0187
        result = propagate_comparison(a, 0., 0., [.2, .3], [.4, .5], duration)
        expected = [np.exp(a*duration)*.4+np.expm1(a*duration)/a*.2, .5+.3*duration]
        np.testing.assert_allclose(result["endpoint"], expected, rtol=2e-15, atol=0)
        self.assertLess(result["initial_contribution"][0], .4)

    def test_nonnegative_coupled_map_and_invalid_domain(self):
        result = propagate_comparison(-.2, .7, 4., [.03, .02], [.01, .005], .3)
        self.assertTrue((result["propagator"] >= 0).all())
        self.assertTrue((result["forcing_contribution"] >= 0).all())
        with self.assertRaises(ValueError):
            propagate_comparison(.1, -.1, 1., [0., 0.], [0., 0.], .1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
