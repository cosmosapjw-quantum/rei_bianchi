"""Independent proper-time ODE integration of an HE25 physical model.

The model supplies the physical RHS and its pinned photon quadrature. This lane
uses SciPy adaptive integration; it does not share the production transport
integrator or replace the native H/He microphysics with a photo-only surrogate.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy import sparse


def solve_reference(model, rtol=1e-10, atol=1e-12, method="Radau"):
    """Integrate physical state in seconds and return ``model.result``.

    ``scale`` conditions each state coordinate. Absolute tolerance therefore
    applies to ``z=y/scale``; relative tolerance applies to the same z. The
    model owns RHS one-sided values at declared discontinuities.
    """
    if method not in ("Radau", "DOP853"):
        raise ValueError("reference method must be Radau or DOP853")
    if not (math.isfinite(rtol) and 0 < rtol < 1):
        raise ValueError("invalid relative tolerance")
    if not (math.isfinite(atol) and 0 < atol < 1):
        raise ValueError("invalid scaled absolute tolerance")

    scale = np.asarray(model.scale, dtype=float)
    y0 = np.asarray(model.initial_state(), dtype=float)
    if y0.ndim != 1 or scale.shape != y0.shape or y0.size == 0:
        raise ValueError("initial state and scale must be equal nonempty vectors")
    if not np.all(np.isfinite(y0)) or not np.all(np.isfinite(scale)) or np.any(scale <= 0):
        raise ValueError("initial state and scale must be finite; scale positive")
    t_end = float(model.t_end)
    if not math.isfinite(t_end) or t_end <= 0:
        raise ValueError("t_end must be positive finite proper seconds")
    raw_breakpoints = np.asarray(getattr(model, "breakpoints", ()), dtype=float)
    if raw_breakpoints.ndim != 1 or not np.all(np.isfinite(raw_breakpoints)):
        raise ValueError("breakpoints must be a finite one-dimensional sequence")
    if np.any(raw_breakpoints <= 0) or np.any(raw_breakpoints >= t_end):
        raise ValueError("breakpoints must lie strictly inside (0, t_end)")
    if raw_breakpoints.size and np.any(np.diff(raw_breakpoints) <= 0):
        raise ValueError("breakpoints must be strictly increasing")

    bounds = np.concatenate(([0.0], raw_breakpoints, [t_end]))
    z = y0 / scale

    def scaled_rhs(t, state):
        derivative = np.asarray(model.rhs(t, state * scale), dtype=float)
        if derivative.shape != scale.shape or not np.all(np.isfinite(derivative)):
            raise FloatingPointError("nonfinite or wrong-sized physical RHS")
        return derivative / scale

    options = {}
    if method == "Radau":
        physical_jac = getattr(model, "jac", None)
        if physical_jac is not None:
            if not callable(physical_jac):
                raise ValueError("model.jac must be callable")

            def scaled_jac(t, state):
                jacobian = physical_jac(t, state * scale)
                if jacobian.shape != (z.size, z.size):
                    raise ValueError("physical Jacobian shape does not match state")
                if sparse.issparse(jacobian):
                    if not np.all(np.isfinite(jacobian.data)):
                        raise FloatingPointError("nonfinite physical Jacobian")
                    return sparse.diags(1.0 / scale) @ jacobian @ sparse.diags(scale)
                jacobian = np.asarray(jacobian, dtype=float)
                if not np.all(np.isfinite(jacobian)):
                    raise FloatingPointError("nonfinite physical Jacobian")
                return jacobian * scale[np.newaxis, :] / scale[:, np.newaxis]

            options["jac"] = scaled_jac
        else:
            sparsity = getattr(model, "jac_sparsity", None)
            if sparsity is not None:
                if sparsity.shape != (z.size, z.size):
                    raise ValueError("Jacobian sparsity shape does not match state")
                options["jac_sparsity"] = sparsity

    evaluations = jac_evaluations = linear_solves = 0
    segment_count = 0
    for left, right in zip(bounds[:-1], bounds[1:]):
        set_interval = getattr(model, "set_interval", None)
        if set_interval is not None:
            set_interval(float(left), float(right))
        solution = solve_ivp(
            scaled_rhs, (float(left), float(right)), z, method=method,
            rtol=rtol, atol=atol, dense_output=True, **options,
        )
        evaluations += solution.nfev
        jac_evaluations += solution.njev
        linear_solves += solution.nlu
        segment_count += 1
        if not solution.success:
            raise RuntimeError(
                f"reference integration failed on [{left:.17g}, {right:.17g}]: "
                + solution.message
            )
        z = solution.y[:, -1]
        if not np.all(np.isfinite(z)):
            raise FloatingPointError("nonfinite reference final state")

    metadata = {
        "method": method,
        "rtol": rtol,
        "atol_scaled": atol,
        "segment_count": segment_count,
        "nfev": evaluations,
        "njev": jac_evaluations,
        "nlu": linear_solves,
        "t_end_s": t_end,
    }
    return model.result(z * scale, metadata)
