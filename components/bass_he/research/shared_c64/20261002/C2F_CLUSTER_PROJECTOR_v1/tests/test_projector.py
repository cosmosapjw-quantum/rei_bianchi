"""Manufactured contract tests; no Coulomb solver or inherited C2 tolerances."""
import dataclasses
import hashlib
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from projector import (ContractError, TransportRejected, Role, TargetKind, StateID,
    StateRecord, Representation, Snapshot, TargetSpec, ValidationTolerances,
    validate_snapshot, weighted_overlap, transport_frames, parallel_transport)

# Registered in C2F_IMPLEMENTATION_CONTRACT.json for manufactured examples only.
TOL = ValidationTolerances(1e-10, 1e-12, 1e-10, 1e-8)
BACKEND = {"backend": "reference"}


def representation(sectors=(0, 1, -1), axial=True, coverage="finite_full_ambient"):
    return Representation("manufactured:common-seven-row:v1", "positive-diagonal:v1",
        "manufactured:finite:C7", "zero-offset:v1", "synthetic-energy", "synthetic-coordinate",
        "analytical-orthogonal-fixture", hashlib.sha256(b"C2f manufactured fixture v1").hexdigest(),
        coverage, sectors, axial, 0.0)


def fixture():
    weights = np.linspace(0.7, 1.8, 7, dtype=np.float64)
    vectors = np.diag(1 / np.sqrt(weights)).astype(np.complex128)
    records = tuple(StateRecord(StateID(f"s{i}"), m, e, 1e-14, role, i == 0)
                    for i, (m, e, role) in enumerate([
                        (0, -2.0, Role.GUARD), (0, -0.6, Role.SELECTED),
                        (0, -0.5, Role.SELECTED), (0, -0.4, Role.SELECTED),
                        (1, -0.45, Role.SELECTED), (-1, -0.45, Role.SELECTED),
                        (0, 0.2, Role.GUARD)]))
    return Snapshot(2.0, vectors, weights, records, representation())


def unitary(n, seed):
    rng = np.random.default_rng(seed)
    q, _ = np.linalg.qr(rng.normal(size=(n, n)) + 1j*rng.normal(size=(n, n)))
    return np.asarray(q, dtype=np.complex128)


def angle_frames(angles):
    k = len(angles)
    weights = np.linspace(0.4, 2.0, 2*k, dtype=np.float64)
    u = np.vstack([np.eye(k), np.zeros((k, k))]).astype(np.complex128)
    v = np.vstack([np.diag(np.cos(angles)), np.diag(np.sin(angles))]).astype(np.complex128)
    return u/np.sqrt(weights[:, None]), v/np.sqrt(weights[:, None]), weights


class ContractTests(unittest.TestCase):
    def test_rank5_and_no_certificate(self):
        d = validate_snapshot(fixture(), TargetSpec.large_R_rank5(), TOL, **BACKEND)
        self.assertEqual(d.selected_rank, 5)
        self.assertEqual(d.guard_count, 2)
        self.assertAlmostEqual(d.internal_min_splitting, 0)
        self.assertAlmostEqual(d.observed_guard_gap, 0.6)
        self.assertFalse(d.continuum_certificate)
        self.assertFalse(d.full_H_certificate)
        self.assertFalse(d.atomic_correlation_established)
        self.assertFalse(d.every_selected_sector_has_guard)
        self.assertTrue(d.supplied_frame_spans_finite_ambient)

    def test_wrong_rank_contract_rejected(self):
        t = TargetSpec("wrong", TargetKind.FULL_ENERGY, ((0, 4), (1, 1)), True, "test")
        with self.assertRaisesRegex(ContractError, "sector ranks"):
            validate_snapshot(fixture(), t, TOL, **BACKEND)

    def test_known_guard_degeneracy_rejected(self):
        s = fixture()
        states = list(s.states)
        states[-1] = dataclasses.replace(states[-1], energy=-0.45)
        with self.assertRaisesRegex(ContractError, "energy-boundary"):
            validate_snapshot(dataclasses.replace(s, states=tuple(states)), TargetSpec.large_R_rank5(), TOL, **BACKEND)

    def test_near_exterior_gap_below_registered_floor_rejected(self):
        s = fixture()
        states = list(s.states)
        states[-1] = dataclasses.replace(states[-1], energy=-0.4+2e-9)
        with self.assertRaisesRegex(ContractError, "energy-boundary"):
            validate_snapshot(dataclasses.replace(s, states=tuple(states)), TargetSpec.large_R_rank5(), TOL, **BACKEND)

    def test_guard_in_other_sector_allowed_only_for_sector_target(self):
        s = fixture()
        states = list(s.states)
        states[5] = dataclasses.replace(states[5], role=Role.GUARD)
        t = TargetSpec("sector-direct-sum", TargetKind.SYMMETRY_BLOCKS, ((0, 3), (1, 1)), True, "explicit sectors")
        reduced = dataclasses.replace(s, states=tuple(states))
        d = validate_snapshot(reduced, t, TOL, **BACKEND)
        self.assertIn("same-m", d.guard_gap_scope)
        self.assertFalse(d.full_H_certificate)
        with self.assertRaises(ContractError):
            validate_snapshot(reduced, dataclasses.replace(t, kind=TargetKind.FULL_ENERGY), TOL, **BACKEND)

    def test_absent_opposite_m_partner_rejected(self):
        s = fixture()
        keep = [0, 1, 2, 3, 4, 6]
        s = dataclasses.replace(s, vectors=s.vectors[:, keep], states=tuple(s.states[i] for i in keep),
             representation=dataclasses.replace(s.representation, sectors_present=(0, 1), spectrum_coverage="finite_sector_subset"))
        t = TargetSpec("incomplete-pi", TargetKind.FULL_ENERGY, ((0, 3), (1, 1)), True, "test")
        with self.assertRaisesRegex(ContractError, "axial"):
            validate_snapshot(s, t, TOL, **BACKEND)

    def test_partner_metadata_identifies_unprovided_dark_state(self):
        s = fixture()
        states = list(s.states)
        states[1] = dataclasses.replace(states[1], known_degenerate_partners=(StateID("missing-dark"),))
        with self.assertRaisesRegex(ContractError, "partner is omitted"):
            validate_snapshot(dataclasses.replace(s, states=tuple(states)), TargetSpec.large_R_rank5(), TOL, **BACKEND)

    def test_incomplete_guard_list_never_certifies(self):
        s = fixture()
        keep = s.selected_indices
        s = dataclasses.replace(s, vectors=s.vectors[:, keep], states=tuple(s.states[i] for i in keep),
                               representation=dataclasses.replace(s.representation, spectrum_coverage="finite_sector_subset"))
        d = validate_snapshot(s, TargetSpec.large_R_rank5(), TOL, **BACKEND)
        self.assertIsNone(d.observed_guard_gap)
        self.assertIsNone(d.observed_guard_gap_exceeds_floor)
        self.assertFalse(d.supplied_frame_spans_finite_ambient)
        # Pure geometric alignment is allowed, explicitly without isolation evidence.
        result = parallel_transport(s, s, TargetSpec.large_R_rank5(), TOL, sigma_min=0.2, **BACKEND)
        self.assertFalse(result.continuum_certificate)
        self.assertIsNone(result.current_diagnostics.observed_guard_gap)

    def test_selected_and_guard_full_orthogonality_checked(self):
        s = fixture()
        v = s.vectors.copy()
        v[:, -1] += 1e-4 * v[:, 1]
        with self.assertRaisesRegex(ContractError, "orthonormal"):
            validate_snapshot(dataclasses.replace(s, vectors=v), TargetSpec.large_R_rank5(), TOL, **BACKEND)

    def test_guard_guard_orthogonality_checked(self):
        s = fixture()
        v = s.vectors.copy()
        v[:, -1] += 1e-4 * v[:, 0]
        with self.assertRaises(ContractError):
            validate_snapshot(dataclasses.replace(s, vectors=v), TargetSpec.large_R_rank5(), TOL, **BACKEND)

    def test_residual_limit_applies_to_guard(self):
        s = fixture()
        states = list(s.states)
        states[-1] = dataclasses.replace(states[-1], residual_norm=2e-10)
        with self.assertRaisesRegex(ContractError, "residual"):
            validate_snapshot(dataclasses.replace(s, states=tuple(states)), TargetSpec.large_R_rank5(), TOL, **BACKEND)

    def test_ground_policy(self):
        s = fixture()
        states = list(s.states)
        states[1] = dataclasses.replace(states[1], is_ground=True)
        with self.assertRaisesRegex(ContractError, "ground"):
            validate_snapshot(dataclasses.replace(s, states=tuple(states)), TargetSpec.large_R_rank5(), TOL, **BACKEND)

    def test_declared_sectors_and_typed_ids(self):
        s = fixture()
        with self.assertRaisesRegex(ContractError, "declared sectors"):
            dataclasses.replace(s, representation=dataclasses.replace(s.representation, sectors_present=(0,)))
        with self.assertRaises(ContractError):
            StateRecord("text-not-StateID", 0, -1.0, 0.0, Role.SELECTED)
        with self.assertRaises(ContractError):
            StateRecord(StateID("bad"), True, -1.0, 0.0, Role.SELECTED)

    def test_weights_and_binary64_mandatory(self):
        s = fixture()
        for w in (s.weights.astype(np.float32), -s.weights, s.weights.astype(np.complex128)):
            with self.assertRaises(ContractError):
                dataclasses.replace(s, weights=w)
        with self.assertRaises(ContractError):
            dataclasses.replace(s, vectors=s.vectors.astype(np.complex64))

    def test_nonfinite_and_duplicate_identity_rejected(self):
        s = fixture()
        with self.assertRaises(ContractError):
            dataclasses.replace(s, coordinate=float("nan"))
        states = list(s.states)
        states[-1] = dataclasses.replace(states[-1], state_id=states[0].state_id)
        with self.assertRaisesRegex(ContractError, "unique"):
            dataclasses.replace(s, states=tuple(states))

    def test_copied_snapshot_is_not_mutated_by_input_alias(self):
        s = fixture()
        original = s.vectors.copy()
        owned = dataclasses.replace(s, vectors=original)
        original[:] = 0
        self.assertGreater(np.linalg.norm(owned.vectors), 1)
        self.assertFalse(owned.vectors.flags.writeable)
        with self.assertRaises(ValueError):
            owned.weights[0] = 0


class TransportTests(unittest.TestCase):
    def test_analytic_principal_angles_and_projectors(self):
        angles = np.array([0.03, 0.2, 0.41], dtype=np.float64)
        u, v, w = angle_frames(angles)
        r = transport_frames(u, v, w, sigma_min=0.2, gram_atol=TOL.gram_atol, **BACKEND)
        np.testing.assert_allclose(r.principal_angles, angles, atol=2e-14, rtol=0)
        self.assertAlmostEqual(r.projector_operator_distance, np.sin(angles[-1]), places=14)
        self.assertAlmostEqual(r.projector_frobenius_distance, np.sqrt(2*np.sum(np.sin(angles)**2)), places=14)
        z = np.sqrt(w)[:, None]
        projector_delta = (z*u)@(z*u).conj().T - (z*v)@(z*v).conj().T
        self.assertAlmostEqual(r.projector_operator_distance, np.linalg.norm(projector_delta, 2), places=14)
        self.assertAlmostEqual(r.projector_frobenius_distance, np.linalg.norm(projector_delta, "fro"), places=14)

    def test_unitary_covariance(self):
        u, v, w = angle_frames(np.array([0.11, 0.21, 0.3]))
        c, d = unitary(3, 61), unitary(3, 92)
        r = transport_frames(u, v, w, sigma_min=0.2, gram_atol=TOL.gram_atol, **BACKEND)
        rp = transport_frames(u@c, v@d, w, sigma_min=0.2, gram_atol=TOL.gram_atol, **BACKEND)
        np.testing.assert_allclose(rp.aligned_frame, r.aligned_frame@c, atol=2e-14, rtol=0)
        np.testing.assert_allclose(rp.singular_values, r.singular_values, atol=2e-14, rtol=0)
        positive_overlap = weighted_overlap(u, r.aligned_frame, w, **BACKEND)
        np.testing.assert_allclose(positive_overlap, positive_overlap.conj().T, atol=2e-14, rtol=0)
        self.assertGreater(np.linalg.eigvalsh(positive_overlap)[0], 0)

    def test_internal_degenerate_rotation_does_not_change_projector(self):
        u, _, w = angle_frames(np.array([0.0, 0.0, 0.0]))
        r = transport_frames(u, u@unitary(3, 214), w, sigma_min=0.2, gram_atol=TOL.gram_atol, **BACKEND)
        np.testing.assert_allclose(r.aligned_frame, u, atol=2e-14, rtol=0)
        self.assertLess(r.projector_operator_distance, 2e-14)

    def test_tiny_angle_not_lost_to_one_minus_sigma_squared(self):
        u, v, w = angle_frames(np.array([1e-10]))
        r = transport_frames(u, v, w, sigma_min=0.2, gram_atol=TOL.gram_atol, **BACKEND)
        self.assertAlmostEqual(r.projector_operator_distance/1e-10, 1.0, places=10)
        self.assertAlmostEqual(r.principal_angles[0]/1e-10, 1.0, places=10)

    def test_gram_whitening_is_recorded_and_same_span_has_zero_distance(self):
        u, _, w = angle_frames(np.array([0.0, 0.0]))
        v = u @ np.diag([1+1e-12, 1-2e-12]).astype(np.complex128)
        r = transport_frames(u, v, w, sigma_min=0.2, gram_atol=TOL.gram_atol, **BACKEND)
        self.assertGreater(r.current_normalization_correction_norm, 1e-12)
        self.assertIn("explicit", r.normalization_policy)
        self.assertLess(r.projector_operator_distance, 2e-14)
        np.testing.assert_allclose(v@r.source_basis_transform, r.aligned_frame, atol=2e-14, rtol=0)

    def test_rank_deficient_gram_cannot_hide_behind_entrywise_tolerance(self):
        frame = (np.eye(11) - np.ones((11, 11))/11).astype(np.complex128)
        with self.assertRaisesRegex(ContractError, "Gram defect"):
            transport_frames(frame, frame, np.ones(11), sigma_min=0.2, gram_atol=0.1, **BACKEND)

    def test_small_sigma_and_zero_gate_reject(self):
        u, v, w = angle_frames(np.array([1.5]))
        with self.assertRaises(TransportRejected):
            transport_frames(u, v, w, sigma_min=0.2, gram_atol=TOL.gram_atol, **BACKEND)
        with self.assertRaises(ContractError):
            transport_frames(u, v, w, sigma_min=0, gram_atol=TOL.gram_atol, **BACKEND)

    def test_backend_choice_is_explicit_without_fallback(self):
        s = fixture()
        with self.assertRaises(ContractError):
            weighted_overlap(s.vectors, s.vectors, s.weights, backend="auto")
        with self.assertRaises(ContractError):
            weighted_overlap(s.vectors, s.vectors, s.weights, backend="native")
        with self.assertRaises(ContractError):
            weighted_overlap(s.vectors, s.vectors, s.weights, backend="reference", native_library="unwanted.so")
        with self.assertRaises(TypeError):
            weighted_overlap(s.vectors, s.vectors, s.weights)

    def test_snapshot_identity_and_exact_weights_required(self):
        s = fixture()
        for field, value in (("embedding_id", "different"), ("metric_id", "different"),
                             ("energy_convention_id", "different"), ("hilbert_space_id", "different")):
            other = dataclasses.replace(s, representation=dataclasses.replace(s.representation, **{field:value}))
            with self.assertRaisesRegex(ContractError, "representation"):
                parallel_transport(s, other, TargetSpec.large_R_rank5(), TOL, sigma_min=0.2, **BACKEND)
        weights = s.weights.copy()
        weights[0] = np.nextafter(weights[0], np.inf)
        with self.assertRaisesRegex(ContractError, "metric-weight equality"):
            parallel_transport(s, dataclasses.replace(s, weights=weights), TargetSpec.large_R_rank5(), TOL, sigma_min=0.2, **BACKEND)

    def test_output_frame_labels_and_rotated_energy_model(self):
        s = fixture()
        v = s.vectors.copy()
        rotation = unitary(3, 60)
        v[:, 1:4] = v[:, 1:4]@rotation
        current = dataclasses.replace(s, coordinate=3.0, vectors=v)
        r = parallel_transport(s, current, TargetSpec.large_R_rank5(), TOL, sigma_min=0.2, **BACKEND)
        self.assertFalse(r.aligned_columns_are_individual_eigenstates)
        self.assertFalse(r.actual_operator_projection_supplied)
        self.assertFalse(r.actual_ritz_residual_certified)
        self.assertIn("nominal", r.reduced_operator_semantics)
        self.assertEqual(r.source_state_ids, tuple(s.states[i].state_id for i in s.selected_indices))
        q = r.transport.right_rotation
        np.testing.assert_allclose(r.transformed_ritz_operator, q.conj().T@np.diag(r.source_energies)@q, atol=2e-14, rtol=0)
        np.testing.assert_allclose(np.linalg.eigvalsh(r.transformed_ritz_operator), np.sort(r.source_energies), atol=2e-14, rtol=0)
        self.assertGreater(abs(r.transformed_ritz_operator[0, 1]), 1e-4)

    def test_supplied_projected_form_transforms_with_gram_whitening(self):
        s = fixture()
        v = s.vectors.copy()
        v[:, 1] *= 1+1e-12
        selected = v[:, s.selected_indices]
        ambient_h = np.diag([x.energy for x in s.states]).astype(np.complex128)
        raw_h = selected.conj().T @ (s.weights[:, None] * (ambient_h@selected))
        current = dataclasses.replace(s, vectors=v, selected_projected_operator=raw_h)
        r = parallel_transport(s, current, TargetSpec.large_R_rank5(), TOL, sigma_min=0.2, **BACKEND)
        a = r.transport.aligned_frame
        expected = a.conj().T@(s.weights[:, None]*(ambient_h@a))
        self.assertTrue(r.actual_operator_projection_supplied)
        self.assertIn("supplied_projected", r.reduced_operator_semantics)
        np.testing.assert_allclose(r.transformed_ritz_operator, expected, atol=2e-14, rtol=0)

    def test_nonhermitian_supplied_projected_form_rejected(self):
        s = fixture()
        h = np.eye(5, dtype=np.complex128)
        h[0, 1] = 1j
        with self.assertRaisesRegex(ContractError, "Hermitian"):
            validate_snapshot(dataclasses.replace(s, selected_projected_operator=h), TargetSpec.large_R_rank5(), TOL, **BACKEND)


if __name__ == "__main__":
    unittest.main(verbosity=2)
