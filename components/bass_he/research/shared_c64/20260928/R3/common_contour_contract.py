"""Research-only contracts for BASS_HE common-contour R3.

This module deliberately does not call the spectral solver.  It separates three
questions that were conflated in earlier exploratory work:

1. the analytic rho-domain of the known kernel on a supplied finite trace,
2. composition of numerical error components only after a separate lifted
   homotopy/same-sheet authority has been established, and
3. an a-priori observable-error bound that uses a cheap approximate stochastic
   chain plus certified per-event probability error radii.

No production tolerance or BASS_HE physics is changed here.
"""
from __future__ import annotations

import math
from numbers import Integral
import numpy as np


def _nonnegative_finite(x, name):
    if isinstance(x, (bool, np.bool_)) or not np.isscalar(x) or np.iscomplexobj(x):
        raise ValueError(f"{name} must be a real scalar")
    x = float(x)
    if not math.isfinite(x) or x < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return x


def kernel_disk_certificate(R, rho_max):
    """Sufficient open-disk certificate for K=(1-rho^2/R^2)^(-1/2).

    For a finite set of nonzero contour points R_j, the germ about rho=0 has
    singularities at rho=+-R_j.  Hence the exact radius of the common Taylor
    disk for the supplied finite trace is r_* = min_j |R_j|.  This does *not*
    claim that the maximal continuation interval along real rho ends at r_*;
    off-axis singularities can leave a longer real interval available.
    """
    rho_max = _nonnegative_finite(rho_max, "rho_max")
    R = np.asarray(R, complex)
    if R.ndim != 1 or len(R) == 0 or np.any(~np.isfinite(R)) or np.any(R == 0):
        raise ValueError("finite nonzero one-dimensional R trace required")
    r_star = float(np.min(np.abs(R)))
    if not rho_max < r_star:
        raise ValueError("rho_max must satisfy 0 <= rho_max < r_star")
    return {
        "status": "CERTIFIED_OPEN_DISK",
        "r_star": r_star,
        "rho_max": rho_max,
        "q_max": float((rho_max / r_star) ** 2),
        "nearest_kernel_singularity_distance": r_star,
        "scope": "FINITE_TRACE_KERNEL_ONLY",
        "claim": "EXACT_TAYLOR_GERM_RADIUS_NOT_MAXIMAL_REAL_RHO_INTERVAL",
    }


def total_error_budget(*, spectral, quadrature, interpolation, roundoff,
                       homotopy_certified):
    """Compose numerical error radii only after homotopy is independently closed.

    The same-sheet/lifted-contour question is a logical gate, not a numerical
    term to be hidden inside an epsilon.  Therefore this function fails closed
    unless that authority is supplied separately.
    """
    if not isinstance(homotopy_certified, (bool, np.bool_)):
        raise ValueError("homotopy_certified must be boolean")
    if not homotopy_certified:
        raise RuntimeError("same-sheet lifted homotopy is not certified")
    parts = {
        "spectral": _nonnegative_finite(spectral, "spectral"),
        "quadrature": _nonnegative_finite(quadrature, "quadrature"),
        "interpolation": _nonnegative_finite(interpolation, "interpolation"),
        "roundoff": _nonnegative_finite(roundoff, "roundoff"),
    }
    return {
        "status": "NUMERICAL_COMPONENTS_COMPOSED_HOMOTOPY_SEPARATELY_CERTIFIED",
        "components": parts,
        "total": float(sum(parts.values())),
        "homotopy_error_term": "NOT_NUMERIC_ZERO_BY_SEPARATE_AUTHORITY",
    }


def _validate_event(dim, event):
    if not isinstance(event, (tuple, list)) or len(event) != 3:
        raise ValueError("event must be (i,j,sink)")
    i, j, sink = event
    if any(isinstance(k, bool) or not isinstance(k, Integral) for k in (i, j)):
        raise ValueError("event indices must be integers")
    if not (0 <= i < dim and 0 <= j < dim) or i == j:
        raise ValueError("distinct in-range event indices required")
    if not isinstance(sink, (bool, np.bool_)):
        raise ValueError("sink flag must be boolean")
    return int(i), int(j), bool(sink)


def _event_matrix(dim, p, event):
    i, j, sink = _validate_event(dim, event)
    T = np.eye(dim)
    T[i, i] = 1.0 - p
    T[j, i] = p
    if not sink:
        T[i, j] = p
        T[j, j] = 1.0 - p
    return T


def hybrid_pruning_bound(approximate, error_radii, events, initial, observable):
    """A-priori observable bound from cheap q_e and |p_e-q_e| <= eps_e.

    Let Q_e be the approximate stochastic events and T_e the unknown true
    events with the same two-state topology.  For the exact hybrid telescope,

        c_e = (p_e-q_e) (lambda^T_{e,j}-lambda^T_{e,i}) * local_population_Q.

    Define lambda^Q using only the approximate downstream chain.  Because every
    stochastic event maps [0,1]^d into itself, and for either reversible or
    one-way sink topology a row-vector perturbation by T_e-Q_e has infinity
    norm at most |p_e-q_e|,

        ||lambda^T_e-lambda^Q_e||_inf
        <= osc(w) sum_{k>e} eps_k,

    where osc(w)=max(w)-min(w). Therefore

        |lambda^T_{e,j}-lambda^T_{e,i}|
        <= min(osc(w), |lambda^Q_{e,j}-lambda^Q_{e,i}|
                         + 2 osc(w) sum_{k>e} eps_k).

    This yields a pre-computation bound without knowing p_e itself.  It becomes
    operational pruning only when the q_e and eps_e contracts are genuinely
    cheaper than the exact event calculation they are meant to avoid.
    """
    q = np.asarray(approximate, float)
    eps = np.asarray(error_radii, float)
    y0 = np.asarray(initial, float)
    w = np.asarray(observable, float)
    if q.ndim != 1 or eps.shape != q.shape or len(q) != len(events) or len(q) == 0:
        raise ValueError("compatible nonempty probability/error/event vectors required")
    if y0.ndim != 1 or w.shape != y0.shape or len(y0) < 2:
        raise ValueError("compatible state and observable vectors required")
    if any(np.any(~np.isfinite(a)) for a in (q, eps, y0, w)):
        raise ValueError("finite inputs required")
    if np.any((q < 0) | (q > 1)) or np.any(eps < 0):
        raise ValueError("q must be stochastic and error radii nonnegative")
    if np.any(y0 < 0) or abs(float(y0.sum()) - 1.0) > 1e-12:
        raise ValueError("normalized nonnegative initial probability required")
    if np.any((w < 0) | (w > 1)):
        raise ValueError("observable must lie in [0,1]")

    dim = len(y0)
    checked_events = [_validate_event(dim, e) for e in events]
    Qs = [_event_matrix(dim, float(v), e) for v, e in zip(q, checked_events)]

    # Q-upstream state immediately before each event.
    upstream = []
    y = y0.copy()
    for Q in Qs:
        upstream.append(y.copy())
        y = Q @ y

    # Q-downstream adjoint immediately after each event.
    adjoint = [None] * len(q)
    row = w.copy()
    for e in range(len(q) - 1, -1, -1):
        adjoint[e] = row.copy()
        row = row @ Qs[e]

    # Tail error budget E_{>e}.
    tail = np.zeros(len(q), float)
    running = 0.0
    for e in range(len(q) - 1, -1, -1):
        tail[e] = running
        running += float(eps[e])

    observable_oscillation = float(np.max(w) - np.min(w))
    rows = []
    total = 0.0
    for e, (i, j, sink) in enumerate(checked_events):
        approx_sensitivity = float(abs(adjoint[e][j] - adjoint[e][i]))
        sensitivity_bound = float(min(observable_oscillation,
                                      approx_sensitivity + 2.0 * observable_oscillation * tail[e]))
        population_factor = float(upstream[e][i] if sink else abs(upstream[e][i] - upstream[e][j]))
        local = float(eps[e] * sensitivity_bound * population_factor)
        total += local
        rows.append({
            "event": e,
            "i": i,
            "j": j,
            "sink": sink,
            "error_radius": float(eps[e]),
            "tail_error_radius": float(tail[e]),
            "approx_downstream_sensitivity": approx_sensitivity,
            "certified_downstream_sensitivity": sensitivity_bound,
            "approx_upstream_population_factor": population_factor,
            "observable_error_contribution_bound": local,
        })

    return {
        "status": "A_PRIORI_BOUND_GIVEN_VALID_Q_AND_EVENT_ERROR_RADII",
        "observable_error_bound": float(total),
        "global_l1_probability_bound": float(np.sum(eps)),
        "oscillation_weighted_global_bound": float(observable_oscillation * np.sum(eps)),
        "observable_oscillation": observable_oscillation,
        "events": rows,
        "requires_exact_probabilities": False,
        "requires_certified_event_error_radii": True,
        "scope": "SAME_EVENT_TOPOLOGY_COLUMN_STOCHASTIC_CHAIN_BOUNDED_OBSERVABLE",
    }
