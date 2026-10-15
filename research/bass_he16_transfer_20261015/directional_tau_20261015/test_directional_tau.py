import math
import unittest

import numpy as np

from directional_tau import (
    KAPPA, PREC, _log_z_relative, solve_directional_redshift,
    tau_between_source_and_observer, directional_moments
)


class TestDirectionalTau(unittest.TestCase):
    @staticmethod
    def manufactured(s=0., n=2049, h=.1):
        t = np.linspace(0.,10.,n)
        u = h*t
        a = np.exp(u)
        b = s*u
        ne = np.full_like(t,.002)
        tau = KAPPA * PREC(".002") * t.astype(PREC)
        source = {"a": a, "t_s": t, "ne_cm3": ne, "tau": tau}
        return source, b, h

    def test_isotropic_direction_independence_and_analytic_tau(self):
        source,b,H=self.manufactured()
        mu=np.linspace(-1,1,67)
        result,info=tau_between_source_and_observer(source,b,.5,mu)
        expect=KAPPA * PREC(".002") * PREC(math.log1p(.5)/H)
        self.assertLess(float(np.max(np.abs(result-expect))/expect),2e-12)
        self.assertTrue(info["strict_directional_monotonicity_interpolant"])

    def test_axial_transverse_exact_powerlaw(self):
        for s in (-.02,.007,.021):
            source,b,H=self.manufactured(s=s)
            tau,info=tau_between_source_and_observer(source,b,.5,np.array([0.,1.]))
            base=KAPPA*PREC(".002")*PREC(math.log1p(.5)/H)
            self.assertLess(float(abs(tau[0]/base - PREC(1)/(1-PREC(s)))),4e-12)
            self.assertLess(float(abs(tau[1]/base - PREC(1)/(1+2*PREC(s)))),4e-12)

    def test_reflection_even_in_direction(self):
        source,b,_=self.manufactured(s=.013)
        mu=np.array([-.9,-.3,0.,.3,.9])
        tau,_=tau_between_source_and_observer(source,b,.2,mu)
        self.assertLess(float(np.max(abs(tau-tau[::-1]))),1e-23)

    def test_redshift_root_residual_and_zero_endpoint(self):
        source,b,_=self.manufactured(s=.01)
        mu=np.linspace(-.95,.95,13)
        result,info=solve_directional_redshift(np.log(source["a"]),b,mu,.4)
        self.assertLess(info["max_abs_log_redshift_residual"],3e-15)
        self.assertLess(float(np.max(abs(_log_z_relative(result,mu,np.log(source["a"]),b)-math.log1p(.4)))),3e-15)
        zero,_=tau_between_source_and_observer(source,b,0.,mu)
        self.assertLess(float(np.max(abs(zero))),1e-18)

    def test_monotonicity_gate(self):
        u=np.linspace(0.,1.,19)
        with self.assertRaisesRegex(ValueError,"monotonicity"):
            solve_directional_redshift(u,.6*u,np.array([0.,1.]),.2)

    def test_target_not_contained(self):
        source,b,_=self.manufactured(s=.01)
        with self.assertRaisesRegex(ValueError,"outside history"):
            tau_between_source_and_observer(source,b,4.,np.array([0.,1.]))

    def test_quadrupole_first_order(self):
        source,b,H=self.manufactured(s=1e-4)
        data=directional_moments(source,b,z_targets=(.3,),angular_orders=(24,48,96))
        mono=PREC(data[0]["selected"]["tau_sky_monopole"])
        a2=PREC(data[0]["selected"]["tau_legendre_a2"])
        baseline=KAPPA*PREC(".002")*PREC(math.log1p(.3)/H)
        # tau(mu)=baseline*(1+s-3s*mu^2)+O(s^2) = baseline*(1-2s P2)+...
        expected=-PREC("0.0002")*baseline
        self.assertLess(float(abs(a2-expected)/abs(expected)),.0008)
        self.assertLess(float(abs(mono-baseline)/baseline),5e-7)
        self.assertLess(float(abs(PREC(data[0]["angular_convergence"][-1]["tau_legendre_a2"])-
                                  PREC(data[0]["angular_convergence"][-2]["tau_legendre_a2"]))),1e-20)


if __name__=="__main__":
    unittest.main()
