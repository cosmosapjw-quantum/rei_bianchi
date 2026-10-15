#!/usr/bin/env python3
"""Four actual completed AX08 histories: SHA, chemistry, geometry and parity.

Tests use the real saved result and an independent std-only Rust output.
No synthetic fake "science" PASS is substituted for the source files.
"""
import json
from pathlib import Path
import unittest
HERE=Path(__file__).resolve().parent

class RealCompletedSignedFamily(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parity=json.loads((HERE/"results/full_halfminus_parity_002/FULL_SIGNED_PARITY.json").read_text())
        cls.rust=json.loads((HERE/"results/halfminus_rust_census.json").read_text())
    def test_source_4_full_and_terminal_identities(self):
        p=self.parity
        self.assertEqual(p["status"],"SCOPED_FOUR_ACTUAL_COMPLETED_CASES")
        self.assertEqual(p["real_rows_each"],312238)
        self.assertEqual(len(p["source_composition_hashes"]),4)
        self.assertEqual(p["scientific_admission"],"NOT_ISSUED")
    def test_exact_background_bitwise_pair(self):
        q=self.parity["verified_exact_background_pair_all_rows"]
        self.assertTrue(q["a_exact_array"])
        self.assertTrue(q["time_exact_array"])
        self.assertTrue(q["b_odd_exact_array"])
        self.assertEqual(q["all_saved_rows"],312238)
        self.assertEqual(q["max_abs_b_plus_bminus"],0.)
        self.assertEqual(self.parity["mean_scale_time_pair_max_abs_s"],0.)
    def test_halfminus_full_chemistry_independent_two_backends(self):
        r=self.rust; p=self.parity["minus_full_species_census"]
        self.assertTrue(r["all_pass"])
        self.assertEqual(r["case"],"SHEAR_HALF_MINUS")
        self.assertEqual(r["history_rows"],312238)
        self.assertEqual(r["ion_rows"],1873428)
        self.assertEqual(p["rows"],1873428)
        index_mapping=("species_number","history_fraction","electron_charge","electron_xe",
            "H_number","He_number","Ybaryon_sum","gas_temperature","electron_history")
        for ref,name in zip(r["max_abs_residuals"],index_mapping):
            self.assertLess(abs(ref-p["max_abs_residuals"][name]),3e-15,name)
    def test_completed_ionic_fractions_are_physical(self):
        for name,v in self.parity["endpoints"].items():
            self.assertTrue(0<=v["x_HII"]<=1)
            self.assertTrue(0<=v["x_HeII"]<=1)
            self.assertTrue(0<=v["x_HeIII"]<=1)
            self.assertTrue(v["x_HeII"]+v["x_HeIII"]<=1.0000001)
            self.assertTrue(v["Tgas_K"]>0)
            self.assertEqual(v["mean_a"],.2)
    def test_even_odd_observables_finite_and_different(self):
        import math
        for name,v in self.parity["parity"].items():
            self.assertTrue(math.isfinite(v["even_max_abs"]))
            self.assertTrue(math.isfinite(v["odd_max_abs"]))
            self.assertEqual(v["relative_source_numerical_error"],"UNKNOWN_AX11")
        self.assertGreater(self.parity["parity"]["x_HII"]["even_max_abs"],
                           self.parity["parity"]["x_HII"]["odd_max_abs"])
        self.assertGreater(self.parity["parity"]["J2_photon_u_eV_per_H"]["odd_max_abs"],
                           self.parity["parity"]["J2_photon_u_eV_per_H"]["even_max_abs"])
    def test_real_bbn_plot_files(self):
        folder=HERE/"results/full_halfminus_parity_002"
        for name in ("full_halfminus_parity.png","four_actual_HHe_histories.png",
                     "four_HHe_BBNstyle_time_temperature.png"):
            self.assertGreater((folder/name).stat().st_size,15_000)

if __name__=="__main__":
    unittest.main(verbosity=2)
