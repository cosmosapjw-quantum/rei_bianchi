"""Subspace Rayleigh-Ritz witness diagnostics for a Hermitian pencil (R,O).

Research-only linear algebra on stored matrices. No HH native integral,
propagator, benchmark, source repair, or production admission.
"""
from __future__ import annotations
import hashlib
import math
from pathlib import Path
import numpy as np
from scipy.linalg import eigh

HERMITICITY_RTOL = 2e-12


def _matrix(x, name, *, square=False, hermitian=False):
    a = np.array(x, dtype=np.complex128, copy=True)
    if a.ndim != 2 or not a.size or not np.isfinite(a).all():
        raise ValueError(f"{name} must be a finite nonempty matrix")
    if square and a.shape[0] != a.shape[1]:
        raise ValueError(f"{name} must be square")
    if hermitian:
        if a.shape[0] != a.shape[1]:
            raise ValueError(f"{name} must be square Hermitian")
        gap = float(np.linalg.norm(a - a.conj().T, 2))
        scale = max(1.0, float(np.linalg.norm(a, 2)))
        if gap > HERMITICITY_RTOL * scale:
            raise ValueError(f"{name} Hermiticity prerequisite failed")
    return a


def _o_norm(x, o, *, allow_zero=False):
    v = np.vdot(x, o @ x)
    if abs(v.imag) > 1e-10 * max(1.0, abs(v.real)) or v.real < 0 or (v.real == 0 and not allow_zero):
        raise ValueError("invalid O norm")
    return math.sqrt(max(0.0, float(v.real)))


def analyze_pencil(overlap, residual, frame):
    """Analyze full and compressed pencils and construct lifted witnesses.

    For full-column-rank Q, the reduced quotient is exactly the ambient
    quotient restricted to range(Q). Therefore nonzero reduced Ritz values
    are ambient witnesses. This routine also computes the full stored-matrix
    spectrum as an optional *pointwise linear-algebra diagnostic*.
    """
    o = _matrix(overlap, "O", square=True, hermitian=True)
    r = _matrix(residual, "R", square=True, hermitian=True)
    if r.shape != o.shape:
        raise ValueError("R shape mismatch")
    q = _matrix(frame, "Q")
    if q.shape[0] != o.shape[0] or q.shape[1] > q.shape[0]:
        raise ValueError("Q shape mismatch")
    if np.linalg.matrix_rank(q) != q.shape[1]:
        raise ValueError("Q must have full column rank")
    if float(np.linalg.eigvalsh(o).min()) <= 0:
        raise ValueError("O must be positive definite")
    oq = q.conj().T @ o @ q
    rq = q.conj().T @ r @ q
    if float(np.linalg.eigvalsh(oq).min()) <= 0:
        raise ValueError("compressed O must be positive definite")

    full_vals, full_vecs = eigh(r, o)
    red_vals, red_vecs = eigh(rq, oq)
    n, k = len(full_vals), len(red_vals)
    interlace_slack = []
    for i, theta in enumerate(red_vals):
        lo = float(full_vals[i])
        hi = float(full_vals[i + n - k])
        interlace_slack.append({"i": i, "lower_slack": float(theta - lo),
                                "upper_slack": float(hi - theta)})
    tol = 5e-12 * max(1.0, float(np.max(np.abs(full_vals))))
    interlacing_pass = all(x["lower_slack"] >= -tol and x["upper_slack"] >= -tol
                           for x in interlace_slack)

    def witness(which):
        idx = 0 if which == "negative" else -1
        y = red_vecs[:, idx]
        x = q @ y
        x = x / _o_norm(x, o)
        denom = np.vdot(x, o @ x)
        rho = np.vdot(x, r @ x) / denom
        eigres = r @ x - rho * (o @ x)
        scale = np.linalg.norm(r, 2) * np.linalg.norm(x) + abs(rho) * np.linalg.norm(o, 2) * np.linalg.norm(x)
        raw = np.ascontiguousarray(x.astype(np.complex128)).tobytes()
        return {
            "which": which,
            "reduced_ritz_value": float(red_vals[idx]),
            "ambient_rayleigh_real": float(rho.real),
            "ambient_rayleigh_imag": float(rho.imag),
            "ambient_O_norm": float(np.vdot(x, o @ x).real),
            "ambient_eigen_residual": float(np.linalg.norm(eigres)),
            "ambient_relative_eigen_residual": float(np.linalg.norm(eigres) / scale) if scale else 0.0,
            "ambient_vector_sha256_complex128": hashlib.sha256(raw).hexdigest(),
            "vector_real": x.real.tolist(),
            "vector_imag": x.imag.tolist(),
        }

    witnesses = {name: witness(name) for name in ("negative", "positive")}
    eta_full = float(np.max(np.abs(full_vals)))
    eta_red = float(np.max(np.abs(red_vals)))

    proj = q @ np.linalg.solve(oq, q.conj().T @ o)
    projection_residuals = {}
    for name, idx in (("negative", 0), ("positive", -1)):
        xf = full_vecs[:, idx]
        projection_residuals[name] = _o_norm(xf - proj @ xf, o, allow_zero=True)

    sfull = np.linalg.svd(r, compute_uv=False)
    sred = np.linalg.svd(rq, compute_uv=False)
    rank_tol_full = max(r.shape) * np.finfo(float).eps * max(1.0, float(sfull[0])) * 100
    rank_tol_red = max(rq.shape) * np.finfo(float).eps * max(1.0, float(sred[0])) * 100
    full_rank = int(np.count_nonzero(sfull > rank_tol_full))
    red_rank = int(np.count_nonzero(sred > rank_tol_red))

    return {
        "schema": "WU088_R31X_SUBSPACE_WITNESS_V1",
        "dimension_full": n,
        "dimension_reduced": k,
        "rank_Q": int(np.linalg.matrix_rank(q)),
        "lambda_full_min": float(full_vals[0]),
        "lambda_full_max": float(full_vals[-1]),
        "lambda_reduced_min": float(red_vals[0]),
        "lambda_reduced_max": float(red_vals[-1]),
        "eta_full_point": eta_full,
        "eta_reduced_point": eta_red,
        "eta_reduced_le_eta_full": bool(eta_red <= eta_full + tol),
        "eta_gap_full_minus_reduced": eta_full - eta_red,
        "interlacing_pass": interlacing_pass,
        "interlacing_slack": interlace_slack,
        "full_generalized_eigenvalues": [float(x) for x in full_vals],
        "reduced_generalized_eigenvalues": [float(x) for x in red_vals],
        "full_nonzero_generalized_eigenvalues_tol1e-12": [float(x) for x in full_vals if abs(x) > 1e-12],
        "reduced_nonzero_generalized_eigenvalues_tol1e-12": [float(x) for x in red_vals if abs(x) > 1e-12],
        "approx_rank_R": full_rank,
        "approx_rank_R_reduced": red_rank,
        "extremal_full_eigenvector_O_projection_residual": projection_residuals,
        "witnesses": witnesses,
        "minimum_whitened_connection_correction_full_point": eta_full / 2,
        "minimum_whitened_connection_correction_lower_bound_from_reduced": eta_red / 2,
        "certified_interval_arithmetic": False,
        "scope": "STORED_POINT_BINARY64_GENERALIZED_HERMITIAN_LINEAR_ALGEBRA",
        "claim_ceiling": [
            "pointwise represented-matrix incompatibility only",
            "reduced FAIL lifts to ambient FAIL; reduced PASS does not lift",
            "no full-cell or trajectory bound",
            "no physical transition-error bound",
            "minimum correction is distance to metric compatibility, not an approved physical repair",
        ],
    }
