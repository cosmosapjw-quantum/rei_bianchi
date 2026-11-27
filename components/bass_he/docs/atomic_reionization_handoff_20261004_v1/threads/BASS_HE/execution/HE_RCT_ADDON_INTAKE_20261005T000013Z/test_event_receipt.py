import copy
import json
from pathlib import Path
import unittest
from event_receipt import audit, audit_static_scope

BASE = Path(__file__).resolve().parent / "inputs"


def bundle():
    def read(name):
        return json.loads((BASE / name).read_text())
    rows = [json.loads(line) for line in (BASE / "archive/evidence/STEP_PROBE.jsonl").read_text().splitlines()]
    return [read("published/NUMERICAL_CONTRACT.json"), read("published/RETURN.json"),
            rows, read("archive/evidence/INDEPENDENT_ENDPOINT_RESULTS.json")]


class EventReceiptBoundary(unittest.TestCase):
    def test_supplied_cases_and_unadopted_budget(self):
        result = audit(*bundle())
        self.assertEqual((result["accepted"], result["rejected"]), (6, 6))
        self.assertFalse(result["production_budget_adopted"])
        case = result["cases"][7]
        self.assertLess(case["state_error_reported"], 2e-4)
        self.assertGreater(case["event_budget_ratio"], 2)
        self.assertEqual(case["status"], "RCT_EVENT_LOCAL_ERROR")

    def reject(self, mutate):
        values = copy.deepcopy(bundle())
        mutate(values)
        with self.assertRaises(ValueError):
            audit(*values)

    def test_state_pass_cannot_override_event_rejection(self):
        self.reject(lambda b: b[2][8].update(status="ACCEPT"))

    def test_widened_event_budget(self):
        self.reject(lambda b: b[0]["event_error"].update(example_absolute_per_h=1e-10))

    def test_implicit_caller_budget(self):
        self.reject(lambda b: b[0]["event_error"].update(required_caller_input=False))

    def test_physical_admission(self):
        self.reject(lambda b: b[1].update(physical_admission=True))

    def test_owner_adoption_not_inferred(self):
        self.reject(lambda b: b[0]["event_error"].update(strict_owner_adoption=True))

    def test_nonfinite_event(self):
        self.reject(lambda b: b[2][1].update(J_full=float("nan")))

    def test_zero_hydrogen_density(self):
        self.reject(lambda b: b[2][0].update(nh=0.0))

    def test_static_estimator_cannot_be_certified_as_flow_bound(self):
        root = BASE / "late_static"
        summary = json.loads((root / "RESULT_SUMMARY.json").read_text())
        receipt = json.loads((root / "RETURN.json").read_text())
        self.assertFalse(audit_static_scope(summary, receipt)["sum_estimator_certified_flow_bound"])
        summary["sum_estimator_is_certified_bound"] = True
        with self.assertRaises(ValueError):
            audit_static_scope(summary, receipt)

    def test_direct_zero_electron_term_does_not_erase_feedback(self):
        root = BASE / "late_static"
        summary = json.loads((root / "RESULT_SUMMARY.json").read_text())
        receipt = json.loads((root / "RETURN.json").read_text())
        self.assertLess(audit_static_scope(summary, receipt)["electron_feedback_reported"], 0)
        summary["ON_OFF_electron_delta_per_H"] = "0"
        with self.assertRaises(ValueError):
            audit_static_scope(summary, receipt)


if __name__ == "__main__":
    unittest.main(verbosity=2)
