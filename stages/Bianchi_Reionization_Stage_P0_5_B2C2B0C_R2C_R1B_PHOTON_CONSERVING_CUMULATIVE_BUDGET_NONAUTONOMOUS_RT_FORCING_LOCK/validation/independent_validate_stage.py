#!/usr/bin/env python3
"""Independent validation of R2C-R1B durable evidence.

This implementation does not import the producer script.  It re-reads the
canonical inputs and emitted tables, recomputes the key identities, and
fails on any status-changing discrepancy.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

MYR_S = 1.0e6 * 365.25 * 86400.0
RTOL = 2.0e-11
SHAPES = [
    "LOCAL_NEUTRAL_HAZARD_PRIMARY",
    "RECOMBINATION_WEIGHTED_AUDITOR",
    "SCRIPT_SELF_SHIELDING_AUDITOR",
]


def rel(a: float, b: float) -> float:
    return abs(a - b) / max(abs(a), abs(b), np.finfo(float).tiny)


def power_integral(lo: float, hi: float, exponent: float) -> float:
    p = exponent + 1.0
    if abs(p) < 1.0e-15:
        return math.log(hi / lo)
    return (hi**p - lo**p) / p


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--stage", type=Path, required=True)
    ap.add_argument("--groups", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    repo, stage = args.repo.resolve(), args.stage.resolve()
    summary = json.loads((stage / "data/summary.json").read_text())
    r2a = repo / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2A_GLOBAL_MOMENT_CONSTRAINED_MACRO_SINK_DISTRIBUTION_LOCK/data"
    glock = pd.read_csv(r2a / "global_moment_lock.csv")
    direct = pd.read_csv(stage / "data/input_canonical_direct_photon_ledger.csv")
    partition = pd.read_csv(stage / "data/global_sink_ledger_partition.csv")

    partition_residuals = []
    for interval in range(5):
        sub = glock[glock.interval_index.eq(interval)]
        weights = sub.dt_Myr.to_numpy(float)
        sink = float(np.average(sub.J_sink_G1_global_s_inv_cMpc3 + sub.J_sink_G2a_global_s_inv_cMpc3, weights=weights))
        d = direct[direct.interval_index.eq(interval)].iloc[0]
        global_low = float(d.absorption_G1_rate + d.absorption_G2a_rate)
        row = partition[partition.interval_index.eq(interval)].iloc[0]
        partition_residuals.extend([
            rel(sink, float(row.sink_low_group_rate)),
            rel(global_low, float(row.global_low_group_rate)),
            rel(sink / global_low, float(row.sink_to_global_low_ratio)),
        ])

    rank = pd.read_csv(stage / "data/constraint_rank_nullity.csv")
    rank_failures = 0
    for row in rank.itertuples(index=False):
        if row.family == "SINGLE_NODE_ENDPOINTS_PLUS_ONE_INTERVAL_INTEGRAL":
            expected = row.time_knot_count - 3
        else:
            expected = (row.node_count - 1) * (row.time_knot_count - 2)
        rank_failures += int(int(row.nullity) != int(expected))

    temporal = pd.read_csv(stage / "data/temporal_null_witness.csv")
    spatial = pd.read_csv(stage / "data/spatial_partition_null_witness.csv")
    temporal_base = float(np.trapezoid(temporal.baseline_J, temporal.time_s))
    temporal_plus = float(np.trapezoid(temporal.plus_J, temporal.time_s))
    temporal_minus = float(np.trapezoid(temporal.minus_J, temporal.time_s))
    temporal_integral_resid = max(rel(temporal_base, temporal_plus), rel(temporal_base, temporal_minus))
    temporal_endpoint_resid = max(
        abs(temporal.plus_J.iloc[0] - temporal.baseline_J.iloc[0]),
        abs(temporal.plus_J.iloc[-1] - temporal.baseline_J.iloc[-1]),
        abs(temporal.minus_J.iloc[0] - temporal.baseline_J.iloc[0]),
        abs(temporal.minus_J.iloc[-1] - temporal.baseline_J.iloc[-1]),
    )
    spatial_total_resid = float(
        np.max(
            np.abs(spatial.redistributed_pointwise_total_J - spatial.baseline_pointwise_total_J)
            / np.maximum(np.abs(spatial.baseline_pointwise_total_J), np.finfo(float).tiny)
        )
    )
    spatial_count_change_sum = float(
        np.trapezoid(spatial.node_a_redistributed_J - spatial.node_a_baseline_J, spatial.time_s)
        + np.trapezoid(spatial.node_b_redistributed_J - spatial.node_b_baseline_J, spatial.time_s)
    )

    moments = pd.read_csv(stage / "data/thermal_group_moment_audit.csv")
    group_bounds = {"G1": (13.60, 24.59), "G2a": (24.59, 39.50), "G2b": (39.50, 54.42), "G3": (54.42, 100.0)}
    source_norms = {}
    for group, (lo, hi) in group_bounds.items():
        source_hi = min(hi, 54.42)
        source_norms[group] = 0.0 if source_hi <= lo else power_integral(lo, source_hi, -2.5)
    total_norm = sum(source_norms.values())
    spectral_residuals = []
    for row in moments.itertuples(index=False):
        lo, hi = group_bounds[row.group]
        mean_e = power_integral(lo, hi, -1.5) / power_integral(lo, hi, -2.5)
        spectral_residuals.append(rel(mean_e, float(row.number_weighted_mean_photon_energy_eV)))
        expected_fraction = source_norms[row.group] / total_norm
        spectral_residuals.append(rel(expected_fraction, float(row.primary_source_fraction)))
        if not (
            row.possible_group_excess_min_eV - 1e-13
            <= row.optically_thin_sigma_weighted_HI_excess_eV
            <= row.possible_group_excess_max_eV + 1e-13
        ):
            spectral_residuals.append(1.0)
        if not (
            row.possible_group_excess_min_eV - 1e-13
            <= row.optically_thick_HI_excess_eV
            <= row.possible_group_excess_max_eV + 1e-13
        ):
            spectral_residuals.append(1.0)

    node_inventory = pd.read_csv(stage / "data/node_group_endpoint_inventory.csv")
    node_tv = pd.read_csv(stage / "data/shape_node_allocation_pairwise_tv.csv")
    endpoint_rel_max = float(node_inventory.max_J_equals_kappa_Phi_relative_residual.max())
    count_ok = int(node_inventory.node_rows.sum()) == 2_764_800
    sign_ok = int(node_inventory.negative_J_rows.sum() + node_inventory.negative_kappa_rows.sum() + node_inventory.nonpositive_Phi_rows.sum()) == 0
    tv_ok = bool(
        len(node_tv) == 1080
        and node_tv.total_variation.min() > 0.0
        and node_tv.total_variation.max() < 1.0
    )

    exact = json.loads((stage / "data/exact_symbolic_fallback_report.json").read_text())
    plugin = json.loads((stage / "receipts/WOLFRAM_PLUGIN_SYMBOLIC_VALIDATION.json").read_text())
    precise = json.loads((stage / "receipts/PRECISE_SPECIAL_FUNCTIONS_AUDIT.json").read_text())

    checks = {
        "partition_replay_max_relative_residual": max(partition_residuals),
        "rank_formula_failures": rank_failures,
        "temporal_integral_relative_residual": temporal_integral_resid,
        "temporal_endpoint_absolute_residual": temporal_endpoint_resid,
        "temporal_minimum_current": float(min(temporal.plus_J.min(), temporal.minus_J.min())),
        "spatial_pointwise_total_relative_residual": spatial_total_resid,
        "spatial_integrated_change_sum_absolute": abs(spatial_count_change_sum),
        "spatial_minimum_current": float(min(spatial.node_a_redistributed_J.min(), spatial.node_b_redistributed_J.min())),
        "spectral_analytic_replay_max_relative_residual": max(spectral_residuals),
        "node_endpoint_relation_max_relative_residual": endpoint_rel_max,
        "node_group_count_ok": count_ok,
        "node_signs_ok": sign_ok,
        "node_shape_TV_table_ok": tv_ok,
        "exact_fallback_pass": bool(exact["pass"]),
        "wolfram_plugin_pass": bool(plugin["result"]["LedgerResidualAfterSubstitution"] == 0),
        "precise_plugin_executed": bool(precise["plugin_executed"]),
        "verdict_string_ok": summary["identifiability_verdict"] == "UNDERIDENTIFIED_NODE_GROUP_FORCING_DYNAMIC_OPACITY_AND_THERMAL_HISTORY",
    }
    passed = bool(
        checks["partition_replay_max_relative_residual"] < 1e-14
        and checks["rank_formula_failures"] == 0
        and checks["temporal_integral_relative_residual"] < 1e-12
        and checks["temporal_endpoint_absolute_residual"] == 0.0
        and checks["temporal_minimum_current"] > 0.0
        and checks["spatial_pointwise_total_relative_residual"] < 1e-12
        and checks["spatial_integrated_change_sum_absolute"] < 1e45
        and checks["spatial_minimum_current"] > 0.0
        and checks["spectral_analytic_replay_max_relative_residual"] < 2e-12
        and checks["node_endpoint_relation_max_relative_residual"] < RTOL
        and count_ok and sign_ok and tv_ok
        and checks["exact_fallback_pass"]
        and checks["wolfram_plugin_pass"]
        and checks["precise_plugin_executed"]
        and checks["verdict_string_ok"]
    )
    report = {
        "classification": "R2C_R1B_INDEPENDENT_VALIDATION",
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "checks": checks,
        "pass": passed,
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
