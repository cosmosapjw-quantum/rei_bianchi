"""Independent algebra discriminants for the new D3 panel core.

No original HH panel, old Volterra integral or completed trajectory runs here.
The angular oracle is a direct full matrix contraction, independently of the
new polar polynomial contraction.  The slab oracle uses exact Fractions.
"""
from dataclasses import replace
from fractions import Fraction as F
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from flint import acb, arb, ctx

from wu088_hh.phys68_angular import angular_taylor_coefficients
from wu088_hh.phys68_profiles import norm_radius_l1, polynomial_integral
from wu088_hh.phys68_taylor import rational_ball
from wu088_hh.phys71_d3 import (
    D3Request, angular_contraction, build_d3_panel, forward_primitive,
    monomial_moments, series,
)


class ThirdBornCoreDiscriminants(unittest.TestCase):
    def setUp(self):
        self.old_prec, self.old_cap = ctx.prec, ctx.cap
        ctx.prec = 384
        ctx.cap = 41

    def tearDown(self):
        ctx.prec, ctx.cap = self.old_prec, self.old_cap

    def assert_same_coefficients(self, actual, reference, degree):
        for n in range(degree+1):
            with self.subTest(coefficient=n):
                self.assertTrue(actual[n].is_finite())
                self.assertTrue(reference[n].is_finite())
                self.assertTrue((actual[n]-reference[n]).contains(0))
                # Prevent vacuous agreement through an unresolved wide ball.
                self.assertLess(norm_radius_l1(actual[n]), F(1, 10**50))
                self.assertLess(norm_radius_l1(reference[n]), F(1, 10**50))

    def test_full_complex_angular_contraction_against_ordered_matrix(self):
        degree, center = 8, F(109, 4)
        ctx.cap = degree+1
        ua = [series([acb(1, 2), acb(rational_ball(F(1, 3)))], degree),
              series([acb(-2, 1), acb(0, -1)], degree),
              series([acb(0, 3), acb(-1, 2), acb(1)], degree),
              series([acb(2, -1), acb(rational_ball(F(2, 7)), 1)], degree)]
        ub = [series([acb(-1, 1), acb(2)], degree),
              series([acb(3, 2), acb(0, 1)], degree),
              series([acb(1, -2), acb(-2)], degree),
              series([acb(0, 1), acb(1, 1)], degree)]
        moments = monomial_moments(center, degree, 6)
        actual = angular_contraction(ua, ub, moments, degree)
        reference = series([acb(0)], degree)
        for j in range(4):
            for k in range(4):
                vjk = series(angular_taylor_coefficients(j, k, center, degree, 384, 1024), degree)
                reference += ua[j]*vjk*ub[k]
        self.assert_same_coefficients(actual, reference, degree)

    def check_high_basis_pair(self, a, b):
        degree, center = 8, F(109, 4)
        ctx.cap = degree+1
        length = max(a, b)+1
        ua = [series([acb(0)], degree) for _ in range(length)]
        ub = [series([acb(0)], degree) for _ in range(length)]
        # Conjugating the second vector reverses the exact sign in this test.
        ua[a], ub[b] = series([acb(0, 2)], degree), series([acb(0, 3)], degree)
        moments = monomial_moments(center, degree, 2*length-2)
        actual = angular_contraction(ua, ub, moments, degree)
        reference = series(angular_taylor_coefficients(a, b, center, degree, 384, 1024), degree)*(-6)
        self.assert_same_coefficients(actual, reference, degree)
        self.assertFalse(actual[0].contains(0))
        self.assertFalse((actual[0]+reference[0]).contains(0))

    def test_external_21_20_basis_normalization(self):
        self.check_high_basis_pair(21, 20)

    def test_high_36_35_basis_normalization(self):
        self.check_high_basis_pair(36, 35)

    def test_forward_primitive_constant_with_nonzero_complex_carry(self):
        degree, h, rho = 40, F(1, 4), F(1, 2)
        constant, left = acb(2, 3), acb(-1, 4)
        coefficients = (constant,) + (acb(0),)*degree
        pc, right, majorant, remainder = forward_primitive(
            coefficients, constant.abs_upper(), left, h, rho, degree)
        self.assertTrue((pc[0]-(left+constant*rational_ball(h))).contains(0))
        self.assertTrue((right-(left+constant*rational_ball(2*h))).contains(0))
        self.assertTrue((pc[1]-constant).contains(0))
        self.assertTrue(all(c.contains(0) for c in pc[2:]))
        self.assertGreater(majorant, left.abs_lower())
        self.assertGreater(remainder, 0)
        self.assertLess(norm_radius_l1(right), F(1, 10**9))

    def test_forward_primitive_polynomial_preserves_left_to_right_orientation(self):
        degree, h, rho = 40, F(1, 4), F(1, 2)
        left = acb(1, -2)
        coeffs = [acb(2, 1), acb(-3, 2), acb(1, -1)] + [acb(0)]*(degree-2)
        ms = sum((c.abs_upper()*rational_ball(rho**n) for n, c in enumerate(coeffs)), arb(0)).upper()
        pc, right, _, _ = forward_primitive(tuple(coeffs), ms, left, h, rho, degree)
        expected_center = left + acb(rational_ball(F(115, 192)), rational_ball(F(35, 192)))
        expected_right = left + acb(rational_ball(F(97, 96)), rational_ball(F(47, 96)))
        # These exact fractions were obtained by integrating each monomial,
        # independently of polynomial_integral and the producer helper.
        self.assertTrue((pc[0]-expected_center).contains(0))
        self.assertTrue((right-expected_right).contains(0))
        for n in range(1, 4):
            self.assertTrue((pc[n]-coeffs[n-1]/n).contains(0))
        self.assertLess(norm_radius_l1(right), F(1, 10**9))

    def test_imaginary_scalar_slab_cubic_coefficient(self):
        degree, length = 20, F(3, 2)
        h, rho = length/2, F(2)
        ctx.cap = degree+1
        kappa = acb(0, 1)
        # q(c+x)=kappa*(L/2-x), f=1, P(0)=0.
        s = (kappa*rational_ball(h), -kappa) + (acb(0),)*(degree-1)
        pc, right, _, _ = forward_primitive(s, rational_ball(h+rho), acb(0), h, rho, degree)
        self.assertTrue((right-kappa*rational_ball(length**2/2)).contains(0))
        pp = series(pc, degree)
        integrand = kappa*pp*pp
        actual = polynomial_integral(tuple(integrand[n] for n in range(degree+1)), -h, h)
        # int_0^L (L*x-x²/2)² dx = 2L⁵/15, and i³=-i.
        exact = acb(0, -rational_ball(2*length**5/15))
        self.assertTrue((actual-exact).contains(0))
        self.assertTrue(actual.imag < 0)
        self.assertFalse((actual+exact).contains(0))
        self.assertFalse((actual-6*exact).contains(0))
        self.assertLess(norm_radius_l1(actual), F(1, 10**6))

    def test_fixed_request_rejects_type_coercion_and_changed_physics(self):
        self.assertEqual(D3Request().validate(), D3Request())
        changes = [{"m":False}, {"degree":80.0}, {"max_ell":36.0},
                   {"boundary":27}, {"outer":"66"}, {"ell":20},
                   {"HH_R10":"ON"}, {"absolute_goal":"1e-76"}]
        for change in changes:
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    replace(D3Request(), **change).validate()

    def test_core_restores_process_context_after_coulomb_failure(self):
        inherited = SimpleNamespace(index=75, center=F(109, 4), left=F(27),
                                    right=F(55, 2), pairs={})
        carry = {(a,j):acb(0) for a in (20,21) for j in range(37)}
        ctx.cap, ctx.prec = 17, 160
        with patch("wu088_hh.phys71_d3.coulomb_taylor", side_effect=ArithmeticError("injected disk failure")) as callback:
            with self.assertRaisesRegex(ArithmeticError, "injected disk failure"):
                build_d3_panel(inherited, carry)
        self.assertEqual(callback.call_count, 1)
        self.assertEqual((ctx.cap, ctx.prec), (17, 160))


if __name__ == "__main__":
    unittest.main()
