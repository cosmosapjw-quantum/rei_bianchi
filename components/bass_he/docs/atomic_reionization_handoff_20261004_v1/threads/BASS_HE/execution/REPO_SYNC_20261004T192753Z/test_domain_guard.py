import copy
import json
from pathlib import Path
import unittest

from domain_guard import validate_gate

GATE = Path(__file__).parents[2] / "runs/HE-F2C_20261005/HE_F3_DOMAIN_GATE.json"


class DomainIntakeTests(unittest.TestCase):
    def setUp(self):
        self.gate = json.loads(GATE.read_text())

    def test_actual_empty_intersection_retains_wait_and_hold(self):
        result = validate_gate(self.gate)
        self.assertIsNone(result["paired_domain"])
        self.assertEqual(result["status"], "WAIT_REI_F09_RESULT")
        self.assertIs(result["physical_admission"], False)

    def test_null_is_empty_not_missing(self):
        self.gate.pop("intersection_FT03_pair_K")
        with self.assertRaises(ValueError):
            validate_gate(self.gate)

    def test_claimed_intersections_must_match_source_windows(self):
        for key, value in [("intersection_FT03_GM25_K", [30000, 10000]),
                           ("intersection_FT03_pair_K", [30000, 110000]),
                           ("intersection_FT03_KF96_K", None),
                           ("pair_common_domain_K", [200, 10000])]:
            with self.subTest(key=key):
                gate = copy.deepcopy(self.gate)
                gate[key] = value
                with self.assertRaises(ValueError):
                    validate_gate(gate)

    def test_source_window_cannot_be_extended_by_gate(self):
        self.gate["GM25_domain_K"] = [200, 110000]
        with self.assertRaises(ValueError):
            validate_gate(self.gate)

    def test_ft03_guard_cannot_be_lowered_for_pair(self):
        self.gate["active_FT03_domain_K"] = [1000, 110000]
        with self.assertRaises(ValueError):
            validate_gate(self.gate)

    def test_off_kf96_is_not_paired_completion(self):
        self.gate["status"] = "COMPLETE"
        with self.assertRaises(ValueError):
            validate_gate(self.gate)

    def test_changed_model_requires_new_intake(self):
        self.gate["active_FT03_model"] = "SYNTHETIC_HHE"
        with self.assertRaises(ValueError):
            validate_gate(self.gate)


if __name__ == "__main__":
    unittest.main()
