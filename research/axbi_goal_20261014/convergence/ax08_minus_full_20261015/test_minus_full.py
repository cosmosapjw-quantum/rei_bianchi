#!/usr/bin/env python3
"""Focused negative-input and actual saved-result AX08 minus full tests."""
import json
from pathlib import Path
import sys
import unittest
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import minus_milestones as mm

class ScopedMinus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=HERE/"results_001"
        cls.result=json.loads((cls.root/"MINUS_SCIENCE_RESULT.json").read_text())
        cls.feedback=json.loads((cls.root/"feedback_minus_crosscheck.json").read_text())
        cls.quad=json.loads((HERE/"quadrupole_minus_crosscheck.json").read_text())
        cls.milestones=json.loads((cls.root/"MINUS_MILESTONES.json").read_text())
        cls.rust=json.loads((HERE/"logs/rust_minus_census.stdout").read_text())

    def test_case_counts_are_real_full_and_mapped(self):
        r=self.result
        self.assertEqual(r["actual_minus_rows"],312238)
        self.assertEqual(r["minus_census"]["rows"],1873428)
        self.assertEqual(len(r["full_case_sha256"]),5)
        self.assertEqual(r["scientific_admission"],"NOT_ISSUED")
        self.assertEqual(set(r["comparisons"]),{"SHEAR_MINUS","SHEAR_HALF_PLUS"})

    def test_science_census_python_rust_same_results(self):
        a=self.result["minus_census"]
        b=self.rust
        self.assertEqual(b["case"],"SHEAR_MINUS")
        self.assertEqual(b["history_rows"],312238)
        self.assertEqual(b["ion_rows"],1873428)
        self.assertTrue(b["all_pass"])
        self.assertAlmostEqual(b["helium_per_hydrogen_initial"],
                               a["initial_nHe_per_nH"],delta=2e-15)
        mapping=("species_number","history_fraction","electron_charge","electron_xe",
                 "H_number","He_number","Ybaryon_sum","gas_temperature","electron_history")
        for v,k in zip(b["max_abs_residuals"],mapping):
            self.assertLess(abs(v-a["max_abs_residuals"][k]),2e-15)

    def test_real_clock_algebra_and_source_level(self):
        r=self.result["comparisons"]["SHEAR_MINUS"]
        self.assertGreater(r["max_proper_time_offset_s"],1e11)
        self.assertEqual(r["nodes"],4097)
        for name,v in r["observables"].items():
            self.assertLess(v["exact_discrete_decomposition_error"],5e-14)
            self.assertEqual(v["numerical_source_error"],"UNKNOWN_NOT_AX11_CERTIFIED")

    def test_real_independent_angular_stress(self):
        self.assertEqual(self.quad["status"],"PASS_STORED_SIMPSON_VS_INDEPENDENT_LOCAL_GL128")
        s=self.quad["results"]["SHEAR_MINUS"]
        self.assertLess(s["max_abs_pressure_difference_over_rho_iso"],3e-14)
        self.assertGreater(s["endpoint_pressure_saved_J_m3"],0.0)

    def test_saved_omitted_feedback_is_screening_only(self):
        self.assertFalse(self.feedback["feedback_applied_to_evolution"])
        self.assertEqual(self.feedback["status"],
                         "PYTHON_KAHAN_RUST_STREAMING_NUMERICAL_PARITY_PASS")
        v=self.feedback["python_science"]["SHEAR_MINUS"]
        self.assertTrue(v["measured_below_perturbative_ceiling"])
        self.assertLess(v["max_abs_delta_s_over_H"]["abs_delta_s_over_H"],1e-4)

    def test_first_upward_crossing_manufactured_and_frozen(self):
        a=np.array([.1,.2,.3,.4])
        t=np.array([0.,1.,2.,3.])
        x=np.array([.0,.3,.8,1.0])
        r=mm.crossing(a,t,x,.5)
        self.assertEqual(r["all_upward_crossings"],1)
        self.assertAlmostEqual(r["a"],.24,places=12)
        self.assertAlmostEqual(r["proper_time_s"],1.4,places=12)
        for x in ([0.,0.,0.,0.],[1.,1.,1.,1.]):
            with self.assertRaisesRegex(ValueError,"NO_UPWARD_CROSSING"):
                mm.crossing(a,t,np.array(x),.5)
        with self.assertRaisesRegex(ValueError,"CLOCK_NOT_STRICTLY_MONOTONE"):
            mm.crossing(np.array([.1,.1,.3,.4]),t,np.array([0.,.3,.8,1.]),.5)

    def test_actual_milestones_first_cross_and_four_to_one_ratio(self):
        r=self.milestones
        self.assertEqual(r["status"],"EXPLORATORY_THREE_ACTUAL_FULL_CASES")
        for level,record in r["results"].items():
            self.assertLess(record["minus_minus_zero_redshift"],0)
            self.assertLess(record["half_plus_minus_zero_redshift"],0)
            for c in record["cases"].values():
                self.assertGreater(c["all_upward_crossings"],0)
                self.assertTrue(0.<=c["linear_fraction"]<=1.)
                self.assertGreater(c["bracketing_time_width_s"],0)
        for level in ("0.1","0.5","0.9"):
            r4=r["results"][level]["unequal_amp_q_squared_ratio"]
            self.assertTrue(3.9<r4<4.1)

if __name__=="__main__":
    unittest.main(verbosity=2)
