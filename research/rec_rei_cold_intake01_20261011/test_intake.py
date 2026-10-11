"""Negative tests against saved campaign outputs; no repeated native campaign."""
import copy
import json
import unittest
import intake

class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.rows = json.loads((intake.HERE / "evidence/RESULTS.json").read_text())

    def test_source_mismatch(self):
        with self.assertRaisesRegex(ValueError, "SOURCE_BYTE_MISMATCH"):
            intake.verify_bytes(b"changed", intake.PINS["inputs/baseline.json"])

    def test_wrong_units(self):
        self.rows[0]["density_units"] = "cm-3"
        with self.assertRaisesRegex(ValueError, "DENSITY_UNITS"):
            intake.validate(self.rows)

    def test_wrong_conversion(self):
        self.rows[0]["consumer"]["nH_cm3"] *= 1e6
        with self.assertRaisesRegex(ValueError, "nH_cm3_DECIMAL80"):
            intake.validate(self.rows)

    def test_Tm_Tgamma_confusion(self):
        self.rows[0]["consumer"]["Tm_roundtrip_K"] = self.rows[0]["saved_endpoint"]["Tgamma_K"]
        with self.assertRaisesRegex(ValueError, "Tm_roundtrip_K_DECIMAL80"):
            intake.validate(self.rows)

    def test_helium_loss(self):
        self.rows[0]["consumer"]["species_m3"][10] = 0.0
        with self.assertRaisesRegex(ValueError, "species_10_DECIMAL80"):
            intake.validate(self.rows)

    def test_xe_to_Q(self):
        self.rows[0]["consumer"]["QHII"] = self.rows[0]["saved_endpoint"]["xe_per_H"]
        with self.assertRaisesRegex(ValueError, "XE_IS_NOT_QHII"):
            intake.validate(self.rows)

    def test_provider_reject_required(self):
        self.rows[0]["consumer"]["provider"] = {"status": "AVAILABLE", "value": 0.0}
        with self.assertRaisesRegex(ValueError, "PROVIDER_REJECT"):
            intake.validate(self.rows)

    def test_positive_saved_rows(self):
        self.assertEqual(intake.validate(self.rows)["intake"], "PASS_SCOPED")

if __name__ == "__main__":
    unittest.main()
