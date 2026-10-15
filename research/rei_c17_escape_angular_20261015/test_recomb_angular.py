#!/usr/bin/env python3
"""Sharp angular Case-A pressure cone and actual C15 stellar/chemistry histories."""
import math,sys,unittest
from pathlib import Path
import numpy as np
from scipy.integrate import quad

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import recomb_angular as a

class EscapePositiveAngular(unittest.TestCase):
    def test_kernel_sharp_bounds_at_true_axis_and_transverse_rays(self):
        for db in (-.3,-.03,-1e-4,0.,1e-4,.03,.3):
            for fraction in (.85,1.):
                aemit=.197; aobs=.2;u=.003*fraction
                bounds=a.exact_positive_bounds(u,aemit,aobs,db)
                r,k,f=a.kernel(np.array([0.,-1.,1.]),db)
                fac=u*aemit/aobs
                self.assertAlmostEqual(fac*k[0],bounds["Pi_lower"],delta=2e-14*u)
                self.assertAlmostEqual(fac*k[1],bounds["Pi_upper"],delta=2e-14*u)
                self.assertAlmostEqual(fac*k[2],bounds["Pi_upper"],delta=2e-14*u)
                for y in np.linspace(0,1,1001):
                    kr=a.kernel(np.array([math.sqrt(y)]),db)[1][0]
                    self.assertGreaterEqual(kr,k[0]-1e-14)
                    self.assertLessEqual(kr,k[1]+1e-14)
                self.assertLessEqual(bounds["energy_lower"],bounds["energy_upper"])
                self.assertGreaterEqual(bounds["Pi_upper"],bounds["Pi_lower"])

    def test_isotropic_condition_small_shear_linear_minus_eight_fifths(self):
        for d in (-.0001,-.00001,.00001,.0001):
            e,Pi,F=a.isotropic_kernel(d,32)
            self.assertLess(abs(F),1e-15)
            self.assertLess(abs(e-1),1e-4)
            self.assertLess(abs(Pi/d+8/5),5e-4)
            self.assertGreater(abs(Pi),0.)
        e,pi,f=a.isotropic_kernel(0,16)
        self.assertAlmostEqual(e,1.,places=14)
        self.assertLess(abs(pi),1e-14)
        self.assertLess(abs(f),1e-14)

    def test_stable_expm1_quadrupole_tiny_shear_roundoff(self):
        # A naive Legendre mean subtracts O(1) positive and negative terms.
        # The new source uses an *exact* k-P2 reformulation and expm1.
        for db in (-1e-9,-1e-11,-1e-12,1e-12,1e-11,1e-9):
            estimated=[a.isotropic_kernel(db,n)[1] for n in (8,16,32,64)]
            for pi in estimated:
                self.assertLess(abs(pi/(-8*db/5)-1),2e-8)
            self.assertLess(max(estimated)-min(estimated),
                            1e-14*max(abs(pi) for pi in estimated))
        self.assertEqual(a.isotropic_kernel(0,8)[1],0.)

    def test_isotropic_gauss_vs_independent_quad_across_signs(self):
        for d in (-.19,-.03,-.000003,0,.000003,.03,.19):
            integr=a.isotropic_independent_quad(d)
            estimated=a.isotropic_kernel(d,48)
            np.testing.assert_allclose(estimated,integr,rtol=3e-12,atol=1e-14)
            if d>0:self.assertLess(estimated[1],0)
            if d<0:self.assertGreater(estimated[1],0)

    def test_true_Killing_packet_reproduces_spectrum_independent_bolometric_Pi(self):
        for db in (-.015,0.,.015):
            fac=a.isotropic_shell(.002,.19,.2,0.,db,32)
            mu,w=a.gauss(32)
            for energy in (18.5,39.,82.):
                cloud=a.c13.PhotonCloud(np.full(len(mu),energy),
                          mu.copy(),w*.002/energy)
                moved=cloud.drift(math.log(.2/.19),db)
                obs=a.c15.UV_moments_per_H if hasattr(a.c15,"UV_moments_per_H") else None
                weight=moved.E*moved.NperH
                actual=float(weight.sum())
                Pi=float(weight@(.5*(3*moved.mu**2-1)))
                F=float(weight@moved.mu)
                self.assertAlmostEqual(actual,fac["U_eV_H"],delta=1e-15)
                self.assertAlmostEqual(Pi,fac["Pi_eV_H"],delta=1e-15)
                self.assertAlmostEqual(F,fac["cPz_eV_H"],delta=1e-15)

    def test_transverse_and_axis_emitted_zero_flux_same_U_but_opposite_Pi(self):
        emit=.003;ae=.199;ao=.2;db=.012
        bounds=a.exact_positive_bounds(emit,ae,ao,db)
        cross=a.c13.PhotonCloud(np.array([40.]),np.array([0.]),np.array([emit/40.]))
        axial=a.c13.PhotonCloud(np.array([40.,40.]),np.array([-1.,1.]),
                                np.array([emit/80.,emit/80.]))
        for cloud,expected in ((cross,bounds["Pi_lower"]),(axial,bounds["Pi_upper"])):
            transformed=cloud.drift(math.log(ao/ae),db)
            w=transformed.NperH*transformed.E
            Pi=float(w@(.5*(3*transformed.mu**2-1)))
            F=float(w@transformed.mu)
            self.assertAlmostEqual(Pi,expected,delta=2e-16)
            self.assertLess(abs(F),1e-16)

    def test_real_C15_caseA_source_two_orientation_and_FLRW_recovery(self):
        for sig,ori in ((0.,0),(.002,1),(.002,-1)):
            p=a.c15.Parameters(sig,ori,.2,.2,.1,.5)
            result=a.actual_C15_case(p,nsteps=32,nmu=32)
            z=result["final"]
            self.assertGreater(z["escape_U_eV_perH"],.0021)
            self.assertGreater(z["U_rec_eV_perH"],.0021)
            self.assertLess(z["U_rec_eV_perH"],z["escape_U_eV_perH"])
            self.assertLess(abs(z["cPz_rec_eV_perH"]),2e-13)
            self.assertLess(result["max_hhe_energy_ledger_replacement_abs_eV_H"],5e-11)
            self.assertLess(result["max_hhe_photon_electron_ledger_abs_perH"],5e-12)
            self.assertLess(result["sharp_linearized_abs_delta_Sigma_envelope_any_positive_angles"],5e-16)
            self.assertGreaterEqual(z["Pi_rec_eV_perH"],z["Pi_rec_lower"]-1e-14)
            self.assertLessEqual(z["Pi_rec_eV_perH"],z["Pi_rec_upper"]+1e-14)
            self.assertLessEqual(
                result["linearized_abs_delta_Sigma_from_conditional_isotropic_CaseA"],
                result["sharp_linearized_abs_delta_Sigma_envelope_any_positive_angles"])
            if ori>0:self.assertLess(z["Pi_rec_eV_perH"],0)
            if ori<0:self.assertGreater(z["Pi_rec_eV_perH"],0)
        zero=a.actual_C15_case(a.c15.Parameters(0.,0,0.,0.,0.,0.),
                              nsteps=32,nmu=32)
        self.assertLess(abs(zero["final"]["Pi_rec_eV_perH"]),1e-12)
        self.assertLess(zero["linearized_abs_delta_Sigma_from_conditional_isotropic_CaseA"],1e-23)

    def test_real_C15_exact_positive_bounds_sharp_source_history(self):
        r=a.actual_C15_case(a.c15.Parameters(.002,1,.2,.2,.1,.5),nsteps=16,nmu=32)
        final=r["final"]
        self.assertEqual(len(r["source_escapes"]),16)
        self.assertEqual(r["history"][0]["U_rec_eV_perH"],0.)
        self.assertTrue(all(item["energy_eV_perH"]>=0 for item in r["source_escapes"]))
        self.assertTrue(all(x["Pi_rec_lower"]<=x["Pi_rec_eV_perH"]<=x["Pi_rec_upper"]
                            for x in r["history"][1:]))
        # The same ejected angular extremes saturate every interim bound,
        # so the *linearized fixed-geometry response interval* is sharp.
        l,u=r["linearized_shear_source_response_interval_per_s"]
        middle=r["linearized_same_background_delta_s_per_s"]
        self.assertLess(l,middle)
        self.assertLess(middle,u)

    def test_invalid_input_and_unadmitted_spectrum(self):
        with self.assertRaises(ValueError):a.isotropic_shell(-.2,.19,.2,0.,0.)
        with self.assertRaises(ValueError):a.isotropic_shell(.2,.21,.2,0.,0.)
        with self.assertRaises(ValueError):a.isotropic_kernel(1.2,16)
        with self.assertRaises(ValueError):a.gauss(7)
        with self.assertRaises(ValueError):a.kernel(np.array([1.1]),.01)
        with self.assertRaises(ValueError):a.radiation_from_births([],-.1,0)
        with self.assertRaises(ValueError):
            a.actual_C15_case(a.c15.Parameters(0.,0),nsteps=16,emission_clock="strange")

if __name__=="__main__":
    unittest.main(verbosity=2)
