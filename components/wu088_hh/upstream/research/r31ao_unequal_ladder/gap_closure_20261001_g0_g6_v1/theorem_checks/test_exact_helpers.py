"""Synthetic exact algebra checks; does not import producer modules or inputs."""
from fractions import Fraction as Q
from math import factorial
import unittest
from exact_helpers import (Poly, rising, radial_shift, even_radial_coefficients,
    hermite_envelope_terms, sqrt_upper_rational, rectangle_disk_radius,
    complement_bound, exact_tau, supported_by_lower_gaps)


class TheoremChecks(unittest.TestCase):
    def test_even_radial_closed_polynomials(self):
        expected = {0: (1,), 2: (3, 1), 4: (15, 10, 1),
                    6: (105, 105, 21, 1), 8: (945, 1260, 378, 36, 1)}
        for k, coeffs in expected.items():
            self.assertEqual(even_radial_coefficients(k), coeffs)

    def test_even_radial_independent_gaussian_moments(self):
        # X has mean 2 and variance 3; Y,Z have zero mean and variance 3.
        # E[(X^2+Y^2+Z^2)^n] is evaluated by elementary Gaussian moments.
        def normal_moment(m, mean):
            total = Q(0)
            for j in range(m//2+1):
                even = Q(factorial(2*j), 2**j * factorial(j)) * 3**j
                total += Q(factorial(m), factorial(2*j)*factorial(m-2*j))*mean**(m-2*j)*even
            return total
        for n in range(5):
            direct = Q(0)
            for x in range(n+1):
                for y in range(n-x+1):
                    z = n-x-y
                    direct += Q(factorial(n), factorial(x)*factorial(y)*factorial(z)) * normal_moment(2*x, 2) * normal_moment(2*y, 0) * normal_moment(2*z, 0)
            expression = sum(c*3**(n-j)*4**j for j, c in enumerate(even_radial_coefficients(2*n)))
            self.assertEqual(direct, expression)

    def test_radial_hypergeometric_coefficient_derivatives(self):
        # Formal power-series coefficient equality at 2*sigma=1; Gamma prefactor cancels.
        for k in range(9):
            a, b = -Q(k, 2), Q(3, 2)
            for r in range(3):
                ar, br, factor = radial_shift(k, r)
                for n in range(13):
                    direct = (-1)**(n+r)*rising(a, n+r)/rising(b, n+r)/factorial(n)
                    shifted = factor*(-1)**n*rising(ar, n)/rising(br, n)/factorial(n)
                    self.assertEqual(direct, shifted)

    def test_zero_derivative_shortcuts(self):
        self.assertEqual(radial_shift(0, 1)[2], 0)
        self.assertEqual(radial_shift(0, 2)[2], 0)
        self.assertEqual(radial_shift(2, 2)[2], 0)

    def test_field_center_derivatives_as_polynomial_identities(self):
        # Variables: d1z,d2z,c1,c2,h1,h2,n1x,delta_x,1/A.
        # c_j denotes i*q_j/(2*A_j); treating it as formal retains complex validity.
        z1,z2,c1,c2,h1,h2,nx,dx,ainv = [Poly.variable(i, 9) for i in range(9)]
        dz = h1*z1+c1-h2*z2-c2
        nz = (h1-1)*z1+c1
        s = dx*dx+dz*dz
        sp1,sp2 = 2*dz*h1,-2*dz*h2
        for degree in range(5):
            M = s**degree
            Mp = degree*s**(degree-1) if degree else s*0
            Mpp = degree*(degree-1)*s**(degree-2) if degree > 1 else s*0
            self.assertEqual(M.diff(0), Mp*sp1)
            self.assertEqual(M.diff(1), Mp*sp2)
            for n, delta, kronecker in ((nx,dx,0),(nz,dz,1)):
                F = n*M+delta*ainv*Mp
                first = (h1-1)*kronecker*M+n*Mp*sp1+h1*ainv*kronecker*Mp+delta*ainv*Mpp*sp1
                second = n*Mp*sp2-h2*ainv*kronecker*Mp+delta*ainv*Mpp*sp2
                self.assertEqual(F.diff(0), first)
                self.assertEqual(F.diff(1), second)

    def test_hermite_positive_coefficients_and_endpoint_integrability(self):
        for i in range(9):
            for Arootpi, nu in hermite_envelope_terms(i, Q(7, 3)):
                self.assertGreater(Arootpi, 0)
                self.assertGreater(nu, 1)
                self.assertGreaterEqual(nu+Q(1,2), 2)

    def test_upper_gamma_lower_endpoint_orientation(self):
        # nu=m+1 and Gamma(m,x)=(m-1)!exp(-x) sum_j x^j/j!.
        # Differentiate the lower-tail expression by ell (x=1/ell).
        x = Poly.variable(0, 1)
        lam = Q(2,3)
        for m in range(1,7):
            P = Poly.constant(0,1)
            for j in range(m):
                P += (lam*x)**j * (Q(factorial(m-1), factorial(j))/lam**m)
            derivative_without_exp = -x*x*(P.diff(0)-lam*P)
            self.assertEqual(derivative_without_exp, x**(m+1))

    def test_rectangular_disk_conversion_corner(self):
        self.assertEqual(rectangle_disk_radius(3,4), 5)
        bound = rectangle_disk_radius(1,1,80)
        self.assertGreaterEqual(bound*bound, 2)
        self.assertLess((bound-Q(1,2**80))**2, 2)
        self.assertGreater(bound, 1)  # max(rx,ry) is not a disk radius.

    def test_integer_sqrt_upper_and_rejection(self):
        for x in (Q(0), Q(1), Q(2), Q(7,13), Q(10**20,7)):
            q = sqrt_upper_rational(x, 60)
            self.assertGreaterEqual(q*q, x)
            if q:
                self.assertLess((q-Q(1,2**60))**2, x)
        for x in (-1, Q(-1,3)):
            with self.assertRaises(ValueError):
                sqrt_upper_rational(x)

    def test_complement_counts_corners_once(self):
        Et,It,Eu,Iu = Q(2),Q(3),Q(5),Q(7)
        self.assertEqual(complement_bound(1,Et,Eu+Iu,It,Eu), (Et+It)*(Eu+Iu)-It*Iu)
        self.assertNotEqual(Et*(Eu+Iu)+(Et+It)*Eu, complement_bound(1,Et,Eu+Iu,It,Eu))

    def test_exact_tau_no_host_rounding(self):
        self.assertEqual(exact_tau(Q(3,4),Q(7,16)),Q(12,7))
        self.assertEqual(exact_tau(Q(3,4),Q(-7,16)),Q(-12,7))
        with self.assertRaises(ValueError):
            exact_tau(1,0)

    def test_strict_pareto_boundary(self):
        tol = Q(1,100)
        self.assertFalse(supported_by_lower_gaps((tol,tol),tol))
        self.assertTrue(supported_by_lower_gaps((-tol,tol+Q(1,100000)),tol))
        self.assertFalse(supported_by_lower_gaps((-tol-Q(1,100000),1),tol))
        self.assertTrue(supported_by_lower_gaps((tol+1,tol),tol))

    def test_nested_midpoint_not_uniform_counterexample(self):
        # f(t,u)=t on [0,1] in u; outer t box [0,2]. Inner at t=1 is 1,
        # but whole image is [0,2]. No HH parameters are used.
        midpoint_value, actual_at_endpoint = Q(1),Q(2)
        self.assertNotEqual(midpoint_value,actual_at_endpoint)

    def test_absent_gamma_subtraction_identity(self):
        # W,S are independent upper bounds; W-S can be below true interior.
        actual_interior, whole_upper, endpoint_upper = Q(9),Q(12),Q(10)
        self.assertLess(whole_upper-endpoint_upper,actual_interior)

    def test_input_contract_refusals(self):
        for args in ((-1,0),(9,0),(0,3),(1.0,0)):
            with self.assertRaises(ValueError):
                radial_shift(*args)
        with self.assertRaises(ValueError):
            hermite_envelope_terms(0,0)
        with self.assertRaises(ValueError):
            rectangle_disk_radius(-1,0)
        with self.assertRaises(ValueError):
            complement_bound(1,-1,1,1,1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
