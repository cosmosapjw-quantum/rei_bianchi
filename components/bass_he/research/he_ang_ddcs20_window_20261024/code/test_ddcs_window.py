"""Targeted controls for the newly frozen operator; standard-library unittest."""
import itertools
import json
import math
import tempfile
import unittest
from pathlib import Path

import numpy as np

from ddcs_window import (UNIT, Source, atomic_json, hat_integral_weights, load_source,
                         linear_box_extrema, moment_weights, quadrature_moments,
                         ratio_box_extrema, theta_interpolation_control,
                         validate_source, window_moments)


RTOL = 5e-13
ATOL = 5e-14


class OperatorControls(unittest.TestCase):
    def assert_scaled_close(self, a, b, scale=1.0):
        self.assertLessEqual(abs(a - b), ATOL * scale + RTOL * abs(b))

    def control_source(self, affine=False):
        mu = np.array([-0.6, 0.1, 0.8])
        E = np.array([1.5, 2.2, 4.0])
        if affine:
            y = 2 + 0.3 * mu[:, None] + 0.4 * E[None, :] + 0.2 * mu[:, None] * E[None, :]
        else:
            y = np.full((3, 3), 2.0)
        return Source(E, mu, y, np.full(3, 15.0))

    def test_source_transcription_all_40_and_primary_32(self):
        s = load_source()
        self.assertEqual(s.raw_values_preserved, 40)
        self.assertEqual(s.values.shape, (8, 4))
        self.assertEqual(s.energy.tolist(), [3, 4, 5, 6])
        self.assertTrue(np.all(np.diff(s.mu) > 0))
        self.assertEqual(s.values[-1].tolist(), [27, 35.8, 47, 60.7])
        self.assertEqual(s.values[0].tolist(), [2.56, 2.99, 3.47, 4])

    def test_constant_and_affine_closed_form_controls(self):
        def primitive(a, b, power):
            return (b ** (power + 1) - a ** (power + 1)) / (power + 1)
        for affine in (False, True):
            s = self.control_source(affine)
            for subwindow in (False, True):
                mw = (-0.4, 0.6) if subwindow else None
                ew = (1.7, 3.7) if subwindow else None
                weights, _, _ = moment_weights(s, ew, mw)
                a, b = mw or (s.mu[0], s.mu[-1])
                c, d = ew or (s.energy[0], s.energy[-1])
                for (r, q), w in weights.items():
                    I = primitive(a, b, r)
                    J = primitive(c, d, q)
                    exact = 2 * I * J
                    if affine:
                        I1, J1 = primitive(a, b, r + 1), primitive(c, d, q + 1)
                        exact += 0.3 * I1 * J + 0.4 * I * J1 + 0.2 * I1 * J1
                    self.assert_scaled_close(float(np.sum(w * s.values)), exact)

    def test_cellwise_GL16_GL32_independent_local_interpolation(self):
        for s in (self.control_source(True), load_source()):
            weights, _, _ = moment_weights(s)
            scale = float(np.sum(weights[(0, 0)] * s.values))
            q16, q32 = quadrature_moments(s, 16), quadrature_moments(s, 32)
            for key, w in weights.items():
                exact = float(np.sum(w * s.values))
                for value in (q16[key], q32[key]):
                    self.assertLessEqual(abs(value - exact) / max(scale, abs(exact)), 5e-13)
                self.assertLessEqual(abs(q16[key] - q32[key]) / max(scale, abs(exact)), 5e-13)

    def test_exhaustive_small_box_signed_ties_equal_and_witnesses(self):
        rng = np.random.default_rng(204022709)
        for n in range(1, 7):
            for kind in ("signed", "ties", "equal", "degenerate"):
                a = rng.uniform(0.1, 2, n)
                q = rng.uniform(-3, 3, n)
                if kind == "ties":
                    q = np.resize(np.array([-2., -2., 1.]), n)
                if kind == "equal":
                    q = np.full(n, -0.75)
                b = a * q
                low = rng.uniform(0.1, 2, n)
                high = low + rng.uniform(0.1, 2, n)
                if kind == "degenerate":
                    high[::2] = low[::2]
                vertices = [np.where(bits, high, low) for bits in itertools.product((False, True), repeat=n)]
                vals = [float(b @ z / (a @ z)) for z in vertices]
                got = ratio_box_extrema(a, b, low, high)
                for label, expected in (("min", min(vals)), ("max", max(vals))):
                    self.assert_scaled_close(got[label + "imum"], expected)
                    z = np.array(got[label + "_witness"])
                    self.assertTrue(np.all((z == low) | (z == high)))
                    self.assert_scaled_close(float(b @ z / (a @ z)), expected)
                    self.assertLessEqual(got[label + "_equality_scaled_residual"], 5e-13)
                    self.assertLessEqual(got[label + "_stationarity_scaled_gap"], 5e-13)
                scaled = ratio_box_extrema(a, b, 7.3 * low, 7.3 * high)
                self.assert_scaled_close(scaled["minimum"], got["minimum"])
                self.assert_scaled_close(scaled["maximum"], got["maximum"])

    def test_signed_linear_box_exact_endpoints(self):
        w = np.array([-3., 0, 2, -0.5])
        lo, hi = np.array([1., 2, 3, 4]), np.array([2., 4, 5, 4])
        vals = [float(w @ np.where(bits, hi, lo)) for bits in itertools.product((False, True), repeat=4)]
        actual = linear_box_extrema(w, lo, hi)
        self.assertEqual(actual["minimum"], min(vals))
        self.assertEqual(actual["maximum"], max(vals))

    def test_actual_invariants_and_scale_invariance(self):
        s = load_source()
        result = window_moments(s)
        self.assertGreater(result["raw_moments"]["R_0_0"], 0)
        r = result["conditional"]
        self.assertTrue(s.mu[0] <= r["mean_mu"] <= s.mu[-1])
        self.assertTrue(3 <= r["mean_E_eV"] <= 6)
        self.assertTrue(-0.5 <= r["mean_P2"] <= 1)
        self.assertLessEqual(result["invariants"]["trace_tensor_scaled_residual"], 5e-13)
        self.assertGreaterEqual(min(result["conditional_covariance_diag_div_2me_epsilon"]), -1e-12 * r["mean_E_eV"])
        scaled = window_moments(Source(s.energy, s.mu, s.values * 3.7, s.uncertainty_percent))
        for name, val in r.items():
            self.assert_scaled_close(scaled["conditional"][name], val)
            for side in ("minimum", "maximum"):
                self.assert_scaled_close(scaled["conditional_deterministic_box_not_CI"][name][side], result["conditional_deterministic_box_not_CI"][name][side])

    def test_theta_radian_jacobian_constant_control(self):
        s = self.control_source(False)
        weights, _, _ = moment_weights(s)
        q = quadrature_moments(s, 32, "theta")
        # A constant source is identical in theta and mu; sin(theta) must recover dmu.
        for key, w in weights.items():
            self.assert_scaled_close(q[key], float(np.sum(w * s.values)))
        self.assertEqual(theta_interpolation_control(s)["order"], 32)

    def test_input_rejections(self):
        s = self.control_source()
        for E in ([0, 1, 2], [1, 1, 2], [2, 1, 3], [1, math.inf, 3]):
            with self.assertRaises(ValueError):
                validate_source(Source(np.array(E), s.mu, s.values, s.uncertainty_percent))
        for mu in ([-.5, -.5, .5], [.5, -.5, .8], [-.5, math.nan, .5]):
            with self.assertRaises(ValueError):
                validate_source(Source(s.energy, np.array(mu), s.values, s.uncertainty_percent))
        for yy in (np.full((3, 3), -1), np.full((3, 3), math.nan), np.ones((3, 2))):
            with self.assertRaises(ValueError):
                validate_source(Source(s.energy, s.mu, yy, s.uncertainty_percent))
        for win in ((1.4, 4), (1.5, 4.1), (3, 2), (2, 2)):
            with self.assertRaises(ValueError):
                window_moments(s, E_window=win)
        with self.assertRaises(ValueError):
            window_moments(s, mu_window=(-0.7, 0.8))
        with self.assertRaises(ValueError):
            hat_integral_weights([-1, 0, 1], 0.5)
        for a, lo, hi in (([0, 1], [1, 1], [2, 2]), ([1, -1], [1, 1], [2, 2]), ([1, 1], [0, 1], [2, 2]), ([1, 1], [1, 2], [2, 1]), ([1, math.inf], [1, 1], [2, 2])):
            with self.assertRaises(ValueError):
                ratio_box_extrema(a, [-1, 2], lo, hi)
        with self.assertRaises(ValueError):
            load_source(primary_energies=(2, 3, 4, 5, 6))
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "incomplete.csv"
            text = (UNIT / "source/Childers2004_TableIV_source_transcript.csv").read_text()
            p.write_text("\n".join(text.splitlines()[:-1]) + "\n")
            with self.assertRaises(ValueError):
                load_source(p, UNIT / "source/Childers2004_TableIV_source_transcript.json")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(OperatorControls)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    atomic_json(UNIT / "results/tests.json", {"tests_run": result.testsRun, "success": result.wasSuccessful(), "failures": len(result.failures), "errors": len(result.errors), "relative_tolerance": RTOL, "near_zero_absolute_tolerance": ATOL, "oracle_max_dimension": 6, "oracle_cases": "signed, ties, equality and degenerate bounds for n=1..6", "claim": "targeted operator controls, not physical full-provider validation"})
    raise SystemExit(0 if result.wasSuccessful() else 1)
