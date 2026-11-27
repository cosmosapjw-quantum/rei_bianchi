"""Independent manufactured oracles for the PHYS71 midpoint error split.

No Coulomb evaluation, inherited integral, or physical D3 panel is executed.
The oracles below use exact rational complex arithmetic and orthogonality.
"""
from contextlib import contextmanager
from fractions import Fraction as F
from itertools import product
import unittest

from flint import acb, arb, ctx

from wu088_hh.phys67_coulomb_certificate import restore_ball
from wu088_hh.phys68_profiles import polynomial_integral
from wu088_hh.phys68_taylor import inflate_complex, rational_ball
from wu088_hh.phys71_d3 import centered_angular_contraction, series


ZERO = (F(0), F(0))


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def multiply(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def convolution(a, b, degree):
    result = [ZERO for _ in range(degree+1)]
    for j, x in enumerate(a):
        for k, y in enumerate(b):
            if j+k <= degree:
                result[j+k] = add(result[j+k], multiply(x, y))
    return result


def dot_polynomials(a, b, degree):
    result = [ZERO for _ in range(degree+1)]
    for x, y in zip(a, b):
        result = [add(p, q) for p, q in zip(result, convolution(x, y, degree))]
    return result


def exact_integral(coefficients, h):
    result = ZERO
    for n, value in enumerate(coefficients):
        if n % 2 == 0:
            weight = 2*h**(n+1)/F(n+1)
            result = add(result, (weight*value[0], weight*value[1]))
    return result


def complex_exact(value):
    return acb(rational_ball(F(value[0])), rational_ball(F(value[1])))


def error_ball(radius):
    radius = rational_ball(F(radius))
    mantissa, exponent = radius.man_exp()
    return arb(0, (int(mantissa), int(exponent)))


def enclosed_series(values, degree, errors=None):
    errors = errors or {}
    coefficients = []
    for n, value in enumerate(values):
        er, ei = errors.get(n, ZERO)
        coefficients.append(complex_exact(value)+acb(error_ball(er), error_ball(ei)))
    return series(coefficients, degree)


@contextmanager
def scope(degree):
    cap = ctx.cap
    with ctx.workprec(384):
        ctx.cap = degree+1
        try:
            yield
        finally:
            ctx.cap = cap


class CenteredAngularTests(unittest.TestCase):
    def test_zero_uncertainty_keeps_nonconstant_multiplier_and_complex_signs(self):
        # One normalized mode: I_0=2V and phi_0^2=1/2.  V=1/(1-t)
        # is analytic on |t|<=1/2 with multiplier norm bounded by two.
        degree, h, rho = 4, F(1,4), F(1,2)
        aa = [(F(1), F(0)), (F(0), F(1))]
        bb = [(F(2), F(0)), (F(0), F(-1))]
        vv = [(F(1), F(0))]*(degree+1)
        oracle = convolution(convolution(aa, bb, degree), vv, degree)
        with scope(degree):
            actual, error, budget = centered_angular_contraction(
                [enclosed_series(aa, degree)], [enclosed_series(bb, degree)],
                [enclosed_series([(F(2), F(0))]*(degree+1), degree)],
                degree, h, rho, arb(2))
            self.assertTrue(error.is_zero())
            self.assertTrue(restore_ball(budget['coefficient_error_weighted_l1_a']).is_zero())
            self.assertTrue(restore_ball(budget['coefficient_error_weighted_l1_b']).is_zero())
            for n, expected in enumerate(oracle):
                self.assertTrue(actual[n].contains(complex_exact(expected)), (n, actual[n], expected))

    def test_all_complex_error_corners_enclose_independent_projected_integrals(self):
        # V=1 has V_jk=delta_jk in the original orthonormal basis.
        # Two uncertain complex coefficients yield sixteen exact corner
        # choices. Their product contributes a retained quadratic cross term.
        degree, h, rho = 3, F(1,4), F(1,2)
        aa = [[(F(3,4),F(1,8)), (F(1,2),F(-1,4)), (F(1,16),F(1,32))],
              [(F(-1,2),F(1,4)), (F(1,8),F(1,16))]]
        bb = [[(F(1,4),F(-1,2)), (F(-1,8),F(1,8))],
              [(F(-3,8),F(-1,4)), (F(1,16),F(-1,16)), (F(1,32),F(0))]]
        ra, rb = (F(1,128), F(1,256)), (F(1,64), F(1,128))
        with scope(degree):
            ua = [enclosed_series(aa[0],degree,{2:ra}), enclosed_series(aa[1],degree)]
            ub = [enclosed_series(bb[0],degree,{0:rb}), enclosed_series(bb[1],degree)]
            moments = [enclosed_series([(F(2),F(0))],degree),
                       enclosed_series([ZERO],degree),
                       enclosed_series([(F(2,3),F(0))],degree)]
            actual, error, budget = centered_angular_contraction(
                ua,ub,moments,degree,h,rho,arb(1))
            midpoint_oracle = dot_polynomials(aa,bb,degree)
            for n, expected in enumerate(midpoint_oracle):
                self.assertTrue(actual[n].contains(complex_exact(expected)))
            integral = inflate_complex(polynomial_integral(
                [actual[n] for n in range(degree+1)],-h,h),rational_ball(2*h)*error)
            self.assertTrue(error > 0)
            self.assertTrue(restore_ball(budget['projected_integrand_coefficient_error']).contains(error))
            for signs in product((-1,1), repeat=4):
                av = [list(row) for row in aa]
                bv = [list(row) for row in bb]
                av[0][2] = add(av[0][2], (signs[0]*ra[0], signs[1]*ra[1]))
                bv[0][0] = add(bv[0][0], (signs[2]*rb[0], signs[3]*rb[1]))
                oracle = dot_polynomials(av,bv,degree)
                self.assertTrue(integral.contains(complex_exact(exact_integral(oracle,h))), signs)
                # The certified weighted coefficient norm bounds the retained
                # difference even before integration, not only sampled values.
                weighted = sum((h**n*(abs(q[0]-p[0])+abs(q[1]-p[1]))
                                for n,(p,q) in enumerate(zip(midpoint_oracle,oracle))),F(0))
                self.assertTrue(error >= rational_ball(weighted), signs)

    def test_projection_cannot_be_replaced_by_untruncated_product_error(self):
        degree, h, rho, epsilon = 2, F(1,4), F(1,2), F(1,8)
        # Delta A=epsilon*t^2 and B=1-t^2/h^2. At both panel endpoints
        # their full product vanishes, while T_2(Delta A*B)=epsilon*t^2.
        aa = [ZERO,ZERO,ZERO]
        bb = [(F(1),F(0)),ZERO,(-1/h**2,F(0))]
        endpoint_a = [ZERO,ZERO,(epsilon,F(0))]
        projected = convolution(endpoint_a,bb,degree)
        full = convolution(endpoint_a,bb,4)
        projected_integral = exact_integral(projected,h)
        full_integral = exact_integral(full,h)
        self.assertEqual(projected_integral, (2*epsilon*h**3/3,F(0)))
        self.assertEqual(full_integral, (4*epsilon*h**3/15,F(0)))
        self.assertGreater(projected_integral[0],full_integral[0])
        with scope(degree):
            actual,error,_ = centered_angular_contraction(
                [enclosed_series(aa,degree,{2:(epsilon,F(0))})],
                [enclosed_series(bb,degree)],
                [enclosed_series([(F(2),F(0))],degree)],degree,h,rho,arb(1))
            integral = inflate_complex(polynomial_integral(
                [actual[n] for n in range(degree+1)],-h,h),rational_ball(2*h)*error)
            self.assertTrue(integral.contains(complex_exact(projected_integral)))
            self.assertTrue(error >= rational_ball(epsilon*h**2))

    def test_invalid_radii_and_multiplier_majorants_are_rejected(self):
        with scope(2):
            one = [enclosed_series([(F(1),F(0))],2)]
            moments = [enclosed_series([(F(2),F(0))],2)]
            for h,rho in ((F(0),F(1,2)),(F(1,2),F(1,2)),
                          (F(1),F(1,2)),(F(-1,4),F(1,2))):
                with self.subTest(h=h,rho=rho), self.assertRaises(ValueError):
                    centered_angular_contraction(one,one,moments,2,h,rho,arb(1))
            for majorant in (arb(-1),arb('nan')):
                with self.subTest(majorant=majorant), self.assertRaises(ArithmeticError):
                    centered_angular_contraction(one,one,moments,2,F(1,4),F(1,2),majorant)


if __name__ == '__main__':
    unittest.main()
