"""Analytic values and time derivatives of archived DOP853 dense polynomials.

The seven coefficient rows are the saved SciPy ``Dop853DenseOutput.F``.
This module does not run an ODE or approximate a derivative by subtraction.
``residual = reconstructed_derivative - rhs`` fixes the sign used throughout.
"""
from __future__ import annotations

import numpy as np


def dense_value_derivative(t, t_old, h, y_old, coefficients):
    """Return (value, dvalue/dt), with the state axis last for vector times.

    ``t`` must belong to the closed saved step.  The recurrence differentiates
    every multiplication by x or (1-x), with x=(t-t_old)/h.  The initial state
    enters only the value, avoiding subtraction of nearly equal O(1) states.
    """
    y_old = np.asarray(y_old, dtype=float)
    coefficients = np.asarray(coefficients, dtype=float)
    times = np.asarray(t, dtype=float)
    if y_old.ndim != 1 or coefficients.shape != (7, y_old.size):
        raise ValueError("seven coefficient rows and a one-dimensional state required")
    if times.ndim > 1 or not np.isfinite(times).all():
        raise ValueError("finite scalar or one-dimensional times required")
    if not np.isfinite(t_old) or not np.isfinite(h) or h <= 0:
        raise ValueError("a finite positive step is required")
    if not np.isfinite(y_old).all() or not np.isfinite(coefficients).all():
        raise ValueError("nonfinite saved polynomial")
    x = (times-t_old)/h
    # Allow only normalization roundoff at an actual saved endpoint.
    eps = 8*np.finfo(float).eps
    if np.any(x < -eps) or np.any(x > 1+eps):
        raise ValueError("dense evaluation outside the saved step")
    x = x[..., None]
    value = np.zeros(x.shape[:-1]+y_old.shape)
    derivative_x = np.zeros_like(value)
    for i, coefficient in enumerate(coefficients[::-1]):
        before = value + coefficient
        if i % 2 == 0:
            derivative_x = derivative_x*x + before
            value = before*x
        else:
            derivative_x = derivative_x*(1-x) - before
            value = before*(1-x)
    return value+y_old, derivative_x/h


def defect(t, t_old, h, y_old, coefficients, rhs):
    """Evaluate the signed local defect at one scalar time (one RHS call)."""
    if np.ndim(t) != 0:
        raise ValueError("defect consumes one scalar time so calls remain countable")
    value, derivative = dense_value_derivative(t, t_old, h, y_old, coefficients)
    force = np.asarray(rhs(float(t), value), dtype=float)
    if force.shape != value.shape or not np.isfinite(force).all():
        raise ValueError("RHS shape/finiteness mismatch")
    return value, derivative-force


def signed_defect_balance(delta0, delta1, force_difference_integral,
                          reconstruction_residual_integral):
    """Check delta=hat_y-y using delta'=F(hat_y)-F(y)+r_hat-r_y.

    The last argument is the integral of (r_hat-r_y).  This algebraic balance
    tests sign/assembly; quadrature accuracy is a separately reported quantity.
    """
    return (np.asarray(delta1)-np.asarray(delta0)
            -np.asarray(force_difference_integral)
            -np.asarray(reconstruction_residual_integral))
