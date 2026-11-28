import copy
import json
from pathlib import Path
import unittest

from mixed_intake import validate

BASE = Path(__file__).resolve().parent / "inputs"
MIXED = BASE / "loop1/he_mixed"


def bundle():
    def read(path):
        return json.loads(path.read_text())
    return [read(MIXED / "EXECUTION_CONTRACT.json"), read(MIXED / "NATIVE_RESULT.json"),
            read(MIXED / "EXECUTION_LOG.json"), (MIXED / "NATIVE_MIXED.stdout").read_text(),
            read(MIXED / "NATIVE_COMPARISONS.json"), read(BASE / "review/LOOP1_REVIEW.json")]


class ReceiptBoundary(unittest.TestCase):
    def test_delivered_finite_gate(self):
        r = validate(*bundle())
        self.assertEqual(r["comparisons"], 274)
        self.assertFalse(r["physical_admission"])
        self.assertFalse(r["history_admission"])

    def reject(self, mutate):
        b = copy.deepcopy(bundle())
        mutate(b)
        with self.assertRaises(ValueError):
            validate(*b)

    def test_widened_tolerance(self):
        self.reject(lambda b: b[0].update(relative_tolerance=2e-12))

    def test_bool_not_numeric_tolerance(self):
        self.reject(lambda b: b[0].update(absolute_tolerance=False))

    def test_nonzero_exit(self):
        self.reject(lambda b: b[2]["commands"][-1].update(exit_code=1))

    def test_missing_row(self):
        self.reject(lambda b: b[4].pop())

    def test_missing_raw_row(self):
        self.reject(lambda b: b.__setitem__(3, b[3].replace("FLRW02_RESIDUAL", "OMITTED", 1)))

    def test_forged_metrics(self):
        self.reject(lambda b: b[4][1].update(absolute=0.0))

    def test_nonfinite_raw_value(self):
        self.reject(lambda b: b.__setitem__(3, b[3].replace("lhs=1.3396010875814407e-16", "lhs=NaN", 1)))

    def test_outside_tolerance_even_with_consistent_metrics(self):
        def mutate(b):
            b[3] = b[3].replace(
                "FLRW02_RESIDUAL absolute=0e0 relative=0e0 lhs=1.3396010875814407e-16 rhs=1.3396010875814407e-16",
                "FLRW02_RESIDUAL absolute=1e0 relative=5e-1 lhs=1e0 rhs=2e0", 1)
            b[4][0].update(absolute=1.0, relative=0.5, lhs=1.0, rhs=2.0)
        self.reject(mutate)

    def test_false_acceptance(self):
        self.reject(lambda b: b[4][0].update(acceptance=False))

    def test_result_promotes_physics(self):
        self.reject(lambda b: b[1].update(source_physical_admission=True))

    def test_result_promotes_history(self):
        self.reject(lambda b: b[1].update(history_admission=True))

    def test_different_review_pin(self):
        self.reject(lambda b: b[5]["decisions"][-1].update(native_commit="0"*40))

    def test_unconfirmed_review(self):
        self.reject(lambda b: b[5].update(status="PENDING"))

    def test_changed_test_identity(self):
        self.reject(lambda b: b[0].update(test_sha256="0"*64))


if __name__ == "__main__":
    unittest.main(verbosity=2)
