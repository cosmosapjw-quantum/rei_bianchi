"""New PHYS72 exact-arithmetic contracts; no legacy campaign is executed."""

from contextlib import redirect_stdout
from decimal import Decimal
from fractions import Fraction
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "bounds.py"
SPEC = importlib.util.spec_from_file_location("phys72_exact_bounds", MODULE_PATH)
bounds = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = bounds
SPEC.loader.exec_module(bounds)


def from_record(record):
    return Fraction(int(record["numerator"]), int(record["denominator"]))


class ExactBoundContracts(unittest.TestCase):
    def test_positive_quadratic_witness_and_root_bracket(self):
        # Polynomial B*x^2 - 2*x/k - 1 has one positive root.  Exact signs
        # bracket that root independently of evaluating its square root.
        self.assertGreater(bounds.resolvent_quadratic_witness(), 0)
        self.assertLess(bounds.resolvent_quadratic_witness("1/4"), 0)
        self.assertEqual(
            bounds.resolvent_quadratic_witness(),
            Fraction(27) * Fraction(253, 1000) ** 2
            - Fraction(20, 7) * Fraction(253, 1000) - 1,
        )

    def test_fixed_q_and_sufficient_radius_exact(self):
        self.assertEqual(bounds.Q_UPPER, Fraction("5.53311e-21"))
        self.assertEqual(bounds.Q_UPPER, Fraction(553311, 10**26))
        self.assertEqual(bounds.V_WEIGHTED_UPPER, Fraction(2187, 10**23))
        self.assertEqual(bounds.GAMMA_EXTERNAL, bounds.c_j(21) * bounds.c_j(20))
        self.assertEqual((1 / bounds.Q_UPPER) * bounds.Q_UPPER, 1)

    def test_geometric_remainder_formula_and_first_omitted_power(self):
        lam = Fraction(3, 2)
        q = bounds.Q_UPPER
        for n in (1, 2, 3, 5):
            result = bounds.born_remainder_bound(n, lam)
            independently = bounds.GAMMA_EXTERNAL * bounds.DELTA / 2
            independently *= lam ** (n + 1) * q**n / (1 - lam * q)
            self.assertEqual(result.remainder_upper, independently)
            self.assertEqual(result.as_dict()["first_omitted_power"], n + 1)
        a = bounds.born_remainder_bound(3).remainder_upper
        b = bounds.born_remainder_bound(4).remainder_upper
        self.assertEqual(b, a * q)
        self.assertLess(b, a)

    def test_zero_lambda_gives_exact_zero_for_every_positive_order(self):
        for n in (1, 3, 25):
            result = bounds.born_remainder_bound(n, "0")
            self.assertEqual(result.remainder_upper, 0)
            self.assertEqual(result.status, "SUFFICIENT_CONDITION_MET")
        found = bounds.minimum_terms(0, lambda_abs=0)
        self.assertEqual(found["minimum_terms"], 1)

    def test_critical_lambda_has_strict_condition_and_no_divergence_claim(self):
        critical = 1 / bounds.Q_UPPER
        for lam in (critical, critical + 1):
            result = bounds.born_remainder_bound(3, lam)
            self.assertIsNone(result.remainder_upper)
            self.assertEqual(result.status, "SUFFICIENT_CONDITION_NOT_MET")
            self.assertIn("does not decide", result.as_dict()["interpretation"])
        below = bounds.born_remainder_bound(3, critical - 1)
        self.assertIsNotNone(below.remainder_upper)

    def test_decimal_display_is_outward_including_tiny_rationals(self):
        values = [Fraction(0), Fraction(1, 3), Fraction(1, 7), Fraction(5, 2),
                  Fraction(10**150 + 3, 10**220 + 7),
                  bounds.born_remainder_bound(3).remainder_upper]
        for value in values:
            for digits in (1, 7, 40):
                shown = Fraction(Decimal(bounds.upward_decimal(value, digits)))
                self.assertGreaterEqual(shown, value)
        self.assertEqual(bounds.upward_decimal("2.5", 2), "2.5E+0")

    def test_fraction_serialization_roundtrip_and_no_float_json(self):
        obj = bounds.report(budget="1e-78")
        self.assertEqual(from_record(obj["constants"]["q_upper"]), bounds.Q_UPPER)
        self.assertEqual(obj["term_budget"]["minimum_terms"], 3)
        self.assertLess(bounds.born_remainder_bound(3).remainder_upper, Fraction("1e-78"))
        self.assertGreater(bounds.born_remainder_bound(2).remainder_upper, Fraction("1e-78"))
        def walk(value):
            self.assertNotIsInstance(value, float)
            if isinstance(value, dict):
                for child in value.values(): walk(child)
            if isinstance(value, list):
                for child in value: walk(child)
        walk(obj)
        json.dumps(obj)

    def test_large_exact_denominator_serialization_preserves_digit_limit(self):
        original_limit = sys.get_int_max_str_digits()
        exact = Fraction(1, 10**5000 + 3)
        obj = bounds.rational_record(exact)
        rebuilt = Fraction(Decimal(obj["numerator"])) / Fraction(Decimal(obj["denominator"]))
        self.assertEqual(rebuilt, exact)
        self.assertGreaterEqual(Fraction(Decimal(obj["upper_decimal"])), exact)
        self.assertEqual(sys.get_int_max_str_digits(), original_limit)

    def test_minimum_budget_inclusive_equality_and_guard(self):
        third = bounds.born_remainder_bound(3).remainder_upper
        self.assertEqual(bounds.minimum_terms(third)["minimum_terms"], 3)
        self.assertEqual(bounds.minimum_terms(third / 2)["minimum_terms"], 4)
        limited = bounds.minimum_terms(third / 2, max_terms=3)
        self.assertEqual(limited["status"], "TERM_SEARCH_LIMIT_REACHED")
        self.assertIsNone(limited["minimum_terms"])
        self.assertEqual(from_record(limited["last_bound"]["remainder_upper"]), third)
        zero = bounds.minimum_terms(0)
        self.assertEqual(zero["status"], "ZERO_BUDGET_NO_FINITE_CERTIFIED_TERM_COUNT")
        failed = bounds.minimum_terms(1, lambda_abs=1 / bounds.Q_UPPER)
        self.assertEqual(failed["status"], "SUFFICIENT_CONDITION_NOT_MET")

    def test_defect_is_same_space_exact_resolvent_error(self):
        rho = Fraction(7, 1000)
        result = bounds.defect_bound(rho)
        self.assertEqual(from_record(result["error_upper"]), rho / (1 - bounds.Q_UPPER))
        self.assertIn("Birman-Schwinger", result["norm_space"])
        result = bounds.defect_bound(rho, 1 / bounds.Q_UPPER)
        self.assertIsNone(result["error_upper"])
        self.assertEqual(result["status"], "SUFFICIENT_CONDITION_NOT_MET")

    def test_angular_weights_continue_to_grow_without_cutoff(self):
        self.assertEqual(bounds.c_j(0), 77)
        self.assertEqual(bounds.c_j(28), 77)
        self.assertEqual(bounds.c_j(29), Fraction(24000, 189))
        self.assertEqual(bounds.c_j(1000000), Fraction(800000800, 189))
        self.assertGreater(bounds.c_j(1000), bounds.c_j(64))
        self.assertEqual(bounds.c_j(1000) / bounds.c_j(999), Fraction(1001, 1000))
        self.assertFalse(bounds.report()["angular_space"]["finite_L_Gamma_replacement"])

    def test_invalid_numeric_inputs_fail_before_any_claim(self):
        for value in (-1, "-1/2", "NaN", "Infinity", "1/0", "not a number"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError): bounds.born_remainder_bound(3, value)
        for value in (1.0, True, None, complex(1)):
            with self.assertRaises(TypeError): bounds.born_remainder_bound(3, value)
        for value in (0, -1, True, 1.5):
            with self.assertRaises(ValueError): bounds.born_remainder_bound(value)
            with self.assertRaises(ValueError): bounds.minimum_terms(1, max_terms=value)
        for value in (-1, True, Fraction(2), 1.5):
            with self.assertRaises(ValueError): bounds.c_j(value)
        with self.assertRaises(ValueError): bounds.minimum_terms(-1)
        with self.assertRaises(ValueError): bounds.minimum_terms(1, max_terms=10001)
        with self.assertRaises(ValueError): bounds.upward_decimal(1, 0)

    def test_byte_identity_match_mismatch_and_readonly(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.bin"
            data = b"PHYS72 identity fixture\x00\x01"
            path.write_bytes(data)
            before = path.stat().st_mtime_ns
            digest = hashlib.sha256(data).hexdigest()
            self.assertEqual(bounds.verify_file_identity(path, digest)["status"], "MATCH")
            self.assertEqual(bounds.verify_file_identity(path, "0" * 64)["status"], "MISMATCH")
            self.assertEqual(path.read_bytes(), data)
            self.assertEqual(path.stat().st_mtime_ns, before)
            with self.assertRaises(ValueError): bounds.verify_file_identity(path, "bad")

    def test_cli_create_only_and_identity_failure_exit(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "new.json"
            self.assertEqual(bounds.main(["--output", str(output), "--budget", "1e-78"]), 0)
            before = output.read_bytes()
            self.assertEqual(json.loads(before)["HH_R10"], "OFF")
            with self.assertRaises(SystemExit): bounds.main(["--output", str(output)])
            self.assertEqual(output.read_bytes(), before)
            wrong = Path(directory) / "wrong.npz"
            wrong.write_bytes(b"wrong input")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = bounds.main(["--frozen-npz", str(wrong)])
            result = json.loads(stdout.getvalue())
            self.assertEqual(code, 2)
            self.assertEqual(result["adoption_status"], "BLOCKED_INPUT_IDENTITY_MISMATCH")


if __name__ == "__main__":
    unittest.main(verbosity=2)
