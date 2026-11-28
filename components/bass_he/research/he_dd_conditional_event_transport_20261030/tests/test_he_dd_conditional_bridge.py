"""Targeted regression for the conditional source-sigma and correlated D pair.

These tests exercise a deliberately uncalibrated physical bridge only, not
original EXFOR parsing or cosmological production.
"""
import json
import sys
import tempfile
import unittest
from fractions import Fraction as F
from pathlib import Path

import mpmath as mp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from he_dd_conditional_bridge import (
    ATLAS_GIT_BLOB, M_ALPHA, M_D, Q, E_THRESHOLD,
    git_blob, load_frozen_atlas, linear_330_reported,
    pair_momentum_kernel, pair_invariants
)

DA_SOURCE_COORDS = [(E, a) for E in (213, 258, 330)
                    for a in (46, 61, 73, 87)]
SIG_SOURCE_ROWS = [(201, "2.41", ".32"), (225, "1.29", ".23"),
                   (253, ".92", ".20"), (285, "1.04", ".20"),
                   (320, ".61", ".16"), (359, ".55", ".15")]


class TestSourceSafeBridge(unittest.TestCase):
    def test_original_source_coordinate_counts(self):
        self.assertEqual(len(DA_SOURCE_COORDS), 12)
        self.assertEqual(len(SIG_SOURCE_ROWS), 6)
        self.assertNotIn(330, [x[0] for x in SIG_SOURCE_ROWS])
        self.assertEqual(len(set(DA_SOURCE_COORDS)), 12)

    def test_exact_interpolation(self):
        r = linear_330_reported(F(".61"), F(".16"), F(".55"), F(".15"))
        self.assertEqual(F(r["sigma330_nb"]), F(773, 1300))
        self.assertEqual(F(r["weight320"])+F(r["weight359"]), 1)
        self.assertEqual(F(r["stat_sd_min_rho_nb"]), F(157, 1950))  # 0.0805128205...
        self.assertEqual(F(r["stat_sd_max_rho_nb"]), F(307, 1950))  # 0.1574358974...
        self.assertAlmostEqual(float(r["stat_sd_independent_nb_approx"]),
                               0.12503674673546186, places=13)
        self.assertEqual(F(r["curvature_coefficient_MeV2"]), F(145))
        self.assertIsNone(r["curvature_bound_nb_per_MeV2"])
        self.assertEqual(F(r["sigma_times_pairK_nb_MeV"]),
                         F(773,1300)*(F(330)-Q))

    def test_outside_source_claim_blocked(self):
        r = linear_330_reported(F(".61"), F(".16"), F(".55"), F(".15"))
        self.assertEqual(r["status"], "MODEL_DEPENDENT_NOT_MEASURED")
        self.assertEqual(r["observable"], "SIG_reported_not_sigma_event")
        for key in ("kappa", "R_event", "heat_rate", "model_systematic_uncertainty"):
            self.assertIsNone(r[key])
        self.assertFalse(r["L4"])
        self.assertFalse(r["physical_activation"])
        self.assertEqual(r["production"], "HOLD")

    def test_modified_byte_atlas_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/"ATLAS.json"
            path.write_text('{"source":{"sha256":"not_original"}}\n')
            self.assertNotEqual(git_blob(path.read_bytes()), ATLAS_GIT_BLOB)
            with self.assertRaisesRegex(ValueError, "ATLAS_BYTE_IDENTITY_MISMATCH"):
                load_frozen_atlas(path)

    def test_threshold_recoil(self):
        self.assertEqual(Q, F("23.84647820"))
        self.assertEqual(E_THRESHOLD, Q+Q*Q/(2*M_ALPHA))
        self.assertGreater(E_THRESHOLD,Q)
        with self.assertRaisesRegex(ValueError, "BELOW_RECOIL"):
            pair_momentum_kernel(E_THRESHOLD-F("0.000001"),F(46))
        with self.assertRaisesRegex(ValueError, "INVALID_CM_ANGLE"):
            pair_momentum_kernel(F(330),F(181))

    def test_all_source_da_kinematic_conservation(self):
        for E,theta in DA_SOURCE_COORDS:
            for phi in (0, 37):
                inv = pair_invariants(F(E), F(theta), F(phi))
                self.assertEqual(inv["daughter_count"],2)
                self.assertLess(abs(inv["energy_minus_initial_MeV"]), mp.mpf("1e-65"))
                self.assertLess(abs(inv["kinetic_minus_E_minus_Q_MeV"]), mp.mpf("1e-65"))
                self.assertLess(max(map(abs, inv["momentum_minus_photon_pc_MeV"])),mp.mpf("1e-65"))
                self.assertLess(max(map(abs, inv["shell_residuals_MeV2"])),mp.mpf("1e-63"))

    def test_identical_d_exchange(self):
        plus,minus=pair_momentum_kernel(F(330),F(46),F(30))
        swap_plus,swap_minus=pair_momentum_kernel(F(330),F(134),F(210))
        for p, q in ((plus,swap_minus),(minus,swap_plus)):
            self.assertLess(abs(p[0]-q[0]),mp.mpf("1e-67"))
            for a,b in zip(p[1],q[1]):
                self.assertLess(abs(a-b),mp.mpf("1e-67"))

    def test_half_sphere_not_half_daughters(self):
        for theta in (0,46,90):
            inv=pair_invariants(F(330),F(theta))
            self.assertEqual(inv["daughter_count"],2)
        plus,minus=pair_momentum_kernel(F(330),F(90))
        self.assertLess(abs(plus[0]-minus[0]),mp.mpf("1e-67"))
        self.assertLess(abs(plus[1][0]+minus[1][0]),mp.mpf("1e-67"))


if __name__=="__main__":
    unittest.main()
