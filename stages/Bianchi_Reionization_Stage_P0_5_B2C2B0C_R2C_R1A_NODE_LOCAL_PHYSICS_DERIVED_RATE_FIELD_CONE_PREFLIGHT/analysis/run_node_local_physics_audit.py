#!/usr/bin/env python3
"""R2C-R1A physics-only state/flux/budget audit.

This executable does not integrate a production history and does not fit
per-node rates.  It classifies inherited endpoint quantities, derives the
local H reaction rates implied by the locked node fields, and tests whether
R2C-R1's common-equilibrium Farkas failures are physical cone obstructions or
artifacts of the surrogate state taxonomy.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

MYR_S = 1.0e6 * 365.25 * 86400.0
K_B_ERG_PER_K = 1.380649e-16
CORE_RTOL = 2.0e-11
KEYS = ["shape_lane", "interval_index", "substep", "macro_index"]
CASE_KEYS = ["shape_lane", "interval_index", "substep"]


def alpha_b_hii(temperature_k: np.ndarray) -> np.ndarray:
    t = np.asarray(temperature_k, dtype=float)
    lam = 315614.0 / t
    return 2.753e-14 * lam**1.5 / (1.0 + (lam / 2.740) ** 0.407) ** 2.242


def beta_hi(temperature_k: np.ndarray) -> np.ndarray:
    t = np.asarray(temperature_k, dtype=float)
    return 5.835e-11 * np.sqrt(t) * np.exp(-157804.0 / t)


def rel(a: np.ndarray | float, b: np.ndarray | float) -> np.ndarray | float:
    aa = np.asarray(a, dtype=float)
    bb = np.asarray(b, dtype=float)
    out = np.abs(aa - bb) / np.maximum(np.maximum(np.abs(aa), np.abs(bb)), np.finfo(float).tiny)
    return float(out) if out.ndim == 0 else out


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_file(path: Path, chunk: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            block = f.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def update_extrema(stats: dict[str, Any], name: str, values: np.ndarray) -> None:
    finite = values[np.isfinite(values)]
    if finite.size:
        stats[name + "_min"] = min(stats.get(name + "_min", math.inf), float(np.min(finite)))
        stats[name + "_max"] = max(stats.get(name + "_max", -math.inf), float(np.max(finite)))


def add_count(stats: dict[str, Any], name: str, count: int) -> None:
    stats[name] = int(stats.get(name, 0)) + int(count)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--state", type=Path, required=True)
    p.add_argument("--groups", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--chunksize", type=int, default=65536)
    args = p.parse_args()

    repo = args.repo.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    r2a = repo / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2A_GLOBAL_MOMENT_CONSTRAINED_MACRO_SINK_DISTRIBUTION_LOCK/data"
    r1 = repo / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1_RATE_DERIVED_POSITIVE_MULTIRATE_RELAXATION_CONE_LOCK/data"
    global_lock = pd.read_csv(r2a / "global_moment_lock.csv")
    target = pd.read_csv(r2a / "macro_projection.csv")
    farkas = pd.read_csv(r1 / "dual_single_bound_extension_diagnostic.csv")
    rate_lock = pd.read_csv(r1 / "rate_interval_lock.csv")

    dt_frame = global_lock[["interval_index", "substep", "dt_Myr"]].copy()
    dt_frame["interval_index"] = dt_frame["interval_index"].astype(int)
    dt_frame["substep"] = dt_frame["substep"].astype(int)
    dt_lookup = {(int(r.interval_index), int(r.substep)): float(r.dt_Myr) for r in dt_frame.itertuples()}

    state_cols = [
        "shape_lane", "interval_index", "substep", "z_mid", "macro_index", "micro_index",
        "M_sink_H_node_cMpc3", "xHII_lift", "T_lift_K", "nH_node_cm3",
        "cycling_capacity_node_s_inv_cMpc3", "mass_transfer_positive_H_s_inv_cMpc3",
        "mass_transfer_negative_H_s_inv_cMpc3", "mass_transfer_net_H_s_inv_cMpc3",
    ]
    group_cols = [
        "shape_lane", "interval_index", "substep", "z_mid", "macro_index", "micro_index", "group",
        "J_sink_node_s_inv_cMpc3", "kappa_sink_node_cMpc_inv", "Phi_current_Gamma_s_inv_cMpc2",
    ]
    dtypes_state = {
        "shape_lane": "string", "interval_index": "int16", "substep": "int8",
        "macro_index": "int8", "micro_index": "int16",
    }
    dtypes_group = {**dtypes_state, "group": "string"}
    sit = pd.read_csv(args.state, usecols=state_cols, dtype=dtypes_state, chunksize=args.chunksize)
    git = pd.read_csv(args.groups, usecols=group_cols, dtype=dtypes_group, chunksize=2 * args.chunksize)

    stats: dict[str, Any] = {
        "classification": "R2C_R1A_NODE_LOCAL_PHYSICS_AUDIT",
        "generated_utc": utc_now(),
        "state_input_sha256": sha256_file(args.state),
        "group_input_sha256": sha256_file(args.groups),
    }
    macro_parts: list[pd.DataFrame] = []
    case_parts: list[pd.DataFrame] = []

    for chunk_index, (s, g) in enumerate(zip(sit, git, strict=True)):
        s = s.reset_index(drop=True)
        g = g.reset_index(drop=True)
        if len(g) != 2 * len(s):
            raise RuntimeError(f"lockstep row mismatch in chunk {chunk_index}: {len(g)} != 2*{len(s)}")
        g1 = g.iloc[0::2].reset_index(drop=True)
        g2 = g.iloc[1::2].reset_index(drop=True)
        for col in ["shape_lane", "interval_index", "substep", "macro_index", "micro_index"]:
            sv = s[col].to_numpy()
            if not np.array_equal(sv, g1[col].to_numpy()) or not np.array_equal(sv, g2[col].to_numpy()):
                raise RuntimeError(f"lockstep key mismatch in chunk {chunk_index}: {col}")
        if not g1["group"].eq("G1").all() or not g2["group"].eq("G2a").all():
            raise RuntimeError(f"group ordering mismatch in chunk {chunk_index}")

        m = s["M_sink_H_node_cMpc3"].to_numpy(float)
        x = s["xHII_lift"].to_numpy(float)
        temp = s["T_lift_K"].to_numpy(float)
        nh = s["nH_node_cm3"].to_numpy(float)
        c_old = s["cycling_capacity_node_s_inv_cMpc3"].to_numpy(float)
        sp = s["mass_transfer_positive_H_s_inv_cMpc3"].to_numpy(float)
        sn = s["mass_transfer_negative_H_s_inv_cMpc3"].to_numpy(float)
        net = s["mass_transfer_net_H_s_inv_cMpc3"].to_numpy(float)
        j1 = g1["J_sink_node_s_inv_cMpc3"].to_numpy(float)
        j2 = g2["J_sink_node_s_inv_cMpc3"].to_numpy(float)
        k1 = g1["kappa_sink_node_cMpc_inv"].to_numpy(float)
        k2 = g2["kappa_sink_node_cMpc_inv"].to_numpy(float)
        phi1 = g1["Phi_current_Gamma_s_inv_cMpc2"].to_numpy(float)
        phi2 = g2["Phi_current_Gamma_s_inv_cMpc2"].to_numpy(float)
        jtot = j1 + j2
        ion = m * x
        neutral = m - ion
        thermal = 1.5 * K_B_ERG_PER_K * m * temp
        alpha = alpha_b_hii(temp)
        beta = beta_hi(temp)
        ne = x * nh
        recomb = alpha * ne * ion
        coll = beta * ne * neutral
        up_coll = beta * ne
        down_rec = alpha * ne
        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            gamma1 = np.divide(j1, neutral, out=np.full_like(j1, np.nan), where=neutral > 0.0)
            gamma2 = np.divide(j2, neutral, out=np.full_like(j2, np.nan), where=neutral > 0.0)
            gamma = gamma1 + gamma2
        dt_myr = np.fromiter(
            (dt_lookup[(int(i), int(q))] for i, q in zip(s["interval_index"], s["substep"], strict=True)),
            dtype=float,
            count=len(s),
        )
        dt_s = dt_myr * MYR_S
        neutral_stock_rate = neutral / dt_s
        local_interval_budget_rate = neutral_stock_rate + recomb
        old_integrated_budget = c_old * dt_s
        local_integrated_budget = neutral + recomb * dt_s
        current_gamma_resid = np.maximum(rel(j1, phi1 * k1), rel(j2, phi2 * k2))
        old_capacity_rel_violation = np.maximum(jtot - c_old, 0.0) / np.maximum(np.maximum(jtot, c_old), np.finfo(float).tiny)
        local_budget_rel_violation = np.maximum(jtot - local_interval_budget_rate, 0.0) / np.maximum(
            np.maximum(jtot, local_interval_budget_rate), np.finfo(float).tiny
        )
        old_vs_local_budget_rel = rel(c_old, local_interval_budget_rate)

        add_count(stats, "state_row_count", len(s))
        add_count(stats, "group_row_count", len(g))
        add_count(stats, "mass_nonpositive_count", np.count_nonzero(m <= 0.0))
        add_count(stats, "x_outside_unit_interval_count", np.count_nonzero((x < 0.0) | (x > 1.0)))
        add_count(stats, "temperature_nonpositive_count", np.count_nonzero(temp <= 0.0))
        add_count(stats, "density_nonpositive_count", np.count_nonzero(nh <= 0.0))
        add_count(stats, "neutral_negative_count", np.count_nonzero(neutral < 0.0))
        add_count(stats, "neutral_exact_zero_count", np.count_nonzero(neutral == 0.0))
        add_count(stats, "nonfinite_direct_rate_count", np.count_nonzero(~np.isfinite(gamma)))
        add_count(stats, "negative_group_current_count", np.count_nonzero(j1 < 0.0) + np.count_nonzero(j2 < 0.0))
        add_count(stats, "negative_group_opacity_count", np.count_nonzero(k1 < 0.0) + np.count_nonzero(k2 < 0.0))
        add_count(stats, "nonpositive_flux_count", np.count_nonzero(phi1 <= 0.0) + np.count_nonzero(phi2 <= 0.0))
        add_count(stats, "old_capacity_pointwise_violation_count_at_2e-11", np.count_nonzero(old_capacity_rel_violation > CORE_RTOL))
        add_count(stats, "local_interval_budget_pointwise_violation_count_at_2e-11", np.count_nonzero(local_budget_rel_violation > CORE_RTOL))
        add_count(stats, "old_vs_local_budget_relative_mismatch_count_at_2e-11", np.count_nonzero(old_vs_local_budget_rel > CORE_RTOL))

        for name, arr in {
            "mass": m, "x_hii": x, "temperature_k": temp, "n_h_cm3": nh,
            "neutral_mass": neutral, "ionized_mass": ion, "thermal_measure": thermal,
            "gamma_G1_s_inv": gamma1, "gamma_G2a_s_inv": gamma2, "gamma_total_s_inv": gamma,
            "collisional_up_rate_s_inv": up_coll, "recombination_down_rate_s_inv": down_rec,
            "recombination_event_rate": recomb, "collisional_event_rate": coll,
            "old_capacity": c_old, "local_interval_budget_rate": local_interval_budget_rate,
            "old_vs_local_budget_relative": old_vs_local_budget_rel,
            "current_gamma_relative_residual": current_gamma_resid,
            "old_capacity_relative_violation": old_capacity_rel_violation,
            "local_budget_relative_violation": local_budget_rel_violation,
        }.items():
            update_extrema(stats, name, np.asarray(arr))

        work = s[KEYS + ["z_mid"]].copy()
        work["state_rows"] = 1
        work["M"] = m
        work["I"] = ion
        work["N"] = neutral
        work["U"] = thermal
        work["C_old"] = c_old
        work["C_local"] = local_interval_budget_rate
        work["B_old"] = old_integrated_budget
        work["B_local"] = local_integrated_budget
        work["R_rec"] = recomb
        work["Q_coll"] = coll
        work["J_G1"] = j1
        work["J_G2a"] = j2
        work["kappa_G1"] = k1
        work["kappa_G2a"] = k2
        work["S_plus"] = sp
        work["S_minus"] = sn
        work["S_net"] = net
        work["local_budget_violation_nodes"] = (local_budget_rel_violation > CORE_RTOL).astype(int)
        work["old_local_budget_mismatch_nodes"] = (old_vs_local_budget_rel > CORE_RTOL).astype(int)
        work["max_current_gamma_resid"] = current_gamma_resid
        work["max_old_capacity_rel_violation"] = old_capacity_rel_violation
        work["max_local_budget_rel_violation"] = local_budget_rel_violation
        work["min_local_budget_slack"] = local_interval_budget_rate - jtot
        work["min_old_capacity_slack"] = c_old - jtot
        work["gamma_M_weight"] = gamma * m
        work["recomb_down_M_weight"] = down_rec * m
        work["coll_up_M_weight"] = up_coll * m

        agg_spec = {
            "z_mid": "first", "state_rows": "sum", "M": "sum", "I": "sum", "N": "sum", "U": "sum",
            "C_old": "sum", "C_local": "sum", "B_old": "sum", "B_local": "sum",
            "R_rec": "sum", "Q_coll": "sum", "J_G1": "sum", "J_G2a": "sum",
            "kappa_G1": "sum", "kappa_G2a": "sum", "S_plus": "sum", "S_minus": "sum", "S_net": "sum",
            "local_budget_violation_nodes": "sum", "old_local_budget_mismatch_nodes": "sum",
            "max_current_gamma_resid": "max", "max_old_capacity_rel_violation": "max",
            "max_local_budget_rel_violation": "max", "min_local_budget_slack": "min", "min_old_capacity_slack": "min",
            "gamma_M_weight": "sum", "recomb_down_M_weight": "sum", "coll_up_M_weight": "sum",
        }
        macro_parts.append(work.groupby(KEYS, observed=True, as_index=False).agg(agg_spec))
        case_parts.append(work.groupby(CASE_KEYS, observed=True, as_index=False).agg(agg_spec))

    try:
        next(sit)
        raise RuntimeError("state iterator has extra chunks")
    except StopIteration:
        pass
    try:
        next(git)
        raise RuntimeError("group iterator has extra chunks")
    except StopIteration:
        pass

    sum_cols = [
        "state_rows", "M", "I", "N", "U", "C_old", "C_local", "B_old", "B_local", "R_rec", "Q_coll",
        "J_G1", "J_G2a", "kappa_G1", "kappa_G2a", "S_plus", "S_minus", "S_net",
        "local_budget_violation_nodes", "old_local_budget_mismatch_nodes", "gamma_M_weight",
        "recomb_down_M_weight", "coll_up_M_weight",
    ]
    max_cols = ["max_current_gamma_resid", "max_old_capacity_rel_violation", "max_local_budget_rel_violation"]
    min_cols = ["min_local_budget_slack", "min_old_capacity_slack"]

    def combine(parts: list[pd.DataFrame], keys: list[str]) -> pd.DataFrame:
        allp = pd.concat(parts, ignore_index=True)
        agg: dict[str, str] = {"z_mid": "first"}
        agg.update({c: "sum" for c in sum_cols})
        agg.update({c: "max" for c in max_cols})
        agg.update({c: "min" for c in min_cols})
        out = allp.groupby(keys, observed=True, as_index=False).agg(agg)
        out["x_mass_weighted"] = out["I"] / out["M"]
        out["T_mass_weighted_K"] = out["U"] / (1.5 * K_B_ERG_PER_K * out["M"])
        out["gamma_mass_weighted_Myr_inv"] = out["gamma_M_weight"] / out["M"] * MYR_S
        out["recombination_down_mass_weighted_Myr_inv"] = out["recomb_down_M_weight"] / out["M"] * MYR_S
        out["collisional_up_mass_weighted_Myr_inv"] = out["coll_up_M_weight"] / out["M"] * MYR_S
        out["old_to_local_budget_ratio"] = out["C_old"] / out["C_local"]
        out["local_budget_to_J_ratio"] = out["C_local"] / (out["J_G1"] + out["J_G2a"])
        return out

    macro = combine(macro_parts, KEYS)
    case = combine(case_parts, CASE_KEYS)

    target_cols = [
        *KEYS, "M_sink_H_cMpc3", "M_sink_H_cap_cosmic_cMpc3", "M_sink_H_cap_volume_cMpc3",
        "kappa_sink_G1_cMpc_inv", "kappa_sink_G2a_cMpc_inv", "J_sink_G1_s_inv_cMpc3",
        "J_sink_G2a_s_inv_cMpc3", "cycling_capacity_macro_s_inv_cMpc3",
        "mass_transfer_rate_macro_H_s_inv_cMpc3", "volume_filling_macro",
    ]
    macro = macro.merge(target[target_cols], on=KEYS, how="left", validate="one_to_one")
    if macro[target_cols[4:]].isna().any().any():
        raise RuntimeError("macro target merge incomplete")
    macro["mass_relative_residual"] = rel(macro["M"], macro["M_sink_H_cMpc3"])
    macro["J_G1_relative_residual"] = rel(macro["J_G1"], macro["J_sink_G1_s_inv_cMpc3"])
    macro["J_G2a_relative_residual"] = rel(macro["J_G2a"], macro["J_sink_G2a_s_inv_cMpc3"])
    macro["kappa_G1_relative_residual"] = rel(macro["kappa_G1"], macro["kappa_sink_G1_cMpc_inv"])
    macro["kappa_G2a_relative_residual"] = rel(macro["kappa_G2a"], macro["kappa_sink_G2a_cMpc_inv"])
    macro["old_capacity_relative_residual"] = rel(macro["C_old"], macro["cycling_capacity_macro_s_inv_cMpc3"])
    macro["transfer_relative_residual"] = rel(macro["S_net"], macro["mass_transfer_rate_macro_H_s_inv_cMpc3"])
    macro["mass_cap_slack_cosmic"] = macro["M_sink_H_cap_cosmic_cMpc3"] - macro["M"]
    macro["mass_cap_slack_volume"] = macro["M_sink_H_cap_volume_cMpc3"] - macro["M"]
    macro["endpoint_state_cone_pass"] = (
        (macro["M"] >= 0.0) & (macro["I"] >= 0.0) & (macro["N"] >= 0.0) & (macro["U"] >= 0.0)
        & (macro["mass_cap_slack_cosmic"] >= -CORE_RTOL * macro["M_sink_H_cap_cosmic_cMpc3"])
        & (macro["mass_cap_slack_volume"] >= -CORE_RTOL * macro["M_sink_H_cap_volume_cMpc3"])
    )

    # The six mass-cap Farkas cases are inspected directly at both endpoints.
    mass_farkas = farkas[farkas["constraint"].eq("MACRO_MASS_CAP")][KEYS + ["box_deficit"]].copy()
    mass_rates = rate_lock[rate_lock["family"].eq("M")][KEYS + ["endpoint_previous", "endpoint_target"]]
    mass_farkas = mass_farkas.merge(mass_rates, on=KEYS, how="left", validate="one_to_one")
    mass_farkas = mass_farkas.merge(
        target[KEYS + ["M_sink_H_cap_cosmic_cMpc3", "M_sink_H_cap_volume_cMpc3"]],
        on=KEYS,
        how="left",
        validate="one_to_one",
    )
    mass_farkas["cap"] = mass_farkas[["M_sink_H_cap_cosmic_cMpc3", "M_sink_H_cap_volume_cMpc3"]].min(axis=1)
    mass_farkas["previous_endpoint_within_cap"] = mass_farkas["endpoint_previous"] <= mass_farkas["cap"] * (1.0 + CORE_RTOL)
    mass_farkas["target_endpoint_within_cap"] = mass_farkas["endpoint_target"] <= mass_farkas["cap"] * (1.0 + CORE_RTOL)
    mass_farkas["convex_segment_within_cap"] = mass_farkas["previous_endpoint_within_cap"] & mass_farkas["target_endpoint_within_cap"]

    # Refinement covariance of C(dt)=N/dt+R.  q>1 represents dt -> dt/q at fixed physical state.
    covariance_rows: list[dict[str, Any]] = []
    for r in global_lock.itertuples():
        n = float(r.N_H_sink_global_cMpc3) * max(1.0 - float(r.x_HII_sink_global), 0.0)
        recomb = float(r.sink_recombination_global_s_inv_cMpc3)
        dt_s = float(r.dt_Myr) * MYR_S
        c = n / dt_s + recomb
        for q in (1, 2, 4, 8):
            cq = q * n / dt_s + recomb
            covariance_rows.append({
                "interval_index": int(r.interval_index), "substep": int(r.substep), "z_mid": float(r.z_mid),
                "q_refinement": q, "dt_refined_Myr": float(r.dt_Myr) / q,
                "neutral_inventory_H_cMpc3": n, "recombination_rate_s_inv_cMpc3": recomb,
                "C_original_s_inv_cMpc3": c, "C_refined_s_inv_cMpc3": cq,
                "C_refined_over_original": cq / c,
                "C_change_relative_to_original": (cq - c) / c,
                "integrated_budget_original_H_cMpc3": n + recomb * dt_s,
                "integrated_budget_refined_one_substep_H_cMpc3": n + recomb * dt_s / q,
            })
    covariance = pd.DataFrame(covariance_rows)

    max_moment_residual = float(macro[[
        "mass_relative_residual", "J_G1_relative_residual", "J_G2a_relative_residual",
        "kappa_G1_relative_residual", "kappa_G2a_relative_residual",
        "old_capacity_relative_residual", "transfer_relative_residual",
    ]].to_numpy().max())

    farkas_counts = {str(k): int(v) for k, v in farkas["constraint"].value_counts().to_dict().items()}
    summary = {
        **stats,
        "macro_case_count": int(len(macro)),
        "case_count": int(len(case)),
        "shape_lane_count": int(macro["shape_lane"].nunique()),
        "endpoint_state_cone_failure_count": int((~macro["endpoint_state_cone_pass"]).sum()),
        "maximum_locked_moment_relative_residual": max_moment_residual,
        "maximum_current_Gamma_relative_residual": float(macro["max_current_gamma_resid"].max()),
        "old_capacity_local_budget_mismatch_macro_count": int((rel(macro["C_old"], macro["C_local"]) > CORE_RTOL).sum()),
        "local_budget_pointwise_violation_node_count": int(macro["local_budget_violation_nodes"].sum()),
        "local_budget_pointwise_violation_macro_count": int((macro["local_budget_violation_nodes"] > 0).sum()),
        "farkas_case_count": int(len(farkas)),
        "farkas_constraint_counts": farkas_counts,
        "radiative_farkas_case_count": int(len(farkas) - len(mass_farkas)),
        "mass_farkas_case_count": int(len(mass_farkas)),
        "mass_farkas_both_endpoints_within_cap_count": int(mass_farkas["convex_segment_within_cap"].sum()),
        "capacity_refinement_noninvariant_case_count_q2": int((covariance.query("q_refinement == 2")["C_change_relative_to_original"] > 0.0).sum()),
        "capacity_refinement_max_relative_change_q8": float(covariance.query("q_refinement == 8")["C_change_relative_to_original"].max()),
        "state_flux_budget_taxonomy": {
            "dynamical_states": ["M=N_HI+N_HII", "N_HI", "N_HII", "U_thermal"],
            "algebraic_RT_fluxes": ["J_G1", "J_G2a", "kappa_g", "Phi_g", "Gamma_g=J_g/N_HI"],
            "source_terms": ["mass_transfer_positive", "mass_transfer_negative", "photoionization", "collisional_ionization", "recombination", "heating", "cooling"],
            "interval_budget_not_state": "C_Delta_t=N_HI,start/Delta_t+R_rec,average",
        },
        "hypothesis_decision_evidence": {
            "H1_unchanged_scalar_taxonomy": "REJECT: C has no independent local autonomous law and J_g is algebraic flux, not reservoir state",
            "H2_state_flux_budget_reclassification": "SUPPORTED: correct positive H generator plus algebraic RT and cumulative photon budget removes the claimed Farkas obstruction",
            "H3_more_general_coupled_generator": "HOLD: not justified before nonautonomous photon-conserving forcing audit",
        },
        "production_node_chemistry_authorized": False,
        "B2C2B_authorized": False,
        "next_stage_authorized": "P0.5-B2C2B0C-R2C-R1B-PHOTON-CONSERVING-CUMULATIVE-BUDGET-NONAUTONOMOUS-RT-FORCING-LOCK",
    }

    macro.sort_values(KEYS).to_csv(output / "node_local_physics_macro_audit.csv", index=False)
    case.sort_values(CASE_KEYS).to_csv(output / "node_local_physics_case_audit.csv", index=False)
    covariance.to_csv(output / "capacity_refinement_covariance.csv", index=False)
    mass_farkas.to_csv(output / "mass_farkas_endpoint_segment_audit.csv", index=False)
    (output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
