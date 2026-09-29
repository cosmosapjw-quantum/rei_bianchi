"""P0.5-B2C0 phase-space maintenance kernel.

Scope
-----
- Primary history: B2B MFP-consistent physical branch.
- Variables: overdensity Delta, temperature T, H/He ion fractions.
- Full-OTS recombination source vector and net external photon demand.
- Deterministic and Beta/Dirichlet patchiness closures.
- F=1 phase-space domain and sharp self-shielding mask auditor.
- Direct fine-bin sum versus independent coarse phase-space quadrature.
- Density-only clumping is an auditor, never the primary maintenance model.

This is a numerical/closure lock, not an astrophysical topology calibration.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from numpy.polynomial.hermite import hermgauss
from numpy.polynomial.legendre import leggauss
from scipy.optimize import brentq, root
from scipy.special import expit, logsumexp

MPC_CM = 3.085677581491367e24
NH0_CM3 = 1.88e-7
YHE = 0.079
DELTA_MIN = 1.0e-2
DELTA_MAX = 100.0
MHR_BETA = 2.52
GAMMA_MINUS_ONE = 0.18
SIGMA_LNT = 0.22
T_MIN_K = 2.5e3
T_MAX_K = 8.0e4

# OTS cross sections locked in B2A.
SIGMA_OTS = {
    "H24": 1.2391519584513023e-18,
    "HeI24": 7.43469869411065e-18,
    "H41": 2.884642817876362e-19,
    "HeI41": 3.0402144676144673e-18,
    "H54": 1.2306959247142394e-19,
    "HeI54": 1.6907806870529807e-18,
    "HeII54": 1.5872802575386495e-18,
}

B_STOICH = np.array(
    [
        [-1.0, 0.0, 0.0],
        [+1.0, 0.0, 0.0],
        [0.0, -1.0, 0.0],
        [0.0, +1.0, -1.0],
        [0.0, 0.0, +1.0],
    ]
)

@dataclass(frozen=True)
class HistoryState:
    z: float
    x_hii: float
    x_heii: float
    x_heiii: float
    temperature: float
    gamma_hi: float


def sigmoid(x: np.ndarray | float) -> np.ndarray:
    return expit(x)


def softmax3(logit2: np.ndarray, logit3: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    zero = np.zeros_like(logit2)
    stacked = np.stack([zero, logit2, logit3], axis=-1)
    norm = logsumexp(stacked, axis=-1, keepdims=True)
    probs = np.exp(stacked - norm)
    return probs[..., 0], probs[..., 1], probs[..., 2]


def logit(x: float) -> float:
    return math.log(x / (1.0 - x))


def lambda_hi(T: np.ndarray) -> np.ndarray:
    return 315614.0 / T


def lambda_hei(T: np.ndarray) -> np.ndarray:
    return 570670.0 / T


def lambda_heii(T: np.ndarray) -> np.ndarray:
    return 1263030.0 / T


def alpha_b_hii(T: np.ndarray) -> np.ndarray:
    ll = lambda_hi(T)
    return 2.753e-14 * ll**1.5 / (1.0 + (ll / 2.740) ** 0.407) ** 2.242


def alpha_a_heii(T: np.ndarray) -> np.ndarray:
    ll = lambda_hei(T)
    base = 3.0e-14 * ll**0.654
    dr = 1.9e-3 * T**-1.5 * np.exp(-473638.0 / T) * (
        1.0 + 0.3 * np.exp(-94728.0 / T)
    )
    gate = sigmoid((T - 1.5e4) / 250.0)
    return base + gate * dr


def alpha_b_heii(T: np.ndarray) -> np.ndarray:
    ll = lambda_hei(T)
    base = 1.26e-14 * ll**0.750
    dr = 1.9e-3 * T**-1.5 * np.exp(-473638.0 / T) * (
        1.0 + 0.3 * np.exp(-94728.0 / T)
    )
    gate = sigmoid((T - 1.5e4) / 250.0)
    return base + gate * dr


def alpha_a_heiii(T: np.ndarray) -> np.ndarray:
    ll = lambda_heii(T)
    return 2.0 * 1.269e-13 * ll**1.503 / (1.0 + (ll / 0.522) ** 0.470) ** 1.923


def alpha_b_heiii(T: np.ndarray) -> np.ndarray:
    ll = lambda_heii(T)
    return 2.0 * 2.753e-14 * ll**1.5 / (1.0 + (ll / 2.740) ** 0.407) ** 2.242


def alpha_heiii_n2(T: np.ndarray) -> np.ndarray:
    return 3.4e-13 * (T / 1.0e4) ** -0.6


def mhr_measure(y: np.ndarray, z: float, c0: float) -> np.ndarray:
    delta0 = 7.61 / (1.0 + z)
    sigma_d = 2.0 * delta0 / 3.0
    # P(Delta)dDelta = exp[(1-beta)y - ...]dy up to normalization.
    return np.exp(
        (1.0 - MHR_BETA) * y
        - (np.exp(-2.0 * y / 3.0) - c0) ** 2 / (2.0 * sigma_d**2)
    )


def calibrate_mhr_c0(z: float, n: int = 768) -> float:
    x, w = leggauss(n)
    ya, yb = math.log(DELTA_MIN), math.log(DELTA_MAX)
    y = 0.5 * (yb - ya) * x + 0.5 * (yb + ya)
    wy = 0.5 * (yb - ya) * w
    delta = np.exp(y)

    def mean_minus_one(c0: float) -> float:
        raw = wy * mhr_measure(y, z, c0)
        return float(np.sum(raw * delta) / np.sum(raw) - 1.0)

    return float(brentq(mean_minus_one, -10.0, 10.0))


def delta_quadrature(z: float, n: int, c0: float) -> tuple[np.ndarray, np.ndarray]:
    x, w = leggauss(n)
    ya, yb = math.log(DELTA_MIN), math.log(DELTA_MAX)
    y = 0.5 * (yb - ya) * x + 0.5 * (yb + ya)
    wy = 0.5 * (yb - ya) * w
    raw = wy * mhr_measure(y, z, c0)
    weights = raw / np.sum(raw)
    return np.exp(y), weights


def temperature_quadrature(
    delta: np.ndarray,
    delta_weights: np.ndarray,
    target_temperature: float,
    n_t: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Truncated-lognormal conditional T quadrature on a locked physical domain."""
    xi, wi = leggauss(n_t)
    ta, tb = math.log(T_MIN_K), math.log(T_MAX_K)
    log_t = 0.5 * (tb - ta) * xi + 0.5 * (tb + ta)
    w_log_t = 0.5 * (tb - ta) * wi
    temperature_nodes = np.exp(log_t)

    shape = delta**GAMMA_MINUS_ONE

    def conditional_weights(log_scale: float) -> np.ndarray:
        mu = log_scale + np.log(shape)
        gaussian = np.exp(
            -0.5 * ((log_t[None, :] - mu[:, None]) / SIGMA_LNT) ** 2
        ) / (math.sqrt(2.0 * math.pi) * SIGMA_LNT)
        raw = gaussian * w_log_t[None, :]
        return raw / np.sum(raw, axis=1, keepdims=True)

    def mean_temperature_minus_target(log_scale: float) -> float:
        wt = conditional_weights(log_scale)
        mean_t = np.sum(
            delta_weights[:, None] * wt * temperature_nodes[None, :]
        )
        return float(mean_t - target_temperature)

    log_scale = brentq(
        mean_temperature_minus_target,
        math.log(target_temperature / 20.0),
        math.log(target_temperature * 20.0),
    )
    wt = conditional_weights(log_scale)
    temperatures = np.broadcast_to(
        temperature_nodes[None, :], (len(delta), n_t)
    )
    return temperatures, wt

def build_grid(
    state: HistoryState,
    n_delta: int,
    n_t: int,
    c0: float,
) -> dict[str, np.ndarray]:
    delta, wd = delta_quadrature(state.z, n_delta, c0)
    temperature, wt = temperature_quadrature(
        delta, wd, state.temperature, n_t
    )
    weight = wd[:, None] * wt
    delta2 = np.broadcast_to(delta[:, None], temperature.shape)
    return {
        "delta": delta2,
        "temperature": temperature,
        "weight": weight,
        "delta_nodes": delta,
        "delta_weights": wd,
    }


def calibrate_fraction_offsets(
    state: HistoryState,
    calibration_grid: dict[str, np.ndarray],
) -> dict[str, float]:
    delta = calibration_grid["delta"]
    temperature = calibration_grid["temperature"]
    weight = calibration_grid["weight"]
    log_d = np.log(delta)
    log_t = np.log(temperature / state.temperature)

    h_base = logit(state.x_hii) + 0.75 * log_t - 0.45 * log_d

    def h_equation(offset: float) -> float:
        return float(np.sum(weight * sigmoid(h_base + offset)) - state.x_hii)

    h_offset = float(brentq(h_equation, -30.0, 30.0))

    p1 = max(1.0 - state.x_heii - state.x_heiii, 1.0e-14)
    l2_base = (
        math.log(state.x_heii / p1)
        + 0.35 * log_t
        - 0.20 * log_d
    )
    l3_base = (
        math.log(state.x_heiii / p1)
        + 1.10 * log_t
        - 0.10 * log_d
    )

    def he_equations(offsets: np.ndarray) -> np.ndarray:
        _, p2, p3 = softmax3(
            l2_base + offsets[0],
            l3_base + offsets[1],
        )
        return np.array(
            [
                np.sum(weight * p2) - state.x_heii,
                np.sum(weight * p3) - state.x_heiii,
            ]
        )

    solution = root(he_equations, np.zeros(2), method="hybr")
    if not solution.success or np.linalg.norm(he_equations(solution.x)) > 1.0e-11:
        raise RuntimeError(
            f"Helium offset calibration failed at z={state.z}: {solution.message}"
        )
    return {
        "h_offset": h_offset,
        "heii_offset": float(solution.x[0]),
        "heiii_offset": float(solution.x[1]),
    }


def conditional_means(
    state: HistoryState,
    grid: dict[str, np.ndarray],
    offsets: dict[str, float],
) -> dict[str, np.ndarray]:
    delta = grid["delta"]
    temperature = grid["temperature"]
    log_d = np.log(delta)
    log_t = np.log(temperature / state.temperature)

    x_hii = sigmoid(
        logit(state.x_hii)
        + 0.75 * log_t
        - 0.45 * log_d
        + offsets["h_offset"]
    )

    p1_global = max(1.0 - state.x_heii - state.x_heiii, 1.0e-14)
    l2 = (
        math.log(state.x_heii / p1_global)
        + 0.35 * log_t
        - 0.20 * log_d
        + offsets["heii_offset"]
    )
    l3 = (
        math.log(state.x_heiii / p1_global)
        + 1.10 * log_t
        - 0.10 * log_d
        + offsets["heiii_offset"]
    )
    x_hei, x_heii, x_heiii = softmax3(l2, l3)
    return {
        "xHII": x_hii,
        "xHeI": x_hei,
        "xHeII": x_heii,
        "xHeIII": x_heiii,
    }


def conditional_moments(
    means: dict[str, np.ndarray],
    closure: str,
) -> dict[str, np.ndarray]:
    h = means["xHII"]
    p1, p2, p3 = means["xHeI"], means["xHeII"], means["xHeIII"]

    if closure == "DETERMINISTIC":
        h2 = h * h
        p22 = p2 * p2
        p33 = p3 * p3
        p23 = p2 * p3
        k_h = np.full_like(h, np.inf)
        k_he = np.full_like(h, np.inf)
    elif closure == "PATCHY_BETA_DIRICHLET":
        # Bounded Beta closure. Patchiness is strongest away from pure states.
        k_h = 15.0 + 85.0 * (2.0 * h - 1.0) ** 2
        h2 = h * h + h * (1.0 - h) / (k_h + 1.0)

        # Simplex-preserving Dirichlet closure.
        max_p = np.maximum.reduce([p1, p2, p3])
        k_he = 10.0 + 90.0 * max_p**2
        p22 = (k_he * p2 * p2 + p2) / (k_he + 1.0)
        p33 = (k_he * p3 * p3 + p3) / (k_he + 1.0)
        p23 = k_he * p2 * p3 / (k_he + 1.0)
    else:
        raise ValueError(closure)

    return {
        **means,
        "xHII2": h2,
        "xHeII2": p22,
        "xHeIII2": p33,
        "xHeII_xHeIII": p23,
        "kappa_H": k_h,
        "kappa_He": k_he,
    }


def full_ots_kernel(
    state: HistoryState,
    grid: dict[str, np.ndarray],
    moments: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    delta = grid["delta"]
    T = grid["temperature"]
    n_h = NH0_CM3 * (1.0 + state.z) ** 3 * delta
    n_he = YHE * n_h

    h = moments["xHII"]
    p1 = moments["xHeI"]
    p2 = moments["xHeII"]
    p3 = moments["xHeIII"]
    h2 = moments["xHII2"]
    p22 = moments["xHeII2"]
    p33 = moments["xHeIII2"]
    p23 = moments["xHeII_xHeIII"]

    # Exact conditional pair moments under independent H-Beta and He-Dirichlet.
    pair_hii = (
        n_h**2 * h2
        + n_h * n_he * h * (p2 + 2.0 * p3)
    )
    pair_heii = (
        n_h * n_he * h * p2
        + n_he**2 * (p22 + 2.0 * p23)
    )
    pair_heiii = (
        n_h * n_he * h * p3
        + n_he**2 * (p23 + 2.0 * p33)
    )

    n_hi_mean = n_h * (1.0 - h)
    n_hei_mean = n_he * p1
    n_heii_mean = n_he * p2
    floor = 1.0e-300

    y = (
        n_hi_mean * SIGMA_OTS["H24"]
        / (
            n_hi_mean * SIGMA_OTS["H24"]
            + n_hei_mean * SIGMA_OTS["HeI24"]
            + floor
        )
    )
    zfrac = (
        n_hi_mean * SIGMA_OTS["H41"]
        / (
            n_hi_mean * SIGMA_OTS["H41"]
            + n_hei_mean * SIGMA_OTS["HeI41"]
            + floor
        )
    )

    op_h54 = n_hi_mean * SIGMA_OTS["H54"]
    op_hei54 = n_hei_mean * SIGMA_OTS["HeI54"]
    op_heii54 = n_heii_mean * SIGMA_OTS["HeII54"]
    total54 = op_h54 + op_hei54 + op_heii54 + floor
    y2a = op_heii54 / total54
    y2b = op_hei54 / total54

    p_exc = 0.96
    l_cas = 1.425
    m_cas = 0.737
    v_t = sigmoid((T - 2.0e4) / 4.0e3)
    f_h = 1.0 - np.exp(-100.0 * (1.0 - h))
    w_cas = (l_cas - m_cas) + m_cas * y
    a_h = v_t * w_cas + (1.0 - v_t) * f_h * zfrac
    a_hei = (
        v_t * m_cas * (1.0 - y)
        + (1.0 - v_t) * f_h * (1.0 - zfrac)
    )

    a_a2 = alpha_a_heii(T)
    a_b2 = alpha_b_heii(T)
    a_a3 = alpha_a_heiii(T)
    a_b3 = alpha_b_heiii(T)
    a_n2 = np.minimum(alpha_heiii_n2(T), a_b3)
    a_cas = np.maximum(a_b3 - a_n2, 0.0)

    rates = [
        pair_hii * alpha_b_hii(T),
        pair_heii * np.maximum(a_a2 - a_b2, 0.0),
        pair_heii * a_b2,
        pair_heiii * np.maximum(a_a3 - a_b3, 0.0),
        pair_heiii * a_n2,
        pair_heiii * a_cas,
    ]

    vectors = [
        np.stack(
            [
                np.ones_like(T),
                -np.ones_like(T),
                np.zeros_like(T),
                np.zeros_like(T),
                np.zeros_like(T),
            ],
            axis=-1,
        ),
        np.stack([-y, y, y, -y, np.zeros_like(T)], axis=-1),
        np.stack(
            [
                -p_exc * np.ones_like(T),
                p_exc * np.ones_like(T),
                np.ones_like(T),
                -np.ones_like(T),
                np.zeros_like(T),
            ],
            axis=-1,
        ),
        np.stack(
            [
                -(1.0 - y2a - y2b),
                1.0 - y2a - y2b,
                -y2b,
                1.0 + y2b - y2a,
                -1.0 + y2a,
            ],
            axis=-1,
        ),
        np.stack(
            [
                -np.ones_like(T),
                np.ones_like(T),
                np.zeros_like(T),
                np.ones_like(T),
                -np.ones_like(T),
            ],
            axis=-1,
        ),
        np.stack(
            [
                -a_h,
                a_h,
                -a_hei,
                1.0 + a_hei,
                -np.ones_like(T),
            ],
            axis=-1,
        ),
    ]

    source = np.zeros(T.shape + (5,), dtype=float)
    for rate, vector in zip(rates, vectors):
        source += rate[..., None] * vector

    # Exact external transition solution for a nucleus-conserving source.
    m_ext = np.stack(
        [source[..., 0], source[..., 2], -source[..., 4]],
        axis=-1,
    )
    stoich_residual = np.einsum("ij,...j->...i", B_STOICH, m_ext) + source

    # H-only clumping auditors.
    delta_h = delta * h
    delta2_h2 = delta**2 * h2
    # Electron-weighted H recombination integrand before alpha.
    pair_hii_dimensionless = pair_hii / (
        (NH0_CM3 * (1.0 + state.z) ** 3) ** 2
    )

    return {
        "source": source,
        "m_ext": m_ext,
        "stoich_residual": stoich_residual,
        "pair_hii": pair_hii,
        "pair_heii": pair_heii,
        "pair_heiii": pair_heiii,
        "pair_hii_dimensionless": pair_hii_dimensionless,
        "delta_h": delta_h,
        "delta2_h2": delta2_h2,
        "alpha_H": alpha_b_hii(T),
        "y": y,
        "zfrac": zfrac,
        "y2a": y2a,
        "y2b": y2b,
    }


def transmission_mask(
    state: HistoryState,
    grid: dict[str, np.ndarray],
    lane: str,
) -> np.ndarray:
    if lane == "F_EQ_1":
        return np.ones_like(grid["delta"])
    if lane == "SHARP_SELF_SHIELDING_AUDITOR":
        delta_ss = (
            37.0
            * (grid["temperature"] / 1.0e4) ** 0.13
            * (state.gamma_hi / 1.0e-12) ** (2.0 / 3.0)
            * ((1.0 + state.z) / 8.0) ** (-3.0)
        )
        return (grid["delta"] <= delta_ss).astype(float)
    raise ValueError(lane)


def integrate_kernel(
    state: HistoryState,
    grid: dict[str, np.ndarray],
    kernel: dict[str, np.ndarray],
    transmission_lane: str,
) -> dict[str, Any]:
    mask = transmission_mask(state, grid, transmission_lane)
    weight = grid["weight"] * mask
    conversion = MPC_CM**3 / (1.0 + state.z) ** 3

    m_phys = np.sum(weight[..., None] * kernel["m_ext"], axis=(0, 1))
    m_comoving = m_phys * conversion

    source_phys = np.sum(weight[..., None] * kernel["source"], axis=(0, 1))
    stoich_integrated = B_STOICH @ m_phys + source_phys

    h_event_phys = np.sum(
        weight * kernel["alpha_H"] * kernel["pair_hii"],
        axis=(0, 1),
    )
    density_only_h_phys = alpha_b_hii(np.array(1.0e4)) * np.sum(
        weight * kernel["pair_hii"], axis=(0, 1)
    )

    mean_delta_h = np.sum(weight * kernel["delta_h"])
    c_hii = (
        np.sum(weight * kernel["delta2_h2"])
        / max(mean_delta_h**2, 1.0e-300)
    )
    c_rec_h = (
        np.sum(
            weight
            * (kernel["alpha_H"] / alpha_b_hii(np.array(1.0e4)))
            * kernel["delta2_h2"]
        )
        / max(mean_delta_h**2, 1.0e-300)
    )

    return {
        "m_phys": m_phys,
        "m_comoving": m_comoving,
        "m_total_comoving": float(np.sum(m_comoving)),
        "source_phys": source_phys,
        "integrated_stoich_residual": stoich_integrated,
        "minimum_bin_m_ext": float(np.min(kernel["m_ext"][mask > 0]))
        if np.any(mask > 0)
        else math.nan,
        "maximum_bin_stoich_residual": float(
            np.max(np.abs(kernel["stoich_residual"][mask > 0]))
        )
        if np.any(mask > 0)
        else math.nan,
        "active_volume_weight": float(np.sum(weight)),
        "h_recombination_event_comoving": float(h_event_phys * conversion),
        "density_only_h_recombination_comoving": float(
            density_only_h_phys * conversion
        ),
        "density_only_over_phase_h": float(
            density_only_h_phys / max(h_event_phys, 1.0e-300)
        ),
        "C_HII": float(c_hii),
        "C_rec_H": float(c_rec_h),
    }


def evaluate_resolution(
    state: HistoryState,
    offsets: dict[str, float],
    c0: float,
    n_delta: int,
    n_t: int,
    closure: str,
    transmission_lane: str,
) -> tuple[dict[str, Any], dict[str, np.ndarray], dict[str, np.ndarray], dict[str, np.ndarray]]:
    grid = build_grid(state, n_delta, n_t, c0)
    means = conditional_means(state, grid, offsets)
    moments = conditional_moments(means, closure)
    kernel = full_ots_kernel(state, grid, moments)
    result = integrate_kernel(state, grid, kernel, transmission_lane)
    return result, grid, moments, kernel


def run_stage(
    history_csv: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    history = pd.read_csv(history_csv)
    history = history[
        history["lane"] == "MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD"
    ].copy()
    states = [
        HistoryState(
            z=float(r.z),
            x_hii=float(r.xHII),
            x_heii=float(r.xHeII),
            x_heiii=float(r.xHeIII),
            temperature=float(r.T_K),
            gamma_hi=float(r.Gamma_HI),
        )
        for r in history.itertuples()
    ]

    calibration_rows = []
    summary_rows = []
    convergence_rows = []
    clumping_rows = []
    failure_rows = []
    representative_rows = []

    closures = ["DETERMINISTIC", "PATCHY_BETA_DIRICHLET"]
    transmissions = ["F_EQ_1", "SHARP_SELF_SHIELDING_AUDITOR"]

    for state in states:
        c0 = calibrate_mhr_c0(state.z)
        calibration_grid = build_grid(state, 256, 32, c0)
        offsets = calibrate_fraction_offsets(state, calibration_grid)
        cal_means = conditional_means(state, calibration_grid, offsets)
        weight = calibration_grid["weight"]

        recovered = {
            "xHII": float(np.sum(weight * cal_means["xHII"])),
            "xHeII": float(np.sum(weight * cal_means["xHeII"])),
            "xHeIII": float(np.sum(weight * cal_means["xHeIII"])),
            "temperature": float(
                np.sum(weight * calibration_grid["temperature"])
            ),
        }
        calibration_rows.append(
            {
                "z": state.z,
                "mhr_c0": c0,
                **offsets,
                "target_xHII": state.x_hii,
                "recovered_xHII": recovered["xHII"],
                "target_xHeII": state.x_heii,
                "recovered_xHeII": recovered["xHeII"],
                "target_xHeIII": state.x_heiii,
                "recovered_xHeIII": recovered["xHeIII"],
                "target_T_K": state.temperature,
                "recovered_T_K": recovered["temperature"],
            }
        )

        for closure in closures:
            for transmission in transmissions:
                fine, fine_grid, fine_moments, fine_kernel = evaluate_resolution(
                    state,
                    offsets,
                    c0,
                    512,
                    64,
                    closure,
                    transmission,
                )
                coarse, coarse_grid, coarse_moments, coarse_kernel = evaluate_resolution(
                    state,
                    offsets,
                    c0,
                    160,
                    32,
                    closure,
                    transmission,
                )

                component_relative = np.abs(
                    coarse["m_comoving"] - fine["m_comoving"]
                ) / np.maximum(np.abs(fine["m_comoving"]), 1.0e-300)
                total_relative = abs(
                    coarse["m_total_comoving"] - fine["m_total_comoving"]
                ) / max(abs(fine["m_total_comoving"]), 1.0e-300)

                convergence_rows.append(
                    {
                        "z": state.z,
                        "closure": closure,
                        "transmission_lane": transmission,
                        "fine_n_delta": 512,
                        "fine_n_T": 64,
                        "coarse_n_delta": 160,
                        "coarse_n_T": 32,
                        "relative_HI_transition": component_relative[0],
                        "relative_HeI_transition": component_relative[1],
                        "relative_HeII_transition": component_relative[2],
                        "relative_total": total_relative,
                    }
                )

                summary_rows.append(
                    {
                        "z": state.z,
                        "closure": closure,
                        "transmission_lane": transmission,
                        "m_HI_to_HII_s-1_cMpc-3": fine["m_comoving"][0],
                        "m_HeI_to_HeII_s-1_cMpc-3": fine["m_comoving"][1],
                        "m_HeII_to_HeIII_s-1_cMpc-3": fine["m_comoving"][2],
                        "m_total_s-1_cMpc-3": fine["m_total_comoving"],
                        "active_volume_weight": fine["active_volume_weight"],
                        "minimum_bin_m_ext_cm-3_s-1": fine["minimum_bin_m_ext"],
                        "maximum_bin_stoich_residual_cm-3_s-1":
                            fine["maximum_bin_stoich_residual"],
                        "integrated_stoich_residual_inf_cm-3_s-1":
                            np.max(np.abs(fine["integrated_stoich_residual"])),
                        "h_recombination_event_s-1_cMpc-3":
                            fine["h_recombination_event_comoving"],
                        "density_only_h_recombination_s-1_cMpc-3":
                            fine["density_only_h_recombination_comoving"],
                        "density_only_over_phase_h":
                            fine["density_only_over_phase_h"],
                        "C_HII": fine["C_HII"],
                        "C_rec_H": fine["C_rec_H"],
                    }
                )

                clumping_rows.append(
                    {
                        "z": state.z,
                        "closure": closure,
                        "transmission_lane": transmission,
                        "C_HII": fine["C_HII"],
                        "C_rec_H": fine["C_rec_H"],
                        "C_rec_over_C_HII":
                            fine["C_rec_H"] / fine["C_HII"],
                        "density_only_over_phase_h":
                            fine["density_only_over_phase_h"],
                    }
                )

                bad = np.argwhere(
                    (fine_kernel["m_ext"] < -1.0e-30).any(axis=-1)
                    | (
                        np.max(
                            np.abs(fine_kernel["stoich_residual"]),
                            axis=-1,
                        )
                        > 1.0e-24
                    )
                )
                for i_delta, i_t in bad[:1000]:
                    failure_rows.append(
                        {
                            "z": state.z,
                            "closure": closure,
                            "transmission_lane": transmission,
                            "delta": fine_grid["delta"][i_delta, i_t],
                            "T_K": fine_grid["temperature"][i_delta, i_t],
                            "m_H": fine_kernel["m_ext"][i_delta, i_t, 0],
                            "m_HeI": fine_kernel["m_ext"][i_delta, i_t, 1],
                            "m_HeII": fine_kernel["m_ext"][i_delta, i_t, 2],
                            "stoich_residual_inf":
                                np.max(
                                    np.abs(
                                        fine_kernel["stoich_residual"][
                                            i_delta, i_t
                                        ]
                                    )
                                ),
                        }
                    )

                if (
                    abs(state.z - 5.5) < 1.0e-8
                    and transmission == "F_EQ_1"
                ):
                    mask = np.ones_like(coarse_grid["delta"], dtype=bool)
                    flat_indices = np.argwhere(mask)
                    for i_delta, i_t in flat_indices:
                        representative_rows.append(
                            {
                                "closure": closure,
                                "delta": coarse_grid["delta"][i_delta, i_t],
                                "T_K": coarse_grid["temperature"][i_delta, i_t],
                                "weight": coarse_grid["weight"][i_delta, i_t],
                                "xHII": coarse_moments["xHII"][i_delta, i_t],
                                "xHeI": coarse_moments["xHeI"][i_delta, i_t],
                                "xHeII": coarse_moments["xHeII"][i_delta, i_t],
                                "xHeIII": coarse_moments["xHeIII"][i_delta, i_t],
                                "xHII2": coarse_moments["xHII2"][i_delta, i_t],
                                "m_HI_to_HII_cm-3_s-1":
                                    coarse_kernel["m_ext"][i_delta, i_t, 0],
                                "m_HeI_to_HeII_cm-3_s-1":
                                    coarse_kernel["m_ext"][i_delta, i_t, 1],
                                "m_HeII_to_HeIII_cm-3_s-1":
                                    coarse_kernel["m_ext"][i_delta, i_t, 2],
                                "stoich_residual_inf":
                                    np.max(
                                        np.abs(
                                            coarse_kernel["stoich_residual"][
                                                i_delta, i_t
                                            ]
                                        )
                                    ),
                            }
                        )

    calibration = pd.DataFrame(calibration_rows)
    summary = pd.DataFrame(summary_rows)
    convergence = pd.DataFrame(convergence_rows)
    clumping = pd.DataFrame(clumping_rows)
    failures = pd.DataFrame(failure_rows)
    representative = pd.DataFrame(representative_rows)

    calibration.to_csv(output_dir / "phase_space_calibration.csv", index=False)
    summary.to_csv(output_dir / "maintenance_summary.csv", index=False)
    convergence.to_csv(output_dir / "integration_convergence.csv", index=False)
    clumping.to_csv(output_dir / "clumping_auditor.csv", index=False)
    failures.to_csv(output_dir / "failed_bins.csv", index=False)
    representative.to_csv(
        output_dir / "kernel_grid_z5p5.csv.gz",
        index=False,
        compression="gzip",
    )

    max_mismatch = float(
        convergence[
            [
                "relative_HI_transition",
                "relative_HeI_transition",
                "relative_HeII_transition",
                "relative_total",
            ]
        ].to_numpy().max()
    )
    max_stoich = float(
        summary[
            [
                "maximum_bin_stoich_residual_cm-3_s-1",
                "integrated_stoich_residual_inf_cm-3_s-1",
            ]
        ].to_numpy().max()
    )
    min_m = float(summary["minimum_bin_m_ext_cm-3_s-1"].min())
    max_calibration_error = float(
        max(
            np.max(np.abs(calibration["target_xHII"] - calibration["recovered_xHII"])),
            np.max(np.abs(calibration["target_xHeII"] - calibration["recovered_xHeII"])),
            np.max(np.abs(calibration["target_xHeIII"] - calibration["recovered_xHeIII"])),
            np.max(
                np.abs(
                    calibration["target_T_K"] - calibration["recovered_T_K"]
                )
                / calibration["target_T_K"]
            ),
        )
    )

    f1 = clumping[clumping["transmission_lane"] == "F_EQ_1"]
    thermal_direction_pass = bool(
        (f1["C_rec_H"] < f1["C_HII"]).all()
        and (f1["density_only_over_phase_h"] > 1.0).all()
    )

    results = {
        "stage": "P0.5-B2C0-PHASESPACE-MAINTENANCE-KERNEL-LOCK",
        "verdict": (
            "PASS"
            if (
                max_mismatch < 0.01
                and max_stoich < 1.0e-24
                and min_m >= -1.0e-30
                and len(failures) == 0
                and thermal_direction_pass
            )
            else "FAIL"
        ),
        "phase_space_domain": {
            "Delta_min": DELTA_MIN,
            "Delta_max": DELTA_MAX,
            "temperature_relation_gamma_minus_one": GAMMA_MINUS_ONE,
            "sigma_lnT": SIGMA_LNT,
            "T_min_K": T_MIN_K,
            "T_max_K": T_MAX_K,
            "domain_note": (
                "F=1 applies on the finite locked Delta-T numerical diffuse-IGM domain; "
                "it is not an all-density physical IGM definition."
            ),
        },
        "closures": {
            "DETERMINISTIC": "conditional means; zero conditional variance",
            "PATCHY_BETA_DIRICHLET": {
                "hydrogen": "Beta moment with kappa_H=15+85(2x-1)^2",
                "helium": "Dirichlet moment with kappa_He=10+90 max(p_i)^2",
                "independence": "H Beta and He Dirichlet independent at fixed (Delta,T)",
                "OTS_fraction_closure": (
                    "event rates use exact conditional second moments; "
                    "OTS opacity fractions are evaluated at conditional means"
                ),
            },
        },
        "gates": {
            "direct_vs_phase_relative_mismatch_max": max_mismatch,
            "direct_vs_phase_target": 0.01,
            "maximum_stoichiometric_residual_cm-3_s-1": max_stoich,
            "minimum_external_transition_rate_cm-3_s-1": min_m,
            "failed_bin_count": int(len(failures)),
            "fraction_temperature_calibration_error_max": max_calibration_error,
            "thermal_suppression_direction": thermal_direction_pass,
        },
        "clumping_external_regression": {
            "Lumina_direction_only": (
                "C_rec<C_HII and density-only recombination exceeds the "
                "temperature-dependent phase-space result"
            ),
            "forced_factor_1p84": False,
            "observed_density_only_over_phase_range_F1": [
                float(f1["density_only_over_phase_h"].min()),
                float(f1["density_only_over_phase_h"].max()),
            ],
            "observed_Crec_over_CHII_range_F1": [
                float((f1["C_rec_H"] / f1["C_HII"]).min()),
                float((f1["C_rec_H"] / f1["C_HII"]).max()),
            ],
        },
        "forbidden_work_confirmed": [
            "unresolved sink",
            "front allocation",
            "source/f_esc calibration",
            "Bianchi geometry",
        ],
    }
    (output_dir.parent / "results.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--history", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_stage(args.history, args.output)
    print(json.dumps(result, indent=2))
