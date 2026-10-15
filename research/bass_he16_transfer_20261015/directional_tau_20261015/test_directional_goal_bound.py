import math
import sys
import unittest
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from signed_prefix_tau import taucum
from directional_tau import tau_between_source_and_observer
from directional_goal_bound import (
    KAPPA, QUAD_L1, F_HE, maxima_chunked, maxima_vectorized,
    per_case_bounds, directional_redshift_domain_margin,
)


class DirectionalGoalBoundTests(unittest.TestCase):
    @staticmethod
    def data(N=2001):
        u=np.linspace(0.,1.,N)
        a=np.exp(u)
        t=1000*u
        ne=.001+.0004*u
        b=.02*u
        tau,_=taucum(t,ne)
        source={"a":a,"t_s":t,"ne_cm3":ne,"tau":tau}
        return source,b,u

    @staticmethod
    def a2(source,b,z=.5):
        mu,w=leggauss(96)
        tau,details=tau_between_source_and_observer(source,b,z,mu)
        return np.longdouble(5)/2*np.dot(w.astype(np.longdouble),
                                            tau.astype(np.longdouble)*(3*mu**2-1).astype(np.longdouble)/2)

    def test_chunked_vs_vectorized(self):
        d,b,_=self.data(2001)
        refL,refM=maxima_vectorized(d["a"],d["t_s"],d["ne_cm3"],b)
        for chunk in (2,3,7,64,128,2001):
            L,M,m=maxima_chunked(d["a"],d["t_s"],d["ne_cm3"],b,chunk)
            self.assertLess(abs(float((L-refL)/refL)),2e-12)
            self.assertLess(abs(float((M-refM)/refM)),2e-12)
            self.assertLess(abs(float(m-(1-2*M))),2e-15)

    def test_manufactured_pointwise_constant_derivative(self):
        d,b,u=self.data()
        L,M,m=maxima_chunked(d["a"],d["t_s"],d["ne_cm3"],b,256)
        ref=KAPPA*np.longdouble(1000)*np.longdouble(.0014)
        self.assertLess(float(abs(L-ref)/ref),1e-11)
        self.assertAlmostEqual(float(M),.02,places=11)
        self.assertAlmostEqual(float(m),.96,places=11)

    def test_geometry_perturbation_respects_bound(self):
        source,b,u=self.data(4001)
        eps=1e-4
        alt=b+eps*np.sin(2*np.pi*u)
        a2_original=self.a2(source,b)
        a2_perturbed=self.a2(source,alt)
        c=per_case_bounds(source["a"],source["t_s"],source["ne_cm3"],b)
        cap=QUAD_L1*np.longdouble(c["geometry_bound_coefficient_per_sup_abs_b_error"])*eps
        self.assertLess(abs(a2_perturbed-a2_original),cap)
        self.assertGreater(cap,0)

    def test_species_perturbation_respects_bound(self):
        src,b,u=self.data(2001)
        nH0=.002
        nH=nH0*(src["a"][0]/src["a"])**3
        # Fixed time and b, all three ionized fractions are changed by eps.
        eps=2e-5
        ne_extra=nH*(1+3*float(F_HE))*eps
        ne_new=src["ne_cm3"]+ne_extra
        tau,_=taucum(src["t_s"],ne_new)
        alt={**src,"ne_cm3":ne_new,"tau":tau}
        delta=abs(self.a2(alt,b)-self.a2(src,b))
        I=KAPPA*np.sum(np.diff(src["t_s"]).astype(np.longdouble)*
                       (nH[:-1].astype(np.longdouble)+nH[1:].astype(np.longdouble))/2)
        cap=QUAD_L1*I*(1+F_HE*3)*eps
        self.assertLess(delta,cap)

    def test_redshift_domain_margin_is_positive(self):
        src,b,u=self.data()
        self.assertGreater(float(directional_redshift_domain_margin(src["a"],b,.5)),.45)
        self.assertLess(float(directional_redshift_domain_margin(src["a"],b,5.)),0)

    def test_degenerate_source_or_geometry_rejected(self):
        src,b,u=self.data()
        bad_b=np.array(b)
        bad_b[4]=float("nan")
        with self.assertRaises(ValueError):
            maxima_chunked(src["a"],src["t_s"],src["ne_cm3"],bad_b)
        with self.assertRaisesRegex(ValueError,"margin"):
            maxima_chunked(src["a"],src["t_s"],src["ne_cm3"],.7*u)

    def test_exact_legendre_L1_identity(self):
        a=1/math.sqrt(3)
        half_negative_integral=(a-a*a*a)/2
        half_positive_integral=-(a*a*a-a)/2
        direct=(5/2)*2*(half_negative_integral+half_positive_integral)
        self.assertAlmostEqual(float(QUAD_L1),direct,places=14)
        self.assertAlmostEqual(float(QUAD_L1),10/(3*math.sqrt(3)),places=14)


if __name__=="__main__":
    unittest.main()
