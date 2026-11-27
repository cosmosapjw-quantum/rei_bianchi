"""Bounded A1b algebra for one normalized target and five projectile orbitals.

X = [u, V], V.conj().T @ V = I, s = V.conj().T @ u.  These helpers
accept s as input; they do not calculate orbitals, ETFs, collision amplitudes,
or cross sections.  Finite-R physical target/projectile projectors overlap.
The orthogonal complement to Ran(V) is a partition component, not the raw
physical target projector.  Delta <= 1e-12 is rejected without regularization.
"""

from __future__ import annotations

import numpy as np

PROJECTILE_DIMENSION = 5
DELTA_REJECTION_TOLERANCE = 1.0e-12


def _vector(value: object, size: int, name: str) -> np.ndarray:
    try:
        vector = np.asarray(value, dtype=np.complex128)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a numeric vector") from exc
    if vector.shape != (size,):
        raise ValueError(f"{name} must have shape ({size},)")
    if not np.isfinite(vector).all():
        raise ValueError(f"{name} must contain only finite entries")
    return vector


def _overlap(value: object) -> tuple[np.ndarray, float]:
    s = _vector(value, PROJECTILE_DIMENSION, "s")
    with np.errstate(over="ignore", invalid="ignore"):
        squared_norm = float(np.vdot(s, s).real)
    delta = 1.0 - squared_norm
    if not np.isfinite(delta) or delta <= DELTA_REJECTION_TOLERANCE:
        raise ValueError("Gram Schur complement delta must exceed 1e-12; no regularization")
    return s, delta


def gram_from_overlap(s: object) -> np.ndarray:
    """Return [[1, s†], [s, I5]] after the fixed Schur-complement check."""
    overlap, _ = _overlap(s)
    gram = np.eye(PROJECTILE_DIMENSION + 1, dtype=np.complex128)
    gram[0, 1:] = overlap.conj()
    gram[1:, 0] = overlap
    return gram


def orthonormalizer(s: object) -> np.ndarray:
    """Return W with XW = [(u - Vs)/sqrt(delta), V]; W†SW = I6."""
    overlap, delta = _overlap(s)
    transform = np.eye(PROJECTILE_DIMENSION + 1, dtype=np.complex128)
    transform[0, 0] = 1.0 / np.sqrt(delta)
    transform[1:, 0] = -overlap / np.sqrt(delta)
    return transform


def channel_probabilities(c: object, s: object) -> dict[str, float]:
    """Return projector quadratic forms, with no implicit state normalization.

    If c†Sc=1 these are probabilities.  At finite overlap, p_A_raw + p_B
    is not a probability partition.  p_B + p_A_orthogonal = c†Sc is the
    orthogonal partition of this six-dimensional trial subspace.
    """
    overlap, delta = _overlap(s)
    coefficients = _vector(c, PROJECTILE_DIMENSION + 1, "c")
    a, b = coefficients[0], coefficients[1:]
    try:
        with np.errstate(over="raise", invalid="raise"):
            projectile = b + overlap * a
            raw_target = a + np.vdot(overlap, b)
            p_b = float(np.vdot(projectile, projectile).real)
            p_a_raw = float(np.abs(raw_target) ** 2)
            p_a_orthogonal = float(delta * np.abs(a) ** 2)
            metric_norm = float(np.vdot(coefficients, gram_from_overlap(overlap) @ coefficients).real)
            partition = p_b + p_a_orthogonal
            raw_sum = p_a_raw + p_b
    except FloatingPointError as exc:
        raise ValueError("Nonfinite arithmetic in projector evaluation") from exc
    result = {
        "delta": delta,
        "p_B": p_b,
        "p_A_raw": p_a_raw,
        "p_A_orthogonal": p_a_orthogonal,
        "metric_norm": metric_norm,
        "orthogonal_partition": partition,
        "raw_projector_sum": raw_sum,
    }
    if not all(np.isfinite(value) for value in result.values()):
        raise ValueError("Nonfinite arithmetic in projector evaluation")
    return result
