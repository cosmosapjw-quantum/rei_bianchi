#!/usr/bin/env python3
"""Physics-preserving tests for Σ and radiation/matter anisotropic stress model."""
import math
import json
from pathlib import Path
import unittest
import numpy as np

from coupled_pi import (
    COEF_M0,COEF_M2,GAMMA_M,HREF,H0,OM,OR,OL,K,RHO_CRIT,
    Moments,Solver,PhysicalScenario,AREF,XEND,
    sigma_init_from_legacy_signed_ratio,legacy_ratio_from_sigma,horner
)
HERE=Path(__file__).resolve().parent

class AnisotropicStress(unittest.TestCase):
    def test_sigma_is_tensor_norm_not_old_signed_component(self):
        for q in (0,.005,-.005,.01,-.01):
            sigma,orientation=sigma_init_from_legacy_signed_ratio(q)
            self.assertAlmostEqual(legacy_ratio_from_sigma(sigma,orientation),q,delta=2e-16)
            s=q*HREF; h=math.hypot(HREF,s)
            tensor=np.diag([-s,-s,2*s])
            sigma_from_tensor=math.sqrt(.5*np.sum(tensor*tensor))/h
            self.assertAlmostEqual(sigma,sigma_from_tensor,delta=2e-16)
            self.assertAlmostEqual(sigma/math.sqrt(3),abs(s)/h,delta=2e-16)
    def test_invalid_orientation_amplitude_and_viscosity(self):
        for args in ((.01,0),(0,1),(-.01,1),(2.,1)):
            with self.assertRaises(ValueError):legacy_ratio_from_sigma(*args)
        with self.assertRaises(ValueError):PhysicalScenario(.01,1,matter_viscosity_strength=-.0001)
        with self.assertRaises(ValueError):PhysicalScenario(.01,1,matter_viscosity_strength=1.)
    def test_orthonormal_shear_pi_sign_and_contraction(self):
        s=1.5e-17;Pr=-1e-15;Pm=-2e-15
        sig=np.diag([-s,-s,2*s])
        pressure=np.diag([-Pr-Pm,-Pr-Pm,2*(Pr+Pm)])
        self.assertAlmostEqual(float(np.einsum("ij,ij->",sig,pressure)),6*s*(Pr+Pm),delta=1e-45)
        self.assertAlmostEqual(pressure[2,2]-pressure[0,0],3*(Pr+Pm),delta=1e-25)
        self.assertEqual(float(np.trace(pressure)),0.0)
    def test_exact_radiation_m0_prime_equals_minus_2_m2(self):
        # Analytic derivative of the independently Wolfram-validated scalar Taylor14.
        # Truncation residual has order b^14, not an exact all-b symbolic identity.
        derivative_coeff=np.array([(i+2)*COEF_M0[i] for i in range(len(COEF_M0))],float)
        for b in (-.02,-.006,-.002,0.,.002,.006,.02):
            derivative=b*horner(b,derivative_coeff)
            m2=b*horner(b,COEF_M2)
            self.assertLess(abs(derivative+2*m2),3e-14)
    def test_angular_128_integral_matches_analytic14_and_FLRW(self):
        for b in (-.024,-.01,-.003,0.,.003,.01,.024):
            t=Moments("taylor14")
            g=Moments("gl128")
            E0,P0=t(b);E1,P1=g(b)
            self.assertAlmostEqual(E0,E1,delta=3e-14)
            self.assertAlmostEqual(P0,P1,delta=3e-14)
            if b==0:
                self.assertEqual(E0,1)
                self.assertEqual(P0,0)
    def test_flrw_invariant_and_matter_stress_zero_at_s_zero(self):
        for f,nu in ((0.,0.),(1.,0.),(1.,.02)):
            S=Solver(PhysicalScenario(0.,0,f,nu))
            sol,infos,wall=S.solve(n=51)
            self.assertTrue(np.array_equal(sol.y[0],np.zeros_like(sol.y[0])))
            self.assertTrue(np.array_equal(sol.y[1],np.zeros_like(sol.y[1])))
            self.assertTrue(np.array_equal(sol.y[2],np.zeros_like(sol.y[2])))
            self.assertTrue(all(x["Sigma"]==0 and x["pi_r_J_m3"]==0 and x["pi_m_J_m3"]==0 for x in infos))
    def test_stress_free_matches_exact_signed_s_a_minus_three(self):
        for q in (.005,-.01):
            sig,eps=sigma_init_from_legacy_signed_ratio(q)
            S=Solver(PhysicalScenario(sig,eps,0.,0.))
            sol,info,_=S.solve(n=251,rtol=1e-11,atol=1e-14)
            for x,point in zip(sol.t[::5],info[::5]):
                s_exact=q*HREF*math.exp(-3*x)
                self.assertAlmostEqual(point["signed_s_per_s"],s_exact,
                                       delta=5e-21)
                self.assertEqual(point["pi_m_J_m3"],0)
                self.assertEqual(point["pi_r_J_m3"],0)
    def test_both_stress_sources_and_thermal_work(self):
        sig,_=sigma_init_from_legacy_signed_ratio(.01)
        r0=Solver(PhysicalScenario(sig,1,0.,0.))
        r1=Solver(PhysicalScenario(sig,1,1.,0.))
        r2=Solver(PhysicalScenario(sig,1,1.,.02))
        a,aa,_=r0.solve(n=501)
        b,bb,_=r1.solve(n=501)
        c,cc,_=r2.solve(n=501)
        self.assertGreater(aa[-1]["Sigma"],bb[-1]["Sigma"])
        self.assertGreater(bb[-1]["Sigma"],cc[-1]["Sigma"])
        self.assertNotEqual(cc[-1]["pi_r_J_m3"],0)
        self.assertNotEqual(cc[-1]["pi_m_J_m3"],0)
        self.assertLess(cc[-1]["pi_m_J_m3"],0)
        # Positive viscous heating: u_th>0 and increasing a^5 u_th.
        self.assertGreater(c.y[2,-1],0)
        U=c.y[2,:]*(AREF*np.exp(c.t))**(3*GAMMA_M)
        self.assertTrue(np.all(np.diff(U)>=-2e-16))
        self.assertTrue(all(info["viscous_heating_source_per_x"]>=0 for info in cc))
        # Approximate entropy proxy is positive when eta>=0:
        self.assertTrue(all(-6*info["signed_s_per_s"]*info["pi_m_J_m3"]>=0 for info in cc))
    def test_unequal_axis_orientation_when_radiation_stress_coupled(self):
        sig,_=sigma_init_from_legacy_signed_ratio(.01)
        plus=Solver(PhysicalScenario(sig,1,1.,0.)).solve(n=101)[0]
        minus=Solver(PhysicalScenario(sig,-1,1.,0.)).solve(n=101)[0]
        self.assertGreater(plus.y[0,-1]+minus.y[0,-1],1e-8)
        self.assertLess(abs(plus.y[0,-1]+minus.y[0,-1]),1e-6)
        p0=Solver(PhysicalScenario(sig,1,0.,0.)).solve(n=101)[0]
        m0=Solver(PhysicalScenario(sig,-1,0.,0.)).solve(n=101)[0]
        self.assertAlmostEqual(p0.y[0,-1]+m0.y[0,-1],0.,delta=2e-14)
    def test_matched_error_GL128_vs_Taylor14_evolved_solution(self):
        sig,_=sigma_init_from_legacy_signed_ratio(.01)
        phys=PhysicalScenario(sig,1,1.,.02)
        t=Solver(phys,"taylor14").solve(n=181,rtol=1e-11,atol=1e-14)[0]
        g=Solver(phys,"gl128").solve(n=181,rtol=1e-11,atol=1e-14)[0]
        self.assertTrue(np.array_equal(t.t,g.t))
        self.assertLess(float(np.max(abs(t.y[0]-g.y[0]))),2e-11)
        self.assertLess(float(np.max(abs(t.y[1]-g.y[1]))),2e-11)
        self.assertLess(float(np.max(abs(t.y[2]-g.y[2]))),2e-11)
        self.assertLess(float(np.max(abs(t.y[3]-g.y[3]))),2e-10)
    def test_time_refinement_in_coupled_new_physics(self):
        sig,_=sigma_init_from_legacy_signed_ratio(.01)
        ph=PhysicalScenario(sig,1,1.,.02)
        coarse=Solver(ph).solve(n=121,rtol=1e-8,atol=1e-10)[0]
        fine=Solver(ph).solve(n=121,rtol=5e-12,atol=3e-14)[0]
        self.assertTrue(np.array_equal(coarse.t,fine.t))
        self.assertLess(float(np.max(abs(coarse.y[0]-fine.y[0]))),2e-8)
        self.assertLess(float(np.max(abs(coarse.y[1]-fine.y[1]))),2e-8)
        self.assertLess(float(np.max(abs(coarse.y[2]-fine.y[2]))),2e-8)
        self.assertLess(float(np.max(abs(coarse.y[3]-fine.y[3]))),2e-8)

if __name__=="__main__":unittest.main(verbosity=2)
