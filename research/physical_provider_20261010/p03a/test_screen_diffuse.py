"""Analytic finite-surrogate tests, not physical diffuse validation."""
import unittest

import numpy as np

from screen_diffuse import escape_energy_screen, tail_optical_depth


class FiniteGridTests(unittest.TestCase):
    def test_constant_opacity_matches_analytic_survival(self):
        times = np.array([0., 1., 3., 8.])
        rates = np.array([0., .01, 2.])
        tau = tail_optical_depth(times, np.tile(rates, (4, 1)))
        expected = (8-times[:, None])*rates
        np.testing.assert_allclose(tau, expected, rtol=2e-16, atol=0.)
        np.testing.assert_allclose(-np.expm1(-tau), 1-np.exp(-expected), atol=1e-16)

    def test_affine_opacity_integral_is_exact(self):
        times = np.array([0., .3, 2., 7.])
        opacity = (1+2*times)[:, None]
        np.testing.assert_allclose(tail_optical_depth(times, opacity)[:, 0],
                                   (7-times)+(49-times**2), rtol=3e-16)

    def test_zero_and_saturated_opacity_do_not_invent_emission(self):
        times = [0., 1., 2.]
        escape = [0., 3., 8.]
        for opacity, expected in ((0., [0., 0.]), (1e4, [3., 5.])):
            probability = -np.expm1(-tail_optical_depth(times, np.full((3, 2), opacity)))
            increments, cap = escape_energy_screen(escape, probability)
            np.testing.assert_array_equal(increments, [3., 5.])
            np.testing.assert_array_equal(cap, expected)

    def test_arbitrary_energy_mixture_is_within_finite_envelope(self):
        probability = np.array([[.1, .8, .4], [.01, .3, .9], [0., 0., 0.]])
        increment, cap = escape_energy_screen([0., 2., 5.], probability)
        for fractions in ([.2, .7, .1], [1., 0., 0.], [0., 0., 1.]):
            absorbed = increment*np.dot(probability[:-1], fractions)
            self.assertTrue(np.all(absorbed <= cap))
        self.assertLessEqual(cap.sum(), 5.)

    def test_invalid_domain_is_rejected_without_clipping(self):
        for times, opacity in (([0., 0.], [[1.], [1.]]),
                               ([0., 1.], [[-1.], [1.]]),
                               ([0., 1.], [[np.nan], [1.]])):
            with self.assertRaisesRegex(ValueError, "OPACITY_DOMAIN"):
                tail_optical_depth(times, opacity)
        for escape, probability in (([0., -1.], [[0.], [0.]]),
                                    ([1., 2.], [[0.], [0.]]),
                                    ([0., 1.], [[1.01], [0.]])):
            with self.assertRaisesRegex(ValueError, "ESCAPE_DOMAIN"):
                escape_energy_screen(escape, probability)


if __name__ == "__main__":
    unittest.main()
