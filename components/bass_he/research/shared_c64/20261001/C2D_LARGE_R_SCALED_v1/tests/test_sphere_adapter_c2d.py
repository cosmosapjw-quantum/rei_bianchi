"""Affected synthetic checks only; no physical eigensolve or integral."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"code"), str(ROOT/"reference")]

import numpy as np
from optimized_solver import PartialWaveState
import sphere_adapter as adapter


class LargeRAdapterTests(unittest.TestCase):
    def fixture(self, folder, m=0):
        boundaries = np.array([0., .5, 1., 32., 40.])
        configuration = dict(R=32., m=m, lmax=m, elements=4, degree=2,
                             rmax=40., quadrature=6, nroots=2, center="B",
                             tol=1e-11, boundaries=boundaries.tolist())
        coefficients = np.array([[0., .1, .2, .3, .4, .5, .4, .2, 0.]])
        metadata = dict(origin_center="B", origin_shift_center_to_O=32./3,
                        nuclear_positions=[-32., 0.], degree=2, angular_lmax=m,
                        rmax=40., explicit_boundaries=boundaries.tolist())
        state = PartialWaveState(32., 1., 2., m, np.array([m]), boundaries,
                                 2, coefficients, -2., 1e-12, 1., 0., metadata)
        with patch("optimized_solver.solve", return_value=state) as solve:
            value = adapter.solve_one(configuration, folder)
            self.assertEqual(solve.call_count, 1)
        data = dict(parameters=dict(kind="sphere", configuration=configuration), value=value)
        (folder/"DATA.json").write_text(json.dumps(data))
        return data, state

    def test_enclosing_large_r_explicit_mesh_roundtrip(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            data, original = self.fixture(folder)
            with patch("optimized_solver.solve", side_effect=AssertionError("no solve on read")):
                restored = adapter.load_one(folder)
            np.testing.assert_array_equal(restored.boundaries, original.boundaries)
            np.testing.assert_array_equal(restored.boundaries,
                                          data["parameters"]["configuration"]["boundaries"])
            self.assertEqual(restored.R, 32.)

    def test_requested_partition_mismatch_rejected_on_load(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            data, _ = self.fixture(folder)
            # Archive bytes and metadata still agree; only the requested mesh differs.
            data["parameters"]["configuration"]["boundaries"][1] = .75
            (folder/"DATA.json").write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "requested explicit boundaries"):
                adapter.load_one(folder)

    def test_requested_partition_mismatch_rejected_on_solve_validation(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            data, state = self.fixture(folder)
            configuration = dict(data["parameters"]["configuration"])
            configuration["boundaries"] = [0., .75, 1., 32., 40.]
            target = folder/"mismatched"
            with patch("optimized_solver.solve", return_value=state):
                with self.assertRaisesRegex(ValueError, "requested explicit boundaries"):
                    adapter.solve_one(configuration, target)
            self.assertFalse((target/"STATE.npz").exists())

    def test_nucleus_knot_and_enclosing_box_guards_preserved(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            data, state = self.fixture(folder)
            configuration = data["parameters"]["configuration"]
            state.boundaries[3] = 31.
            with self.assertRaisesRegex(ValueError, "invalid spherical radial partition"):
                adapter._validate_state(state, configuration)
            with self.assertRaisesRegex(ValueError, "enclosing positive box"):
                adapter._configuration({**configuration, "rmax": 24.})

    def test_scaled_fields_preserve_signed_local_and_legacy_key(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            left, right = root/"g", root/"b"
            left.mkdir(); right.mkdir()
            self.fixture(left, m=0)
            self.fixture(right, m=1)
            def synthetic_observable(g, b, quadrature):
                local = -.25 if quadrature == 14 else .25
                return dict(L_center_over_minus_i_hbar=local,
                            L_O_over_minus_i_hbar=local+6.,
                            p_x_over_minus_i_hbar=.5625, dipole_x=.5,
                            origin_center="B", origin_shift_center_to_O=32./3)
            with patch("fast_observables.direct_observables", side_effect=synthetic_observable) as mock:
                result = adapter.observe_pair(left, right, orders=(14, 22))
            self.assertEqual(mock.call_count, 2)
            for order, sign in (("14", 1), ("22", -1)):
                value = result["direct"][order]
                self.assertEqual(value["Q_B"], sign*256.)
                self.assertEqual(value["Q_O"], value["L_O_bar"]/32.)
                self.assertEqual(value["L_O_scaled"], value["L_O_bar"]/32.**3)
                self.assertEqual(value["L_B_bar"], -sign*.25)
            self.assertEqual(result["new_eigensolves"], 0)


if __name__ == "__main__":
    unittest.main()
