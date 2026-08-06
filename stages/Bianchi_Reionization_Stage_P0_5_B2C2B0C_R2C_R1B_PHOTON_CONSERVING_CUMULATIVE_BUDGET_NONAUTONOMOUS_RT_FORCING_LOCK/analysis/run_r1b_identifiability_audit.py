#!/usr/bin/env python3
"""R2C-R1B physics-only forcing/thermal identifiability audit.

This stage does not integrate a production chemistry history.  It asks a
prior question: whether the durable endpoint moments and interval ledgers
identify the node/group nonautonomous forcing, dynamic opacity law, and
energy-weighted heating history required by a C2-Ray-type fixed point.

No node-wise fit, clipping, inter-macro transport, source/fesc calibration,
Jeans-cloud mass inversion, recombination surrogate, CAMB transfer, or
Bianchi feedback is performed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import itertools
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

MYR_S = 1.0e6 * 365.25 * 86400.0
EV_ERG = 1.602176634e-12
CORE_RTOL = 2.0e-11
SHAPES = [
    "LOCAL_NEUTRAL_HAZARD_PRIMARY",
    "RECOMBINATION_WEIGHTED_AUDITOR",
    "SCRIPT_SELF_SHIELDING_AUDITOR",
]
ACTIVE_GROUPS = ["G1", "G2a"]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_file(path: Path, chunk: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def relative_residual(a: np.ndarray | float, b: np.ndarray | float) -> np.ndarray:
    aa = np.asarray(a, dtype=float)
    bb = np.asarray(b, dtype=float)
    return np.abs(aa - bb) / np.maximum(
        np.maximum(np.abs(aa), np.abs(bb)), np.finfo(float).tiny
    )


def write_inventory(stage: Path, repo: Path) -> pd.DataFrame:
    rows = [
        {
            "source": "B2C2A_R1 canonical_direct_photon_ledger",
            "repo_or_stage_path": "data/input_canonical_direct_photon_ledger.csv",
            "spatial_resolution": "GLOBAL",
            "time_resolution": "ONE_INTERVAL_AVERAGE",
            "group_resolution": "G1,G2a,G2b,G3",
            "independent_boundary_or_source_history": False,
            "node_partition_supplied": False,
            "dynamic_opacity_constitutive_law": False,
            "energy_weighted_heating_history": False,
            "load_bearing_interpretation": "Exact global interval photon bookkeeping; not a sink/node forcing history.",
        },
        {
            "source": "B2C2A_R1 gamma_conditioned_group_fit_tables",
            "repo_or_stage_path": "data/input_gamma_conditioned_group_fit_tables.csv",
            "spatial_resolution": "GLOBAL_EFFECTIVE",
            "time_resolution": "Z_MIDPOINT_X_GAMMA_GRID",
            "group_resolution": "G1,G2a",
            "independent_boundary_or_source_history": False,
            "node_partition_supplied": False,
            "dynamic_opacity_constitutive_law": "PARTIAL_GLOBAL_KAPPA_OF_GAMMA_ONLY",
            "energy_weighted_heating_history": False,
            "load_bearing_interpretation": "Global effective opacity table conditional on Gamma; Gamma(t) and a node map are not supplied.",
        },
        {
            "source": "B2C2A_R1 cell_deposition_refinement",
            "repo_or_stage_path": "data/input_cell_deposition_refinement.csv",
            "spatial_resolution": "GLOBAL_COMPONENT_AUDITOR",
            "time_resolution": "INTERVAL_MIDPOINT_STRESS_SEQUENCE",
            "group_resolution": "MULTIGROUP",
            "independent_boundary_or_source_history": False,
            "node_partition_supplied": False,
            "dynamic_opacity_constitutive_law": False,
            "energy_weighted_heating_history": False,
            "load_bearing_interpretation": "Finite-cell deposition convergence auditor, not a time-resolved boundary condition.",
        },
        {
            "source": "B2C2B0A hierarchical_full_ots_source",
            "repo_or_stage_path": "data/input_hierarchical_full_ots_source.csv",
            "spatial_resolution": "GLOBAL_CLOSURE_LANE",
            "time_resolution": "Z_MIDPOINT",
            "group_resolution": "SPECIES_STOICHIOMETRIC_NOT_BOUNDARY_GROUP_FLUX",
            "independent_boundary_or_source_history": False,
            "node_partition_supplied": False,
            "dynamic_opacity_constitutive_law": False,
            "energy_weighted_heating_history": False,
            "load_bearing_interpretation": "Species maintenance/source rates; not incident or absorbed group flux versus time.",
        },
        {
            "source": "B2C2B0A r1_opacity_targets",
            "repo_or_stage_path": "data/input_r1_opacity_targets.csv",
            "spatial_resolution": "GLOBAL_COMPONENT_TARGET",
            "time_resolution": "Z_MIDPOINT",
            "group_resolution": "MULTIGROUP",
            "independent_boundary_or_source_history": False,
            "node_partition_supplied": False,
            "dynamic_opacity_constitutive_law": False,
            "energy_weighted_heating_history": False,
            "load_bearing_interpretation": "Locked midpoint opacity moments; no path from evolving node neutral state to opacity.",
        },
        {
            "source": "B2C2B0A macro_species_photon_allocation",
            "repo_or_stage_path": "data/input_macro_species_photon_allocation.csv",
            "spatial_resolution": "18_MACRO_PRIOR",
            "time_resolution": "Z_MIDPOINT",
            "group_resolution": "MULTIGROUP_X_SPECIES",
            "independent_boundary_or_source_history": False,
            "node_partition_supplied": False,
            "dynamic_opacity_constitutive_law": False,
            "energy_weighted_heating_history": False,
            "load_bearing_interpretation": "Prior macro allocation at a midpoint, not a unique time-dependent node allocation.",
        },
        {
            "source": "R2A global_moment_lock",
            "repo_or_stage_path": "../R2A/data/global_moment_lock.csv",
            "spatial_resolution": "GLOBAL_SINK",
            "time_resolution": "TWO_LOCKED_SUBSTEP_ENDPOINTS_PER_INTERVAL",
            "group_resolution": "G1,G2a,G2b,G3",
            "independent_boundary_or_source_history": False,
            "node_partition_supplied": False,
            "dynamic_opacity_constitutive_law": False,
            "energy_weighted_heating_history": False,
            "load_bearing_interpretation": "Hard global sink moments; no interior forcing path.",
        },
        {
            "source": "R2A macro_projection",
            "repo_or_stage_path": "../R2A/data/macro_projection.csv",
            "spatial_resolution": "18_MACROS_X_3_SHAPE_PRIORS",
            "time_resolution": "TWO_LOCKED_SUBSTEP_ENDPOINTS_PER_INTERVAL",
            "group_resolution": "G1,G2a",
            "independent_boundary_or_source_history": False,
            "node_partition_supplied": False,
            "dynamic_opacity_constitutive_law": False,
            "energy_weighted_heating_history": False,
            "load_bearing_interpretation": "Three feasible prior-dependent macro endpoint distributions, not one canonical trajectory.",
        },
        {
            "source": "R2B node_group_lift",
            "repo_or_stage_path": "external logical node_group_lift.csv.gz",
            "spatial_resolution": "46080_NODES_PER_SHAPE_CASE",
            "time_resolution": "TWO_LOCKED_SUBSTEP_ENDPOINTS_PER_INTERVAL",
            "group_resolution": "G1,G2a",
            "independent_boundary_or_source_history": False,
            "node_partition_supplied": "ENDPOINT_PROJECTION_ONLY",
            "dynamic_opacity_constitutive_law": False,
            "energy_weighted_heating_history": False,
            "load_bearing_interpretation": "J is KL-projected and kappa is then defined as J/Phi; this is an endpoint algebraic lift, not kappa[N_HI,T,...].",
        },
        {
            "source": "Primary E^-2.5 spectrum and atomic group moments",
            "repo_or_stage_path": "src/rei_bianchi/{absorption_decomposition,b2b_physical_model}.py",
            "spatial_resolution": "SOURCE_SPECTRAL_PRIOR",
            "time_resolution": "STATIC_WITHIN_GROUP_PRIOR",
            "group_resolution": "G1,G2a,G2b,G3",
            "independent_boundary_or_source_history": False,
            "node_partition_supplied": False,
            "dynamic_opacity_constitutive_law": "ATOMIC_SPECTRAL_AUDITOR_ONLY",
            "energy_weighted_heating_history": "CANDIDATE_GROUP_MOMENTS_ONLY",
            "load_bearing_interpretation": "Supplies candidate thin/thick excess-energy moments; evolving absorbed spectrum still depends on optical depth and incident flux.",
        },
    ]
    out = pd.DataFrame(rows)
    out.to_csv(stage / "data/input_information_inventory.csv", index=False)
    return out


def global_partition(stage: Path, global_lock: pd.DataFrame) -> pd.DataFrame:
    direct = pd.read_csv(stage / "data/input_canonical_direct_photon_ledger.csv")
    rows: list[dict[str, Any]] = []
    for interval, g in global_lock.groupby("interval_index", sort=True):
        weight = g["dt_Myr"].to_numpy(float)
        sink_g1 = float(np.average(g["J_sink_G1_global_s_inv_cMpc3"], weights=weight))
        sink_g2a = float(np.average(g["J_sink_G2a_global_s_inv_cMpc3"], weights=weight))
        sink_low = sink_g1 + sink_g2a
        d = direct.loc[direct["interval_index"].eq(interval)].iloc[0]
        global_low = float(d.absorption_G1_rate + d.absorption_G2a_rate)
        global_all = float(
            d.absorption_G1_rate
            + d.absorption_G2a_rate
            + d.absorption_G2b_rate
            + d.absorption_G3_rate
        )
        ionized_abs = float(d.ionized_absorption_rate)
        rows.append(
            {
                "interval_index": int(interval),
                "z_mid": float(d.z_mid),
                "duration_Myr": float(d.dt_Myr),
                "sink_G1_time_weighted_rate": sink_g1,
                "sink_G2a_time_weighted_rate": sink_g2a,
                "sink_low_group_rate": sink_low,
                "global_G1_rate": float(d.absorption_G1_rate),
                "global_G2a_rate": float(d.absorption_G2a_rate),
                "global_G2b_rate": float(d.absorption_G2b_rate),
                "global_G3_rate": float(d.absorption_G3_rate),
                "global_low_group_rate": global_low,
                "global_all_group_rate": global_all,
                "global_ionized_absorption_rate": ionized_abs,
                "sink_to_global_low_ratio": sink_low / global_low,
                "sink_to_global_all_ratio": sink_low / global_all,
                "sink_to_ionized_absorption_ratio": sink_low / ionized_abs,
                "G2b_fraction_of_all": float(d.absorption_G2b_rate) / global_all,
                "G3_exact_zero": float(d.absorption_G3_rate) == 0.0,
                "canonical_sink_partition_supplied": False,
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(stage / "data/global_sink_ledger_partition.csv", index=False)
    return out


def macro_pairwise_tv(stage: Path, macro: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    quantities = {
        "MASS": "M_sink_H_cMpc3",
        "G1_CURRENT": "J_sink_G1_s_inv_cMpc3",
        "G2a_CURRENT": "J_sink_G2a_s_inv_cMpc3",
        "G1_OPACITY": "kappa_sink_G1_cMpc_inv",
        "G2a_OPACITY": "kappa_sink_G2a_cMpc_inv",
    }
    for (interval, substep), case in macro.groupby(["interval_index", "substep"], sort=True):
        for quantity, column in quantities.items():
            distributions: dict[str, np.ndarray] = {}
            for shape in SHAPES:
                values = (
                    case.loc[case.shape_lane.eq(shape)]
                    .sort_values("macro_index")[column]
                    .to_numpy(float)
                )
                if len(values) != 18 or values.sum() <= 0:
                    raise RuntimeError((interval, substep, shape, quantity, len(values), values.sum()))
                distributions[shape] = values / values.sum()
            for a, b in itertools.combinations(SHAPES, 2):
                pa, pb = distributions[a], distributions[b]
                rows.append(
                    {
                        "interval_index": int(interval),
                        "substep": int(substep),
                        "quantity": quantity,
                        "shape_a": a,
                        "shape_b": b,
                        "total_variation": 0.5 * float(np.abs(pa - pb).sum()),
                        "l1_distance": float(np.abs(pa - pb).sum()),
                        "same_global_sum_by_construction": True,
                    }
                )
    out = pd.DataFrame(rows)
    out.to_csv(stage / "data/shape_macro_allocation_pairwise_tv.csv", index=False)
    return out


def rank_nullity_table(stage: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for k in [4, 8, 16]:
        rows.append(
            {
                "family": "SINGLE_NODE_ENDPOINTS_PLUS_ONE_INTERVAL_INTEGRAL",
                "node_count": 1,
                "time_knot_count": k,
                "unknown_count": k,
                "constraint_rank": 3,
                "nullity": k - 3,
                "formula": "K-3",
            }
        )
        for n in [1, 2560, 46080]:
            rank = 2 * n + k - 2
            unknown = n * k
            rows.append(
                {
                    "family": "NODE_ENDPOINTS_PLUS_POINTWISE_MACRO_TOTAL",
                    "node_count": n,
                    "time_knot_count": k,
                    "unknown_count": unknown,
                    "constraint_rank": rank,
                    "nullity": unknown - rank,
                    "formula": "(N-1)(K-2)",
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(stage / "data/constraint_rank_nullity.csv", index=False)
    return out


def scan_node_groups(stage: Path, group_path: Path, chunksize: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    usecols = [
        "shape_lane",
        "interval_index",
        "substep",
        "z_mid",
        "macro_index",
        "micro_index",
        "group",
        "J_sink_node_s_inv_cMpc3",
        "kappa_sink_node_cMpc_inv",
        "Phi_current_Gamma_s_inv_cMpc2",
    ]
    dtypes = {
        "shape_lane": "string",
        "interval_index": "int16",
        "substep": "int8",
        "macro_index": "int8",
        "micro_index": "int16",
        "group": "string",
    }
    sums: dict[tuple[str, int, int, str], dict[str, Any]] = defaultdict(
        lambda: {
            "row_count": 0,
            "J_sum": 0.0,
            "kappa_sum": 0.0,
            "J_negative": 0,
            "kappa_negative": 0,
            "Phi_nonpositive": 0,
            "current_gamma_residual_max": 0.0,
            "Phi_min": math.inf,
            "Phi_max": -math.inf,
            "Phi_values": set(),
        }
    )
    sample_parts: list[pd.DataFrame] = []
    node_distributions: dict[tuple[str, int, int, int, str], np.ndarray] = {}
    total_rows = 0
    for chunk in pd.read_csv(group_path, usecols=usecols, dtype=dtypes, chunksize=chunksize):
        total_rows += len(chunk)
        mask = (
            chunk.shape_lane.eq(SHAPES[0])
            & chunk.interval_index.eq(0)
            & chunk.macro_index.eq(0)
            & chunk.group.eq("G1")
            & chunk.substep.isin([1, 2])
        )
        if mask.any():
            sample_parts.append(chunk.loc[mask].copy())
        for key_macro, gm in chunk.groupby(
            ["shape_lane", "interval_index", "substep", "macro_index", "group"],
            observed=True,
            sort=False,
        ):
            stable_key = (
                str(key_macro[0]), int(key_macro[1]), int(key_macro[2]),
                int(key_macro[3]), str(key_macro[4])
            )
            target = node_distributions.setdefault(stable_key, np.zeros(2560, dtype=float))
            target[gm.micro_index.to_numpy(int)] = gm.J_sink_node_s_inv_cMpc3.to_numpy(float)
        for key, g in chunk.groupby(
            ["shape_lane", "interval_index", "substep", "group"], observed=True, sort=False
        ):
            record = sums[(str(key[0]), int(key[1]), int(key[2]), str(key[3]))]
            j = g.J_sink_node_s_inv_cMpc3.to_numpy(float)
            kappa = g.kappa_sink_node_cMpc_inv.to_numpy(float)
            phi = g.Phi_current_Gamma_s_inv_cMpc2.to_numpy(float)
            resid = relative_residual(j, kappa * phi)
            record["row_count"] += len(g)
            record["J_sum"] += float(j.sum())
            record["kappa_sum"] += float(kappa.sum())
            record["J_negative"] += int(np.count_nonzero(j < 0.0))
            record["kappa_negative"] += int(np.count_nonzero(kappa < 0.0))
            record["Phi_nonpositive"] += int(np.count_nonzero(phi <= 0.0))
            record["current_gamma_residual_max"] = max(
                record["current_gamma_residual_max"], float(np.nanmax(resid))
            )
            record["Phi_min"] = min(record["Phi_min"], float(np.min(phi)))
            record["Phi_max"] = max(record["Phi_max"], float(np.max(phi)))
            # Values are macro constants.  Rounding only stabilizes binary print noise.
            record["Phi_values"].update(np.round(phi, 9).tolist())

    rows: list[dict[str, Any]] = []
    for key, value in sorted(sums.items()):
        rows.append(
            {
                "shape_lane": key[0],
                "interval_index": key[1],
                "substep": key[2],
                "group": key[3],
                "node_rows": value["row_count"],
                "J_sum": value["J_sum"],
                "kappa_sum": value["kappa_sum"],
                "Phi_min": value["Phi_min"],
                "Phi_max": value["Phi_max"],
                "Phi_distinct_rounded_1e_minus_9": len(value["Phi_values"]),
                "negative_J_rows": value["J_negative"],
                "negative_kappa_rows": value["kappa_negative"],
                "nonpositive_Phi_rows": value["Phi_nonpositive"],
                "max_J_equals_kappa_Phi_relative_residual": value[
                    "current_gamma_residual_max"
                ],
                "dynamic_opacity_law_present_in_rows": False,
            }
        )
    inventory = pd.DataFrame(rows)
    inventory.to_csv(stage / "data/node_group_endpoint_inventory.csv", index=False)

    samples = pd.concat(sample_parts, ignore_index=True)
    pivot = samples.pivot_table(
        index=["macro_index", "micro_index"],
        columns="substep",
        values="J_sink_node_s_inv_cMpc3",
        aggfunc="first",
    ).dropna()
    if not {1, 2}.issubset(pivot.columns):
        raise RuntimeError("No common sample nodes between the two R2B substeps")
    pivot["minimum_endpoint"] = pivot[[1, 2]].min(axis=1)
    chosen = pivot.nlargest(2, "minimum_endpoint").reset_index()
    chosen.columns = [
        "macro_index",
        "micro_index",
        "J_substep_1",
        "J_substep_2",
        "minimum_endpoint",
    ]
    chosen["shape_lane"] = SHAPES[0]
    chosen["interval_index"] = 0
    chosen["group"] = "G1"
    chosen.to_csv(stage / "data/constructive_witness_selected_nodes.csv", index=False)

    node_tv_rows: list[dict[str, Any]] = []
    for interval in range(5):
        for substep in [1, 2]:
            for macro_index in range(18):
                for group in ACTIVE_GROUPS:
                    distributions: dict[str, np.ndarray] = {}
                    for shape in SHAPES:
                        values = node_distributions[(shape, interval, substep, macro_index, group)]
                        if np.count_nonzero(values) != 2560 or values.sum() <= 0.0:
                            raise RuntimeError((shape, interval, substep, macro_index, group))
                        distributions[shape] = values / values.sum()
                    for shape_a, shape_b in itertools.combinations(SHAPES, 2):
                        delta = np.abs(distributions[shape_a] - distributions[shape_b])
                        node_tv_rows.append({
                            "interval_index": interval,
                            "substep": substep,
                            "macro_index": macro_index,
                            "group": group,
                            "shape_a": shape_a,
                            "shape_b": shape_b,
                            "node_count": 2560,
                            "total_variation": 0.5 * float(delta.sum()),
                            "l1_distance": float(delta.sum()),
                            "same_macro_group_total_by_construction": True,
                        })
    node_tv = pd.DataFrame(node_tv_rows)
    node_tv.to_csv(stage / "data/shape_node_allocation_pairwise_tv.csv", index=False)

    if total_rows != 2_764_800:
        raise RuntimeError(f"Unexpected node-group row count: {total_rows}")
    return inventory, chosen, node_tv


def witness_tables(stage: Path, chosen: pd.DataFrame, global_lock: pd.DataFrame) -> dict[str, Any]:
    s = np.linspace(0.0, 1.0, 1001)
    dt_myr = float(
        global_lock.loc[global_lock.interval_index.eq(0), "dt_Myr"].sum()
    )
    dt_s = dt_myr * MYR_S
    t_s = s * dt_s

    first = chosen.iloc[0]
    j0, j1 = float(first.J_substep_1), float(first.J_substep_2)
    baseline = (1.0 - s) * j0 + s * j1
    g = s * (1.0 - s) * (s - 0.5)
    amplitude = 0.2 * min(j0, j1) / np.max(np.abs(g))
    plus = baseline + amplitude * g
    minus = baseline - amplitude * g
    temporal = pd.DataFrame(
        {
            "s": s,
            "time_s": t_s,
            "baseline_J": baseline,
            "null_shape_g": g,
            "plus_J": plus,
            "minus_J": minus,
        }
    )
    temporal.to_csv(stage / "data/temporal_null_witness.csv", index=False)
    base_int = float(np.trapezoid(baseline, t_s))
    plus_int = float(np.trapezoid(plus, t_s))
    minus_int = float(np.trapezoid(minus, t_s))

    arow, brow = chosen.iloc[0], chosen.iloc[1]
    a0, a1 = float(arow.J_substep_1), float(arow.J_substep_2)
    b0, b1 = float(brow.J_substep_1), float(brow.J_substep_2)
    abase = (1.0 - s) * a0 + s * a1
    bbase = (1.0 - s) * b0 + s * b1
    f = s * (1.0 - s)
    spatial_amplitude = 0.1 * min(a0, a1, b0, b1) / np.max(f)
    aprime = abase + spatial_amplitude * f
    bprime = bbase - spatial_amplitude * f
    spatial = pd.DataFrame(
        {
            "s": s,
            "time_s": t_s,
            "node_a_baseline_J": abase,
            "node_b_baseline_J": bbase,
            "partition_shape_f": f,
            "node_a_redistributed_J": aprime,
            "node_b_redistributed_J": bprime,
            "baseline_pointwise_total_J": abase + bbase,
            "redistributed_pointwise_total_J": aprime + bprime,
        }
    )
    spatial.to_csv(stage / "data/spatial_partition_null_witness.csv", index=False)

    summary = {
        "classification": "R2C_R1B_CONSTRUCTIVE_POSITIVE_NULL_WITNESS",
        "duration_Myr": dt_myr,
        "temporal": {
            "shape": "g(s)=s(1-s)(s-1/2)",
            "endpoint_residual_max": float(
                max(abs(plus[0] - baseline[0]), abs(plus[-1] - baseline[-1]))
            ),
            "integral_relative_residual_plus": float(relative_residual(plus_int, base_int)),
            "integral_relative_residual_minus": float(relative_residual(minus_int, base_int)),
            "minimum_plus_J": float(plus.min()),
            "minimum_minus_J": float(minus.min()),
            "interior_max_relative_separation": float(
                np.max(np.abs(plus - minus) / np.maximum(baseline, np.finfo(float).tiny))
            ),
        },
        "spatial": {
            "shape": "f(s)=s(1-s)",
            "pointwise_total_relative_residual_max": float(
                np.max(relative_residual(aprime + bprime, abase + bbase))
            ),
            "endpoint_residual_max": float(
                max(
                    abs(aprime[0] - abase[0]),
                    abs(aprime[-1] - abase[-1]),
                    abs(bprime[0] - bbase[0]),
                    abs(bprime[-1] - bbase[-1]),
                )
            ),
            "node_a_integrated_count_change": float(
                np.trapezoid(aprime - abase, t_s)
            ),
            "node_b_integrated_count_change": float(
                np.trapezoid(bprime - bbase, t_s)
            ),
            "integrated_change_sum_relative_to_total": float(
                abs(
                    np.trapezoid(aprime - abase, t_s)
                    + np.trapezoid(bprime - bbase, t_s)
                )
                / max(abs(np.trapezoid(abase + bbase, t_s)), np.finfo(float).tiny)
            ),
            "minimum_redistributed_J": float(min(aprime.min(), bprime.min())),
        },
    }
    (stage / "data/constructive_witness_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    return summary


def thermal_moment_audit(stage: Path, repo: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    sys.path.insert(0, str(repo / "src/rei_bianchi"))
    from absorption_decomposition import normalized_group_quadrature  # type: ignore
    from b2b_physical_model import make_spectrum_lanes  # type: ignore
    from multigroup_hhe_transmission import GROUPS, verner_sigma  # type: ignore

    lane = make_spectrum_lanes()["MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD"]
    group_names = ["G1", "G2a", "G2b", "G3"]
    columns = [0.0, 1.0e16, 1.0e17, 1.0e18, 1.0e19, math.inf]
    rows: list[dict[str, Any]] = []
    moment_lookup: dict[str, dict[str, float]] = {}
    for idx, group in enumerate(group_names):
        bounds = GROUPS[group]
        energy, weight = normalized_group_quadrature(group, 512)
        sigma = np.asarray(verner_sigma("HI", energy), dtype=float)
        threshold = 13.60
        excess = np.maximum(energy - threshold, 0.0)
        source_mean = float(np.sum(weight * excess))
        thin_denom = float(np.sum(weight * sigma))
        thin = 0.0 if thin_denom <= 0 else float(np.sum(weight * sigma * excess) / thin_denom)
        record: dict[str, Any] = {
            "group": group,
            "low_eV": float(bounds[0]),
            "high_eV": float(bounds[1]),
            "primary_source_fraction": float(lane.source_fraction[idx]),
            "primary_source_exact_zero": bool(lane.source_fraction[idx] == 0.0),
            "number_weighted_mean_photon_energy_eV": float(np.sum(weight * energy)),
            "number_weighted_mean_HI_excess_eV": source_mean,
            "optically_thin_sigma_weighted_HI_excess_eV": thin,
            "optically_thick_HI_excess_eV": source_mean,
            "possible_group_excess_min_eV": max(float(bounds[0]) - threshold, 0.0),
            "possible_group_excess_max_eV": max(float(bounds[1]) - threshold, 0.0),
            "production_status": "SPECTRAL_AUDITOR_NOT_DYNAMIC_HEATING_LOCK",
        }
        for column in columns:
            label = "infinite" if math.isinf(column) else f"{column:.0e}"
            if math.isinf(column):
                absorb = np.ones_like(sigma)
            elif column == 0.0:
                absorb = sigma
            else:
                absorb = -np.expm1(-np.clip(sigma * column, 0.0, 745.0))
            denom = float(np.sum(weight * absorb))
            value = 0.0 if denom <= 0 else float(np.sum(weight * absorb * excess) / denom)
            record[f"absorbed_excess_NHI_{label}_cm_minus_2_eV"] = value
        rows.append(record)
        moment_lookup[group] = {
            "thin": thin,
            "thick": source_mean,
        }
    moments = pd.DataFrame(rows)
    moments.to_csv(stage / "data/thermal_group_moment_audit.csv", index=False)

    direct = pd.read_csv(stage / "data/input_canonical_direct_photon_ledger.csv")
    heating_rows: list[dict[str, Any]] = []
    for row in direct.itertuples(index=False):
        thin_total = 0.0
        thick_total = 0.0
        for group in ["G1", "G2a", "G2b", "G3"]:
            rate = float(getattr(row, f"absorption_{group}_rate"))
            thin_power = rate * moment_lookup[group]["thin"] * EV_ERG
            thick_power = rate * moment_lookup[group]["thick"] * EV_ERG
            thin_total += thin_power
            thick_total += thick_power
            heating_rows.append(
                {
                    "interval_index": int(row.interval_index),
                    "z_mid": float(row.z_mid),
                    "group": group,
                    "absorbed_photon_rate_s_inv_cMpc3": rate,
                    "thin_atomic_HI_heating_erg_s_inv_cMpc3": thin_power,
                    "thick_atomic_HI_heating_erg_s_inv_cMpc3": thick_power,
                    "heating_difference_fraction_of_max": abs(thick_power - thin_power)
                    / max(abs(thin_power), abs(thick_power), np.finfo(float).tiny),
                    "production_status": "AUDITOR_ENVELOPE_ONLY",
                }
            )
        heating_rows.append(
            {
                "interval_index": int(row.interval_index),
                "z_mid": float(row.z_mid),
                "group": "TOTAL",
                "absorbed_photon_rate_s_inv_cMpc3": float(row.ionized_absorption_rate),
                "thin_atomic_HI_heating_erg_s_inv_cMpc3": thin_total,
                "thick_atomic_HI_heating_erg_s_inv_cMpc3": thick_total,
                "heating_difference_fraction_of_max": abs(thick_total - thin_total)
                / max(abs(thin_total), abs(thick_total), np.finfo(float).tiny),
                "production_status": "AUDITOR_ENVELOPE_ONLY",
            }
        )
    heating = pd.DataFrame(heating_rows)
    heating.to_csv(stage / "data/thermal_interval_heating_envelope.csv", index=False)
    return moments, heating


def state_row_count(state_path: Path, chunksize: int) -> dict[str, Any]:
    cols = [
        "shape_lane",
        "interval_index",
        "substep",
        "macro_index",
        "micro_index",
        "M_sink_H_node_cMpc3",
        "xHII_lift",
        "T_lift_K",
    ]
    count = 0
    nonfinite = 0
    cone_fail = 0
    for chunk in pd.read_csv(state_path, usecols=cols, chunksize=chunksize):
        count += len(chunk)
        m = chunk.M_sink_H_node_cMpc3.to_numpy(float)
        x = chunk.xHII_lift.to_numpy(float)
        t = chunk.T_lift_K.to_numpy(float)
        nonfinite += int(np.count_nonzero(~np.isfinite(m) | ~np.isfinite(x) | ~np.isfinite(t)))
        cone_fail += int(np.count_nonzero((m < 0.0) | (x < 0.0) | (x > 1.0) | (t <= 0.0)))
    if count != 1_382_400:
        raise RuntimeError(f"Unexpected state row count: {count}")
    return {
        "state_rows": count,
        "nonfinite_state_rows": nonfinite,
        "endpoint_state_cone_failures": cone_fail,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--groups", type=Path, required=True)
    parser.add_argument("--chunksize", type=int, default=250_000)
    args = parser.parse_args()

    repo = args.repo.resolve()
    stage = args.stage.resolve()
    (stage / "data").mkdir(parents=True, exist_ok=True)

    r2a = repo / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2A_GLOBAL_MOMENT_CONSTRAINED_MACRO_SINK_DISTRIBUTION_LOCK/data"
    global_lock = pd.read_csv(r2a / "global_moment_lock.csv")
    macro = pd.read_csv(r2a / "macro_projection.csv")

    inventory = write_inventory(stage, repo)
    partition = global_partition(stage, global_lock)
    tv = macro_pairwise_tv(stage, macro)
    rank = rank_nullity_table(stage)
    endpoint_inventory, chosen, node_tv = scan_node_groups(stage, args.groups, args.chunksize)
    witnesses = witness_tables(stage, chosen, global_lock)
    moments, heating = thermal_moment_audit(stage, repo)
    state_stats = state_row_count(args.state, args.chunksize)

    sink_ratio_min = float(partition.sink_to_global_low_ratio.min())
    sink_ratio_max = float(partition.sink_to_global_low_ratio.max())
    tv_current = tv[tv.quantity.isin(["G1_CURRENT", "G2a_CURRENT"])]
    total_heating = heating[heating.group.eq("TOTAL")]
    summary = {
        "classification": "R2C_R1B_FORCING_IDENTIFIABILITY_AUDIT",
        "generated_utc": utc_now(),
        "conventions": {
            "metric_signature": "(-,+,+,+)",
            "epsilon_123": "+1",
            "natural_units": False,
            "constants_explicit": ["c", "hbar", "k_B"],
        },
        "input_hashes": {
            "node_state_lift_sha256": sha256_file(args.state),
            "node_group_lift_sha256": sha256_file(args.groups),
        },
        **state_stats,
        "node_group_rows": int(endpoint_inventory.node_rows.sum()),
        "endpoint_group_case_rows": int(len(endpoint_inventory)),
        "negative_node_current_rows": int(endpoint_inventory.negative_J_rows.sum()),
        "negative_node_opacity_rows": int(endpoint_inventory.negative_kappa_rows.sum()),
        "nonpositive_node_flux_rows": int(endpoint_inventory.nonpositive_Phi_rows.sum()),
        "max_endpoint_J_equals_kappa_Phi_relative_residual": float(
            endpoint_inventory.max_J_equals_kappa_Phi_relative_residual.max()
        ),
        "sink_to_global_low_group_ratio_min": sink_ratio_min,
        "sink_to_global_low_group_ratio_max": sink_ratio_max,
        "macro_current_pairwise_TV_min": float(tv_current.total_variation.min()),
        "macro_current_pairwise_TV_max": float(tv_current.total_variation.max()),
        "node_current_pairwise_TV_min": float(node_tv.total_variation.min()),
        "node_current_pairwise_TV_median": float(node_tv.total_variation.median()),
        "node_current_pairwise_TV_max": float(node_tv.total_variation.max()),
        "constraint_nullity_single_history_K8": int(
            rank[
                rank.family.eq("SINGLE_NODE_ENDPOINTS_PLUS_ONE_INTERVAL_INTEGRAL")
                & rank.time_knot_count.eq(8)
            ].nullity.iloc[0]
        ),
        "constraint_nullity_46080_nodes_K8": int(
            rank[
                rank.family.eq("NODE_ENDPOINTS_PLUS_POINTWISE_MACRO_TOTAL")
                & rank.node_count.eq(46080)
                & rank.time_knot_count.eq(8)
            ].nullity.iloc[0]
        ),
        "temporal_positive_null_witness_pass": bool(
            witnesses["temporal"]["minimum_plus_J"] > 0.0
            and witnesses["temporal"]["minimum_minus_J"] > 0.0
            and witnesses["temporal"]["integral_relative_residual_plus"] < 1.0e-12
            and witnesses["temporal"]["integral_relative_residual_minus"] < 1.0e-12
        ),
        "spatial_positive_partition_null_witness_pass": bool(
            witnesses["spatial"]["minimum_redistributed_J"] > 0.0
            and witnesses["spatial"]["pointwise_total_relative_residual_max"] < 1.0e-12
            and abs(witnesses["spatial"]["node_a_integrated_count_change"]) > 0.0
        ),
        "thermal_primary_spectrum_prior_present": True,
        "thermal_dynamic_absorbed_spectrum_identified": False,
        "thermal_total_thin_vs_thick_difference_fraction_min": float(
            total_heating.heating_difference_fraction_of_max.min()
        ),
        "thermal_total_thin_vs_thick_difference_fraction_max": float(
            total_heating.heating_difference_fraction_of_max.max()
        ),
        "input_inventory_rows": int(len(inventory)),
        "identifiability_verdict": "UNDERIDENTIFIED_NODE_GROUP_FORCING_DYNAMIC_OPACITY_AND_THERMAL_HISTORY",
        "not_a_claim_of": [
            "physical nonexistence",
            "numerical nonconvergence",
            "failure of global photon conservation",
            "need for an immediate larger coupled generator",
        ],
        "next_smallest_action": "CANONICAL_TIME_RESOLVED_GROUP_BOUNDARY_FLUX_DYNAMIC_OPACITY_AND_HEATING_MOMENT_EXTRACTION_LOCK",
    }
    (stage / "data/summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
