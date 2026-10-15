#!/usr/bin/env python3
"""Real source C15 iterative Einstein-Boltzmann-UV HHe coupling regressions."""
import hashlib,math,sys
from pathlib import Path
import unittest
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from c15_coupled import (Coupled,Config,NativeStellarSource,Scenario,ROOT,
        START,STOP,THOMSON_RATE,KAPPA,initial_gas,PhotonCloud,SourceState)
from short_interval import run as original_C13,Background,Family
from dynamic_thomson import validate_source_sha

class C15TrueSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=Scenario(ROOT)
        cls.source=NativeStellarSource.load(cls.model,
            ROOT/"research/rei_c13_live_source_20261015/NATIVE_SOURCE_8X8.csv")
        cls.case0=Coupled(Config(nstep=16),cls.source).run()
        cls.caseplus=Coupled(Config(legacy_q_for_locked_source=.005,nstep=16),
                             cls.source).run()
    def solve(self,**kwargs):
        return Coupled(Config(**kwargs),self.source).run()
    def test_real_native_source_git_and_BASS_PSTF_identical(self):
        self.assertEqual(self.source.source_id,"MD14_Z002_FESC_BB50K_13P6_100_V1")
        self.assertAlmostEqual(float(self.source.weights.sum()),1)
        self.assertEqual(self.source.grid_rate.shape,(17,4))
        source=validate_source_sha()
        self.assertEqual(source["PR137_git_blob"],"e15e1875fba7fcc4a42e257e291c54d9b540a3f0")
        s=Coupled(Config(nstep=8),self.source)
        self.assertTrue(.5<s.og/(s.og+s.on)<.7)
    def test_shear_tensor_definition_and_public_sigma(self):
        for q in (0.,.005,-.005):
            c=Coupled(Config(legacy_q_for_locked_source=q,nstep=8),self.source)
            st,y=c.init_state()
            w=c.quantities(math.log(st.a),y,st,float(y[1]))
            sh=w["s"];H=w["h"]
            actual=math.sqrt(.5*((-sh)**2+(-sh)**2+(2*sh)**2))/H
            self.assertAlmostEqual(w["Sigma"],actual,delta=3e-16)
            self.assertEqual(w["epsilon_sigma"],int(np.sign(sh)))
    def test_bass_energy_and_particle_number_monopoles_exact(self):
        c=Coupled(Config(nstep=8),self.source)
        st,y=c.init_state()
        alpha=c.quantities(math.log(st.a),y,st,float(y[1]))["s"]/c.quantities(
            math.log(st.a),y,st,float(y[1]))["h"]
        derivative=c.rhs(math.log(st.a),y,st,float(y[1]))
        n=c.n
        for e,part in ((3,3+n),(3+2*n,3+3*n)):
            self.assertLess(abs(derivative[e]+2*alpha*y[e+2]),2e-14)
            self.assertLess(abs(derivative[part]),2e-14)
        self.assertEqual(c.initial_state if False else st.photons.number,0)
    def test_nonnegative_gas_photons_real_C13_chemical_and_source_ledger(self):
        for r in (self.case0,self.caseplus):
            n=r["numerical"]
            self.assertLess(n["max_photo_number_ledger_error_perH"],3e-13)
            self.assertLess(n["max_photo_energy_ledger_error_eV_perH"],3e-11)
            self.assertTrue(0<r["endpoint"]["photon_N_perH"]<r["endpoint"]["source_N_perH"])
            self.assertGreater(r["endpoint"]["x_HII"],.4)
            self.assertGreater(r["endpoint"]["x_HeII"],.5)
            self.assertGreater(r["endpoint"]["Tgas_K"],12000)
            self.assertLess(abs(r["endpoint"]["number_gamma_N0"]-1),2e-11)
            self.assertLess(abs(r["endpoint"]["number_nu_N0"]-1),2e-11)
            self.assertEqual(r["endpoint"]["a"],STOP)
    def test_sigma_0_without_seed_quadrupole_stays_exact_FLRW(self):
        r=self.solve(nstep=8,kappa_gamma=0.,kappa_nu=0.)
        self.assertLess(r["endpoint"]["Sigma"],1e-20)
        self.assertLess(abs(r["endpoint"]["radiation_gamma_E2"]),1e-15)
        self.assertLess(abs(r["endpoint"]["radiation_nu_E2"]),1e-15)
        self.assertLess(abs(r["endpoint"]["Pi_ion_Pa"]),1e-30)
    def test_new_true_geometry_changes_same_C13_chemistry_proper_clock(self):
        # Unlike the original background prescribed C13, new H additionally
        # contains gas UV/chemical energy; small quantitative difference is REAL.
        old=original_C13(0.,self.source,nstep=16,coalescence_budget=(1e-12,1e-11))
        new=self.case0
        self.assertLess(abs(new["endpoint"]["x_HII"]-old["end"]["x_HII"]),2e-9)
        self.assertLess(abs(new["endpoint"]["Tgas_K"]-old["end"]["Tgas_K"]),2e-4)
        self.assertGreater(abs(new["endpoint"]["elapsed_s"]-old["end"]["elapsed_s"]),10)
        self.assertGreater(new["endpoint"]["Sigma"],1e-9)
        self.assertEqual(old["end"]["Sigma"],0)
    def test_photons_directly_thomson_neutrinos_never_collide(self):
        collided=self.case0
        naked=self.solve(nstep=16,thomson=False)
        self.assertLess(collided["endpoint"]["radiation_gamma_E2"],
                        naked["endpoint"]["radiation_gamma_E2"])
        self.assertAlmostEqual(collided["endpoint"]["radiation_nu_E2"],
                         naked["endpoint"]["radiation_nu_E2"],delta=1e-10)
        self.assertAlmostEqual(collided["endpoint"]["number_nu_N0"],1,delta=2e-12)
        self.assertGreater(collided["numerical"]["tau_Thomson_coupled_differential"],0)
    def test_einstein_uv_pi_is_real_C13_source_pressure(self):
        r=self.caseplus
        endpoint=r["endpoint"]
        self.assertLess(endpoint["Pi_ion_Pa"],0.)
        self.assertAlmostEqual(endpoint["Pi_UV_feedback_Pa"],endpoint["Pi_ion_Pa"],delta=1e-35)
        self.assertAlmostEqual(endpoint["Pi_Einstein_shear_Pa"],
           endpoint["Pi_gamma_and_nu_Pa"]+endpoint["Pi_ion_Pa"],delta=3e-25)
        self.assertGreater(endpoint["UV_to_CMB_radiation_energy"],0)
        self.assertLess(endpoint["UV_to_CMB_radiation_energy"],1e-7)
        no_uv=self.solve(nstep=16,legacy_q_for_locked_source=.005,
             uv_stress_in_shear=False)
        self.assertEqual(no_uv["numerical"]["uv_pi_in_shear"],False)
        self.assertLess(abs(endpoint["x_HII"]-no_uv["endpoint"]["x_HII"]),3e-9)
        # Double precision cannot resolve this UV source's tiny difference
        # against the full primordial radiation stress; no detected response.
    def test_true_scattering_proper_tau_matches_independent_trapezoid(self):
        for result in (self.case0,self.caseplus):
            n=result["numerical"]
            self.assertLess(n["tau_relative_coupled_vs_trapezoid"],1e-7)
            self.assertGreater(n["tau_Thomson_coupled_differential"],1e-6)
            self.assertLess(n["tau_Thomson_coupled_differential"],3e-5)
    def test_source_specific_negative_inputs_rejected(self):
        for args in ({"legacy_q_for_locked_source":.012},
                     {"L":6},{"nstep":600},{"kappa_gamma":.8},
                     {"gravity_feedback":False,"uv_stress_in_shear":True}):
            with self.assertRaises(ValueError):Config(**args)
    def test_shared_source_identity_unmodified(self):
        expected="MD14_Z002_FESC_BB50K_13P6_100_V1"
        self.assertEqual(self.source.source_id,expected)
        self.assertEqual(len(self.case0["history"]),17)
        self.assertTrue(self.case0["numerical"]["coalescence_holds"]==0)
        self.assertEqual(self.case0["physical_gap"]["scientific_admission"],"NOT_ISSUED")

if __name__=="__main__":
    unittest.main(verbosity=2)
