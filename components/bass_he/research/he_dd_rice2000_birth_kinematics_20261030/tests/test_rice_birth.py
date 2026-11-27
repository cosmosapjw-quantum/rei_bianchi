import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from build_rice_birth import (E_ALPHA, E_D, Q, PARENT_BLOB_SHA, atlas,
    invariants, monotonic_certificate, one_pair, source_blob_sha, write)


class TestRiceBirth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "inputs/RICE2000_TABLE_I_AUTHORITATIVE.json").read_text())
        cls.atlas = atlas(cls.data)

    def test_original_git_blob_and_sha256(self):
        raw = (ROOT / "inputs/RICE2000_TABLE_I_AUTHORITATIVE.json").read_bytes()
        self.assertEqual(source_blob_sha(raw), PARENT_BLOB_SHA)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), "dd29c7b492162b257b6b9674792c2db5cf65c98921cbea088a9283ea641bc03a")

    def test_source_count_and_nonindependent(self):
        self.assertEqual(len(self.atlas["rows"]), 12)
        self.assertEqual(self.atlas["source"]["independent_experiments"], 1)

    def test_threshold(self):
        with self.assertRaises(ValueError):
            one_pair(Q - 1e-3, 90)

    def test_daughter_energy_sum_and_swap(self):
        for e in (150, 170, 190, 220, 250):
            for a in (0, 33, 44.7, 90, 107.3, 180):
                v = one_pair(e, a)
                w = one_pair(e, 180-a)
                self.assertAlmostEqual(v["K_sum_MeV"], e-Q, places=9)
                self.assertAlmostEqual(v["K_plus_MeV"], w["K_minus_MeV"], places=9)
                self.assertAlmostEqual(v["pair_population_variance_MeV2"], w["pair_population_variance_MeV2"], places=9)

    def test_mass_shell_and_four_momentum(self):
        for e in (150, 170, 190, 220, 250):
            for a in (0, 44.7, 90.3, 138.9, 180):
                v = one_pair(e, a)
                self.assertLess(abs(v["mass_shell_plus_MeV2"]), 1e-5)
                self.assertLess(abs(v["mass_shell_minus_MeV2"]), 1e-5)
                self.assertLess(abs(v["momentum_z_residual_c_MeV"]), 1e-9)

    def test_endpoint_monotonic_certificate(self):
        self.assertLess(monotonic_certificate(150,190), 1)
        self.assertLess(monotonic_certificate(190,250), 1)
        for row in self.atlas["rows"]:
            for key in ("pair_Ksum_support_MeV", "daughter_Khigh_support_MeV", "daughter_Klow_support_MeV", "pair_population_variance_support_MeV2"):
                lo, hi = row[key]
                self.assertLessEqual(lo, hi)

    def test_endpoint_grid_inside_support(self):
        for row in self.atlas["rows"]:
            lo, hi = row["Egamma_interval_MeV"]
            for j in range(21):
                e = lo + (hi-lo)*j/20
                p = one_pair(e, row["effective_theta_cm_deg"])
                for key, pk in (("daughter_Khigh_support_MeV","K_high_MeV"),("daughter_Klow_support_MeV","K_low_MeV"),("pair_population_variance_support_MeV2","pair_population_variance_MeV2")):
                    self.assertGreaterEqual(p[pk]+1e-9,row[key][0])
                    self.assertLessEqual(p[pk]-1e-9,row[key][1])

    def test_binned_birth_moment_bounds(self):
        for row in self.atlas["rows"]:
            lo,hi = row["Egamma_interval_MeV"]
            da = row["measured_DA_nb_per_sr"]
            self.assertAlmostEqual(row["same_weight_birth_energy_DA_support_nb_MeV_per_sr"][0], da*(lo-Q), places=9)
            self.assertAlmostEqual(row["same_weight_birth_energy_DA_support_nb_MeV_per_sr"][1], da*(hi-Q), places=9)

    def test_measured_errors_not_joint_covariance(self):
        self.assertIsNone(self.data["covariance_observed"])
        for row in self.atlas["rows"]:
            self.assertGreater(row["measured_DA_nb_per_sr"],0)
            self.assertIn(row["systematic_fraction_reported_not_joint_covariance"], (0.071, 0.13))

    def test_result_has_no_photon_source_or_heat(self):
        self.assertIsNone(self.atlas["R_event"])
        self.assertIsNone(self.atlas["heat_rate"])
        self.assertFalse(self.atlas["L4"])
        self.assertEqual(self.atlas["canonical_DAG"], "28/88")

    def test_idempotent_regeneration(self):
        write(ROOT)
        names = ("RICE2000_BIRTH_KINEMATICS.json", "RICE2000_BIRTH_KINEMATICS.csv")
        old = [hashlib.sha256((ROOT/"results"/n).read_bytes()).hexdigest() for n in names]
        write(ROOT)
        new = [hashlib.sha256((ROOT/"results"/n).read_bytes()).hexdigest() for n in names]
        self.assertEqual(old, new)


if __name__ == "__main__":
    unittest.main()
