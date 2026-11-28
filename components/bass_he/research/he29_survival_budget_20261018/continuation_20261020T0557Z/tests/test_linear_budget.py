"""New manufactured algebra checks only; no old campaign or solver is executed."""
import itertools
import math
from pathlib import Path
import sys
import unittest
from fractions import Fraction as F

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from linear_budget import LinearForm as L, Hull, exact, outward, project


class LinearBudgetTests(unittest.TestCase):
    def test_shared_reference_cancellation_needs_no_candidates(self):
        a, b = L.reference("r2"), L.reference("r4")
        expression = (b - a) + (L(9) - b) - (L(8) - a)
        self.assertEqual(expression, L(1))
        self.assertEqual(expression.product_hull({}).as_dict()["exact_width"], "0")
        closure = expression - (L(9) - L(8))
        self.assertEqual(closure, L(0))
        self.assertEqual(project(closure, {})["product_hull"]["display_width"], 0.0)

    def test_repeated_key_coefficients_merge_before_range(self):
        f = L(F(1, 3), (("shared", 2), ("other", 0), ("shared", -2)))
        self.assertEqual(f.terms, ())
        display = f.product_hull({}).as_dict()
        self.assertEqual(display["exact_width"], "0")
        self.assertGreater(display["display_width"], 0)
        self.assertLessEqual(F.from_float(display["lower_float"]), F(1, 3))
        self.assertGreaterEqual(F.from_float(display["upper_float"]), F(1, 3))

    def test_product_and_coherent_are_different_selection_sets(self):
        f = L.reference("b") - L.reference("a")
        candidates = {"a": {"Radau": 1, "DOP853": 2},
                      "b": {"Radau": 11, "DOP853": 12}}
        self.assertEqual((f.product_hull(candidates).lower, f.product_hull(candidates).upper), (9, 11))
        self.assertEqual((f.coherent_hull(candidates).lower, f.coherent_hull(candidates).upper), (10, 10))
        self.assertEqual(f.product_hull(candidates).choices, 4)
        self.assertEqual(f.coherent_hull(candidates).choices, 2)

    def test_product_extrema_match_independent_corner_enumeration(self):
        candidates = {"a": {"Radau": F(1, 3), "DOP853": F(5, 7)},
                      "b": {"Radau": F(-9, 5), "DOP853": F(2, 7)},
                      "c": {"Radau": F(11, 13), "DOP853": F(11, 13)}}
        for coefficients in ((-2, 3, 5), (0, -1, 2), (4, 0, 0), (0, 0, 0)):
            with self.subTest(coefficients=coefficients):
                f = L(F(17, 19), zip(candidates, coefficients))
                values = [F(17, 19) + sum((coef * x for coef, x in zip(coefficients, xs)), F(0))
                          for xs in itertools.product(*(row.values() for row in candidates.values()))]
                hull = f.product_hull(candidates)
                self.assertEqual((hull.lower, hull.upper), (min(values), max(values)))

    def test_coherent_projection_requires_a_common_method(self):
        f = L.reference("a") + L.reference("b")
        candidates = {"a": {"Radau": 1}, "b": {"DOP853": 2}}
        self.assertEqual(f.product_hull(candidates).lower, 3)
        with self.assertRaisesRegex(ValueError, "No common method"):
            f.coherent_hull(candidates)

    def test_float_inputs_are_converted_before_subtraction(self):
        a, b = 1.0, 2.0 ** -54
        required = exact(a) - exact(b)
        rounded_first = exact(a - b)
        self.assertNotEqual(required, rounded_first)
        self.assertEqual((L(a) - L(b)).constant, required)
        self.assertEqual(exact(0.1), F(3602879701896397, 36028797018963968))

    def test_directed_rounding_and_subnormal_endpoints(self):
        values = [F(0), F(1), F(-1), F(1, 3), F(-1, 3),
                  F(1, 2 ** 1075), F(-1, 2 ** 1075),
                  F.from_float(math.nextafter(1., math.inf))]
        for q in values:
            with self.subTest(value=q):
                lo, hi = outward(q, -1), outward(q, 1)
                self.assertLessEqual(F.from_float(lo), q)
                self.assertGreaterEqual(F.from_float(hi), q)
                if lo != hi:
                    self.assertEqual(math.nextafter(lo, math.inf), hi)
        self.assertEqual(outward(0, -1), 0.)
        self.assertEqual(outward(1, 1), 1.)

    def test_canonical_serialization_and_nonlinear_rejection(self):
        f = 3 * (L.reference("b") - L.reference("a")) + 7
        self.assertEqual(list(f.as_dict()["coefficients"]), ["a", "b"])
        self.assertEqual(f.evaluate({"a": 2, "b": 5}), 16)
        with self.assertRaises(ValueError):
            f * L.reference("a")

    def test_invalid_inputs_and_missing_candidates_fail_explicitly(self):
        for value in (float("nan"), float("inf"), float("-inf"), "1.0", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                exact(value)
        with self.assertRaises(TypeError):
            exact(True)
        with self.assertRaises(ValueError):
            L.reference("")
        with self.assertRaises(ValueError):
            L.reference("a").product_hull({"a": {}})
        with self.assertRaises(ValueError):
            L.reference("a").product_hull({})

    def test_overflow_retains_exact_range_without_nonfinite_json(self):
        h = Hull(F(10 ** 400), F(10 ** 400) + 1, 2, "manufactured")
        d = h.as_dict()
        self.assertEqual(d["exact_width"], "1")
        self.assertIsNone(d["lower_float"])
        self.assertEqual(d["display_status"], "OUTSIDE_FINITE_BINARY64")
        self.assertFalse(d["true_solution_error_bound"])


if __name__ == "__main__":
    unittest.main()
