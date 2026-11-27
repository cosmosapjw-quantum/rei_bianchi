"""Seeded finite Hilbert examples with analytic principal angles; no molecular H."""
from __future__ import annotations

import hashlib
import json
import math
import numpy as np
from projector import (StateID, StateRecord, Representation, Snapshot, TargetSpec,
                       TargetKind, Role, ValidationTolerances, parallel_transport)


def _unitary(rng, n):
    q, _ = np.linalg.qr(rng.normal(size=(n, n)) + 1j*rng.normal(size=(n, n)))
    return np.asarray(q, dtype=np.complex128)


def make_case(case):
    """Every energy and coordinate here is synthetic and dimensionless."""
    n, k, theta = case['n_rows'], case['rank'], case['angle']
    if n < 2*k+1:
        raise ValueError('manufactured ambient needs ground + two rank-k spaces')
    rng = np.random.default_rng(case['seed'])
    weights = np.asarray(np.exp(rng.uniform(-1, 1, n)), dtype=np.float64)
    x = rng.normal(size=(n, 2*k+1)) + 1j*rng.normal(size=(n, 2*k+1))
    q, _ = np.linalg.qr(x)
    q = np.asarray(q / np.sqrt(weights)[:, None], dtype=np.complex128)
    a, b = _unitary(rng, k), _unitary(rng, k)
    u, e = q[:, 1:k+1], q[:, k+1:]
    v = u*math.cos(theta) + e*math.sin(theta)
    exterior = -u*math.sin(theta) + e*math.cos(theta)
    vectors = [np.column_stack((q[:, 0], u@a, e)),
               np.column_stack((q[:, 0], v@b, exterior))]
    energy = np.asarray([-2.] + [-.5]*k + [.2]*k, dtype=np.float64)
    snapshots = []
    for index, frame in enumerate(vectors):
        gram = frame.conj().T @ (weights[:, None]*frame)
        # Defines a finite Hermitian operator H=V diag(E) V^dagger W;
        # supplied residuals and reduced forms are computed, not assumed zero.
        h_frame = frame @ (energy[:, None]*gram)
        residuals = np.sqrt(np.sum(weights[:, None]*abs(h_frame-frame*energy)**2, axis=0))
        projected = gram @ (energy[:, None]*gram)
        states = tuple(StateRecord(StateID(f'state_{j:02d}'), 0, float(energy[j]),
                                   float(residuals[j]),
                                   Role.SELECTED if 1 <= j <= k else Role.GUARD,
                                   is_ground=(j == 0)) for j in range(2*k+1))
        digest = hashlib.sha256()
        digest.update(json.dumps(case, sort_keys=True, allow_nan=False).encode())
        for array in (frame, weights, energy):
            digest.update(np.ascontiguousarray(array).tobytes())
        rep = Representation(
            embedding_id=f"synthetic_rows_{n}", metric_id=f"weights_seed_{case['seed']}",
            hilbert_space_id='finite_weighted_complex_sample_space',
            energy_convention_id='synthetic_energy_origin', energy_unit='dimensionless_synthetic',
            coordinate_unit='dimensionless_synthetic', source_id=f"{case['case_id']}_{index}",
            source_sha256=digest.hexdigest(), spectrum_coverage='finite_sector_subset',
            sectors_present=(0,), axial_real_spinless=False, continuum_threshold=1.0)
        snapshots.append(Snapshot(float(index), frame, weights, states, rep,
                                  selected_projected_operator=projected[1:k+1, 1:k+1]))
    target = TargetSpec(f'synthetic_full_energy_rank_{k}', TargetKind.FULL_ENERGY,
                        ((0, k),), True, 'explicit synthetic degenerate eigenspace, no atomic label')
    tolerance = ValidationTolerances(gram_atol=1e-10, degeneracy_atol=1e-12,
                                     residual_max=1e-10, external_gap_min=1e-8)
    return snapshots, target, tolerance, v@a


def run_case(case, *, backend, native_library):
    snapshots, target, tolerances, expected = make_case(case)
    result = parallel_transport(*snapshots, target, tolerances, sigma_min=.2,
                                backend=backend, native_library=native_library)
    transported = result.transport
    theta, k = case['angle'], case['rank']
    errors = {
        'singular_values': float(np.max(abs(transported.singular_values-math.cos(theta)))),
        'operator_distance': abs(transported.projector_operator_distance-math.sin(theta)),
        'frobenius_distance': abs(transported.projector_frobenius_distance-math.sqrt(2*k)*math.sin(theta)),
        'aligned_frame': float(np.linalg.norm(np.sqrt(snapshots[0].weights)[:, None]*(transported.aligned_frame-expected), ord=2)),
        'small_operator': float(np.linalg.norm(result.transformed_ritz_operator+.5*np.eye(k), ord=2)),
    }
    if max(errors.values()) > 2e-11:
        raise AssertionError(f'manufactured analytic parity failure: {errors}')
    if result.continuum_certificate or result.current_diagnostics.full_H_certificate:
        raise AssertionError('finite manufactured fixture promoted to continuum certificate')
    return {'case_id': case['case_id'], 'status': 'PASS_MANUFACTURED_FINITE_HILBERT',
            'backend': backend, 'analytic_theta': theta, 'rank': k, 'n_rows': case['n_rows'],
            'errors': errors, 'max_error': max(errors.values()),
            'source_sha256': [s.representation.source_sha256 for s in snapshots],
            'observed_guard_gap': result.current_diagnostics.observed_guard_gap,
            'missing_zero_energy_complement_dimension': case['n_rows']-2*k-1,
            'ideal_orthonormal_model_full_finite_gap': .5 if case['n_rows'] > 2*k+1 else .7,
            'gap_note': 'observed guards .7 do not enclose omitted zero-energy complement (.5 from target)',
            'continuum_certificate': False, 'physical_evaluations': 0}
