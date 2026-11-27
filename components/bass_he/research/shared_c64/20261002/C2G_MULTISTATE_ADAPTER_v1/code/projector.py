"""C2f finite-frame contracts and weighted polar transport (no physical solver).

All tolerances, source/representation identities and backend choices are explicit.
Energies/residuals are caller-declared finite data, never continuum enclosures.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import math
import numpy as np


class ContractError(ValueError):
    """Malformed or semantically incompatible finite-frame input."""


class TransportRejected(ContractError):
    """Registered principal-overlap gate did not pass."""


class Role(str, Enum):
    SELECTED = "selected"
    GUARD = "guard"


class TargetKind(str, Enum):
    FULL_ENERGY = "full_energy"
    SYMMETRY_BLOCKS = "symmetry_blocks"


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} must be a nonempty string")


def _finite(value, field, lower=None, upper=None):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, float, np.integer, np.floating)):
        raise ContractError(f"{field} must be a finite real scalar")
    if not math.isfinite(float(value)) or (lower is not None and value < lower) or (upper is not None and value > upper):
        raise ContractError(f"{field} is outside its finite range")


def _int(value, field):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise ContractError(f"{field} must be an integer")


def _array(value, dtype, ndim, field):
    if not isinstance(value, np.ndarray) or value.dtype != np.dtype(dtype) or value.ndim != ndim:
        raise ContractError(f"{field} must be a {ndim}D {np.dtype(dtype)} ndarray")
    if not all(value.shape) or not np.isfinite(value).all():
        raise ContractError(f"{field} must be nonempty and finite")
    return value


def _readonly(value):
    result = np.array(value, copy=True)
    result.setflags(write=False)
    return result


@dataclass(frozen=True, order=True)
class StateID:
    value: str

    def __post_init__(self):
        _text(self.value, "state ID")


@dataclass(frozen=True)
class StateRecord:
    state_id: StateID
    m: int
    energy: float
    residual_norm: float
    role: Role
    is_ground: bool = False
    known_degenerate_partners: tuple[StateID, ...] = ()

    def __post_init__(self):
        if not isinstance(self.state_id, StateID) or not isinstance(self.role, Role):
            raise ContractError("typed StateID and Role are required")
        _int(self.m, "m")
        _finite(self.energy, "energy")
        _finite(self.residual_norm, "residual_norm", 0)
        if not isinstance(self.is_ground, bool):
            raise ContractError("is_ground must be bool")
        if not isinstance(self.known_degenerate_partners, tuple) or any(not isinstance(x, StateID) for x in self.known_degenerate_partners):
            raise ContractError("known_degenerate_partners must be a tuple of StateID")
        if self.state_id in self.known_degenerate_partners or len(set(self.known_degenerate_partners)) != len(self.known_degenerate_partners):
            raise ContractError("invalid or duplicate partner ID")


@dataclass(frozen=True)
class Representation:
    embedding_id: str
    metric_id: str
    hilbert_space_id: str
    energy_convention_id: str
    energy_unit: str
    coordinate_unit: str
    source_id: str
    source_sha256: str
    spectrum_coverage: str  # finite_full_ambient or finite_sector_subset
    sectors_present: tuple[int, ...]
    axial_real_spinless: bool
    continuum_threshold: float

    def __post_init__(self):
        for name in ("embedding_id", "metric_id", "hilbert_space_id", "energy_convention_id", "energy_unit", "coordinate_unit", "source_id"):
            _text(getattr(self, name), name)
        if not isinstance(self.source_sha256, str) or len(self.source_sha256) != 64 or any(c not in "0123456789abcdef" for c in self.source_sha256):
            raise ContractError("source_sha256 must be a lowercase SHA-256 hex digest")
        if self.spectrum_coverage not in ("finite_full_ambient", "finite_sector_subset"):
            raise ContractError("unsupported spectrum_coverage")
        if not isinstance(self.sectors_present, tuple) or not self.sectors_present:
            raise ContractError("sectors_present must be a nonempty tuple")
        for m in self.sectors_present:
            _int(m, "sectors_present member")
        if len(set(self.sectors_present)) != len(self.sectors_present):
            raise ContractError("duplicate sector declaration")
        if not isinstance(self.axial_real_spinless, bool):
            raise ContractError("axial_real_spinless must be bool")
        _finite(self.continuum_threshold, "continuum_threshold")


@dataclass(frozen=True)
class Snapshot:
    coordinate: float
    vectors: np.ndarray  # N x n, columns correspond exactly to states
    weights: np.ndarray  # N, positive diagonal W
    states: tuple[StateRecord, ...]
    representation: Representation
    selected_projected_operator: np.ndarray | None = None

    def __post_init__(self):
        _finite(self.coordinate, "coordinate")
        _array(self.vectors, np.complex128, 2, "vectors")
        _array(self.weights, np.float64, 1, "weights")
        if self.weights.shape != (self.vectors.shape[0],) or np.any(self.weights <= 0):
            raise ContractError("weights must be positive and match the common embedding")
        if not isinstance(self.states, tuple) or any(not isinstance(x, StateRecord) for x in self.states):
            raise ContractError("states must be a tuple of StateRecord")
        if len(self.states) != self.vectors.shape[1] or self.vectors.shape[1] > self.vectors.shape[0]:
            raise ContractError("state/frame shape mismatch or more vectors than ambient dimensions")
        if len({s.state_id for s in self.states}) != len(self.states):
            raise ContractError("state IDs must be unique within a snapshot")
        if not isinstance(self.representation, Representation):
            raise ContractError("typed Representation required")
        if set(s.m for s in self.states) != set(self.representation.sectors_present):
            raise ContractError("actual and declared sectors_present differ")
        if not any(s.role is Role.SELECTED for s in self.states):
            raise ContractError("at least one selected state is required")
        if self.selected_projected_operator is not None:
            _array(self.selected_projected_operator, np.complex128, 2, "selected_projected_operator")
            k = len(self.selected_indices)
            if self.selected_projected_operator.shape != (k, k):
                raise ContractError("selected projected operator shape differs from selected rank")
            object.__setattr__(self, "selected_projected_operator", _readonly(self.selected_projected_operator))
        object.__setattr__(self, "vectors", _readonly(self.vectors))
        object.__setattr__(self, "weights", _readonly(self.weights))

    @property
    def selected_indices(self):
        return tuple(i for i, s in enumerate(self.states) if s.role is Role.SELECTED)

    @property
    def guard_indices(self):
        return tuple(i for i, s in enumerate(self.states) if s.role is Role.GUARD)

    @property
    def selected_frame(self):
        return self.vectors[:, self.selected_indices]


@dataclass(frozen=True)
class TargetSpec:
    name: str
    kind: TargetKind
    sector_ranks: tuple[tuple[int, int], ...]
    excludes_ground: bool
    selection_basis: str

    def __post_init__(self):
        _text(self.name, "target name")
        _text(self.selection_basis, "selection_basis")
        if not isinstance(self.kind, TargetKind) or not isinstance(self.excludes_ground, bool):
            raise ContractError("typed target kind and bool ground policy required")
        if not isinstance(self.sector_ranks, tuple) or not self.sector_ranks:
            raise ContractError("sector_ranks must be a nonempty tuple")
        for item in self.sector_ranks:
            if not isinstance(item, tuple) or len(item) != 2:
                raise ContractError("each sector rank is an (m, count) tuple")
            _int(item[0], "target m")
            _int(item[1], "target count")
            if item[1] <= 0:
                raise ContractError("target count must be positive")
        if len({m for m, _ in self.sector_ranks}) != len(self.sector_ranks):
            raise ContractError("duplicate target sector")

    @classmethod
    def large_R_rank5(cls):
        return cls("large_R_rank5_candidate", TargetKind.FULL_ENERGY,
                   ((0, 3), (1, 1), (-1, 1)), True,
                   "explicit candidate ranks only; atomic correlation and continuation unresolved")


@dataclass(frozen=True)
class ValidationTolerances:
    gram_atol: float
    degeneracy_atol: float
    residual_max: float
    external_gap_min: float
    # Inputs are declared in the representation energy unit, not inferred from old C2 gates.

    def __post_init__(self):
        _finite(self.gram_atol, "gram_atol", 0, 0.1)
        _finite(self.degeneracy_atol, "degeneracy_atol", 0)
        _finite(self.residual_max, "residual_max", 0)
        _finite(self.external_gap_min, "external_gap_min", 0)


@dataclass(frozen=True)
class SnapshotDiagnostics:
    target_name: str
    selected_rank: int
    guard_count: int
    gram_max_error: float
    selected_guard_max_overlap: float
    internal_min_splitting: float | None
    observed_guard_gap: float | None
    guard_gap_scope: str
    guards_by_sector: tuple[tuple[int, int], ...]
    max_declared_residual_norm: float
    supplied_frame_spans_finite_ambient: bool
    every_selected_sector_has_guard: bool
    observed_guard_gap_exceeds_floor: bool | None
    continuum_certificate: bool = False
    full_H_certificate: bool = False
    atomic_correlation_established: bool = False
    collision_domain_covered: bool = False


def weighted_overlap(u, v, weights, *, backend, native_library=None):
    """Compute u^dagger W v; explicit reference/native choice, no fallback."""
    _array(u, np.complex128, 2, "u")
    _array(v, np.complex128, 2, "v")
    _array(weights, np.float64, 1, "weights")
    if u.shape[0] != v.shape[0] or weights.shape != (u.shape[0],) or np.any(weights <= 0):
        raise ContractError("incompatible positive diagonal metric")
    if backend == "reference":
        if native_library is not None:
            raise ContractError("native_library is incompatible with reference backend")
        answer = u.conj().T @ (weights[:, None] * v)
    elif backend == "native":
        if not isinstance(native_library, (str, Path)) or not str(native_library):
            raise ContractError("native backend requires an explicit library path")
        from native_overlap import overlap
        answer = overlap(u, v, weights, library=native_library)
    else:
        raise ContractError("backend must be explicitly reference or native")
    _array(answer, np.complex128, 2, "overlap output")
    if answer.shape != (u.shape[1], v.shape[1]):
        raise ContractError("backend returned a wrong overlap shape")
    return answer


def validate_snapshot(snapshot, target, tolerances, *, backend, native_library=None):
    """Validate all supplied columns; observed Ritz spacings remain diagnostics."""
    if not isinstance(snapshot, Snapshot) or not isinstance(target, TargetSpec) or not isinstance(tolerances, ValidationTolerances):
        raise ContractError("typed snapshot, target and tolerances are required")
    selected = [snapshot.states[i] for i in snapshot.selected_indices]
    guards = [snapshot.states[i] for i in snapshot.guard_indices]
    ranks = {m: sum(s.m == m for s in selected) for m in {s.m for s in selected}}
    if ranks != dict(target.sector_ranks):
        raise ContractError("selected sector ranks disagree with target")
    if target.excludes_ground and any(s.is_ground for s in selected):
        raise ContractError("target excludes a declared selected ground state")
    gram = weighted_overlap(snapshot.vectors, snapshot.vectors, snapshot.weights,
                            backend=backend, native_library=native_library)
    gram_error = float(np.max(np.abs(gram - np.eye(len(snapshot.states)))))
    if np.linalg.norm(gram - np.eye(len(snapshot.states)), ord=2) > tolerances.gram_atol:
        raise ContractError("supplied selected/guard frame is not W-orthonormal; no repair performed")
    if max(s.residual_norm for s in snapshot.states) > tolerances.residual_max:
        raise ContractError("declared selected/guard residual exceeds registered maximum")
    if snapshot.selected_projected_operator is not None:
        h = snapshot.selected_projected_operator
        if np.linalg.norm(h - h.conj().T, ord=2) > tolerances.degeneracy_atol:
            raise ContractError("selected projected operator is not Hermitian within registered energy tolerance")
    overlaps = gram[np.ix_(snapshot.selected_indices, snapshot.guard_indices)]
    overlap_error = float(np.max(np.abs(overlaps))) if overlaps.size else 0.0
    by_id = {s.state_id: s for s in snapshot.states}
    selected_ids = {s.state_id for s in selected}
    if target.kind is TargetKind.FULL_ENERGY:
        # Explicit partner metadata is stronger than accidental finite rounding differences.
        for s in selected:
            if any(partner not in selected_ids for partner in s.known_degenerate_partners):
                raise ContractError("known degenerate partner is omitted from full-energy target")
        for s in guards:
            if any(partner in selected_ids for partner in s.known_degenerate_partners):
                raise ContractError("guard is a known omitted degenerate partner")
        if snapshot.representation.axial_real_spinless:
            # This physical symmetry is supplied explicitly, never inferred from a numeric gap.
            for m in {abs(s.m) for s in selected if s.m != 0}:
                plus = sorted(s.energy for s in selected if s.m == m)
                minus = sorted(s.energy for s in selected if s.m == -m)
                if len(plus) != len(minus) or any(abs(a-b) > tolerances.degeneracy_atol for a, b in zip(plus, minus)):
                    raise ContractError("full-energy target omits or mismatches an axial +/-m partner")
    # Metadata may point outside the supplied set; that remains an explicit missing partner.
    for s in snapshot.states:
        for partner in s.known_degenerate_partners:
            if partner in by_id and abs(s.energy - by_id[partner].energy) > tolerances.degeneracy_atol:
                raise ContractError("declared degenerate partners have inconsistent energies")
    relevant = [abs(s.energy - g.energy) for s in selected for g in guards
                if target.kind is TargetKind.FULL_ENERGY or s.m == g.m]
    observed_gap = min(relevant) if relevant else None
    if observed_gap is not None and observed_gap <= max(tolerances.degeneracy_atol, tolerances.external_gap_min):
        raise ContractError("known selected/guard gap fails the registered energy-boundary floor")
    internal = [abs(a.energy-b.energy) for i, a in enumerate(selected) for b in selected[i+1:]]
    return SnapshotDiagnostics(
        target.name, len(selected), len(guards), gram_error, overlap_error,
        min(internal) if internal else None, observed_gap,
        "all supplied sectors" if target.kind is TargetKind.FULL_ENERGY else "same-m supplied guards only",
        tuple(sorted((m, sum(g.m == m for g in guards)) for m in snapshot.representation.sectors_present)),
        max(s.residual_norm for s in snapshot.states),
        snapshot.representation.spectrum_coverage == "finite_full_ambient" and snapshot.vectors.shape[0] == len(snapshot.states),
        all(any(g.m == m for g in guards) for m in ranks),
        observed_gap > tolerances.external_gap_min if observed_gap is not None else None)


@dataclass(frozen=True)
class FrameTransport:
    aligned_frame: np.ndarray
    right_rotation: np.ndarray
    singular_values: np.ndarray
    principal_angles: np.ndarray
    projector_operator_distance: float
    projector_frobenius_distance: float
    registered_sigma_min: float
    previous_gram: np.ndarray
    current_gram: np.ndarray
    previous_inverse_sqrt_gram: np.ndarray
    current_inverse_sqrt_gram: np.ndarray
    source_basis_transform: np.ndarray
    previous_normalization_correction_norm: float
    current_normalization_correction_norm: float
    normalization_policy: str = "explicit_symmetric_gram_whitening_within_registered_tolerance"


def transport_frames(u, v, weights, *, sigma_min, gram_atol, backend, native_library=None):
    """Weighted U(k)-covariant polar transport of equal-rank orthonormal frames.

    Caller must separately establish common physical embedding. This algebraic
    primitive accepts frame vectors, not eigenstate labels or certified projectors.
    """
    _finite(sigma_min, "sigma_min", 0, 1)
    _finite(gram_atol, "gram_atol", 0, 0.1)
    if sigma_min <= 0:
        raise ContractError("sigma_min must be strictly positive to avoid nonunique polar transport")
    _array(u, np.complex128, 2, "u")
    _array(v, np.complex128, 2, "v")
    if u.shape != v.shape:
        raise ContractError("transport requires equal ambient dimension and rank")
    if u.shape[1] > u.shape[0]:
        raise ContractError("transport rank exceeds embedding dimension")
    grams, whiteners, frames = [], [], []
    for frame in (u, v):
        gram = weighted_overlap(frame, frame, weights, backend=backend, native_library=native_library)
        identity = np.eye(frame.shape[1])
        if np.linalg.norm(gram - identity, ord=2) > gram_atol:
            raise ContractError("transport Gram defect exceeds tolerance; no repair performed")
        hermitian_gram = (gram + gram.conj().T) * 0.5
        values, basis = np.linalg.eigh(hermitian_gram)
        if values[0] <= np.finfo(np.float64).eps * frame.shape[1] * values[-1]:
            raise ContractError("Gram matrix is not numerically positive definite")
        inverse_sqrt = (basis * (1 / np.sqrt(values))[None, :]) @ basis.conj().T
        grams.append(gram)
        whiteners.append(inverse_sqrt)
        frames.append(frame @ inverse_sqrt)
    uhat, vhat = frames
    overlap = weighted_overlap(uhat, vhat, weights, backend=backend, native_library=native_library)
    left, singular_values, right_h = np.linalg.svd(overlap, full_matrices=False)
    if singular_values[-1] <= sigma_min:
        raise TransportRejected("smallest principal overlap does not exceed the registered gate")
    if singular_values[0] > 1 + 32 * u.shape[1] * np.finfo(np.float64).eps:
        raise ContractError("normalized principal overlap exceeds numerical unit range")
    rotation = right_h.conj().T @ left.conj().T
    # Work with normalized frames to represent the actual span projectors. The
    # residual form avoids sqrt(1-sigma**2) cancellation near identical spans.
    sqrt_w = np.sqrt(weights)[:, None]
    residual = sqrt_w * (vhat - uhat @ overlap)
    sines = np.linalg.svd(residual, compute_uv=False)
    angles = np.arctan2(np.clip(sines[::-1], 0, 1), np.clip(singular_values, 0, 1))
    op_distance = float(sines[0])
    frob_distance = float(np.sqrt(2.0) * np.linalg.norm(sines))
    return FrameTransport(
        _readonly(vhat @ rotation), _readonly(rotation),
        _readonly(singular_values), _readonly(angles), op_distance, frob_distance, float(sigma_min),
        _readonly(grams[0]), _readonly(grams[1]), _readonly(whiteners[0]), _readonly(whiteners[1]),
        _readonly(whiteners[1] @ rotation),
        float(np.linalg.norm(whiteners[0] - np.eye(u.shape[1]), ord=2)),
        float(np.linalg.norm(whiteners[1] - np.eye(v.shape[1]), ord=2)))


@dataclass(frozen=True)
class SnapshotTransport:
    transport: FrameTransport
    previous_coordinate: float
    current_coordinate: float
    source_state_ids: tuple[StateID, ...]
    source_energies: np.ndarray
    source_residual_norms: np.ndarray
    aligned_column_labels: tuple[str, ...]
    transformed_ritz_operator: np.ndarray
    reduced_operator_semantics: str
    previous_diagnostics: SnapshotDiagnostics
    current_diagnostics: SnapshotDiagnostics
    aligned_columns_are_individual_eigenstates: bool = False
    actual_operator_projection_supplied: bool = False
    actual_ritz_residual_certified: bool = False
    continuum_certificate: bool = False


def parallel_transport(previous, current, target, tolerances, *, sigma_min, backend, native_library=None):
    """Validate snapshots, require identical embedding/metric, then transport frames.

    Explicit IDs describe pre-transport source eigenstates. Mixed output columns
    are frame vectors. With supplied Hsmall=V^dagger W H V, the transported
    form is (C Q)^dagger Hsmall (C Q), C=G_V^-1/2. Without Hsmall,
    diag(E_current) is only a declared model on the normalized source frame.
    """
    if not isinstance(previous, Snapshot) or not isinstance(current, Snapshot):
        raise ContractError("typed snapshots required")
    rp, rc = previous.representation, current.representation
    for field in ("embedding_id", "metric_id", "hilbert_space_id", "energy_convention_id",
                  "energy_unit", "coordinate_unit", "axial_real_spinless"):
        if getattr(rp, field) != getattr(rc, field):
            raise ContractError(f"incompatible cross-coordinate representation: {field}")
    if rp.continuum_threshold != rc.continuum_threshold:
        raise ContractError("continuum energy origins differ")
    if not np.array_equal(previous.weights, current.weights):
        raise ContractError("common embedding ID does not replace exact metric-weight equality")
    dp = validate_snapshot(previous, target, tolerances, backend=backend, native_library=native_library)
    dc = validate_snapshot(current, target, tolerances, backend=backend, native_library=native_library)
    transported = transport_frames(previous.selected_frame, current.selected_frame, current.weights,
                                   sigma_min=sigma_min, gram_atol=tolerances.gram_atol,
                                   backend=backend, native_library=native_library)
    records = [current.states[i] for i in current.selected_indices]
    energy = np.array([s.energy for s in records], dtype=np.float64)
    residual = np.array([s.residual_norm for s in records], dtype=np.float64)
    q = transported.right_rotation
    supplied = current.selected_projected_operator is not None
    if supplied:
        c = transported.source_basis_transform
        h = current.selected_projected_operator
        ritz = c.conj().T @ ((h + h.conj().T) * 0.5) @ c
        semantics = "supplied_projected_H_form_transformed_by_recorded_gram_whitening_and_polar_rotation"
    else:
        ritz = q.conj().T @ (energy[:, None] * q)
        semantics = "nominal_diagonal_energy_model_on_normalized_source_frame_not_computed_H_projection"
    return SnapshotTransport(transported, previous.coordinate, current.coordinate,
                             tuple(s.state_id for s in records), _readonly(energy), _readonly(residual),
                             tuple(f"transported_frame[{i}]" for i in range(len(records))), _readonly(ritz),
                             semantics, dp, dc, actual_operator_projection_supplied=supplied)
