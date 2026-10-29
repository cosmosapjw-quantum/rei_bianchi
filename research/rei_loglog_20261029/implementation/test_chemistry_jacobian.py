"""Bounded point checks; caller supplies the actual frozen model/saved state.

No IVP or model setup occurs here. Scientific execution requires the controller's
frozen run contract. Finite differences are verification only.
"""
import numpy as np
from chemistry_jacobian import physical_jacobian, scaled_jacobian


def check_saved_state(model, t, physical, mode, directions, steps):
    """Return raw Jv/central-difference errors for explicit contract inputs.

    directions are in scaled coordinates. No acceptance tolerance is invented;
    the controller must apply the frozen numerical acceptance criteria.
    """
    physical = np.asarray(physical)
    scaled = physical / model.scale
    jac = scaled_jacobian(model, t, scaled, mode)
    physical_jac = physical_jacobian(model, t, physical, mode)
    rows = []
    for direction_id, direction in enumerate(directions):
        direction = np.asarray(direction)
        if direction.shape != (23,):
            raise ValueError("direction must have 23 components")
        jv = jac @ direction
        for step in steps:
            if step <= 0:
                raise ValueError("central-difference step must be positive")
            plus = model.rhs(t, scaled + step * direction, mode)
            minus = model.rhs(t, scaled - step * direction, mode)
            finite_difference = (plus - minus) / (2 * step)
            error = finite_difference - jv
            rows.append({"direction": direction_id, "step": float(step),
                         "jv": jv.tolist(), "finite_difference": finite_difference.tolist(),
                         "absolute_error": np.abs(error).tolist(),
                         "max_absolute_error": float(np.max(np.abs(error))),
                         "max_jv": float(np.max(np.abs(jv))),
                         "max_finite_difference": float(np.max(np.abs(finite_difference)))})
    # Ledger invariants apply to physical coordinates. Hidden bath terms are
    # state independent, so their state derivatives vanish at this fixed clock.
    baryon = np.array([1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 7, 7, 7, 7,
                        1, 3, 0, 0, 1, 0])
    charge = np.array([0, 0, 1, 0, 1, 0, 1, 0, 1, 2, 0, 1, 2, 0, 1, 2, 3,
                        0, 1, 0, 0, 0, -1])
    invariants = {}
    for name, weight in (("baryon", baryon), ("charge", charge)):
        terms = weight[:, None] * physical_jac
        denominator = np.abs(terms).sum(axis=0)
        numerator = np.abs(terms.sum(axis=0))
        residual = np.divide(numerator, denominator, out=np.zeros(23), where=denominator != 0)
        invariants[name] = {"relative_residual_by_column": residual.tolist(),
                            "maximum_relative_residual": float(residual.max())}
    return {"mode": mode, "t": float(t), "ivp_calls": 0,
            "finite_jacobian": bool(np.isfinite(jac).all()),
            "scale_transform_max_error": float(np.max(np.abs(
                jac * model.scale[:, None] - physical_jac * model.scale[None, :]))),
            "ledger_feedback_columns_max": float(np.max(np.abs(jac[:, 21:23]))),
            "ledger_invariants": invariants,
            "checks": rows}
