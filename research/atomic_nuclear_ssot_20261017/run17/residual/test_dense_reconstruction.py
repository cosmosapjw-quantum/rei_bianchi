"""Focused derivative, sign, and actual dense-output reconstruction tests."""
import unittest

import numpy as np
from numpy.polynomial import Polynomial
from scipy.integrate import solve_ivp

from dense_reconstruction import dense_value_derivative, defect, signed_defect_balance


class DenseReconstructionTests(unittest.TestCase):
    def test_seven_term_basis_and_nonunit_clock(self):
        # Independent polynomial basis expansion, including endpoint derivatives.
        x = Polynomial([0., 1.])
        one_minus = Polynomial([1., -1.])
        bases = [x, x*one_minus, x*x*one_minus,
                 x*x*one_minus**2, x**3*one_minus**2,
                 x**3*one_minus**3, x**4*one_minus**3]
        coeff = np.array([[.13, -.9], [-.25, .12], [.5, -.7],
                          [.08, .03], [-.002, .06], [.015, -.14], [.07, .23]])
        y0 = np.array([.9, 1.2])
        t0, h = 3.25, .125
        normalized = np.array([0., .07, .31, .62, 1.])
        value, derivative = dense_value_derivative(t0+h*normalized, t0, h, y0, coeff)
        for column in range(2):
            polynomial = sum((coeff[k, column]*bases[k] for k in range(7)), Polynomial([y0[column]]))
            np.testing.assert_allclose(value[:, column], polynomial(normalized), rtol=0, atol=2e-15)
            np.testing.assert_allclose(derivative[:, column], polynomial.deriv()(normalized)/h, rtol=0, atol=3e-14)

    def test_scalar_derivative_avoids_initial_state_cancellation(self):
        coeff = np.zeros((7, 1)); coeff[0, 0] = 1e-20
        value, derivative = dense_value_derivative(.5, 0., 1., [1.], coeff)
        self.assertEqual(value[0], 1.)
        self.assertEqual(derivative[0], 1e-20)

    def test_actual_dop853_dense_values_and_linear_decay_residual(self):
        rate = -16.7
        sol = solve_ivp(lambda t, y: rate*y, (0., .03), [.7, 1.],
                        method="DOP853", rtol=1e-12, atol=1e-14,
                        max_step=.005, dense_output=True)
        self.assertTrue(sol.success)
        worst = 0.
        for piece in sol.sol.interpolants:
            t = piece.t_old+piece.h*np.array([0., .17, .5, .83, 1.])
            value, derivative = dense_value_derivative(t, piece.t_old, piece.h, piece.y_old, piece.F)
            np.testing.assert_array_equal(value, piece(t).T)
            worst = max(worst, float(np.max(np.abs(derivative-rate*value))))
        self.assertLess(worst, 1e-10)

    def test_residual_sign_and_forced_linear_balance(self):
        # hat_y(t)=1+t, y'=2, y(0)=1: r_hat=-1 and delta(1)=-1.
        coefficients = np.zeros((7, 1)); coefficients[0, 0] = 1.
        value, residual = defect(.4, 0., 1., [1.], coefficients,
                                 lambda t, y: np.array([2.]))
        np.testing.assert_allclose(value, [1.4], rtol=0, atol=0)
        np.testing.assert_array_equal(residual, [-1.])
        np.testing.assert_array_equal(signed_defect_balance([0.], [-1.], [0.], [-1.]), [0.])

    def test_invalid_domain_and_polynomial_rejected(self):
        coefficients = np.zeros((7, 1))
        for t, h, coeff in [(1.1, 1., coefficients), (0., 0., coefficients),
                            (0., 1., np.zeros((6, 1)))]:
            with self.assertRaises(ValueError):
                dense_value_derivative(t, 0., h, [1.], coeff)
        with self.assertRaises(ValueError):
            defect([.5], 0., 1., [1.], coefficients, lambda t, y: y)


if __name__ == "__main__":
    unittest.main(verbosity=2)
