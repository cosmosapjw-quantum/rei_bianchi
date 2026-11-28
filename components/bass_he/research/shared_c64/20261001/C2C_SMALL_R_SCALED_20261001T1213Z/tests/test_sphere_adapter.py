"""Synthetic archive checks only: no physical eigensolve or coupling integral."""
from io import BytesIO
import hashlib
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


class SphereArchiveTests(unittest.TestCase):
    def fixture(self, folder):
        configuration = dict(R=.125, m=0, lmax=0, elements=4, degree=2,
                             rmax=1., quadrature=6, nroots=2, center="B", tol=1e-11)
        boundaries = np.array([0., .125, .25, .5, 1.])
        coefficients = np.array([[0., .1, .2, .3, .4, .5, .4, .2, 0.]])
        metadata = dict(origin_center="B", origin_shift_center_to_O=.125/3,
                        nuclear_positions=[-.125, 0.], degree=2, angular_lmax=0,
                        rmax=1., explicit_boundaries=boundaries.tolist())
        state = PartialWaveState(.125, 1., 2., 0, np.array([0]), boundaries,
                                 2, coefficients, -4., 1e-12, 1., 0., metadata)
        with patch("optimized_solver.solve", return_value=state) as solve:
            value = adapter.solve_one(configuration, folder)
            self.assertEqual(solve.call_count, 1)
        data = dict(parameters=dict(kind="sphere", configuration=configuration), value=value)
        (folder/"DATA.json").write_text(json.dumps(data))
        return data, state

    def test_roundtrip_and_no_solve_on_read(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            _, original = self.fixture(folder)
            with patch("optimized_solver.solve", side_effect=AssertionError("read cannot solve")):
                restored = adapter.load_one(folder)
            np.testing.assert_array_equal(original.coefficients, restored.coefficients)
            self.assertGreater(restored.phase_probe, 0.)
            self.assertEqual(restored.energy, original.energy)

    def test_create_only_guard_precedes_solve(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            data, _ = self.fixture(folder)
            with patch("optimized_solver.solve", side_effect=AssertionError("duplicate cannot solve")):
                with self.assertRaises(FileExistsError):
                    adapter.solve_one(data["parameters"]["configuration"], folder)

    def test_byte_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            self.fixture(folder)
            with (folder/"STATE.npz").open("ab") as stream:
                stream.write(b"corrupt")
            with self.assertRaisesRegex(ValueError, "size/SHA"):
                adapter.load_one(folder)

    def test_rehashed_bad_boundary_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            data, state = self.fixture(folder)
            coefficients = state.coefficients.copy()
            coefficients[0, 0] = 1.
            stream = BytesIO()
            np.savez_compressed(stream, coefficients=coefficients, ls=state.ls,
                                boundaries=state.boundaries)
            raw = stream.getvalue()
            (folder/"STATE.npz").write_bytes(raw)
            data["value"].update(state_bytes=len(raw), state_sha256=hashlib.sha256(raw).hexdigest())
            (folder/"DATA.json").write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "boundary conditions"):
                adapter.load_one(folder)

    def test_phase_tamper_rejected_without_refitting(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            data, _ = self.fixture(folder)
            data["value"]["phase_probe"] *= -1
            (folder/"DATA.json").write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "phase probe"):
                adapter.load_one(folder)

    def test_order_validation_precedes_archives(self):
        for orders in ((14, 14), (22, 14), (True,), (), (1.5,)):
            with self.assertRaisesRegex(ValueError, "orders"):
                adapter.observe_pair("absent", "absent", orders)


if __name__ == "__main__":
    unittest.main()
