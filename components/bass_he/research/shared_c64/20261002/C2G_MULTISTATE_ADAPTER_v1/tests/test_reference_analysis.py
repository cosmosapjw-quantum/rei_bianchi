"""Manufactured analysis tests; no molecular eigensolve or old suite replay."""
import copy
import json
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"code"))
from analyze_reference import Gates, common_frame_comparison, normalized_observables, validate_layout_arguments
from runtime_support import ContractError


class ReferenceAnalysisTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(239)
        self.weights = np.linspace(.2, 1.7, 40)
        q, _ = np.linalg.qr(rng.normal(size=(40, 5))+1j*rng.normal(size=(40, 5)))
        self.frame = q / np.sqrt(self.weights[:, None])
        self.r = np.linspace(.1, 20., 40)
        self.unitary, _ = np.linalg.qr(rng.normal(size=(5, 5))+1j*rng.normal(size=(5, 5)))

    def test_whitened_observable_under_nonsingular_frame_change(self):
        base, _ = normalized_observables(self.frame, self.weights, self.r)
        altered = self.frame @ (self.unitary @ np.diag([.8, 1.2, .9, 1.1, .7]))
        changed, _ = normalized_observables(altered, self.weights, self.r)
        self.assertAlmostEqual(base["trace_r2"], changed["trace_r2"], places=10)
        self.assertGreater(changed["selected_Gram_operator_norm_error"], .1)

    def test_outer_layer_is_basis_invariant_max_eigenvalue(self):
        base, _ = normalized_observables(self.frame, self.weights, self.r)
        changed, _ = normalized_observables(self.frame@self.unitary, self.weights, self.r)
        self.assertAlmostEqual(base["outer_layer_probability_max"], changed["outer_layer_probability_max"], places=13)
        self.assertGreaterEqual(base["outer_layer_probability_max"], 0)
        self.assertLessEqual(base["outer_layer_probability_max"], 1)

    def test_parity_geometry_stable_at_identical_subspace(self):
        values, overlap = common_frame_comparison(self.frame, self.frame@self.unitary, self.weights)
        self.assertLess(values["projector_operator_distance"], 4e-15)
        np.testing.assert_allclose(overlap, self.unitary, rtol=0, atol=2e-15)

    def test_invalid_manifest_layout_omission_or_duplicate(self):
        prereg = {"campaign": {"layouts": [{"id": "numpy_serial_1x1"}, {"id": "native_mpi_2x1"}]}}
        with self.assertRaises(ContractError):
            validate_layout_arguments(prereg, {"numpy_serial_1x1": "/tmp/a.json"})
        with self.assertRaises(ContractError):
            validate_layout_arguments(prereg, {"numpy_serial_1x1": "/tmp/a.json", "native_mpi_2x1": "/tmp/a.json"})

    def test_preregistration_thresholds_not_mutated_by_failure(self):
        path = Path(__file__).resolve().parents[1]/"contract"/"PHYSICAL_PREREGISTRATION.json"
        raw = path.read_bytes()
        contract = json.loads(raw)
        original = copy.deepcopy(contract)
        g = Gates()
        threshold = contract["gates"]["finite_basis_exploration"]["medium_to_fine_energy_max_abs_delta"]
        self.assertFalse(g.add("energy", .02, threshold, category="finite_basis_exploration"))
        g.add("later", .01, threshold, category="finite_basis_exploration")
        result = g.result()
        self.assertEqual(result["first_failed_gate"]["value"], .02)
        self.assertEqual(result["failed_count"], 2)
        self.assertEqual(contract, original)
        self.assertEqual(path.read_bytes(), raw)

    def test_nonpositive_metric_and_rank_deficiency_rejected(self):
        w = self.weights.copy()
        w[3] = 0
        with self.assertRaises(ContractError):
            normalized_observables(self.frame, w, self.r)
        with self.assertRaises(ContractError):
            normalized_observables(np.column_stack([self.frame[:, 0]]*2), self.weights, self.r)


if __name__ == "__main__":
    unittest.main()
