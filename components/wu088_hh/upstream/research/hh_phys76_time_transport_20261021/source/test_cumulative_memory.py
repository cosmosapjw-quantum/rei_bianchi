"""Bounded numerical/unit controls; no ODE integration or benchmark."""
import importlib.util
from pathlib import Path
import unittest

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
from scipy.integrate import cumulative_simpson

from cumulative_memory import cumulative_memory_budget


_PR128_PATH = (Path(__file__).resolve().parents[2]
               / "hh_phys75_sector_memory_20261021/source/stress_memory.py")
_SPEC = importlib.util.spec_from_file_location("pinned_phys75_stress_memory", _PR128_PATH)
_PR128 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_PR128)


class CumulativeMemoryTests(unittest.TestCase):
    def setUp(self):
        self.x = np.linspace(0.0, 2.0, 65)

    def test_endpoint_matches_pinned_pr128_for_multiple_case_axes(self):
        x = self.x
        coeff = np.arange(1, 7, dtype=float).reshape(2, 3, 1) / 10
        H = np.exp(-(1.0 + coeff) * x)
        S = coeff * np.cos(x)
        Pm = coeff * np.sin(x)
        Pr = -0.3 * coeff * np.cos(2.0 * x)
        actual = cumulative_memory_budget(x, H, S, Pm, Pr)
        endpoint = _PR128.memory_budget(x, H, S, Pm, Pr)
        for name in ("initial_memory", "matter_memory", "radiation_memory",
                     "predicted_signed_shear", "observed_signed_shear",
                     "closure_defect", "closure_scaled_defect",
                     "stress_memory_cancellation"):
            assert_allclose(actual[name][..., -1], endpoint[name], rtol=4e-14, atol=2e-16)
        assert_array_equal(actual["has_stress_memory"][..., -1], endpoint["has_stress_memory"])

    def test_every_node_matches_independent_scipy_cumulative_simpson(self):
        x = self.x
        H = np.exp(-np.array([0.7, 1.8, 3.2])[:, None] * x)
        Pm = np.array([1.0, 2.0, -0.1])[:, None] * np.sin(1.7 * x)
        Pr = np.array([-0.5, 0.3, 0.0])[:, None] * np.cos(x)
        S = np.broadcast_to(np.sin(x), H.shape).copy()
        actual = cumulative_memory_budget(x, H, S, Pm, Pr)
        # Ordinary range only: the independent oracle may safely construct a
        # global integrating factor here; the production function never does.
        factor = np.exp(3.0 * (x - x[0])) * H / H[..., :1]
        for key, source in (("matter_memory", Pm), ("radiation_memory", Pr)):
            oracle = cumulative_simpson(factor * source, x=x, axis=-1, initial=0.0) / factor
            assert_allclose(actual[key], oracle, rtol=5e-13, atol=3e-16)

    def test_quadratic_weighted_source_is_exact_at_every_node(self):
        x = self.x
        H = np.exp(-3.0 * x)
        Pm = 1.0 + 2.0 * x + x**2
        Pr = 3.0 - 0.5 * x
        im = x + x**2 + x**3 / 3.0
        ir = 3.0 * x - x**2 / 4.0
        S = 0.2 + im + ir
        r = cumulative_memory_budget(x, H, S, Pm, Pr)
        assert_allclose(r["matter_memory"], im, rtol=5e-15, atol=5e-15)
        assert_allclose(r["radiation_memory"], ir, rtol=5e-15, atol=5e-15)
        assert_allclose(r["closure_defect"], 0.0, atol=2e-14)

    def test_cubic_weighted_source_is_exact_at_even_nodes(self):
        x = self.x
        H = np.exp(-3.0 * x)
        z = np.zeros_like(x)
        r = cumulative_memory_budget(x, H, z, x**3, z)
        assert_allclose(r["matter_memory"][::2], x[::2]**4 / 4.0, rtol=5e-15, atol=5e-15)

    def test_zero_stress_matches_analytic_free_decay(self):
        x = self.x
        H = np.exp(-1.5 * x)
        S = -0.004 * np.exp(-1.5 * x)
        z = np.zeros_like(x)
        r = cumulative_memory_budget(x, H, S, z, z)
        assert_allclose(r["initial_memory"], S, rtol=4e-15, atol=1e-18)
        assert_array_equal(r["matter_memory"], z)
        assert_array_equal(r["radiation_memory"], z)
        self.assertFalse(r["has_stress_memory"].any())

    def test_opposite_signed_species_cancel_after_sum(self):
        x = self.x
        h = np.ones_like(x)
        Pm = 0.2 + x
        S = 0.01 * np.exp(-3.0 * x)
        r = cumulative_memory_budget(x, h, S, Pm, -Pm)
        assert_array_equal(r["matter_memory"], -r["radiation_memory"])
        assert_array_equal(r["stress_memory_total_F"], np.zeros_like(x))
        assert_array_equal(r["Pi_total_F"], np.zeros_like(x))
        assert_array_equal(r["stress_memory_cancellation"][1:], np.ones(x.size - 1))
        self.assertTrue(np.all(r["Pi_m_F"] > 0))
        assert_allclose(r["Sigma_F"], np.sqrt(2.0) * r["Sigma_half"], rtol=0, atol=0)

    def test_long_damped_tiny_sources_do_not_build_growing_factor(self):
        x = np.linspace(0.0, 2000.0, 2001)
        H = np.ones_like(x)
        Pm = np.full_like(x, 1e-250)
        z = np.zeros_like(x)
        S = np.full_like(x, 1e-250)
        r = cumulative_memory_budget(x, H, S, Pm, z)
        # Infinite-history steady even-node composite-Simpson sum at h=1.
        expected = 1e-250 * (np.exp(-6.0) + 4.0 * np.exp(-3.0) + 1.0) / (3.0 * (1.0 - np.exp(-6.0)))
        self.assertTrue(all(np.isfinite(v).all() for v in r.values()))
        self.assertGreater(r["matter_memory"][-1], 0)
        assert_allclose(r["matter_memory"][-1], expected, rtol=2e-14, atol=0)
        self.assertEqual(r["initial_memory"][-1], 0.0)

    def test_arbitrary_leading_shapes_and_readonly_inputs(self):
        x = self.x.copy()
        shape = (2, 1, 3, x.size)
        H = np.broadcast_to(np.exp(-x), shape)
        S = np.broadcast_to(0.01 * np.exp(-2.0 * x), shape)
        Pm = np.broadcast_to(np.sin(x), shape)
        Pr = np.broadcast_to(-np.cos(x), shape)
        x.flags.writeable = False
        before = [v.tobytes() for v in (x, H, S, Pm, Pr)]
        r = cumulative_memory_budget(x, H, S, Pm, Pr)
        scalar = cumulative_memory_budget(x, H[0, 0, 0], S[0, 0, 0], Pm[0, 0, 0], Pr[0, 0, 0])
        for key, value in r.items():
            self.assertEqual(value.shape, shape)
            assert_allclose(value[1, 0, 2], scalar[key], rtol=0, atol=0)
        self.assertEqual(before, [v.tobytes() for v in (x, H, S, Pm, Pr)])
        self.assertFalse(np.shares_memory(r["observed_signed_shear"], S))

    def test_positive_samples_can_have_negative_odd_primitive(self):
        x = np.array([0.0, 1.0, 2.0])
        H = np.exp(-3.0 * x)
        z = np.zeros_like(x)
        r = cumulative_memory_budget(x, H, z, [0.0, 0.0, 12.0], z)
        assert_allclose(r["matter_memory"], [0.0, -1.0, 4.0], rtol=2e-15, atol=2e-15)

    def test_odd_node_depends_on_one_future_sample(self):
        x = np.array([0.0, 1.0, 2.0])
        H = np.exp(-3.0 * x)
        z = np.zeros_like(x)
        a = cumulative_memory_budget(x, H, z, [1.0, 1.0, 1.0], z)
        b = cumulative_memory_budget(x, H, z, [1.0, 1.0, 2.0], z)
        self.assertNotEqual(a["matter_memory"][1], b["matter_memory"][1])
        assert_allclose(b["matter_memory"][1] - a["matter_memory"][1], -1 / 12, atol=3e-16)

    def test_invalid_grid_shape_hubble_and_nonfinite_rejected(self):
        for x in ([0, 1], [0, 1, 2, 3], [0, 1, 3], [2, 1, 0],
                  [0, 0, 1], [0, np.nan, 1], [0, 1, np.inf], [[0, 1, 2]]):
            with self.subTest(x=x), self.assertRaises(ValueError):
                cumulative_memory_budget(x, [1, 1, 1], [0, 0, 0], [0, 0, 0], [0, 0, 0])
        z = np.zeros_like(self.x)
        one = np.ones_like(self.x)
        for H in (one[:-1], -one, z, np.full_like(z, np.nan), np.full_like(z, np.inf)):
            with self.assertRaises(ValueError):
                cumulative_memory_budget(self.x, H, z, z, z)
        with self.assertRaises(ValueError):
            cumulative_memory_budget(self.x, one, z[None, :], z, z)
        with self.assertRaises(ValueError):
            cumulative_memory_budget(self.x, 1.0, 0.0, 0.0, 0.0)
        for which in range(1, 4):
            args = [one.copy(), z.copy(), z.copy(), z.copy()]
            args[which][3] = np.nan
            with self.assertRaises(ValueError):
                cumulative_memory_budget(self.x, *args)

    def test_complex_inputs_rejected_without_silent_cast(self):
        z = np.zeros_like(self.x)
        for which in range(5):
            args = [self.x, np.ones_like(z), z, z, z]
            args[which] = args[which].astype(complex)
            args[which][1] += 1j
            with self.subTest(which=which), self.assertRaises(ValueError):
                cumulative_memory_budget(*args)
        with self.assertRaises(ValueError):
            cumulative_memory_budget([0, 1, 2], [1, 1, 1], [0, 0, 0],
                                     np.array([0, 1j, 0], dtype=object), [0, 0, 0])

    def test_overflow_is_reported_and_never_silently_clipped(self):
        x = np.array([0.0, 1.0, 2.0])
        z = np.zeros_like(x)
        with self.assertRaisesRegex(FloatingPointError, "NONFINITE_MEMORY"):
            cumulative_memory_budget(x, [1e300, 1e-300, 1e300], z, z, z)
        with self.assertRaisesRegex(FloatingPointError, "NONFINITE_MEMORY"):
            cumulative_memory_budget(x, np.ones_like(x), z,
                                     np.full_like(x, 1e308), np.full_like(x, 1e308))


if __name__ == "__main__":
    unittest.main(verbosity=2)
