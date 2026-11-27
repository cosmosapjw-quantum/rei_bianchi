"""Manufactured large-R continuation/parity values; no physical evaluations."""
import copy
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
import continuation_audit as ca


def overlap(left, right, sector, order, mean=.9, direction=0., norm_left=1., norm_right=1.):
    a, b = mean + direction / 2, mean - direction / 2
    mean = (a + b) / 2
    return {"R_left": left, "R_right": right, "m": sector, "order": order,
            "overlap": mean, "normalized_overlap": mean / math.sqrt(norm_left * norm_right),
            "left_domain_overlap": a, "right_domain_overlap": b,
            "directional_difference_abs": abs(a - b), "self_norm_left": norm_left,
            "self_norm_right": norm_right,
            "max_self_norm_error_abs": max(abs(norm_left - 1), abs(norm_right - 1)),
            "phase_factor_suggestion": 1 if mean >= 0 else -1}


class ContinuationTests(unittest.TestCase):
    def setUp(self):
        self.cfg = json.loads((ROOT / "CONTRACT.json").read_text())

    def records(self):
        return {f"{i}_{m}_{q}": overlap(a, b, m, q)
                for i, (a, b) in enumerate(self.cfg["continuation"]["edges"])
                for m in (0, 1) for q in (16, 24, 32)}

    def parity(self):
        direct = dict(zip(ca.DIRECT_KEYS, [1., -.01, .8, .2, 1., 1.]))
        force = dict(zip(ca.FORCE_KEYS, [1., -.01, .9, .901, 3.]))
        return {"0": dict(direct), "1": dict(direct), "2": force,
                "3": overlap(62, 64, 0, 24)}

    def test_full_48_group_chain_and_exact_parity(self):
        result = ca.continuation_audit(self.records(), self.cfg)
        self.assertTrue(result["pass"], result)
        self.assertEqual(result["edge_sector_count"], 48)
        self.assertEqual(result["evaluation_count"], 144)
        self.assertEqual([r["factor"] for r in result["coupling_phase"]], [1] * 25)
        values = self.parity()
        self.assertTrue(ca.parity_audit(values, copy.deepcopy(values), self.cfg)["pass"])

    def test_large_R_scales_and_independent_thresholds(self):
        actual, reference = self.parity(), self.parity()
        actual["1"]["L_O_bar"] += 4e-12
        actual["1"]["L_B_bar"] += 4e-12
        result = ca.parity_audit(actual, reference, self.cfg)
        row = result["rows"][1]
        self.assertTrue(row["gates"]["physical_quantities_raw"])
        self.assertTrue(row["gates"]["Q_O_scaled"])
        self.assertFalse(row["gates"]["Q_B_scaled"])
        self.assertEqual(row["Q_O_delta_abs"], abs(actual["1"]["L_O_bar"] - 1.) / 64)
        self.assertEqual(row["Q_B_delta_abs"], abs(actual["1"]["L_B_bar"] + .01) * 64**2)
        cfg = copy.deepcopy(self.cfg)
        cfg["scaled_criteria"]["Q_O_native_parity_abs"] = 1e-14
        cfg["scaled_criteria"]["Q_B_native_parity_abs"] = 1e-2
        row = ca.parity_audit(actual, reference, cfg)["rows"][1]
        self.assertFalse(row["gates"]["Q_O_scaled"])
        self.assertTrue(row["gates"]["Q_B_scaled"])

    def test_force_scales_and_all_raw_quantities_retained(self):
        actual, reference = self.parity(), self.parity()
        actual["2"]["L_B_bar"] += 4e-12
        row = ca.parity_audit(actual, reference, self.cfg)["rows"][2]
        self.assertFalse(row["gates"]["Q_B_scaled"])
        self.assertEqual(set(row["quantity_deltas_abs"]), set(ca.FORCE_KEYS))
        actual["2"]["T_A"] += 2e-11
        self.assertFalse(ca.parity_audit(actual, reference, self.cfg)["rows"][2]["gates"]["physical_quantities_raw"])

    def test_two_increments_and_failed_group_only_fallback(self):
        records = self.records()
        records["0_0_48"] = overlap(16, 18, 0, 48)
        self.assertFalse(ca.continuation_audit(records, self.cfg)["input_valid"])
        records["0_0_16"] = overlap(16, 18, 0, 16, mean=.8)
        records["0_0_64"] = overlap(16, 18, 0, 64)
        result = ca.continuation_audit(records, self.cfg)
        self.assertTrue(result["pass"], result)
        self.assertEqual(result["rows"][0]["terminal_orders"], [32, 48, 64])
        self.assertEqual(len(result["rows"][0]["quadrature_increments_abs"]), 2)
        self.assertFalse(result["rows"][0]["initial_audit"]["pass"])
        del records["0_0_48"]
        self.assertFalse(ca.continuation_audit(records, self.cfg)["input_valid"])

    def test_both_domains_self_norm_and_cache_consistency(self):
        records = self.records()
        records["0_0_16"] = overlap(16, 18, 0, 16, direction=2e-7)
        row = ca.continuation_audit(records, self.cfg)["rows"][0]
        self.assertFalse(row["gates"]["three_directional_checks"])
        self.assertEqual(row["quadrature_increments_abs"][1], 0.)
        records["0_0_16"] = overlap(16, 18, 0, 16, norm_left=1+2e-7)
        self.assertFalse(ca.continuation_audit(records, self.cfg)["pass"])
        records["0_0_16"]["max_self_norm_error_abs"] = 0.
        self.assertFalse(ca.continuation_audit(records, self.cfg)["input_valid"])

    def test_phase_chain_stops_at_unresolved_step(self):
        records = self.records()
        for q in (16, 24, 32):
            records[f"0_0_{q}"] = overlap(16, 18, 0, q, mean=-.9)
            records[f"1_0_{q}"] = overlap(18, 20, 0, q, mean=.4)
        result = ca.continuation_audit(records, self.cfg)
        chain = result["phase_chains"]["0"]
        self.assertEqual([r["phase"] for r in chain[:3]], [1, -1, None])
        self.assertTrue(all(r["phase"] is None for r in chain[2:]))

    def test_malformed_and_wrong_metadata_fail_closed(self):
        records = self.records()
        del records["0_0_16"]
        self.assertFalse(ca.continuation_audit(records, self.cfg)["input_valid"])
        records = self.records()
        records["duplicate"] = copy.deepcopy(records["0_0_16"])
        self.assertFalse(ca.continuation_audit(records, self.cfg)["input_valid"])
        actual, reference = self.parity(), self.parity()
        actual["3"]["order"] = 32
        self.assertFalse(ca.parity_audit(actual, reference, self.cfg)["rows"][3]["gates"]["case_metadata"])
        actual["0"]["L_O_bar"] = math.nan
        self.assertFalse(ca.parity_audit(actual, reference, self.cfg)["input_valid"])


if __name__ == "__main__":
    unittest.main()
