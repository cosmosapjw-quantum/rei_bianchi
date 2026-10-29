"""Exact fixed-clock Jacobian of the frozen prescribed-bath Coupled RHS.

Source: coupled.py Git blob 4773d4278e1fa2f1a8a24a9df79f9ba5d46d5771.
No source import, bath reconstruction, IVP, or numerical differentiation occurs.
The supplied model must be the frozen Coupled instance, including its compiled
event matrices. Electron density is prescribed by that source's saved bath;
the electron ledger is an output and does not feed recombination hazards.
"""
import numpy as np


CHARGE = np.array([0, 0, 1, 0, 1, 0, 1, 0, 1, 2, 0, 1, 2, 0, 1, 2, 3])


def physical_jacobian(model, t, state, mode="ON"):
    """Return d(rhs_physical)/d(state) at fixed t and prescribed bath.

    Rows/columns follow the frozen 23-state ordering. The compiled affine
    event operator contains source, particle escape, decay and boundary ledger
    derivatives. The only remaining nonlinear event is n+H -> D capture.
    """
    state = np.asarray(state)
    if state.shape != (23,):
        raise ValueError("expected frozen 23-state ordering")
    G, nref, _, _ = model.fields(t)
    _, matrix, _, power, loss = model.new[mode]
    jac = np.zeros((23, 23), dtype=np.result_type(state, matrix, float))
    jac[:19, :19] = matrix[:19]
    jac[:17, :17] += G
    jac[21:23, :19] = matrix[19:21]
    jac[22, :17] += CHARGE @ G
    jac[19:21, :17] = power
    jac[19, 19], jac[20, 20] = -loss
    coefficient = nref * model.c["capture_C_cm3_s"]
    for hydrogen, deuterium in ((1, 3), (2, 4)):
        # Differentiate the mass-action polynomial directly, including at zero.
        gradient = np.zeros(23, dtype=jac.dtype)
        gradient[0] = coefficient * state[hydrogen]
        gradient[hydrogen] = coefficient * state[0]
        jac[0] -= gradient
        jac[hydrogen] -= gradient
        jac[deuterium] += gradient
    return jac


def scaled_jacobian(model, t, scaled, mode="ON"):
    """Exact derivative in the solver's frozen scaled coordinates, D^-1 J D."""
    scale = np.asarray(model.scale)
    if scale.shape != (23,) or np.any(scale <= 0) or not np.isfinite(scale).all():
        raise ValueError("invalid frozen solver scale")
    jac = physical_jacobian(model, t, np.asarray(scaled) * scale, mode)
    return jac * scale[None, :] / scale[:, None]


def jacobian(model, t, u, on):
    """Controller API: boolean ON/OFF, derivative in frozen solver coordinates."""
    if not isinstance(on, (bool, np.bool_)):
        raise TypeError("on must be boolean")
    return scaled_jacobian(model, t, u, "ON" if on else "OFF")
