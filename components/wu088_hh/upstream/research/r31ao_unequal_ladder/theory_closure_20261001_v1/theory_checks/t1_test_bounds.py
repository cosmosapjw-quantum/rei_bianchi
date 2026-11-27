"""Exact synthetic checks supporting, and never replacing, the T1 proof."""
from fractions import Fraction as Q
import unittest
from t1_bounds import (inverse, shifted_bounds, sigma_bounds, density_geometry,
                       source_geometry, dyadic_radius)


def grid(lo, hi):
    return [lo, (3*lo+hi)/4, (lo+hi)/2, (lo+3*hi)/4, hi]


class T1ExactChecks(unittest.TestCase):
    def test_inverse_margins_on_synthetic_rectangles(self):
        for a, box in [(Q(2), (Q(-1), Q(3), Q(-7), Q(4))),
                       (Q(1, 3), (Q(1, 8), Q(9), Q(1), Q(5)))]:
            bounds = shifted_bounds(a, box)
            for x in grid(box[0], box[1]):
                for y in grid(box[2], box[3]):
                    real, imag = inverse((a+x, y))
                    self.assertGreaterEqual(real, bounds['inverse_real_lower'])
                    self.assertLessEqual(real*real+imag*imag, bounds['inverse_modulus_upper']**2)
                    self.assertGreaterEqual(real*real+imag*imag, 1/bounds['q'])

    def test_sigma_bounds_and_safe_set_intersection(self):
        a, b = Q(2), Q(3)
        t = (Q(-1), Q(2), Q(1), Q(4))
        u = (Q(-2), Q(1), Q(-5), Q(-1))
        lower, upper = sigma_bounds(a, t, b, u)
        self.assertGreater(lower, 0)
        # A deliberately poor raw real interval crosses zero.
        raw_real = (-2*upper, 2*upper)
        refined_real = (max(raw_real[0], lower), min(raw_real[1], upper))
        self.assertGreater(refined_real[0], 0)
        for x in grid(t[0], t[1]):
            for y in grid(t[2], t[3]):
                for v in grid(u[0], u[1]):
                    ar, ai = inverse((a+x, y))
                    br, bi = inverse((b+v, u[2]))
                    sr, si = (ar+br)/2, (ai+bi)/2
                    self.assertLessEqual(refined_real[0], sr)
                    self.assertLessEqual(sr, refined_real[1])
                    self.assertLessEqual(sr*sr+si*si, upper*upper)
                    ir, ii = inverse((sr, si))
                    self.assertGreaterEqual(ir, lower/(upper*upper))

    def test_shifted_domain_does_not_imply_density_domain(self):
        for point in (Q(0), Q(-1, 2)):
            box = (point, point, Q(0), Q(0))
            self.assertGreater(shifted_bounds(Q(1), box)['alpha'], 0)
            with self.assertRaises(ValueError):
                density_geometry(box)
        box = (Q(-1, 2), Q(1), Q(1, 4), Q(1, 2))
        d = density_geometry(box)
        self.assertEqual(d['tau_squared'], Q(1, 16))
        self.assertEqual(d['exponential_growth_per_lambda'], Q(8))

    def test_general_center_and_attenuation_constants(self):
        a, D = Q(3), Q(5)
        box = (Q(-2), Q(7), Q(1), Q(3))
        geom = source_geometry(a, box, D)
        for x in grid(box[0], box[1]):
            self.assertLessEqual(a/(a+x), geom['mean_factor'])
            self.assertLessEqual(abs(x/(a+x)), geom['displacement_factor'])
            self.assertLessEqual(-a*x*D*D/(a+x), geom['attenuation_log_upper'])
        positive = source_geometry(a, (Q(1), Q(4), Q(-2), Q(3)), D)
        self.assertEqual(positive['attenuation_log_upper'], 0)

    def test_real_completion_and_young_identity(self):
        for a, x, d, r in [(Q(3), Q(-2), Q(5, 2), Q(-7, 3)),
                            (Q(1, 2), Q(2), Q(-3), Q(4))]:
            A = a+x
            original = -a*(r-d)**2-x*r*r
            completed = -A*(r-a*d/A)**2-a*x*d*d/A
            self.assertEqual(original, completed)
            alpha, D = A, abs(d)
            young_gap = alpha*r*r/2+2*a*a*D*D/alpha-2*a*D*abs(r)
            self.assertEqual(young_gap, (alpha*abs(r)-2*a*D)**2/(2*alpha))
            self.assertGreaterEqual(young_gap, 0)
            self.assertLessEqual(original, -alpha*r*r/2+2*a*a*D*D/alpha)

    def test_completed_phase_is_not_separately_unit_modulus(self):
        inverse_real, inverse_imag = inverse((Q(1), Q(1)))
        # Re(i/A) = -Im(1/A) = 1/2, so |exp(i/A)| = exp(1/2) > 1.
        self.assertEqual(-inverse_imag, Q(1, 2))
        self.assertGreater(-inverse_imag, 0)

    def test_no_global_density_bound_near_zero(self):
        for n in (1, 2, 4, 8, 16, 64):
            t = (Q(1, n*n), Q(1, n))
            real_inverse, _ = inverse(t)
            norm_squared = t[0]*t[0]+t[1]*t[1]
            self.assertEqual(real_inverse, Q(n*n, n*n+1))
            self.assertLessEqual(real_inverse, 1)
            # |t|^-6 >= n^6/8, while exp(-lambda*Re(1/t)) >= exp(-lambda).
            self.assertGreaterEqual(1/norm_squared**3, Q(n**6, 8))

    def test_dyadic_extensions_have_strict_margin(self):
        for left in (Q(1, 1000), Q(3, 7), Q(5), Q(19, 2)):
            delta = dyadic_radius(left)
            self.assertGreater(delta, 0)
            self.assertLessEqual(delta, left/4)
            self.assertGreater(left-delta, 0)
            self.assertEqual(delta.denominator & (delta.denominator-1), 0)
        with self.assertRaises(ValueError):
            dyadic_radius(Q(0))
        with self.assertRaises(TypeError):
            dyadic_radius(0.5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
