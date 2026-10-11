"""New local closure tests; no native provider or physical history is executed."""
import math
import unittest
import numpy as np
from scipy.integrate import quad

from reconstruction import (
    reconstruct, opacity_moments, InvalidCone, UndefinedJacobian,
    TraceRequired, QuadratureNotConverged,
)


def independent_mean(a, b, p, k=1):
    # Independent adaptive integration in log q, never imports closure helpers.
    L = math.log(b / a)
    top = quad(lambda x: (a * math.exp(x))**k * math.exp(p*x),
               0., L, epsabs=1e-11, epsrel=2e-13)[0]
    bot = quad(lambda x: math.exp(p*x), 0., L,
               epsabs=1e-11, epsrel=2e-13)[0]
    return top / bot


class ReconstructionTests(unittest.TestCase):
    def test_mean_inverse_and_p_zero_minus_one(self):
        a, b, N, R = 10., 40., 2., 0.7
        for p in [0., -1., 4., -6.]:
            m = independent_mean(a, b, p)
            cell = reconstruct(N, R*N*m, R, a, b)
            self.assertEqual(cell.status, "INTERIOR")
            self.assertAlmostEqual(cell.p, p, delta=3e-11)
            for k in [0, 1, 2]:
                self.assertAlmostEqual(cell.moment(k) / N,
                                       independent_mean(a, b, p, k),
                                       delta=2e-10)
        self.assertAlmostEqual(reconstruct(1., 30./math.log(4), 1., a, b).p,
                               0., delta=2e-13)
        self.assertAlmostEqual(reconstruct(1., a*math.log(4)/0.75, 1., a, b).p,
                               -1., delta=2e-13)

    def test_empty_endpoints_invalid_and_trace(self):
        empty = reconstruct(0., 0., 1., 10., 40.)
        self.assertEqual(empty.jacobian_status, "NO_JAC_AT_EMPTY")
        self.assertEqual(empty.moment(3), 0.)
        out = opacity_moments(empty, lambda q: q, require_jacobian=False)
        self.assertEqual(out["K0"], 0.)
        self.assertEqual(out["KE"], 0.)
        with self.assertRaises(UndefinedJacobian):
            opacity_moments(empty, lambda q: q)
        zero_width=reconstruct(0.,0.,1.,10.,10.)
        self.assertEqual(zero_width.status,"ZERO_WIDTH_EMPTY")
        self.assertEqual(zero_width.jacobian_status,"NO_JAC_AT_ZERO_WIDTH")
        self.assertEqual(opacity_moments(zero_width,lambda q: q,
                                        require_jacobian=False)["KE"],0.)
        with self.assertRaises(InvalidCone):
            reconstruct(1.,10.,1.,10.,10.)
        for U, expected, side in [(10., 10., "right"), (40., 40., "left")]:
            c = reconstruct(1., U, 1., 10., 40.)
            self.assertEqual(c.moment(1), expected)
            with self.assertRaises(TraceRequired):
                opacity_moments(c, lambda q: 99., require_jacobian=False)
            out = opacity_moments(c, lambda q: 99., require_jacobian=False,
                                  endpoint_trace=(side, 2.))
            self.assertEqual(out["K0"], 2.)
            self.assertEqual(out["KE"], 2.*expected)
        for N, U in [(0., 1.), (-1., -20.), (1., 9.), (1., 41.), (1., float("nan"))]:
            with self.assertRaises(InvalidCone):
                reconstruct(N, U, 1., 10., 40.)

    def test_constant_polynomial_and_step_common_operator(self):
        a,b,p,R,N = 10.,40.,-0.7,0.8,1.3
        m = independent_mean(a,b,p)
        cell = reconstruct(N,R*N*m,R,a,b)
        kernels = [(lambda q: 2., []), (lambda q: q*q, []),
                   (lambda q: np.where(q<22.,0.,3.), [22.])]
        for kernel, splits in kernels:
            out = opacity_moments(cell,kernel,split_points=splits,
                                  orders=(64,128),rtol=1e-7)
            L=math.log(b/a)
            Z=quad(lambda x:math.exp(p*x),0,L)[0]
            for k,key in [(0,"K0"),(1,"KE")]:
                ref=N*(R if k else 1.)*quad(
                    lambda x: float(kernel(a*math.exp(x)))*(a*math.exp(x))**k*math.exp(p*x),
                    0,L,points=[math.log(v/a) for v in splits],
                    epsabs=1e-9,epsrel=1e-12)[0]/Z
                self.assertAlmostEqual(out[key]/ref,1.,delta=2e-9)
            chi=4.
            self.assertAlmostEqual((out["KE"]-chi*out["K0"])+chi*out["K0"],
                                   out["KE"],delta=1e-9)

    def test_admissible_directional_jacobian_sweep(self):
        N,R,a,b,p=2.,0.9,10.,40.,0.3
        U=R*N*independent_mean(a,b,p)
        kernel=lambda q: 0.2+q*q/100.
        c=reconstruct(N,U,R,a,b)
        out=opacity_moments(c,kernel,orders=(64,128),rtol=1e-7)
        direction=np.array([0.13*N,-0.07*U])
        predicted=np.asarray(out["jacobian_N_U"])@direction
        errors=[]
        for h in [1e-3,3e-4,1e-4]:
            vals=[]
            for sign in [-1,1]:
                pert=np.array([N,U])+sign*h*direction
                v=opacity_moments(reconstruct(*pert,R,a,b),kernel,
                                  orders=(64,128),rtol=1e-7)
                vals.append(np.array([v["K0"],v["KE"]]))
            fd=(vals[1]-vals[0])/(2*h)
            errors.append(float(np.max(abs(fd-predicted)/np.maximum(abs(predicted),1.))))
        self.assertLess(errors[-1],2e-8)
        self.assertLess(errors[-1],errors[0])

    def test_small_number_homogeneity_and_source_entry(self):
        N,R,a,b=2.,0.5,10.,25.
        U=R*N*17.
        c=reconstruct(N,U,R,a,b)
        tiny=reconstruct(N*1e-180,U*1e-180,R,a,b)
        self.assertAlmostEqual(tiny.p,c.p,delta=1e-13)
        first=opacity_moments(c,lambda q:q,orders=(64,128),rtol=1e-7)
        second=opacity_moments(tiny,lambda q:q,orders=(64,128),rtol=1e-7)
        for key in ["K0","KE"]:
            self.assertAlmostEqual(second[key]/first[key]/1e-180,1.,delta=2e-13)
        np.testing.assert_allclose(second["jacobian_N_U"],first["jacobian_N_U"],rtol=1e-12)
        # Exact source addition from empty at the caller-supplied active cap.
        source_N,source_U=3.,R*3.*18.
        for dt in [1e-180,1e-5,1.]:
            entered=reconstruct(dt*source_N,dt*source_U,R,a,b)
            self.assertEqual(entered.status,"INTERIOR")
            self.assertAlmostEqual(entered.mean_q,18.)
        with self.assertRaises(InvalidCone):
            reconstruct(1.,R*26.,R,a,b)

    def test_large_slope_explicit_convergence_limit(self):
        # Analytic truncated-power mean; order-pair failure is explicit, not clipping.
        p=1e4
        m=40.*p/(p+1.)
        cell=reconstruct(1.,m,1.,10.,40.)
        self.assertAlmostEqual(cell.p/p,1.,delta=1e-8)
        self.assertAlmostEqual(cell.moment(1)/m,1.,delta=1e-14)
        with self.assertRaises(QuadratureNotConverged):
            opacity_moments(cell,lambda q:q*q,orders=(4,8),rtol=1e-10)

    def test_narrow_support_independent_affine_identity_or_explicit_rejection(self):
        # Identity holds for EVERY distribution with the supplied moments;
        # this oracle shares no power-law formula or quadrature implementation.
        for eps in [1e-4,1e-6,1e-8,1e-10,1e-12,1e-14]:
            a=50000.
            b=a*(1+eps)
            U=a+(b-a)/3
            cell=reconstruct(1.,U,1.,a,b)
            exact=(U-a)/(b-a)
            if eps<1e-6:
                with self.assertRaises(QuadratureNotConverged):
                    opacity_moments(cell,lambda q:(q-a)/(b-a),orders=(64,128),rtol=1e-7)
            else:
                out=opacity_moments(cell,lambda q:(q-a)/(b-a),orders=(64,128),rtol=1e-7)
                self.assertLessEqual(abs(out['K0']/exact-1),1e-7)
                self.assertIn('order_pair_component_errors',out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
