#!/usr/bin/env python3
"""Build the R1B-R2A photon-owner split preflight evidence.

This stage does not integrate chemistry.  It separates the canonical total
absorption into mutually exclusive opacity owners, proves exact photon closure,
checks material-capacity necessity under time refinement, and audits node/macro
disintegration without selecting a historical subgrid prior post hoc.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import PchipInterpolator

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from owner_split_operator import (  # noqa: E402
    COMPONENT_OWNER,
    capacity_certificate,
    condition_component_opacities,
    disintegrate_owner_current,
    resolved_source_coefficients,
    split_group_by_owner,
)

GROUPS = ("G1", "G2a", "G2b", "G3")
COMPONENTS = tuple(COMPONENT_OWNER)
RESOLVED_COMPONENT_SPECIES = {
    "EXPLICIT_HI_ATOMIC": "HI",
    "EXPLICIT_HEI_ATOMIC": "HeI",
    "EXPLICIT_HEII_ATOMIC": "HeII",
}
SUBGRID_LANES = (
    "LOCAL_NEUTRAL_HAZARD_PRIMARY",
    "RECOMBINATION_WEIGHTED_AUDITOR",
    "SCRIPT_SELF_SHIELDING_AUDITOR",
)
NH0_CM3 = 1.88e-7
YHE = 0.079
MPC_CM = 3.085677581491367e24
KPC_CM = 3.0856775814913673e21
H_SMALL = 0.68


def rel(a: float, b: float, floor: float = 1.0e-300) -> float:
    return abs(float(a) - float(b)) / max(abs(float(b)), floor)


def sha_array(array: np.ndarray) -> str:
    payload = np.ascontiguousarray(np.asarray(array, dtype="<f8")).tobytes()
    return hashlib.sha256(payload).hexdigest()


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_canonical_source(source_dir: Path) -> tuple[Any, Any]:
    sys.path.insert(0, str(source_dir))
    gamma = __import__("gamma_conditioned_reconciliation")
    absorption = __import__("absorption_decomposition")
    return gamma, absorption


def integrate_positive_pchip(
    fraction: np.ndarray,
    values: np.ndarray,
    left: float,
    right: float,
    *,
    order: int = 64,
) -> float:
    x = np.asarray(fraction, dtype=float)
    y = np.asarray(values, dtype=float)
    if np.any(~np.isfinite(y)) or np.any(y < 0.0):
        raise ValueError("non-finite or negative forcing values")
    if np.all(y == 0.0):
        return 0.0
    pchip = PchipInterpolator(x, y, extrapolate=False)
    # PCHIP is shape preserving on every data interval, so non-negative node
    # values define a non-negative interpolant.  Use its exact piecewise-cubic
    # antiderivative rather than a quadrature whose error changes when an
    # interval is subdivided.
    integral = float(pchip.integrate(left, right))
    scale = max(float(np.max(y)) * max(right - left, 1.0e-300), 1.0)
    if integral < -1.0e-14 * scale:
        raise ValueError("positive forcing interpolation has negative integral")
    if integral < 0.0:
        raise ValueError("negative interpolation integral; clipping forbidden")
    return integral


def build_time_resolved_owner_split(
    *,
    forcing: pd.DataFrame,
    public: pd.DataFrame,
    raw_path: Path,
    density_path: Path,
    source_dir: Path,
    output: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    gamma_mod, absorption_mod = load_canonical_source(source_dir)
    response_cache: dict[int, Any] = {}
    quadrature = {
        group: absorption_mod.normalized_group_quadrature(group, 144)
        for group in GROUPS
    }
    rows: list[dict[str, Any]] = []
    audits: list[dict[str, Any]] = []

    ordered = forcing.sort_values(["interval_index", "node_index"])
    for rec in ordered.to_dict(orient="records"):
        interval = int(rec["interval_index"])
        if interval not in response_cache:
            response_cache[interval] = gamma_mod.ResponseAnchoredOpacity(
                public=public,
                raw_path=raw_path,
                density_path=density_path,
                z=float(rec["z_mid"]),
                direct_nodes=144,
            )
        response = response_cache[interval]
        gamma12 = float(rec["Gamma_HI_s-1"]) / 1.0e-12
        response.check_gamma(gamma12)
        evaluator = response.conditioned_energy_evaluator(gamma12)
        state = {
            "xHII": float(rec["xHII"]),
            "xHeI": float(rec["xHeI"]),
            "xHeII": float(rec["xHeII"]),
        }
        params = {"z_cos": float(rec["z_mid"])}

        for group in GROUPS:
            energy, weights = quadrature[group]
            arrays = absorption_mod.component_energy_arrays(
                state, params, group, energy, evaluator
            )
            raw_component = {
                name: float(np.dot(weights, np.asarray(arrays[name], dtype=float)))
                for name in COMPONENTS
            }
            raw_sum = math.fsum(raw_component.values())
            authoritative_kappa = float(rec[f"kappa_{group}_cMpc-1"])
            authoritative_current = float(rec[f"absorption_{group}_s-1_cMpc-3"])
            conditioned = condition_component_opacities(
                authoritative_total_kappa=authoritative_kappa,
                raw_component_kappa=raw_component,
            )
            owner_rows = split_group_by_owner(
                total_kappa=authoritative_kappa,
                total_current=authoritative_current,
                component_kappa=conditioned,
                relative_tolerance=1.0e-12,
            )
            phi = authoritative_current / authoritative_kappa if authoritative_kappa > 0.0 else 0.0
            for owner_row in owner_rows:
                source = resolved_source_coefficients(owner_row.component)
                rows.append(
                    {
                        "interval_index": interval,
                        "node_index": int(rec["node_index"]),
                        "node_count": int(rec["node_count"]),
                        "fraction": float(rec["fraction"]),
                        "time_s": float(rec["time_s"]),
                        "weight": float(rec["weight"]),
                        "z_start": float(rec["z_start"]),
                        "z_mid": float(rec["z_mid"]),
                        "z_end": float(rec["z_end"]),
                        "group": group,
                        "component": owner_row.component,
                        "owner": owner_row.owner,
                        "raw_component_kappa_cMpc_inv": raw_component[owner_row.component],
                        "raw_component_fraction": (
                            raw_component[owner_row.component] / raw_sum if raw_sum > 0.0 else 0.0
                        ),
                        "conditioned_component_kappa_cMpc_inv": owner_row.kappa,
                        "conditioned_component_fraction": owner_row.fraction,
                        "owner_absorption_rate_s-1_cMpc-3": owner_row.current,
                        "authoritative_total_kappa_cMpc_inv": authoritative_kappa,
                        "authoritative_total_absorption_rate_s-1_cMpc-3": authoritative_current,
                        "common_incident_flux_s-1_cMpc-2": phi,
                        "resolved_H_source_coefficient": source["resolved_H"],
                        "resolved_He_source_coefficient": source["resolved_He"],
                        "resolved_thermal_source_coefficient": source["resolved_thermal"],
                    }
                )
            ksum = math.fsum(r.kappa for r in owner_rows)
            jsum = math.fsum(r.current for r in owner_rows)
            audits.append(
                {
                    "interval_index": interval,
                    "node_index": int(rec["node_index"]),
                    "fraction": float(rec["fraction"]),
                    "z_mid": float(rec["z_mid"]),
                    "group": group,
                    "raw_component_sum_kappa_cMpc_inv": raw_sum,
                    "authoritative_total_kappa_cMpc_inv": authoritative_kappa,
                    "raw_sum_vs_authoritative_relative_residual": rel(raw_sum, authoritative_kappa),
                    "conditioned_kappa_sum_relative_residual": rel(ksum, authoritative_kappa),
                    "conditioned_current_sum_relative_residual": rel(jsum, authoritative_current) if authoritative_current != 0.0 else abs(jsum),
                    "minimum_component_kappa_cMpc_inv": min(r.kappa for r in owner_rows),
                    "minimum_component_current_s-1_cMpc-3": min(r.current for r in owner_rows),
                    "exact_zero_G3_current": bool(group != "G3" or authoritative_current == 0.0),
                }
            )

    split = pd.DataFrame(rows)
    audit = pd.DataFrame(audits)
    split.to_csv(output / "time_resolved_owner_split.csv", index=False)
    audit.to_csv(output / "owner_group_closure_audit.csv", index=False)

    reference_path = output.parent / "inputs" / "upstream" / "reconciled_physical_component_absorption.csv"
    reference = pd.read_csv(reference_path)
    average_rows: list[dict[str, Any]] = []
    for (interval, group, component), sub in split.groupby(
        ["interval_index", "group", "component"], sort=True
    ):
        average = float(np.dot(sub["weight"], sub["owner_absorption_rate_s-1_cMpc-3"]))
        ref = reference[
            (reference["interval_index"] == interval)
            & (reference["group"] == group)
            & (reference["component"] == component)
        ]
        reference_rate = float(ref.iloc[0]["absorption_rate_s-1_cMpc-3"])
        average_rows.append(
            {
                "interval_index": int(interval),
                "z_mid": float(sub.iloc[0]["z_mid"]),
                "group": group,
                "component": component,
                "conditioned_quadrature_average_rate_s-1_cMpc-3": average,
                "canonical_component_average_rate_s-1_cMpc-3": reference_rate,
                "relative_difference": rel(average, reference_rate) if reference_rate != 0.0 else abs(average),
                "load_bearing": False,
                "interpretation": "AUDITOR_ONLY_CONDITIONAL_RESPLIT_VS_CANONICAL_INTERVAL_COMPONENT_DECOMPOSITION",
            }
        )
    comparison = pd.DataFrame(average_rows)
    comparison.to_csv(output / "interval_component_average_comparison.csv", index=False)
    return split, audit, comparison


def owner_rate_interpolators(split: pd.DataFrame, interval: int) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    sub = split[split["interval_index"] == interval]
    fraction = np.sort(sub["fraction"].unique())
    out: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for owner in sorted(sub["owner"].unique()):
        values = []
        for x in fraction:
            values.append(
                float(
                    sub[(sub["fraction"] == x) & (sub["owner"] == owner)][
                        "owner_absorption_rate_s-1_cMpc-3"
                    ].sum()
                )
            )
        out[owner] = (fraction, np.asarray(values, dtype=float))
    for group in ("G1", "G2a"):
        values = []
        for x in fraction:
            values.append(
                float(
                    sub[(sub["fraction"] == x) & (sub["group"] == group)][
                        "authoritative_total_absorption_rate_s-1_cMpc-3"
                    ].drop_duplicates().sum()
                )
            )
        out[f"INVALID_TOTAL_{group}_TO_RESOLVED_H"] = (
            fraction,
            np.asarray(values, dtype=float),
        )
    return out


def build_capacity_refinement(
    *, split: pd.DataFrame, forcing: pd.DataFrame, ots: pd.DataFrame, output: Path
) -> tuple[pd.DataFrame, pd.DataFrame]:
    total_h = NH0_CM3 * MPC_CM**3
    total_he = YHE * total_h
    primary_ots = ots[ots["closure"] == "LOCAL_NODE_STATE_PRIMARY_DETERMINISTIC"]
    rows: list[dict[str, Any]] = []
    totals: list[dict[str, Any]] = []

    for interval in sorted(split["interval_index"].unique()):
        base = forcing[forcing["interval_index"] == interval].sort_values("fraction")
        first = base.iloc[0]
        duration = float(base["time_s"].max())
        zmid = float(first["z_mid"])
        source = primary_ots[np.isclose(primary_ots["z"], zmid)].iloc[0]
        interpolators = owner_rate_interpolators(split, int(interval))

        for refinement in (1, 2, 4, 8):
            reservoirs = {
                "HI": total_h * (1.0 - float(first["xHII"])),
                "HeI": total_he * float(first["xHeI"]),
                "HeII": total_he * float(first["xHeII"]),
                "INVALID_HI": total_h * (1.0 - float(first["xHII"])),
            }
            assigned_totals = {"HI": 0.0, "HeI": 0.0, "HeII": 0.0, "INVALID_HI": 0.0}
            feasible_totals = {name: True for name in assigned_totals}
            reachable = {name: True for name in assigned_totals}
            for substep in range(refinement):
                left = substep / refinement
                right = (substep + 1) / refinement
                dt = duration * (right - left)
                assigned_h = duration * integrate_positive_pchip(*interpolators["RESOLVED_HI"], left, right)
                assigned_hei = duration * integrate_positive_pchip(*interpolators["RESOLVED_HeI"], left, right)
                assigned_heii = duration * integrate_positive_pchip(*interpolators["RESOLVED_HeII"], left, right)
                old_g1 = duration * integrate_positive_pchip(
                    *interpolators["INVALID_TOTAL_G1_TO_RESOLVED_H"], left, right
                )
                old_g2a = duration * integrate_positive_pchip(
                    *interpolators["INVALID_TOTAL_G2a_TO_RESOLVED_H"], left, right
                )
                assigned_invalid = old_g1 + old_g2a

                rec_h = float(source["source_HI"]) * dt
                rec_hei = float(source["source_HeI"]) * dt
                rec_heiii_to_heii = float(source["m_HeII_to_HeIII_s-1_cMpc-3"]) * dt
                rec_heii_to_hei = float(source["m_HeI_to_HeII_s-1_cMpc-3"]) * dt

                cert_h = capacity_certificate(
                    assigned_absorption=assigned_h,
                    initial_reservoir=reservoirs["HI"],
                    recombination_supply=rec_h,
                )
                cert_hei = capacity_certificate(
                    assigned_absorption=assigned_hei,
                    initial_reservoir=reservoirs["HeI"],
                    recombination_supply=rec_hei,
                )
                cert_heii = capacity_certificate(
                    assigned_absorption=assigned_heii,
                    initial_reservoir=reservoirs["HeII"],
                    recombination_supply=rec_heiii_to_heii,
                    material_inflow=assigned_hei,
                    material_outflow=rec_heii_to_hei,
                )
                cert_invalid = None
                if reachable["INVALID_HI"]:
                    cert_invalid = capacity_certificate(
                        assigned_absorption=assigned_invalid,
                        initial_reservoir=reservoirs["INVALID_HI"],
                        recombination_supply=rec_h,
                    )
                certs = {
                    "HI": (cert_h, assigned_h, rec_h, 0.0, 0.0, "OWNER_CORRECT"),
                    "HeI": (cert_hei, assigned_hei, rec_hei, 0.0, 0.0, "OWNER_CORRECT"),
                    "HeII": (
                        cert_heii,
                        assigned_heii,
                        rec_heiii_to_heii,
                        assigned_hei,
                        rec_heii_to_hei,
                        "OWNER_CORRECT",
                    ),
                    "INVALID_HI": (
                        cert_invalid,
                        assigned_invalid,
                        rec_h,
                        0.0,
                        0.0,
                        "INVALID_UNSPLIT_G1_G2A_TO_RESOLVED_H",
                    ),
                }
                for species, (cert, assigned, recomb, inflow, outflow, mode) in certs.items():
                    if cert is None:
                        rows.append(
                            {
                                "interval_index": int(interval),
                                "z_mid": zmid,
                                "refinement": refinement,
                                "substep": substep,
                                "fraction_left": left,
                                "fraction_right": right,
                                "dt_s": dt,
                                "mode": mode,
                                "species_reservoir": species,
                                "reservoir_start_cMpc-3": math.nan,
                                "assigned_absorption_cMpc-3": assigned,
                                "recombination_supply_cMpc-3": recomb,
                                "material_inflow_cMpc-3": inflow,
                                "material_outflow_cMpc-3": outflow,
                                "capacity_cMpc-3": math.nan,
                                "slack_cMpc-3": 0.0,
                                "overshoot_cMpc-3": math.nan,
                                "feasible": False,
                                "reachable": False,
                                "status": "UNREACHABLE_AFTER_PRIOR_CAPACITY_FAILURE",
                            }
                        )
                        feasible_totals[species] = False
                        continue
                    rows.append(
                        {
                            "interval_index": int(interval),
                            "z_mid": zmid,
                            "refinement": refinement,
                            "substep": substep,
                            "fraction_left": left,
                            "fraction_right": right,
                            "dt_s": dt,
                            "mode": mode,
                            "species_reservoir": species,
                            "reservoir_start_cMpc-3": reservoirs[species],
                            "assigned_absorption_cMpc-3": assigned,
                            "recombination_supply_cMpc-3": recomb,
                            "material_inflow_cMpc-3": inflow,
                            "material_outflow_cMpc-3": outflow,
                            "capacity_cMpc-3": cert.capacity,
                            "slack_cMpc-3": cert.slack,
                            "overshoot_cMpc-3": cert.overshoot,
                            "feasible": cert.feasible,
                            "reachable": True,
                            "status": "PASS" if cert.feasible else "CAPACITY_FAILURE",
                        }
                    )
                    assigned_totals[species] += assigned
                    feasible_totals[species] = feasible_totals[species] and cert.feasible
                    if cert.feasible:
                        reservoirs[species] = cert.capacity - assigned
                    else:
                        reachable[species] = False
            for species in assigned_totals:
                totals.append(
                    {
                        "interval_index": int(interval),
                        "z_mid": zmid,
                        "refinement": refinement,
                        "species_reservoir": species,
                        "assigned_total_cMpc-3": assigned_totals[species],
                        "all_substeps_feasible": feasible_totals[species],
                        "reservoir_end_cMpc-3": reservoirs[species],
                    }
                )
    matrix = pd.DataFrame(rows)
    total_frame = pd.DataFrame(totals)
    matrix.to_csv(output / "capacity_refinement_matrix.csv", index=False)
    total_frame.to_csv(output / "capacity_refinement_totals.csv", index=False)
    return matrix, total_frame


def build_midpoint_node_audit(
    *,
    split: pd.DataFrame,
    forcing: pd.DataFrame,
    stage_root: Path,
    source_dir: Path,
    r1b_r1_root: Path,
    output: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sys.path.insert(0, str(source_dir))
    hierarchy_path = stage_root / "inputs" / "upstream" / "hierarchical_two_scale_closure.py"
    hierarchy = load_module("r1b_r2a_hierarchy", hierarchy_path)
    micro_npz = np.load(stage_root / "inputs" / "upstream" / "fixed_micro_parcel_template_z6.npz")
    fixed_micro = hierarchy.FixedMicroTemplate(
        n_delta=len(micro_npz["w_delta"]),
        n_t=micro_npz["w_temperature"].shape[1],
        w_delta=micro_npz["w_delta"],
        w_temperature=micro_npz["w_temperature"],
        u_delta=micro_npz["u_delta"],
        u_temperature=micro_npz["u_temperature"],
        weight_lock_redshift=6.0,
    )
    macro_template = pd.read_csv(stage_root / "inputs" / "upstream" / "fixed_macro_parcel_template_z6.csv")
    mapping = pd.read_csv(stage_root / "inputs" / "upstream" / "density_mapping_colossus_1_3_10_port.csv")
    atomic = pd.read_csv(
        r1b_r1_root / "data" / "atomic_moments" / "verner_gray_and_limit_moments.csv"
    )
    sigma = {(r.species, r.group): float(r.gray_sigma_cm2) for r in atomic.itertuples()}
    prior_path = stage_root.parents[0] / "Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2B_MOMENT_CONSTRAINED_NODE_LIFT_HISTORY_UPLOAD_RECOVERY_V2" / "data" / "b0a_full_node_priors.npz"
    priors = np.load(prior_path)

    audit_rows: list[dict[str, Any]] = []
    macro_rows: list[dict[str, Any]] = []
    tv_rows: list[dict[str, Any]] = []
    midpoint = forcing[np.isclose(forcing["fraction"], 0.5)].sort_values("interval_index")

    for rec in midpoint.to_dict(orient="records"):
        interval = int(rec["interval_index"])
        zmid = float(rec["z_mid"])
        history_state = hierarchy.B2C0.HistoryState(
            z=zmid,
            x_hii=float(rec["xHII"]),
            x_heii=float(rec["xHeII"]),
            x_heiii=float(rec["xHeIII"]),
            temperature=float(rec["T_K"]),
            gamma_hi=float(rec["Gamma_HI_s-1"]),
        )
        macro = hierarchy.macro_measure(zmid, mapping, macro_template)
        nodes, _, diagnostics = hierarchy.construct_hierarchy(
            history_state, macro, fixed_micro, "BASELINE"
        )
        weights = nodes.W_node.to_numpy(dtype=float)
        density = nodes.delta_total.to_numpy(dtype=float)
        n_h = hierarchy.NH0 * (1.0 + zmid) ** 3 * density
        n_he = hierarchy.YHE * n_h
        species_density = {
            "HI": n_h * (1.0 - nodes.xHII.to_numpy(dtype=float)),
            "HeI": n_he * nodes.xHeI.to_numpy(dtype=float),
            "HeII": n_he * nodes.xHeII.to_numpy(dtype=float),
        }
        macro_index = nodes.macro_index.to_numpy(dtype=int)
        proper_length = (2.0 / H_SMALL) * KPC_CM / (1.0 + zmid)
        node_split = split[
            (split["interval_index"] == interval) & np.isclose(split["fraction"], 0.5)
        ]
        zlabel = f"z{zmid:.2f}"

        for group in GROUPS:
            for component in COMPONENTS:
                owner_total = float(
                    node_split[
                        (node_split["group"] == group)
                        & (node_split["component"] == component)
                    ]["owner_absorption_rate_s-1_cMpc-3"].iloc[0]
                )
                if component == "EFFECTIVE_HI_SUBGRID":
                    lanes = SUBGRID_LANES if group in {"G1", "G2a"} else ("STRUCTURAL_ZERO",)
                else:
                    lanes = ("STATE_DERIVED",)
                allocations: dict[str, np.ndarray] = {}
                for lane in lanes:
                    if component == "EFFECTIVE_HI_SUBGRID":
                        if lane == "STRUCTURAL_ZERO":
                            measure = np.zeros_like(weights)
                        else:
                            key = f"{zlabel}_{lane}_{group}_q_node"
                            measure = np.asarray(priors[key], dtype=float)
                            macro_index_lane = np.asarray(
                                priors[f"{zlabel}_{lane}_{group}_macro_index"], dtype=int
                            )
                            if not np.array_equal(macro_index_lane, macro_index):
                                raise RuntimeError("macro-index mismatch between hierarchy and locked prior")
                    else:
                        species = RESOLVED_COMPONENT_SPECIES[component]
                        if (species, group) not in sigma or sigma[(species, group)] == 0.0:
                            measure = np.zeros_like(weights)
                        else:
                            measure = (
                                weights
                                * proper_length
                                * species_density[species]
                                * sigma[(species, group)]
                            )
                    allocation = disintegrate_owner_current(
                        owner_total=owner_total, measure=measure
                    )
                    allocations[lane] = allocation
                    support = measure > 0.0
                    audit_rows.append(
                        {
                            "interval_index": interval,
                            "z_mid": zmid,
                            "group": group,
                            "component": component,
                            "owner": COMPONENT_OWNER[component],
                            "partition_lane": lane,
                            "node_count": len(allocation),
                            "owner_total_s-1_cMpc-3": owner_total,
                            "allocation_sum_relative_residual": rel(float(allocation.sum()), owner_total) if owner_total != 0.0 else abs(float(allocation.sum())),
                            "minimum_allocation": float(allocation.min()),
                            "negative_allocation_count": int(np.count_nonzero(allocation < 0.0)),
                            "zero_support_nonzero_allocation_count": int(
                                np.count_nonzero((~support) & (allocation != 0.0))
                            ),
                            "allocation_sha256": sha_array(allocation),
                            "measure_sha256": sha_array(measure),
                            "hierarchy_weight_residual": abs(float(diagnostics["mass_density_sum"]) - 1.0),
                        }
                    )
                    for macro_id in range(18):
                        sel = macro_index == macro_id
                        macro_rows.append(
                            {
                                "interval_index": interval,
                                "z_mid": zmid,
                                "group": group,
                                "component": component,
                                "partition_lane": lane,
                                "macro_index": macro_id,
                                "macro_owner_current_s-1_cMpc-3": float(allocation[sel].sum()),
                            }
                        )
                if component == "EFFECTIVE_HI_SUBGRID" and len(allocations) == 3:
                    lane_names = list(allocations)
                    for i in range(len(lane_names)):
                        for j in range(i + 1, len(lane_names)):
                            a = allocations[lane_names[i]] / owner_total if owner_total > 0.0 else allocations[lane_names[i]]
                            b = allocations[lane_names[j]] / owner_total if owner_total > 0.0 else allocations[lane_names[j]]
                            tv_rows.append(
                                {
                                    "interval_index": interval,
                                    "z_mid": zmid,
                                    "group": group,
                                    "lane_a": lane_names[i],
                                    "lane_b": lane_names[j],
                                    "total_variation": 0.5 * float(np.abs(a - b).sum()),
                                }
                            )

    audit = pd.DataFrame(audit_rows)
    macro = pd.DataFrame(macro_rows)
    tv_frame = pd.DataFrame(tv_rows)
    audit.to_csv(output / "midpoint_node_owner_disintegration_audit.csv", index=False)
    macro.to_csv(output / "midpoint_macro_owner_disintegration.csv", index=False)
    tv_frame.to_csv(output / "subgrid_prior_TV_envelope.csv", index=False)
    return audit, macro, tv_frame


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--r1b-r1", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    stage = args.stage.resolve()
    r1b_r1 = args.r1b_r1.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    forcing_path = r1b_r1 / "data" / "bdf_replay" / "canonical_time_resolved_forcing_nodes.csv"
    forcing = pd.read_csv(forcing_path)
    public = pd.read_csv(stage / "inputs" / "upstream" / "public_repo_exact_checkpoint_global.csv")
    source_dir = r1b_r1 / "inputs" / "canonical_b2c2a_r1_src"
    split, audit, comparison = build_time_resolved_owner_split(
        forcing=forcing,
        public=public,
        raw_path=stage / "inputs" / "upstream" / "environment_mfp_energies.txt",
        density_path=stage / "inputs" / "upstream" / "density_mapping_colossus_1_3_10_port.csv",
        source_dir=source_dir,
        output=output,
    )
    capacity, capacity_totals = build_capacity_refinement(
        split=split,
        forcing=forcing,
        ots=pd.read_csv(stage / "inputs" / "upstream" / "hierarchical_full_ots_source.csv"),
        output=output,
    )
    node_audit, macro_audit, tv_frame = build_midpoint_node_audit(
        split=split,
        forcing=forcing,
        stage_root=stage,
        source_dir=source_dir,
        r1b_r1_root=r1b_r1,
        output=output,
    )

    owner_correct = capacity[capacity["mode"] == "OWNER_CORRECT"]
    invalid = capacity[capacity["mode"] != "OWNER_CORRECT"]
    invalid_reachable = invalid[invalid["reachable"]]
    invalid_unreachable = invalid[~invalid["reachable"]]
    owner_correct_ratio = (
        owner_correct["assigned_absorption_cMpc-3"]
        / owner_correct["capacity_cMpc-3"]
    )
    subgrid_zero = split[split["component"] == "EFFECTIVE_HI_SUBGRID"]
    qtotals = capacity_totals[capacity_totals["species_reservoir"] != "INVALID_HI"]
    reference = qtotals[qtotals["refinement"] == 8].set_index(
        ["interval_index", "species_reservoir"]
    )["assigned_total_cMpc-3"]
    refinement_residuals = []
    for row in qtotals.to_dict(orient="records"):
        ref_value = float(reference.loc[(row["interval_index"], row["species_reservoir"])])
        value = float(row["assigned_total_cMpc-3"])
        refinement_residuals.append(rel(value, ref_value) if ref_value != 0.0 else abs(value))

    hard_pass = bool(
        audit["conditioned_kappa_sum_relative_residual"].max() <= 1.0e-11
        and audit["conditioned_current_sum_relative_residual"].max() <= 1.0e-11
        and audit["minimum_component_kappa_cMpc_inv"].min() >= 0.0
        and audit["minimum_component_current_s-1_cMpc-3"].min() >= 0.0
        and owner_correct["feasible"].all()
        and len(invalid_reachable) == 20
        and (~invalid_reachable["feasible"]).all()
        and (invalid_reachable["substep"] == 0).all()
        and max(refinement_residuals) <= 1.0e-12
        and (subgrid_zero["resolved_H_source_coefficient"] == 0).all()
        and (subgrid_zero["resolved_He_source_coefficient"] == 0).all()
        and (subgrid_zero["resolved_thermal_source_coefficient"] == 0).all()
        and node_audit["negative_allocation_count"].sum() == 0
        and node_audit["zero_support_nonzero_allocation_count"].sum() == 0
        and node_audit["allocation_sum_relative_residual"].max() <= 1.0e-11
    )
    verdict = (
        "DURABLE_PASS_R2C_R1B_R2A_OWNER_SPLIT_REMOVES_FALSE_CAPACITY_BLOCKER_"
        "OWNER_CORRECT_R1B_R2B_AUTHORIZED"
        if hard_pass
        else "DURABLE_FAIL_CLOSED_R2C_R1B_R2A_OWNER_SPLIT_PREFLIGHT_GATE_FAILURE"
    )
    summary = {
        "classification": "R1B_R2A_OWNER_SPLIT_PREFLIGHT_SUMMARY",
        "stage": "P0.5-B2C2B0C-R2C-R1B-R2A-PHOTON-SINK-MATERIAL-REACTION-OWNER-SPLIT-PREFLIGHT",
        "verdict": verdict,
        "hard_pass": hard_pass,
        "time_resolved_forcing_rows": int(len(forcing)),
        "owner_component_rows": int(len(split)),
        "group_cases": int(len(audit)),
        "max_raw_component_sum_vs_authoritative_relative_residual": float(audit["raw_sum_vs_authoritative_relative_residual"].max()),
        "max_conditioned_kappa_sum_relative_residual": float(audit["conditioned_kappa_sum_relative_residual"].max()),
        "max_conditioned_current_sum_relative_residual": float(audit["conditioned_current_sum_relative_residual"].max()),
        "owner_correct_capacity_cases": int(len(owner_correct)),
        "owner_correct_capacity_failures": int((~owner_correct["feasible"]).sum()),
        "max_owner_correct_assigned_to_capacity_ratio": float(owner_correct_ratio.max()),
        "min_owner_correct_slack_fraction": float((1.0 - owner_correct_ratio).min()),
        "invalid_unsplit_reachable_cases": int(len(invalid_reachable)),
        "invalid_unsplit_reachable_failures": int((~invalid_reachable["feasible"]).sum()),
        "invalid_unsplit_unreachable_after_failure_rows": int(len(invalid_unreachable)),
        "max_refinement_total_relative_residual": float(max(refinement_residuals)),
        "subgrid_resolved_source_coefficients_exact_zero": bool(
            (subgrid_zero[[
                "resolved_H_source_coefficient",
                "resolved_He_source_coefficient",
                "resolved_thermal_source_coefficient",
            ]] == 0).all().all()
        ),
        "midpoint_node_disintegration_cases": int(len(node_audit)),
        "midpoint_macro_disintegration_rows": int(len(macro_audit)),
        "max_node_allocation_sum_relative_residual": float(node_audit["allocation_sum_relative_residual"].max()),
        "negative_node_allocation_count": int(node_audit["negative_allocation_count"].sum()),
        "zero_support_nonzero_node_allocation_count": int(node_audit["zero_support_nonzero_allocation_count"].sum()),
        "subgrid_prior_TV_range": [
            float(tv_frame["total_variation"].min()),
            float(tv_frame["total_variation"].max()),
        ] if len(tv_frame) else None,
        "canonical_component_average_comparison_max_relative_difference_auditor": float(comparison["relative_difference"].max()),
        "scope": {
            "chemistry_integrated": False,
            "thermal_history_integrated": False,
            "subgrid_absorption_added_to_resolved_thermal_state": False,
            "recombination_surrogate": False,
        },
    }
    (output / "owner_split_preflight_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not hard_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
