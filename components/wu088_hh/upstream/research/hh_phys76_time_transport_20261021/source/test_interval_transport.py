import copy
import unittest
from decimal import Decimal, DecimalException, localcontext, ROUND_DOWN

from interval_transport import propagate, _Arithmetic, _Interval


def witness(scope):
    return {"scope": scope, "source_identity": "manufactured-exact-constant-v1",
            "method": "explicit constant functions on the complete cell",
            "locator": "test_interval_transport.py"}


def cell(a=("2", "2"), pm=("3", "3"), pr=("-1", "-1"), h="0.25"):
    return {"h": h, "A": list(a), "P_m": list(pm), "P_r": list(pr),
            "witness": witness("entire_cell")}


def exact_constant(a, p, h, value="0"):
    """Separate 160-digit closed-form evaluation, not engine arithmetic."""
    with localcontext() as ctx:
        ctx.prec = 160
        a, p, h, value = map(Decimal, (a, p, h, value))
        if a == 0:
            return value + h*p
        e = (-a*h).exp()
        return e*value + (1-e)*p/a


class ConditionalIntervalTransportTests(unittest.TestCase):
    def check_contains(self, interval, value):
        lo, hi = map(Decimal, interval)
        self.assertLessEqual(lo, value)
        self.assertGreaterEqual(hi, value)

    def run_cells(self, cells, initial=("0", "0"), **kw):
        return propagate(cells, list(initial), witness("initial_value"), **kw)

    def test_exact_zero_damping_signed_sources(self):
        out = self.run_cells([cell(a=("0", "0"))], initial=("2", "2"))
        node = out["nodes"][-1]
        self.assertEqual(node["initial_memory"], ["2", "2"])
        self.assertEqual(node["matter_memory"], ["0.75", "0.75"])
        self.assertEqual(node["radiation_memory"], ["-0.25", "-0.25"])
        self.assertEqual(node["total_signed_shear"], ["2.50", "2.50"])

    def test_positive_negative_zero_and_small_constant_damping(self):
        for a in ("2", "-2", "0", "0.001", "-0.001", "1e-24", "-1e-24"):
            with self.subTest(a=a):
                out = self.run_cells([cell(a=(a, a))], initial=("1", "1"))
                node = out["nodes"][-1]
                self.check_contains(node["matter_memory"], exact_constant(a, "3", "0.25"))
                self.check_contains(node["radiation_memory"], exact_constant(a, "-1", "0.25"))
                self.check_contains(node["total_signed_shear"], exact_constant(a, "2", "0.25", "1"))

    def test_interval_corners_and_interior(self):
        out = self.run_cells([cell(a=("-1", "2"), pm=("-3", "4"), pr=("-2", "1"))],
                             initial=("-1", "2"))
        node = out["nodes"][-1]
        for a in ("-1", "0", "2"):
            for pm in ("-3", "0", "4"):
                for pr in ("-2", "0", "1"):
                    for s0 in ("-1", "0", "2"):
                        with localcontext() as ctx:
                            ctx.prec = 160
                            p = str(Decimal(pm)+Decimal(pr))
                        self.check_contains(node["total_signed_shear"], exact_constant(a, p, "0.25", s0))

    def test_two_piecewise_constant_cells(self):
        out = self.run_cells([cell(), cell(a=("-1", "-1"), pm=("-2", "-2"),
                                          pr=("4", "4"), h="0.125")], initial=("1", "1"))
        jm = exact_constant("2", "3", "0.25")
        jm = exact_constant("-1", "-2", "0.125", str(jm))
        jr = exact_constant("2", "-1", "0.25")
        jr = exact_constant("-1", "4", "0.125", str(jr))
        self.check_contains(out["nodes"][-1]["matter_memory"], jm)
        self.check_contains(out["nodes"][-1]["radiation_memory"], jr)

    def test_cancellation_keeps_signed_sectors(self):
        out = self.run_cells([cell(pm=("1", "1"), pr=("-1", "-1"))])
        node = out["nodes"][-1]
        self.assertGreater(Decimal(node["matter_memory"][0]), 0)
        self.assertLess(Decimal(node["radiation_memory"][1]), 0)
        self.check_contains(node["total_signed_shear"], Decimal(0))

    def test_condition_and_input_immutability(self):
        cells = [cell()]
        before = copy.deepcopy(cells)
        out = self.run_cells(cells)
        self.assertEqual(cells, before)
        self.assertEqual(out["status"], "conditional_on_input_enclosures")
        self.assertFalse(out["input_witnesses_verified"])
        self.assertEqual(out["HH_R10"], "OFF")
        self.assertEqual(out["production"], "NOT_ISSUED")

    def test_ambient_context_is_not_used_or_changed(self):
        expected = self.run_cells([cell(a=("0.001", "0.001"))])
        with localcontext() as ctx:
            ctx.prec = 6
            ctx.rounding = ROUND_DOWN
            actual = self.run_cells([cell(a=("0.001", "0.001"))])
            self.assertEqual(actual, expected)
            self.assertEqual(ctx.prec, 6)
            self.assertEqual(ctx.rounding, ROUND_DOWN)

    def test_missing_or_sample_only_witness_rejected(self):
        for bad in (None, {}, {"scope": "sample_points", "source_identity": "x", "method": "sample minmax", "locator": "x"}):
            c = cell()
            c["witness"] = bad
            with self.assertRaisesRegex(ValueError, "ENCLOSURE_WITNESS"):
                self.run_cells([c])

    def test_invalid_numeric_inputs_rejected(self):
        bad_cells = [cell(h="0"), cell(h="-1"), cell(h=0.5), cell(h="NaN"),
                     cell(a=("2", "1")), cell(pm=("-Infinity", "0")),
                     cell(pr=("0", 1)), cell(a=("wrong", "2"))]
        for c in bad_cells:
            with self.subTest(cell=c), self.assertRaises(ValueError):
                self.run_cells([c])
        for precision in (True, 0, 15, 16.5, 10001):
            with self.assertRaises(ValueError):
                self.run_cells([cell()], precision=precision)
        with self.assertRaises(ValueError):
            self.run_cells([])

    def test_unrepresentable_exponential_raises(self):
        for a in ("1e8", "-1e8"):
            with self.subTest(a=a), self.assertRaises(DecimalException):
                self.run_cells([cell(a=(a, a), h="1")])

    def test_quiet_subnormal_exp_neighbor_is_rejected(self):
        # The correctly rounded exp can be normal while next_minus is quietly
        # subnormal. Independent audit identified this Decimal boundary case.
        with localcontext() as ctx:
            ctx.prec = 160
            exponent = -(Decimal(10).ln() * 999999)
        with self.assertRaisesRegex(ArithmeticError, "EXP_ENCLOSURE_OUTSIDE"):
            _Arithmetic(60).exp(_Interval(exponent, exponent))


if __name__ == "__main__":
    unittest.main()
