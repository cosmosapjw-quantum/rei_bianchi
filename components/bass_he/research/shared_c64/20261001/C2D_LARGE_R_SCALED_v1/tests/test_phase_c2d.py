"""Manufactured phase checks: no physical eigensolves or observables."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "reference"))
import spheroidal_tail as st


class DominantPhaseTests(unittest.TestCase):
    def setUp(self):
        self.axis = st._Axis(np.linspace(-1, 1, 9), 2, 6, 0, False)

    def weak_tail_vector(self):
        vector = np.zeros(self.axis.mass.shape[0])
        vector[:2] = -1e-16
        vector[-2:] = 1.0
        return vector / np.sqrt(vector @ self.axis.mass @ vector)

    def mocked_lowest(self, vector):
        with patch.object(st, "eigh", return_value=(np.array([1.0]), vector[:, None])):
            return self.axis.lowest(self.axis.mass.copy())

    def test_weak_opposite_tail_does_not_control_phase(self):
        vector = self.weak_tail_vector()
        first_midpoint = np.mean(self.axis.edges[:2])
        self.assertLess(float(self.axis.basis(first_midpoint) @ vector), 0.0)
        eigenvalue, oriented, residual = self.mocked_lowest(vector)
        np.testing.assert_array_equal(oriented, vector)
        self.assertEqual(eigenvalue, 1.0)
        self.assertEqual(residual, 0.0)
        diag = self.axis.phase_diagnostics(oriented)
        self.assertGreater(diag["dominant_value"], 0.0)
        self.assertLess(diag["negative_l2_fraction"], 1e-30)

    def test_global_sign_input_has_identical_oriented_result(self):
        vector = self.weak_tail_vector()
        plus = self.mocked_lowest(vector)
        minus = self.mocked_lowest(-vector)
        self.assertEqual(plus[0], minus[0])
        np.testing.assert_array_equal(plus[1], minus[1])
        self.assertEqual(plus[2], minus[2])
        self.assertAlmostEqual(plus[1] @ self.axis.mass @ plus[1], 1.0)

    def test_weighted_negative_mass_uses_regularized_measure(self):
        for m in (0, 1):
            axis = st._Axis(np.array([-1.0, 0.0, 1.0]), 2, 6, m, False)
            # Reflection-odd regular spline and reflection-even weight p^m.
            odd = np.array([-1.0, -1.0, 1.0, 1.0])
            self.assertAlmostEqual(axis.phase_diagnostics(odd)["negative_l2_fraction"], 0.5)
            positive = np.ones(4)
            self.assertEqual(axis.phase_diagnostics(positive)["negative_l2_fraction"], 0.0)
            self.assertEqual(axis.phase_diagnostics(-positive)["negative_l2_fraction"], 1.0)

    def test_nonfinite_and_zero_vectors_fail_closed(self):
        n = len(self.weak_tail_vector())
        for value in (np.nan, np.inf, 0.0):
            with self.assertRaises(ValueError):
                self.axis.phase_diagnostics(np.full(n, value))


if __name__ == "__main__":
    unittest.main()
