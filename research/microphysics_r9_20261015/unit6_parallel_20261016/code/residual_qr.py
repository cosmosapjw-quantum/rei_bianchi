"""Standalone cached residual diagnostic; no Hamiltonian actions or runner imports.

The returned floating-point bound is conditional, not an interval certificate.
See spec/RESIDUAL_CONTRACT.json for the frozen scientific interpretation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

import numpy as np


def _positive_int(value, name):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return int(value)


def _floating(value, name):
    array = np.asanyarray(value)
    if array.dtype.kind not in "fc":
        raise ValueError(f"{name} must have a floating real or complex dtype")
    dtype = np.complex128 if array.dtype.kind == "c" else np.float64
    return np.asarray(array, dtype=dtype)


def _finite_real_vector(value, name, positive=False):
    array = np.asarray(value)
    if array.ndim != 1 or array.size == 0 or array.dtype.kind not in "fiu":
        raise ValueError(f"{name} must be a nonempty real one-dimensional array")
    array = np.asarray(array, dtype=np.float64)
    if not np.isfinite(array).all() or (positive and not (array > 0).all()):
        raise ValueError(f"{name} must be finite" + (" and positive" if positive else ""))
    return array


def streamed_qr(row_blocks):
    """Return reduced R for finite double real/complex row blocks.

    Short and rank-deficient blocks are valid. No diagonal division, column
    truncation, Gram construction, or global Q is used.
    """
    R = None
    columns = None
    for raw in row_blocks:
        block = _floating(raw, "row block")
        if block.ndim != 2 or not np.isfinite(block).all():
            raise ValueError("row blocks must be finite two-dimensional arrays")
        if columns is None:
            columns = block.shape[1]
            if columns < 1:
                raise ValueError("row blocks must have at least one column")
        if block.shape[1] != columns:
            raise ValueError("row blocks must have the same column count")
        if block.shape[0] == 0:
            continue
        stacked = block if R is None else np.concatenate((R, block), axis=0)
        R = np.linalg.qr(stacked, mode="r")
    if R is None:
        raise ValueError("at least one nonempty row block is required")
    return R


def streamed_residual_factor(V, KV, u, block_rows=64):
    """Return (J, R, delta_row, norm_u, scale_diagnostics).

    Two row passes over V/KV/u form the projected matrix and reduce [d,E].
    Input float64/complex128 arrays (including memmaps) are used without a
    global copy. Other floating precision is promoted and its storage is
    included in cache_storage_bytes. A full E or A is never allocated here.
    """
    start = time.perf_counter()
    block_rows = _positive_int(block_rows, "block_rows")
    V, KV, u = _floating(V, "V"), _floating(KV, "KV"), _floating(u, "u")
    if V.ndim != 2 or KV.shape != V.shape or u.ndim != 1 or u.shape[0] != V.shape[0]:
        raise ValueError("require V/KV shape (N,m) and u shape (N,)")
    N, m = V.shape
    if not N >= m >= 1:
        raise ValueError("require N >= m >= 1")
    dtype = np.result_type(V.dtype, KV.dtype, u.dtype)
    C = np.zeros((m, m), dtype=dtype)
    delta_row = np.zeros(m, dtype=dtype)
    norm_u = norm_V = norm_KV = norm_v0 = 0.0
    # Pass 1 also validates finiteness, avoiding a separate full cache pass.
    for left in range(0, N, block_rows):
        vb, kb, ub = V[left:left+block_rows], KV[left:left+block_rows], u[left:left+block_rows]
        if not all(np.isfinite(a).all() for a in (vb, kb, ub)):
            raise ValueError("V, KV and u must be finite")
        C += vb.conj().T @ kb
        delta_row += ub.conj() @ vb
        norm_u = float(np.hypot(norm_u, np.linalg.norm(ub)))
        norm_V = float(np.hypot(norm_V, np.linalg.norm(vb)))
        norm_KV = float(np.hypot(norm_KV, np.linalg.norm(kb)))
        norm_v0 = float(np.hypot(norm_v0, np.linalg.norm(vb[:, 0])))
    J = (C + C.conj().T) / 2
    delta_row[0] -= 1
    norm_d = norm_E = 0.0

    def blocks():
        nonlocal norm_d, norm_E
        # Pass 2: only a row block of d/E exists at once.
        for left in range(0, N, block_rows):
            vb, kb, ub = V[left:left+block_rows], KV[left:left+block_rows], u[left:left+block_rows]
            d = ub - vb[:, 0]
            E = kb - vb @ J
            norm_d = float(np.hypot(norm_d, np.linalg.norm(d)))
            norm_E = float(np.hypot(norm_E, np.linalg.norm(E)))
            yield np.column_stack((d, E))

    R = streamed_qr(blocks())
    p, b, item = m + 1, min(block_rows, N), np.dtype(dtype).itemsize
    scales = {
        "N": N, "m": m, "block_rows": block_rows, "dtype": str(np.dtype(dtype)),
        "norm_d": norm_d, "norm_E_fro": norm_E, "norm_V_fro": norm_V,
        "norm_KV_fro": norm_KV, "norm_v0": norm_v0,
        "norm_J_2": float(np.linalg.norm(J, 2)),
        "norm_C_minus_J_fro": float(np.linalg.norm(C-J)),
        "cache_storage_bytes": int(V.nbytes+KV.nbytes+u.nbytes),
        # Conservative live array estimate, excluding LAPACK/BLAS internals.
        "factor_workspace_estimate_bytes": int(item*(4*m*m+4*(b+p)*p+4*m)),
        "workspace_estimate_excludes": "BLAS/LAPACK internal workspace and Python allocator overhead",
        "setup_s": time.perf_counter()-start,
    }
    return J, R, delta_row, norm_u, scales


def residual_diagnostic_qr(V, KV, u, W, grid, etas, block_rows=64, batch_points=256):
    """Return Unit5-compatible eta-major arrays plus a factual summary."""
    batch_points = min(_positive_int(batch_points, "batch_points"), 256)
    weight = np.asarray(W)
    if weight.ndim != 0 or weight.dtype.kind not in "fiu" or not np.isfinite(weight) or weight < 0:
        raise ValueError("W must be a finite real nonnegative scalar")
    W = float(weight)
    grid = _finite_real_vector(grid, "grid")
    etas = _finite_real_vector(etas, "etas", positive=True)
    setup_start = time.perf_counter()
    J, R, delta_row, norm_u, scales = streamed_residual_factor(V, KV, u, block_rows)
    nodes, Y = np.linalg.eigh(J)
    m = J.shape[0]
    e1 = np.zeros(m, dtype=J.dtype)
    e1[0] = 1
    coefficients = Y.conj().T @ e1
    setup_s = time.perf_counter()-setup_start
    evaluation_start = time.perf_counter()
    shape = (etas.size, grid.size)
    scalars = np.empty(shape, dtype=np.complex128)
    residuals, deltas, bounds = (np.empty(shape) for _ in range(3))
    max_defect = max_scaled_defect = 0.0
    for i, eta in enumerate(etas):
        for left in range(0, grid.size, batch_points):
            sl = slice(left, left+batch_points)
            z = grid[sl]+1j*eta
            t = Y @ (coefficients[:, None]/(z[None, :]-nodes[:, None]))
            x = np.vstack((np.ones((1, z.size)), t))
            rn = np.linalg.norm(R @ x, axis=0)
            delta = np.abs(delta_row @ t)
            scalars[i, sl], residuals[i, sl], deltas[i, sl] = t[0], rn, delta
            bounds[i, sl] = norm_u*rn/eta+delta
            defect = np.linalg.norm(e1[:, None]-(z[None, :]*t-J@t), axis=0)
            defect_scale = np.maximum(1., (np.abs(z)+scales["norm_J_2"])*np.linalg.norm(t, axis=0))
            max_defect = max(max_defect, float(defect.max()))
            max_scaled_defect = max(max_scaled_defect, float((defect/defect_scale).max()))
    density = W*bounds/np.pi
    trap = getattr(np, "trapezoid", None) or np.trapz
    evaluation_s = time.perf_counter()-evaluation_start
    # Retained outputs + conservative batched complex temporary storage.
    output_bytes = scalars.nbytes+residuals.nbytes+deltas.nbytes+bounds.nbytes+density.nbytes+grid.nbytes+etas.nbytes
    workspace_bytes = scales["factor_workspace_estimate_bytes"]+output_bytes+16*(8*m*batch_points+4*m*m)
    summary = {
        "classification": "floating-point conditional residual diagnostic; not interval certification",
        "formula": "norm(u)*norm(d+(KV-VJ)t)/eta+abs((u^dagger V-e1^dagger)t)",
        "evaluation": "streamed QR", "changes_refinement_rule": False,
        "max_scalar_bound_per_eta": bounds.max(axis=1).tolist(),
        "max_density_bound_per_eta": density.max(axis=1).tolist(),
        "grid_integral_density_bound_per_eta": [float(trap(row, grid)) for row in density],
        **scales, "setup_s": setup_s, "evaluation_s": evaluation_s,
        "total_s": setup_s+evaluation_s, "batch_points": batch_points,
        "workspace_estimate_bytes": int(workspace_bytes), "output_storage_bytes": int(output_bytes),
        "cache_loading": "existing arrays; NPZ CLI materializes cache, not disk streaming",
        "max_solve_defect": max_defect, "max_scaled_solve_defect": max_scaled_defect,
        "production_performance": "NOT_MEASURED", "physical_H_actions": 0,
        "actual_checkpoint_execution": "NOT_RUN", "actual_refinement": "HOLD",
        "grid_integral_classification": "trapezoid diagnostic; not a certified continuum integral",
    }
    return {"grid": grid, "etas": etas, "scalar_resolvent": scalars, "scalar_bound": bounds,
            "density_bound": density, "residual_norm": residuals, "coordinate_delta": deltas,
            "summary": summary}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("postprocess")
    command.add_argument("--checkpoint", type=Path, required=True)
    command.add_argument("--weight", type=float, required=True)
    command.add_argument("--out", type=Path, required=True)
    command.add_argument("--block-rows", type=int, default=64)
    command.add_argument("--batch-points", type=int, default=256)
    args = parser.parse_args(argv)
    if args.out.exists():
        parser.error("--out must be a new output directory")
    with np.load(args.checkpoint, allow_pickle=False) as checkpoint:
        V, KV, u = (checkpoint[key] for key in ("V", "KV", "u"))
        if V.ndim == 2 and V.shape[1] > 128:
            parser.error("CLI requires m <= 128")
        result = residual_diagnostic_qr(V, KV, u, args.weight, np.linspace(0., 20., 2001),
                                       np.array([.05, .1, .2]), args.block_rows, args.batch_points)
    summary = result.pop("summary")
    args.out.mkdir(parents=True, exist_ok=False)
    np.savez(args.out/"residual.npz", **result)
    (args.out/"residual_summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    print(json.dumps({"output": str(args.out), "physical_H_actions": 0, "shape": list(result["scalar_bound"].shape)}))


if __name__ == "__main__":
    main()
