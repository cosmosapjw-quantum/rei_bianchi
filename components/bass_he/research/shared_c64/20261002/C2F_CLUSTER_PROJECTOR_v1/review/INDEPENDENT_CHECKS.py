"""Independent C2f matrix counterexamples; no molecular/continuum solve."""
from pathlib import Path
import dataclasses
import hashlib
import io
import json
import os
import sys
import unittest
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
import projector as p


def unitary(n, rng):
    q, r = np.linalg.qr(rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n)))
    d = np.diag(r)
    return q * (d / np.abs(d)).conj()[None, :]


def representation(identity="grid-independent-v1", coverage="finite_sector_subset"):
    return p.Representation(identity, "metric-independent-v1", "manufactured-C4", "finite-diagonal", "dimensionless", "dimensionless", "independent-manufactured", "0" * 64, coverage, (0,), False, 0.0)


def snapshot(frame, energies, roles, *, coordinate=1.0, identity="grid-independent-v1", coverage="finite_sector_subset"):
    states = tuple(p.StateRecord(p.StateID(f"state-{i}"), 0, float(e), 0.0, r) for i, (e, r) in enumerate(zip(energies, roles)))
    return p.Snapshot(coordinate, np.asarray(frame, dtype=np.complex128), np.ones(frame.shape[0], dtype=np.float64), states, representation(identity, coverage))


def target(rank):
    return p.TargetSpec("independent-finite-cluster", p.TargetKind.FULL_ENERGY, ((0, rank),), False, "explicit manufactured span only")


def transport(u, v, w, **kw):
    args = dict(sigma_min=0.1, gram_atol=1e-10, backend="reference")
    args.update(kw)
    return p.transport_frames(np.asarray(u, dtype=np.complex128), np.asarray(v, dtype=np.complex128), np.asarray(w, dtype=np.float64), **args)


class IndependentChecks(unittest.TestCase):
    def test_weighted_projector_against_dense_projector(self):
        rng = np.random.default_rng(2026100201)
        n, k = 17, 5
        a = unitary(n, rng)
        theta = np.array([0.002, 0.01, 0.03, 0.07, 0.12])
        x = a[:, :k]
        y = x * np.cos(theta) + a[:, k:2*k] * np.sin(theta)
        w = np.geomspace(0.01, 100.0, n)
        t = transport(x / np.sqrt(w)[:, None], y / np.sqrt(w)[:, None], w)
        dense = x @ x.conj().T - y @ y.conj().T
        self.assertAlmostEqual(t.projector_operator_distance, np.linalg.norm(dense, 2), delta=3e-14)
        self.assertAlmostEqual(t.projector_frobenius_distance, np.linalg.norm(dense, 'fro'), delta=3e-14)

    def test_complex_unitary_covariance_at_internal_degeneracy(self):
        rng = np.random.default_rng(2026100202)
        n, k = 13, 3
        a = unitary(n, rng)
        u = a[:, :k]
        v = (u * np.cos(0.05) + a[:, k:2*k] * np.sin(0.05)) @ unitary(k, rng)
        s, q = unitary(k, rng), unitary(k, rng)
        t0 = transport(u, v, np.ones(n))
        t1 = transport(u @ s, v @ q, np.ones(n))
        self.assertLess(np.linalg.norm(t1.aligned_frame - t0.aligned_frame @ s), 8e-14)
        self.assertLess(np.linalg.norm(t1.right_rotation - q.conj().T @ t0.right_rotation @ s), 8e-14)

    def test_near_orthonormal_same_span_is_not_fake_distance(self):
        rng = np.random.default_rng(2026100203)
        n, k = 11, 3
        base = unitary(n, rng)[:, :k]
        h = np.array([[2, 1j, 0.5], [-1j, -1, 0], [0.5, 0, 1]], dtype=complex)
        u = base @ (np.eye(k) + 1e-5 * h)
        v = base @ unitary(k, rng) @ np.diag([1.00001, 0.99999, 1.00002])
        t = transport(u, v, np.ones(n), gram_atol=1e-3)
        self.assertLess(t.projector_operator_distance, 4e-14)
        self.assertLess(np.linalg.norm(t.aligned_frame.conj().T @ t.aligned_frame - np.eye(k)), 4e-14)

    def test_tiny_angle_residual_survives_overlap_roundoff(self):
        theta = 1e-10
        u = np.array([[1], [0], [0]], dtype=complex)
        v = np.array([[np.cos(theta)], [np.sin(theta)], [0]], dtype=complex)
        t = transport(u, v, np.ones(3))
        self.assertAlmostEqual(t.projector_operator_distance, theta, delta=1e-24)
        self.assertAlmostEqual(float(t.principal_angles[0]), theta, delta=1e-24)

    def test_small_principal_overlap_rejected(self):
        u = np.eye(3, dtype=complex)[:, :1]
        v = np.array([[0.01], [np.sqrt(1-0.01**2)], [0]], dtype=complex)
        with self.assertRaises(p.TransportRejected):
            transport(u, v, np.ones(3), sigma_min=0.1)

    def test_rank_mismatch_rejected(self):
        with self.assertRaises(p.ContractError):
            transport(np.eye(3, dtype=complex)[:, :1], np.eye(3, dtype=complex)[:, :2], np.ones(3))

    def test_missing_dark_partner_rejected(self):
        snap = snapshot(np.eye(4, dtype=complex), [-2, -0.5, -0.5, 1], [p.Role.SELECTED, p.Role.SELECTED, p.Role.GUARD, p.Role.GUARD], coverage="finite_full_ambient")
        states = list(snap.states)
        states[1] = dataclasses.replace(states[1], known_degenerate_partners=(states[2].state_id,))
        states[2] = dataclasses.replace(states[2], known_degenerate_partners=(states[1].state_id,))
        snap = dataclasses.replace(snap, states=tuple(states))
        with self.assertRaises(p.ContractError):
            p.validate_snapshot(snap, target(2), p.ValidationTolerances(1e-12, 1e-12, 1e-12, 1e-8), backend="reference")

    def test_internal_degeneracy_with_complete_finite_frame(self):
        snap = snapshot(np.eye(5, dtype=complex), [-2, -0.5, -0.5, -0.5, 1], [p.Role.GUARD, p.Role.SELECTED, p.Role.SELECTED, p.Role.SELECTED, p.Role.GUARD], coverage="finite_full_ambient")
        d = p.validate_snapshot(snap, target(3), p.ValidationTolerances(1e-12, 1e-12, 1e-12, 1e-8), backend="reference")
        self.assertEqual(d.internal_min_splitting, 0.0)
        self.assertEqual(d.observed_guard_gap, 1.5)
        self.assertTrue(d.supplied_frame_spans_finite_ambient)
        self.assertFalse(d.full_H_certificate)
        self.assertFalse(d.continuum_certificate)

    def test_incomplete_guards_do_not_certify_hidden_degeneracy(self):
        # Actual manufactured H=diag(-0.5,-0.5,1), omitted second state.
        snap = snapshot(np.eye(3, dtype=complex)[:, [0, 2]], [-0.5, 1], [p.Role.SELECTED, p.Role.GUARD])
        d = p.validate_snapshot(snap, target(1), p.ValidationTolerances(1e-12, 1e-12, 1e-12, 1e-8), backend="reference")
        self.assertEqual(d.observed_guard_gap, 1.5)
        self.assertFalse(d.supplied_frame_spans_finite_ambient)
        self.assertFalse(d.full_H_certificate)
        self.assertFalse(d.continuum_certificate)

    def test_cross_coordinate_embedding_mismatch_rejected(self):
        snap = snapshot(np.eye(3, dtype=complex), [-1, 0, 1], [p.Role.SELECTED, p.Role.GUARD, p.Role.GUARD], coverage="finite_full_ambient")
        other = dataclasses.replace(snap, coordinate=2.0, representation=representation("different-grid", "finite_full_ambient"))
        with self.assertRaises(p.ContractError):
            p.parallel_transport(snap, other, target(1), p.ValidationTolerances(1e-12, 1e-12, 1e-12, 1e-8), sigma_min=0.1, backend="reference")

    def test_mixed_small_hamiltonian_matches_finite_operator(self):
        theta = 0.37
        q = np.array([[np.cos(theta), 1j*np.sin(theta)], [1j*np.sin(theta), np.cos(theta)]])
        e = np.eye(4, dtype=complex)
        prev = snapshot(e, [-2, -1, 1, 2], [p.Role.SELECTED, p.Role.SELECTED, p.Role.GUARD, p.Role.GUARD])
        v = e.copy(); v[:, :2] = e[:, :2] @ q
        cur = snapshot(v, [-2, -1, 1, 2], [p.Role.SELECTED, p.Role.SELECTED, p.Role.GUARD, p.Role.GUARD], coordinate=2)
        out = p.parallel_transport(prev, cur, target(2), p.ValidationTolerances(1e-12, 1e-12, 1e-12, 1e-8), sigma_min=0.1, backend="reference")
        h = v @ np.diag([-2., -1., 1., 2.]) @ v.conj().T
        f = out.transport.aligned_frame
        self.assertLess(np.linalg.norm(h @ f - f @ out.transformed_ritz_operator), 1e-13)
        self.assertGreater(np.linalg.norm(h @ f - f @ np.diag([-2., -1.])), 0.1)
        self.assertFalse(out.aligned_columns_are_individual_eigenstates)
        self.assertFalse(out.continuum_certificate)

    def test_supplied_projected_form_with_gram_whitening(self):
        theta = 0.37
        q = np.array([[np.cos(theta), 1j*np.sin(theta)], [1j*np.sin(theta), np.cos(theta)]])
        e = np.eye(4, dtype=complex)
        prev = snapshot(e, [-2, -1, 1, 2], [p.Role.SELECTED, p.Role.SELECTED, p.Role.GUARD, p.Role.GUARD])
        physical = e.copy(); physical[:, :2] = e[:, :2] @ q
        h = physical @ np.diag([-2., -1., 1., 2.]) @ physical.conj().T
        v = physical.copy(); v[:, :2] = physical[:, :2] @ np.diag([1.00001, 0.99999])
        cur = snapshot(v, [-2, -1, 1, 2], [p.Role.SELECTED, p.Role.SELECTED, p.Role.GUARD, p.Role.GUARD], coordinate=2)
        cur = dataclasses.replace(cur, selected_projected_operator=v[:, :2].conj().T @ h @ v[:, :2])
        out = p.parallel_transport(prev, cur, target(2), p.ValidationTolerances(1e-3, 1e-12, 1e-12, 1e-8), sigma_min=0.1, backend="reference")
        f = out.transport.aligned_frame
        self.assertLess(np.linalg.norm(h @ f - f @ out.transformed_ritz_operator), 1e-13)
        self.assertTrue(out.actual_operator_projection_supplied)
        self.assertFalse(out.actual_ritz_residual_certified)

    def test_raw_residual_defect_bound(self):
        rng = np.random.default_rng(2026100204)
        a = unitary(8, rng)
        x = a[:, :2] @ np.diag([1.0001, 0.9999])
        y = (a[:, :2]*np.cos(0.07)+a[:, 2:4]*np.sin(0.07)) @ np.diag([1.0002,0.9998])
        gu, gv = x.conj().T @ x, y.conj().T @ y
        eu, ev = np.linalg.norm(gu-np.eye(2),2), np.linalg.norm(gv-np.eye(2),2)
        r0 = np.linalg.norm(y-x @ (x.conj().T @ y), 2)
        qx=np.linalg.qr(x)[0];qy=np.linalg.qr(y)[0]
        d=np.linalg.norm(qx @ qx.conj().T-qy @ qy.conj().T,2)
        lower=max(0,r0/np.sqrt(1+ev)-eu);upper=min(1,r0/np.sqrt(1-ev)+eu)
        self.assertLessEqual(lower,d);self.assertLessEqual(d,upper)


def main():
    output = Path(sys.argv[1]) if len(sys.argv) == 2 else ROOT / "review/INDEPENDENT_CHECKS.json"
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(IndependentChecks))
    files = [ROOT / "code/projector.py", Path(__file__), ROOT / "math/PROJECTOR_TRANSPORT_DERIVATION_KO.md"]
    record = {
        "schema": "bass-he.c2f.independent-checks.v1", "checks_run": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors), "successful": result.wasSuccessful(),
        "scope": "independent manufactured finite-dimensional algebra and claim-separation checks",
        "physical_eigensolves": 0, "molecular_quadratures": 0, "continuum_certificate": False,
        "author_tests_imported": False, "numpy_version": np.__version__, "test_log": stream.getvalue(),
        "input_identities": [{"path": str(f.relative_to(ROOT)), "bytes": f.stat().st_size, "sha256": hashlib.sha256(f.read_bytes()).hexdigest()} for f in files]
    }
    tmp = output.with_suffix(output.suffix + ".pending")
    with open(tmp, "x") as f:
        json.dump(record, f, indent=2); f.write("\n"); f.flush(); os.fsync(f.fileno())
    os.link(tmp, output); tmp.unlink()
    fd=os.open(output.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)
    print(stream.getvalue(),end="")
    print(json.dumps({"checks_run":result.testsRun,"successful":result.wasSuccessful(),"output":str(output)}))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
