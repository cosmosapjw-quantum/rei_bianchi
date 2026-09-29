"""P0.5-B2C1B multigroup H/He transmission and source-support lock.

Canonical groups
----------------
G1  = [13.60, 24.59) eV
G2a = [24.59, 39.50] eV
G2b = (39.50, 54.42) eV
G3  = [54.42, 100.0] eV

Species support
---------------
HI   : G1, G2a, G2b, G3
HeI  :     G2a, G2b, G3
HeII :                G3

Finite-optical-depth transmission is computed by direct spectral quadrature:

    F_g = <exp[-tau_g(E)]>_phi

and absorbed-photon species allocation by

    A_sg = <(1-exp[-tau]) tau_s/tau>_phi / <1-exp[-tau]>_phi.

The primary MFP source has exact G3 occupation zero. Its positive
HeII->HeIII external-maintenance demand is therefore reported as an
unsupported physical demand, never filled by a numerical photon floor.
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
from scipy.optimize import nnls

HERE = Path(__file__).resolve().parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


B2C0 = load_module("phase_space_kernel_b2c0", HERE / "phase_space_kernel_b2c0.py")
B2C1A = load_module("hi_transmission_kernel_b2c1a", HERE / "hi_transmission_kernel_b2c1a.py")

MPC_CM = B2C0.MPC_CM
YHE = B2C0.YHE

GROUPS = {
    "G1": (13.60, 24.59),
    "G2a": (24.59, 39.50),
    "G2b": (39.50, 54.42),
    "G3": (54.42, 100.0),
}
GROUP_ORDER = list(GROUPS)
SPECIES = ["HI", "HeI", "HeII"]
THRESHOLDS = {"HI": 13.60, "HeI": 24.59, "HeII": 54.42}
SUPPORT = {
    "HI": {"G1", "G2a", "G2b", "G3"},
    "HeI": {"G2a", "G2b", "G3"},
    "HeII": {"G3"},
}

VERNER = {
    "HI": {
        "Eth_eV": 13.60,
        "E0_eV": 0.4298,
        "sigma0_Mb": 5.475e4,
        "ya": 32.88,
        "p": 2.963,
        "yw": 0.0,
        "y0": 0.0,
        "y1": 0.0,
    },
    "HeI": {
        "Eth_eV": 24.59,
        "E0_eV": 13.61,
        "sigma0_Mb": 949.2,
        "ya": 1.469,
        "p": 3.188,
        "yw": 2.039,
        "y0": 0.4434,
        "y1": 2.136,
    },
    "HeII": {
        "Eth_eV": 54.42,
        "E0_eV": 1.720,
        "sigma0_Mb": 1.369e4,
        "ya": 32.88,
        "p": 2.963,
        "yw": 0.0,
        "y0": 0.0,
        "y1": 0.0,
    },
}

SPECTRUM_LANES = {
    "MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD": {
        "role": "PRIMARY_PHYSICAL_MFP_CONSISTENT",
        "kind": "POWERLAW_PHOTON",
        "photon_index": -2.5,
        "source_max_eV": 54.42,
    },
    "CLOUDY_BLACKBODY_80000K": {
        "role": "STELLAR_HARD_AUDITOR",
        "kind": "BLACKBODY_PHOTON",
        "temperature_K": 8.0e4,
        "source_max_eV": 100.0,
    },
    "CLOUDY_HARD_POWERLAW_FNU_MINUS_1P5": {
        "role": "HARD_POWERLAW_STRESS_AUDITOR",
        "kind": "POWERLAW_PHOTON",
        "photon_index": -2.5,
        "source_max_eV": 100.0,
    },
    "B2A_E_MINUS_4_NUMERICAL": {
        "role": "NUMERICAL_AUDITOR_NOT_PHYSICAL_PRIOR",
        "kind": "POWERLAW_PHOTON",
        "photon_index": -4.0,
        "source_max_eV": 100.0,
    },
}

PRODUCTION_NODES = {"G1": 12, "G2a": 24, "G2b": 24, "G3": 32}
REFERENCE_NODES = 64
ATOMIC_TABLE_NODES = 512

B_STOICH = B2C0.B_STOICH


@dataclass(frozen=True)
class SpectrumLane:
    name: str
    role: str
    source_max_eV: float


def verner_sigma(species: str, energy_eV: np.ndarray | float) -> np.ndarray:
    p = VERNER[species]
    energy = np.asarray(energy_eV, dtype=float)
    x = energy / p["E0_eV"] - p["y0"]
    y = np.sqrt(x * x + p["y1"] ** 2)
    value = (
        1.0e-18
        * p["sigma0_Mb"]
        * ((x - 1.0) ** 2 + p["yw"] ** 2)
        * y ** (0.5 * p["p"] - 5.5)
        / (1.0 + np.sqrt(y / p["ya"])) ** p["p"]
    )
    return np.where(energy >= p["Eth_eV"], value, 0.0)


def spectrum_weight(energy_eV: np.ndarray, lane: str, operator_only: bool = False) -> np.ndarray:
    config = SPECTRUM_LANES[lane]
    energy = np.asarray(energy_eV, dtype=float)
    if config["kind"] == "POWERLAW_PHOTON":
        weight = energy ** config["photon_index"]
    elif config["kind"] == "BLACKBODY_PHOTON":
        kT_eV = 8.617333262145e-5 * config["temperature_K"]
        x = energy / kT_eV
        weight = np.where(x < 700.0, energy**2 / np.expm1(x), 0.0)
    else:
        raise ValueError(lane)

    if not operator_only:
        weight = np.where(energy <= config["source_max_eV"], weight, 0.0)
    return weight


def gl_nodes(group: str, n: int) -> tuple[np.ndarray, np.ndarray]:
    lo, hi = GROUPS[group]
    x, w = leggauss(n)
    energy = 0.5 * (hi - lo) * x + 0.5 * (hi + lo)
    weights = 0.5 * (hi - lo) * w
    return energy, weights


def integrate_group(
    group: str,
    lane: str,
    values: Callable[[np.ndarray], np.ndarray],
    n: int,
    operator_only: bool = False,
) -> float:
    energy, weights = gl_nodes(group, n)
    phi = spectrum_weight(energy, lane, operator_only=operator_only)
    return float(np.sum(weights * phi * values(energy)))


def source_occupation(lane: str, n: int = 128) -> dict[str, float]:
    raw = {}
    for group in GROUP_ORDER:
        raw[group] = integrate_group(
            group, lane, lambda e: np.ones_like(e), n, operator_only=False
        )
        if lane == "MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD" and group == "G3":
            raw[group] = 0.0
    total = sum(raw.values())
    if total <= 0.0:
        raise RuntimeError(f"No source occupation for {lane}")
    fractions = {g: raw[g] / total for g in GROUP_ORDER}
    if lane == "MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD":
        fractions["G3"] = 0.0
        renorm = sum(fractions[g] for g in GROUP_ORDER[:-1])
        for group in GROUP_ORDER[:-1]:
            fractions[group] /= renorm
    return fractions


def atomic_operator_table() -> pd.DataFrame:
    rows = []
    for group, (lo, hi) in GROUPS.items():
        # Diagnostic high-resolution log-energy grid. Endpoints are retained
        # with explicit edge policy metadata; threshold support is still exact.
        energy = np.geomspace(lo, hi, ATOMIC_TABLE_NODES)
        for i, e in enumerate(energy):
            row = {
                "group": group,
                "node_index": i,
                "energy_eV": e,
                "group_low_eV": lo,
                "group_high_eV": hi,
                "edge_policy": (
                    "LEFT_CLOSED_RIGHT_OPEN"
                    if group in {"G1", "G2b"}
                    else "CLOSED_FOR_TABLE_MEASURE_ZERO_EDGES"
                ),
            }
            for species in SPECIES:
                row[f"support_{species}"] = group in SUPPORT[species]
                row[f"sigma_{species}_cm2"] = float(verner_sigma(species, e))
            rows.append(row)
    return pd.DataFrame(rows)


def source_moment_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    occupation_rows = []
    moment_rows = []

    for lane, config in SPECTRUM_LANES.items():
        fractions = source_occupation(lane)
        for group in GROUP_ORDER:
            occupation_rows.append(
                {
                    "lane": lane,
                    "role": config["role"],
                    "group": group,
                    "source_occupation": fractions[group],
                    "source_max_eV": config["source_max_eV"],
                    "exact_primary_G3_zero": (
                        lane == "MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD"
                        and group == "G3"
                    ),
                }
            )
            source_norm = integrate_group(
                group,
                lane,
                lambda e: np.ones_like(e),
                REFERENCE_NODES,
                operator_only=False,
            )
            operator_only = source_norm == 0.0
            operator_norm = integrate_group(
                group,
                lane,
                lambda e: np.ones_like(e),
                REFERENCE_NODES,
                operator_only=operator_only,
            )
            mean_energy = (
                integrate_group(
                    group,
                    lane,
                    lambda e: e,
                    REFERENCE_NODES,
                    operator_only=operator_only,
                )
                / operator_norm
            )

            for species in SPECIES:
                supported = group in SUPPORT[species]
                if not supported:
                    sigma_bar = 0.0
                    excess = 0.0
                    sigma_energy = 0.0
                else:
                    sigma_integral = integrate_group(
                        group,
                        lane,
                        lambda e, s=species: verner_sigma(s, e),
                        REFERENCE_NODES,
                        operator_only=operator_only,
                    )
                    sigma_bar = sigma_integral / operator_norm
                    if sigma_integral > 0:
                        excess = (
                            integrate_group(
                                group,
                                lane,
                                lambda e, s=species: (
                                    verner_sigma(s, e) * (e - THRESHOLDS[s])
                                ),
                                REFERENCE_NODES,
                                operator_only=operator_only,
                            )
                            / sigma_integral
                        )
                        sigma_energy = (
                            integrate_group(
                                group,
                                lane,
                                lambda e, s=species: verner_sigma(s, e) * e,
                                REFERENCE_NODES,
                                operator_only=operator_only,
                            )
                            / sigma_integral
                        )
                    else:
                        excess = 0.0
                        sigma_energy = 0.0
                moment_rows.append(
                    {
                        "lane": lane,
                        "role": config["role"],
                        "group": group,
                        "species": species,
                        "supported": supported,
                        "source_occupation": fractions[group],
                        "operator_only_due_zero_source": operator_only,
                        "mean_group_energy_eV": mean_energy,
                        "sigma_bar_cm2": sigma_bar,
                        "sigma_weighted_mean_energy_eV": sigma_energy,
                        "mean_excess_energy_eV": excess,
                    }
                )
    return pd.DataFrame(occupation_rows), pd.DataFrame(moment_rows)


def threshold_audit() -> pd.DataFrame:
    rows = []
    for species, threshold in THRESHOLDS.items():
        below = np.nextafter(threshold, 0.0)
        above = np.nextafter(threshold, np.inf)
        rows.append(
            {
                "species": species,
                "threshold_eV": threshold,
                "sigma_just_below_cm2": float(verner_sigma(species, below)),
                "sigma_at_threshold_cm2": float(verner_sigma(species, threshold)),
                "sigma_just_above_cm2": float(verner_sigma(species, above)),
                "below_threshold_exact_zero": float(verner_sigma(species, below)) == 0.0,
            }
        )
    # 39.5 eV is an implementation boundary, not an atomic threshold.
    for species in SPECIES:
        e0 = 39.5
        rows.append(
            {
                "species": species,
                "threshold_eV": e0,
                "sigma_just_below_cm2": float(verner_sigma(species, np.nextafter(e0, 0.0))),
                "sigma_at_threshold_cm2": float(verner_sigma(species, e0)),
                "sigma_just_above_cm2": float(verner_sigma(species, np.nextafter(e0, np.inf))),
                "below_threshold_exact_zero": None,
                "note": "MFP_DOMAIN_BOUNDARY_NOT_ATOMIC_THRESHOLD",
            }
        )
    return pd.DataFrame(rows)


def atomic_monotonicity_audit() -> pd.DataFrame:
    rows = []
    for group, (lo, hi) in GROUPS.items():
        energy = np.geomspace(np.nextafter(lo, hi), np.nextafter(hi, lo), 2048)
        for species in SPECIES:
            sigma = verner_sigma(species, energy)
            supported = group in SUPPORT[species]
            if supported:
                diff = np.diff(sigma)
                positive = diff > max(float(np.max(sigma)), 1.0) * 1.0e-13
                count = int(np.count_nonzero(positive))
                max_positive = float(np.max(diff)) if len(diff) else 0.0
            else:
                count = 0
                max_positive = 0.0
            rows.append(
                {
                    "group": group,
                    "species": species,
                    "supported": supported,
                    "positive_slope_violation_count": count,
                    "maximum_positive_delta_sigma_cm2": max_positive,
                }
            )
    return pd.DataFrame(rows)


def phase_state_rows(history_csv: Path) -> list[tuple[str, B2C0.HistoryState]]:
    history = pd.read_csv(history_csv)
    rows = []
    for row in history.itertuples():
        rows.append(
            (
                row.lane,
                B2C0.HistoryState(
                    z=float(row.z),
                    x_hii=float(row.xHII),
                    x_heii=float(row.xHeII),
                    x_heiii=float(row.xHeIII),
                    temperature=float(row.T_K),
                    gamma_hi=float(row.Gamma_HI),
                ),
            )
        )
    return rows


def transmission_allocation(
    n_species: np.ndarray,
    lengths_cm: np.ndarray,
    lane: str,
    group: str,
    n_energy: int,
) -> dict[str, np.ndarray]:
    energy, quadrature_weights = gl_nodes(group, n_energy)
    operator_only = (
        lane == "MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD"
        and group == "G3"
    )
    phi = spectrum_weight(energy, lane, operator_only=operator_only)
    weighted_phi = quadrature_weights * phi
    norm = float(np.sum(weighted_phi))
    if norm <= 0.0:
        raise RuntimeError(f"Zero operator norm for {lane}, {group}")

    sigma = np.stack([verner_sigma(s, energy) for s in SPECIES], axis=0)
    # shape: bins, species
    column = 0.5 * n_species * lengths_cm
    # tau species: bins, species, energy
    tau_species = column[:, :, None] * sigma[None, :, :]
    tau_total = np.sum(tau_species, axis=1)

    trans = np.exp(-np.clip(tau_total, 0.0, 745.0))
    F = np.sum(trans * weighted_phi[None, :], axis=1) / norm
    absorbed_energy = -np.expm1(-np.clip(tau_total, 0.0, 745.0))
    absorbed_fraction = np.sum(
        absorbed_energy * weighted_phi[None, :], axis=1
    ) / norm

    tau_fraction = np.divide(
        tau_species,
        tau_total[:, None, :],
        out=np.zeros_like(tau_species),
        where=tau_total[:, None, :] > 0.0,
    )
    numerators = np.sum(
        weighted_phi[None, None, :]
        * absorbed_energy[:, None, :]
        * tau_fraction,
        axis=2,
    ) / norm

    allocation = np.divide(
        numerators,
        absorbed_fraction[:, None],
        out=np.zeros_like(numerators),
        where=absorbed_fraction[:, None] > 1.0e-15,
    )

    # Optically thin limit for bins below the numerical absorption floor.
    thin_numerators = np.sum(
        weighted_phi[None, None, :]
        * tau_species,
        axis=2,
    ) / norm
    thin_total = np.sum(thin_numerators, axis=1)
    thin_allocation = np.divide(
        thin_numerators,
        thin_total[:, None],
        out=np.zeros_like(thin_numerators),
        where=thin_total[:, None] > 0.0,
    )
    thin_mask = absorbed_fraction <= 1.0e-15
    allocation[thin_mask] = thin_allocation[thin_mask]

    # Enforce exact support zeros after quadrature.
    for i, species in enumerate(SPECIES):
        if group not in SUPPORT[species]:
            allocation[:, i] = 0.0

    alloc_sum = np.sum(allocation, axis=1)
    positive_abs = absorbed_fraction > 1.0e-15
    allocation[positive_abs] /= alloc_sum[positive_abs, None]

    return {
        "F": F,
        "absorbed_fraction": absorbed_fraction,
        "allocation": allocation,
        "energy_eV": energy,
        "sigma": sigma,
    }


def integrated_operator(
    state: B2C0.HistoryState,
    lane: str,
    closure: str,
    n_delta: int,
    n_t: int,
    n_energy_by_group: dict[str, int],
    he_length_factor: float = 1.0,
    heii_length_factor: float = 1.0,
    use_mfp_length: bool = False,
    mfp_lookup: dict[float, float] | None = None,
) -> dict[str, Any]:
    c0 = B2C0.calibrate_mhr_c0(state.z)
    calibration_grid = B2C0.build_grid(state, 192, 28, c0)
    offsets = B2C0.calibrate_fraction_offsets(state, calibration_grid)
    grid = B2C0.build_grid(state, n_delta, n_t, c0)
    means = B2C0.conditional_means(state, grid, offsets)
    moments = B2C0.conditional_moments(means, closure)
    kernel = B2C0.full_ots_kernel(state, grid, moments)

    n_h = B2C0.NH0_CM3 * (1.0 + state.z) ** 3 * grid["delta"]
    n_he = YHE * n_h
    n_species = np.stack(
        [
            n_h * (1.0 - moments["xHII"]),
            n_he * moments["xHeI"],
            n_he * moments["xHeII"],
        ],
        axis=-1,
    )

    if use_mfp_length:
        if mfp_lookup is None:
            raise ValueError("MFP lookup required")
        key = round(float(state.z), 8)
        common_length = np.full_like(
            n_h, mfp_lookup[key] / (1.0 + state.z) * MPC_CM
        )
    else:
        sigma_bar_h = B2C1A.gray_sigma_hi()[0]
        chi = B2C1A.calibrate_chi_jeans(
            state.z, state.gamma_hi, sigma_bar_h
        )["chi_J"]
        common_length = chi * B2C1A.jeans_length_cm(
            n_h,
            grid["temperature"],
            moments["xHII"],
            moments["xHeII"],
            moments["xHeIII"],
        )

    lengths = np.stack(
        [
            common_length,
            he_length_factor * common_length,
            heii_length_factor * common_length,
        ],
        axis=-1,
    )

    weights = grid["weight"].reshape(-1)
    n_species_flat = n_species.reshape(-1, 3)
    lengths_flat = lengths.reshape(-1, 3)
    kernel_m = kernel["m_ext"].reshape(-1, 3)
    kernel_source = kernel["source"].reshape(-1, 5)
    conversion = MPC_CM**3 / (1.0 + state.z) ** 3

    group_results = {}
    A_matrix = np.zeros((3, 4), dtype=float)
    absorbed_phase = np.zeros(4, dtype=float)
    F_phase = np.zeros(4, dtype=float)

    for j, group in enumerate(GROUP_ORDER):
        op = transmission_allocation(
            n_species_flat,
            lengths_flat,
            lane,
            group,
            n_energy_by_group[group],
        )
        F_phase[j] = float(np.sum(weights * op["F"]))
        absorbed_phase[j] = float(np.sum(weights * op["absorbed_fraction"]))
        absorption_weight = weights * op["absorbed_fraction"]
        denom = float(np.sum(absorption_weight))
        if denom > 0.0:
            A_matrix[:, j] = np.sum(
                absorption_weight[:, None] * op["allocation"], axis=0
            ) / denom
        group_results[group] = {
            "F_phase": F_phase[j],
            "absorbed_phase": absorbed_phase[j],
            "allocation": A_matrix[:, j].copy(),
            "F_min": float(np.min(op["F"])),
            "F_max": float(np.max(op["F"])),
            "allocation_sum_error_max": float(
                np.max(
                    np.abs(
                        np.sum(op["allocation"], axis=1)[
                            op["absorbed_fraction"] > 1.0e-15
                        ]
                        - 1.0
                    )
                )
            )
            if np.any(op["absorbed_fraction"] > 1.0e-15)
            else 0.0,
        }

    maintenance = np.sum(weights[:, None] * kernel_m, axis=0) * conversion
    source_vec = np.sum(weights[:, None] * kernel_source, axis=0) * conversion

    occupation = source_occupation(lane)
    support_groups = [
        j for j, group in enumerate(GROUP_ORDER) if occupation[group] > 0.0
    ]
    A_supported = A_matrix[:, support_groups]
    required, residual_norm = nnls(A_supported, maintenance)
    absorbed_required = np.zeros(4)
    absorbed_required[support_groups] = required
    supplied = A_matrix @ absorbed_required
    residual_vector = maintenance - supplied
    relative_residual = float(
        np.linalg.norm(residual_vector)
        / max(np.linalg.norm(maintenance), 1.0)
    )
    stoich_residual = B_STOICH @ supplied + source_vec

    incident_required = np.divide(
        absorbed_required,
        absorbed_phase,
        out=np.zeros_like(absorbed_required),
        where=absorbed_phase > 1.0e-15,
    )
    if incident_required.sum() > 0:
        required_incident_fraction = incident_required / incident_required.sum()
    else:
        required_incident_fraction = np.zeros(4)
    source_fraction = np.array([occupation[g] for g in GROUP_ORDER])
    source_ratio_l1 = float(
        np.sum(np.abs(required_incident_fraction - source_fraction))
    )

    return {
        "state": state,
        "lane": lane,
        "closure": closure,
        "F_phase": F_phase,
        "absorbed_phase": absorbed_phase,
        "A_matrix": A_matrix,
        "maintenance": maintenance,
        "source_vector": source_vec,
        "absorbed_required": absorbed_required,
        "supplied": supplied,
        "support_residual": residual_vector,
        "support_relative_residual": relative_residual,
        "support_nnls_residual_norm": float(residual_norm),
        "stoich_residual": stoich_residual,
        "required_incident_fraction": required_incident_fraction,
        "source_fraction": source_fraction,
        "source_ratio_l1": source_ratio_l1,
        "minimum_length_cm": float(np.min(lengths_flat)),
        "maximum_length_cm": float(np.max(lengths_flat)),
        "group_results": group_results,
    }


def mfp_lookup_from_b2c1a(root: Path) -> dict[float, float]:
    candidates = list(
        root.rglob("public_repo_exact_checkpoint_global.csv")
    )
    if not candidates:
        raise FileNotFoundError("P0.4 MFP table not found")
    frame = pd.read_csv(candidates[0])
    use = frame[
        np.isclose(frame["energy_eV"], 13.6)
        & (frame["mode"] == "public_continuous_joint")
    ]
    return {
        round(float(row.z), 8): float(row.lambda_density_cMpc)
        for row in use.itertuples()
    }


def run_stage(
    history_csv: Path,
    spectrum_lock_json: Path,
    b2c1a_extracted_root: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    atomic = atomic_operator_table()
    occupations, moments = source_moment_tables()
    thresholds = threshold_audit()
    monotonicity = atomic_monotonicity_audit()

    atomic.to_csv(
        output_dir / "atomic_operator_table.csv.gz",
        index=False,
        compression="gzip",
    )
    occupations.to_csv(output_dir / "source_occupation_table.csv", index=False)
    moments.to_csv(output_dir / "source_projected_moments.csv", index=False)
    thresholds.to_csv(output_dir / "threshold_audit.csv", index=False)
    monotonicity.to_csv(output_dir / "atomic_monotonicity_audit.csv", index=False)

    support_matrix = pd.DataFrame(
        [
            {
                "species": species,
                **{group: group in SUPPORT[species] for group in GROUP_ORDER},
            }
            for species in SPECIES
        ]
    )
    support_matrix.to_csv(output_dir / "species_support_matrix.csv", index=False)

    locked_spectra = json.loads(spectrum_lock_json.read_text())
    locked_fraction = {
        row["lane"]: np.array(row["source_fraction"], dtype=float)
        for row in locked_spectra
    }
    occupation_checks = []
    for lane in SPECTRUM_LANES:
        calculated = occupations[
            occupations["lane"] == lane
        ].set_index("group").loc[GROUP_ORDER]["source_occupation"].to_numpy()
        difference = calculated - locked_fraction[lane]
        occupation_checks.append(
            {
                "lane": lane,
                "max_absolute_difference": float(np.max(np.abs(difference))),
                "primary_G3_exact_zero": (
                    lane != "MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD"
                    or calculated[3] == 0.0
                ),
            }
        )
    pd.DataFrame(occupation_checks).to_csv(
        output_dir / "spectrum_lock_regression.csv", index=False
    )

    history_rows = phase_state_rows(history_csv)
    mfp_lookup = mfp_lookup_from_b2c1a(b2c1a_extracted_root)

    transmission_rows = []
    allocation_rows = []
    support_rows = []
    convergence_rows = []

    # Full history for the three physically relevant source lanes; E^-4 remains
    # a moment/operator auditor and is evaluated at z=5.5 only.
    selected_rows = [
        (lane, state)
        for lane, state in history_rows
        if lane != "B2A_E_MINUS_4_NUMERICAL" or abs(state.z - 5.5) < 1.0e-9
    ]

    for lane, state in selected_rows:
        closures = ["DETERMINISTIC"]
        if abs(state.z - 5.5) < 1.0e-9:
            closures.append("PATCHY_BETA_DIRICHLET")

        for closure in closures:
            reference = integrated_operator(
                state,
                lane,
                closure,
                n_delta=160,
                n_t=24,
                n_energy_by_group={g: REFERENCE_NODES for g in GROUP_ORDER},
            )
            production = integrated_operator(
                state,
                lane,
                closure,
                n_delta=80,
                n_t=16,
                n_energy_by_group=PRODUCTION_NODES,
            )

            for j, group in enumerate(GROUP_ORDER):
                ref_group = reference["group_results"][group]
                prod_group = production["group_results"][group]
                f_error = abs(
                    prod_group["F_phase"] - ref_group["F_phase"]
                ) / max(abs(ref_group["F_phase"]), 1.0e-8)
                a_ref = ref_group["allocation"]
                a_prod = prod_group["allocation"]
                a_error = np.abs(a_prod - a_ref) / np.maximum(
                    np.abs(a_ref), 1.0e-6
                )

                transmission_rows.append(
                    {
                        "lane": lane,
                        "role": SPECTRUM_LANES[lane]["role"],
                        "z": state.z,
                        "closure": closure,
                        "group": group,
                        "source_occupation":
                            reference["source_fraction"][j],
                        "operator_only_due_zero_source": (
                            lane == "MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD"
                            and group == "G3"
                        ),
                        "F_reference": ref_group["F_phase"],
                        "F_production": prod_group["F_phase"],
                        "absorbed_fraction_reference":
                            ref_group["absorbed_phase"],
                        "F_relative_mismatch": f_error,
                        "allocation_sum_error_max":
                            ref_group["allocation_sum_error_max"],
                        "F_min_bin": ref_group["F_min"],
                        "F_max_bin": ref_group["F_max"],
                    }
                )
                for i, species in enumerate(SPECIES):
                    allocation_rows.append(
                        {
                            "lane": lane,
                            "z": state.z,
                            "closure": closure,
                            "group": group,
                            "species": species,
                            "supported": group in SUPPORT[species],
                            "A_reference": a_ref[i],
                            "A_production": a_prod[i],
                            "relative_mismatch_with_floor": a_error[i],
                        }
                    )
                convergence_rows.append(
                    {
                        "lane": lane,
                        "z": state.z,
                        "closure": closure,
                        "group": group,
                        "F_relative_mismatch": f_error,
                        "A_relative_mismatch_max_with_floor":
                            float(np.max(a_error)),
                    }
                )

            primary = lane == "MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD"
            support_status = (
                "PRIMARY_SOURCE_CANNOT_MAINTAIN_HEIII"
                if primary and reference["maintenance"][2] > 0.0
                else (
                    "FULL_SUPPORT_CLOSED"
                    if reference["support_relative_residual"] < 1.0e-8
                    else "SUPPORT_CONE_RESIDUAL"
                )
            )
            support_rows.append(
                {
                    "lane": lane,
                    "z": state.z,
                    "closure": closure,
                    "status": support_status,
                    "m_HI_to_HII_s-1_cMpc-3":
                        reference["maintenance"][0],
                    "m_HeI_to_HeII_s-1_cMpc-3":
                        reference["maintenance"][1],
                    "m_HeII_to_HeIII_s-1_cMpc-3":
                        reference["maintenance"][2],
                    "supplied_HI_s-1_cMpc-3": reference["supplied"][0],
                    "supplied_HeI_s-1_cMpc-3": reference["supplied"][1],
                    "supplied_HeII_s-1_cMpc-3": reference["supplied"][2],
                    "residual_HI_s-1_cMpc-3":
                        reference["support_residual"][0],
                    "residual_HeI_s-1_cMpc-3":
                        reference["support_residual"][1],
                    "residual_HeII_s-1_cMpc-3":
                        reference["support_residual"][2],
                    "support_relative_residual":
                        reference["support_relative_residual"],
                    "stoich_residual_inf_s-1_cMpc-3":
                        float(np.max(np.abs(reference["stoich_residual"]))),
                    "source_ratio_L1_auditor": reference["source_ratio_l1"],
                    "primary_G3_source_exact_zero":
                        (not primary or reference["source_fraction"][3] == 0.0),
                }
            )

    transmission = pd.DataFrame(transmission_rows)
    allocations = pd.DataFrame(allocation_rows)
    support = pd.DataFrame(support_rows)
    convergence = pd.DataFrame(convergence_rows)

    transmission.to_csv(output_dir / "group_transmission_summary.csv", index=False)
    allocations.to_csv(output_dir / "species_allocation_summary.csv", index=False)
    support.to_csv(output_dir / "maintenance_source_support.csv", index=False)
    convergence.to_csv(output_dir / "quadrature_convergence.csv", index=False)

    # Species-specific length sensitivity at z=5.5 for the primary gas state
    # and the two hard auditor gas states.
    sensitivity_rows = []
    for lane, state in history_rows:
        if abs(state.z - 5.5) > 1.0e-9:
            continue
        if lane not in {
            "MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD",
            "CLOUDY_BLACKBODY_80000K",
            "CLOUDY_HARD_POWERLAW_FNU_MINUS_1P5",
        }:
            continue
        for he_factor in [0.5, 1.0, 2.0]:
            for heii_factor in [0.5, 1.0, 2.0]:
                result = integrated_operator(
                    state,
                    lane,
                    "DETERMINISTIC",
                    n_delta=80,
                    n_t=16,
                    n_energy_by_group=PRODUCTION_NODES,
                    he_length_factor=he_factor,
                    heii_length_factor=heii_factor,
                )
                sensitivity_rows.append(
                    {
                        "lane": lane,
                        "z": state.z,
                        "chi_HeI": he_factor,
                        "chi_HeII": heii_factor,
                        "support_relative_residual":
                            result["support_relative_residual"],
                        "residual_HI": result["support_residual"][0],
                        "residual_HeI": result["support_residual"][1],
                        "residual_HeII": result["support_residual"][2],
                        **{
                            f"F_{group}": result["F_phase"][j]
                            for j, group in enumerate(GROUP_ORDER)
                        },
                    }
                )
    pd.DataFrame(sensitivity_rows).to_csv(
        output_dir / "species_length_sensitivity.csv", index=False
    )

    # MFP circularity auditor: primary lane, z=5.5 only.
    primary_state = next(
        state
        for lane, state in history_rows
        if lane == "MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD"
        and abs(state.z - 5.5) < 1.0e-9
    )
    mfp_result = integrated_operator(
        primary_state,
        "MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD",
        "DETERMINISTIC",
        n_delta=80,
        n_t=16,
        n_energy_by_group=PRODUCTION_NODES,
        use_mfp_length=True,
        mfp_lookup=mfp_lookup,
    )
    mfp_record = {
        "status": "AUDITOR_ONLY_CIRCULARITY_FIREWALL",
        "z": 5.5,
        "proper_length_cm": mfp_result["minimum_length_cm"],
        "F_by_group": {
            group: mfp_result["F_phase"][j]
            for j, group in enumerate(GROUP_ORDER)
        },
        "support_relative_residual": mfp_result["support_relative_residual"],
        "reason": (
            "P0.4 MFP already encodes absorber opacity; it cannot be reused "
            "as production local scaleheight and later combined with an "
            "unresolved MFP sink."
        ),
    }
    (output_dir.parent / "MFP_CIRCULARITY_LEDGER.json").write_text(
        json.dumps(mfp_record, indent=2), encoding="utf-8"
    )

    max_f_error = float(convergence["F_relative_mismatch"].max())
    max_a_error = float(
        convergence["A_relative_mismatch_max_with_floor"].max()
    )
    allocation_sum_max = float(
        transmission["allocation_sum_error_max"].max()
    )
    support_zero_pass = bool(
        thresholds[
            thresholds["species"].isin(SPECIES)
            & thresholds["below_threshold_exact_zero"].eq(True)
        ].shape[0]
        == 3
    )
    primary_support = support[
        support["lane"] == "MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD"
    ]
    hard_support = support[
        support["lane"].isin(
            [
                "CLOUDY_BLACKBODY_80000K",
                "CLOUDY_HARD_POWERLAW_FNU_MINUS_1P5",
            ]
        )
    ]
    primary_unsupported = bool(
        (primary_support["status"] == "PRIMARY_SOURCE_CANNOT_MAINTAIN_HEIII").all()
        and (primary_support["m_HeII_to_HeIII_s-1_cMpc-3"] > 0.0).all()
        and primary_support["primary_G3_source_exact_zero"].all()
    )
    hard_closed_fraction = float(
        np.mean(hard_support["status"] == "FULL_SUPPORT_CLOSED")
    )

    results = {
        "stage": "P0.5-B2C1B-MULTIGROUP-HHE-TRANSMISSION-LOCK",
        "verdict": (
            "PASS_WITH_PRIMARY_HEIII_UNSUPPORTED"
            if (
                max_f_error < 0.01
                and max_a_error < 0.01
                and allocation_sum_max < 1.0e-10
                and support_zero_pass
                and primary_unsupported
            )
            else "FAIL"
        ),
        "atomic_groups": GROUPS,
        "species_support": {
            species: sorted(SUPPORT[species], key=GROUP_ORDER.index)
            for species in SPECIES
        },
        "gates": {
            "F_quadrature_relative_mismatch_max": max_f_error,
            "A_quadrature_relative_mismatch_max_with_floor": max_a_error,
            "allocation_sum_error_max": allocation_sum_max,
            "threshold_zero_exact": support_zero_pass,
            "primary_G3_exact_zero": bool(
                occupations[
                    (occupations["lane"] == "MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD")
                    & (occupations["group"] == "G3")
                ]["source_occupation"].iloc[0]
                == 0.0
            ),
            "primary_HeIII_unsupported_fail_closed": primary_unsupported,
            "hard_auditor_full_support_fraction": hard_closed_fraction,
            "atomic_monotonicity_positive_slope_violations":
                int(monotonicity["positive_slope_violation_count"].sum()),
        },
        "interpretation": {
            "primary": (
                "H/HeI operator closed; HeII->HeIII maintenance demand is "
                "positive while primary G3 source support is exactly zero."
            ),
            "hard_auditors": (
                "G3 operator and source support are active; full support is "
                "tested independently of the primary stellar source."
            ),
            "next_required_gate": (
                "Primary HeIII must be converted from static maintenance "
                "unknown to a decay/recombination variable before B2C2."
            ),
        },
        "forbidden_work_confirmed": [
            "unresolved sink subtraction",
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", type=Path, required=True)
    parser.add_argument("--spectrum-lock", type=Path, required=True)
    parser.add_argument("--b2c1a-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            run_stage(
                args.history,
                args.spectrum_lock,
                args.b2c1a_root,
                args.output,
            ),
            indent=2,
        )
    )
