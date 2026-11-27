"""New C2g manufactured/mocked checks: no physical molecular eigensolve."""
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from scipy import sparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"code"))
import optimized_solver as solver
from multistate_provider import save_sector, load_sector, validate_identity


def fixture():
    mass = np.arange(1., 8.)
    energy = np.array([-3., -1., 2., 4., 5., 6., 7.])
    H, M = sparse.diags(mass*energy), sparse.diags(mass)
    vec = np.zeros((7, 3))
    vec[2, 0] = -4.
    vec[0, 1] = 3.
    vec[1, 2] = -2.
    result = solver._finish_eigenpairs(H, M, energy[[2, 0, 1]], vec,
        R=4., ZA=1., ZB=2., m=0, ls=np.array([0], np.int64),
        boundaries=np.array([0., 1., 2., 3., 4.]), degree=2, nroots=3,
        metadata={"backend": "manufactured-test", "source_files_sha256": {"fixture": "a"*64}})
    return result, H, M


class MultiStateTests(unittest.TestCase):
    def test_all_distinct_sorted_and_phase(self):
        r, H, M = fixture()
        self.assertEqual([s.energy for s in r.states], [-3., -1., 2.])
        self.assertEqual([s.metadata["source_ordinal"] for s in r.states], [0, 1, 2])
        np.testing.assert_allclose(r.mass_gram, np.eye(3), atol=3e-16)
        np.testing.assert_allclose(r.projected_operator, np.diag([-3., -1., 2.]), atol=5e-16)
        np.testing.assert_array_equal(np.argmax(abs(r.coefficient_vectors), axis=0), [0, 1, 2])
        self.assertTrue(np.all(r.coefficient_vectors[np.arange(3), np.arange(3)] > 0))
        np.testing.assert_allclose(r.projected_operator, r.coefficient_vectors.T @ H @ r.coefficient_vectors)
        self.assertTrue(all(s.residual < 1e-15 for s in r.states))
        self.assertFalse(r.coefficient_vectors.flags.writeable)

    def test_relative_residual_measured_not_claimed(self):
        r, H, M = fixture()
        vec = r.coefficient_vectors.copy()
        vec[5, 1] = .03
        t = solver._finish_eigenpairs(H, M, np.array([-3., -1., 2.]), vec,
            R=4., ZA=1., ZB=2., m=0, ls=r.states[0].ls,
            boundaries=r.states[0].boundaries, degree=2, nroots=3, metadata={})
        c = t.coefficient_vectors[:, 1]
        expected = np.linalg.norm(H@c + M@c)/(np.linalg.norm(H@c)+np.linalg.norm(M@c))
        self.assertEqual(t.states[1].residual, expected)
        self.assertGreater(t.states[1].residual, 0.01)
        self.assertIn("not a dimensional PDE", t.metadata["residual_definition"])

    def test_nonfinite_and_mass_invalid(self):
        r, H, M = fixture()
        kwargs = dict(R=4., ZA=1., ZB=2., m=0, ls=r.states[0].ls,
            boundaries=r.states[0].boundaries, degree=2, nroots=3, metadata={})
        for eig, mat in [(np.array([-3., np.nan, 2.]), M), (np.array([-3., -1., 2.]), -M)]:
            with self.assertRaises(ArithmeticError):
                solver._finish_eigenpairs(H, mat, eig, r.coefficient_vectors, **kwargs)

    def test_mocked_eigsh_once_preserves_three_vectors(self):
        def fake(H, **kwargs):
            k = kwargs["k"]
            self.assertEqual(k, 3)
            v = np.zeros((H.shape[0], k))
            v[[2, 0, 1], np.arange(k)] = [-2., 1., -3.]
            return np.array([2., -3., -1.]), v
        with patch.object(solver, "eigsh", side_effect=fake) as mock:
            r = solver.solve_many(0., lmax=0, elements=4, degree=2,
                                  nroots=3, backend="numpy")
        self.assertEqual(mock.call_count, 1)
        self.assertEqual(len(r.states), 3)
        np.testing.assert_array_equal(np.argmax(abs(r.coefficient_vectors), axis=0), [0, 1, 2])
        self.assertEqual(r.metadata["backend"], "numpy")
        self.assertIn("optimized_solver.py", r.metadata["source_files_sha256"])

    def test_invalid_roots_before_eigsh(self):
        for roots in (0, -1, 1.5, True, np.nan, np.inf, 7, 8):
            with self.subTest(roots=roots), patch.object(solver, "eigsh") as mock:
                with self.assertRaises(ValueError):
                    solver.solve_many(0., lmax=0, elements=4, degree=2,
                                      nroots=roots, backend="numpy")
                mock.assert_not_called()

    def test_legacy_solve_returns_first_once(self):
        result, _, _ = fixture()
        with patch.object(solver, "solve_many", return_value=result) as mock:
            state = solver.solve(4., nroots=3, backend="numpy")
        self.assertEqual(mock.call_count, 1)
        self.assertEqual(state.energy, -3.)
        self.assertGreaterEqual(state.phase_probe, 0)
        self.assertEqual(state.metadata["ritz_eigenvalues"], [-3., -1., 2.])
        self.assertIsNot(state.coefficients, result.states[0].coefficients)

    def test_archive_roundtrip_binding_and_create_only(self):
        r, _, _ = fixture()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/"sector.npz"
            receipt = save_sector(r, path, "R4-m0-L0")
            archive = load_sector(path, receipt["source_sha256"])
            self.assertEqual(archive.state_ids, tuple(f"R4-m0-L0:root:{j:04d}" for j in range(3)))
            self.assertEqual(archive.source_bytes, path.stat().st_size)
            np.testing.assert_array_equal(archive.result.coefficient_vectors, r.coefficient_vectors)
            np.testing.assert_array_equal(archive.result.projected_operator, r.projected_operator)
            self.assertFalse(archive.result.states[0].coefficients.flags.writeable)
            validate_identity(archive)
            with self.assertRaises(FileExistsError):
                save_sector(r, path, "R4-m0-L0")
            with self.assertRaises(ValueError):
                load_sector(path, "b"*64)
            path.write_bytes(path.read_bytes()+b"corruption")
            with self.assertRaises(ValueError):
                validate_identity(archive)

    def test_in_memory_provenance_mutation_rejected(self):
        r, _, _ = fixture()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/"sector.npz"
            save_sector(r, path, "fixture")
            archive = load_sector(path)
            archive.result.states[1].energy = -99.
            with self.assertRaises(ValueError):
                validate_identity(archive)

    def test_invalid_source_and_provenance(self):
        r, _, _ = fixture()
        with tempfile.TemporaryDirectory() as td:
            for value in ("", "spaces bad", "한글", 0):
                with self.assertRaises(ValueError):
                    save_sector(r, Path(td)/"bad.npz", value)
            r.metadata.pop("source_files_sha256")
            with self.assertRaises(ValueError):
                save_sector(r, Path(td)/"bad.npz", "valid")

    def test_state_coefficient_or_ordinal_mismatch_rejected(self):
        for kind in ("coeff", "ordinal", "nan", "residual_definition"):
            r, _, _ = fixture()
            if kind == "coeff": r.states[0].coefficients[0, 1] += .1
            if kind == "ordinal": r.states[0].metadata["source_ordinal"] = 1
            if kind == "nan": r.metadata["invalid"] = float("nan")
            if kind == "residual_definition": r.states[0].metadata["residual_definition"] = "PDE"
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as td:
                with self.assertRaises(ValueError):
                    save_sector(r, Path(td)/"bad.npz", "valid")

    def test_object_archive_rejected(self):
        r, _, _ = fixture()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/"sector.npz"
            save_sector(r, path, "fixture")
            with np.load(path, allow_pickle=False) as z:
                arrays = {k:z[k] for k in z.files}
            arrays["coefficients"] = np.array([object()], dtype=object)
            np.savez(path, **arrays)
            with self.assertRaises(ValueError):
                load_sector(path)

    def test_duplicate_json_keys_rejected(self):
        r, _, _ = fixture()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/"sector.npz"
            save_sector(r, path, "fixture")
            with np.load(path, allow_pickle=False) as z:
                arrays = {k:z[k] for k in z.files}
            doc = arrays["metadata_json"].tobytes().decode()
            arrays["metadata_json"] = np.frombuffer(("{\"schema\":\"bad\","+doc[1:]).encode(), dtype=np.uint8)
            np.savez(path, **arrays)
            with self.assertRaises(ValueError):
                load_sector(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
