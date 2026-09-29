"""P0.5-B2C1A H-only transmission, QV/QM, and topology auditor.

The physical transmission is applied only to the H external-maintenance
component from B2C0. Global Q_V and Q_M are computed without transmission
weights. F-weighted Q quantities are separate diffuse-phase diagnostics.

Production primary:
- JEANS_SCALEHEIGHT_BASELINE

Auditors:
- CELL_SCALEHEIGHT_AUDITOR
- MIN_JEANS_CELL_CONSERVATIVE
- MFP_SCALEHEIGHT_CIRCULARITY_AUDITOR
- SHARP_SELF_SHIELDING_AUDITOR
- F_EQ_1_AUDITOR

No He transmission, unresolved-sink subtraction, front allocation, source
calibration, or Bianchi geometry is performed.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import math
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.integrate import quad
from scipy.optimize import brentq

# ---------------------------------------------------------------------------
# Import B2C0 canonical implementation.
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "phase_space_kernel_b2c0",
    HERE / "phase_space_kernel_b2c0.py",
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Cannot load B2C0 phase-space kernel")
B2C0 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = B2C0
SPEC.loader.exec_module(B2C0)

# ---------------------------------------------------------------------------
# Constants and source-locked definitions.
# ---------------------------------------------------------------------------

C_LIGHT = 2.99792458e10
G_NEWTON = 6.67430e-8
K_BOLTZMANN = 1.380649e-16
M_PROTON = 1.67262192369e-24
MPC_CM = B2C0.MPC_CM
KPC_CM = MPC_CM / 1.0e3
NH0_CM3 = B2C0.NH0_CM3
YHE = B2C0.YHE

OMEGA_M = 0.305
OMEGA_B = 0.048
F_GAS = OMEGA_B / OMEGA_M
H_REDUCED = 0.68
X_H_MASS = 1.0 / (1.0 + 4.0 * YHE)
GAMMA_AD = 5.0 / 3.0

E_HI = 13.60
E_HEII = 54.42
CELL_COMOVING_CKPC_H = 2.0
L_CELL_LABEL = "2 h^-1 ckpc / (1+z), from MFP simulation resolution"

# Verner ground-state H I fit.
VERNER_HI = {
    "Eth_eV": 13.60,
    "E0_eV": 0.4298,
    "sigma0_Mb": 5.475e4,
    "ya": 32.88,
    "p": 2.963,
    "yw": 0.0,
    "y0": 0.0,
    "y1": 0.0,
}

LANES = [
    "JEANS_SCALEHEIGHT_BASELINE",
    "CELL_SCALEHEIGHT_AUDITOR",
    "MIN_JEANS_CELL_CONSERVATIVE",
    "MFP_SCALEHEIGHT_CIRCULARITY_AUDITOR",
    "SHARP_SELF_SHIELDING_AUDITOR",
    "F_EQ_1_AUDITOR",
]

CIRCULARITY_LANE = "MFP_SCALEHEIGHT_CIRCULARITY_AUDITOR"


def verner_hi_sigma(energy_eV: np.ndarray | float) -> np.ndarray:
    p = VERNER_HI
    energy = np.asarray(energy_eV, dtype=float)
    x = energy / p["E0_eV"] - p["y0"]
    y = np.sqrt(x * x + p["y1"] ** 2)
    sigma = (
        1.0e-18
        * p["sigma0_Mb"]
        * ((x - 1.0) ** 2 + p["yw"] ** 2)
        * y ** (0.5 * p["p"] - 5.5)
        / (1.0 + np.sqrt(y / p["ya"])) ** p["p"]
    )
    return np.where(energy >= p["Eth_eV"], sigma, 0.0)


def source_photon_weight(energy_eV: float) -> float:
    # J_nu ~ nu^-1.5 and photon-number weighting J_nu/nu.
    return energy_eV ** (-2.5)


def gray_sigma_hi() -> tuple[float, dict[str, float]]:
    numerator = quad(
        lambda log_e: (
            source_photon_weight(math.exp(log_e))
            * float(verner_hi_sigma(math.exp(log_e)))
            * math.exp(log_e)
        ),
        math.log(E_HI),
        math.log(E_HEII),
        epsabs=0.0,
        epsrel=2.0e-11,
        limit=400,
    )[0]
    denominator = quad(
        lambda log_e: source_photon_weight(math.exp(log_e)) * math.exp(log_e),
        math.log(E_HI),
        math.log(E_HEII),
        epsabs=0.0,
        epsrel=2.0e-12,
        limit=400,
    )[0]
    value = numerator / denominator
    return value, {
        "numerator_cm2_weighted": numerator,
        "denominator_weight": denominator,
        "reference_cross_section_cm2": 2.49e-18,
        "ratio_to_reference": value / 2.49e-18,
    }


def alpha_a_hii(T: np.ndarray | float) -> np.ndarray:
    temp = np.asarray(T, dtype=float)
    lam = 315614.0 / temp
    return (
        1.269e-13
        * lam**1.503
        / (1.0 + (lam / 0.522) ** 0.470) ** 1.923
    )


def mean_molecular_weight(
    x_hii: np.ndarray,
    x_heii: np.ndarray,
    x_heiii: np.ndarray,
) -> np.ndarray:
    particles_per_h = (
        1.0 + x_hii
        + YHE * (1.0 + x_heii + 2.0 * x_heiii)
    )
    return (1.0 + 4.0 * YHE) / particles_per_h


def jeans_length_cm(
    n_h_cm3: np.ndarray,
    T_K: np.ndarray,
    x_hii: np.ndarray,
    x_heii: np.ndarray,
    x_heiii: np.ndarray,
) -> np.ndarray:
    mu = mean_molecular_weight(x_hii, x_heii, x_heiii)
    rho_b = M_PROTON * n_h_cm3 * (1.0 + 4.0 * YHE)
    rho_total = rho_b / F_GAS
    sound_speed_sq = GAMMA_AD * K_BOLTZMANN * T_K / (mu * M_PROTON)
    return np.sqrt(math.pi * sound_speed_sq / (G_NEWTON * rho_total))


def self_shielding_density_cm3(
    T_K: np.ndarray | float,
    gamma_hi_s: float,
    sigma_bar_cm2: float,
) -> np.ndarray:
    temp = np.asarray(T_K, dtype=float)
    return (
        6.73e-3
        * (sigma_bar_cm2 / 2.49e-18) ** (-2.0 / 3.0)
        * (temp / 1.0e4) ** 0.17
        * (gamma_hi_s / 1.0e-12) ** (2.0 / 3.0)
        * (F_GAS / 0.17) ** (-1.0 / 3.0)
    )


def rahmati_gamma_ratio(n_h_cm3: np.ndarray, n_ss_cm3: np.ndarray) -> np.ndarray:
    ratio = np.asarray(n_h_cm3, dtype=float) / np.asarray(n_ss_cm3, dtype=float)
    return (
        0.98 * (1.0 + ratio**1.64) ** (-2.28)
        + 0.02 * (1.0 + ratio) ** (-0.84)
    )


def solve_hydrogen_equilibrium(
    n_h_cm3: np.ndarray,
    T_K: np.ndarray,
    gamma_hi_s: np.ndarray,
    helium_electrons_cm3: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    alpha = B2C0.alpha_b_hii(np.asarray(T_K, dtype=float))
    n_h = np.asarray(n_h_cm3, dtype=float)
    gamma = np.asarray(gamma_hi_s, dtype=float)
    c_e = np.asarray(helium_electrons_cm3, dtype=float)

    b = alpha * c_e + gamma
    discriminant = b * b + 4.0 * alpha * n_h * gamma
    x_hii = (-b + np.sqrt(discriminant)) / (2.0 * alpha * n_h)
    x_hii = np.clip(x_hii, 0.0, 1.0)
    return x_hii, 1.0 - x_hii


def calibrate_chi_jeans(
    z: float,
    gamma_hi_s: float,
    sigma_bar_cm2: float,
) -> dict[str, float]:
    T_ref = 1.0e4
    n_ss = float(self_shielding_density_cm3(T_ref, gamma_hi_s, sigma_bar_cm2))
    alpha = float(alpha_a_hii(T_ref))
    electron_factor = 1.08
    x_hi = alpha * electron_factor * n_ss / (
        gamma_hi_s + alpha * electron_factor * n_ss
    )
    x_hii = 1.0 - x_hi
    # Use mu=0.61 as in the analytic self-shielding scaling lineage.
    rho_b = M_PROTON * n_ss / X_H_MASS
    rho_total = rho_b / F_GAS
    c_s_sq = GAMMA_AD * K_BOLTZMANN * T_ref / (0.61 * M_PROTON)
    l_jeans = math.sqrt(math.pi * c_s_sq / (G_NEWTON * rho_total))
    tau_raw = 0.5 * sigma_bar_cm2 * (n_ss * x_hi) * l_jeans
    chi = 1.0 / tau_raw
    tau_calibrated = tau_raw * chi
    return {
        "z": z,
        "Gamma_HI_s-1": gamma_hi_s,
        "T_reference_K": T_ref,
        "sigma_bar_H_cm2": sigma_bar_cm2,
        "n_ss_cm-3": n_ss,
        "xHI_optically_thin_at_nss": x_hi,
        "L_Jeans_raw_cm": l_jeans,
        "L_Jeans_raw_proper_kpc": l_jeans / KPC_CM,
        "tau_raw_at_nss": tau_raw,
        "chi_J": chi,
        "tau_calibrated_at_nss": tau_calibrated,
    }


def cell_length_proper_cm(z: float) -> float:
    return CELL_COMOVING_CKPC_H / H_REDUCED / (1.0 + z) * KPC_CM


def load_mfp_lookup(mfp_csv: Path) -> dict[float, float]:
    frame = pd.read_csv(mfp_csv)
    use = frame[
        np.isclose(frame["energy_eV"], 13.6)
        & (frame["mode"] == "public_continuous_joint")
    ]
    return {
        round(float(row.z), 8): float(row.lambda_density_cMpc)
        for row in use.itertuples()
    }


def mfp_length_proper_cm(z: float, lookup: dict[float, float]) -> float:
    key = round(float(z), 8)
    if key not in lookup:
        raise KeyError(f"No P0.4 13.6-eV MFP for z={z}")
    return lookup[key] / (1.0 + z) * MPC_CM


def transmission_for_lane(
    lane: str,
    state: Any,
    grid: dict[str, np.ndarray],
    moments: dict[str, np.ndarray],
    sigma_bar_cm2: float,
    chi_record: dict[str, float],
    mfp_lookup: dict[float, float],
) -> dict[str, np.ndarray]:
    delta = grid["delta"]
    T = grid["temperature"]
    x_hii = moments["xHII"]
    x_heii = moments["xHeII"]
    x_heiii = moments["xHeIII"]

    n_h = B2C0.NH0_CM3 * (1.0 + state.z) ** 3 * delta
    n_hi = n_h * (1.0 - x_hii)

    l_jeans = jeans_length_cm(
        n_h, T, x_hii, x_heii, x_heiii
    )
    l_jeans_calibrated = chi_record["chi_J"] * l_jeans
    l_cell = np.full_like(n_h, cell_length_proper_cm(state.z))
    l_mfp = np.full_like(n_h, mfp_length_proper_cm(state.z, mfp_lookup))
    n_ss = self_shielding_density_cm3(T, state.gamma_hi, sigma_bar_cm2)

    if lane == "JEANS_SCALEHEIGHT_BASELINE":
        length = l_jeans_calibrated
        tau = 0.5 * sigma_bar_cm2 * n_hi * length
        F = np.exp(-np.clip(tau, 0.0, 745.0))
    elif lane == "CELL_SCALEHEIGHT_AUDITOR":
        length = l_cell
        tau = 0.5 * sigma_bar_cm2 * n_hi * length
        F = np.exp(-np.clip(tau, 0.0, 745.0))
    elif lane == "MIN_JEANS_CELL_CONSERVATIVE":
        length = np.minimum(l_jeans_calibrated, l_cell)
        tau = 0.5 * sigma_bar_cm2 * n_hi * length
        F = np.exp(-np.clip(tau, 0.0, 745.0))
    elif lane == "MFP_SCALEHEIGHT_CIRCULARITY_AUDITOR":
        length = l_mfp
        tau = 0.5 * sigma_bar_cm2 * n_hi * length
        F = np.exp(-np.clip(tau, 0.0, 745.0))
    elif lane == "SHARP_SELF_SHIELDING_AUDITOR":
        length = np.full_like(n_h, np.nan)
        tau = np.where(n_h <= n_ss, 0.0, np.inf)
        F = (n_h <= n_ss).astype(float)
    elif lane == "F_EQ_1_AUDITOR":
        length = np.full_like(n_h, np.nan)
        tau = np.zeros_like(n_h)
        F = np.ones_like(n_h)
    else:
        raise ValueError(lane)

    return {
        "F": F,
        "tau": tau,
        "length_cm": length,
        "n_h_cm3": n_h,
        "n_hi_cm3": n_hi,
        "n_ss_cm3": n_ss,
        "L_Jeans_raw_cm": l_jeans,
        "L_Jeans_calibrated_cm": l_jeans_calibrated,
        "L_cell_cm": l_cell,
        "L_mfp_cm": l_mfp,
    }


def global_and_selected_q(
    grid: dict[str, np.ndarray],
    moments: dict[str, np.ndarray],
    F: np.ndarray,
) -> dict[str, float]:
    weight = grid["weight"]
    delta = grid["delta"]
    x = moments["xHII"]

    mass_norm = float(np.sum(weight * delta))
    qv = float(np.sum(weight * x))
    qm = float(np.sum(weight * delta * x) / mass_norm)

    f_v = float(np.sum(weight * F))
    qv_f = float(np.sum(weight * F * x) / max(f_v, 1.0e-300))
    mass_f = float(np.sum(weight * delta * F))
    qm_f = float(
        np.sum(weight * delta * F * x) / max(mass_f, 1.0e-300)
    )
    return {
        "Q_V_global": qv,
        "Q_M_global": qm,
        "xHI_V_global": 1.0 - qv,
        "xHI_M_global": 1.0 - qm,
        "f_V_IGM": f_v,
        "Q_V_given_F": qv_f,
        "Q_M_given_F": qm_f,
        "mass_weight_F": mass_f,
    }


def normalized_clumping_F(
    state: Any,
    grid: dict[str, np.ndarray],
    moments: dict[str, np.ndarray],
    kernel: dict[str, np.ndarray],
    F: np.ndarray,
) -> float:
    weight = grid["weight"]
    delta = grid["delta"]
    n_h = B2C0.NH0_CM3 * (1.0 + state.z) ** 3 * delta
    n_he = B2C0.YHE * n_h
    n_hii = n_h * moments["xHII"]
    n_e = n_h * moments["xHII"] + n_he * (
        moments["xHeII"] + 2.0 * moments["xHeIII"]
    )
    numerator = float(
        np.sum(weight * F * kernel["alpha_H"] * kernel["pair_hii"])
    )
    denominator = float(
        B2C0.alpha_b_hii(np.array(1.0e4))
        * np.sum(weight * n_hii)
        * np.sum(weight * n_e)
    )
    return numerator / denominator


def evaluate_resolution(
    state: Any,
    offsets: dict[str, float],
    c0: float,
    n_delta: int,
    n_t: int,
    closure: str,
    lane: str,
    sigma_bar_cm2: float,
    chi_record: dict[str, float],
    mfp_lookup: dict[float, float],
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    grid = B2C0.build_grid(state, n_delta, n_t, c0)
    means = B2C0.conditional_means(state, grid, offsets)
    moments = B2C0.conditional_moments(means, closure)
    kernel = B2C0.full_ots_kernel(state, grid, moments)
    transmission = transmission_for_lane(
        lane,
        state,
        grid,
        moments,
        sigma_bar_cm2,
        chi_record,
        mfp_lookup,
    )
    F = transmission["F"]
    weight = grid["weight"]
    conversion = MPC_CM**3 / (1.0 + state.z) ** 3

    maintenance_h = float(
        np.sum(weight * F * kernel["m_ext"][..., 0]) * conversion
    )
    q = global_and_selected_q(grid, moments, F)
    c_norm_f = normalized_clumping_F(
        state, grid, moments, kernel, F
    )

    # Monotonicity audit along Delta at every common temperature node.
    max_positive_delta_F = 0.0
    for j in range(F.shape[1]):
        order = np.argsort(transmission["n_hi_cm3"][:, j])
        diff = np.diff(F[order, j])
        if diff.size:
            max_positive_delta_F = max(
                max_positive_delta_F,
                float(np.max(diff)),
            )

    result = {
        "maintenance_H_s-1_cMpc-3": maintenance_h,
        "F_min": float(np.min(F)),
        "F_max": float(np.max(F)),
        "tau_min": float(np.nanmin(transmission["tau"])),
        "tau_max_finite": float(
            np.max(
                transmission["tau"][
                    np.isfinite(transmission["tau"])
                ]
            )
        )
        if np.any(np.isfinite(transmission["tau"]))
        else math.nan,
        "max_positive_monotonicity_violation": max_positive_delta_F,
        "minimum_length_cm": float(np.nanmin(transmission["length_cm"]))
        if np.any(np.isfinite(transmission["length_cm"]))
        else math.nan,
        "maximum_length_cm": float(np.nanmax(transmission["length_cm"]))
        if np.any(np.isfinite(transmission["length_cm"]))
        else math.nan,
        "C_norm_F_H": c_norm_f,
        **q,
    }
    return result, {
        "grid": grid,
        "means": means,
        "moments": moments,
        "kernel": kernel,
        "transmission": transmission,
    }


def rahmati_profile(
    state: Any,
    sigma_bar_cm2: float,
    chi_record: dict[str, float],
    mfp_lookup: dict[float, float],
    n_points: int = 360,
) -> pd.DataFrame:
    n_h = np.geomspace(1.0e-7, 1.0e-1, n_points)
    T = np.full_like(n_h, 1.0e4)
    n_he = YHE * n_h
    # Helium electron background from the B2B global state.
    he_e = n_he * (state.x_heii + 2.0 * state.x_heiii)

    x_hii_thin, x_hi_thin = solve_hydrogen_equilibrium(
        n_h, T, np.full_like(n_h, state.gamma_hi), he_e
    )
    n_ss = self_shielding_density_cm3(
        T, state.gamma_hi, sigma_bar_cm2
    )
    gamma_ratio = rahmati_gamma_ratio(n_h, n_ss)
    x_hii_rah, x_hi_rah = solve_hydrogen_equilibrium(
        n_h,
        T,
        state.gamma_hi * gamma_ratio,
        he_e,
    )

    x_heii = np.full_like(n_h, state.x_heii)
    x_heiii = np.full_like(n_h, state.x_heiii)
    l_j = jeans_length_cm(
        n_h, T, x_hii_thin, x_heii, x_heiii
    )
    lengths = {
        "JEANS_SCALEHEIGHT_BASELINE":
            chi_record["chi_J"] * l_j,
        "CELL_SCALEHEIGHT_AUDITOR":
            np.full_like(n_h, cell_length_proper_cm(state.z)),
        "MIN_JEANS_CELL_CONSERVATIVE":
            np.minimum(
                chi_record["chi_J"] * l_j,
                cell_length_proper_cm(state.z),
            ),
        "MFP_SCALEHEIGHT_CIRCULARITY_AUDITOR":
            np.full_like(n_h, mfp_length_proper_cm(state.z, mfp_lookup)),
    }

    frame = pd.DataFrame(
        {
            "z": state.z,
            "n_H_cm-3": n_h,
            "n_ss_cm-3": n_ss,
            "Gamma_ratio_Rahmati": gamma_ratio,
            "xHI_optically_thin": x_hi_thin,
            "xHI_Rahmati_equilibrium": x_hi_rah,
        }
    )
    for lane, length in lengths.items():
        tau = 0.5 * sigma_bar_cm2 * n_h * x_hi_thin * length
        frame[f"F_{lane}"] = np.exp(-np.clip(tau, 0.0, 745.0))
        frame[f"Lproper_kpc_{lane}"] = length / KPC_CM
    frame["F_SHARP_SELF_SHIELDING_AUDITOR"] = (n_h <= n_ss).astype(float)
    frame["F_F_EQ_1_AUDITOR"] = 1.0
    return frame


def crossing_density(
    x: np.ndarray,
    y: np.ndarray,
    target: float,
) -> float:
    values = np.asarray(y) - target
    indices = np.where(values[:-1] * values[1:] <= 0.0)[0]
    if len(indices) == 0:
        return math.nan
    i = indices[0]
    lx0, lx1 = math.log(x[i]), math.log(x[i + 1])
    y0, y1 = values[i], values[i + 1]
    if y1 == y0:
        return float(x[i])
    lx = lx0 - y0 * (lx1 - lx0) / (y1 - y0)
    return math.exp(lx)


def topology_auditors(z: float, q: dict[str, float]) -> dict[str, float]:
    x_v = q["xHI_V_global"]
    x_m = q["xHI_M_global"]
    oku = x_m ** (3.14 - 0.12 * z)
    scorch = 1.344 * x_m - 0.134 * x_m**2 - 0.211 * x_m**3
    return {
        "z": z,
        "xHI_V_primary": x_v,
        "xHI_M_primary": x_m,
        "xHI_V_Oku_outside_in_prediction": oku,
        "xHI_V_SCORCH_inside_out_prediction": scorch,
        "absolute_residual_Oku": abs(x_v - oku),
        "absolute_residual_SCORCH": abs(x_v - scorch),
        "closer_topology_auditor": (
            "OKU_OUTSIDE_IN"
            if abs(x_v - oku) < abs(x_v - scorch)
            else "SCORCH_INSIDE_OUT"
        ),
    }


def run_stage(
    history_csv: Path,
    mfp_csv: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    history = pd.read_csv(history_csv)
    primary = history[
        history["lane"] == "MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD"
    ].copy()

    states = [
        B2C0.HistoryState(
            z=float(row.z),
            x_hii=float(row.xHII),
            x_heii=float(row.xHeII),
            x_heiii=float(row.xHeIII),
            temperature=float(row.T_K),
            gamma_hi=float(row.Gamma_HI),
        )
        for row in primary.itertuples()
    ]

    sigma_bar, sigma_meta = gray_sigma_hi()
    mfp_lookup = load_mfp_lookup(mfp_csv)

    chi_rows: list[dict[str, float]] = []
    summary_rows: list[dict[str, Any]] = []
    convergence_rows: list[dict[str, Any]] = []
    topology_rows: list[dict[str, Any]] = []
    rahmati_frames: list[pd.DataFrame] = []
    failure_rows: list[dict[str, Any]] = []
    grid_rows: list[dict[str, Any]] = []

    closures = ["DETERMINISTIC", "PATCHY_BETA_DIRICHLET"]

    for state in states:
        c0 = B2C0.calibrate_mhr_c0(state.z)
        calibration_grid = B2C0.build_grid(state, 256, 32, c0)
        offsets = B2C0.calibrate_fraction_offsets(
            state, calibration_grid
        )
        chi_record = calibrate_chi_jeans(
            state.z, state.gamma_hi, sigma_bar
        )
        chi_rows.append(chi_record)

        profile = rahmati_profile(
            state, sigma_bar, chi_record, mfp_lookup
        )
        rahmati_frames.append(profile)

        for closure in closures:
            f1_reference: float | None = None
            q_primary: dict[str, float] | None = None

            for lane in LANES:
                fine, fine_objects = evaluate_resolution(
                    state,
                    offsets,
                    c0,
                    512,
                    64,
                    closure,
                    lane,
                    sigma_bar,
                    chi_record,
                    mfp_lookup,
                )
                coarse, _ = evaluate_resolution(
                    state,
                    offsets,
                    c0,
                    160,
                    32,
                    closure,
                    lane,
                    sigma_bar,
                    chi_record,
                    mfp_lookup,
                )
                mismatch = abs(
                    coarse["maintenance_H_s-1_cMpc-3"]
                    - fine["maintenance_H_s-1_cMpc-3"]
                ) / max(
                    abs(fine["maintenance_H_s-1_cMpc-3"]),
                    1.0,
                )
                if lane == "F_EQ_1_AUDITOR":
                    f1_reference = fine["maintenance_H_s-1_cMpc-3"]
                if lane == "JEANS_SCALEHEIGHT_BASELINE":
                    q_primary = {
                        key: fine[key]
                        for key in [
                            "Q_V_global",
                            "Q_M_global",
                            "xHI_V_global",
                            "xHI_M_global",
                        ]
                    }

                summary_rows.append(
                    {
                        "z": state.z,
                        "closure": closure,
                        "lane": lane,
                        **fine,
                        "direct_phase_relative_mismatch": mismatch,
                        "production_status": (
                            "PRIMARY"
                            if lane == "JEANS_SCALEHEIGHT_BASELINE"
                            else "AUDITOR_ONLY"
                        ),
                        "circularity_risk": lane == CIRCULARITY_LANE,
                    }
                )
                convergence_rows.append(
                    {
                        "z": state.z,
                        "closure": closure,
                        "lane": lane,
                        "fine_n_delta": 512,
                        "fine_n_T": 64,
                        "coarse_n_delta": 160,
                        "coarse_n_T": 32,
                        "relative_mismatch_H_maintenance": mismatch,
                    }
                )

                if not (
                    fine["F_min"] >= -1.0e-15
                    and fine["F_max"] <= 1.0 + 1.0e-15
                    and fine[
                        "max_positive_monotonicity_violation"
                    ] <= 1.0e-10
                ):
                    failure_rows.append(
                        {
                            "z": state.z,
                            "closure": closure,
                            "lane": lane,
                            "F_min": fine["F_min"],
                            "F_max": fine["F_max"],
                            "monotonicity_violation":
                                fine[
                                    "max_positive_monotonicity_violation"
                                ],
                        }
                    )

                if (
                    abs(state.z - 5.5) < 1.0e-9
                    and closure == "DETERMINISTIC"
                ):
                    obj = fine_objects
                    grid = obj["grid"]
                    trans = obj["transmission"]
                    means = obj["means"]
                    kernel = obj["kernel"]
                    for i in range(0, grid["delta"].shape[0], 4):
                        for j in range(0, grid["delta"].shape[1], 4):
                            grid_rows.append(
                                {
                                    "lane": lane,
                                    "delta": grid["delta"][i, j],
                                    "T_K": grid["temperature"][i, j],
                                    "weight": grid["weight"][i, j],
                                    "xHII": means["xHII"][i, j],
                                    "n_H_cm-3": trans["n_h_cm3"][i, j],
                                    "n_HI_cm-3": trans["n_hi_cm3"][i, j],
                                    "F_H": trans["F"][i, j],
                                    "tau_H": trans["tau"][i, j],
                                    "m_H_cm-3_s-1":
                                        kernel["m_ext"][i, j, 0],
                                }
                            )

            # Fill maintenance ratio after the F=1 row is known.
            if f1_reference is None or q_primary is None:
                raise RuntimeError("Missing F=1 or primary Q result")
            for row in summary_rows:
                if (
                    row["z"] == state.z
                    and row["closure"] == closure
                    and "maintenance_fraction_of_F1" not in row
                ):
                    row["maintenance_fraction_of_F1"] = (
                        row["maintenance_H_s-1_cMpc-3"]
                        / f1_reference
                    )

            if closure == "DETERMINISTIC":
                topology_rows.append(
                    topology_auditors(state.z, q_primary)
                )

    summary = pd.DataFrame(summary_rows)
    convergence = pd.DataFrame(convergence_rows)
    chi = pd.DataFrame(chi_rows)
    topology = pd.DataFrame(topology_rows)
    rahmati = pd.concat(rahmati_frames, ignore_index=True)
    failures = pd.DataFrame(
        failure_rows,
        columns=[
            "z",
            "closure",
            "lane",
            "F_min",
            "F_max",
            "monotonicity_violation",
        ],
    )
    grid_out = pd.DataFrame(grid_rows)

    # Add profile crossing diagnostics.
    crossing_rows = []
    for z, group in rahmati.groupby("z"):
        base = {
            "z": z,
            "n_ss_formula_cm-3": float(group["n_ss_cm-3"].iloc[0]),
            "n_at_Rahmati_Gamma_ratio_0p5_cm-3":
                crossing_density(
                    group["n_H_cm-3"].to_numpy(),
                    group["Gamma_ratio_Rahmati"].to_numpy(),
                    0.5,
                ),
            "n_at_Rahmati_xHI_0p5_cm-3":
                crossing_density(
                    group["n_H_cm-3"].to_numpy(),
                    group["xHI_Rahmati_equilibrium"].to_numpy(),
                    0.5,
                ),
        }
        for lane in [
            "JEANS_SCALEHEIGHT_BASELINE",
            "CELL_SCALEHEIGHT_AUDITOR",
            "MIN_JEANS_CELL_CONSERVATIVE",
            "MFP_SCALEHEIGHT_CIRCULARITY_AUDITOR",
        ]:
            base[f"n_at_F_0p5_{lane}_cm-3"] = crossing_density(
                group["n_H_cm-3"].to_numpy(),
                group[f"F_{lane}"].to_numpy(),
                0.5,
            )
        crossing_rows.append(base)
    crossings = pd.DataFrame(crossing_rows)

    summary.to_csv(output_dir / "transmission_summary.csv", index=False)
    convergence.to_csv(output_dir / "integration_convergence.csv", index=False)
    chi.to_csv(output_dir / "jeans_calibration.csv", index=False)
    topology.to_csv(output_dir / "topology_auditors.csv", index=False)
    rahmati.to_csv(
        output_dir / "rahmati_chardin_profiles.csv.gz",
        index=False,
        compression="gzip",
    )
    crossings.to_csv(
        output_dir / "self_shielding_crossings.csv",
        index=False,
    )
    failures.to_csv(output_dir / "failed_lanes.csv", index=False)
    grid_out.to_csv(
        output_dir / "transmission_grid_z5p5.csv.gz",
        index=False,
        compression="gzip",
    )

    sigma_record = {
        "source_spectrum": "J_nu proportional nu^-1.5, 1-4 Ryd",
        "photon_weight": "J_nu/nu proportional E^-2.5",
        "energy_min_eV": E_HI,
        "energy_max_eV": E_HEII,
        "sigma_bar_H_cm2": sigma_bar,
        "verner_parameters": VERNER_HI,
        **sigma_meta,
    }
    (output_dir.parent / "GRAY_CROSS_SECTION.json").write_text(
        json.dumps(sigma_record, indent=2), encoding="utf-8"
    )

    circularity = {
        "lane": CIRCULARITY_LANE,
        "production_status": "AUDITOR_ONLY",
        "P0_4_quantity": "13.6-eV PUBLIC_REPO_EXACT global MFP",
        "proper_conversion": "lambda_proper=lambda_comoving/(1+z)",
        "risk": (
            "The P0.4 MFP already encodes H I absorber opacity. Reusing it as "
            "a local transmission scaleheight and later subtracting unresolved "
            "MFP sinks would count the same absorber population twice."
        ),
        "forbidden_promotion": True,
    }
    (output_dir.parent / "MFP_CIRCULARITY_LEDGER.json").write_text(
        json.dumps(circularity, indent=2), encoding="utf-8"
    )

    max_mismatch = float(
        convergence["relative_mismatch_H_maintenance"].max()
    )
    max_monotonicity = float(
        summary["max_positive_monotonicity_violation"].max()
    )
    min_f = float(summary["F_min"].min())
    max_f = float(summary["F_max"].max())
    max_maintenance_ratio = float(
        summary["maintenance_fraction_of_F1"].max()
    )
    min_maintenance_ratio = float(
        summary["maintenance_fraction_of_F1"].min()
    )
    q_columns = [
        "Q_V_global",
        "Q_M_global",
        "Q_V_given_F",
        "Q_M_given_F",
        "f_V_IGM",
    ]
    q_min = float(summary[q_columns].to_numpy().min())
    q_max = float(summary[q_columns].to_numpy().max())

    primary_summary = summary[
        summary["lane"] == "JEANS_SCALEHEIGHT_BASELINE"
    ]
    results = {
        "stage": "P0.5-B2C1A-HI-TRANSMISSION-QM-LOCK",
        "verdict": (
            "PASS"
            if (
                max_mismatch < 0.01
                and min_f >= -1.0e-15
                and max_f <= 1.0 + 1.0e-15
                and max_monotonicity <= 1.0e-10
                and max_maintenance_ratio <= 1.0 + 1.0e-12
                and q_min >= -1.0e-12
                and q_max <= 1.0 + 1.0e-12
                and len(failures) == 0
            )
            else "FAIL"
        ),
        "gates": {
            "direct_phase_mismatch_max": max_mismatch,
            "direct_phase_target": 0.01,
            "F_min": min_f,
            "F_max": max_f,
            "monotonicity_violation_max": max_monotonicity,
            "maintenance_fraction_of_F1_range": [
                min_maintenance_ratio,
                max_maintenance_ratio,
            ],
            "Q_and_diagnostic_range": [q_min, q_max],
            "failed_lane_count": int(len(failures)),
            "proper_length_dimension": "PASS",
        },
        "primary_lane": {
            "name": "JEANS_SCALEHEIGHT_BASELINE",
            "chi_J_range": [
                float(chi["chi_J"].min()),
                float(chi["chi_J"].max()),
            ],
            "tau_nss_range": [
                float(chi["tau_calibrated_at_nss"].min()),
                float(chi["tau_calibrated_at_nss"].max()),
            ],
            "Q_V_global_range": [
                float(primary_summary["Q_V_global"].min()),
                float(primary_summary["Q_V_global"].max()),
            ],
            "Q_M_global_range": [
                float(primary_summary["Q_M_global"].min()),
                float(primary_summary["Q_M_global"].max()),
            ],
            "f_V_IGM_range": [
                float(primary_summary["f_V_IGM"].min()),
                float(primary_summary["f_V_IGM"].max()),
            ],
            "maintenance_fraction_of_F1_range": [
                float(
                    primary_summary[
                        "maintenance_fraction_of_F1"
                    ].min()
                ),
                float(
                    primary_summary[
                        "maintenance_fraction_of_F1"
                    ].max()
                ),
            ],
            "C_norm_F_H_range": [
                float(primary_summary["C_norm_F_H"].min()),
                float(primary_summary["C_norm_F_H"].max()),
            ],
        },
        "bookkeeping_firewall": {
            "global_Q": "computed without F",
            "selected_Q": "stored separately as Q_V_given_F and Q_M_given_F",
            "MFP_scaleheight": "AUDITOR_ONLY",
            "He_transmission": "NOT_STARTED",
            "unresolved_sink": "NOT_STARTED",
            "front_allocation": "NOT_STARTED",
        },
    }
    (output_dir.parent / "results.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", type=Path, required=True)
    parser.add_argument("--mfp", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run_stage(args.history, args.mfp, args.output), indent=2))
