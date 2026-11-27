"""Binary64 reference operator for CONTRACT.json / THEORY_KO.md.

All integrals concern the declared detected-electron window. The deterministic
cell box is a sensitivity set and has no statistical coverage interpretation.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np

UNIT = Path(__file__).resolve().parents[1]
FACTOR = 2.0 * math.pi * 1e-23
EPSILON = 1.602176634e-19
POWERS_R = (0, 1, 2)
POWERS_Q = (0.0, 0.5, 1.0)


def atomic_json(path, obj):
    """Atomic replacement for generated files; invocation IDs are managed outside."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(obj, f, indent=2, allow_nan=False, ensure_ascii=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
        dfd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def vector(x, name):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim != 1 or not len(x) or not np.all(np.isfinite(x)):
        raise ValueError(name + " must be a finite nonempty vector")
    return x


def grid(x, name, positive=False):
    x = vector(x, name)
    if len(x) < 2 or np.any(np.diff(x) <= 0):
        raise ValueError(name + " must be strictly increasing with >=2 knots")
    if positive and np.any(x <= 0):
        raise ValueError(name + " must be positive")
    return x


@dataclass(frozen=True)
class Source:
    energy: np.ndarray
    mu: np.ndarray
    values: np.ndarray
    uncertainty_percent: np.ndarray
    csv_sha256: str = "control"
    raw_values_preserved: int = 0


def validate_source(s):
    E = grid(s.energy, "E", positive=True)
    mu = grid(s.mu, "mu")
    y = np.asarray(s.values, dtype=np.float64)
    u = vector(s.uncertainty_percent, "row uncertainty")
    if y.shape != (len(mu), len(E)) or len(u) != len(mu):
        raise ValueError("incomplete rectangular source or row uncertainty")
    if not np.all(np.isfinite(y)) or np.any(y < 0):
        raise ValueError("source values must be finite and nonnegative")
    if np.any(u < 0) or np.any(u >= 100):
        raise ValueError("row uncertainty must lie in [0,100)")
    if mu[0] < -1 or mu[-1] > 1:
        raise ValueError("mu outside physical support")
    return E, mu, y, u


def load_source(csv_path=None, json_path=None, primary_energies=(3, 4, 5, 6)):
    """Check source JSON/CSV transcription, then select only E=3..6 eV."""
    if tuple(primary_energies) != (3, 4, 5, 6):
        raise ValueError("primary selection is frozen at 3,4,5,6 eV; E=2 excluded")
    default = csv_path is None and json_path is None
    csv_path = Path(csv_path or UNIT / "source/Childers2004_TableIV_source_transcript.csv")
    json_path = Path(json_path or UNIT / "source/Childers2004_TableIV_source_transcript.json")
    data = csv_path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if default:
        contract = json.loads((UNIT / "CONTRACT.json").read_text())
        if sha != contract["source"]["csv_sha256"]:
            raise ValueError("immutable source CSV SHA mismatch")
    transcript = json.loads(json_path.read_text())
    expected_fields = ["theta_deg"] + [f"D_E1_{e}eV" for e in (2, 3, 4, 5, 6)] + ["row_quoted_one_sigma_percent"]
    reader = csv.DictReader(io.StringIO(data.decode()))
    if reader.fieldnames != expected_fields:
        raise ValueError("source CSV column schema mismatch")
    rows = list(reader)
    if len(rows) != 8 or transcript["energy_columns_eV"] != [2, 3, 4, 5, 6] or len(transcript["rows"]) != 8:
        raise ValueError("source raw rectangle must contain 8x5 cells")
    theta, y, u = [], [], []
    for r, t in zip(rows, transcript["rows"]):
        theta.append(float(r["theta_deg"]))
        yy = [float(r[f"D_E1_{e}eV"]) for e in (2, 3, 4, 5, 6)]
        uu = float(r["row_quoted_one_sigma_percent"])
        if theta[-1] != t["theta_deg"] or yy != t["ddcs_native"] or yy != [float(v) for v in t["printed_values"]] or uu != t["quoted_one_sigma_percent"]:
            raise ValueError("JSON/CSV raw-cell or uncertainty mismatch")
        y.append(yy)
        u.append(uu)
    theta = grid(theta, "theta")
    if theta.tolist() != [15, 20, 25, 30, 40, 60, 90, 120]:
        raise ValueError("source angular knots changed")
    y = np.asarray(y, dtype=np.float64)
    if not np.all(np.isfinite(y)) or np.any(y < 0):
        raise ValueError("all 40 source values must be finite and nonnegative")
    mu = np.cos(np.deg2rad(theta))[::-1].copy()
    s = Source(np.array(primary_energies, dtype=float), mu, y[::-1, 1:].copy(), np.asarray(u)[::-1].copy(), sha, 40)
    validate_source(s)
    return s


def interval(nodes, window):
    if window is None:
        return float(nodes[0]), float(nodes[-1])
    w = vector(window, "window")
    if len(w) != 2 or w[0] >= w[1] or w[0] < nodes[0] or w[1] > nodes[-1]:
        raise ValueError("window outside source support; extrapolation is forbidden")
    return float(w[0]), float(w[1])


def hat_integral_weights(nodes, power, window=None):
    """Exact segment primitive integral of x**power times each linear hat."""
    x = grid(nodes, "hat nodes")
    if power not in (0, 0.5, 1, 2):
        raise ValueError("unsupported power")
    if power == 0.5 and np.any(x <= 0):
        raise ValueError("fractional power requires positive nodes")
    lo, hi = interval(x, window)
    w = np.zeros(len(x))
    for i, (a, b) in enumerate(zip(x[:-1], x[1:])):
        c, d = max(a, lo), min(b, hi)
        if c >= d:
            continue
        p0 = (d ** (power + 1) - c ** (power + 1)) / (power + 1)
        p1 = (d ** (power + 2) - c ** (power + 2)) / (power + 2)
        w[i] += (b * p0 - p1) / (b - a)
        w[i + 1] += (p1 - a * p0) / (b - a)
    return w


def _box_inputs(a, b, low, high):
    a, b, low, high = [vector(x, name) for x, name in zip((a, b, low, high), ("a", "b", "low", "high"))]
    if any(x.shape != a.shape for x in (b, low, high)) or np.any(a <= 0) or np.any(low <= 0) or np.any(high < low):
        raise ValueError("ratio requires a>0, 0<low<=high, matching finite vectors")
    return a, b, low, high


def linear_box_extrema(weights, low, high):
    w, lo, hi = [vector(x, name) for x, name in zip((weights, low, high), ("weights", "low", "high"))]
    if w.shape != lo.shape or w.shape != hi.shape or np.any(lo > hi):
        raise ValueError("invalid linear box")
    zmin = np.where(w < 0, hi, lo)
    zmax = np.where(w > 0, hi, lo)
    return {"minimum": float(w @ zmin), "maximum": float(w @ zmax), "min_witness": zmin.tolist(), "max_witness": zmax.tolist()}


def ratio_box_extrema(a, b, low, high):
    """Global min/max by n+1 sorted threshold vertices, with actual witnesses."""
    a, b, lo, hi = _box_inputs(a, b, low, high)
    order = np.argsort(b / a, kind="stable")
    aa, bb, ll, hh = (x[order] for x in (a, b, lo, hi))
    d = hh - ll
    # Prefix sums produce all n+1 candidate numerators/denominators in O(n).
    da = np.r_[0.0, np.cumsum(aa * d)]
    db = np.r_[0.0, np.cumsum(bb * d)]
    mins = (float(bb @ ll) + db) / (float(aa @ ll) + da)
    maxs = (float(bb @ hh) - db) / (float(aa @ hh) - da)
    result = {"method": "sorted threshold scan; deterministic box, not CI", "candidate_count_per_extremum": len(a) + 1, "sort_order": order.tolist()}
    for label, values, index, minimize in (("min", mins, int(np.argmin(mins)), True), ("max", maxs, int(np.argmax(maxs)), False)):
        zz = np.where(np.arange(len(a)) < index, hh if minimize else ll, ll if minimize else hh)
        z = np.empty_like(zz)
        z[order] = zz
        actual = float((b @ z) / (a @ z))
        c = b - actual * a
        best_linear = np.where(c < 0, hi, lo) if minimize else np.where(c > 0, hi, lo)
        scale = max(float(np.sum(np.abs(b * z))), abs(actual) * float(a @ z), np.finfo(float).tiny)
        result[label + "imum"] = actual
        result[label + "_witness"] = z.tolist()
        result[label + "_threshold_index"] = index
        result[label + "_equality_scaled_residual"] = abs(float(c @ z)) / scale
        result[label + "_stationarity_scaled_gap"] = abs(float(c @ z - c @ best_linear)) / scale
    return result


def moment_weights(s, E_window=None, mu_window=None):
    E, mu, _, _ = validate_source(s)
    A = {r: hat_integral_weights(mu, r, mu_window) for r in POWERS_R}
    B = {q: hat_integral_weights(E, q, E_window) for q in POWERS_Q}
    return {(r, q): np.outer(A[r], B[q]) for r in POWERS_R for q in POWERS_Q}, A, B


def moment_key(r, q):
    return f"R_{r}_{q:g}"


def window_moments(s, E_window=None, mu_window=None):
    E, mu, y, u = validate_source(s)
    weights, A, B = moment_weights(s, E_window, mu_window)
    v = {key: float(np.sum(y * w)) for key, w in weights.items()}
    if v[(0, 0)] <= 0:
        raise ValueError("window measure must be positive")
    N = v[(0, 0)]
    ratio_weights = {"mean_mu": weights[(1, 0)], "mean_P2": (3 * weights[(2, 0)] - weights[(0, 0)]) / 2,
                     "mean_E_eV": weights[(0, 1)], "mean_sqrtE_mu": weights[(1, 0.5)]}
    ratios = {name: float(np.sum(y * w) / N) for name, w in ratio_weights.items()}
    low = (y * (1 - u[:, None] / 100)).ravel()
    high = (y * (1 + u[:, None] / 100)).ravel()
    raw_bounds = {moment_key(r, q): linear_box_extrema((FACTOR * w).ravel(), low, high) for (r, q), w in weights.items()}
    ratio_bounds = {name: ratio_box_extrema(weights[(0, 0)].ravel(), w.ravel(), low, high) for name, w in ratio_weights.items()}
    trans = (v[(0, 1)] - v[(2, 1)]) / 2
    second = np.array([trans, trans, v[(2, 1)]])
    cov = second / N - np.array([0, 0, ratios["mean_sqrtE_mu"] ** 2])
    theta = np.rad2deg(np.arccos(mu))
    return {
        "claim": "conditional detected-electron window moments under declared interpolation and deterministic sensitivity box",
        "parent_HE_ANG_state": "SOURCE_INPUT_PENDING",
        "source": {"csv_sha256": s.csv_sha256, "raw_cells_preserved": s.raw_values_preserved, "primary_cells": int(y.size), "E2_excluded": True},
        "window": {"E_eV": list(interval(E, E_window)), "mu": list(interval(mu, mu_window)), "theta_degrees": [float(theta[-1]), float(theta[0])]},
        "interpolation": "tensor linear hats in increasing mu and E; axisymmetric laboratory completion; no extrapolation",
        "units": {"source_native": "10^-19 cm^2/(sr eV)", "R_rq": "m^2 eV^q", "per_energy_J_r": "m^2/eV", "tensor_scale": "2 m_e epsilon", "momentum_scale": "sqrt(2 m_e epsilon)", "epsilon_J_per_eV": EPSILON},
        "raw_moments": {moment_key(r, q): FACTOR * vv for (r, q), vv in v.items()},
        "raw_moment_box": raw_bounds,
        "per_energy": [{"E_eV": float(e), "J_r_m2_per_eV": {str(r): FACTOR * float(y[:, j] @ A[r]) for r in POWERS_R}} for j, e in enumerate(E)],
        "conditional": ratios, "conditional_deterministic_box_not_CI": ratio_bounds,
        "U_W_J_m2": EPSILON * FACTOR * v[(0, 1)],
        "P_z_div_sqrt_2me_epsilon": FACTOR * v[(1, 0.5)],
        "second_tensor_diag_div_2me_epsilon": (FACTOR * second).tolist(),
        "STF_tensor_diag_div_2me_epsilon": (FACTOR * (second - np.sum(second) / 3)).tolist(),
        "conditional_covariance_diag_div_2me_epsilon": cov.tolist(),
        "invariants": {"positive_N": N > 0, "trace_tensor_scaled_residual": float(abs(np.sum(second) - v[(0, 1)]) / v[(0, 1)]),
                       "minimum_covariance_eigenvalue": float(np.min(cov)), "covariance_PSD_tolerance": 1e-12 * ratios["mean_E_eV"],
                       "Cauchy_Schwarz_margin_native": N * v[(2, 1)] - v[(1, 0.5)] ** 2},
        "witness_layout": "row-major, increasing mu then increasing E",
        "cells": [{"index": i * len(E) + j, "mu": float(m), "theta_deg": float(theta[i]), "E_eV": float(e), "ddcs_native": float(y[i, j]), "quoted_row_sigma_percent": float(u[i]), "box_low": float(low[i * len(E) + j]), "box_high": float(high[i * len(E) + j])} for i, m in enumerate(mu) for j, e in enumerate(E)],
        "uncertainty_notice": "Source percentages are quoted 1-sigma; chosen independent-coordinate box is deterministic, not a CI or coverage bound. No covariance, reference-DCS error, interpolation error or omitted-domain bound inferred.",
    }


def quadrature_moments(s, order=32, coordinate="mu"):
    """Independent local bilinear formula at cellwise GL nodes (no hat weights)."""
    E, mu, y, _ = validate_source(s)
    if coordinate not in ("mu", "theta"):
        raise ValueError("quadrature coordinate")
    g, w = np.polynomial.legendre.leggauss(order)
    t = (g + 1) / 2
    W = w[:, None] * w[None, :]
    total = {(r, q): 0.0 for r in POWERS_R for q in POWERS_Q}
    if coordinate == "theta":
        x = np.arccos(mu[::-1])
        yy = y[::-1]
    else:
        x, yy = mu, y
    for i in range(len(x) - 1):
        a, b = x[i:i+2]
        xx = a + (b - a) * t
        m = xx if coordinate == "mu" else np.cos(xx)
        jac = np.ones_like(xx) if coordinate == "mu" else np.sin(xx)
        for j in range(len(E) - 1):
            c, d = E[j:j+2]
            ee = c + (d - c) * t
            # This local four-corner evaluation is independent of analytic hats.
            f = ((1 - t[:, None]) * (1 - t[None, :]) * yy[i, j] + t[:, None] * (1 - t[None, :]) * yy[i+1, j]
                 + (1 - t[:, None]) * t[None, :] * yy[i, j+1] + t[:, None] * t[None, :] * yy[i+1, j+1])
            for r, q in total:
                total[(r, q)] += float(np.sum(W * f * ((m**r) * jac)[:, None] * (ee**q)[None, :])) * (b - a) * (d - c) / 4
    return total


def theta_interpolation_control(s, order=32):
    v = quadrature_moments(s, order, "theta")
    N = v[(0, 0)]
    return {"model": "piecewise linear theta with sin(theta) Jacobian; same knots/energy/window; representation sensitivity only",
            "order": order, "raw_moments": {moment_key(r, q): FACTOR * z for (r, q), z in v.items()},
            "conditional": {"mean_mu": v[(1, 0)] / N, "mean_P2": (3 * v[(2, 0)] / N - 1) / 2,
                            "mean_E_eV": v[(0, 1)] / N, "mean_sqrtE_mu": v[(1, 0.5)] / N}}
