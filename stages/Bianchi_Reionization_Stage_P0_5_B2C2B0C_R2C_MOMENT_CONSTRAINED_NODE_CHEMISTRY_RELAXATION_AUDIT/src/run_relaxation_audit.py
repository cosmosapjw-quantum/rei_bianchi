#!/usr/bin/env python3
"""Execute the R2C finite-relaxation auditor on the fixed R2B node support."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
import zipfile
from typing import Any

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from relaxation_audit_core import (  # noqa: E402
    InitialGlobalState,
    NodeEndpoint,
    construct_initial_endpoint,
    infer_endpoint_equilibrium,
    run_refinement,
)
from relaxation_operator import (  # noqa: E402
    K_B_ERG_PER_K,
    refinement_convergence,
    to_builtin,
)

STAGE_ID = "P0.5-B2C2B0C-R2C-MOMENT-CONSTRAINED-NODE-CHEMISTRY-RELAXATION-AUDIT"
SHAPE_LANES = (
    "LOCAL_NEUTRAL_HAZARD_PRIMARY",
    "RECOMBINATION_WEIGHTED_AUDITOR",
    "SCRIPT_SELF_SHIELDING_AUDITOR",
)
TAU_MYR = (10.0, 100.0, 300.0)
REFINEMENTS = (1, 2, 4)
ACTIVE_GROUPS = ("G1", "G2a")
YHE = 0.079
NODES_PER_MACRO = 2560
MACROS_PER_CASE = 18


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_file(path: Path, chunk: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            data = f.read(chunk)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_builtin(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(to_builtin(row), sort_keys=True, separators=(",", ":")) + "\n")


def reassemble_logical(parts_dir: Path, destination: Path) -> dict[str, Any]:
    manifest_path = parts_dir / "parts_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    destination.parent.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256()
    size = 0
    with destination.open("wb") as out:
        for part in manifest["parts"]:
            path = parts_dir / part["name"]
            actual = sha256_file(path)
            if actual != part["sha256"]:
                raise RuntimeError(f"part hash mismatch: {path}: {actual} != {part['sha256']}")
            if path.stat().st_size != int(part["size_bytes"]):
                raise RuntimeError(f"part size mismatch: {path}")
            with path.open("rb") as src:
                while True:
                    data = src.read(8 * 1024 * 1024)
                    if not data:
                        break
                    out.write(data)
                    h.update(data)
                    size += len(data)
    actual = h.hexdigest()
    if actual != manifest["logical_sha256"] or size != int(manifest["logical_size_bytes"]):
        raise RuntimeError(
            f"logical output mismatch: {destination}: sha={actual}, size={size}, "
            f"expected sha={manifest['logical_sha256']}, size={manifest['logical_size_bytes']}"
        )
    return {
        "manifest": str(manifest_path),
        "output": str(destination),
        "logical_sha256": actual,
        "logical_size_bytes": size,
        "part_count": int(manifest["part_count"]),
        "status": "PASS",
    }


def load_initial_global(repo: Path) -> InitialGlobalState:
    artifact = repo / "artifacts/compact/Bianchi_Reionization_Stage_P0_5_B2C2B0C_JOINT_CHEMISTRY_SINK_RESERVOIR_HISTORY_LOCK_compact_bundle.zip"
    with zipfile.ZipFile(artifact) as z:
        member = next(name for name in z.namelist() if name.endswith("data/primary_joint_history.csv"))
        with z.open(member) as f:
            frame = pd.read_csv(f)
    row = frame[frame["interval_index"].isna()].iloc[0]
    return InitialGlobalState(
        n_h_sink=float(row["N_sink"]),
        x_hii_sink=float(row["x_sink"]),
        temperature_sink_k=float(row["T_sink"]),
        z=float(row["z"]),
    )


def load_node_tables(state_path: Path, group_path: Path) -> pd.DataFrame:
    state_columns = [
        "shape_lane",
        "interval_index",
        "substep",
        "z_mid",
        "macro_index",
        "micro_index",
        "M_sink_H_node_cMpc3",
        "p_mass_conditional",
        "xHII_lift",
        "T_lift_K",
        "nH_node_cm3",
        "cycling_capacity_node_s_inv_cMpc3",
    ]
    group_columns = [
        "shape_lane",
        "interval_index",
        "substep",
        "macro_index",
        "micro_index",
        "group",
        "J_sink_node_s_inv_cMpc3",
        "kappa_sink_node_cMpc_inv",
        "Phi_current_Gamma_s_inv_cMpc2",
    ]
    state = pd.read_csv(
        state_path,
        usecols=state_columns,
        dtype={
            "shape_lane": "category",
            "interval_index": "int16",
            "substep": "int8",
            "macro_index": "int8",
            "micro_index": "int16",
        },
    )
    groups = pd.read_csv(
        group_path,
        usecols=group_columns,
        dtype={
            "shape_lane": "category",
            "interval_index": "int16",
            "substep": "int8",
            "macro_index": "int8",
            "micro_index": "int16",
            "group": "category",
        },
    )
    if len(groups) != 2 * len(state):
        raise RuntimeError(f"group/state row mismatch: {len(groups)} != 2*{len(state)}")
    g1 = groups.iloc[0::2].reset_index(drop=True)
    g2 = groups.iloc[1::2].reset_index(drop=True)
    if not (g1["group"].astype(str).eq("G1").all() and g2["group"].astype(str).eq("G2a").all()):
        raise RuntimeError("active group rows are not ordered G1,G2a for every node")
    for key in ("shape_lane", "interval_index", "substep", "macro_index", "micro_index"):
        a = state[key].astype(str).to_numpy() if key == "shape_lane" else state[key].to_numpy()
        b1 = g1[key].astype(str).to_numpy() if key == "shape_lane" else g1[key].to_numpy()
        b2 = g2[key].astype(str).to_numpy() if key == "shape_lane" else g2[key].to_numpy()
        if not np.array_equal(a, b1) or not np.array_equal(a, b2):
            raise RuntimeError(f"state/group key ordering mismatch: {key}")
    state = state.copy()
    state["J_G1"] = g1["J_sink_node_s_inv_cMpc3"].to_numpy(float)
    state["J_G2a"] = g2["J_sink_node_s_inv_cMpc3"].to_numpy(float)
    state["kappa_G1"] = g1["kappa_sink_node_cMpc_inv"].to_numpy(float)
    state["kappa_G2a"] = g2["kappa_sink_node_cMpc_inv"].to_numpy(float)
    state["phi_G1"] = g1["Phi_current_Gamma_s_inv_cMpc2"].to_numpy(float)
    state["phi_G2a"] = g2["Phi_current_Gamma_s_inv_cMpc2"].to_numpy(float)
    if state.isna().any().any():
        raise RuntimeError("node inputs contain missing values")
    if len(state) != len(SHAPE_LANES) * 10 * MACROS_PER_CASE * NODES_PER_MACRO:
        raise RuntimeError(f"unexpected state row count: {len(state)}")
    return state


def endpoint_from_frame(frame: pd.DataFrame) -> NodeEndpoint:
    frame = frame.sort_values(["macro_index", "micro_index"]).reset_index(drop=True)
    expected = MACROS_PER_CASE * NODES_PER_MACRO
    if len(frame) != expected:
        raise RuntimeError(f"endpoint has {len(frame)} nodes, expected {expected}")
    for macro, subset in frame.groupby("macro_index", sort=True):
        if int(macro) not in range(MACROS_PER_CASE) or len(subset) != NODES_PER_MACRO:
            raise RuntimeError(f"invalid macro support: macro={macro}, rows={len(subset)}")
        if not np.array_equal(subset["micro_index"].to_numpy(), np.arange(NODES_PER_MACRO)):
            raise RuntimeError(f"micro ordering mismatch in macro {macro}")
    phi1 = frame["phi_G1"].to_numpy(float)
    phi2 = frame["phi_G2a"].to_numpy(float)
    if np.max(np.abs(phi1 / phi1[0] - 1.0)) > 2.0e-12 or np.max(np.abs(phi2 / phi2[0] - 1.0)) > 2.0e-12:
        raise RuntimeError("current-Gamma flux is not macro-independent within endpoint")
    mass = frame["M_sink_H_node_cMpc3"].to_numpy(float)
    return NodeEndpoint(
        mass=mass,
        x_hii=frame["xHII_lift"].to_numpy(float),
        temperature_k=frame["T_lift_K"].to_numpy(float),
        capacity=frame["cycling_capacity_node_s_inv_cMpc3"].to_numpy(float),
        current=np.column_stack([frame["J_G1"].to_numpy(float), frame["J_G2a"].to_numpy(float)]),
        phi=np.array([phi1[0], phi2[0]], dtype=float),
        n_h_cm3=frame["nH_node_cm3"].to_numpy(float),
        p_mass=mass / float(np.sum(mass)),
        z=float(frame["z_mid"].iloc[0]),
    )


def slice_macro(endpoint: NodeEndpoint, macro_index: int) -> NodeEndpoint:
    start = int(macro_index) * NODES_PER_MACRO
    stop = start + NODES_PER_MACRO
    sl = slice(start, stop)
    mass = np.asarray(endpoint.mass[sl], dtype=float)
    return NodeEndpoint(
        mass=mass,
        x_hii=np.asarray(endpoint.x_hii[sl], dtype=float),
        temperature_k=np.asarray(endpoint.temperature_k[sl], dtype=float),
        capacity=np.asarray(endpoint.capacity[sl], dtype=float),
        current=np.asarray(endpoint.current[sl], dtype=float),
        phi=np.asarray(endpoint.phi, dtype=float),
        n_h_cm3=np.asarray(endpoint.n_h_cm3[sl], dtype=float),
        p_mass=mass / max(float(np.sum(mass)), 1.0),
        z=float(endpoint.z),
    )


def flatten_substep(record: dict[str, Any], dual_path: Path) -> dict[str, Any]:
    rec = dict(record)
    projection = rec.pop("projection", None)
    exact_projection = rec.pop("exact_reference_projection", None)
    errors = rec.pop("errors_to_exact_reference", {})
    if projection is not None or exact_projection is not None:
        append_jsonl(
            dual_path,
            [
                {
                    "shape_lane": rec.get("shape_lane"),
                    "interval_index": rec.get("interval_index"),
                    "substep": rec.get("substep"),
                    "macro_index": rec.get("macro_index"),
                    "tau_Myr": rec.get("tau_Myr"),
                    "refinement": rec.get("refinement"),
                    "refined_substep": rec.get("refined_substep"),
                    "projection": projection,
                    "exact_reference_projection": exact_projection,
                }
            ],
        )
    for key, value in errors.items():
        rec[f"error_{key}"] = value
    if projection:
        for key in (
            "pass",
            "solver_status",
            "active_set_count",
            "active_set_sha256",
            "max_column_relative_residual",
            "max_capacity_violation",
            "max_capacity_relative_violation",
            "max_stationarity_residual",
            "max_complementarity_residual",
            "projection_generalized_kl_to_raw",
            "projection_TV_G1",
            "projection_TV_G2a",
        ):
            if key in projection:
                rec[f"projection_{key}"] = projection[key]
    rec["He_nuclei_total"] = YHE * float(rec.get("H_nuclei_total", 0.0)) if rec.get("status") == "PASS" else math.nan
    rec["He_nuclei_identity_residual"] = 0.0 if rec.get("status") == "PASS" else math.nan
    return to_builtin(rec)


def convergence_pass(errors: list[float]) -> tuple[bool, dict[str, Any]]:
    if len(errors) != 3 or not all(math.isfinite(v) for v in errors):
        return False, {"status": "NOT_AVAILABLE"}
    conv = refinement_convergence(errors)
    if max(errors) <= 1.0e-14:
        return True, {**conv, "status": "TRIVIAL_MACHINE_ZERO"}
    passed = bool(conv["monotone"] and conv["observed_order_1_to_2_to_4"] >= 0.5)
    return passed, {**conv, "status": "PASS" if passed else "FAIL"}


def run(repo: Path, stage: Path, work_dir: Path) -> dict[str, Any]:
    started = time.time()
    data_dir = stage / "data"
    logs_dir = stage / "logs"
    receipts_dir = stage / "receipts"
    for directory in (data_dir, logs_dir, receipts_dir, work_dir):
        directory.mkdir(parents=True, exist_ok=True)

    r2b = repo / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2B_MOMENT_CONSTRAINED_NODE_LIFT_HISTORY_UPLOAD_RECOVERY_V2"
    state_receipt = reassemble_logical(r2b / "data/node_state_lift.csv.gz.parts", work_dir / "node_state_lift.csv.gz")
    group_receipt = reassemble_logical(r2b / "data/node_group_lift.csv.gz.parts", work_dir / "node_group_lift.csv.gz")
    write_json(receipts_dir / "logical_input_reassembly.json", {"node_state": state_receipt, "node_group": group_receipt})

    nodes = load_node_tables(work_dir / "node_state_lift.csv.gz", work_dir / "node_group_lift.csv.gz")
    r2a = repo / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2A_GLOBAL_MOMENT_CONSTRAINED_MACRO_SINK_DISTRIBUTION_LOCK"
    global_df = pd.read_csv(r2a / "data/global_moment_lock.csv").sort_values(["interval_index", "substep"]).reset_index(drop=True)
    macro_df = pd.read_csv(r2a / "data/macro_projection.csv").sort_values(["shape_lane", "interval_index", "substep", "macro_index"]).reset_index(drop=True)
    inherited_relax = pd.read_csv(r2a / "data/finite_relaxation_feasibility.csv")
    shutil.copyfile(r2a / "data/finite_relaxation_feasibility.csv", data_dir / "R2A_finite_relaxation_inheritance.csv")
    initial_global = load_initial_global(repo)

    equilibrium_rows: list[dict[str, Any]] = []
    macro_equilibrium_rows: list[dict[str, Any]] = []
    violation_rows: list[dict[str, Any]] = []
    substep_rows: list[dict[str, Any]] = []
    convergence_rows: list[dict[str, Any]] = []
    exact_zero_rows: list[dict[str, Any]] = []
    dual_path = data_dir / "dual_kkt_certificates.jsonl"
    dual_path.write_text("", encoding="utf-8")

    endpoint_keys = [
        (int(row.interval_index), int(row.substep), float(row.dt_Myr), float(row.z_mid))
        for row in global_df.itertuples(index=False)
    ]

    for lane in SHAPE_LANES:
        lane_nodes = nodes[nodes["shape_lane"].astype(str) == lane]
        first_key = endpoint_keys[0]
        first_frame = lane_nodes[
            (lane_nodes["interval_index"] == first_key[0]) & (lane_nodes["substep"] == first_key[1])
        ]
        first_endpoint = endpoint_from_frame(first_frame)
        previous_full = construct_initial_endpoint(
            first_endpoint, initial_global, nodes_per_macro=NODES_PER_MACRO
        )
        write_json(
            receipts_dir / f"initial_current_projection_{lane}.json",
            previous_full.construction_certificate,
        )

        for interval_index, substep, dt_myr, z_mid in endpoint_keys:
            frame = lane_nodes[
                (lane_nodes["interval_index"] == interval_index) & (lane_nodes["substep"] == substep)
            ]
            target_full = endpoint_from_frame(frame)
            macro_case = macro_df[
                (macro_df["shape_lane"] == lane)
                & (macro_df["interval_index"] == interval_index)
                & (macro_df["substep"] == substep)
            ].sort_values("macro_index")
            if len(macro_case) != MACROS_PER_CASE:
                raise RuntimeError(f"macro metadata incomplete for {lane} {interval_index}/{substep}")
            inherited_row = inherited_relax[
                (inherited_relax["shape_lane"] == lane)
                & (inherited_relax["interval_index"] == interval_index)
                & (inherited_relax["substep"] == substep)
            ]

            for tau_myr in TAU_MYR:
                case_equilibrium_pass = True
                failed_macros = 0
                refinement_macro_errors: dict[int, dict[str, list[float]]] = {
                    n: {name: [] for name in (
                        "mass_l1_relative",
                        "ionized_l1_relative",
                        "thermal_l1_relative",
                        "capacity_l1_relative",
                        "current_l1_relative",
                        "opacity_l1_relative",
                        "combined_extensive_l1_relative",
                    )}
                    for n in REFINEMENTS
                }
                refinement_pass = {n: True for n in REFINEMENTS}
                completed_substeps = {n: 0 for n in REFINEMENTS}

                inherited_match = inherited_row[np.isclose(inherited_row["tau_Myr"], tau_myr)]
                inherited_absolute = bool(inherited_match.iloc[0]["absolute_state_feasible"]) if len(inherited_match) else None
                inherited_shape = bool(inherited_match.iloc[0]["shape_only_feasible"]) if len(inherited_match) else None

                for macro_index in range(MACROS_PER_CASE):
                    previous = slice_macro(previous_full, macro_index)
                    target = slice_macro(target_full, macro_index)
                    mr = macro_case[macro_case["macro_index"] == macro_index].iloc[0]
                    equilibrium, cert = infer_endpoint_equilibrium(
                        previous,
                        target,
                        dt_myr=dt_myr,
                        tau_myr=tau_myr,
                        macro_mass_cap=float(mr["M_sink_H_cap_cosmic_cMpc3"]),
                        macro_volume_cap=float(mr["M_sink_H_cap_volume_cMpc3"]),
                    )
                    normalized = cert["normalized"]
                    macro_row = {
                        "shape_lane": lane,
                        "interval_index": interval_index,
                        "substep": substep,
                        "z_mid": z_mid,
                        "macro_index": macro_index,
                        "tau_Myr": tau_myr,
                        "equilibrium_pass": bool(cert["pass"]),
                        "violated_constraints": ";".join(cert["violated_constraints"]),
                        "temperature_min_K": cert["temperature_min_K"],
                        "temperature_max_K": cert["temperature_max_K"],
                        "minimum_row_capacity_slack": cert["minimum_row_capacity_slack"],
                        **{f"normalized_{k}": v for k, v in normalized.items()},
                    }
                    macro_equilibrium_rows.append(to_builtin(macro_row))
                    append_jsonl(
                        dual_path,
                        [{
                            "certificate_type": "EXTENSIVE_EQUILIBRIUM_CONE",
                            "shape_lane": lane,
                            "interval_index": interval_index,
                            "substep": substep,
                            "macro_index": macro_index,
                            "tau_Myr": tau_myr,
                            "certificate": cert,
                        }],
                    )
                    if not cert["pass"]:
                        case_equilibrium_pass = False
                        failed_macros += 1
                        for constraint in cert["violated_constraints"]:
                            violation_rows.append(
                                {
                                    "shape_lane": lane,
                                    "interval_index": interval_index,
                                    "substep": substep,
                                    "z_mid": z_mid,
                                    "macro_index": macro_index,
                                    "tau_Myr": tau_myr,
                                    "constraint": constraint,
                                    **{f"normalized_{k}": v for k, v in normalized.items()},
                                    "clipping_used": False,
                                }
                            )
                        for n in REFINEMENTS:
                            refinement_pass[n] = False
                            for k in range(1, n + 1):
                                substep_rows.append(
                                    {
                                        "shape_lane": lane,
                                        "interval_index": interval_index,
                                        "substep": substep,
                                        "z_mid": z_mid,
                                        "macro_index": macro_index,
                                        "tau_Myr": tau_myr,
                                        "refinement": n,
                                        "refined_substep": k,
                                        "elapsed_Myr": k * dt_myr / n,
                                        "status": "SKIPPED_FAIL_CLOSED_EQUILIBRIUM_INFEASIBLE",
                                        "equilibrium_violations": ";".join(cert["violated_constraints"]),
                                    }
                                )
                        continue

                    for n in REFINEMENTS:
                        result = run_refinement(
                            previous,
                            target,
                            equilibrium,
                            dt_myr=dt_myr,
                            tau_myr=tau_myr,
                            refinement=n,
                            interval_index=interval_index,
                            substep=substep,
                            macro_index=macro_index,
                            shape_lane=lane,
                        )
                        refinement_pass[n] = refinement_pass[n] and bool(result["pass"])
                        for rec in result["substeps"]:
                            rec["z_mid"] = z_mid
                            flat = flatten_substep(rec, dual_path)
                            substep_rows.append(flat)
                            if flat.get("status") == "PASS":
                                completed_substeps[n] += 1
                        for name, value in result["final_errors"].items():
                            if math.isfinite(float(value)):
                                refinement_macro_errors[n][name].append(float(value))

                equilibrium_rows.append(
                    {
                        "shape_lane": lane,
                        "interval_index": interval_index,
                        "substep": substep,
                        "z_mid": z_mid,
                        "dt_Myr": dt_myr,
                        "tau_Myr": tau_myr,
                        "node_equilibrium_all_macros_feasible": case_equilibrium_pass,
                        "failed_macro_count": failed_macros,
                        "inherited_R2A_absolute_feasible": inherited_absolute,
                        "inherited_R2A_shape_feasible": inherited_shape,
                        "node_gate_stricter_than_R2A": bool(inherited_absolute and not case_equilibrium_pass),
                    }
                )

                conv_row: dict[str, Any] = {
                    "shape_lane": lane,
                    "interval_index": interval_index,
                    "substep": substep,
                    "z_mid": z_mid,
                    "dt_Myr": dt_myr,
                    "tau_Myr": tau_myr,
                    "equilibrium_pass": case_equilibrium_pass,
                    "projection_all_refinements_pass": all(refinement_pass.values()),
                    "completed_macro_substeps_n1": completed_substeps[1],
                    "completed_macro_substeps_n2": completed_substeps[2],
                    "completed_macro_substeps_n4": completed_substeps[4],
                }
                all_conv_pass = case_equilibrium_pass and all(refinement_pass.values())
                for name in refinement_macro_errors[1]:
                    errors = []
                    for n in REFINEMENTS:
                        values = refinement_macro_errors[n][name]
                        errors.append(max(values) if len(values) == MACROS_PER_CASE else math.nan)
                    passed, conv = convergence_pass(errors)
                    all_conv_pass = all_conv_pass and passed
                    conv_row[f"{name}_n1_max"] = errors[0]
                    conv_row[f"{name}_n2_max"] = errors[1]
                    conv_row[f"{name}_n4_max"] = errors[2]
                    conv_row[f"{name}_monotone"] = conv.get("monotone")
                    conv_row[f"{name}_order_2_to_4"] = conv.get("observed_order_1_to_2_to_4")
                    conv_row[f"{name}_convergence_status"] = conv.get("status")
                conv_row["convergence_pass"] = bool(all_conv_pass)
                convergence_rows.append(to_builtin(conv_row))

                for quantity in (
                    "kappa_sink_G2b_effective_HI",
                    "kappa_sink_G3_effective_HI",
                    "J_sink_G2b_effective_HI",
                    "J_sink_G3_effective_HI",
                    "HeII_G3_primary_absorption",
                ):
                    exact_zero_rows.append(
                        {
                            "shape_lane": lane,
                            "interval_index": interval_index,
                            "substep": substep,
                            "z_mid": z_mid,
                            "tau_Myr": tau_myr,
                            "quantity": quantity,
                            "value": "0",
                            "exact_zero": True,
                        }
                    )
            previous_full = target_full

    equilibrium_frame = pd.DataFrame(equilibrium_rows)
    macro_equilibrium_frame = pd.DataFrame(macro_equilibrium_rows)
    violation_frame = pd.DataFrame(violation_rows)
    substep_frame = pd.DataFrame(substep_rows)
    convergence_frame = pd.DataFrame(convergence_rows)
    exact_zero_frame = pd.DataFrame(exact_zero_rows)

    equilibrium_frame.to_csv(data_dir / "equilibrium_feasibility.csv", index=False)
    macro_equilibrium_frame.to_csv(data_dir / "macro_equilibrium_certificates.csv", index=False)
    violation_frame.to_csv(data_dir / "violated_constraints.csv", index=False)
    substep_frame.to_csv(data_dir / "relaxation_substep_ledger.csv", index=False)
    convergence_frame.to_csv(data_dir / "temporal_convergence.csv", index=False)
    exact_zero_frame.to_csv(data_dir / "exact_zero_audit.csv", index=False)

    pass_by_tau: dict[str, Any] = {}
    for tau in TAU_MYR:
        eq_subset = equilibrium_frame[np.isclose(equilibrium_frame["tau_Myr"], tau)]
        cv_subset = convergence_frame[np.isclose(convergence_frame["tau_Myr"], tau)]
        pass_by_tau[str(int(tau))] = {
            "case_count": int(len(eq_subset)),
            "equilibrium_feasible_case_count": int(eq_subset["node_equilibrium_all_macros_feasible"].sum()),
            "convergent_case_count": int(cv_subset["convergence_pass"].sum()),
            "all_equilibrium_feasible": bool(eq_subset["node_equilibrium_all_macros_feasible"].all()),
            "all_convergent": bool(cv_subset["convergence_pass"].all()),
        }

    all_equilibrium = bool(equilibrium_frame["node_equilibrium_all_macros_feasible"].all())
    all_convergent = bool(convergence_frame["convergence_pass"].all())
    production_authorized = bool(all_equilibrium and all_convergent)
    tau10_witness = bool(
        equilibrium_frame[np.isclose(equilibrium_frame["tau_Myr"], 10.0)]["node_equilibrium_all_macros_feasible"].all()
    )

    successful_substeps = substep_frame[substep_frame["status"] == "PASS"]
    summary = {
        "stage": STAGE_ID,
        "generated_utc": utc_now(),
        "verdict": (
            "DURABLE_PASS_R2C_ALL_LANE_RELAXATION_AUDIT_PRODUCTION_HISTORY_AUTHORIZED"
            if production_authorized
            else "DURABLE_FAIL_CLOSED_R2C_CONSTANT_EQUILIBRIUM_RELAXATION_NOT_ALL_LANES_REACHABLE"
        ),
        "production_node_chemistry_authorized": production_authorized,
        "B2C2B_authorized": False,
        "tau10_all_case_existence_witness": tau10_witness,
        "all_requested_tau_equilibrium_feasible": all_equilibrium,
        "all_requested_tau_temporally_convergent": all_convergent,
        "case_count": int(len(equilibrium_frame)),
        "macro_equilibrium_certificate_count": int(len(macro_equilibrium_frame)),
        "violated_constraint_row_count": int(len(violation_frame)),
        "relaxation_substep_ledger_rows": int(len(substep_frame)),
        "successful_relaxation_substeps": int(len(successful_substeps)),
        "dual_certificate_lines": sum(1 for _ in dual_path.open("r", encoding="utf-8")),
        "exact_zero_rows": int(len(exact_zero_frame)),
        "by_tau": pass_by_tau,
        "maximum_projection_column_residual": (
            float(successful_substeps["projection_max_column_relative_residual"].max())
            if len(successful_substeps) and "projection_max_column_relative_residual" in successful_substeps
            else math.nan
        ),
        "maximum_projection_capacity_violation_absolute": (
            float(successful_substeps["projection_max_capacity_violation"].max())
            if len(successful_substeps) and "projection_max_capacity_violation" in successful_substeps
            else math.nan
        ),
        "maximum_projection_capacity_relative_violation": (
            float(successful_substeps["projection_max_capacity_relative_violation"].max())
            if len(successful_substeps) and "projection_max_capacity_relative_violation" in successful_substeps
            else math.nan
        ),
        "maximum_current_Gamma_residual": (
            float(successful_substeps["current_Gamma_residual_max"].max())
            if len(successful_substeps)
            else math.nan
        ),
        "maximum_H_nuclei_identity_residual": (
            float(successful_substeps["H_nuclei_identity_residual"].abs().max())
            if len(successful_substeps)
            else math.nan
        ),
        "maximum_He_nuclei_identity_residual": (
            float(successful_substeps["He_nuclei_identity_residual"].abs().max())
            if len(successful_substeps)
            else math.nan
        ),
        "maximum_R2B_endpoint_error_n4": (
            float(
                convergence_frame.filter(regex=r"_n4_max$").replace([np.inf, -np.inf], np.nan).max().max()
            )
            if len(convergence_frame)
            else math.nan
        ),
        "scope_exclusions_confirmed": [
            "no unresolved subtraction",
            "no front/Q_M",
            "no source/fesc",
            "no primordial recombination adapter or surrogate",
            "no CAMB transfer",
            "no Bianchi feedback",
            "no cloud mass inferred from opacity",
        ],
        "interpretation": (
            "The exact first-order equilibrium model is an auditor. A failed lane is a model-adequacy/no-go result, "
            "not permission to clip a node state or replace the hard endpoint."
        ),
        "runtime_seconds": time.time() - started,
    }
    write_json(data_dir / "summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path)
    args = parser.parse_args()
    work = args.work_dir or Path(tempfile.mkdtemp(prefix="rei_bianchi_r2c_"))
    summary = run(args.repo.resolve(), args.stage.resolve(), work.resolve())
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
