"""Targeted scientific tests for source-frozen REI Σ–π initial-condition response."""
from __future__ import annotations
import json,math,sys,unittest
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import response
from response import one,check_parent,BASE,DELTA,PARAM_NAMES,CanonicalFVSpecies,source_lock,public_sigma_from_q

class SigmaPiSensitivity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.j=json.loads((HERE/"evidence/RESPONSE_INITIAL.json").read_text())
        cls.deg=json.loads((HERE/"evidence/NONLINEAR_DEGENERACY.json").read_text())

    def test_original_canonical_kinetic_source_exact_hash(self):
        self.assertEqual(check_parent(),response.FV_SHA)

    def test_sources_include_real_signed_Sigma_and_independent_kappa(self):
        self.assertEqual(PARAM_NAMES,("signed_q_shear","initial_kappa_gamma","initial_kappa_nu","initial_A_massive"))
        self.assertAlmostEqual(public_sigma_from_q(.01)[0],math.sqrt(3)*.01/math.sqrt(1+.01**2),delta=1e-15)
        self.assertEqual(public_sigma_from_q(-.01)[1],-1)

    def test_real_native_frozen_electron_donor_identity(self):
        self.assertEqual(self.deg["electron_source_sha256"],"4f6852c3a5152b91224ce5fecad6ccdfe9f7ece4c8a6d39825c6f5e5ca8ae92f")
        self.assertEqual(self.j["cases"]["actual_zero_HHe_oneway_thomson"]["source_physics"]["nfev"]>0,True)

    def test_baseline_matches_parent_actual_canonical_FV_values(self):
        a=self.j["cases"]["collisionless_gamma_nu"]
        b=self.j["cases"]["actual_zero_HHe_oneway_thomson"]
        self.assertLess(abs(a["source_physics"]["Sigma_end"]-0.0001309027031229716),1e-14)
        self.assertLess(abs(b["source_physics"]["Sigma_end"]-0.0001303240572010518),1e-14)

    def test_massive_and_radiation_initial_pi_are_independent_nonzero(self):
        p=self.j["cases"]["actual_zero_HHe_oneway_thomson"]["source_physics"]
        for key in ["initial_pi_massive","initial_rad_pi_gamma","initial_rad_pi_nu"]:
            self.assertGreater(p[key],0)

    def test_empirical_derivative_refinement(self):
        for name,z in self.j["cases"].items():
            c=z["finite_difference_consistency"]
            self.assertLess(c["signed_s_endpoint_response_error"],.005,name)
            self.assertLess(c["max_row_normalized"],.005,name)

    def test_full_observable_jacobian_is_four_parameter_structurally_rank_four(self):
        for lane,z in self.j["cases"].items():
            self.assertEqual(z["coarse"]["rank"],4,lane)
            sv=z["coarse"]["SVD"]
            self.assertEqual(len(sv),4)
            self.assertGreater(min(sv),0.05)
            self.assertLess(z["coarse"]["condition"],100)

    def test_single_final_shear_is_not_injective(self):
        a=self.deg
        self.assertEqual(a["baseline_IC"]["signed_q_ref"],0)
        self.assertNotEqual(a["distinct_IC"]["signed_q_ref"],0)
        self.assertNotEqual(a["distinct_IC"]["kappa_gamma"],a["baseline_IC"]["kappa_gamma"])
        self.assertLess(a["abs_match_error"],1e-12)

    def test_other_sources_observables_separate_degenerate_shear(self):
        d=self.deg["observables_end_delta"]
        self.assertGreater(abs(d["gamma_E2"]),.005)
        self.assertGreater(abs(d["b"]),1e-5)
        self.assertGreater(abs(d["nu_E2"]),1e-5)
        self.assertLess(abs(d["signed_s_over_H"]),1e-12)

    def test_nonlinear_case_respects_original_einstein_hamiltonian(self):
        self.assertLess(self.deg["maximum_full_constraint_error"],4e-14)
        self.assertGreater(self.deg["initial_pi"]["baseline"]["initial_rad_pi_gamma"],0)
        self.assertGreater(self.deg["initial_pi"]["distinct"]["initial_rad_pi_gamma"],0)

    def test_initial_photon_source_quadrupole_analytic_rational(self):
        source=source_lock()
        P=CanonicalFVSpecies(source,2.7255,8,
             Sigma_ref=0.,orientation=0,kappa_gamma=.2,kappa_nu=.2,
             ne_source=None,mass_fraction=.1,massive_A=.5,
             mass_over_Tref=30.,radial_cells=24,angular_cells=12,subcell_gauss_order=3)
        q=P.initial_state()
        d=P.fields(0.,q)
        self.assertAlmostEqual(d["E_gamma"][2],.2/5,delta=1e-15)
        self.assertAlmostEqual(d["E_nu"][2],.2/5,delta=1e-15)
        self.assertLess(abs(d["N_gamma"][2]-.2/5),1e-15)

    def test_physical_source_exact_massless_stress_partial(self):
        src=source_lock()
        def rhs(k):
            P=CanonicalFVSpecies(src,2.7255,8,Sigma_ref=0.,orientation=0,
                 kappa_gamma=k,kappa_nu=.2,ne_source=None,mass_fraction=.1,massive_A=.5,
                 mass_over_Tref=30.,radial_cells=24,angular_cells=12,subcell_gauss_order=3)
            return P.rhs(0.,P.initial_state())[2],P.omega_gamma
        a,omega=rhs(.2+1e-4);b,_=rhs(.2-1e-4)
        numerical=(a-b)/(2e-4)
        theorem=src.h0**2*omega/(5*src.href**2*src.aref**4)
        self.assertLess(abs(numerical/theorem-1),1e-8)

    def test_initial_shear_sign_and_metric_units(self):
        s=one(.0005,.2,.2,.5,donor=None,n=21)
        t=one(-.0005,.2,.2,.5,donor=None,n=21)
        self.assertGreater(s["physical"]["signed_Sigma_ref"],0)
        self.assertLess(t["physical"]["signed_Sigma_ref"],0)
        self.assertLess(s["physical"]["Einstein_H2_constraint_max_relative"],4e-14)
        self.assertLess(t["physical"]["Einstein_H2_constraint_max_relative"],4e-14)

    def test_physical_distribution_rejects_out_of_domain(self):
        for param in [
          (0,.6,.2,.5),(0,.2,-.6,.5),(0,.2,.2,2.1),(.1,.2,.2,.5)]:
            with self.assertRaises(ValueError):one(*param,n=11)

    def test_targeted_only_not_observational_fisher(self):
        self.assertIsNone(self.deg["observational_posterior"])
        self.assertFalse(self.deg["full_ionizing_source_selfconsistent"])
        self.assertIn("collisionless positive canonical massive",self.j["source_scope"])

    def test_actual_process_parallel_same_physical_outputs(self):
        j=json.loads((HERE/"evidence/PARALLEL.json").read_text())
        self.assertEqual(j["physical_sources"],16)
        self.assertEqual(j["worker_counts"],[1,2,4])
        for name in ["1","2","4"]:
            self.assertEqual(j["performance"][name]["max_abs_diff_vs_serial"],0)
        self.assertGreater(j["observed_speedup_4v1"],1.)
        self.assertIsNone(j["native_ionizing_HHe_solver_speedup"])

if __name__=="__main__":
    unittest.main(verbosity=2)
