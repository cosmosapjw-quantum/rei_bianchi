import copy
import json
import hashlib
from pathlib import Path
import tempfile
import unittest

from rct_intake import validate, verify_saved

BASE = Path(__file__).parent
FILES = {
    "return": "publication/he_consumer_return/HE_F2_RCT_CONSUMER_RETURN.json",
    "providers": "publication/PROVIDER_SELECTION_RECORDS.json",
    "final": "evidence/FINAL_INTEGRATION.json",
    "e2": "evidence/INDEPENDENT_RESULT.json",
    "e2x": "evidence/FT03_INDEPENDENT_RESULT.json",
    "review": "review/POST_FT03_REVIEW.json",
    "theory": "theory/CONTRACT.json",
    "kf": "survey/thermal_rate_views/KF96_THERMAL_RATE_PACKET.json",
    "gm": "survey/thermal_rate_views/GM25_THERMAL_RATE_PACKET.json",
    "cases": "evidence/FT03_INDEPENDENT_CASES.json",
}

def fixture():
    return {k: json.loads((BASE / "consumer" / v).read_text()) for k, v in FILES.items()}


class IntakeTest(unittest.TestCase):
    def setUp(self):
        self.b = fixture()

    def rejects(self, section, keys, value):
        data = copy.deepcopy(self.b)
        target = data[section]
        for key in keys[:-1]:
            target = target[key]
        target[keys[-1]] = value
        with self.assertRaises(ValueError):
            validate(data)

    def test_delivered_contract_accepted_only_as_local_rhs(self):
        result = validate(self.b)
        self.assertIs(result["accepted"], True)
        self.assertEqual(result["scope"], "EXPLICIT_CONDITIONAL_LOCAL_RHS_ONLY")
        self.assertIs(result["physical_admission"], False)
        self.assertIs(result["time_integrator_admission"], False)

    def test_no_implicit_activation_or_source_sum(self):
        for key, value in [("default", "ON"), ("source_addition", True),
                           ("automatic_source_switch", True), ("physical_admission", True)]:
            with self.subTest(key=key):
                self.rejects("return", ["selection", key], value)

    def test_no_stepper_or_underflow_certificate(self):
        for key in ["production_HHe_stepper_RCT_integration", "production_FT03_stepper_RCT_integration",
                    "FT03_strict_underflow_representability_inherited_by_RCT"]:
            with self.subTest(key=key):
                self.rejects("return", ["implementation", key], True)

    def test_missing_moments_cannot_be_zero(self):
        for key in ["source_photon_moment", "source_heat_moment", "source_recoil_moment", "source_spectrum"]:
            with self.subTest(key=key):
                self.rejects("return", ["closure", key], 0)
        self.rejects("providers", ["records", 0, "energy_photon_closure", "source_heat_moment_eV"], 0)

    def test_count_packet_not_thermal_rate(self):
        self.rejects("kf", ["request", "quantity"], "event_count_coefficients")
        self.rejects("providers", ["records", 0, "observable_kind"], "event_count")

    def test_coefficient_units_and_source_bytes(self):
        self.rejects("providers", ["records", 0, "coefficient", "si_token"], "1e-14")
        self.rejects("providers", ["records", 0, "source_identity", "sha256"], "0" * 64)
        self.rejects("providers", ["records", 0, "units"], "m3 s-1")

    def test_duplicate_alternative_rejected(self):
        self.rejects("providers", ["records", 1], self.b["providers"]["records"][0])

    def test_density_and_electron_ledger(self):
        self.rejects("providers", ["records", 0, "separate_event_stoichiometry", "density_applied"], True)
        self.rejects("theory", ["reaction", "stoichiometry"], [-1, 1, 0, 1, -1, -1])

    def test_wrong_actual_ft03_adapter(self):
        self.rejects("return", ["implementation", "FT03_base_rhs"], "hhe_rhs(ft03.gas)")
        self.rejects("return", ["selection", "GM25_with_new_FT03"], "CLAMP")

    def test_final_binary_must_bind_both_oracles(self):
        self.rejects("e2x", ["native_binary_sha256"], "0" * 64)
        self.rejects("e2", ["oracle_sha256"], "0" * 64)

    def test_failed_numerical_evidence_not_reused(self):
        self.rejects("final", ["runs", 0, "exit_code"], 1)
        self.rejects("e2", ["failures"], ["failed"])
        self.rejects("e2x", ["status"], "FAIL")

    def test_historical_review_cannot_replace_ft03_delta(self):
        old = json.loads((BASE / "consumer/review/FINAL_REVIEW.json").read_text())
        self.rejects("review", ["schema"], old.get("schema"))
        self.rejects("review", ["source_identity_matches", 1, "sha256"], "0" * 64)
        self.rejects("review", ["open_blockers"], 1)

    def test_closure_class_and_photon_route_are_explicit(self):
        self.rejects("return", ["closure", "input_origin"], "PROVIDER_PREDICTED")
        self.rejects("return", ["closure", "primary_tracked_photon_injection"], [1, 0, 0])
        self.rejects("return", ["closure", "id"], "MONO_Q")

    def test_case_requires_positive_finite_explicit_scenario(self):
        for value in [None, 0, -1, float("inf"), float("nan")]:
            with self.subTest(value=value):
                self.rejects("cases", [0, "native", "mean_escaped_photon_energy_ev"], value)
        self.rejects("cases", [0, "mean_origin"], None)
        self.rejects("cases", [0, "native", "physical_admission"], True)

    def test_provider_physical_admission_remains_false(self):
        for key in ["consumer_admission", "physical_accuracy_certified", "baseline_global_rct_enabled",
                    "alternatives_are_additive"]:
            with self.subTest(key=key):
                self.rejects("providers", ["records", 0, key], True)

    def test_missing_or_corrupted_saved_input_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            record = [{"status": 200, "local_path": "input.json",
                       "sha256": hashlib.sha256(b"{}").hexdigest()}]
            with self.assertRaises(ValueError):
                verify_saved(base, record)
            (base / "input.json").write_bytes(b"{}")
            verify_saved(base, record)
            (base / "input.json").write_bytes(b"{\"physical_admission\":true}")
            with self.assertRaises(ValueError):
                verify_saved(base, record)

    def test_missing_ft03_case_not_full_recorded_grid(self):
        self.rejects("cases", [0, "native", "ok"], False)
        b = fixture()
        b["cases"] = []
        with self.assertRaises(ValueError):
            validate(b)


if __name__ == "__main__":
    unittest.main()
