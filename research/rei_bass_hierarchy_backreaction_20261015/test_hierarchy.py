#!/usr/bin/env python3
"""Source-bound BASS Einstein-Vlasov and REI HHe Thomson hierarchy regression."""
from pathlib import Path
import json
import math
import sys
import unittest
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE/"suppliers/bass/rei_axbi_initial_stress_20261015"))
from einstein_vlasov import KineticStressBackground,Initial
from lrs_boltzmann import (HierarchyBackground,SourceLock,ElectronHistory,
        legendre_matrix,thomson_coeffs,GAMMA_PER_NE)
from run_hierarchy import source_lock,actual_electrons,public_sigma_from_q
from receiver_coupled import real_C11,Receiver,DURATION

class BASSPositiveHierarchyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=source_lock()
        cls.owner=Path.home()/"Dropbox/bianchi/rei_bianchi"
        cls.ne,cls.receipt=actual_electrons(cls.owner)
    def test_source_sha_and_legacy_full_electron_donor(self):
        self.assertEqual(self.receipt["original_rows"],312238)
        self.assertEqual(len(self.ne.x),8193)
        self.assertTrue(np.all(self.ne.density(np.exp(self.ne.x))>0))
        # Actual source is not smooth; report, do not misrepresent this C2
        # reconstruction error as hierarchy truncation error.
        self.assertLess(self.ne.max_relative_source_error,3e-4)
        with self.assertRaises(ValueError):
            self.ne.density(self.source.aend*1.01)
    def test_bass_pstf_shear_energy_number_monopole(self):
        for L in (2,4,8,12,16):
            A=legendre_matrix(L,power=4)
            N=legendre_matrix(L,power=3)
            exact=np.zeros(L+1);exact[2]=-2
            self.assertLess(float(np.max(abs(A[0]-exact))),2e-12)
            self.assertLess(float(np.max(abs(N[0]))),2e-12)
            # Bianchi I angle transport couples ell only by Δell=0,±2.
            mask=np.array([[abs(i-j) not in (0,2) for j in range(L+1)] for i in range(L+1)])
            self.assertLess(float(np.max(abs(A[mask]))),2e-11)
            self.assertLess(float(np.max(abs(N[mask]))),2e-11)
    def test_thomson_unpolarized_source_0_9_quadrupole(self):
        c=thomson_coeffs(8)
        self.assertEqual(c[0],0)
        self.assertEqual(c[1],1)
        self.assertEqual(c[2],.9)
        self.assertTrue(np.array_equal(c[3:],np.ones(6)))
        bg=HierarchyBackground(self.source,8,1.,.2,0.,0)
        y=bg.initial_state()
        q=bg.diagnostic(0.,y)
        gamma=1e-18
        j=y[4:13]
        # Source stress zero s=0 initially, Thomson quadrupole rate = -.9 Gamma J2.
        C=-gamma*c*j
        self.assertEqual(C[0],0)
        self.assertAlmostEqual(C[2],-.9*gamma*(.2/5),delta=1e-32)
    def test_exact_BASS_PR159_initial_sigma_0_quadrupole_and_positive(self):
        for q,kappa in ((0.,.2),(0.,-.2),(.005,.2),(-.005,.2)):
            sig,e=public_sigma_from_q(q)
            bg=HierarchyBackground(self.source,8,1.,kappa,sig,e)
            solution,_=bg.integrate(n=141)
            ref=KineticStressBackground(Initial(q,kappa))
            actual=bg.diagnostic(solution.t[-1],solution.y[:,-1])
            expected=ref.at_a(self.source.aend)
            self.assertLess(abs(solution.y[1,-1]-expected["b"]),1e-10)
            self.assertLess(abs(actual["J0"]-expected["radiation_monopole_M"]),1e-10)
            self.assertLess(abs(actual["J2"]/3-expected["radiation_P"]),1e-10)
            self.assertLess(abs(actual["Sigma"]-math.sqrt(3)*abs(expected["s_per_s"])/expected["h_per_s"]),1e-10)
            self.assertGreater(bg.minimum_angular_brightness(solution.y[:,-1]),.6)
    def test_initial_independent_positive_rad_stress_without_shear(self):
        bg=HierarchyBackground(self.source,8,1.,.2,0.,0)
        y=bg.initial_state()
        x=bg.diagnostic(0.,y)
        self.assertEqual(x["Sigma"],0)
        self.assertEqual(x["N0"],1)
        self.assertEqual(x["J0"],1)
        self.assertEqual(x["J2"],.04)
        self.assertAlmostEqual(x["piR"]/(x["radiation_density"]),.2/15,delta=1e-13)
        self.assertGreater(bg.rhs(0.,y)[2],0)
    def test_actual_REI_n_e_Thomson_backreaction(self):
        bg0=HierarchyBackground(self.source,8,1.,.2,0.,0)
        bg1=HierarchyBackground(self.source,8,1.,.2,0.,0,ne_source=self.ne)
        x0,_=bg0.integrate(n=171)
        x1,_=bg1.integrate(n=171)
        a=bg0.diagnostic(x0.t[-1],x0.y[:,-1])
        b=bg1.diagnostic(x1.t[-1],x1.y[:,-1])
        self.assertLess(b["J2"],a["J2"])
        self.assertLess(b["Sigma"],a["Sigma"])
        self.assertGreater(b["GammaT_per_s"],0)
        self.assertLess(abs(x1.y[4+9,-1]-1),2e-12)
        self.assertAlmostEqual(b["piR"],b["radiation_density"]*b["J2"]/(3*b["J0"]),delta=1e-25)
    def test_radiation_and_matter_pi_viscosity_source(self):
        sig,e=public_sigma_from_q(.005)
        m=HierarchyBackground(self.source,8,1.,.2,sig,e,ne_source=self.ne,nu_visc=.02)
        y,dt=m.integrate(n=101)
        finish=m.diagnostic(y.t[-1],y.y[:,-1])
        self.assertGreater(y.y[3,-1],0)
        self.assertLess(finish["piM"],0)
        self.assertGreater(finish["GammaT_per_s"],0)
    def test_legendre_refinement_on_backreacted_full_source(self):
        runs=[]
        for L in (2,4,8,12):
            m=HierarchyBackground(self.source,L,1.,.2,0.,0,ne_source=self.ne)
            # The actual ne(a) has rapid non-smooth source features, so
            # DOP853 adaptivity must be tightened BEFORE comparing L cutoffs.
            s,_=m.integrate(n=101,rtol=1e-13,atol=4e-15)
            diag=m.diagnostic(s.t[-1],s.y[:,-1])
            runs.append((diag["Sigma"],diag["J2"],diag["N0"]))
        d4=max(abs(runs[1][j]-runs[2][j]) for j in range(2))
        d8=max(abs(runs[2][j]-runs[3][j]) for j in range(2))
        self.assertLess(d8,1e-10)
        self.assertLess(d8,d4+1e-11)
        self.assertLess(max(abs(z[2]-1) for z in runs),2e-12)
    def test_convergence_of_saved_Ax08_electron_donor_decimation(self):
        # Two actual source resolutions interpolated without changing scientific history.
        path=self.owner/"research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO_composed_001/history.csv"
        h=np.loadtxt(path,delimiter=",",skiprows=1,usecols=(4,13))
        outputs=[]
        for skip in (17,7,1):
            indices=np.unique(np.r_[np.arange(0,len(h),skip),len(h)-1])
            ne=ElectronHistory(h[indices,0],h[indices,1])
            m=HierarchyBackground(self.source,8,1.,.2,0.,0,ne_source=ne)
            s,_=m.integrate(n=101)
            outputs.append(m.diagnostic(s.t[-1],s.y[:,-1])["J2"])
        self.assertLess(abs(outputs[1]-outputs[2]),1e-10)
        self.assertLess(abs(outputs[0]-outputs[2]),1e-9)
    def test_source_provenance_guards(self):
        with self.assertRaises(ValueError):
            HierarchyBackground(self.source,8,1.,.9,0.,0)
        with self.assertRaises(ValueError):
            HierarchyBackground(self.source,8,1.,.2,.01,0)
        with self.assertRaises(ValueError):
            HierarchyBackground(self.source,8,1.,.2,0.,1)
        with self.assertRaises(ValueError):
            HierarchyBackground(self.source,8,1.,.2,0.,0,nu_visc=-1)
        with self.assertRaises(ValueError):
            legendre_matrix(11)
    def test_original_C11_actual_HHe_thermo_ledgers(self):
        c=real_C11(nsteps=32)
        self.assertEqual(c["accepted"],32)
        self.assertEqual(c["rejected"],0)
        self.assertLess(c["max_energy_eV_H"],1e-9)
        self.assertLess(c["max_photon_electron_per_H"],1e-9)
        self.assertGreater(c["final"]["Tgas_K"],c["initial"]["Tgas_K"])
        self.assertGreater(c["final"]["x_HII"],c["initial"]["x_HII"])
    def test_C11_CMB_receiver_Thomson_feedback_and_number(self):
        sig,e=public_sigma_from_q(0.)
        bg=HierarchyBackground(self.source,8,1.,.2,sig,e)
        sol,_=bg.integrate(n=101)
        c=real_C11(nsteps=32)
        y=np.r_[bg.cos.xmax,sol.y[1:,-1]]
        x0,r0,_=Receiver(bg,c,False).solve(y)
        x1,r1,_=Receiver(bg,c,True).solve(y)
        self.assertLess(r1[-1]["radiation_J2"],r0[-1]["radiation_J2"])
        self.assertLess(abs(r1[-1]["number_N0"]-1),3e-12)
        self.assertTrue(0<r1[-1]["gamma_T_per_s"]<1e-17)
        self.assertLess(abs(r1[-1]["radiation_J2"]-r0[-1]["radiation_J2"]),1e-6)

if __name__=="__main__":
    unittest.main(verbosity=2)
