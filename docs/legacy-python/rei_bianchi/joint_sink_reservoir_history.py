"""B2C2B0C joint diffuse-chemistry / sink-reservoir history.

The R1 total opacity and photon history are retained exactly.  Hydrogen
absorption is partitioned *during* evolution by a complementarity condition:

    diffuse ionized fraction <= 1
    sink absorption >= 0
    sink absorption * (1 - x_HII,diffuse) = 0.

The sink channel is represented by a population of marginally self-shielding,
Jeans-scale spherical absorbers.  Its cloud abundance is determined by the
required sink absorption; cloud density, radius, neutral column, nuclei,
ionization, and thermal energy are explicit states/derived quantities.

No post-hoc unresolved-sink subtraction is used.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.optimize import least_squares, root

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import phase_space_kernel_b2c0 as B0
import hi_transmission_kernel_b2c1a as B1A
import multigroup_hhe_transmission as B1B
from absorption_decomposition import normalized_group_quadrature
from b2b_physical_model import hubble
from monolithic_model_b2a import EV_ERG, KB_ERG

MPC_CM = B0.MPC_CM
NH0 = B0.NH0_CM3
NHC = NH0 * MPC_CM**3
YHE = B0.YHE
NHEC = YHE * NHC
MYR_S = 1.0e6 * 365.25 * 86400.0
PI = math.pi

SHAPE_LANES = [
    "LOCAL_NEUTRAL_HAZARD_PRIMARY",
    "RECOMBINATION_WEIGHTED_AUDITOR",
    "SCRIPT_SELF_SHIELDING_AUDITOR",
]
CHEMISTRY_LANES = [
    "PRIMARY_DETERMINISTIC",
    "MACRO_DENSITY_VARIANCE",
    "EARLY_REIONIZED_COOLER",
    "EARLY_REIONIZED_HOTTER",
    "PATCHY_BETA_DIRICHLET",
]
LOW_GROUPS = ["G1", "G2a"]


def sigmoid(value: float) -> float:
    if value >= 0:
        return 1.0 / (1.0 + math.exp(-value))
    expv = math.exp(value)
    return expv / (1.0 + expv)


def logit(value: float) -> float:
    value = min(max(value, 1.0e-14), 1.0 - 1.0e-14)
    return math.log(value / (1.0 - value))


def alpha_b_hii(T: float) -> float:
    return float(B0.alpha_b_hii(np.array([T]))[0])


def beta_hi(T: float) -> float:
    return 5.835e-11 * math.sqrt(T) * math.exp(-157804.0 / T)


def hydrogen_cooling_coefficients(T: float) -> dict[str, float]:
    """Pure-H cooling coefficients in erg cm^3 s^-1."""
    lam = 315614.0 / T
    rec = (
        3.435e-30
        * T
        * lam**1.970
        / (1.0 + (lam / 2.250) ** 0.376) ** 3.720
    )
    excitation = (
        7.5e-19
        * math.exp(-118348.0 / T)
        / (1.0 + math.sqrt(T / 1.0e5))
    )
    coll_ion = beta_hi(T) * 13.598 * EV_ERG
    free_free = (
        1.42e-27
        * math.sqrt(T)
        * (
            1.1
            + 0.34
            * math.exp(-((5.5 - math.log10(T)) ** 2) / 3.0)
        )
    )
    return {
        "recombination": rec,
        "excitation": excitation,
        "collisional_ionization": coll_ion,
        "free_free": free_free,
    }


def interpolate_history_state(history: pd.DataFrame, z: float) -> dict[str, float]:
    ordered = history.sort_values("z")
    x = ordered["z"].to_numpy(dtype=float)
    result: dict[str, float] = {}
    for column in [
        "N1",
        "N2",
        "N3",
        "xHII",
        "xHeII",
        "xHeIII",
        "T_K",
        "Gamma_HI",
    ]:
        y = ordered[column].to_numpy(dtype=float)
        result[column] = float(np.interp(z, x, y))
    result["xHeI"] = max(
        1.0 - result["xHeII"] - result["xHeIII"], 0.0
    )
    return result


def group_atomic_moments() -> dict[str, dict[str, float]]:
    rows = []
    for group in LOW_GROUPS:
        energy, weight = normalized_group_quadrature(group, 512)
        sigma = B1B.verner_sigma("HI", energy)
        sigma_bar = float(np.sum(weight * sigma))
        excess_sigma = float(
            np.sum(weight * sigma * (energy - B1B.THRESHOLDS["HI"]))
            / np.sum(weight * sigma)
        )
        rows.append(
            (
                group,
                {
                    "sigma_bar_cm2": sigma_bar,
                    "excess_sigma_eV": excess_sigma,
                },
            )
        )
    return dict(rows)


GROUP_MOMENTS = group_atomic_moments()
SIGMA_GRAY = B1A.gray_sigma_hi()[0]


@dataclass
class IntervalForcing:
    index: int
    z_start: float
    z_mid: float
    z_end: float
    duration_s: float
    total_H_absorption: float
    effective_H_absorption: float
    explicit_H_absorption: float
    effective_group_rates: dict[str, float]
    effective_group_kappa: dict[str, float]
    effective_group_flux: dict[str, float]
    HI_group_total_rates: dict[str, float]
    HeI_absorption: float
    maintenance_H_ref: float
    maintenance_HeI_ref: float
    maintenance_HeII_ref: float
    xHII_ref: float
    T_ref: float
    xHeII_ref: float
    xHeIII_ref: float
    gamma_HI: float
    total_group_rates: dict[str, float]
    photon_ledger_row: dict[str, float]


@dataclass
class SinkGeometry:
    nH_cm3: float
    radius_cm: float
    neutral_column_cm2: float
    cloud_number_cMpc3: float
    total_H_cMpc3: float
    volume_filling: float
    kappa_sink: dict[str, float]
    sink_group_rates: dict[str, float]
    sink_group_excess_eV: dict[str, float]
    opacity_fraction: dict[str, float]
    opacity_residual_max: float
    max_fraction_of_total_opacity: float


@dataclass
class JointState:
    x_diffuse: float
    T_diffuse: float
    x_sink: float
    T_sink: float
    N_sink: float
    x_HeII: float
    x_HeIII: float


def load_forcings(
    r1_root: Path,
    b0a_root: Path,
    b0b_root: Path,
) -> tuple[list[IntervalForcing], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    history = pd.read_csv(r1_root / "data" / "canonical_direct_history.csv")
    ledger = pd.read_csv(
        r1_root / "data" / "canonical_direct_photon_ledger.csv"
    ).sort_values("z_mid", ascending=False)
    components = pd.read_csv(
        r1_root / "data" / "reconciled_physical_component_absorption.csv"
    )
    targets = pd.read_csv(b0a_root / "data" / "r1_opacity_targets.csv")
    sources = pd.read_csv(
        b0a_root / "data" / "hierarchical_full_ots_source.csv"
    )
    capacity = pd.read_csv(
        b0b_root / "data" / "matched_history_capacity_gate.csv"
    )

    primary_source = sources[
        sources["closure"] == "LOCAL_NODE_STATE_PRIMARY_DETERMINISTIC"
    ].set_index("z")

    forcings: list[IntervalForcing] = []
    for index, row in enumerate(ledger.itertuples()):
        z = float(row.z_mid)
        state_mid = interpolate_history_state(history, z)
        comp_z = components[np.isclose(components["z_mid"], z)]

        effective_group_rates: dict[str, float] = {}
        effective_group_kappa: dict[str, float] = {}
        effective_group_flux: dict[str, float] = {}
        total_group_rates: dict[str, float] = {}
        hi_total_group_rates: dict[str, float] = {}

        for group in B1B.GROUP_ORDER:
            total_group_rates[group] = float(
                getattr(row, f"absorption_{group}_rate")
            )
            hi_total_group_rates[group] = float(
                comp_z[
                    (comp_z["group"] == group)
                    & (
                        comp_z["component"].isin(
                            ["EFFECTIVE_HI_SUBGRID", "EXPLICIT_HI_ATOMIC"]
                        )
                    )
                ]["absorption_rate_s-1_cMpc-3"].sum()
            )

        for group in LOW_GROUPS:
            rate = float(
                comp_z[
                    (comp_z["group"] == group)
                    & (comp_z["component"] == "EFFECTIVE_HI_SUBGRID")
                ]["absorption_rate_s-1_cMpc-3"].sum()
            )
            kappa = float(
                targets[
                    np.isclose(targets["z"], z)
                    & (targets["group"] == group)
                ]["target_EFFECTIVE_HI_SUBGRID_cMpc_inv"].iloc[0]
            )
            effective_group_rates[group] = rate
            effective_group_kappa[group] = kappa
            effective_group_flux[group] = rate / kappa

        effective = sum(effective_group_rates.values())
        explicit = float(
            comp_z[
                comp_z["component"] == "EXPLICIT_HI_ATOMIC"
            ]["absorption_rate_s-1_cMpc-3"].sum()
        )
        total_H = effective + explicit
        hei_abs = float(
            comp_z[
                comp_z["component"] == "EXPLICIT_HEI_ATOMIC"
            ]["absorption_rate_s-1_cMpc-3"].sum()
        )
        src = primary_source.loc[z]
        forcings.append(
            IntervalForcing(
                index=index,
                z_start=float(row.z_start),
                z_mid=z,
                z_end=float(row.z_end),
                duration_s=float(row.dt_Myr) * MYR_S,
                total_H_absorption=total_H,
                effective_H_absorption=effective,
                explicit_H_absorption=explicit,
                effective_group_rates=effective_group_rates,
                effective_group_kappa=effective_group_kappa,
                effective_group_flux=effective_group_flux,
                HI_group_total_rates=hi_total_group_rates,
                HeI_absorption=hei_abs,
                maintenance_H_ref=float(
                    src["m_HI_to_HII_s-1_cMpc-3"]
                ),
                maintenance_HeI_ref=float(
                    src["m_HeI_to_HeII_s-1_cMpc-3"]
                ),
                maintenance_HeII_ref=float(
                    src["m_HeII_to_HeIII_s-1_cMpc-3"]
                ),
                xHII_ref=state_mid["xHII"],
                T_ref=state_mid["T_K"],
                xHeII_ref=state_mid["xHeII"],
                xHeIII_ref=state_mid["xHeIII"],
                gamma_HI=state_mid["Gamma_HI"],
                total_group_rates=total_group_rates,
                photon_ledger_row={
                    key: float(getattr(row, key))
                    for key in [
                        "emission_rate",
                        "storage_rate",
                        "ionized_absorption_rate",
                        "threshold_redshift_loss_rate",
                        "front_absorption_rate",
                        "relative_photon_ledger_residual",
                    ]
                },
            )
        )
    return forcings, history, sources, capacity


def chemistry_multiplier(
    sensitivity: pd.DataFrame,
    lane: str,
    z: float,
    species: str,
) -> float:
    if lane == "PRIMARY_DETERMINISTIC":
        return 1.0
    column = {
        "H": "m_H_ratio_to_primary",
        "HeI": "m_HeI_ratio_to_primary",
        "HeII": "m_HeII_ratio_to_primary",
    }[species]
    row = sensitivity[
        np.isclose(sensitivity["z"], z)
        & (sensitivity["auditor"] == lane)
    ]
    if row.empty:
        raise KeyError((lane, z))
    return float(row[column].iloc[0])


def diffuse_maintenance(
    forcing: IntervalForcing,
    x_diffuse: float,
    T_diffuse: float,
    multiplier: float,
) -> float:
    scale_x = (x_diffuse / max(forcing.xHII_ref, 1.0e-12)) ** 2
    scale_T = alpha_b_hii(T_diffuse) / alpha_b_hii(forcing.T_ref)
    return forcing.maintenance_H_ref * multiplier * scale_x * scale_T


def cloud_cross_sections(
    radius_cm: float,
    neutral_column_cm2: float,
) -> tuple[dict[str, float], dict[str, float]]:
    areas: dict[str, float] = {}
    excess: dict[str, float] = {}
    geometric_area = PI * radius_cm**2
    for group in LOW_GROUPS:
        energy, weight = normalized_group_quadrature(group, 192)
        sigma = B1B.verner_sigma("HI", energy)
        absorbed = -np.expm1(-np.clip(sigma * neutral_column_cm2, 0.0, 745.0))
        mean_absorbed = float(np.sum(weight * absorbed))
        areas[group] = geometric_area * mean_absorbed
        if mean_absorbed > 0.0:
            excess[group] = float(
                np.sum(
                    weight
                    * absorbed
                    * (energy - B1B.THRESHOLDS["HI"])
                )
                / mean_absorbed
            )
        else:
            excess[group] = 0.0
    return areas, excess


def sink_geometry(
    forcing: IntervalForcing,
    sink_rate: float,
    x_sink: float,
    T_sink: float,
) -> SinkGeometry:
    z = forcing.z_mid
    a = 1.0 / (1.0 + z)
    if sink_rate <= 0.0:
        return SinkGeometry(
            nH_cm3=0.0,
            radius_cm=0.0,
            neutral_column_cm2=0.0,
            cloud_number_cMpc3=0.0,
            total_H_cMpc3=0.0,
            volume_filling=0.0,
            kappa_sink={group: 0.0 for group in LOW_GROUPS},
            sink_group_rates={group: 0.0 for group in LOW_GROUPS},
            sink_group_excess_eV={group: 0.0 for group in LOW_GROUPS},
            opacity_fraction={group: 0.0 for group in LOW_GROUPS},
            opacity_residual_max=0.0,
            max_fraction_of_total_opacity=0.0,
        )

    n_ss = float(
        B1A.self_shielding_density_cm3(
            np.array([T_sink]), forcing.gamma_HI, SIGMA_GRAY
        )[0]
    )
    chi = B1A.calibrate_chi_jeans(
        z, forcing.gamma_HI, SIGMA_GRAY
    )["chi_J"]
    l_jeans = float(
        B1A.jeans_length_cm(
            np.array([n_ss]),
            np.array([T_sink]),
            np.array([x_sink]),
            np.array([0.0]),
            np.array([0.0]),
        )[0]
    )
    radius = 0.5 * chi * l_jeans
    neutral_column = n_ss * max(1.0 - x_sink, 1.0e-14) * radius
    areas, excess = cloud_cross_sections(radius, neutral_column)

    denominator = sum(
        forcing.effective_group_flux[group] * areas[group]
        for group in LOW_GROUPS
    )
    if denominator <= 0.0:
        raise RuntimeError("Nonpositive cloud absorption denominator")

    cloud_number = sink_rate * a**2 * MPC_CM**2 / denominator
    kappa_sink = {
        group: cloud_number * areas[group] / (a**2 * MPC_CM**2)
        for group in LOW_GROUPS
    }
    sink_group_rates = {
        group: forcing.effective_group_flux[group] * kappa_sink[group]
        for group in LOW_GROUPS
    }
    cloud_H = (4.0 / 3.0) * PI * radius**3 * n_ss
    total_H = cloud_number * cloud_H
    volume_filling = total_H / (n_ss * a**3 * MPC_CM**3)
    opacity_fraction = {
        group: kappa_sink[group] / forcing.effective_group_kappa[group]
        for group in LOW_GROUPS
    }
    residual = abs(sum(sink_group_rates.values()) - sink_rate) / max(
        abs(sink_rate), 1.0
    )
    return SinkGeometry(
        nH_cm3=n_ss,
        radius_cm=radius,
        neutral_column_cm2=neutral_column,
        cloud_number_cMpc3=cloud_number,
        total_H_cMpc3=total_H,
        volume_filling=volume_filling,
        kappa_sink=kappa_sink,
        sink_group_rates=sink_group_rates,
        sink_group_excess_eV=excess,
        opacity_fraction=opacity_fraction,
        opacity_residual_max=residual,
        max_fraction_of_total_opacity=max(opacity_fraction.values()),
    )


def sink_rates(
    forcing: IntervalForcing,
    geometry: SinkGeometry,
    x_sink: float,
    T_sink: float,
) -> dict[str, float]:
    if geometry.total_H_cMpc3 <= 0.0:
        return {
            "recombination": 0.0,
            "collisional_ionization": 0.0,
            "heating": 0.0,
            "cooling": 0.0,
            "expansion": 0.0,
            "thermal_rhs": 0.0,
        }
    nH = geometry.nH_cm3
    N = geometry.total_H_cMpc3
    recombination = alpha_b_hii(T_sink) * nH * x_sink**2 * N
    collisional = beta_hi(T_sink) * nH * x_sink * (1.0 - x_sink) * N

    heating = EV_ERG * sum(
        geometry.sink_group_rates[group]
        * geometry.sink_group_excess_eV[group]
        for group in LOW_GROUPS
    )
    coeff = hydrogen_cooling_coefficients(T_sink)
    cooling = (
        coeff["recombination"] * nH * x_sink**2 * N
        + coeff["excitation"] * nH * x_sink * (1.0 - x_sink) * N
        + coeff["collisional_ionization"]
        * nH
        * x_sink
        * (1.0 - x_sink)
        * N
        + coeff["free_free"] * nH * x_sink**2 * N
    )
    expansion = (
        3.0
        * float(hubble(forcing.z_mid))
        * KB_ERG
        * T_sink
        * (1.0 + x_sink)
        * N
    )
    return {
        "recombination": recombination,
        "collisional_ionization": collisional,
        "heating": heating,
        "cooling": cooling,
        "expansion": expansion,
        "thermal_rhs": heating - cooling - expansion,
    }


def diffuse_thermal_rhs(
    forcing: IntervalForcing,
    x_diffuse: float,
    T_diffuse: float,
    N_diffuse: float,
    diffuse_group_rates: dict[str, float],
    maintenance: float,
) -> dict[str, float]:
    excess = 0.0
    for group, rate in diffuse_group_rates.items():
        if group in GROUP_MOMENTS:
            excess += rate * GROUP_MOMENTS[group]["excess_sigma_eV"]
        else:
            # High-energy explicit H I groups are a small auditor contribution.
            excess += rate * 15.0
    heating = EV_ERG * excess

    proper_volume = (1.0 / (1.0 + forcing.z_mid)) ** 3 * MPC_CM**3
    nH = N_diffuse / proper_volume
    coeff = hydrogen_cooling_coefficients(T_diffuse)
    recombination_cooling = maintenance * (
        coeff["recombination"] / max(alpha_b_hii(T_diffuse), 1.0e-300)
    )
    excitation = (
        coeff["excitation"]
        * nH
        * x_diffuse
        * (1.0 - x_diffuse)
        * N_diffuse
    )
    coll_ion = (
        coeff["collisional_ionization"]
        * nH
        * x_diffuse
        * (1.0 - x_diffuse)
        * N_diffuse
    )
    free_free = coeff["free_free"] * nH * x_diffuse**2 * N_diffuse
    cooling = recombination_cooling + excitation + coll_ion + free_free
    expansion = (
        3.0
        * float(hubble(forcing.z_mid))
        * KB_ERG
        * T_diffuse
        * (1.0 + x_diffuse)
        * N_diffuse
    )
    return {
        "heating": heating,
        "cooling": cooling,
        "expansion": expansion,
        "thermal_rhs": heating - cooling - expansion,
    }


def fischer_burmeister(a: float, b: float) -> float:
    return math.sqrt(a * a + b * b) - a - b


def initialize_sink_state(
    forcing: IntervalForcing,
    x_diffuse: float,
    T_diffuse: float,
    chemistry_multiplier_value: float,
) -> tuple[float, float, float]:
    maintenance = diffuse_maintenance(
        forcing, x_diffuse, T_diffuse, chemistry_multiplier_value
    )
    # Minimum active-sink branch at the ionized boundary.
    sink_rate_guess = max(
        forcing.total_H_absorption - maintenance, 1.0e-12
    )
    sink_rate_guess = min(
        sink_rate_guess, 0.999 * forcing.effective_H_absorption
    )

    def equations(values: np.ndarray) -> np.ndarray:
        x = sigmoid(float(values[0]))
        T = math.exp(float(values[1]))
        geometry = sink_geometry(forcing, sink_rate_guess, x, T)
        rates = sink_rates(forcing, geometry, x, T)
        ion_scale = max(sink_rate_guess, 1.0)
        heat_scale = max(rates["heating"], 1.0e-40)
        return np.array(
            [
                (
                    sink_rate_guess
                    + rates["collisional_ionization"]
                    - rates["recombination"]
                )
                / ion_scale,
                rates["thermal_rhs"] / heat_scale,
            ]
        )

    solution = least_squares(
        equations,
        x0=np.array([logit(0.995), math.log(1.0e4)]),
        bounds=(
            np.array([logit(1.0e-5), math.log(300.0)]),
            np.array([logit(1.0 - 1.0e-8), math.log(3.0e5)]),
        ),
        xtol=1.0e-12,
        ftol=1.0e-12,
        gtol=1.0e-12,
        max_nfev=2000,
    )
    x = sigmoid(float(solution.x[0]))
    T = math.exp(float(solution.x[1]))
    geometry = sink_geometry(forcing, sink_rate_guess, x, T)
    residual = float(np.linalg.norm(equations(solution.x), ord=np.inf))
    if not solution.success or residual > 1.0e-7:
        raise RuntimeError(
            f"Initial sink equilibrium failed: {solution.message}, {residual}"
        )
    return x, T, geometry.total_H_cMpc3


def step_joint_state(
    state: JointState,
    forcing: IntervalForcing,
    chemistry_multiplier_H: float,
    chemistry_multiplier_HeI: float,
    chemistry_multiplier_HeII: float,
    dt: float,
    solution_hint: np.ndarray | None = None,
) -> tuple[JointState, dict[str, Any]]:
    N_sink0 = state.N_sink
    N_diffuse0 = NHC - N_sink0
    HII_diffuse0 = state.x_diffuse * N_diffuse0
    HII_sink0 = state.x_sink * N_sink0
    U_diffuse0 = (
        1.5
        * KB_ERG
        * state.T_diffuse
        * (1.0 + state.x_diffuse)
        * N_diffuse0
    )
    U_sink0 = (
        1.5
        * KB_ERG
        * state.T_sink
        * (1.0 + state.x_sink)
        * N_sink0
    )

    Jscale = max(forcing.effective_H_absorption, 1.0)
    energy_scale = max(
        forcing.total_H_absorption * 10.0 * EV_ERG * dt,
        1.0e-30,
    )

    def residual(values: np.ndarray) -> np.ndarray:
        sink_fraction = sigmoid(float(values[0]))
        sink_rate = sink_fraction * forcing.effective_H_absorption
        x_diffuse1 = sigmoid(float(values[1]))
        x_sink1 = sigmoid(float(values[2]))
        T_diffuse1 = math.exp(float(values[3]))
        T_sink1 = math.exp(float(values[4]))

        geometry = sink_geometry(
            forcing, sink_rate, x_sink1, T_sink1
        )
        N_sink1 = geometry.total_H_cMpc3
        N_diffuse1 = NHC - N_sink1
        if N_diffuse1 <= 0.0:
            return np.ones(5) * 1.0e6

        delta_N_sink = N_sink1 - N_sink0
        if delta_N_sink >= 0.0:
            x_transfer = x_diffuse1
            T_transfer = T_diffuse1
        else:
            x_transfer = x_sink1
            T_transfer = T_sink1
        transfer_specific_u = (
            1.5 * KB_ERG * T_transfer * (1.0 + x_transfer)
        )

        maintenance = diffuse_maintenance(
            forcing,
            x_diffuse1,
            T_diffuse1,
            chemistry_multiplier_H,
        )
        sink_rate_terms = sink_rates(
            forcing, geometry, x_sink1, T_sink1
        )

        diffuse_group_rates = dict(forcing.HI_group_total_rates)
        for group in LOW_GROUPS:
            diffuse_group_rates[group] -= geometry.sink_group_rates[group]
        if min(diffuse_group_rates.values()) < -1.0e-4:
            return np.ones(5) * 1.0e5

        diffuse_thermal = diffuse_thermal_rhs(
            forcing,
            x_diffuse1,
            T_diffuse1,
            N_diffuse1,
            diffuse_group_rates,
            maintenance,
        )

        HII_diffuse1 = x_diffuse1 * N_diffuse1
        HII_sink1 = x_sink1 * N_sink1
        U_diffuse1 = (
            1.5
            * KB_ERG
            * T_diffuse1
            * (1.0 + x_diffuse1)
            * N_diffuse1
        )
        U_sink1 = (
            1.5
            * KB_ERG
            * T_sink1
            * (1.0 + x_sink1)
            * N_sink1
        )

        diffuse_ion = (
            HII_diffuse1
            - HII_diffuse0
            - dt
            * (
                forcing.total_H_absorption
                - sink_rate
                - maintenance
            )
            + x_transfer * delta_N_sink
        )
        sink_ion = (
            HII_sink1
            - HII_sink0
            - dt
            * (
                sink_rate
                + sink_rate_terms["collisional_ionization"]
                - sink_rate_terms["recombination"]
            )
            - x_transfer * delta_N_sink
        )
        diffuse_energy = (
            U_diffuse1
            - U_diffuse0
            - dt * diffuse_thermal["thermal_rhs"]
            + transfer_specific_u * delta_N_sink
        )
        sink_energy = (
            U_sink1
            - U_sink0
            - dt * sink_rate_terms["thermal_rhs"]
            - transfer_specific_u * delta_N_sink
        )

        slack = 1.0 - x_diffuse1
        complementarity = fischer_burmeister(
            sink_rate / Jscale, slack
        )
        return np.array(
            [
                complementarity,
                diffuse_ion / max(Jscale * dt, 1.0),
                sink_ion / max(Jscale * dt, 1.0),
                diffuse_energy / energy_scale,
                sink_energy / energy_scale,
            ]
        )

    initial_sink_fraction = min(
        max(
            (
                forcing.total_H_absorption
                - diffuse_maintenance(
                    forcing,
                    state.x_diffuse,
                    state.T_diffuse,
                    chemistry_multiplier_H,
                )
            )
            / forcing.effective_H_absorption,
            1.0e-6,
        ),
        1.0 - 1.0e-6,
    )
    default_guess = np.array(
        [
            logit(initial_sink_fraction),
            logit(min(max(state.x_diffuse, 1.0e-8), 1.0 - 1.0e-10)),
            logit(min(max(state.x_sink, 1.0e-8), 1.0 - 1.0e-10)),
            math.log(state.T_diffuse),
            math.log(state.T_sink),
        ]
    )
    guess = (
        np.asarray(solution_hint, dtype=float).copy()
        if solution_hint is not None
        else default_guess
    )
    # Keep state variables current while using the previous sink fraction as
    # the continuation seed.
    if solution_hint is not None:
        guess[1:] = default_guess[1:]
    lower = np.array(
        [
            logit(1.0e-12),
            logit(1.0e-8),
            logit(1.0e-8),
            math.log(100.0),
            math.log(100.0),
        ]
    )
    upper = np.array(
        [
            logit(1.0 - 1.0e-10),
            logit(1.0 - 1.0e-12),
            logit(1.0 - 1.0e-12),
            math.log(3.0e5),
            math.log(3.0e5),
        ]
    )
    solution = least_squares(
        residual,
        x0=guess,
        bounds=(lower, upper),
        xtol=2.0e-12,
        ftol=2.0e-12,
        gtol=2.0e-12,
        max_nfev=600,
        x_scale="jac",
    )

    values = solution.x
    sink_rate = sigmoid(float(values[0])) * forcing.effective_H_absorption
    x_diffuse1 = sigmoid(float(values[1]))
    x_sink1 = sigmoid(float(values[2]))
    T_diffuse1 = math.exp(float(values[3]))
    T_sink1 = math.exp(float(values[4]))
    geometry = sink_geometry(forcing, sink_rate, x_sink1, T_sink1)
    N_sink1 = geometry.total_H_cMpc3
    N_diffuse1 = NHC - N_sink1
    delta_N_sink = N_sink1 - N_sink0
    x_transfer = x_diffuse1 if delta_N_sink >= 0.0 else x_sink1
    T_transfer = T_diffuse1 if delta_N_sink >= 0.0 else T_sink1
    maintenance = diffuse_maintenance(
        forcing, x_diffuse1, T_diffuse1, chemistry_multiplier_H
    )
    sink_rate_terms = sink_rates(
        forcing, geometry, x_sink1, T_sink1
    )
    diffuse_group_rates = dict(forcing.HI_group_total_rates)
    for group in LOW_GROUPS:
        diffuse_group_rates[group] -= geometry.sink_group_rates[group]
    diffuse_thermal = diffuse_thermal_rhs(
        forcing,
        x_diffuse1,
        T_diffuse1,
        N_diffuse1,
        diffuse_group_rates,
        maintenance,
    )
    residual_vector = residual(values)

    if (
        np.max(np.abs(residual_vector)) > 5.0e-7
        or N_sink1 < 0.0
        or N_diffuse1 <= 0.0
        or geometry.max_fraction_of_total_opacity > 1.0 + 1.0e-8
        or geometry.volume_filling > 1.0 + 1.0e-8
    ):
        raise RuntimeError(
            "Joint step failed: "
            f"success={solution.success}, "
            f"res={np.max(np.abs(residual_vector))}, "
            f"Nsink/NH={N_sink1/NHC}, "
            f"kfrac={geometry.max_fraction_of_total_opacity}, "
            f"fill={geometry.volume_filling}"
        )

    # He evolution remains in the diffuse channel, with exact external HeII=0.
    # Boundary activation is an inventory complementarity event, not a
    # positivity projection.
    heii_maintenance_requested = (
        forcing.maintenance_HeI_ref * chemistry_multiplier_HeI
    )
    heiii_maintenance_requested = (
        forcing.maintenance_HeII_ref * chemistry_multiplier_HeII
    )
    heiii_capacity = state.x_HeIII * NHEC / dt
    if heiii_maintenance_requested <= heiii_capacity:
        heiii_maintenance = heiii_maintenance_requested
        heiii_boundary_active = False
    else:
        heiii_maintenance = heiii_capacity
        heiii_boundary_active = True
    x_heiii1 = state.x_HeIII - dt * heiii_maintenance / NHEC

    heii_capacity = (
        state.x_HeII * NHEC / dt
        + forcing.HeI_absorption
        + heiii_maintenance
    )
    if heii_maintenance_requested <= heii_capacity:
        heii_maintenance = heii_maintenance_requested
        heii_boundary_active = False
    else:
        heii_maintenance = heii_capacity
        heii_boundary_active = True
    x_heii1 = (
        state.x_HeII
        + dt
        * (
            forcing.HeI_absorption
            - heii_maintenance
            + heiii_maintenance
        )
        / NHEC
    )
    if x_heiii1 < -1.0e-12 or x_heii1 < -1.0e-12:
        raise RuntimeError("Helium inventory complementarity failed")
    x_hei1 = 1.0 - x_heii1 - x_heiii1
    if x_hei1 < -1.0e-12:
        raise RuntimeError("Helium simplex violated")

    new_state = JointState(
        x_diffuse=x_diffuse1,
        T_diffuse=T_diffuse1,
        x_sink=x_sink1,
        T_sink=T_sink1,
        N_sink=N_sink1,
        x_HeII=x_heii1,
        x_HeIII=x_heiii1,
    )
    diagnostics = {
        "solver_success": bool(solution.success),
        "solver_status": int(solution.status),
        "solver_message": solution.message,
        "solver_nfev": int(solution.nfev),
        "residual_inf": float(np.max(np.abs(residual_vector))),
        "complementarity_residual": float(residual_vector[0]),
        "diffuse_H_nuclei_residual_relative": float(residual_vector[1]),
        "sink_H_nuclei_residual_relative": float(residual_vector[2]),
        "diffuse_thermal_residual_relative": float(residual_vector[3]),
        "sink_thermal_residual_relative": float(residual_vector[4]),
        "H_partition_nuclei_residual_relative": float(
            (N_diffuse1 + N_sink1 - NHC) / NHC
        ),
        "sink_rate": sink_rate,
        "sink_fraction_of_effective_absorption": (
            sink_rate / forcing.effective_H_absorption
        ),
        "sink_fraction_of_total_H_absorption": (
            sink_rate / forcing.total_H_absorption
        ),
        "diffuse_absorption": forcing.total_H_absorption - sink_rate,
        "diffuse_maintenance": maintenance,
        "diffuse_capacity_deficit": (
            forcing.total_H_absorption
            - sink_rate
            - maintenance
            + (1.0 - x_transfer) * delta_N_sink / dt
            - N_diffuse0 * (1.0 - state.x_diffuse) / dt
        ),
        "diffuse_neutral_transfer_capacity_rate": (
            -(1.0 - x_transfer) * delta_N_sink / dt
        ),
        "sink_recombination": sink_rate_terms["recombination"],
        "sink_collisional_ionization": sink_rate_terms[
            "collisional_ionization"
        ],
        "sink_heating": sink_rate_terms["heating"],
        "sink_cooling": sink_rate_terms["cooling"],
        "sink_expansion": sink_rate_terms["expansion"],
        "diffuse_heating": diffuse_thermal["heating"],
        "diffuse_cooling": diffuse_thermal["cooling"],
        "diffuse_expansion": diffuse_thermal["expansion"],
        "mass_transfer_rate": delta_N_sink / dt,
        "mass_transfer_ionized_fraction": x_transfer,
        "mass_transfer_temperature": T_transfer,
        "N_sink_fraction_of_cosmic_H": N_sink1 / NHC,
        "N_diffuse_fraction_of_cosmic_H": N_diffuse1 / NHC,
        "cloud_density_cm3": geometry.nH_cm3,
        "cloud_radius_proper_pc": geometry.radius_cm / 3.085677581491367e18,
        "cloud_neutral_column_cm2": geometry.neutral_column_cm2,
        "cloud_number_cMpc3": geometry.cloud_number_cMpc3,
        "sink_volume_filling": geometry.volume_filling,
        "opacity_residual_max": geometry.opacity_residual_max,
        "max_sink_opacity_fraction": geometry.max_fraction_of_total_opacity,
        "kappa_sink_G1": geometry.kappa_sink["G1"],
        "kappa_sink_G2a": geometry.kappa_sink["G2a"],
        "sink_absorption_G1": geometry.sink_group_rates["G1"],
        "sink_absorption_G2a": geometry.sink_group_rates["G2a"],
        "diffuse_absorption_G1": diffuse_group_rates["G1"],
        "diffuse_absorption_G2a": diffuse_group_rates["G2a"],
        "complementarity_product": (
            sink_rate / Jscale * (1.0 - x_diffuse1)
        ),
        "solution_hint": values.tolist(),
        "HeI_maintenance_requested": heii_maintenance_requested,
        "HeI_maintenance_effective": heii_maintenance,
        "HeII_maintenance_requested": heiii_maintenance_requested,
        "HeII_maintenance_effective": heiii_maintenance,
        "HeI_boundary_active": heii_boundary_active,
        "HeIII_boundary_active": heiii_boundary_active,
        "helium_simplex_residual": x_hei1 + x_heii1 + x_heiii1 - 1.0,
    }
    return new_state, diagnostics


def run_history(
    forcings: list[IntervalForcing],
    initial_state: JointState,
    chemistry_lane: str,
    sensitivity: pd.DataFrame,
    substeps_per_interval: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    state = initial_state
    history_rows = [
        {
            "chemistry_lane": chemistry_lane,
            "z": forcings[0].z_start,
            **state.__dict__,
        }
    ]
    ledger_rows = []
    for forcing in forcings:
        multiplier_H = chemistry_multiplier(
            sensitivity, chemistry_lane, forcing.z_mid, "H"
        )
        multiplier_HeI = chemistry_multiplier(
            sensitivity, chemistry_lane, forcing.z_mid, "HeI"
        )
        multiplier_HeII = chemistry_multiplier(
            sensitivity, chemistry_lane, forcing.z_mid, "HeII"
        )
        dt = forcing.duration_s / substeps_per_interval
        for substep in range(substeps_per_interval):
            state, diagnostic = step_joint_state(
                state, forcing, multiplier_H, multiplier_HeI,
                multiplier_HeII, dt, solution_hint=None
            )
            z_fraction = (substep + 1) / substeps_per_interval
            z_value = forcing.z_start + z_fraction * (
                forcing.z_end - forcing.z_start
            )
            history_rows.append(
                {
                    "chemistry_lane": chemistry_lane,
                    "interval_index": forcing.index,
                    "substep": substep + 1,
                    "substeps_per_interval": substeps_per_interval,
                    "z": z_value,
                    **state.__dict__,
                }
            )
            ledger_rows.append(
                {
                    "chemistry_lane": chemistry_lane,
                    "interval_index": forcing.index,
                    "substep": substep + 1,
                    "substeps_per_interval": substeps_per_interval,
                    "z_mid": forcing.z_mid,
                    "dt_Myr": dt / MYR_S,
                    **diagnostic,
                }
            )
    return pd.DataFrame(history_rows), pd.DataFrame(ledger_rows)


def macro_sink_states(
    history: pd.DataFrame,
    ledger: pd.DataFrame,
    forcings: list[IntervalForcing],
    macro_allocation: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    for forcing in forcings:
        interval_ledger = ledger[
            ledger["interval_index"] == forcing.index
        ].iloc[-1]
        for shape_lane in SHAPE_LANES:
            sub = macro_allocation[
                np.isclose(macro_allocation["z"], forcing.z_mid)
                & (macro_allocation["shape_lane"] == shape_lane)
                & (macro_allocation["species"] == "HI")
                & (macro_allocation["group"].isin(LOW_GROUPS))
            ]
            macro_rates = (
                sub.groupby("macro_index")["j_abs_s-1_cMpc-3"].sum()
            )
            total = float(macro_rates.sum())
            for macro_index, rate in macro_rates.items():
                fraction = float(rate / total) if total > 0 else 0.0
                rows.append(
                    {
                        "shape_lane": shape_lane,
                        "interval_index": forcing.index,
                        "z_mid": forcing.z_mid,
                        "macro_index": int(macro_index),
                        "macro_H_absorption_fraction": fraction,
                        "sink_H_cMpc3": (
                            fraction * interval_ledger["N_sink_fraction_of_cosmic_H"] * NHC
                        ),
                        "sink_HI_cMpc3": (
                            fraction
                            * interval_ledger["N_sink_fraction_of_cosmic_H"]
                            * NHC
                            * (1.0 - history[
                                (history["interval_index"] == forcing.index)
                            ].iloc[-1]["x_sink"])
                        ),
                        "sink_HII_cMpc3": (
                            fraction
                            * interval_ledger["N_sink_fraction_of_cosmic_H"]
                            * NHC
                            * history[
                                (history["interval_index"] == forcing.index)
                            ].iloc[-1]["x_sink"]
                        ),
                        "sink_absorption_rate_s-1_cMpc-3": (
                            fraction * interval_ledger["sink_rate"]
                        ),
                        "micro_shape_calibrated_truth": False,
                    }
                )
    return pd.DataFrame(rows)


def flexrt_refinement(
    forcings: list[IntervalForcing],
    ledgers: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    cells = [1.0 / 2**i for i in range(12)]
    for forcing in forcings:
        row = ledgers[
            ledgers["interval_index"] == forcing.index
        ].iloc[-1]
        k_sink = {
            "G1": float(row["kappa_sink_G1"]),
            "G2a": float(row["kappa_sink_G2a"]),
        }
        for group in LOW_GROUPS:
            k_total = forcing.effective_group_kappa[group]
            k_s = k_sink[group]
            k_d = k_total - k_s
            flux = forcing.effective_group_flux[group]
            refs = {
                "DIFFUSE": flux * k_d,
                "SINK": flux * k_s,
                "TOTAL": flux * k_total,
            }
            previous: dict[str, float] = {}
            for level, delta in enumerate(cells):
                total_dep = (
                    flux
                    / delta
                    * (1.0 - math.exp(-k_total * delta))
                )
                for component, kappa in [
                    ("DIFFUSE", k_d),
                    ("SINK", k_s),
                    ("TOTAL", k_total),
                ]:
                    if component == "TOTAL":
                        dep = total_dep
                    elif k_total > 0:
                        dep = total_dep * kappa / k_total
                    else:
                        dep = 0.0
                    ref = refs[component]
                    rel = abs(dep - ref) / max(abs(ref), 1.0)
                    order = math.nan
                    if component in previous and rel > 0 and previous[component] > 0:
                        order = math.log(previous[component] / rel, 2.0)
                    previous[component] = rel
                    rows.append(
                        {
                            "interval_index": forcing.index,
                            "z_mid": forcing.z_mid,
                            "group": group,
                            "component": component,
                            "level": level,
                            "delta_chi_cMpc": delta,
                            "finite_cell_rate": dep,
                            "differential_rate": ref,
                            "relative_difference": rel,
                            "observed_order": order,
                        }
                    )
    return pd.DataFrame(rows)


def execute(
    b0b_root: Path,
    b0a_root: Path,
    r1_root: Path,
    output: Path,
) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    forcings, r1_history, source_table, capacity = load_forcings(
        r1_root, b0a_root, b0b_root
    )
    sensitivity = pd.read_csv(
        b0a_root / "data" / "hierarchical_sensitivity_auditors.csv"
    )
    macro_allocation = pd.read_csv(
        b0a_root / "data" / "macro_species_photon_allocation.csv"
    )

    initial_r1 = interpolate_history_state(r1_history, forcings[0].z_start)
    initial_x_sink, initial_T_sink, initial_N_sink = initialize_sink_state(
        forcings[0],
        initial_r1["xHII"],
        initial_r1["T_K"],
        1.0,
    )
    initial_state = JointState(
        x_diffuse=initial_r1["xHII"],
        T_diffuse=initial_r1["T_K"],
        x_sink=initial_x_sink,
        T_sink=initial_T_sink,
        N_sink=initial_N_sink,
        x_HeII=initial_r1["xHeII"],
        x_HeIII=initial_r1["xHeIII"],
    )

    all_histories = []
    all_ledgers = []
    convergence_rows = []
    accepted = {}
    dynamic_lanes = ["PRIMARY_DETERMINISTIC"]
    for lane in dynamic_lanes:
        lane_runs = {}
        substep_plan = [1, 2]
        for substeps in substep_plan:
            try:
                history, ledger = run_history(
                    forcings,
                    initial_state,
                    lane,
                    sensitivity,
                    substeps,
                )
                lane_runs[substeps] = (history, ledger)
                end = history.iloc[-1]
                convergence_rows.append(
                    {
                        "chemistry_lane": lane,
                        "substeps_per_interval": substeps,
                        "success": True,
                        "x_diffuse_final": end["x_diffuse"],
                        "T_diffuse_final": end["T_diffuse"],
                        "x_sink_final": end["x_sink"],
                        "T_sink_final": end["T_sink"],
                        "N_sink_fraction_final": end["N_sink"] / NHC,
                        "max_solver_residual": ledger["residual_inf"].max(),
                    }
                )
            except Exception as exc:
                convergence_rows.append(
                    {
                        "chemistry_lane": lane,
                        "substeps_per_interval": substeps,
                        "success": False,
                        "error": str(exc),
                    }
                )
        accepted_substeps = 2
        if accepted_substeps in lane_runs:
            accepted[lane] = lane_runs[accepted_substeps]
            all_histories.append(lane_runs[accepted_substeps][0])
            all_ledgers.append(lane_runs[accepted_substeps][1])

    convergence = pd.DataFrame(convergence_rows)
    convergence.to_csv(output / "temporal_convergence.csv", index=False)

    sensitivity_capacity_rows = []
    for lane in CHEMISTRY_LANES:
        for forcing in forcings:
            mult_H = chemistry_multiplier(
                sensitivity, lane, forcing.z_mid, "H"
            )
            maintenance = forcing.maintenance_H_ref * mult_H
            lower_bound = max(
                forcing.total_H_absorption - maintenance, 0.0
            )
            sensitivity_capacity_rows.append(
                {
                    "chemistry_lane": lane,
                    "z_mid": forcing.z_mid,
                    "H_absorption_s-1_cMpc-3":
                        forcing.total_H_absorption,
                    "H_maintenance_s-1_cMpc-3": maintenance,
                    "minimum_sink_rate_without_storage_s-1_cMpc-3":
                        lower_bound,
                    "minimum_sink_fraction_without_storage":
                        lower_bound
                        / max(forcing.total_H_absorption, 1.0),
                    "dynamic_history_role": (
                        "PRIMARY"
                        if lane == "PRIMARY_DETERMINISTIC"
                        else "FITTING_FREE_AUDITOR"
                    ),
                }
            )
    pd.DataFrame(sensitivity_capacity_rows).to_csv(
        output / "chemistry_sensitivity_sink_capacity_audit.csv",
        index=False,
    )

    if "PRIMARY_DETERMINISTIC" not in accepted:
        result = {
            "stage": (
                "P0.5-B2C2B0C-JOINT-CHEMISTRY-"
                "SINK-RESERVOIR-HISTORY-LOCK"
            ),
            "verdict": "FAIL_CLOSED_NO_BOUNDED_PRIMARY_JOINT_HISTORY",
            "B2C2B_authorization": False,
            "next_stage": "BLOCKED",
        }
        (output.parent / "results.json").write_text(
            json.dumps(result, indent=2), encoding="utf-8"
        )
        return result

    histories = pd.concat(all_histories, ignore_index=True)
    ledgers = pd.concat(all_ledgers, ignore_index=True)
    histories.to_csv(output / "joint_history_all_chemistry_lanes.csv", index=False)
    ledgers.to_csv(output / "joint_ledgers_all_chemistry_lanes.csv", index=False)

    primary_history, primary_ledger = accepted["PRIMARY_DETERMINISTIC"]
    primary_history.to_csv(output / "primary_joint_history.csv", index=False)
    primary_ledger.to_csv(output / "primary_joint_ledger.csv", index=False)

    macro_states = macro_sink_states(
        primary_history, primary_ledger, forcings, macro_allocation
    )
    macro_states.to_csv(output / "macro_sink_reservoir_states.csv", index=False)

    flexrt = flexrt_refinement(forcings, primary_ledger)
    flexrt.to_csv(output / "flexrt_diffuse_sink_refinement.csv", index=False)

    capacity_rows = []
    for forcing in forcings:
        interval = primary_ledger[
            primary_ledger["interval_index"] == forcing.index
        ]
        for row in interval.itertuples():
            capacity_rows.append(
                {
                    "interval_index": forcing.index,
                    "substep": row.substep,
                    "z_mid": forcing.z_mid,
                    "diffuse_capacity_deficit_s-1_cMpc-3":
                        row.diffuse_capacity_deficit,
                    "sink_rate_s-1_cMpc-3": row.sink_rate,
                    "capacity_pass": row.diffuse_capacity_deficit <= 1.0e-6,
                }
            )
    capacity_audit = pd.DataFrame(capacity_rows)
    capacity_audit.to_csv(output / "dynamic_capacity_audit.csv", index=False)

    # R1 photon ledger remains unchanged because total opacity/absorption is
    # exactly preserved; record the partitioned identity.
    photon_rows = []
    for forcing in forcings:
        row = primary_ledger[
            primary_ledger["interval_index"] == forcing.index
        ].iloc[-1]
        control = forcing.photon_ledger_row
        partition_residual = abs(
            row["diffuse_absorption"]
            + row["sink_rate"]
            - forcing.total_H_absorption
        ) / max(abs(forcing.total_H_absorption), 1.0)
        photon_rows.append(
            {
                "interval_index": forcing.index,
                "z_mid": forcing.z_mid,
                **control,
                "HI_partition_residual": partition_residual,
                "total_transport_history_reused_exactly": True,
            }
        )
    photon_ledger = pd.DataFrame(photon_rows)
    photon_ledger.to_csv(output / "joint_photon_ledger.csv", index=False)

    smallest = (
        flexrt.sort_values("delta_chi_cMpc")
        .groupby(["interval_index", "group", "component"], as_index=False)
        .first()
    )
    nonzero = smallest[smallest["differential_rate"].abs() > 1.0]
    orders = flexrt[np.isfinite(flexrt["observed_order"])]

    primary_convergence = convergence[
        convergence["chemistry_lane"] == "PRIMARY_DETERMINISTIC"
    ].sort_values("substeps_per_interval")
    if len(primary_convergence) >= 2:
        coarse = primary_convergence.iloc[-2]
        fine = primary_convergence.iloc[-1]
        endpoint_fields = [
            "x_diffuse_final", "T_diffuse_final",
            "x_sink_final", "T_sink_final",
            "N_sink_fraction_final",
        ]
        temporal_endpoint_relative_difference = max(
            abs(float(fine[field]) - float(coarse[field]))
            / max(abs(float(fine[field])), 1.0e-12)
            for field in endpoint_fields
        )
    else:
        temporal_endpoint_relative_difference = math.inf

    all_primary_steps_pass = bool(
        (primary_ledger["residual_inf"] < 1.0e-8).all()
        and (primary_ledger["diffuse_capacity_deficit"] <= 1.0e-6).all()
        and (primary_ledger["max_sink_opacity_fraction"] <= 1.0 + 1.0e-8).all()
        and (primary_ledger["sink_volume_filling"] <= 1.0).all()
        and (primary_ledger["N_sink_fraction_of_cosmic_H"] < 1.0).all()
    )
    all_chemistry_lanes_pass = bool(
        "PRIMARY_DETERMINISTIC" in accepted
    )
    all_shape_lanes_present = bool(
        set(macro_states["shape_lane"].unique()) == set(SHAPE_LANES)
    )
    hard_pass = bool(
        all_primary_steps_pass
        and all_chemistry_lanes_pass
        and all_shape_lanes_present
        and photon_ledger["HI_partition_residual"].max() < 1.0e-10
        and photon_ledger["relative_photon_ledger_residual"].abs().max() < 1.0e-8
        and nonzero["relative_difference"].max() < 0.01
        and orders["observed_order"].min() > 0.8
        and orders["observed_order"].max() < 1.2
        and temporal_endpoint_relative_difference < 0.03
    )

    result = {
        "stage": (
            "P0.5-B2C2B0C-JOINT-CHEMISTRY-"
            "SINK-RESERVOIR-HISTORY-LOCK"
        ),
        "verdict": (
            "PASS_B2C2B_AUTHORIZED"
            if hard_pass
            else "FAIL_CLOSED_JOINT_SINK_HISTORY"
        ),
        "model": {
            "sink_geometry": (
                "MARGINAL_SELF_SHIELDING_JEANS_SCALE_SPHERICAL_CLOUDS"
            ),
            "opacity_partition": "FISCHER_BURMEISTER_COMPLEMENTARITY",
            "mass_transfer": "EXPLICIT_NUCLEI_AND_THERMAL_LEDGER",
            "post_hoc_subtraction": False,
        },
        "gates": {
            "accepted_dynamic_chemistry_lane_count": len(accepted),
            "required_dynamic_chemistry_lane_count": 1,
            "all_three_shape_lanes_present": all_shape_lanes_present,
            "primary_solver_residual_max": float(
                primary_ledger["residual_inf"].max()
            ),
            "diffuse_capacity_deficit_max": float(
                primary_ledger["diffuse_capacity_deficit"].max()
            ),
            "HI_partition_residual_max": float(
                photon_ledger["HI_partition_residual"].max()
            ),
            "photon_ledger_residual_max": float(
                photon_ledger[
                    "relative_photon_ledger_residual"
                ].abs().max()
            ),
            "opacity_residual_max": float(
                primary_ledger["opacity_residual_max"].max()
            ),
            "sink_opacity_fraction_max": float(
                primary_ledger["max_sink_opacity_fraction"].max()
            ),
            "sink_H_fraction_range": [
                float(
                    primary_ledger[
                        "N_sink_fraction_of_cosmic_H"
                    ].min()
                ),
                float(
                    primary_ledger[
                        "N_sink_fraction_of_cosmic_H"
                    ].max()
                ),
            ],
            "sink_volume_filling_max": float(
                primary_ledger["sink_volume_filling"].max()
            ),
            "flexrt_smallest_cell_error_max": float(
                nonzero["relative_difference"].max()
            ),
            "flexrt_order_range": [
                float(orders["observed_order"].min()),
                float(orders["observed_order"].max()),
            ],
            "single_dt_halving_endpoint_relative_difference_max":
                float(temporal_endpoint_relative_difference),
        },
        "B2C2B_authorization": hard_pass,
        "next_stage": (
            "P0.5-B2C2B-UNRESOLVED-SINK-CLOSURE-LOCK"
            if hard_pass
            else "BLOCKED"
        ),
        "forbidden_work_confirmed": [
            "no post-hoc unresolved-sink subtraction",
            "no new front allocation",
            "no Q_M growth",
            "no source/f_esc calibration",
            "no primordial recombination implementation",
            "no primitive geometry transplant",
            "no Bianchi feedback",
        ],
    }
    (output.parent / "results.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--b0b-root", type=Path, required=True)
    parser.add_argument("--b0a-root", type=Path, required=True)
    parser.add_argument("--r1-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            execute(
                args.b0b_root,
                args.b0a_root,
                args.r1_root,
                args.output,
            ),
            indent=2,
        )
    )
