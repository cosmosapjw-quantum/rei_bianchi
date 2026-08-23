from __future__ import annotations

from fractions import Fraction
import math
from pathlib import Path
import sys
import unittest


ANALYSIS = Path(__file__).resolve().parents[1] / "analysis"
sys.path.insert(0, str(ANALYSIS))

import verified_backend as vb


def _float_le_rational(value: float, rational: Fraction) -> bool:
    numerator, denominator = value.as_integer_ratio()
    return numerator * rational.denominator <= rational.numerator * denominator


def _rational_le_float(rational: Fraction, value: float) -> bool:
    numerator, denominator = value.as_integer_ratio()
    return rational.numerator * denominator <= numerator * rational.denominator


class VerifiedBackendTests(unittest.TestCase):
    def test_decimal_and_binary64_provenance_are_distinct(self) -> None:
        decimal = vb.exact_scalar_from_decimal_text("0.079")
        binary = vb.exact_scalar_from_binary64(0.079)
        self.assertEqual(decimal.status, vb.NumericStatus.OK)
        self.assertEqual(binary.status, vb.NumericStatus.OK)
        self.assertEqual(decimal.value.value, Fraction(79, 1000))
        self.assertNotEqual(decimal.value.value, binary.value.value)
        self.assertEqual(decimal.value.provenance, vb.ExactProvenance.DECIMAL_TEXT)
        self.assertEqual(binary.value.provenance, vb.ExactProvenance.BINARY64)

    def test_exact_sum_kills_current_signed_cancellation_failure(self) -> None:
        result = vb.exact_sum_binary64([1.0e20, 1.0, -1.0e20])
        self.assertEqual(result.status, vb.NumericStatus.OK)
        self.assertEqual(result.value.exact, Fraction(1, 1))
        self.assertEqual(result.value.binary64.lo, 1.0)
        self.assertEqual(result.value.binary64.hi, 1.0)

    def test_half_minimum_subnormal_is_outward_not_silently_zero(self) -> None:
        exact = Fraction(1, 1 << 1075)
        result = vb.outward_binary64(exact)
        self.assertEqual(result.status, vb.NumericStatus.OK)
        self.assertEqual(result.value.lo, 0.0)
        self.assertEqual(result.value.hi, math.ulp(0.0))
        self.assertTrue(_float_le_rational(result.value.lo, exact))
        self.assertTrue(_rational_le_float(exact, result.value.hi))

    def test_exact_interval_algebra_and_zero_divisor_status(self) -> None:
        a = vb.ExactInterval(Fraction(-2), Fraction(3))
        b = vb.ExactInterval(Fraction(1, 2), Fraction(5, 2))
        product = vb.exact_mul(a, b)
        self.assertEqual(product.status, vb.NumericStatus.OK)
        self.assertEqual(product.value, vb.ExactInterval(Fraction(-5), Fraction(15, 2)))
        quotient = vb.exact_div(a, vb.ExactInterval(Fraction(-1), Fraction(1)))
        self.assertEqual(quotient.status, vb.NumericStatus.DIVISOR_CONTAINS_ZERO)
        self.assertIsNone(quotient.value)

    def test_nonfinite_overflow_resource_and_transcendental_are_typed(self) -> None:
        self.assertEqual(
            vb.exact_scalar_from_binary64(float("inf")).status,
            vb.NumericStatus.NONFINITE_INPUT,
        )
        too_large = Fraction.from_float(sys.float_info.max) * 2
        self.assertEqual(
            vb.outward_binary64(too_large).status,
            vb.NumericStatus.BINARY64_OVERFLOW,
        )
        self.assertEqual(
            vb.exact_sum_binary64([0.0] * (vb.MAX_SUM_TERMS + 1)).status,
            vb.NumericStatus.EXACT_RESOURCE_LIMIT,
        )
        x = vb.ExactInterval(Fraction(0), Fraction(1))
        self.assertEqual(
            vb.outward_elementary("exp", x).status,
            vb.NumericStatus.UNSUPPORTED_TRANSCENDENTAL,
        )

    def test_exact_sum_is_permutation_invariant(self) -> None:
        values = [2.0**500, 3.0, -(2.0**500), -2.0, math.ulp(0.0)]
        forward = vb.exact_sum_binary64(values)
        reverse = vb.exact_sum_binary64(list(reversed(values)))
        self.assertEqual(forward.status, vb.NumericStatus.OK)
        self.assertEqual(reverse.status, vb.NumericStatus.OK)
        self.assertEqual(forward.value.exact, Fraction(1) + Fraction(1, 1 << 1074))
        self.assertEqual(forward.value, reverse.value)


if __name__ == "__main__":
    unittest.main()
