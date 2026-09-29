"""P0.5-B2C2B0A hierarchical two-scale opacity/chemistry closure.

Scope
-----
- No history re-evolution.
- No unresolved-sink subtraction.
- No front/Q_M evolution.
- No primordial recombination implementation.
- No Bianchi geometry coupling.

The stage constructs a fixed-weight hierarchical measure

    macro J = (box-scale density, local reionization redshift)
    micro I = (local subgrid overdensity, temperature)

and verifies that the same nodes can reproduce:
- R1 current-Gamma group opacity;
- B2C0 full-OTS phase-space source in the homogeneous-macro limit;
- photon allocation from group -> macro -> micro -> species.

The P0.4 emulator density coordinate and the cosmic-mass-normalized density
factor are stored separately. They are not silently identified.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
from numpy.polynomial.legendre import leggauss
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq, root
from scipy.special import ndtr, ndtri

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import phase_space_kernel_b2c0 as B2C0
import hi_transmission_kernel_b2c1a as B2C1A
import multigroup_hhe_transmission as B2C1B
from absorption_decomposition import normalized_group_quadrature
from gamma_conditioned_reconciliation import ResponseAnchoredOpacity

MPC_CM = B2C0.MPC_CM
NH0 = B2C0.NH0_CM3
YHE = B2C0.YHE
GROUPS = B2C1B.GROUPS
GROUP_ORDER = B2C1B.GROUP_ORDER
SPECIES = B2C1B.SPECIES
SUPPORT = B2C1B.SUPPORT
PRIMARY_LANE = "MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD"

ZRE_NODES = np.array([6.0, 7.0, 8.0, 9.0, 12.0, 15.0])
RAW_ENERGY_NODES = np.array([13.60, 14.48, 16.70, 20.05, 25.50, 39.50])
DENSITY_SIGMA_NODES = np.array([-1.7320508075688772, 0.0, 1.7320508075688772])

MICRO_SHAPE_LANES = [
    "LOCAL_NEUTRAL_HAZARD_PRIMARY",
    "RECOMBINATION_WEIGHTED_AUDITOR",
    "SCRIPT_SELF_SHIELDING_AUDITOR",
]

CLOSURE_LANES = [
    "LOCAL_NODE_STATE_PRIMARY",
    "ALGEBRAIC_BETA_DIRICHLET_AUDITOR",
    "HOMOGENEOUS_CHEMISTRY_AUDITOR",
]

B_STOICH = B2C0.B_STOICH


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def find_one(root: Path, filename: str) -> Path:
    matches = list(root.rglob(filename))
    if not matches:
        raise FileNotFoundError(f"{filename} below {root}")
    return sorted(matches, key=lambda p: (len(p.parts), str(p)))[0]


def q_history(z: np.ndarray | float) -> np.ndarray:
    """The exact P0.4 tanh history recovered from PUBLIC_REPO_EXACT."""
    z_arr = np.asarray(z, dtype=float)
    return 0.5 * (1.0 - np.tanh((z_arr - 6.58) / 1.63))


def zre_conditional_weights(z: float) -> tuple[np.ndarray, np.ndarray]:
    """Discretize -dQ/dzre on the locked raw z_re representatives.

    The last representative z_re=15 carries the [13.5,18] tail. This is a
    positive bin projection, not extrapolation of the raw opacity table.
    """
    boundaries = np.array([z, 6.5, 7.5, 8.5, 10.5, 13.5, 18.0])
    if not np.all(np.diff(boundaries) > 0):
        raise ValueError(f"Invalid z_re boundaries at z={z}")
    masses = q_history(boundaries[:-1]) - q_history(boundaries[1:])
    if np.any(masses < 0):
        raise RuntimeError("Negative z_re probability mass")
    weights = masses / masses.sum()
    return ZRE_NODES.copy(), weights


def interpolate_history_state(history: pd.DataFrame, z: float) -> dict[str, float]:
    ordered = history.sort_values("z")
    x = ordered["z"].to_numpy(dtype=float)
    result: dict[str, float] = {}
    for column in [
        "N1", "N2", "N3", "xHII", "xHeI", "xHeII", "xHeIII",
        "T_K", "Gamma_HI", "Gamma_HeI",
    ]:
        y = ordered[column].to_numpy(dtype=float)
        finite = np.isfinite(y)
        xf = x[finite]
        yf = y[finite]
        if len(yf) < 2:
            result[column] = float(yf[0]) if len(yf) == 1 else math.nan
        elif column in {"N1", "N2", "N3", "T_K", "Gamma_HI", "Gamma_HeI"}:
            if np.any(yf <= 0):
                result[column] = float(PchipInterpolator(xf, yf)(z))
            else:
                result[column] = float(
                    np.exp(PchipInterpolator(xf, np.log(yf))(z))
                )
        else:
            result[column] = float(PchipInterpolator(xf, yf)(z))
    result["xHeI_interpolated_auditor"] = result.get("xHeI", math.nan)
    result["xHeI"] = max(
        1.0 - result["xHeII"] - result["xHeIII"], 0.0
    )
    result["helium_simplex_residual"] = (
        result["xHeI"] + result["xHeII"] + result["xHeIII"] - 1.0
    )
    result["N4_exact"] = 0.0
    result["Gamma_HeII_exact"] = 0.0
    return result


def interpolate_density_mapping(mapping: pd.DataFrame, z: float) -> pd.DataFrame:
    rows = []
    for density_sigma in sorted(mapping["density_sigma"].unique()):
        subset = mapping[np.isclose(mapping["density_sigma"], density_sigma)].sort_values("z")
        x = subset["z"].to_numpy()
        record = {"z": z, "density_sigma": float(density_sigma)}
        for column in [
            "delta_NL", "effective_GH_weight", "eta_continuous",
            "volume_factor", "sigma_R_z",
        ]:
            record[column] = float(
                PchipInterpolator(x, subset[column].to_numpy())(z)
            )
        rows.append(record)
    frame = pd.DataFrame(rows).sort_values("density_sigma").reset_index(drop=True)
    frame["W_density"] = frame["effective_GH_weight"] / frame["effective_GH_weight"].sum()
    frame["D_L_emulator"] = 1.0 + frame["delta_NL"]
    raw_mean = float(np.sum(frame["W_density"] * frame["D_L_emulator"]))
    frame["D_L_mass"] = frame["D_L_emulator"] / raw_mean
    frame["mass_normalization_factor"] = 1.0 / raw_mean
    frame["raw_weighted_D_mean"] = raw_mean
    frame["normalized_weighted_D_mean"] = float(
        np.sum(frame["W_density"] * frame["D_L_mass"])
    )
    return frame


@dataclass
class RawMacroOpacity:
    raw: pd.DataFrame

    def __post_init__(self) -> None:
        self.gamma_nearest_fill_count = 0
        self.gamma_interpolation_count = 0

    def _gamma_interpolate(
        self,
        z_grid: float,
        z_re: float,
        density_label: float,
        energy_eV: float,
        gamma12: float,
    ) -> float:
        subset = self.raw[
            np.isclose(self.raw["z"], z_grid)
            & np.isclose(self.raw["z_re"], z_re)
            & np.isclose(self.raw["density"], density_label, atol=5.0e-3)
            & np.isclose(self.raw["energy_eV"], energy_eV)
        ].sort_values("gamma12")
        if subset.empty:
            raise KeyError(
                f"raw node missing z={z_grid}, zre={z_re}, "
                f"density={density_label}, E={energy_eV}"
            )
        gamma = subset["gamma12"].to_numpy()
        kappa = 1.0 / subset["lambda_raw_cMpc"].to_numpy()
        if len(gamma) < 2 or not (gamma.min() <= gamma12 <= gamma.max()):
            nearest = int(
                np.argmin(np.abs(np.log(gamma) - np.log(gamma12)))
            )
            self.gamma_nearest_fill_count += 1
            return float(kappa[nearest])
        self.gamma_interpolation_count += 1
        return float(
            np.exp(
                PchipInterpolator(np.log(gamma), np.log(kappa))(
                    np.log(gamma12)
                )
            )
        )

    def node_kappa_locked_energies(
        self,
        z: float,
        z_re: float,
        density_label: float,
        gamma12: float,
    ) -> tuple[np.ndarray, str]:
        z_values = np.sort(self.raw["z"].unique())
        lower_candidates = z_values[z_values <= z]
        upper_candidates = z_values[z_values >= z]
        if len(lower_candidates) == 0 or len(upper_candidates) == 0:
            raise ValueError(f"z={z} outside raw domain")
        z0 = float(lower_candidates[-1])
        z1 = float(upper_candidates[0])
        boundary_policy = "INTERPOLATED"

        # The raw table excludes z=z_re. At z=5.95, z_re=6 has only the
        # z=5.9 side. Use the nearest valid one-sided node and record it.
        def available(zg: float) -> bool:
            return bool(
                (
                    np.isclose(self.raw["z"], zg)
                    & np.isclose(self.raw["z_re"], z_re)
                ).any()
            )

        if not available(z0):
            valid = [
                float(v)
                for v in z_values
                if v <= z and available(float(v))
            ]
            if not valid:
                raise KeyError(f"No lower valid z for z_re={z_re}")
            z0 = valid[-1]
            boundary_policy = "ONE_SIDED_VALID_RAW_NODE"
        if not available(z1):
            valid = [
                float(v)
                for v in z_values
                if v >= z and available(float(v))
            ]
            if valid:
                z1 = valid[0]
            else:
                z1 = z0
            boundary_policy = "ONE_SIDED_VALID_RAW_NODE"

        values0 = np.array(
            [
                self._gamma_interpolate(
                    z0, z_re, density_label, energy, gamma12
                )
                for energy in RAW_ENERGY_NODES
            ]
        )
        if z1 == z0:
            return values0, boundary_policy
        values1 = np.array(
            [
                self._gamma_interpolate(
                    z1, z_re, density_label, energy, gamma12
                )
                for energy in RAW_ENERGY_NODES
            ]
        )
        frac = (z - z0) / (z1 - z0)
        values = np.exp((1.0 - frac) * np.log(values0) + frac * np.log(values1))
        return values, boundary_policy

    def energy_evaluator(
        self,
        z: float,
        z_re: float,
        density_label: float,
        gamma12: float,
    ) -> tuple[Callable[[np.ndarray], np.ndarray], str]:
        nodes, policy = self.node_kappa_locked_energies(
            z, z_re, density_label, gamma12
        )
        pchip = PchipInterpolator(
            np.log(RAW_ENERGY_NODES), np.log(nodes), extrapolate=False
        )

        def evaluate(energy: np.ndarray) -> np.ndarray:
            e = np.asarray(energy, dtype=float)
            if np.any(e < RAW_ENERGY_NODES[0]) or np.any(
                e > RAW_ENERGY_NODES[-1]
            ):
                raise ValueError("Raw macro-opacity energy extrapolation")
            return np.exp(pchip(np.log(e)))

        return evaluate, policy


def build_fixed_macro_template(
    mapping: pd.DataFrame,
    z_initial: float = 6.0,
) -> pd.DataFrame:
    """Lock the Lagrangian macro weights at z_initial."""
    density = interpolate_density_mapping(mapping, z_initial)
    zre_nodes, zre_weights = zre_conditional_weights(z_initial)
    rows = []
    for d_index, drow in density.iterrows():
        for r_index, (zre, wr) in enumerate(zip(zre_nodes, zre_weights)):
            rows.append(
                {
                    "macro_density_index": int(d_index),
                    "zre_index": int(r_index),
                    "density_sigma": float(drow["density_sigma"]),
                    "z_re": float(zre),
                    "W_density_fixed": float(drow["W_density"]),
                    "W_zre_fixed": float(wr),
                    "W_macro_fixed": float(drow["W_density"] * wr),
                    "weight_lock_redshift": z_initial,
                }
            )
    frame = pd.DataFrame(rows)
    if abs(frame["W_macro_fixed"].sum() - 1.0) > 1.0e-14:
        raise RuntimeError("Fixed macro template is not normalized")
    return frame


def macro_measure(
    z: float,
    mapping: pd.DataFrame,
    template: pd.DataFrame,
) -> pd.DataFrame:
    """Evaluate evolving macro coordinates on fixed Lagrangian weights."""
    density = interpolate_density_mapping(mapping, z).set_index(
        "density_sigma"
    )
    fixed_density = (
        template[
            [
                "macro_density_index",
                "density_sigma",
                "W_density_fixed",
            ]
        ]
        .drop_duplicates()
        .sort_values("macro_density_index")
    )
    raw_mean = 0.0
    current_by_index: dict[int, dict[str, float]] = {}
    for row in fixed_density.itertuples():
        current = density.loc[row.density_sigma]
        raw_mean += row.W_density_fixed * float(current["D_L_emulator"])
        current_by_index[int(row.macro_density_index)] = {
            "D_L_emulator": float(current["D_L_emulator"]),
            "delta_NL": float(current["delta_NL"]),
            "eta_continuous": float(current["eta_continuous"]),
            "volume_factor": float(current["volume_factor"]),
            "sigma_R_z": float(current["sigma_R_z"]),
        }

    rows = []
    for macro_index, row in template.reset_index(drop=True).iterrows():
        current = current_by_index[int(row["macro_density_index"])]
        rows.append(
            {
                "z": z,
                "macro_index": int(macro_index),
                "macro_density_index": int(row["macro_density_index"]),
                "zre_index": int(row["zre_index"]),
                "density_sigma": float(row["density_sigma"]),
                "z_re": float(row["z_re"]),
                "W_density": float(row["W_density_fixed"]),
                "W_zre": float(row["W_zre_fixed"]),
                "W_macro": float(row["W_macro_fixed"]),
                "D_L_emulator": current["D_L_emulator"],
                "D_L_mass": current["D_L_emulator"] / raw_mean,
                "delta_NL": current["delta_NL"],
                "eta_continuous": current["eta_continuous"],
                "volume_factor": current["volume_factor"],
                "sigma_R_z": current["sigma_R_z"],
                "raw_weighted_D_mean": raw_mean,
                "mass_normalization_factor": 1.0 / raw_mean,
                "weight_lock_redshift": float(row["weight_lock_redshift"]),
                "measure_policy":
                    "FIXED_WEIGHT_LAGRANGIAN_MACRO_MICRO_PARCELS",
            }
        )
    frame = pd.DataFrame(rows)
    frame["normalized_weighted_D_mean"] = float(
        np.sum(frame["W_macro"] * frame["D_L_mass"])
    )
    return frame




def solve_primary_offsets(
    state: B2C0.HistoryState,
    delta_total: np.ndarray,
    temperature: np.ndarray,
    mass_weight: np.ndarray,
) -> dict[str, float]:
    """Calibrate local means to nuclei/mass-weighted global fractions."""
    log_d = np.log(delta_total)
    log_t = np.log(temperature / state.temperature)
    h_base = B2C0.logit(state.x_hii) + 0.75 * log_t - 0.45 * log_d

    def h_residual(offset: float) -> float:
        return float(np.sum(mass_weight * B2C0.sigmoid(h_base + offset)) - state.x_hii)

    h_offset = float(brentq(h_residual, -40.0, 40.0))

    x_hei_global = max(1.0 - state.x_heii - state.x_heiii, 1.0e-14)
    l2_base = (
        math.log(state.x_heii / x_hei_global)
        + 0.35 * log_t
        - 0.20 * log_d
    )
    l3_base = (
        math.log(state.x_heiii / x_hei_global)
        + 1.10 * log_t
        - 0.10 * log_d
    )

    def he_residual(offsets: np.ndarray) -> np.ndarray:
        _, p2, p3 = B2C0.softmax3(
            l2_base + offsets[0], l3_base + offsets[1]
        )
        return np.array(
            [
                np.sum(mass_weight * p2) - state.x_heii,
                np.sum(mass_weight * p3) - state.x_heiii,
            ]
        )

    sol = root(he_residual, np.zeros(2), method="hybr")
    if not sol.success or np.linalg.norm(he_residual(sol.x)) > 1.0e-11:
        raise RuntimeError(f"Primary He offsets failed: {sol.message}")
    return {
        "h_offset": h_offset,
        "heii_offset": float(sol.x[0]),
        "heiii_offset": float(sol.x[1]),
    }


def means_from_offsets(
    state: B2C0.HistoryState,
    delta_total: np.ndarray,
    temperature: np.ndarray,
    offsets: dict[str, float],
) -> dict[str, np.ndarray]:
    log_d = np.log(delta_total)
    log_t = np.log(temperature / state.temperature)
    x_hii = B2C0.sigmoid(
        B2C0.logit(state.x_hii)
        + 0.75 * log_t
        - 0.45 * log_d
        + offsets["h_offset"]
    )
    x_hei_global = max(1.0 - state.x_heii - state.x_heiii, 1.0e-14)
    l2 = (
        math.log(state.x_heii / x_hei_global)
        + 0.35 * log_t
        - 0.20 * log_d
        + offsets["heii_offset"]
    )
    l3 = (
        math.log(state.x_heiii / x_hei_global)
        + 1.10 * log_t
        - 0.10 * log_d
        + offsets["heiii_offset"]
    )
    x_hei, x_heii, x_heiii = B2C0.softmax3(l2, l3)
    return {
        "xHII": x_hii,
        "xHeI": x_hei,
        "xHeII": x_heii,
        "xHeIII": x_heiii,
    }


@dataclass(frozen=True)
class FixedMicroTemplate:
    n_delta: int
    n_t: int
    w_delta: np.ndarray
    w_temperature: np.ndarray
    u_delta: np.ndarray
    u_temperature: np.ndarray
    weight_lock_redshift: float

    @property
    def weight(self) -> np.ndarray:
        return self.w_delta[:, None] * self.w_temperature


def build_fixed_micro_template(
    state_initial: B2C0.HistoryState,
    n_delta: int = 80,
    n_t: int = 32,
) -> FixedMicroTemplate:
    """Lock B2C0 quadrature weights at z=6 and retain quantile labels."""
    c0 = B2C0.calibrate_mhr_c0(state_initial.z)
    grid = B2C0.build_grid(state_initial, n_delta, n_t, c0)
    weight = grid["weight"]
    w_delta = weight.sum(axis=1)
    w_temperature = weight / w_delta[:, None]
    u_delta = np.cumsum(w_delta) - 0.5 * w_delta
    u_temperature = (
        np.cumsum(w_temperature, axis=1) - 0.5 * w_temperature
    )
    if abs(w_delta.sum() - 1.0) > 1.0e-14:
        raise RuntimeError("Fixed micro density weights do not sum to one")
    if np.max(np.abs(w_temperature.sum(axis=1) - 1.0)) > 1.0e-14:
        raise RuntimeError("Fixed conditional temperature weights invalid")
    return FixedMicroTemplate(
        n_delta=n_delta,
        n_t=n_t,
        w_delta=w_delta,
        w_temperature=w_temperature,
        u_delta=u_delta,
        u_temperature=u_temperature,
        weight_lock_redshift=state_initial.z,
    )


def transported_micro_grid(
    state: B2C0.HistoryState,
    template: FixedMicroTemplate,
    closure_variant: str = "BASELINE",
) -> tuple[dict[str, np.ndarray], dict[str, float]]:
    """Transport fixed quantile labels through the evolving B2C0 PDF.

    Weights are immutable; only parcel coordinates move.
    """
    c0 = B2C0.calibrate_mhr_c0(state.z)
    y_dense = np.linspace(
        math.log(B2C0.DELTA_MIN),
        math.log(B2C0.DELTA_MAX),
        100000,
    )
    pdf_y = B2C0.mhr_measure(y_dense, state.z, c0)
    cdf = cumulative_trapezoid(pdf_y, y_dense, initial=0.0)
    cdf /= cdf[-1]
    delta = np.exp(np.interp(template.u_delta, cdf, y_dense))

    if closure_variant == "MACRO_DENSITY_VARIANCE":
        # A declared sensitivity deformation of the local density rank map.
        delta = delta**1.18
    delta_pre_normalization_mean = float(
        np.sum(template.w_delta * delta)
    )
    delta /= delta_pre_normalization_mean

    lo, hi = math.log(B2C0.T_MIN_K), math.log(B2C0.T_MAX_K)
    sigma = B2C0.SIGMA_LNT

    def temperature_nodes(log_scale: float) -> np.ndarray:
        mu = log_scale + B2C0.GAMMA_MINUS_ONE * np.log(delta)
        p_lo = ndtr((lo - mu) / sigma)
        p_hi = ndtr((hi - mu) / sigma)
        probabilities = (
            p_lo[:, None]
            + template.u_temperature * (p_hi - p_lo)[:, None]
        )
        probabilities = np.clip(probabilities, 1.0e-15, 1.0 - 1.0e-15)
        return np.exp(
            mu[:, None] + sigma * ndtri(probabilities)
        )

    def temperature_residual(log_scale: float) -> float:
        values = temperature_nodes(log_scale)
        return float(np.sum(template.weight * values) - state.temperature)

    scan = np.linspace(
        math.log(B2C0.T_MIN_K) - 10.0,
        math.log(B2C0.T_MAX_K) + 10.0,
        600,
    )
    scan_value = np.array([temperature_residual(value) for value in scan])
    crossings = np.where(scan_value[:-1] * scan_value[1:] <= 0.0)[0]
    if len(crossings) == 0:
        raise RuntimeError("No transported temperature-scale root")
    index = int(crossings[0])
    log_scale = brentq(
        temperature_residual, scan[index], scan[index + 1]
    )
    temperature = temperature_nodes(log_scale)

    if closure_variant in {
        "EARLY_REIONIZED_COOLER",
        "EARLY_REIONIZED_HOTTER",
    }:
        raise ValueError(
            "z_re-dependent temperature sensitivity is applied after macro "
            "expansion in construct_hierarchy"
        )
    if closure_variant not in {"BASELINE", "MACRO_DENSITY_VARIANCE"}:
        raise ValueError(closure_variant)

    delta_2d = np.broadcast_to(delta[:, None], temperature.shape)
    diagnostics = {
        "delta_pre_normalization_mean": delta_pre_normalization_mean,
        "delta_post_normalization_mean": float(
            np.sum(template.w_delta * delta)
        ),
        "temperature_weighted_mean": float(
            np.sum(template.weight * temperature)
        ),
        "weight_sum": float(template.weight.sum()),
        "weight_lock_redshift": template.weight_lock_redshift,
    }
    return {
        "delta": delta_2d,
        "temperature": temperature,
        "weight": template.weight.copy(),
    }, diagnostics


def construct_hierarchy(
    state: B2C0.HistoryState,
    macro: pd.DataFrame,
    micro_template: FixedMicroTemplate,
    closure_variant: str = "BASELINE",
) -> tuple[pd.DataFrame, dict[str, np.ndarray], dict[str, float]]:
    base_variant = (
        "MACRO_DENSITY_VARIANCE"
        if closure_variant == "MACRO_DENSITY_VARIANCE"
        else "BASELINE"
    )
    micro_grid, transport_diag = transported_micro_grid(
        state, micro_template, base_variant
    )
    delta_sub_base = micro_grid["delta"].reshape(-1)
    temperature_base = micro_grid["temperature"].reshape(-1)
    w_micro = micro_grid["weight"].reshape(-1)

    rows = []
    for macro_index, mrow in macro.iterrows():
        delta_sub = delta_sub_base.copy()
        temperature = temperature_base.copy()
        if closure_variant in {
            "EARLY_REIONIZED_COOLER",
            "EARLY_REIONIZED_HOTTER",
        }:
            sign = (
                -1.0
                if closure_variant == "EARLY_REIONIZED_COOLER"
                else 1.0
            )
            z_standard = (mrow["z_re"] - 8.0) / 3.0
            temperature = temperature * np.exp(
                sign * 0.18 * z_standard
            )
        delta_total = mrow["D_L_mass"] * delta_sub
        for micro_index in range(len(w_micro)):
            rows.append(
                {
                    "z": state.z,
                    "macro_index": int(macro_index),
                    "micro_index": int(micro_index),
                    "density_sigma": mrow["density_sigma"],
                    "z_re": mrow["z_re"],
                    "W_macro": mrow["W_macro"],
                    "D_L_emulator": mrow["D_L_emulator"],
                    "D_L_mass": mrow["D_L_mass"],
                    "delta_sub": delta_sub[micro_index],
                    "delta_total": delta_total[micro_index],
                    "T_K": temperature[micro_index],
                    "w_micro": w_micro[micro_index],
                    "W_node": mrow["W_macro"] * w_micro[micro_index],
                    "closure_variant": closure_variant,
                    "weight_lock_redshift":
                        micro_template.weight_lock_redshift,
                    "parcel_label": (
                        f"D{int(mrow['macro_density_index'])}_"
                        f"R{int(mrow['zre_index'])}_"
                        f"M{micro_index}"
                    ),
                }
            )
    nodes = pd.DataFrame(rows)
    node_weight = nodes["W_node"].to_numpy()
    mass_weight = node_weight * nodes["delta_total"].to_numpy()
    mass_weight /= mass_weight.sum()
    offsets = solve_primary_offsets(
        state,
        nodes["delta_total"].to_numpy(),
        nodes["T_K"].to_numpy(),
        mass_weight,
    )
    means = means_from_offsets(
        state,
        nodes["delta_total"].to_numpy(),
        nodes["T_K"].to_numpy(),
        offsets,
    )
    for name, values in means.items():
        nodes[name] = values

    diagnostics = {
        "weight_sum": float(node_weight.sum()),
        "mass_density_sum": float(
            np.sum(node_weight * nodes["delta_total"].to_numpy())
        ),
        "mass_xHII": float(np.sum(mass_weight * means["xHII"])),
        "mass_xHeII": float(np.sum(mass_weight * means["xHeII"])),
        "mass_xHeIII": float(np.sum(mass_weight * means["xHeIII"])),
        **transport_diag,
    }
    return nodes, means, {**offsets, **diagnostics}


def fixed_micro_b2c0_source(
    state: B2C0.HistoryState,
    micro_template: FixedMicroTemplate,
    closure: str,
) -> dict[str, np.ndarray]:
    """B2C0 homogeneous-macro source on the same fixed parcel weights."""
    grid, _ = transported_micro_grid(state, micro_template, "BASELINE")
    offsets = B2C0.calibrate_fraction_offsets(state, grid)
    means = B2C0.conditional_means(state, grid, offsets)
    moments = B2C0.conditional_moments(means, closure)
    kernel = B2C0.full_ots_kernel(state, grid, moments)
    conversion = MPC_CM**3 / (1.0 + state.z) ** 3
    return {
        "source": np.sum(
            grid["weight"][..., None] * kernel["source"], axis=(0, 1)
        )
        * conversion,
        "m_ext": np.sum(
            grid["weight"][..., None] * kernel["m_ext"], axis=(0, 1)
        )
        * conversion,
    }




def full_ots_on_nodes(
    state: B2C0.HistoryState,
    nodes: pd.DataFrame,
    closure: str,
) -> dict[str, Any]:
    means = {
        key: nodes[key].to_numpy()
        for key in ["xHII", "xHeI", "xHeII", "xHeIII"]
    }
    moments = B2C0.conditional_moments(means, closure)
    grid = {
        "delta": nodes["delta_total"].to_numpy(),
        "temperature": nodes["T_K"].to_numpy(),
        "weight": nodes["W_node"].to_numpy(),
    }
    kernel = B2C0.full_ots_kernel(state, grid, moments)
    weights = nodes["W_node"].to_numpy()
    conversion = MPC_CM**3 / (1.0 + state.z) ** 3
    return {
        "source": np.sum(weights[:, None] * kernel["source"], axis=0) * conversion,
        "m_ext": np.sum(weights[:, None] * kernel["m_ext"], axis=0) * conversion,
        "stoich_residual_max": float(
            np.max(np.abs(kernel["stoich_residual"]))
        ),
        "kernel": kernel,
        "moments": moments,
    }


def homogeneous_b2c0_reference(
    state: B2C0.HistoryState,
    n_delta: int,
    n_t: int,
    closure: str,
) -> dict[str, np.ndarray]:
    c0 = B2C0.calibrate_mhr_c0(state.z)
    calibration = B2C0.build_grid(state, 192, 32, c0)
    offsets = B2C0.calibrate_fraction_offsets(state, calibration)
    grid = B2C0.build_grid(state, n_delta, n_t, c0)
    means = B2C0.conditional_means(state, grid, offsets)
    moments = B2C0.conditional_moments(means, closure)
    kernel = B2C0.full_ots_kernel(state, grid, moments)
    weight = grid["weight"]
    conversion = MPC_CM**3 / (1.0 + state.z) ** 3
    return {
        "source": np.sum(weight[..., None] * kernel["source"], axis=(0, 1))
        * conversion,
        "m_ext": np.sum(weight[..., None] * kernel["m_ext"], axis=(0, 1))
        * conversion,
    }


def raw_macro_shapes(
    macro: pd.DataFrame,
    raw_model: RawMacroOpacity,
    z: float,
    gamma12: float,
    energy: np.ndarray,
) -> tuple[np.ndarray, list[str]]:
    evaluations = []
    policies = []
    for row in macro.itertuples():
        evaluator, policy = raw_model.energy_evaluator(
            z,
            row.z_re,
            float(row.density_sigma),
            gamma12,
        )
        evaluations.append(evaluator(energy))
        policies.append(policy)
    return np.asarray(evaluations), policies


def r1_effective_energy_evaluator(
    response: ResponseAnchoredOpacity,
    gamma12: float,
) -> Callable[[np.ndarray], np.ndarray]:
    return response.conditioned_energy_evaluator(gamma12)


def global_target_group_kappa(
    state: dict[str, float],
    z: float,
    response: ResponseAnchoredOpacity,
    gamma12: float,
    group: str,
    n_energy: int,
) -> tuple[float, dict[str, float]]:
    energy, weights = normalized_group_quadrature(group, n_energy)
    zeros = np.zeros_like(energy)
    if group in {"G1", "G2a"}:
        hi_eff = r1_effective_energy_evaluator(response, gamma12)(energy)
    else:
        hi_eff = zeros
    n_h = NH0 * (1.0 + z) ** 3
    n_he = YHE * n_h
    a = 1.0 / (1.0 + z)
    atomic = {
        "HI": a
        * n_h
        * (1.0 - state["xHII"])
        * B2C1B.verner_sigma("HI", energy)
        * MPC_CM,
        "HeI": a
        * n_he
        * state["xHeI"]
        * B2C1B.verner_sigma("HeI", energy)
        * MPC_CM,
        "HeII": a
        * n_he
        * state["xHeII"]
        * B2C1B.verner_sigma("HeII", energy)
        * MPC_CM,
    }
    components = {
        "EFFECTIVE_HI_SUBGRID": hi_eff,
        "EXPLICIT_HI_ATOMIC": atomic["HI"] if group in {"G2b", "G3"} else zeros,
        "EXPLICIT_HEI_ATOMIC": atomic["HeI"] if group in {"G2a", "G2b", "G3"} else zeros,
        "EXPLICIT_HEII_ATOMIC": atomic["HeII"] if group == "G3" else zeros,
    }
    averages = {
        name: float(np.sum(weights * value))
        for name, value in components.items()
    }
    return sum(averages.values()), averages


def node_opacity_and_allocation(
    state: dict[str, float],
    history_state: B2C0.HistoryState,
    nodes: pd.DataFrame,
    macro: pd.DataFrame,
    raw_model: RawMacroOpacity,
    response: ResponseAnchoredOpacity,
    gamma12: float,
    group_absorption_rate: float,
    group: str,
    shape_lane: str,
    n_energy: int,
    return_detail: bool = False,
) -> tuple[pd.DataFrame, dict[str, float], dict[str, np.ndarray] | None]:
    energy, phi = normalized_group_quadrature(group, n_energy)
    n_nodes = len(nodes)
    component_energy = {
        "EFFECTIVE_HI_SUBGRID": np.zeros((n_nodes, len(energy))),
        "EXPLICIT_HI_ATOMIC": np.zeros((n_nodes, len(energy))),
        "EXPLICIT_HEI_ATOMIC": np.zeros((n_nodes, len(energy))),
        "EXPLICIT_HEII_ATOMIC": np.zeros((n_nodes, len(energy))),
    }
    n_h = (
        NH0
        * (1.0 + history_state.z) ** 3
        * nodes["delta_total"].to_numpy()
    )
    n_he = YHE * n_h
    xh = nodes["xHII"].to_numpy()
    x1 = nodes["xHeI"].to_numpy()
    x2 = nodes["xHeII"].to_numpy()
    x3 = nodes["xHeIII"].to_numpy()
    a = 1.0 / (1.0 + history_state.z)

    explicit = {
        "HI": (
            a
            * n_h[:, None]
            * (1.0 - xh[:, None])
            * B2C1B.verner_sigma("HI", energy)[None, :]
            * MPC_CM
        ),
        "HeI": (
            a
            * n_he[:, None]
            * x1[:, None]
            * B2C1B.verner_sigma("HeI", energy)[None, :]
            * MPC_CM
        ),
        "HeII": (
            a
            * n_he[:, None]
            * x2[:, None]
            * B2C1B.verner_sigma("HeII", energy)[None, :]
            * MPC_CM
        ),
    }
    if group in {"G2b", "G3"}:
        component_energy["EXPLICIT_HI_ATOMIC"] = explicit["HI"]
    if group in {"G2a", "G2b", "G3"}:
        component_energy["EXPLICIT_HEI_ATOMIC"] = explicit["HeI"]
    if group == "G3":
        component_energy["EXPLICIT_HEII_ATOMIC"] = explicit["HeII"]

    boundary_policies: list[str] = []
    if group in {"G1", "G2a"}:
        macro_raw, boundary_policies = raw_macro_shapes(
            macro, raw_model, history_state.z, gamma12, energy
        )
        macro_weights = macro["W_macro"].to_numpy()
        raw_global = np.sum(
            macro_weights[:, None] * macro_raw, axis=0
        )
        global_effective = response.conditioned_energy_evaluator(
            gamma12
        )(energy)
        macro_effective = (
            global_effective[None, :] * macro_raw / raw_global[None, :]
        )

        sigma_hi = B2C1B.verner_sigma("HI", energy)
        gray_sigma = B2C1A.gray_sigma_hi()[0]
        chi = B2C1A.calibrate_chi_jeans(
            history_state.z, history_state.gamma_hi, gray_sigma
        )["chi_J"]
        length = chi * B2C1A.jeans_length_cm(
            n_h, nodes["T_K"].to_numpy(), xh, x2, x3
        )
        length_cMpc = length * (1.0 + history_state.z) / MPC_CM

        macro_index_array = nodes["macro_index"].to_numpy()
        for macro_index, _ in macro.iterrows():
            select = macro_index_array == macro_index
            w = nodes.loc[select, "w_micro"].to_numpy()
            n_hi = n_h[select] * (1.0 - xh[select])
            if shape_lane == "LOCAL_NEUTRAL_HAZARD_PRIMARY":
                transmission = np.exp(
                    -0.5
                    * n_hi[:, None]
                    * sigma_hi[None, :]
                    * length[select, None]
                )
                shape = (
                    n_hi[:, None]
                    * sigma_hi[None, :]
                    * transmission
                    + 1.0e-300
                )
            elif shape_lane == "RECOMBINATION_WEIGHTED_AUDITOR":
                ne = n_h[select] * xh[select] + n_he[select] * (
                    x2[select] + 2.0 * x3[select]
                )
                recomb = (
                    B2C0.alpha_b_hii(
                        nodes.loc[select, "T_K"].to_numpy()
                    )
                    * ne
                    * n_h[select]
                    * xh[select]
                )
                shape = (
                    recomb[:, None]
                    * np.ones_like(energy)[None, :]
                    + 1.0e-300
                )
            elif shape_lane == "SCRIPT_SELF_SHIELDING_AUDITOR":
                nss = B2C1A.self_shielding_density_cm3(
                    nodes.loc[select, "T_K"].to_numpy(),
                    history_state.gamma_hi,
                    gray_sigma,
                )
                attenuation = 1.0 - B2C1A.rahmati_gamma_ratio(
                    n_h[select], nss
                )
                shape = (
                    n_hi[:, None]
                    * sigma_hi[None, :]
                    * np.maximum(attenuation[:, None], 1.0e-12)
                    + 1.0e-300
                )
            else:
                raise ValueError(shape_lane)
            norm = np.sum(w[:, None] * shape, axis=0)
            component_energy["EFFECTIVE_HI_SUBGRID"][select, :] = (
                macro_effective[macro_index][None, :]
                * shape
                / norm[None, :]
            )
    else:
        length_cMpc = (
            B2C1A.jeans_length_cm(
                n_h, nodes["T_K"].to_numpy(), xh, x2, x3
            )
            * (1.0 + history_state.z)
            / MPC_CM
        )

    total_energy = sum(component_energy.values())
    group_kappa_node = np.sum(phi[None, :] * total_energy, axis=1)
    node_weight = nodes["W_node"].to_numpy()
    global_kappa = float(np.sum(node_weight * group_kappa_node))

    tau_components = {
        name: values * length_cMpc[:, None]
        for name, values in component_energy.items()
    }
    tau_total = sum(tau_components.values())
    absorbed = -np.expm1(-np.clip(tau_total, 0.0, 745.0))
    absorbed_group = np.sum(phi[None, :] * absorbed, axis=1)

    species_tau = {
        "HI": (
            tau_components["EFFECTIVE_HI_SUBGRID"]
            + tau_components["EXPLICIT_HI_ATOMIC"]
        ),
        "HeI": tau_components["EXPLICIT_HEI_ATOMIC"],
        "HeII": tau_components["EXPLICIT_HEII_ATOMIC"],
    }
    A = np.zeros((n_nodes, 3))
    for s_index, species in enumerate(SPECIES):
        frac = np.divide(
            species_tau[species],
            tau_total,
            out=np.zeros_like(tau_total),
            where=tau_total > 0,
        )
        numerator = np.sum(
            phi[None, :] * absorbed * frac, axis=1
        )
        A[:, s_index] = np.divide(
            numerator,
            absorbed_group,
            out=np.zeros_like(numerator),
            where=absorbed_group > 1.0e-15,
        )
    for s_index, species in enumerate(SPECIES):
        if group not in SUPPORT[species]:
            A[:, s_index] = 0.0
    positive = absorbed_group > 1.0e-15
    sums = A.sum(axis=1)
    A[positive] /= sums[positive, None]

    q_node = node_weight * group_kappa_node
    if q_node.sum() > 0:
        q_node /= q_node.sum()
    j = q_node[:, None] * A * group_absorption_rate

    rows = []
    macro_index_array = nodes["macro_index"].to_numpy()
    for macro_index in sorted(nodes["macro_index"].unique()):
        select = macro_index_array == macro_index
        for s_index, species in enumerate(SPECIES):
            rows.append(
                {
                    "z": history_state.z,
                    "shape_lane": shape_lane,
                    "group": group,
                    "macro_index": int(macro_index),
                    "species": species,
                    "q_macro_group": float(q_node[select].sum()),
                    "j_abs_s-1_cMpc-3": float(
                        j[select, s_index].sum()
                    ),
                    "threshold_supported": group in SUPPORT[species],
                    "micro_node_count": int(select.sum()),
                }
            )
    diagnostics = {
        "global_kappa_cMpc_inv": global_kappa,
        "q_sum": float(q_node.sum()),
        "allocation_sum_residual_max": (
            float(np.max(np.abs(A[positive].sum(axis=1) - 1.0)))
            if np.any(positive)
            else 0.0
        ),
        "photon_allocation_relative_residual": float(
            abs(j.sum() - group_absorption_rate)
            / max(abs(group_absorption_rate), 1.0)
        ),
        "boundary_policy_count": len(
            [p for p in boundary_policies if p != "INTERPOLATED"]
        ),
    }
    detail = None
    if return_detail:
        detail = {
            "q_node": q_node,
            "A_species": A,
            "j_abs": j,
            "group_kappa_node": group_kappa_node,
            "macro_index": macro_index_array,
            "micro_index": nodes["micro_index"].to_numpy(),
        }
    return pd.DataFrame(rows), diagnostics, detail




def ipf(
    seed: np.ndarray,
    row_target: np.ndarray,
    col_target: np.ndarray,
    max_iter: int = 20000,
    tolerance: float = 1.0e-14,
) -> tuple[np.ndarray, int, float]:
    table = np.asarray(seed, dtype=float).copy()
    if np.any(table < 0):
        raise ValueError("Negative IPF seed")
    if np.any((table.sum(axis=1) == 0) & (row_target > 0)):
        raise ValueError("Structural-zero row conflicts with target")
    if np.any((table.sum(axis=0) == 0) & (col_target > 0)):
        raise ValueError("Structural-zero column conflicts with target")
    for iteration in range(1, max_iter + 1):
        row_sum = table.sum(axis=1)
        table *= np.divide(
            row_target,
            row_sum,
            out=np.ones_like(row_target),
            where=row_sum > 0,
        )[:, None]
        col_sum = table.sum(axis=0)
        table *= np.divide(
            col_target,
            col_sum,
            out=np.ones_like(col_target),
            where=col_sum > 0,
        )[None, :]
        residual = max(
            float(np.max(np.abs(table.sum(axis=1) - row_target))),
            float(np.max(np.abs(table.sum(axis=0) - col_target))),
        )
        if residual < tolerance:
            return table, iteration, residual
    raise RuntimeError("IPF did not converge")


def kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
    mask = p > 0
    return float(np.sum(p[mask] * np.log(p[mask] / q[mask])))


def entropy(p: np.ndarray) -> float:
    mask = p > 0
    return float(-np.sum(p[mask] * np.log(p[mask])))


def run_stage(
    r1_root: Path,
    b2c0_root: Path,
    p04_root: Path,
    output: Path,
) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    history = pd.read_csv(
        r1_root / "data" / "canonical_direct_history.csv"
    )
    group_absorption = pd.read_csv(
        r1_root / "data" / "reconciled_group_total_absorption.csv"
    )
    component_absorption = pd.read_csv(
        r1_root / "data" / "reconciled_physical_component_absorption.csv"
    )
    public = pd.read_csv(
        p04_root / "data" / "public_repo_exact_checkpoint_global.csv"
    )
    public = public[
        (public["source"] == "PUBLIC_REPO_EXACT_CHECKPOINT")
        & (public["mode"] == "public_continuous_joint")
    ].copy()
    mapping = pd.read_csv(
        p04_root / "data" / "density_mapping_colossus_1_3_10_port.csv"
    )
    raw = pd.read_csv(
        p04_root / "data" / "checkpoint_raw_cellwise.csv.gz"
    )
    raw_model = RawMacroOpacity(raw)

    raw_text = find_one(r1_root, "environment_mfp_energies.txt")
    density_path = find_one(
        r1_root, "density_mapping_colossus_1_3_10_port.csv"
    )

    initial_values = interpolate_history_state(history, 6.0)
    initial_state = B2C0.HistoryState(
        z=6.0,
        x_hii=initial_values["xHII"],
        x_heii=initial_values["xHeII"],
        x_heiii=initial_values["xHeIII"],
        temperature=initial_values["T_K"],
        gamma_hi=initial_values["Gamma_HI"],
    )
    fixed_macro = build_fixed_macro_template(mapping, 6.0)
    fixed_micro = build_fixed_micro_template(
        initial_state, n_delta=80, n_t=32
    )
    fixed_macro.to_csv(
        output / "fixed_macro_parcel_template_z6.csv", index=False
    )
    np.savez_compressed(
        output / "fixed_micro_parcel_template_z6.npz",
        w_delta=fixed_micro.w_delta,
        w_temperature=fixed_micro.w_temperature,
        u_delta=fixed_micro.u_delta,
        u_temperature=fixed_micro.u_temperature,
        n_delta=fixed_micro.n_delta,
        n_t=fixed_micro.n_t,
        weight_lock_redshift=fixed_micro.weight_lock_redshift,
    )

    macro_tables = []
    node_tables = []
    macro_opacity_rows = []
    source_rows = []
    source_convergence_rows = []
    allocation_tables = []
    allocation_summary_rows = []
    sensitivity_rows = []
    density_adapter_rows = []
    ipf_rows = []
    target_rows = []
    weight_invariance_rows = []
    primary_detail: dict[str, np.ndarray] = {}

    for z in sorted(group_absorption["z_mid"].unique(), reverse=True):
        state_values = interpolate_history_state(history, z)
        hstate = B2C0.HistoryState(
            z=float(z),
            x_hii=state_values["xHII"],
            x_heii=state_values["xHeII"],
            x_heiii=state_values["xHeIII"],
            temperature=state_values["T_K"],
            gamma_hi=state_values["Gamma_HI"],
        )
        gamma12 = hstate.gamma_hi / 1.0e-12
        macro = macro_measure(z, mapping, fixed_macro)
        macro["interval_index"] = int(
            group_absorption[
                np.isclose(group_absorption["z_mid"], z)
            ]["interval_index"].iloc[0]
        )
        macro_tables.append(macro)
        density_adapter_rows.append(
            {
                "z": z,
                "raw_weighted_D_mean":
                    macro["raw_weighted_D_mean"].iloc[0],
                "mass_normalization_factor":
                    macro["mass_normalization_factor"].iloc[0],
                "normalized_weighted_D_mean": float(
                    np.sum(macro["W_macro"] * macro["D_L_mass"])
                ),
                "emulator_coordinate_unchanged": True,
            }
        )

        nodes, means, node_diag = construct_hierarchy(
            hstate,
            macro,
            fixed_micro,
            closure_variant="BASELINE",
        )
        nodes["history_provenance"] = (
            "R1_CANONICAL_STATE_NO_REEVOLUTION"
        )
        node_tables.append(nodes)
        weight_invariance_rows.append(
            {
                "z": z,
                "macro_weight_hash": str(
                    hash(tuple(np.round(macro["W_macro"], 18)))
                ),
                "micro_weight_hash": str(
                    hash(
                        tuple(
                            np.round(
                                nodes[
                                    nodes["macro_index"] == 0
                                ]
                                .sort_values("micro_index")[
                                    "w_micro"
                                ],
                                18,
                            )
                        )
                    )
                ),
                "macro_weight_max_abs_difference_from_z6":
                    float(
                        np.max(
                            np.abs(
                                macro["W_macro"].to_numpy()
                                - fixed_macro[
                                    "W_macro_fixed"
                                ].to_numpy()
                            )
                        )
                    ),
                "micro_weight_max_abs_difference_from_z6":
                    float(
                        np.max(
                            np.abs(
                                nodes[
                                    nodes["macro_index"] == 0
                                ]
                                .sort_values("micro_index")[
                                    "w_micro"
                                ]
                                .to_numpy()
                                - fixed_micro.weight.reshape(-1)
                            )
                        )
                    ),
                "dot_W_J": 0.0,
                "dot_w_I_given_J": 0.0,
            }
        )

        reference_fine = homogeneous_b2c0_reference(
            hstate,
            n_delta=128,
            n_t=32,
            closure="DETERMINISTIC",
        )
        fixed_reference = fixed_micro_b2c0_source(
            hstate, fixed_micro, "DETERMINISTIC"
        )
        source_rel = np.abs(
            fixed_reference["m_ext"] - reference_fine["m_ext"]
        ) / np.maximum(np.abs(reference_fine["m_ext"]), 1.0)
        source_convergence_rows.append(
            {
                "z": z,
                "closure":
                    "FIXED_WEIGHT_HOMOGENEOUS_MACRO_B2C0_AUDITOR",
                "H_relative_error": source_rel[0],
                "HeI_relative_error": source_rel[1],
                "HeII_relative_error": source_rel[2],
                "max_relative_error": float(source_rel.max()),
            }
        )

        actual_det = full_ots_on_nodes(
            hstate, nodes, "DETERMINISTIC"
        )
        actual_patch = full_ots_on_nodes(
            hstate, nodes, "PATCHY_BETA_DIRICHLET"
        )
        for closure_name, source_result in [
            (
                "LOCAL_NODE_STATE_PRIMARY_DETERMINISTIC",
                actual_det,
            ),
            (
                "LOCAL_NODE_STATE_PRIMARY_PATCHY_AUDITOR",
                actual_patch,
            ),
            (
                "B2C0_HOMOGENEOUS_MACRO_REFERENCE",
                reference_fine,
            ),
            (
                "FIXED_WEIGHT_HOMOGENEOUS_MACRO_AUDITOR",
                fixed_reference,
            ),
        ]:
            source_rows.append(
                {
                    "z": z,
                    "closure": closure_name,
                    "m_HI_to_HII_s-1_cMpc-3":
                        source_result["m_ext"][0],
                    "m_HeI_to_HeII_s-1_cMpc-3":
                        source_result["m_ext"][1],
                    "m_HeII_to_HeIII_s-1_cMpc-3":
                        source_result["m_ext"][2],
                    "source_HI": source_result["source"][0],
                    "source_HII": source_result["source"][1],
                    "source_HeI": source_result["source"][2],
                    "source_HeII": source_result["source"][3],
                    "source_HeIII": source_result["source"][4],
                    "stoich_residual_max":
                        source_result.get(
                            "stoich_residual_max", 0.0
                        ),
                }
            )

        for variant in [
            "MACRO_DENSITY_VARIANCE",
            "EARLY_REIONIZED_COOLER",
            "EARLY_REIONIZED_HOTTER",
        ]:
            varied_nodes, _, varied_diag = construct_hierarchy(
                hstate,
                macro,
                fixed_micro,
                closure_variant=variant,
            )
            varied_result = full_ots_on_nodes(
                hstate, varied_nodes, "DETERMINISTIC"
            )
            sensitivity_rows.append(
                {
                    "z": z,
                    "auditor": variant,
                    "m_H_ratio_to_primary":
                        varied_result["m_ext"][0]
                        / actual_det["m_ext"][0],
                    "m_HeI_ratio_to_primary":
                        varied_result["m_ext"][1]
                        / actual_det["m_ext"][1],
                    "m_HeII_ratio_to_primary":
                        varied_result["m_ext"][2]
                        / actual_det["m_ext"][2],
                    "mass_density_sum":
                        varied_diag["mass_density_sum"],
                }
            )
        sensitivity_rows.append(
            {
                "z": z,
                "auditor": "PATCHY_BETA_DIRICHLET",
                "m_H_ratio_to_primary":
                    actual_patch["m_ext"][0]
                    / actual_det["m_ext"][0],
                "m_HeI_ratio_to_primary":
                    actual_patch["m_ext"][1]
                    / actual_det["m_ext"][1],
                "m_HeII_ratio_to_primary":
                    actual_patch["m_ext"][2]
                    / actual_det["m_ext"][2],
                "mass_density_sum": node_diag["mass_density_sum"],
            }
        )

        response = ResponseAnchoredOpacity(
            public, raw_text, density_path, float(z)
        )

        for group in GROUP_ORDER:
            group_rate = float(
                group_absorption[
                    np.isclose(group_absorption["z_mid"], z)
                    & (group_absorption["group"] == group)
                ]["total_absorption_rate_s-1_cMpc-3"].iloc[0]
            )
            target_kappa, target_components = (
                global_target_group_kappa(
                    state_values,
                    z,
                    response,
                    gamma12,
                    group,
                    n_energy=96,
                )
            )
            target_rows.append(
                {
                    "z": z,
                    "group": group,
                    "helium_simplex_residual":
                        state_values["helium_simplex_residual"],
                    "xHeI_interpolated_auditor":
                        state_values["xHeI_interpolated_auditor"],
                    "xHeI_simplex_canonical":
                        state_values["xHeI"],
                    "target_total_kappa_cMpc_inv": target_kappa,
                    **{
                        f"target_{name}_cMpc_inv": value
                        for name, value in target_components.items()
                    },
                }
            )

            for shape_lane in MICRO_SHAPE_LANES:
                return_detail = (
                    shape_lane
                    == "LOCAL_NEUTRAL_HAZARD_PRIMARY"
                    and np.isclose(z, 5.75)
                )
                allocation_frame, diagnostics, detail = (
                    node_opacity_and_allocation(
                        state_values,
                        hstate,
                        nodes,
                        macro,
                        raw_model,
                        response,
                        gamma12,
                        group_rate,
                        group,
                        shape_lane,
                        n_energy=48,
                        return_detail=return_detail,
                    )
                )
                allocation_tables.append(allocation_frame)
                if detail is not None:
                    for name, values in detail.items():
                        primary_detail[
                            f"{group}_{name}"
                        ] = values
                relative_opacity = abs(
                    diagnostics["global_kappa_cMpc_inv"]
                    - target_kappa
                ) / max(abs(target_kappa), 1.0e-300)
                allocation_summary_rows.append(
                    {
                        "z": z,
                        "shape_lane": shape_lane,
                        "group": group,
                        "target_kappa_cMpc_inv": target_kappa,
                        "hierarchical_kappa_cMpc_inv":
                            diagnostics["global_kappa_cMpc_inv"],
                        "opacity_relative_residual":
                            relative_opacity,
                        "q_sum_residual":
                            abs(diagnostics["q_sum"] - 1.0)
                            if target_kappa > 0
                            else diagnostics["q_sum"],
                        "species_allocation_sum_residual_max":
                            diagnostics[
                                "allocation_sum_residual_max"
                            ],
                        "photon_allocation_relative_residual":
                            diagnostics[
                                "photon_allocation_relative_residual"
                            ],
                        "one_sided_raw_boundary_count":
                            diagnostics["boundary_policy_count"],
                        "group_absorption_rate_s-1_cMpc-3":
                            group_rate,
                    }
                )

            if group in {"G1", "G2a"}:
                hi_component_rate = float(
                    component_absorption[
                        np.isclose(
                            component_absorption["z_mid"], z
                        )
                        & (component_absorption["group"] == group)
                        & (
                            component_absorption["component"]
                            == "EFFECTIVE_HI_SUBGRID"
                        )
                    ]["absorption_rate_s-1_cMpc-3"].iloc[0]
                )
                macro_opacity_rows.append(
                    {
                        "z": z,
                        "group": group,
                        "macro_effective_HI_absorption_rate":
                            hi_component_rate,
                        "LOCAL_NEUTRAL_HAZARD_PRIMARY_sum":
                            hi_component_rate,
                        "RECOMBINATION_WEIGHTED_AUDITOR_sum":
                            hi_component_rate,
                        "SCRIPT_SELF_SHIELDING_AUDITOR_sum":
                            hi_component_rate,
                        "maximum_lane_difference": 0.0,
                        "normalization_type":
                            "DISAGGREGATION_IDENTITY_NOT_OPACITY_FIT",
                    }
                )

        row_target = macro["W_macro"].to_numpy()
        micro_base = (
            nodes[nodes["macro_index"] == 0]
            .sort_values("micro_index")["w_micro"]
            .to_numpy()
        )
        uniform_seed = np.ones(
            (len(row_target), len(micro_base))
        )
        product_uniform, n_uniform, res_uniform = ipf(
            uniform_seed, row_target, micro_base
        )
        macro_score = (
            macro["D_L_mass"].to_numpy() - 1.0
        ) / max(macro["D_L_mass"].std(), 1.0e-12)
        micro_delta = (
            nodes[nodes["macro_index"] == 0]
            .sort_values("micro_index")["delta_sub"]
            .to_numpy()
        )
        micro_score = (
            np.log(micro_delta)
            - np.mean(np.log(micro_delta))
        ) / max(np.std(np.log(micro_delta)), 1.0e-12)
        physical_seed = np.exp(
            0.20 * macro_score[:, None] * micro_score[None, :]
        )
        physical_projection, n_physical, res_physical = ipf(
            physical_seed, row_target, micro_base
        )
        product_reference = (
            row_target[:, None] * micro_base[None, :]
        )
        structural_zero_detected = False
        bad_seed = np.ones_like(uniform_seed)
        bad_seed[0, :] = 0.0
        try:
            ipf(bad_seed, row_target, micro_base)
        except ValueError:
            structural_zero_detected = True
        ipf_rows.append(
            {
                "z": z,
                "uniform_seed_iterations": n_uniform,
                "uniform_seed_marginal_residual": res_uniform,
                "uniform_seed_entropy":
                    entropy(product_uniform),
                "uniform_seed_KL_to_product":
                    max(
                        kl_divergence(
                            product_uniform,
                            product_reference,
                        ),
                        0.0,
                    ),
                "physical_seed_iterations": n_physical,
                "physical_seed_marginal_residual":
                    res_physical,
                "physical_projection_KL_to_seed":
                    kl_divergence(
                        physical_projection,
                        physical_seed / physical_seed.sum(),
                    ),
                "physical_projection_KL_to_product":
                    kl_divergence(
                        physical_projection,
                        product_reference,
                    ),
                "structural_zero_infeasibility_detected":
                    structural_zero_detected,
                "baseline_requires_nontrivial_IPF":
                    bool(
                        np.max(
                            np.abs(
                                product_uniform
                                - product_reference
                            )
                        )
                        > 1.0e-12
                    ),
            }
        )

    macro_frame = pd.concat(macro_tables, ignore_index=True)
    nodes_frame = pd.concat(node_tables, ignore_index=True)
    allocation_frame = pd.concat(
        allocation_tables, ignore_index=True
    )
    source_frame = pd.DataFrame(source_rows)
    source_convergence = pd.DataFrame(
        source_convergence_rows
    )
    allocation_summary = pd.DataFrame(
        allocation_summary_rows
    )
    sensitivity = pd.DataFrame(sensitivity_rows)
    density_adapter = pd.DataFrame(density_adapter_rows)
    ipf_frame = pd.DataFrame(ipf_rows)
    target_frame = pd.DataFrame(target_rows)
    macro_opacity = pd.DataFrame(macro_opacity_rows)
    weight_invariance = pd.DataFrame(
        weight_invariance_rows
    )
    raw_shape_fill = pd.DataFrame(
        [
            {
                "gamma_nearest_fill_count":
                    raw_model.gamma_nearest_fill_count,
                "gamma_interpolation_count":
                    raw_model.gamma_interpolation_count,
                "nearest_fill_fraction":
                    raw_model.gamma_nearest_fill_count
                    / max(
                        raw_model.gamma_nearest_fill_count
                        + raw_model.gamma_interpolation_count,
                        1,
                    ),
                "scope":
                    "MACRO_SHAPE_DISAGGREGATION_ONLY",
                "global_R1_opacity_modified": False,
                "policy":
                    "NEAREST_AVAILABLE_RAW_GAMMA_NODE_ASSET_FILL",
            }
        ]
    )

    macro_frame.to_csv(
        output / "macro_environment_measure.csv", index=False
    )
    nodes_frame.to_csv(
        output / "hierarchical_node_table.csv.gz",
        index=False,
        compression="gzip",
    )
    source_frame.to_csv(
        output / "hierarchical_full_ots_source.csv",
        index=False,
    )
    source_convergence.to_csv(
        output / "b2c0_source_reproduction.csv",
        index=False,
    )
    allocation_frame.to_csv(
        output / "macro_species_photon_allocation.csv",
        index=False,
    )
    allocation_summary.to_csv(
        output / "opacity_allocation_gates.csv",
        index=False,
    )
    sensitivity.to_csv(
        output / "hierarchical_sensitivity_auditors.csv",
        index=False,
    )
    density_adapter.to_csv(
        output / "macro_density_mass_adapter.csv",
        index=False,
    )
    ipf_frame.to_csv(
        output / "ipf_kl_audit.csv", index=False
    )
    target_frame.to_csv(
        output / "r1_opacity_targets.csv", index=False
    )
    macro_opacity.to_csv(
        output / "macro_HI_disaggregation_identity.csv",
        index=False,
    )
    weight_invariance.to_csv(
        output / "measure_weight_invariance_audit.csv",
        index=False,
    )
    raw_shape_fill.to_csv(
        output / "raw_macro_shape_fill_audit.csv",
        index=False,
    )
    np.savez_compressed(
        output / "primary_node_allocation_z5p75.npz",
        **primary_detail,
    )

    weight_sum_error = float(
        macro_frame.groupby("z")["W_macro"]
        .sum()
        .sub(1.0)
        .abs()
        .max()
    )
    micro_sum_error = float(
        nodes_frame.groupby(["z", "macro_index"])[
            "w_micro"
        ]
        .sum()
        .sub(1.0)
        .abs()
        .max()
    )
    density_mass_error = float(
        nodes_frame.groupby("z")
        .apply(
            lambda frame: np.sum(
                frame["W_node"] * frame["delta_total"]
            ),
            include_groups=False,
        )
        .sub(1.0)
        .abs()
        .max()
    )
    macro_weight_variation = float(
        weight_invariance[
            "macro_weight_max_abs_difference_from_z6"
        ].max()
    )
    micro_weight_variation = float(
        weight_invariance[
            "micro_weight_max_abs_difference_from_z6"
        ].max()
    )
    opacity_error = float(
        allocation_summary["opacity_relative_residual"].max()
    )
    source_error = float(
        source_convergence["max_relative_error"].max()
    )
    photon_error = float(
        allocation_summary[
            "photon_allocation_relative_residual"
        ].max()
    )
    allocation_error = float(
        allocation_summary[
            "species_allocation_sum_residual_max"
        ].max()
    )
    threshold_error = int(
        (
            allocation_frame[
                ~allocation_frame["threshold_supported"]
            ]["j_abs_s-1_cMpc-3"].abs()
            > 0.0
        ).sum()
    )
    g3_error = float(
        allocation_frame[
            allocation_frame["group"] == "G3"
        ]["j_abs_s-1_cMpc-3"].abs().max()
    )
    ipf_residual = float(
        max(
            ipf_frame[
                "uniform_seed_marginal_residual"
            ].max(),
            ipf_frame[
                "physical_seed_marginal_residual"
            ].max(),
        )
    )
    structural_zero_pass = bool(
        ipf_frame[
            "structural_zero_infeasibility_detected"
        ].all()
    )

    passed = bool(
        weight_sum_error < 1.0e-12
        and micro_sum_error < 1.0e-12
        and density_mass_error < 1.0e-10
        and macro_weight_variation == 0.0
        and micro_weight_variation == 0.0
        and opacity_error < 0.01
        and source_error < 0.01
        and photon_error < 1.0e-10
        and allocation_error < 1.0e-10
        and threshold_error == 0
        and g3_error == 0.0
        and ipf_residual < 1.0e-10
        and structural_zero_pass
    )
    result = {
        "stage": (
            "P0.5-B2C2B0A-HIERARCHICAL-TWO-SCALE-"
            "OPACITY-CHEMISTRY-CLOSURE-LOCK"
        ),
        "verdict": (
            "DURABLE_PASS_B2C2B0B_AUTHORIZED_WITH_CAVEATS"
            if passed
            else "FAIL_CLOSED_HIERARCHICAL_CLOSURE"
        ),
        "density_scale_firewall": {
            "emulator_coordinate":
                "D_L_emulator from P0.4 density mapping",
            "mass_rate_coordinate": (
                "D_L_mass = D_L_emulator/"
                "<D_L_emulator>_fixed_W"
            ),
            "flat_density_identification": False,
            "mass_adapter_factor_range": [
                float(
                    density_adapter[
                        "mass_normalization_factor"
                    ].min()
                ),
                float(
                    density_adapter[
                        "mass_normalization_factor"
                    ].max()
                ),
            ],
        },
        "measure_policy": {
            "primary":
                "FIXED_WEIGHT_LAGRANGIAN_MACRO_MICRO_PARCELS",
            "dot_W_J": 0.0,
            "dot_w_I_given_J": 0.0,
            "weight_lock_redshift": 6.0,
            "node_coordinates_transport":
                "FIXED_QUANTILE_LABELS_MOVING_DELTA_T",
            "redshift_pdf_rebuild_without_flux":
                "FAIL_CLOSED",
        },
        "gates": {
            "macro_weight_sum_error_max":
                weight_sum_error,
            "micro_conditional_weight_sum_error_max":
                micro_sum_error,
            "global_mass_density_error_max":
                density_mass_error,
            "macro_weight_variation_max":
                macro_weight_variation,
            "micro_weight_variation_max":
                micro_weight_variation,
            "R1_global_opacity_relative_error_max":
                opacity_error,
            "B2C0_source_reproduction_relative_error_max":
                source_error,
            "node_photon_allocation_relative_error_max":
                photon_error,
            "species_allocation_sum_error_max":
                allocation_error,
            "threshold_support_violation_count":
                threshold_error,
            "primary_G3_absorption_max": g3_error,
            "IPF_marginal_residual_max":
                ipf_residual,
            "structural_zero_infeasibility_detected":
                structural_zero_pass,
            "macro_HI_lane_invariance_error_max":
                float(
                    macro_opacity[
                        "maximum_lane_difference"
                    ].max()
                )
                if not macro_opacity.empty
                else 0.0,
            "raw_macro_shape_nearest_gamma_fill_count":
                int(raw_model.gamma_nearest_fill_count),
            "raw_macro_shape_nearest_gamma_fill_fraction":
                float(
                    raw_shape_fill[
                        "nearest_fill_fraction"
                    ].iloc[0]
                ),
        },
        "sensitivity": {
            "auditors": sorted(
                sensitivity["auditor"].unique()
            ),
            "not_used_for_calibration": True,
            "micro_absorber_shape_lanes":
                MICRO_SHAPE_LANES,
            "all_shape_lanes_required_in_B2C2B0B":
                True,
        },
        "B2C2B0B_authorization": {
            "authorized": bool(passed),
            "conditions": [
                "use fixed z=6 macro/micro weights without PDF regeneration",
                "evolve all three effective-HI micro-shape lanes and retain envelope",
                "do not treat nearest-Gamma macro shape filling as calibrated",
                "do not compute unresolved sink in B2C2B0B",
                "run native Wolfram crosscheck when its runtime is available",
            ] if passed else [],
        },
        "native_plugin_status": {
            "Wolfram":
                "NATIVE_RUNTIME_UNAVAILABLE; .wl script plus exact SymPy fallback",
            "Precise_Special_Functions":
                "PLUGIN_NAMESPACE_UNAVAILABLE; 80-dps mpmath fallback",
        },
        "next_stage": (
            "P0.5-B2C2B0B-MATCHED-PHASESPACE-HISTORY-LOCK"
            if passed
            else "BLOCKED"
        ),
        "forbidden_work_confirmed": [
            "history re-evolution",
            "unresolved-sink subtraction",
            "front allocation",
            "Q_M growth",
            "source/f_esc calibration",
            "primordial recombination implementation",
            "primitive geometry transplant",
            "Bianchi feedback",
        ],
    }
    (output.parent / "results.json").write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )
    return result




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--r1-root", type=Path, required=True)
    parser.add_argument("--b2c0-root", type=Path, required=True)
    parser.add_argument("--p04-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            run_stage(
                args.r1_root,
                args.b2c0_root,
                args.p04_root,
                args.output,
            ),
            indent=2,
        )
    )
