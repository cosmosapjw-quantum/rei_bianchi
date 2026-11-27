"""New A1b checks only; explicit 8D ambient geometry supplies references."""

import math
import unittest
from fractions import Fraction

import numpy as np

from channel_embedding_algebra import (
    DELTA_REJECTION_TOLERANCE,
    channel_probabilities,
    gram_from_overlap,
    orthonormalizer,
)

ATOL = 2.0e-12


def fixture():
    # A deterministic complex unitary rotates the ambient coordinate axes.
    indices = np.arange(8)
    q = np.exp(2j * np.pi * np.outer(indices, indices) / 8) / np.sqrt(8)
    v = q[:, :5]
    s = np.array([0.2 + 0.1j, -0.1 + 0.15j, 0.07j, 0.13, -0.05j])
    u = v @ s + np.sqrt(1.0 - np.vdot(s, s).real) * q[:, 5]
    x = np.column_stack((u, v))
    return u, v, x, s


class ChannelEmbeddingChecks(unittest.TestCase):
    def assert_close(self, actual, expected):
        np.testing.assert_allclose(actual, expected, rtol=0, atol=ATOL)

    def test_ambient_projectors_gram_and_orthonormalizer(self):
        u, v, x, s = fixture()
        c = np.array([0.4 - 0.3j, 0.2j, -0.5, 0.3 + 0.1j, 0.7, -0.2j])
        state = x @ c
        self.assert_close(gram_from_overlap(s), x.conj().T @ x)
        y = x @ orthonormalizer(s)
        self.assert_close(y.conj().T @ y, np.eye(6))
        out = channel_probabilities(c, s)
        self.assert_close(out["p_B"], np.linalg.norm(v @ (v.conj().T @ state)) ** 2)
        self.assert_close(out["p_A_raw"], np.linalg.norm(u * np.vdot(u, state)) ** 2)
        self.assert_close(out["p_A_orthogonal"], np.linalg.norm(y[:, 0] * np.vdot(y[:, 0], state)) ** 2)
        self.assert_close(out["metric_norm"], np.vdot(state, state).real)
        self.assert_close(out["orthogonal_partition"], np.vdot(state, state).real)

    def test_finite_overlap_double_count_counterexample(self):
        _, _, _, s = fixture()
        c = np.zeros(6, dtype=complex)
        c[0] = 1
        out = channel_probabilities(c, s)
        self.assert_close(out["metric_norm"], 1)
        self.assert_close(out["p_A_raw"], 1)
        self.assert_close(out["p_B"], np.vdot(s, s).real)
        self.assertGreater(out["raw_projector_sum"], 1)
        self.assert_close(out["orthogonal_partition"], 1)

    def test_asymptotic_zero_overlap(self):
        s = np.zeros(5)
        c = np.array([0.3j, 0.2 + 0.1j, -0.4, 0.5, 0, -0.1j])
        self.assert_close(gram_from_overlap(s), np.eye(6))
        self.assert_close(orthonormalizer(s), np.eye(6))
        out = channel_probabilities(c, s)
        self.assert_close(out["p_A_raw"], abs(c[0]) ** 2)
        self.assert_close(out["raw_projector_sum"], np.vdot(c, c).real)
        self.assert_close(out["p_A_raw"], out["p_A_orthogonal"])

    def test_same_center_unitary_covariance(self):
        u, v, x, s = fixture()
        indices = np.arange(5)
        unitary = np.exp(2j * np.pi * np.outer(indices, indices) / 5) / np.sqrt(5)
        c = np.array([0.4 + 0.2j, 0.1j, -0.2, 0.3j, 0.4, -0.5j])
        transformed_s = unitary.conj().T @ s
        transformed_c = np.r_[c[0], unitary.conj().T @ c[1:]]
        transformed_x = np.column_stack((u, v @ unitary))
        self.assert_close(transformed_x @ transformed_c, x @ c)
        reference = channel_probabilities(c, s)
        transformed = channel_probabilities(transformed_c, transformed_s)
        for key in reference:
            self.assert_close(transformed[key], reference[key])

    def test_coherent_projectile_cancellation(self):
        _, v, x, s = fixture()
        a = 0.4 + 0.3j
        c = np.r_[a, -s * a]
        out = channel_probabilities(c, s)
        self.assert_close(out["p_B"], 0)
        self.assert_close(v.conj().T @ (x @ c), np.zeros(5))
        self.assertGreater(np.vdot(c[1:], c[1:]).real, 0)
        self.assert_close(out["orthogonal_partition"], out["metric_norm"])

    def test_exact_coalescence_overlap_fixture(self):
        # Algebra fixture provided by the analytic embedding, not an orbital solver.
        exact_delta = 1 - Fraction(512, 729) - Fraction(1, 4)
        self.assertEqual(exact_delta, Fraction(139, 2916))
        s = np.array([16 * math.sqrt(2) / 27, -0.5, 0, 0, 0])
        w = orthonormalizer(s)
        self.assert_close(w.conj().T @ gram_from_overlap(s) @ w, np.eye(6))
        self.assert_close(channel_probabilities(np.r_[1, np.zeros(5)], s)["delta"], float(exact_delta))

    def test_singular_and_nearly_singular_gram_rejected(self):
        for length in (1.0, 1.01, np.sqrt(1 - DELTA_REJECTION_TOLERANCE / 2)):
            s = np.array([length, 0, 0, 0, 0])
            for function in (gram_from_overlap, orthonormalizer):
                with self.subTest(length=length, function=function.__name__):
                    with self.assertRaises(ValueError):
                        function(s)
            with self.assertRaises(ValueError):
                channel_probabilities(np.ones(6), s)

    def test_invalid_input_and_overflow_fail_closed(self):
        bad_s = (np.zeros((5, 1)), np.zeros(4), [np.nan, 0, 0, 0, 0], [np.inf, 0, 0, 0, 0], [1e308, 0, 0, 0, 0])
        for s in bad_s:
            with self.subTest(s=str(s)):
                with self.assertRaises(ValueError):
                    gram_from_overlap(s)
                with self.assertRaises(ValueError):
                    orthonormalizer(s)
                with self.assertRaises(ValueError):
                    channel_probabilities(np.ones(6), s)
        for c in (np.zeros((6, 1)), np.zeros(5), [0, 0, 0, 0, 0, np.nan], [np.inf] * 6, [1e308] * 6):
            with self.subTest(c=str(c)):
                with self.assertRaises(ValueError):
                    channel_probabilities(c, np.zeros(5))


if __name__ == "__main__":
    unittest.main(verbosity=2)
