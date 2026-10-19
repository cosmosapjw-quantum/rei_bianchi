"""Independent analytic controls for RUN16 response and quadrature contracts."""
from decimal import Decimal, localcontext
from types import SimpleNamespace
import unittest

import numpy as np
import gas_path_response as g


class ResponseTests(unittest.TestCase):
    def test_tiny_signed_remainder_against_decimal80(self):
        xs = [-20., -.2, -.009, -1e-10, 0., 1e-14, 1e-6, .009, .2, 20.]
        with localcontext() as ctx:
            ctx.prec = 80
            for x in xs:
                d = Decimal.from_float(x)
                expected = float((-d).exp()-1+d)
                actual = float(g.exp_remainder(x))
                self.assertLessEqual(abs(actual-expected), 4e-15*abs(expected)+1e-300)

    def test_signed_finite_change_convexity(self):
        weights = np.array([2., 3., 1.])
        dt = np.array([-1e-6, 2e-6, -.003])
        r = g.finite_response(weights, dt)
        with localcontext() as ctx:
            ctx.prec = 80
            expected = sum(Decimal.from_float(float(w))*((-Decimal.from_float(float(d))).exp()-1)
                           for w, d in zip(weights, dt))
        self.assertAlmostEqual(r['delta_S_com3'], float(expected), delta=2e-18)
        self.assertGreaterEqual(r['convex_remainder_com3'], r['remainder_lower_com3'])
        self.assertLessEqual(r['convex_remainder_com3'], r['remainder_upper_com3'])
        self.assertLess(abs(r['stable_identity_absolute_residual_com3']), 2e-18)

    def test_positive_kernel_uniform_enclosure(self):
        K = np.array([[.1, 2., .3], [1., .5, 0.], [2., .01, 4.]])
        n = np.array([.8, 1.2, .3])
        tau = K@n
        w = np.array([.3, 4., .9])
        v = w*np.exp(-tau)
        eps = .002
        env = g.uniform_envelope(v, tau, eps)
        for direction in ([1, -1, .4], [-.7, .2, .9], [1, 1, 1], [-1, -1, -1]):
            perturbed = n*(1+eps*np.array(direction))
            s = float(np.dot(w, np.exp(-K@perturbed)))
            self.assertGreaterEqual(s, env['core_lower_com3']*(1-4e-15))
            self.assertLessEqual(s, env['core_upper_com3']*(1+4e-15))
        for eps_bad in (-1e-9, 1., float('nan')):
            with self.assertRaises(ValueError):
                g.uniform_envelope(v, tau, eps_bad)

    def test_bump_checkpoint_values_and_peak(self):
        knots = np.array([0., .125, .5, 1.])
        np.testing.assert_array_equal(g.bump(knots, knots), 0.)
        np.testing.assert_array_equal(g.bump((knots[:-1]+knots[1:])/2, knots), 1.)
        with self.assertRaises(ValueError):
            g.bump(np.array([-1e-4]), knots)

    def test_time_kernel_against_polynomial_integrals(self):
        obj = g.PathResponse.__new__(g.PathResponse)
        obj.knots = obj.time_knots = np.array([0., .25, .5, 1.])
        obj.y0 = lambda z: np.full_like(z, 2.)
        obj.ys = lambda z: 3.+z
        obj.regrid_t_on_s = lambda z: 2.+z*z
        obj.regrid_s_on_t = lambda z: 2.+2*z
        # H(z)=exp(-3z) exactly cancels the physical density dilution factor.
        # Thus K=1, so every optical integral below has an analytic polynomial value.
        obj.base = SimpleNamespace(zbirth=np.array([0., .25]), dx=1., nh=1.,
            ratio=lambda z, ray: (np.ones_like(z), np.exp(-3*z), np.ones_like(z)),
            native=SimpleNamespace(sigma_native_formula=lambda E, chi: np.ones((len(E), 4))),
            model=SimpleNamespace(chi=np.zeros(4)))
        obj.k = SimpleNamespace(C_M_S=1., D_GATE=10.)
        end = np.array([.5, .75])
        left = obj.base.zbirth
        tau, fields, partial, _ = obj.optical_fields(np.array([2., 3.]), np.array([0, 1]), end, 8)
        np.testing.assert_allclose(tau, 2*(end-left), rtol=2e-15)
        np.testing.assert_allclose(fields['standard'], end-left+(end**2-left**2)/2, rtol=3e-15)
        np.testing.assert_allclose(fields['regrid_t_on_s'], (end**3-left**3)/3, rtol=3e-15)
        np.testing.assert_allclose(fields['regrid_s_on_t'], end**2-left**2, rtol=3e-15)
        def primitive(u):
            return 16*(u**3/3-u**4/2+u**5/5)
        expected_bump = []
        for lo, hi in zip(left, end):
            answer = 0.
            for a, b in zip(obj.knots[:-1], obj.knots[1:]):
                aa, bb = max(a, lo), min(b, hi)
                if bb > aa:
                    answer += 2*(b-a)*(primitive((bb-a)/(b-a))-primitive((aa-a)/(b-a)))
            expected_bump.append(answer)
        np.testing.assert_allclose(fields['bump'], expected_bump, rtol=4e-15)
        np.testing.assert_allclose(partial.sum(axis=0), tau, rtol=3e-15)
        self.assertTrue(np.all(partial >= 0))


if __name__ == '__main__':
    unittest.main(verbosity=2)
