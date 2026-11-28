"""Independent exact checks of PHYS73 continuum source-budget assembly."""
from fractions import Fraction as Q
from math import comb, factorial
from pathlib import Path
import importlib.util
import sys
import tempfile
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "implementation" / "source_budget.py"
spec = importlib.util.spec_from_file_location("phys73_source_budget_tests", MODULE_PATH)
budget = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = budget
spec.loader.exec_module(budget)


def exact(record):
    return Q(int(record["numerator"]), int(record["denominator"]))


class SourceBudgetChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.default = budget.source_budget(64, "44", 1)

    def test_moment_from_binomial_gamma_integrals(self):
        # Independent polynomial construction: integral t^n exp(-6t)=n!/6^(n+1).
        for radius in (Q(27), Q(44), Q(109, 3)):
            direct = sum(Q(comb(4, j) * factorial(j), 6**(j + 1))
                         * radius**(4 - j) for j in range(5))
            self.assertEqual(budget.moment4(radius), direct)

    def test_ellipse_geometry_and_growth(self):
        shift, axis, B = Q(7, 10), Q(65, 16), Q(27)
        s2 = B*B + shift*shift - 2*B*shift*axis
        self.assertEqual(s2, Q(230371, 400))
        self.assertEqual(s2 - 23**2, Q(18771, 400))
        self.assertGreater(B - shift*axis, 0)
        self.assertEqual((B-shift*axis)**2 - s2, shift**2*(axis**2-1))
        self.assertGreater(shift**2*(axis**2-1), 0)

    def test_positive_taylor_envelope_direction(self):
        partial = sum(Q(46)**n / factorial(n) for n in range(129))
        self.assertEqual(partial, budget.positive_taylor(Q(46)))
        self.assertLess(Q(48, 23) / partial, Q(3, 10**20))
        self.assertEqual(budget.exp_negative_upper(Q(0)), 1)
        self.assertLess(budget.exp_negative_upper(Q(54)), 1)

    def test_square_root_bounds_are_outward(self):
        bounds = self.default["bounds"]
        for stem in ("source_Xplus", "b0_L2", "radial_omitted_source_Xplus",
                     "angular_omitted_source_Xplus"):
            root = exact(bounds[stem + "_upper"])
            sq = exact(bounds[stem + "_squared_upper"])
            self.assertGreaterEqual(root*root, sq)
        for x in (Q(0), Q(1, 3), Q(10)**-499, Q(10)**70 + Q(1, 7)):
            self.assertGreaterEqual(budget.sqrt_upper(x)**2, x)

    def test_angular_tail_is_unbounded_space_geometric_bound(self):
        d65 = budget.source_budget(65, "44", 1)
        a64 = exact(self.default["bounds"]["angular_omitted_source_Xplus_squared_upper"])
        a65 = exact(d65["bounds"]["angular_omitted_source_Xplus_squared_upper"])
        self.assertEqual(a64, 64*a65)
        p72 = budget._authority()
        self.assertGreater(p72.c_j(10000), p72.c_j(64))

    def test_radial_tail_decreases_at_larger_radius(self):
        d45 = budget.source_budget(64, "45", 1)
        key = "radial_omitted_source_Xplus_squared_upper"
        self.assertLess(exact(d45["bounds"][key]), exact(self.default["bounds"][key]))

    def test_source_born_terms_start_with_R0_f(self):
        second = budget.source_budget(64, "44", 2)
        q = exact(self.default["inherited"]["q_upper"])
        key = "born_tail_after_N_Xminus_upper"
        self.assertEqual(exact(second["bounds"][key]), q*exact(self.default["bounds"][key]))
        c = exact(self.default["inherited"]["C_R_upper"])
        M = exact(self.default["inherited"]["M_upper"])
        self.assertEqual(q, c*M)

    def test_assembled_components_and_upward_displays(self):
        d = self.default
        b = d["bounds"]
        total = exact(b["born_tail_after_N_Xminus_upper"]) + exact(b["source_omission_solution_Xminus_upper"])
        self.assertEqual(total, exact(b["analytic_components_Xminus_upper"]))
        for v in b.values():
            self.assertGreaterEqual(Q(v["upper_decimal"]), exact(v))
        self.assertLess(total, Q("4.918263356868373e-53"))

    def test_empty_radial_interval_has_conservative_bound(self):
        empty = budget.source_budget(0, "27", 1)
        b = empty["bounds"]
        self.assertGreaterEqual(exact(b["analytic_components_Xminus_upper"]),
                                exact(b["solution_Xminus_upper"]))

    def test_does_not_certify_grid_or_matched_boundary(self):
        d = self.default
        self.assertFalse(d["finite_grid_certified"])
        self.assertFalse(d["input_identity"]["frozen_npz_used_as_exterior_source"])
        self.assertEqual(d["HH_R10"], "OFF")
        self.assertIn("X_plus", d["source_space"])
        self.assertIn("X_minus", d["solution_space"])
        self.assertTrue(d["remaining_numerical_obligations"])

    def test_bad_contract_inputs_and_stale_authority_rejected(self):
        for args in ((True, "44", 1), (-1, "44", 1), (64, 44.0, 1),
                     (64, "26", 1), (64, "257", 1), (64, "44", 0),
                     (64, "NaN", 1), (64, "44", True)):
            with self.assertRaises((TypeError, ValueError)):
                budget.source_budget(*args)
        original = budget.PHYS72_PATH
        with tempfile.TemporaryDirectory() as tmp:
            forged = Path(tmp) / "bounds.py"
            forged.write_text("# mismatched scalar authority\n", encoding="utf-8")
            try:
                budget.PHYS72_PATH = forged
                with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                    budget.source_budget()
            finally:
                budget.PHYS72_PATH = original

    def test_cli_create_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "budget.json"
            out.write_text("existing evidence\n", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                budget.main(["--out", str(out)])
            self.assertEqual(out.read_text(), "existing evidence\n")


if __name__ == "__main__":
    unittest.main()
