#!/usr/bin/env python3
"""Native C13 e(a) -> exact PR137 gamma/nu unpolarized Thomson receiver tests."""
import hashlib
import math
import sys
import unittest
from pathlib import Path

import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import dynamic_thomson as c14


class SourceDrivenThomson(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m=c14.Scenario(c14.ROOT)
        src=c14.NativeStellarSource.load(m,c14.ROOT/
                 "research/rei_c13_live_source_20261015/NATIVE_SOURCE_8X8.csv")
        cls.model=m
        cls.real_src=src
        cls.donors={q:c14.ElectronSource.from_real_c13(
            c14.run_c13(q,src,nstep=128,coalescence_budget=(1e-12,1e-11)),m)
            for q in (0.,.01,-.01)}

    def test_exact_pr137_git_blob_and_scattering_constant(self):
        meta=c14.validate_source_sha()
        self.assertEqual(meta["PR137_git_blob"],c14.SOURCE_GIT_BLOB)
        self.assertEqual(meta["PR137_git_commit"],c14.SOURCE_COMMIT)
        self.assertAlmostEqual(c14.GAMMA_PER_NE,c14.C_CGS*c14.THOMSON_CGS,places=32)
        self.assertTrue(0.5<c14.omega_gamma_fraction(self.model)["Omega_gamma_fraction"]<.7)

    def test_c13_source_radiation_and_electron_clock_are_the_same(self):
        for q,donor in self.donors.items():
            a=donor.a
            self.assertGreater(len(a),100)
            self.assertTrue(np.all(np.diff(a)>0))
            self.assertAlmostEqual(float(donor.ne(a[0])),float(donor.proper_ne_cm3[0]),places=17)
            self.assertAlmostEqual(float(donor.ne(a[-1])),float(donor.proper_ne_cm3[-1]),places=17)
            self.assertEqual(donor.donor["q"],q)
            self.assertEqual(donor.donor["model"],"REI_AXBI_MD14_NATIVE_SOURCE_SHORT_C13")

    def test_isotropic_flrw_exact_scalar_Thomson_P2_damping(self):
        electron=self.donors[0.]
        initial=.2/5.
        thomson=c14.OneWayThomson(electron,c14.PhysicalThomson(.2,.2,L=8,scattering=True)).run()
        off=c14.OneWayThomson(electron,c14.PhysicalThomson(.2,.2,L=8,scattering=False)).run()
        tau=thomson["tau_thomson_DOP853"]
        on_end=thomson["history"][-1]
        off_end=off["history"][-1]
        self.assertAlmostEqual(thomson["history"][0]["gamma_energy_J2"],initial,places=14)
        self.assertLess(abs(on_end["gamma_energy_J2"]-
                            initial*math.exp(-.9*tau)),5e-12)
        self.assertLess(abs(on_end["nu_energy_J2"]-initial),5e-14)
        self.assertLess(abs(off_end["gamma_energy_J2"]-initial),5e-14)
        self.assertLess(abs(off_end["nu_energy_J2"]-initial),5e-14)
        self.assertLess(on_end["gamma_energy_J2"],off_end["gamma_energy_J2"])
        self.assertGreater(on_end["gamma_energy_J2"],0.)

    def test_physical_Pi_vs_PR137_driver_normalization(self):
        electron=self.donors[0.]
        r=c14.OneWayThomson(
            electron,c14.PhysicalThomson(.2,.0,L=8,scattering=False)).run()
        ini=r["history"][0]
        u0=c14.A_RAD*2.7255**4/ini["a"]**4
        # Original PR135 pressure Pi=p_parallel-p_perp is epsilon*J2.
        self.assertAlmostEqual(ini["Pi_gamma_physical_Pa"]/u0,.2/5,places=13)
        self.assertAlmostEqual(ini["PR137_normalized_shear_source_gamma_Pa"]/u0,
                               (.2/5)/3,places=13)
        self.assertAlmostEqual(
            ini["shear_rhs_source_gamma_s2"],
            3*c14.KAPPA*ini["PR137_normalized_shear_source_gamma_Pa"],
            delta=3e-44)

    def test_number_mono_ledger_and_independent_tau_quadrature(self):
        for q,donor in self.donors.items():
            c14run=c14.OneWayThomson(donor,c14.PhysicalThomson(.2,-.1,L=8)).run()
            self.assertLess(c14run["gamma_number_N0_max_drift"],2e-12)
            self.assertLess(c14run["nu_number_N0_max_drift"],2e-12)
            self.assertLess(c14run["max_unpolarized_energy_mono_RHS_residual"],1e-12)
            self.assertLess(c14run["max_photon_and_neutrino_number_mono_RHS_residual"],1e-12)
            self.assertLess(c14run["tau_relative_disagreement_solver_vs_quad"],2e-7)
            self.assertLess(c14run["tau_relative_disagreement_C13_vs_quad"],2e-5)
            self.assertTrue(c14run["tau_thomson_DOP853"]>0)

    def test_signed_q_sourced_quadrupole_and_uncollided_neutrinos(self):
        for q,sign in ((.01,-1),(-.01,1)):
            donor=self.donors[q]
            baseline=c14.OneWayThomson(donor,c14.PhysicalThomson(0.,0.,L=8,scattering=False)).run()
            scatter=c14.OneWayThomson(donor,c14.PhysicalThomson(0.,0.,L=8,scattering=True)).run()
            after0=baseline["history"][-1];after1=scatter["history"][-1]
            self.assertGreater(sign*after1["gamma_energy_J2"],0)
            self.assertGreater(sign*after1["nu_energy_J2"],0)
            self.assertAlmostEqual(after1["nu_energy_J2"],after0["nu_energy_J2"],delta=5e-13)
            self.assertLess(abs(after1["gamma_energy_J2"]),abs(after0["gamma_energy_J2"]))
            self.assertGreater(abs(after1["Pi_gamma_physical_Pa"]),0.)
            self.assertGreater(abs(after1["Pi_nu_physical_Pa"]),0.)

    def test_angular_hierarchy_convergence_for_current_short_interval(self):
        electron=self.donors[.01]
        series=[c14.OneWayThomson(electron,c14.PhysicalThomson(.2,.0,L=L)).run()
                for L in (4,8,12)]
        for field in ("gamma_energy_J0","gamma_energy_J2","nu_energy_J2"):
            d=abs(series[0]["history"][-1][field]-
                  series[1]["history"][-1][field])
            self.assertLess(d,1e-9)
            d2=abs(series[1]["history"][-1][field]-
                   series[2]["history"][-1][field])
            self.assertLess(d2,1e-12)

    def test_cached_original_BASS_LRS_operators_are_identical_readonly(self):
        for L in (4,8,12):
            saved=c14._cached_source_angular_operators(L)
            again=c14._cached_source_angular_operators(L)
            self.assertIs(saved,again)
            for got,ref in zip(saved,(c14.legendre_matrix(L,power=4),
                                       c14.legendre_matrix(L,power=3),
                                       c14.thomson_coeffs(L))):
                np.testing.assert_array_equal(got,ref)
                self.assertFalse(got.flags.writeable)

    def test_unphysical_pr137_initial_source_rejected(self):
        with self.assertRaises(ValueError):
            c14.PhysicalThomson(2.01,0.)
        with self.assertRaises(ValueError):
            c14.PhysicalThomson(-1.01,0.)
        with self.assertRaises(ValueError):
            c14.PhysicalThomson(0.,0.,L=7)
        with self.assertRaises(ValueError):
            c14.ElectronSource.from_real_c13({"q":0.},self.model)

if __name__=="__main__":unittest.main(verbosity=2)
