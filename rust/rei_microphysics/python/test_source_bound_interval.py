"""Targeted production-boundary tests; no full scientific sweep is repeated."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

import source_bound_interval as production


class ProductionBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verified = production.preflight(production.DEFAULT_PACKET)
        cls.interval = production.ProductionInterval(production.DEFAULT_PACKET, cls.verified, None)

    def test_immutable_source_change_rejects_before_provider_use(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source"
            path.write_bytes(b"source-v1")
            expected = hashlib.sha256(b"source-v1").hexdigest()
            self.assertEqual(production.verify_bytes(path, expected), expected)
            path.write_bytes(b"source-v2")
            with self.assertRaisesRegex(ValueError, "IMMUTABLE_INPUT_SHA_MISMATCH"):
                production.verify_bytes(path, expected)

    def test_stage_consumes_current_state_with_current_source_geometry(self):
        interval = self.interval
        state = interval.y0.copy()
        state[0] *= 0.99
        state[3] *= 1.01
        state[4] *= 0.5
        time = 4e10
        values, source = interval.stage(time, state)
        geometry = interval.background.at(time)
        np.testing.assert_array_equal(values[7:11], state[:4])
        nodes = values[12:].reshape(-1, 4)
        np.testing.assert_array_equal(nodes[:, 2], state[4:4+interval.n])
        self.assertEqual(values[0], time)
        np.testing.assert_array_equal(values[1:7], [geometry[key] for key in
            ("a_rel", "b", "H", "s", "nH", "nHe")])
        expected = interval.emissivity.photon_emission_log(nodes[:, 0], geometry["z"])
        # Jacobian written in directional-coordinate form independently of
        # source assembly: a_rel^3*dOmega/dOmega0 = (E/q)^-3.
        expected *= interval.weights*(interval.q/nodes[:, 0])**3
        np.testing.assert_allclose(source, expected, rtol=8*np.finfo(float).eps, atol=0)
        np.testing.assert_array_equal(nodes[:, 3], source)

    def test_bound_time_domain_rejects_extrapolation(self):
        with self.assertRaisesRegex(ValueError, "BACKGROUND_TIME_OUTSIDE_IMMUTABLE_DOMAIN"):
            self.interval.stage(1e11+1, self.interval.y0)

    def test_initial_data_is_not_reference_history(self):
        interval = self.interval
        self.assertEqual(interval.y0.shape, (2913,))
        self.assertEqual(interval.n, 2904)
        self.assertTrue(np.all(interval.y0[-5:] == 0))
        self.assertNotIn("reference_states", vars(interval))
        self.assertNotIn("states", vars(interval))

    def test_comparison_is_serializable_and_detects_wrong_state(self):
        packet = production.DEFAULT_PACKET
        with np.load(packet / "evidence/extended_dataset.npz", allow_pickle=False) as dataset:
            state = dataset["states"].copy()
        rows = json.loads((packet / "evidence/extended.json").read_text())["history"]
        self.interval.max_local_number = np.float64(1e-16)
        self.interval.max_local_energy = np.float64(1e-16)
        result = production.compare_reference(packet, self.interval, state, rows, self.verified["contract"])
        self.assertEqual(result["status"], "PASS_SCOPED")
        json.dumps(result)
        state[0, -1] -= 1e-4
        failed = production.compare_reference(packet, self.interval, state, rows, self.verified["contract"])
        self.assertEqual(failed["status"], "FAIL")
        self.assertFalse(failed["checks"]["state_agreement"])


if __name__ == "__main__":
    unittest.main()
