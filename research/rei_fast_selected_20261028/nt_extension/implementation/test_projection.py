"""Small presentation-only tests; original nuclear solver is never imported."""

import math
import unittest

from project_saved import LN10, encoded_log, log10_view, _assert_monotone_cumulative
import numpy as np


class SavedPresentationTests(unittest.TestCase):
    def test_log_preserves_finite_tiny_and_exact_zero(self):
        self.assertEqual(encoded_log(-math.inf), "-Infinity")
        self.assertIsNone(log10_view("-Infinity"))
        self.assertAlmostEqual(log10_view(-950.0), -950.0 / LN10, places=12)

    def test_reject_invalid_source_logs(self):
        for value in (math.nan, math.inf):
            with self.assertRaises(ValueError):
                encoded_log(value)

    def test_cumulative_monotonicity_with_initial_zero(self):
        _assert_monotone_cumulative(np.array([-math.inf, -950.0, -240.0]), "fixture")
        with self.assertRaisesRegex(ValueError, "decreasing"):
            _assert_monotone_cumulative(np.array([-math.inf, -240.0, -241.0]), "fixture")


if __name__ == "__main__":
    unittest.main()
