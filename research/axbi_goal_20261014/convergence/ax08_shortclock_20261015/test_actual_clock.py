#!/usr/bin/env python3
"""Real-source AX08 background clock scientific C8 regression + negative fixtures."""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from actual_clock_gl4 import load_one, signed_prefix, case_audit, SOURCE_SHA
from perturbative_clock import physical_coefficients,prediction
from shortstep import Background,Family,gauss_batch,gauss_increment,stable_dx

class SourceClockRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.owner=Path.home()/"Dropbox/bianchi/rei_bianchi"
        cls.result=json.loads((HERE/"results/actual_clock_gl4.json").read_text())
        cls.allrows=json.loads((HERE/"results/actual_clock_allrows.json").read_text())
        cls.model=json.loads((HERE/"results/perturbative_clock.json").read_text())
    def test_vendor_source_byte_identity_and_physics_case(self):
        p=HERE/"vendor/bass_20261015/source/REI_BACKGROUND_FAMILY_LOCK.json"
        self.assertTrue(p.is_file())
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),SOURCE_SHA)
        z=Background(Family(0.0))
        self.assertEqual(z.aref,1/21)
        self.assertEqual(z.aend,.2)
        self.assertEqual(z.case.family,"PhysicalDensityFixed")
    def test_5_source_history_identity_and_volume(self):
        self.assertEqual(self.allrows["status"],"REAL_SAVED_AX08_5_INPUT_CLOCK_ANALYSIS_PASS")
        for name,v in self.allrows["modes"].items():
            expected=312238 if not name.endswith("_PREFIX") else 200001
            self.assertEqual(v["rows"],expected)
            self.assertEqual(v["sampled_states"],expected)
            self.assertLess(v["max_rel_GL4_GL8_time_increment"],1e-12)
            self.assertGreaterEqual(v["max_rel_saved_dt_minus_GL4"],0)
    def test_exact_signed_original_background_pair_symmetry(self):
        pair=self.allrows["signed_static_prefix"]
        self.assertTrue(pair["clock_array_identical_bytes_as_float"])
        self.assertTrue(pair["same_mean_scale_exact"])
        for k in ("max_abs_saved_proper_clock_symmetry_s","max_abs_saved_b_antisymmetry",
                  "max_abs_GL4_dt_even_antisymmetric_error_s","max_abs_GL4_db_odd_symmetry_error"):
            self.assertEqual(pair[k],0)
    def test_gauss_interval_independent_order_and_positive(self):
        for q in (0.,-.005,.005,-.01):
            bg=Background(Family(q))
            a=np.array([.06,.091,.15])
            delta=np.array([1e-7,1e-6,1e-5])
            s,e=a,a+delta
            t4,b4=gauss_batch(bg,s,e,order=4)
            t8,b8=gauss_batch(bg,s,e,order=8)
            self.assertTrue(np.all(t4>0))
            self.assertLess(float(np.max(np.abs(t4-t8)/t8)),1e-12)
            if q==0.:self.assertTrue(np.array_equal(b4,np.zeros_like(b4)))
            else:self.assertTrue(np.all(np.sign(b4)==np.sign(q)))
    def test_nextfloat_nearby_not_zero(self):
        bg=Background(Family(.01))
        a=.1; nexta=float(np.nextafter(a,1))
        x=stable_dx(a,nexta)
        self.assertGreater(x,0)
        t,b=gauss_increment(bg,a,nexta,order=4)
        self.assertTrue(3.<t<4.)
        self.assertGreater(b,0)
    def test_source_locked_negative_unphysical(self):
        with self.assertRaises(ValueError):
            Background(Family(.000123))
        bg=Background(Family(.005))
        with self.assertRaises(ValueError):
            gauss_increment(bg,.1,.09,order=4)
        with self.assertRaises(ValueError):
            gauss_batch(bg,np.array([.1]),np.array([.09]),order=4)
        with self.assertRaises(ValueError):
            stable_dx(-1,.1)
    def test_perturbative_integral_parity_and_positive_remainder(self):
        coeff=physical_coefficients(order=16,n_panel=128)
        for q in (.005,.01):
            p=prediction(coeff,q)
            n=prediction(coeff,-q)
            self.assertEqual(p["clock_shift_s_taylor6"],n["clock_shift_s_taylor6"])
            self.assertAlmostEqual(p["b_shift_taylor7"],-n["b_shift_taylor7"],delta=1e-17)
            self.assertLess(p["analytic_clock_taylor_remainder_bound_s"]/abs(p["clock_shift_s_taylor6"]),1e-10)
    def test_real_full_case_perturbative_clock_relative_residual(self):
        cases={i["case"]:i for i in self.model["saved_case_endpoint_samples"]}
        self.assertAlmostEqual(cases["ZERO"]["actual_saved_t_shift_s"],0)
        for case in ("SHEAR_HALF_PLUS","SHEAR_MINUS"):
            x=cases[case]
            self.assertLess(x["relative_observed_clock_residual_to_effect"],1e-8)
            self.assertLess(abs(x["observed_minus_taylor_b"]),1e-13)

if __name__=="__main__":
    unittest.main(verbosity=2)
