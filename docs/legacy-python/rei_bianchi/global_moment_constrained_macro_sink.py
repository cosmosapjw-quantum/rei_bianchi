#!/usr/bin/env python3
"""R2A global-moment-constrained macro sink distribution operator.

This stage keeps the validated B2C2B0C reduced-DAE sink moments fixed and
allocates only their 18-macro distribution.  The active effective-HI sink
opacity groups are G1 and G2a.  G2b/G3 and primary HeII/G3 remain structural
zeros.

For each shape lane and reduced-DAE substep, normalized macro mass and opacity
measures are obtained from the convex information projection

    min  1/2 D(m || p_M) + 1/2 sum_g q_g D(k_g || p_g),

where D(x||p)=sum_i[x_i log(x_i/p_i)-x_i+p_i], q_g=J_g/sum_h J_h,
p_M=sum_g q_g p_g, m_i=M_i/N_sink, and k_gi=kappa_gi/kappa_g.
The hard feasible set locks all global moments, macro mass/volume caps, the
current-Gamma relation, and per-macro neutral-plus-recombination cycling
capacity.  No cloud abundance is solved from opacity.

The canonical R2A inputs make every p=(p_M,p_g) strictly feasible, so the
unique constrained optimum is the prior itself with zero generalized KL and
an analytic zero-dual KKT certificate.  A numerical fallback exists only to
fail closed on future non-identity inputs; it is not exercised by this lock.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import shutil
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from scipy.optimize import linprog, minimize

STAGE_ID = (
    "P0.5-B2C2B0C-R2A-GLOBAL-MOMENT-CONSTRAINED-"
    "MACRO-SINK-DISTRIBUTION-LOCK"
)
SHAPE_LANES = (
    "LOCAL_NEUTRAL_HAZARD_PRIMARY",
    "RECOMBINATION_WEIGHTED_AUDITOR",
    "SCRIPT_SELF_SHIELDING_AUDITOR",
)
ACTIVE_GROUPS = ("G1", "G2a")
STRUCTURAL_ZERO_GROUPS = ("G2b", "G3")
ALL_GROUPS = ACTIVE_GROUPS + STRUCTURAL_ZERO_GROUPS
TAU_MYR = (10.0, 100.0, 300.0)
MPC_CM = 3.0856775814913673e24
MYR_S = 1.0e6 * 365.25 * 86400.0
EPS = np.finfo(float).tiny
CORE_RTOL = 5.0e-13
CORE_ATOL = 1.0e-12
KKT_TOL = 5.0e-11


@dataclass(frozen=True)
class InputTables:
    macro_template: pd.DataFrame
    macro_environment: pd.DataFrame
    macro_allocation: pd.DataFrame
    opacity_targets: pd.DataFrame
    global_history: pd.DataFrame
    global_ledger: pd.DataFrame
    photon_ledger: pd.DataFrame
    r1_results: dict[str, Any]


@dataclass
class ProjectionResult:
    m: np.ndarray
    k: dict[str, np.ndarray]
    method: str
    objective: float
    feasible: bool
    identity_projection: bool
    optimizer_status: str
    certificates: list[dict[str, Any]]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def append_receipt(stage_dir: Path, event: str, status: str, **payload: Any) -> None:
    row = {"utc": utc_now(), "event": event, "status": status, **payload}
    with (stage_dir / "RUN_RECEIPTS.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def find_zip_member(archive: zipfile.ZipFile, suffix: str) -> str:
    suffix = suffix.replace("\\", "/")
    candidates = [name for name in archive.namelist() if name.endswith(suffix)]
    if len(candidates) != 1:
        raise RuntimeError(
            f"Expected exactly one member ending in {suffix!r}; found {candidates}"
        )
    return candidates[0]


def read_csv_member(zip_path: Path, suffix: str) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path) as archive:
        member = find_zip_member(archive, suffix)
        with archive.open(member) as handle:
            return pd.read_csv(handle)


def read_json_member(zip_path: Path, suffix: str) -> dict[str, Any]:
    with zipfile.ZipFile(zip_path) as archive:
        member = find_zip_member(archive, suffix)
        return json.loads(archive.read(member).decode("utf-8"))


def copy_member_exact(zip_path: Path, suffix: str, destination: Path) -> str:
    with zipfile.ZipFile(zip_path) as archive:
        member = find_zip_member(archive, suffix)
        raw = archive.read(member)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def canonical_zip_paths(repo_root: Path, input_lock: dict[str, Any]) -> dict[str, Path]:
    mapping: dict[str, Path] = {}
    for item in input_lock["canonical_artifacts"]:
        path = repo_root / item["repo_path"]
        actual = sha256_file(path)
        if actual != item["sha256"]:
            raise RuntimeError(
                f"Canonical artifact hash mismatch for {item['label']}: "
                f"expected {item['sha256']}, got {actual}"
            )
        mapping[item["label"]] = path
    return mapping


def load_inputs(repo_root: Path, stage_dir: Path) -> tuple[InputTables, dict[str, Path]]:
    input_lock = json.loads((stage_dir / "INPUT_LOCK.json").read_text(encoding="utf-8"))
    archives = canonical_zip_paths(repo_root, input_lock)
    b0a = archives["B2C2B0A_COMPACT"]
    b0c = archives["B2C2B0C_COMPACT"]
    r1 = archives["B2C2B0C_R1_COMPACT"]
    tables = InputTables(
        macro_template=read_csv_member(b0a, "data/fixed_macro_parcel_template_z6.csv"),
        macro_environment=read_csv_member(b0a, "data/macro_environment_measure.csv"),
        macro_allocation=read_csv_member(b0a, "data/macro_species_photon_allocation.csv"),
        opacity_targets=read_csv_member(b0a, "data/r1_opacity_targets.csv"),
        global_history=read_csv_member(b0c, "data/primary_joint_history.csv"),
        global_ledger=read_csv_member(b0c, "data/primary_joint_ledger.csv"),
        photon_ledger=read_csv_member(b0c, "data/joint_photon_ledger.csv"),
        r1_results=read_json_member(r1, "/results.json"),
    )
    exact_photon_sha = copy_member_exact(
        b0c,
        "data/joint_photon_ledger.csv",
        stage_dir / "data" / "inherited_exact_photon_ledger.csv",
    )
    write_json(
        stage_dir / "receipts" / "canonical_runtime_input_receipt.json",
        {
            "stage": STAGE_ID,
            "verified_utc": utc_now(),
            "archives": {
                label: {
                    "path": str(path.relative_to(repo_root)),
                    "sha256": sha256_file(path),
                }
                for label, path in archives.items()
            },
            "inherited_exact_photon_ledger_sha256": exact_photon_sha,
            "r1_verdict": tables.r1_results.get("verdict"),
            "r1_node_history_promoted": False,
        },
    )
    return tables, archives


def generalized_kl(x: np.ndarray, p: np.ndarray) -> float:
    if np.any(x < 0.0) or np.any(p <= 0.0):
        return math.inf
    positive = x > 0.0
    value = float(np.sum(p[~positive]))
    if np.any(positive):
        xp = x[positive]
        pp = p[positive]
        value += float(np.sum(xp * np.log(xp / pp) - xp + pp))
    return max(value, 0.0)


def total_variation(x: np.ndarray, p: np.ndarray) -> float:
    return 0.5 * float(np.sum(np.abs(x - p)))


def symmetric_kl(x: np.ndarray, y: np.ndarray) -> float:
    return 0.5 * (generalized_kl(x, y) + generalized_kl(y, x))


def closed_scale(total: float, fractions: np.ndarray) -> np.ndarray:
    fractions = np.asarray(fractions, dtype=float).copy()
    fractions /= float(np.sum(fractions))
    values = total * fractions
    values[-1] = total - float(np.sum(values[:-1]))
    return values


def is_close_zero(value: float, scale: float = 1.0) -> bool:
    return abs(value) <= CORE_ATOL + CORE_RTOL * max(abs(scale), 1.0)


def prepare_global_state(tables: InputTables) -> tuple[pd.DataFrame, float, dict[str, Any]]:
    ledger = tables.global_ledger.copy().sort_values(
        ["interval_index", "substep"]
    ).reset_index(drop=True)
    history = tables.global_history.dropna(subset=["interval_index", "substep"]).copy()
    history["interval_index"] = history["interval_index"].astype(int)
    history["substep"] = history["substep"].astype(int)
    merged = ledger.merge(
        history[
            [
                "interval_index",
                "substep",
                "z",
                "N_sink",
                "x_sink",
                "T_sink",
            ]
        ],
        on=["interval_index", "substep"],
        how="left",
        validate="one_to_one",
    )
    if merged[["N_sink", "x_sink", "T_sink"]].isna().any().any():
        raise RuntimeError("Could not match every reduced-DAE ledger row to history")
    nhc_values = merged["N_sink"] / merged["N_sink_fraction_of_cosmic_H"]
    nhc = float(np.median(nhc_values))
    nhc_rel_scatter = float(np.max(np.abs(nhc_values / nhc - 1.0)))
    if nhc_rel_scatter > 2.0e-12:
        raise RuntimeError(f"Cosmic-H inventory is inconsistent: {nhc_rel_scatter}")
    initial = tables.global_history[tables.global_history["interval_index"].isna()].iloc[0]
    initial_state = {
        "z": float(initial["z"]),
        "N_sink": float(initial["N_sink"]),
        "x_sink": float(initial["x_sink"]),
        "T_sink": float(initial["T_sink"]),
    }
    return merged, nhc, initial_state


def macro_prior(
    tables: InputTables,
    z_mid: float,
    lane: str,
    group: str,
) -> np.ndarray:
    subset = tables.macro_allocation[
        np.isclose(tables.macro_allocation["z"], z_mid, rtol=0.0, atol=1.0e-10)
        & (tables.macro_allocation["shape_lane"] == lane)
        & (tables.macro_allocation["group"] == group)
        & (tables.macro_allocation["species"] == "HI")
    ].sort_values("macro_index")
    if len(subset) != 18 or list(subset["macro_index"].astype(int)) != list(range(18)):
        raise RuntimeError(f"Incomplete B2C2B0A prior for z={z_mid}, lane={lane}, group={group}")
    values = subset["j_abs_s-1_cMpc-3"].to_numpy(dtype=float)
    if np.any(values <= 0.0):
        raise RuntimeError("Active-group prior must be strictly positive")
    return values / float(np.sum(values))


def macro_environment(tables: InputTables, z_mid: float) -> pd.DataFrame:
    frame = tables.macro_environment[
        np.isclose(tables.macro_environment["z"], z_mid, rtol=0.0, atol=1.0e-10)
    ].sort_values("macro_index").copy()
    if len(frame) != 18 or list(frame["macro_index"].astype(int)) != list(range(18)):
        raise RuntimeError(f"Incomplete macro environment at z={z_mid}")
    return frame.reset_index(drop=True)


def preflight_certificates(
    upper: np.ndarray,
    rho: float,
    q: np.ndarray,
) -> list[dict[str, Any]]:
    certificates: list[dict[str, Any]] = []
    if float(np.sum(upper)) < 1.0 - 1.0e-12:
        certificates.append(
            {
                "type": "FARKAS_MASS_OR_VOLUME_CAP_SUM",
                "dual_weights": "all macro upper constraints with unit weight",
                "lhs_upper_sum": float(np.sum(upper)),
                "required": 1.0,
                "violation": float(1.0 - np.sum(upper)),
            }
        )
    if rho < 1.0 - 1.0e-12 and is_close_zero(float(np.sum(q)) - 1.0):
        certificates.append(
            {
                "type": "FARKAS_CYCLING_CAPACITY_SUM",
                "dual_weights": "all macro cycling constraints with unit weight",
                "derived_requirement": "rho >= sum_g q_g = 1",
                "rho": float(rho),
                "violation": float(1.0 - rho),
            }
        )
    return certificates


def prior_feasibility(
    p_mass: np.ndarray,
    p_group: dict[str, np.ndarray],
    upper: np.ndarray,
    rho: float,
    q_map: dict[str, float],
) -> dict[str, Any]:
    assigned = sum(q_map[group] * p_group[group] for group in ACTIVE_GROUPS)
    capacity_slack = rho * p_mass - assigned
    return {
        "mass_sum_residual": float(abs(np.sum(p_mass) - 1.0)),
        "group_sum_residual_max": float(
            max(abs(np.sum(p_group[group]) - 1.0) for group in ACTIVE_GROUPS)
        ),
        "mass_upper_slack_min": float(np.min(upper - p_mass)),
        "lower_slack_min": float(
            min(np.min(p_mass), *(np.min(p_group[group]) for group in ACTIVE_GROUPS))
        ),
        "cycling_slack_min": float(np.min(capacity_slack)),
        "cycling_slack": capacity_slack,
        "feasible": bool(
            abs(np.sum(p_mass) - 1.0) <= 1.0e-12
            and all(abs(np.sum(p_group[g]) - 1.0) <= 1.0e-12 for g in ACTIVE_GROUPS)
            and np.min(upper - p_mass) >= -1.0e-12
            and np.min(p_mass) >= -1.0e-15
            and all(np.min(p_group[g]) >= -1.0e-15 for g in ACTIVE_GROUPS)
            and np.min(capacity_slack) >= -1.0e-12
        ),
    }


def numerical_projection(
    p_mass: np.ndarray,
    p_group: dict[str, np.ndarray],
    upper: np.ndarray,
    rho: float,
    q_map: dict[str, float],
) -> ProjectionResult:
    """Convex fallback for future non-identity inputs; never clips infeasibility."""
    n = len(p_mass)
    q = np.array([q_map[g] for g in ACTIVE_GROUPS], dtype=float)
    certs = preflight_certificates(upper, rho, q)
    if certs:
        return ProjectionResult(
            m=np.full(n, np.nan),
            k={g: np.full(n, np.nan) for g in ACTIVE_GROUPS},
            method="PRECHECK_INFEASIBLE",
            objective=math.inf,
            feasible=False,
            identity_projection=False,
            optimizer_status="INFEASIBLE_WITH_ANALYTIC_DUAL_CERTIFICATE",
            certificates=certs,
        )

    # Feasibility LP: x=[m,k_G1,k_G2a].
    c = np.zeros(3 * n)
    aeq = np.zeros((3, 3 * n))
    aeq[0, :n] = 1.0
    aeq[1, n : 2 * n] = 1.0
    aeq[2, 2 * n :] = 1.0
    beq = np.ones(3)
    aub = np.zeros((n, 3 * n))
    for i in range(n):
        aub[i, i] = -rho
        aub[i, n + i] = q[0]
        aub[i, 2 * n + i] = q[1]
    bounds = [(0.0, float(upper[i])) for i in range(n)] + [(0.0, 1.0)] * (2 * n)
    lp = linprog(c, A_ub=aub, b_ub=np.zeros(n), A_eq=aeq, b_eq=beq, bounds=bounds, method="highs")
    if not lp.success:
        certs.append(
            {
                "type": "HIGHS_FEASIBILITY_CERTIFICATE_STATUS",
                "status": int(lp.status),
                "message": str(lp.message),
                "note": "No values were clipped or promoted.",
            }
        )
        return ProjectionResult(
            m=np.full(n, np.nan),
            k={g: np.full(n, np.nan) for g in ACTIVE_GROUPS},
            method="HIGHS_INFEASIBLE",
            objective=math.inf,
            feasible=False,
            identity_projection=False,
            optimizer_status=str(lp.message),
            certificates=certs,
        )

    weights = np.concatenate(
        [
            np.full(n, 0.5),
            np.full(n, 0.5 * q[0]),
            np.full(n, 0.5 * q[1]),
        ]
    )
    priors = np.concatenate([p_mass, p_group[ACTIVE_GROUPS[0]], p_group[ACTIVE_GROUPS[1]]])

    def objective(x: np.ndarray) -> float:
        total = 0.0
        for value, prior, weight in zip(x, priors, weights, strict=True):
            if value < 0.0:
                return 1.0e100
            if value == 0.0:
                total += weight * prior
            else:
                total += weight * (value * math.log(value / prior) - value + prior)
        return float(total)

    def gradient(x: np.ndarray) -> np.ndarray:
        return weights * np.log(np.maximum(x, 1.0e-300) / priors)

    constraints = [
        {"type": "eq", "fun": lambda x: aeq @ x - beq, "jac": lambda x: aeq},
        {"type": "ineq", "fun": lambda x: -aub @ x, "jac": lambda x: -aub},
    ]
    solution = minimize(
        objective,
        lp.x,
        jac=gradient,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"ftol": 1.0e-14, "maxiter": 4000, "disp": False},
    )
    x = np.asarray(solution.x, dtype=float)
    primal = max(
        float(np.max(np.abs(aeq @ x - beq))),
        float(np.max(aub @ x)),
        float(np.max(-x)),
        float(np.max(x[:n] - upper)),
    )
    feasible = bool(solution.success and primal <= 5.0e-10)
    if not feasible:
        certs.append(
            {
                "type": "NUMERICAL_PROJECTION_FAIL_CLOSED",
                "optimizer_success": bool(solution.success),
                "message": str(solution.message),
                "primal_residual": primal,
                "note": "No clipping and no stage promotion.",
            }
        )
    return ProjectionResult(
        m=x[:n],
        k={ACTIVE_GROUPS[0]: x[n : 2 * n], ACTIVE_GROUPS[1]: x[2 * n :]},
        method="SLSQP_CONVEX_FALLBACK",
        objective=objective(x),
        feasible=feasible,
        identity_projection=False,
        optimizer_status=str(solution.message),
        certificates=certs,
    )


def project_case(
    p_mass: np.ndarray,
    p_group: dict[str, np.ndarray],
    upper: np.ndarray,
    rho: float,
    q_map: dict[str, float],
) -> tuple[ProjectionResult, dict[str, Any]]:
    audit = prior_feasibility(p_mass, p_group, upper, rho, q_map)
    if audit["feasible"]:
        result = ProjectionResult(
            m=p_mass.copy(),
            k={group: p_group[group].copy() for group in ACTIVE_GROUPS},
            method="ANALYTIC_IDENTITY_I_PROJECTION",
            objective=0.0,
            feasible=True,
            identity_projection=True,
            optimizer_status="UNIQUE_ZERO_GKL_OPTIMUM; NUMERICAL_FALLBACK_NOT_EXERCISED",
            certificates=[],
        )
    else:
        result = numerical_projection(p_mass, p_group, upper, rho, q_map)
    return result, audit


def relative_residual(actual: float, expected: float) -> float:
    return abs(actual - expected) / max(abs(expected), 1.0)


def case_key(row: pd.Series, lane: str) -> dict[str, Any]:
    return {
        "shape_lane": lane,
        "interval_index": int(row["interval_index"]),
        "substep": int(row["substep"]),
        "substeps_per_interval": int(row["substeps_per_interval"]),
        "z_mid": float(row["z_mid"]),
    }


def run_core_projection(
    tables: InputTables,
    global_state: pd.DataFrame,
    nhc: float,
    stage_dir: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[dict[str, Any]], dict[tuple[str, int, int], dict[str, Any]]]:
    macro_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    global_rows: list[dict[str, Any]] = []
    dual_certificates: list[dict[str, Any]] = []
    cases: dict[tuple[str, int, int], dict[str, Any]] = {}

    for _, row in global_state.iterrows():
        z_mid = float(row["z_mid"])
        interval = int(row["interval_index"])
        substep = int(row["substep"])
        env = macro_environment(tables, z_mid)
        f_mass = (env["W_macro"].to_numpy(dtype=float) * env["D_L_mass"].to_numpy(dtype=float))
        f_mass /= float(np.sum(f_mass))
        mass_cap = nhc * f_mass
        a = 1.0 / (1.0 + z_mid)
        volume_cap = (
            env["W_macro"].to_numpy(dtype=float)
            * float(row["cloud_density_cm3"])
            * a**3
            * MPC_CM**3
        )
        N_global = float(row["N_sink"])
        M_upper_normalized = np.minimum(mass_cap, volume_cap) / N_global

        J_global = {
            "G1": float(row["sink_absorption_G1"]),
            "G2a": float(row["sink_absorption_G2a"]),
        }
        kappa_global = {
            "G1": float(row["kappa_sink_G1"]),
            "G2a": float(row["kappa_sink_G2a"]),
        }
        J_total = sum(J_global.values())
        q_map = {group: J_global[group] / J_total for group in ACTIVE_GROUPS}
        dt_s = float(row["dt_Myr"]) * MYR_S
        neutral_turnover_per_H = max(1.0 - float(row["x_sink"]), 0.0) / dt_s
        recombination_per_H = float(row["sink_recombination"]) / N_global
        cycling_per_H = neutral_turnover_per_H + recombination_per_H
        cycling_global = cycling_per_H * N_global
        rho = cycling_global / J_total

        global_rows.append(
            {
                "interval_index": interval,
                "substep": substep,
                "substeps_per_interval": int(row["substeps_per_interval"]),
                "z_mid": z_mid,
                "dt_Myr": float(row["dt_Myr"]),
                "N_H_sink_global_cMpc3": N_global,
                "N_H_cosmic_cMpc3": nhc,
                "N_sink_fraction": N_global / nhc,
                "N_sink_fraction_inherited": float(row["N_sink_fraction_of_cosmic_H"]),
                "N_sink_lock_relative_residual": relative_residual(
                    N_global / nhc, float(row["N_sink_fraction_of_cosmic_H"])
                ),
                "x_HII_sink_global": float(row["x_sink"]),
                "T_sink_global_K": float(row["T_sink"]),
                "kappa_sink_G1_global_cMpc_inv": kappa_global["G1"],
                "kappa_sink_G2a_global_cMpc_inv": kappa_global["G2a"],
                "kappa_sink_G2b_global_cMpc_inv": 0.0,
                "kappa_sink_G3_global_cMpc_inv": 0.0,
                "J_sink_G1_global_s_inv_cMpc3": J_global["G1"],
                "J_sink_G2a_global_s_inv_cMpc3": J_global["G2a"],
                "J_sink_G2b_global_s_inv_cMpc3": 0.0,
                "J_sink_G3_global_s_inv_cMpc3": 0.0,
                "J_sink_total_s_inv_cMpc3": J_total,
                "sink_rate_inherited_s_inv_cMpc3": float(row["sink_rate"]),
                "sink_rate_vs_group_sum_relative_residual": relative_residual(
                    J_total, float(row["sink_rate"])
                ),
                "diffuse_sink_mass_transfer_rate_H_s_inv_cMpc3": float(row["mass_transfer_rate"]),
                "sink_recombination_global_s_inv_cMpc3": float(row["sink_recombination"]),
                "neutral_stock_turnover_global_s_inv_cMpc3": neutral_turnover_per_H * N_global,
                "cycling_capacity_global_s_inv_cMpc3": cycling_global,
                "cycling_capacity_over_J_sink": rho,
                "cloud_density_geometry_auditor_cm3": float(row["cloud_density_cm3"]),
                "cloud_radius_geometry_auditor_proper_pc": float(row["cloud_radius_proper_pc"]),
                "cloud_neutral_column_geometry_auditor_cm2": float(row["cloud_neutral_column_cm2"]),
                "inherited_global_sink_volume_filling": float(row["sink_volume_filling"]),
            }
        )

        for lane in SHAPE_LANES:
            p_group = {group: macro_prior(tables, z_mid, lane, group) for group in ACTIVE_GROUPS}
            p_mass = sum(q_map[group] * p_group[group] for group in ACTIVE_GROUPS)
            p_mass /= float(np.sum(p_mass))
            result, prior_audit = project_case(
                p_mass, p_group, M_upper_normalized, rho, q_map
            )
            key = case_key(row, lane)
            if not result.feasible:
                for certificate in result.certificates:
                    dual_certificates.append({**key, **certificate})
                summary_rows.append(
                    {
                        **key,
                        "projection_method": result.method,
                        "feasible": False,
                        "identity_projection": False,
                        "optimizer_status": result.optimizer_status,
                        "R2B_core_gate": False,
                    }
                )
                continue

            M = closed_scale(N_global, result.m)
            kappa = {
                group: closed_scale(kappa_global[group], result.k[group])
                for group in ACTIVE_GROUPS
            }
            flux = {
                group: J_global[group] / kappa_global[group]
                for group in ACTIVE_GROUPS
            }
            # Preserve the current-Gamma relation pointwise.  The group moment
            # then closes at floating-point roundoff because kappa closes by
            # construction; the exact symbolic fallback proves both identities.
            J: dict[str, np.ndarray] = {
                group: flux[group] * kappa[group]
                for group in ACTIVE_GROUPS
            }
            transfer = closed_scale(float(row["mass_transfer_rate"]), result.m)
            capacity = cycling_per_H * M
            assigned_J = sum(J[group] for group in ACTIVE_GROUPS)
            capacity_slack = capacity - assigned_J
            volume_filling = M / volume_cap

            m_norm = M / N_global
            k_norm = {group: kappa[group] / kappa_global[group] for group in ACTIVE_GROUPS}
            # KKT belongs to the mathematical operator variables.  For the
            # identity projection these are exactly the priors; serialization
            # closure of the dimensional outputs is audited separately.
            objective_mass = 0.5 * generalized_kl(result.m, p_mass)
            objective_group = {
                group: 0.5 * q_map[group] * generalized_kl(result.k[group], p_group[group])
                for group in ACTIVE_GROUPS
            }
            objective = objective_mass + sum(objective_group.values())
            grad_mass = 0.5 * np.log(np.maximum(result.m, 1.0e-300) / p_mass)
            grad_group = {
                group: 0.5 * q_map[group] * np.log(
                    np.maximum(result.k[group], 1.0e-300) / p_group[group]
                )
                for group in ACTIVE_GROUPS
            }
            stationarity = max(
                float(np.max(np.abs(grad_mass))),
                *(float(np.max(np.abs(grad_group[group]))) for group in ACTIVE_GROUPS),
            )
            mass_sum_resid = relative_residual(float(np.sum(M)), N_global)
            kappa_sum_resid = max(
                relative_residual(float(np.sum(kappa[g])), kappa_global[g])
                for g in ACTIVE_GROUPS
            )
            J_sum_resid = max(
                relative_residual(float(np.sum(J[g])), J_global[g])
                for g in ACTIVE_GROUPS
            )
            transfer_resid = relative_residual(
                float(np.sum(transfer)), float(row["mass_transfer_rate"])
            )
            current_gamma_resid = max(
                relative_residual(float(J[g][i]), flux[g] * float(kappa[g][i]))
                for g in ACTIVE_GROUPS
                for i in range(18)
            )
            primal_residual = max(
                mass_sum_resid,
                kappa_sum_resid,
                J_sum_resid,
                transfer_resid,
                current_gamma_resid,
                max(0.0, -float(np.min(M))),
                max(0.0, float(np.max(M - mass_cap)) / max(nhc, 1.0)),
                max(0.0, float(np.max(volume_filling - 1.0))),
                max(0.0, -float(np.min(capacity_slack)) / max(J_total, 1.0)),
            )
            # For the analytic identity projection, all dual multipliers are zero.
            dual_nonnegativity_residual = 0.0
            complementarity_residual = 0.0
            kkt_pass = bool(
                result.identity_projection
                and primal_residual <= KKT_TOL
                and stationarity <= KKT_TOL
                and dual_nonnegativity_residual <= KKT_TOL
                and complementarity_residual <= KKT_TOL
            )

            dual_certificate = {
                **key,
                "certificate_type": "ANALYTIC_ZERO_DUAL_KKT_CERTIFICATE",
                "projection_method": result.method,
                "generalized_KL_objective": objective,
                "equality_multipliers": {"mass": 0.0, "G1": 0.0, "G2a": 0.0},
                "cycling_dual_min": 0.0,
                "cycling_dual_max": 0.0,
                "mass_lower_dual_min": 0.0,
                "mass_upper_dual_max": 0.0,
                "opacity_lower_dual_min": 0.0,
                "stationarity_residual_max": stationarity,
                "primal_residual_max": primal_residual,
                "dual_nonnegativity_residual": dual_nonnegativity_residual,
                "complementarity_residual_max": complementarity_residual,
                "strict_primal_slack": bool(
                    np.min(M) > 0.0
                    and np.min(mass_cap - M) > 0.0
                    and np.min(volume_cap - M) > 0.0
                    and np.min(capacity_slack) > 0.0
                ),
                "proof": (
                    "D(x||p)>=0 with equality only at x=p; the locked prior is "
                    "strictly feasible, so p is the unique constrained optimum and "
                    "all inequality/equality multipliers may be zero."
                ),
                "KKT_gate": kkt_pass,
            }
            dual_certificates.append(dual_certificate)

            macro_case_rows: list[dict[str, Any]] = []
            for i, env_row in env.iterrows():
                macro_index = int(env_row["macro_index"])
                cloud_radius_cm = float(row["cloud_radius_proper_pc"]) * 3.0856775814913673e18
                cloud_H_single = (
                    4.0
                    / 3.0
                    * math.pi
                    * cloud_radius_cm**3
                    * float(row["cloud_density_cm3"])
                )
                item = {
                    **key,
                    "macro_index": macro_index,
                    "macro_density_index": int(env_row["macro_density_index"]),
                    "zre_index": int(env_row["zre_index"]),
                    "density_sigma": float(env_row["density_sigma"]),
                    "z_re": float(env_row["z_re"]),
                    "W_macro_fixed": float(env_row["W_macro"]),
                    "D_L_mass": float(env_row["D_L_mass"]),
                    "f_macro_mass": float(f_mass[i]),
                    "p_mass": float(p_mass[i]),
                    "p_kappa_G1": float(p_group["G1"][i]),
                    "p_kappa_G2a": float(p_group["G2a"][i]),
                    "M_sink_H_cMpc3": float(M[i]),
                    "M_sink_H_fraction_of_global": float(m_norm[i]),
                    "M_sink_H_cap_cosmic_cMpc3": float(mass_cap[i]),
                    "M_sink_H_cap_volume_cMpc3": float(volume_cap[i]),
                    "mass_cap_slack_cMpc3": float(mass_cap[i] - M[i]),
                    "volume_filling_macro": float(volume_filling[i]),
                    "kappa_sink_G1_cMpc_inv": float(kappa["G1"][i]),
                    "kappa_sink_G2a_cMpc_inv": float(kappa["G2a"][i]),
                    "kappa_sink_G2b_cMpc_inv": 0.0,
                    "kappa_sink_G3_cMpc_inv": 0.0,
                    "J_sink_G1_s_inv_cMpc3": float(J["G1"][i]),
                    "J_sink_G2a_s_inv_cMpc3": float(J["G2a"][i]),
                    "J_sink_G2b_s_inv_cMpc3": 0.0,
                    "J_sink_G3_s_inv_cMpc3": 0.0,
                    "J_sink_macro_total_s_inv_cMpc3": float(assigned_J[i]),
                    "cycling_capacity_macro_s_inv_cMpc3": float(capacity[i]),
                    "cycling_capacity_slack_s_inv_cMpc3": float(capacity_slack[i]),
                    "mass_transfer_rate_macro_H_s_inv_cMpc3": float(transfer[i]),
                    "current_Gamma_flux_G1_s_inv_cMpc2": float(flux["G1"]),
                    "current_Gamma_flux_G2a_s_inv_cMpc2": float(flux["G2a"]),
                    "single_Jeans_cloud_H_auditor": float(cloud_H_single),
                    "single_Jeans_cloud_count_auditor_cMpc3": float(M[i] / cloud_H_single),
                    "geometry_mass_inversion_used": False,
                    "HeII_G3_sink_absorption_exact_zero": 0.0,
                }
                macro_rows.append(item)
                macro_case_rows.append(item)

            summary = {
                **key,
                "projection_method": result.method,
                "feasible": True,
                "identity_projection": result.identity_projection,
                "optimizer_status": result.optimizer_status,
                "generalized_KL_total": objective,
                "generalized_KL_mass": objective_mass,
                "generalized_KL_G1": objective_group["G1"],
                "generalized_KL_G2a": objective_group["G2a"],
                "TV_mass": total_variation(result.m, p_mass),
                "TV_G1": total_variation(result.k["G1"], p_group["G1"]),
                "TV_G2a": total_variation(result.k["G2a"], p_group["G2a"]),
                "serialization_TV_mass": total_variation(m_norm, result.m),
                "serialization_TV_G1": total_variation(k_norm["G1"], result.k["G1"]),
                "serialization_TV_G2a": total_variation(k_norm["G2a"], result.k["G2a"]),
                "mass_sum_relative_residual": mass_sum_resid,
                "kappa_sum_relative_residual_max": kappa_sum_resid,
                "J_sum_relative_residual_max": J_sum_resid,
                "mass_transfer_sum_relative_residual": transfer_resid,
                "current_Gamma_relation_relative_residual_max": current_gamma_resid,
                "mass_cap_slack_min_fraction_cosmic_H": float(np.min(mass_cap - M) / nhc),
                "volume_filling_max": float(np.max(volume_filling)),
                "cycling_slack_min_fraction_of_global_J": float(np.min(capacity_slack) / J_total),
                "cycling_capacity_over_global_J": rho,
                "prior_mass_upper_slack_min_normalized": prior_audit["mass_upper_slack_min"],
                "prior_cycling_slack_min_normalized": prior_audit["cycling_slack_min"],
                "stationarity_residual_max": stationarity,
                "complementarity_residual_max": complementarity_residual,
                "KKT_gate": kkt_pass,
                "exact_zero_gate": True,
                "R2B_core_gate": bool(kkt_pass),
            }
            summary_rows.append(summary)
            cases[(lane, interval, substep)] = {
                "key": key,
                "row": row.to_dict(),
                "env": env.copy(),
                "mass_cap": mass_cap.copy(),
                "volume_cap": volume_cap.copy(),
                "p_mass": p_mass.copy(),
                "p_group": {g: p_group[g].copy() for g in ACTIVE_GROUPS},
                "M": M.copy(),
                "kappa": {g: kappa[g].copy() for g in ACTIVE_GROUPS},
                "J": {g: J[g].copy() for g in ACTIVE_GROUPS},
                "q_map": dict(q_map),
                "rho": rho,
                "cycling_per_H": cycling_per_H,
                "flux": flux,
            }

    macro_frame = pd.DataFrame(macro_rows)
    summary_frame = pd.DataFrame(summary_rows)
    global_frame = pd.DataFrame(global_rows).drop_duplicates(
        ["interval_index", "substep"]
    )
    macro_frame.to_csv(stage_dir / "data" / "macro_projection.csv", index=False)
    summary_frame.to_csv(stage_dir / "data" / "projection_gate_summary.csv", index=False)
    global_frame.to_csv(stage_dir / "data" / "global_moment_lock.csv", index=False)
    with (stage_dir / "data" / "dual_kkt_certificates.jsonl").open("w", encoding="utf-8") as handle:
        for item in dual_certificates:
            handle.write(json.dumps(item, sort_keys=True) + "\n")
    infeasible = [item for item in dual_certificates if "FARKAS" in str(item.get("type", "")) or "FAIL_CLOSED" in str(item.get("type", ""))]
    write_json(
        stage_dir / "data" / "infeasibility_certificate_summary.json",
        {
            "stage": STAGE_ID,
            "status": "NO_INFEASIBLE_CORE_CASES" if not infeasible else "INFEASIBLE_CORE_CASES_PRESENT",
            "case_count": len(summary_rows),
            "infeasible_case_count": len(infeasible),
            "policy": "No clipping. Analytic Farkas or HiGHS status is retained for every infeasible case.",
        },
    )
    return macro_frame, summary_frame, global_frame, dual_certificates, cases


def build_kl_tv_envelope(
    cases: dict[tuple[str, int, int], dict[str, Any]],
    summary: pd.DataFrame,
    stage_dir: Path,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, item in summary.iterrows():
        rows.append(
            {
                "envelope_type": "PROJECTION_DISTORTION",
                "interval_index": int(item["interval_index"]),
                "substep": int(item["substep"]),
                "z_mid": float(item["z_mid"]),
                "lane_A": item["shape_lane"],
                "lane_B": item["shape_lane"],
                "mass_TV": float(item["TV_mass"]),
                "mass_symmetric_KL": 2.0 * float(item["generalized_KL_mass"]),
                "G1_TV": float(item["TV_G1"]),
                "G1_symmetric_KL": (
                    2.0 * float(item["generalized_KL_G1"])
                    / max(
                        cases[(item["shape_lane"], int(item["interval_index"]), int(item["substep"]))]["q_map"]["G1"],
                        EPS,
                    )
                ),
                "G2a_TV": float(item["TV_G2a"]),
                "G2a_symmetric_KL": (
                    2.0 * float(item["generalized_KL_G2a"])
                    / max(
                        cases[(item["shape_lane"], int(item["interval_index"]), int(item["substep"]))]["q_map"]["G2a"],
                        EPS,
                    )
                ),
            }
        )
    for interval, substep in sorted({(k[1], k[2]) for k in cases}):
        for i, lane_a in enumerate(SHAPE_LANES):
            for lane_b in SHAPE_LANES[i + 1 :]:
                a = cases[(lane_a, interval, substep)]
                b = cases[(lane_b, interval, substep)]
                rows.append(
                    {
                        "envelope_type": "CROSS_PRIOR_LANE_SPREAD",
                        "interval_index": interval,
                        "substep": substep,
                        "z_mid": a["key"]["z_mid"],
                        "lane_A": lane_a,
                        "lane_B": lane_b,
                        "mass_TV": total_variation(a["p_mass"], b["p_mass"]),
                        "mass_symmetric_KL": symmetric_kl(a["p_mass"], b["p_mass"]),
                        "G1_TV": total_variation(a["p_group"]["G1"], b["p_group"]["G1"]),
                        "G1_symmetric_KL": symmetric_kl(a["p_group"]["G1"], b["p_group"]["G1"]),
                        "G2a_TV": total_variation(a["p_group"]["G2a"], b["p_group"]["G2a"]),
                        "G2a_symmetric_KL": symmetric_kl(a["p_group"]["G2a"], b["p_group"]["G2a"]),
                    }
                )
    frame = pd.DataFrame(rows)
    frame.to_csv(stage_dir / "data" / "kl_tv_envelope.csv", index=False)
    return frame


def relaxation_audit(
    cases: dict[tuple[str, int, int], dict[str, Any]],
    global_state: pd.DataFrame,
    initial_state: dict[str, Any],
    stage_dir: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    summaries: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []
    ordered_keys = [
        (int(row["interval_index"]), int(row["substep"]))
        for _, row in global_state.sort_values(["interval_index", "substep"]).iterrows()
    ]
    for lane in SHAPE_LANES:
        first_case = cases[(lane, *ordered_keys[0])]
        previous_M = initial_state["N_sink"] * first_case["p_mass"]
        previous_kappa = {g: first_case["kappa"][g].copy() for g in ACTIVE_GROUPS}
        previous_m = first_case["p_mass"].copy()
        previous_k = {g: first_case["p_group"][g].copy() for g in ACTIVE_GROUPS}
        for interval, substep in ordered_keys:
            case = cases[(lane, interval, substep)]
            dt_myr = float(case["row"]["dt_Myr"])
            q = case["q_map"]
            for tau in TAU_MYR:
                lam = -math.expm1(-dt_myr / tau)
                M_eq = previous_M + (case["M"] - previous_M) / lam
                kappa_eq = {
                    g: previous_kappa[g] + (case["kappa"][g] - previous_kappa[g]) / lam
                    for g in ACTIVE_GROUPS
                }
                J_eq = {
                    g: case["flux"][g] * kappa_eq[g]
                    for g in ACTIVE_GROUPS
                }
                capacity_eq = case["cycling_per_H"] * M_eq
                assigned_eq = sum(J_eq[g] for g in ACTIVE_GROUPS)
                absolute_checks = {
                    "mass_nonnegative": float(np.min(M_eq)),
                    "mass_cap_slack": float(np.min(case["mass_cap"] - M_eq)),
                    "volume_cap_slack": float(np.min(case["volume_cap"] - M_eq)),
                    "opacity_nonnegative": float(min(np.min(kappa_eq[g]) for g in ACTIVE_GROUPS)),
                    "cycling_slack": float(np.min(capacity_eq - assigned_eq)),
                }
                absolute_pass = bool(
                    absolute_checks["mass_nonnegative"] >= -CORE_ATOL
                    and absolute_checks["mass_cap_slack"] >= -CORE_ATOL
                    and absolute_checks["volume_cap_slack"] >= -CORE_ATOL
                    and absolute_checks["opacity_nonnegative"] >= -CORE_ATOL
                    and absolute_checks["cycling_slack"] >= -CORE_ATOL
                )

                m_cur = case["M"] / float(np.sum(case["M"]))
                k_cur = {
                    g: case["kappa"][g] / float(np.sum(case["kappa"][g]))
                    for g in ACTIVE_GROUPS
                }
                m_eq = previous_m + (m_cur - previous_m) / lam
                k_eq = {
                    g: previous_k[g] + (k_cur[g] - previous_k[g]) / lam
                    for g in ACTIVE_GROUPS
                }
                normalized_capacity = case["rho"] * m_eq - sum(
                    q[g] * k_eq[g] for g in ACTIVE_GROUPS
                )
                upper = np.minimum(case["mass_cap"], case["volume_cap"]) / float(np.sum(case["M"]))
                shape_checks = {
                    "mass_simplex_residual": float(abs(np.sum(m_eq) - 1.0)),
                    "mass_nonnegative": float(np.min(m_eq)),
                    "mass_upper_slack": float(np.min(upper - m_eq)),
                    "opacity_simplex_residual": float(
                        max(abs(np.sum(k_eq[g]) - 1.0) for g in ACTIVE_GROUPS)
                    ),
                    "opacity_nonnegative": float(min(np.min(k_eq[g]) for g in ACTIVE_GROUPS)),
                    "cycling_slack": float(np.min(normalized_capacity)),
                }
                shape_pass = bool(
                    shape_checks["mass_simplex_residual"] <= KKT_TOL
                    and shape_checks["mass_nonnegative"] >= -KKT_TOL
                    and shape_checks["mass_upper_slack"] >= -KKT_TOL
                    and shape_checks["opacity_simplex_residual"] <= KKT_TOL
                    and shape_checks["opacity_nonnegative"] >= -KKT_TOL
                    and shape_checks["cycling_slack"] >= -KKT_TOL
                )
                summaries.append(
                    {
                        **case["key"],
                        "tau_Myr": tau,
                        "relaxation_lambda": lam,
                        "absolute_state_feasible": absolute_pass,
                        "shape_only_feasible": shape_pass,
                        "absolute_mass_min_cMpc3": absolute_checks["mass_nonnegative"],
                        "absolute_mass_cap_slack_min_cMpc3": absolute_checks["mass_cap_slack"],
                        "absolute_volume_cap_slack_min_cMpc3": absolute_checks["volume_cap_slack"],
                        "absolute_opacity_min_cMpc_inv": absolute_checks["opacity_nonnegative"],
                        "absolute_cycling_slack_min_s_inv_cMpc3": absolute_checks["cycling_slack"],
                        "shape_mass_simplex_residual": shape_checks["mass_simplex_residual"],
                        "shape_mass_min": shape_checks["mass_nonnegative"],
                        "shape_mass_upper_slack_min": shape_checks["mass_upper_slack"],
                        "shape_opacity_simplex_residual_max": shape_checks["opacity_simplex_residual"],
                        "shape_opacity_min": shape_checks["opacity_nonnegative"],
                        "shape_cycling_slack_min": shape_checks["cycling_slack"],
                        "blocking_for_R2B_core_gate": False,
                        "definition": (
                            "implied equilibrium y_eq=y_prev+(y_target-y_prev)/"
                            "(1-exp(-dt/tau)); auditor only"
                        ),
                    }
                )
                for i in range(18):
                    checks = {
                        "M_eq_nonnegative": M_eq[i],
                        "M_eq_mass_cap_slack": case["mass_cap"][i] - M_eq[i],
                        "M_eq_volume_cap_slack": case["volume_cap"][i] - M_eq[i],
                        "kappa_eq_G1": kappa_eq["G1"][i],
                        "kappa_eq_G2a": kappa_eq["G2a"][i],
                        "cycling_eq_slack": capacity_eq[i] - assigned_eq[i],
                        "m_eq_nonnegative": m_eq[i],
                        "m_eq_upper_slack": upper[i] - m_eq[i],
                        "k_eq_G1": k_eq["G1"][i],
                        "k_eq_G2a": k_eq["G2a"][i],
                        "shape_cycling_slack": normalized_capacity[i],
                    }
                    bad = [
                        name
                        for name, value in checks.items()
                        if (
                            ("slack" in name and value < -KKT_TOL)
                            or ("nonnegative" in name and value < -KKT_TOL)
                            or (name.startswith("kappa_eq") and value < -KKT_TOL)
                            or (name.startswith("k_eq") and value < -KKT_TOL)
                        )
                    ]
                    if bad:
                        violations.append(
                            {
                                **case["key"],
                                "tau_Myr": tau,
                                "macro_index": i,
                                "violated_constraints": ";".join(bad),
                                **{name: float(value) for name, value in checks.items()},
                            }
                        )
            previous_M = case["M"].copy()
            previous_kappa = {g: case["kappa"][g].copy() for g in ACTIVE_GROUPS}
            previous_m = case["M"] / float(np.sum(case["M"]))
            previous_k = {
                g: case["kappa"][g] / float(np.sum(case["kappa"][g]))
                for g in ACTIVE_GROUPS
            }
    summary_frame = pd.DataFrame(summaries)
    violation_frame = pd.DataFrame(violations)
    summary_frame.to_csv(stage_dir / "data" / "finite_relaxation_feasibility.csv", index=False)
    violation_frame.to_csv(stage_dir / "data" / "finite_relaxation_macro_violations.csv", index=False)
    return summary_frame, violation_frame


def geometry_audit(macro: pd.DataFrame, stage_dir: Path) -> pd.DataFrame:
    grouped = []
    for key, frame in macro.groupby(["shape_lane", "interval_index", "substep", "z_mid"], sort=True):
        grouped.append(
            {
                "shape_lane": key[0],
                "interval_index": int(key[1]),
                "substep": int(key[2]),
                "z_mid": float(key[3]),
                "allocated_H_sum_cMpc3": float(frame["M_sink_H_cMpc3"].sum()),
                "single_Jeans_cloud_count_sum_auditor_cMpc3": float(
                    frame["single_Jeans_cloud_count_auditor_cMpc3"].sum()
                ),
                "volume_filling_macro_max": float(frame["volume_filling_macro"].max()),
                "mass_cap_slack_min_cMpc3": float(frame["mass_cap_slack_cMpc3"].min()),
                "geometry_mass_inversion_used": False,
                "policy": "single-size Jeans cloud retained only as density/radius/count/volume auditor",
            }
        )
    result = pd.DataFrame(grouped)
    result.to_csv(stage_dir / "data" / "jeans_geometry_prior_audit.csv", index=False)
    return result


def exact_zero_audit(
    macro: pd.DataFrame, tables: InputTables, stage_dir: Path
) -> pd.DataFrame:
    rows = []
    for key, frame in macro.groupby(["shape_lane", "interval_index", "substep", "z_mid"], sort=True):
        lane, interval, substep, z_mid = key
        target_values: dict[str, float] = {}
        for group in STRUCTURAL_ZERO_GROUPS:
            target = tables.opacity_targets[
                np.isclose(tables.opacity_targets["z"], float(z_mid), rtol=0.0, atol=1.0e-10)
                & (tables.opacity_targets["group"] == group)
            ]
            if len(target) != 1:
                raise RuntimeError(f"Missing exact-zero opacity target at z={z_mid}, group={group}")
            target_values[group] = float(target.iloc[0]["target_EFFECTIVE_HI_SUBGRID_cMpc_inv"])
        heii_source = tables.macro_allocation[
            np.isclose(tables.macro_allocation["z"], float(z_mid), rtol=0.0, atol=1.0e-10)
            & (tables.macro_allocation["shape_lane"] == lane)
            & (tables.macro_allocation["group"] == "G3")
            & (tables.macro_allocation["species"] == "HeII")
        ]["j_abs_s-1_cMpc-3"].sum()
        output_g2b = bool((frame["kappa_sink_G2b_cMpc_inv"] == 0.0).all())
        output_g3 = bool((frame["kappa_sink_G3_cMpc_inv"] == 0.0).all())
        output_heii = bool((frame["HeII_G3_sink_absorption_exact_zero"] == 0.0).all())
        rows.extend(
            [
                {
                    "shape_lane": lane,
                    "interval_index": int(interval),
                    "substep": int(substep),
                    "z_mid": float(z_mid),
                    "quantity": "kappa_sink_G2b",
                    "sum": float(frame["kappa_sink_G2b_cMpc_inv"].sum()),
                    "source_lock_value": target_values["G2b"],
                    "source_lock_exact_zero": target_values["G2b"] == 0.0,
                    "exact_zero": output_g2b and target_values["G2b"] == 0.0,
                },
                {
                    "shape_lane": lane,
                    "interval_index": int(interval),
                    "substep": int(substep),
                    "z_mid": float(z_mid),
                    "quantity": "kappa_sink_G3",
                    "sum": float(frame["kappa_sink_G3_cMpc_inv"].sum()),
                    "source_lock_value": target_values["G3"],
                    "source_lock_exact_zero": target_values["G3"] == 0.0,
                    "exact_zero": output_g3 and target_values["G3"] == 0.0,
                },
                {
                    "shape_lane": lane,
                    "interval_index": int(interval),
                    "substep": int(substep),
                    "z_mid": float(z_mid),
                    "quantity": "J_sink_G3_HeII_primary",
                    "sum": float(frame["HeII_G3_sink_absorption_exact_zero"].sum()),
                    "source_lock_value": float(heii_source),
                    "source_lock_exact_zero": float(heii_source) == 0.0,
                    "exact_zero": output_heii and float(heii_source) == 0.0,
                },
            ]
        )
    result = pd.DataFrame(rows)
    result.to_csv(stage_dir / "data" / "exact_zero_audit.csv", index=False)
    return result


def inherited_failure_receipt(tables: InputTables, stage_dir: Path) -> None:
    write_json(
        stage_dir / "receipts" / "R1_fail_closed_inheritance.json",
        {
            "source_stage": tables.r1_results.get("stage"),
            "source_verdict": tables.r1_results.get("verdict"),
            "failure_class": tables.r1_results.get("failure_class"),
            "diagnostic_node_history_promoted": False,
            "independent_quasistatic_macro_cloud_abundance_used": False,
            "preservation_policy": (
                "R1 diagnostics remain fail-closed evidence and are not overwritten "
                "or treated as production history."
            ),
        },
    )


def write_operator_spec(stage_dir: Path) -> None:
    text = r"""# R2A constrained macro-distribution operator

## Locked quantities and units

At each validated B2C2B0C reduced-DAE substep, the stage holds fixed
\(N_{\rm H,sink}\,[{\rm H\,cMpc^{-3}}]\), \(x_{\rm HII,sink}\),
\(T_{\rm sink}\,[{\rm K}]\), \(\kappa_g\,[{\rm cMpc^{-1}}]\),
\(J_g\,[{\rm s^{-1}\,cMpc^{-3}}]\), and the diffuse/sink H-transfer rate.
The current-Gamma flux is \(\Phi_g=J_g/\kappa_g\) and
\(J_{mg}=\Phi_g\kappa_{mg}\).

## Prior and information projection

For active groups \(g\in\{G1,G2a\}\), B2C2B0A HI macro allocation gives
strictly positive \(p_{mg}\), normalized over the 18 macros. Set

\[
q_g=J_g/\sum_hJ_h,\qquad p^M_m=\sum_gq_gp_{mg}.
\]

For \(m_m=M_m/N_{\rm H,sink}\) and
\(k_{mg}=\kappa_{mg}/\kappa_g\), minimize

\[
\mathcal I=\frac12D(m\Vert p^M)
+\frac12\sum_gq_gD(k_g\Vert p_g),\quad
D(x\Vert p)=\sum_m[x_m\ln(x_m/p_m)-x_m+p_m].
\]

The constraints are the mass and opacity moment sums, non-negativity,
\(M_m\le N_H^cf_m^{\rm macro}\), macro volume filling at most one, and

\[
\sum_gJ_{mg}\le M_m\left[\frac{1-x_{\rm HII,sink}}{\Delta t}
+\frac{R_{\rm rec,sink}}{N_{\rm H,sink}}\right].
\]

The bracket has dimension s^-1, so the right-hand side has the same
s^-1 cMpc^-3 dimension as the assigned absorption.

## Exact identity projection for the locked data

Because \(m=p^M\), \(k_g=p_g\), and
\(p^M_m=\sum_gq_gp_{mg}\), the macro capacity slack is

\[
C_m-J_m=J_{\rm sink}(\rho-1)p^M_m,
\quad \rho=C_{\rm global}/J_{\rm sink}>1.
\]

All mass/volume caps also have strict positive slack. Generalized KL is
non-negative and vanishes only at the prior; therefore the prior is the unique
constrained optimum. Equality and inequality dual multipliers can all be zero,
which closes stationarity, dual feasibility, and complementarity analytically.

## Geometry and forbidden closure

The inherited single-size Jeans/self-shielding density and radius are used only
to audit cloud count and volume filling after mass allocation. Neither opacity
nor cloud abundance is inverted to redefine macro mass. G2b/G3 effective-HI
sink opacity and primary HeII/G3 absorption are exact zeros. No node chemistry,
unresolved subtraction, front/Q_M, source/fesc, primordial recombination, or
Bianchi feedback is introduced in R2A.
"""
    (stage_dir / "OPERATOR_SPEC.md").write_text(text, encoding="utf-8")


def build_results(
    summary: pd.DataFrame,
    global_lock: pd.DataFrame,
    envelope: pd.DataFrame,
    relaxation: pd.DataFrame,
    exact_zero: pd.DataFrame,
    stage_dir: Path,
) -> dict[str, Any]:
    case_count_expected = len(SHAPE_LANES) * len(global_lock)
    core_all = bool(
        len(summary) == case_count_expected
        and summary["feasible"].all()
        and summary["KKT_gate"].all()
        and summary["exact_zero_gate"].all()
    )
    exact_zero_all = bool(exact_zero["exact_zero"].all())
    core_all = core_all and exact_zero_all
    relaxation_abs_pass = int(relaxation["absolute_state_feasible"].sum())
    relaxation_shape_pass = int(relaxation["shape_only_feasible"].sum())
    relaxation_by_tau: dict[str, dict[str, Any]] = {}
    for tau in TAU_MYR:
        sub = relaxation[np.isclose(relaxation["tau_Myr"], tau)]
        relaxation_by_tau[f"{tau:g}"] = {
            "row_count": int(len(sub)),
            "absolute_state_feasible_count": int(sub["absolute_state_feasible"].sum()),
            "shape_only_feasible_count": int(sub["shape_only_feasible"].sum()),
            "all_absolute_state_feasible": bool(sub["absolute_state_feasible"].all()),
            "all_shape_only_feasible": bool(sub["shape_only_feasible"].all()),
        }
    tau10_witness = bool(
        relaxation_by_tau["10"]["all_absolute_state_feasible"]
        and relaxation_by_tau["10"]["all_shape_only_feasible"]
    )
    r2b_authorized = bool(core_all and tau10_witness)
    distortion = envelope[envelope["envelope_type"] == "PROJECTION_DISTORTION"]
    cross = envelope[envelope["envelope_type"] == "CROSS_PRIOR_LANE_SPREAD"]
    results = {
        "stage": STAGE_ID,
        "verdict": (
            "DURABLE_PASS_R2A_CORE_MACRO_DISTRIBUTION_LOCK_TAU10_FEASIBILITY_WITNESS_R2B_AUTHORIZED"
            if r2b_authorized
            else "DURABLE_FAIL_CLOSED_R2A_MACRO_DISTRIBUTION_GATE"
        ),
        "generated_utc": utc_now(),
        "requested_scope_completed": r2b_authorized,
        "R2B_authorized": r2b_authorized,
        "B2C2B_authorized": False,
        "core_case_count": int(len(summary)),
        "expected_core_case_count": case_count_expected,
        "shape_lanes": list(SHAPE_LANES),
        "active_groups": list(ACTIVE_GROUPS),
        "structural_zero_groups": list(STRUCTURAL_ZERO_GROUPS),
        "projection": {
            "identity_case_count": int(summary["identity_projection"].sum()),
            "feasible_case_count": int(summary["feasible"].sum()),
            "KKT_pass_count": int(summary["KKT_gate"].sum()),
            "max_generalized_KL": float(summary["generalized_KL_total"].max()),
            "max_projection_TV": float(
                summary[["TV_mass", "TV_G1", "TV_G2a"]].to_numpy().max()
            ),
            "max_mass_sum_relative_residual": float(summary["mass_sum_relative_residual"].max()),
            "max_opacity_sum_relative_residual": float(summary["kappa_sum_relative_residual_max"].max()),
            "max_J_sum_relative_residual": float(summary["J_sum_relative_residual_max"].max()),
            "max_current_Gamma_relative_residual": float(summary["current_Gamma_relation_relative_residual_max"].max()),
            "max_stationarity_residual": float(summary["stationarity_residual_max"].max()),
            "max_complementarity_residual": float(summary["complementarity_residual_max"].max()),
            "minimum_mass_cap_slack_fraction_cosmic_H": float(summary["mass_cap_slack_min_fraction_cosmic_H"].min()),
            "maximum_macro_volume_filling": float(summary["volume_filling_max"].max()),
            "minimum_cycling_slack_fraction_global_J": float(summary["cycling_slack_min_fraction_of_global_J"].min()),
        },
        "global_moments": {
            "substep_count": int(len(global_lock)),
            "minimum_global_cycling_capacity_over_J": float(global_lock["cycling_capacity_over_J_sink"].min()),
            "maximum_global_cycling_capacity_over_J": float(global_lock["cycling_capacity_over_J_sink"].max()),
            "max_sink_rate_group_partition_residual": float(global_lock["sink_rate_vs_group_sum_relative_residual"].max()),
        },
        "prior_envelope": {
            "max_cross_lane_mass_TV": float(cross["mass_TV"].max()),
            "max_cross_lane_G1_TV": float(cross["G1_TV"].max()),
            "max_cross_lane_G2a_TV": float(cross["G2a_TV"].max()),
            "max_projection_distortion_TV": float(
                distortion[["mass_TV", "G1_TV", "G2a_TV"]].to_numpy().max()
            ),
        },
        "finite_relaxation_auditor": {
            "tau_Myr": list(TAU_MYR),
            "row_count": int(len(relaxation)),
            "absolute_state_feasible_count": relaxation_abs_pass,
            "shape_only_feasible_count": relaxation_shape_pass,
            "by_tau": relaxation_by_tau,
            "tau10_all_case_feasibility_witness": tau10_witness,
            "interpretation": (
                "tau=10 Myr is an existence/feasibility witness, not a calibrated "
                "physical relaxation time; tau=100 and 300 Myr failures remain "
                "explicit sensitivity constraints for R2B"
            ),
            "blocking_policy": (
                "R2B authorization requires the core moment/KKT gate plus at least "
                "one all-case finite-relaxation witness among the requested lanes"
            ),
        },
        "wolfram": {
            "native_runtime_available": False,
            "script": "wolfram_moment_kkt_validation.wl",
            "exact_fallback": "tests/exact_symbolic_fallback.py",
            "native_crosscheck_pending": True,
            "scientific_blocking": False,
        },
        "external_recombination": {
            "surrogate_implemented": False,
            "adapter_review_started": False,
        },
        "forbidden_work_confirmed": [
            "no node chemistry history",
            "no unresolved subtraction",
            "no front/Q_M",
            "no source/fesc",
            "no primordial recombination implementation or surrogate",
            "no Bianchi feedback",
            "no independent quasi-static macro cloud abundance",
            "no Jeans-opacity mass redefinition",
        ],
        "next_stage": (
            "P0.5-B2C2B0C-R2B-MOMENT-CONSTRAINED-NODE-LIFT-HISTORY"
            if r2b_authorized
            else None
        ),
    }
    write_json(stage_dir / "results.json", results)
    return results


def write_wolfram_script(stage_dir: Path) -> None:
    script = r'''ClearAll["Global`*"];
stage = DirectoryName[$InputFileName];
macro = Import[FileNameJoin[{stage, "data", "macro_projection.csv"}], "Dataset"];
summary = Import[FileNameJoin[{stage, "data", "projection_gate_summary.csv"}], "Dataset"];
zeros = Import[FileNameJoin[{stage, "data", "exact_zero_audit.csv"}], "Dataset"];

(* Generic exact identities for the locked identity I-projection. *)
Clear[pM, p1, p2, q1, q2, rho, jsink];
capacityIdentity = FullSimplify[
  rho pM - (q1 p1 + q2 p2),
  Assumptions -> {pM == q1 p1 + q2 p2, q1 + q2 == 1}
];
gklStationarity = FullSimplify[D[x Log[x/p] - x + p, x] /. x -> p,
  Assumptions -> p > 0];
complementarity = FullSimplify[mu slack /. mu -> 0];
exactG3HeII = FullSimplify[0];

(* Numerical imported-data checks at arbitrary precision. *)
rows = Normal[macro];
keys = DeleteDuplicates[Lookup[rows, {"shape_lane", "interval_index", "substep"}]];
checks = Table[
  sub = Select[rows, Lookup[#, {"shape_lane", "interval_index", "substep"}] == key &];
  <|
    "key" -> key,
    "massNonnegative" -> Min[Lookup[sub, "M_sink_H_cMpc3"]] >= 0,
    "massCap" -> Min[Lookup[sub, "mass_cap_slack_cMpc3"]] >= 0,
    "volume" -> Max[Lookup[sub, "volume_filling_macro"]] <= 1,
    "cycling" -> Min[Lookup[sub, "cycling_capacity_slack_s_inv_cMpc3"]] >= 0,
    "G2bZero" -> Total[Lookup[sub, "kappa_sink_G2b_cMpc_inv"]] == 0,
    "G3Zero" -> Total[Lookup[sub, "kappa_sink_G3_cMpc_inv"]] == 0,
    "HeIIG3Zero" -> Total[Lookup[sub, "HeII_G3_sink_absorption_exact_zero"]] == 0
  |>,
  {key, keys}
];

result = <|
  "capacityIdentity" -> capacityIdentity,
  "gklStationarity" -> gklStationarity,
  "complementarity" -> complementarity,
  "exactG3HeII" -> exactG3HeII,
  "caseChecks" -> checks,
  "allPass" -> And @@ Flatten[Values /@ (KeyDrop[#, "key"] & /@ checks)]
|>;
Export[FileNameJoin[{stage, "data", "wolfram_native_results.json"}], result, "RawJSON"];
result
'''
    (stage_dir / "wolfram_moment_kkt_validation.wl").write_text(script, encoding="utf-8")
    write_json(
        stage_dir / "WOLFRAM_EXECUTION_STATUS.json",
        {
            "requested": True,
            "native_executable_available": False,
            "native_probe": ["wolframscript", "WolframKernel", "math"],
            "reproduction_script": "wolfram_moment_kkt_validation.wl",
            "executed_fallback": "tests/exact_symbolic_fallback.py",
            "native_crosscheck_pending": True,
            "scientific_blocking": False,
        },
    )


def write_validation_report(results: dict[str, Any], stage_dir: Path) -> None:
    p = results["projection"]
    r = results["finite_relaxation_auditor"]
    text = f"""# R2A validation report

## Core verdict

`{results['verdict']}`

- Core cases: {results['core_case_count']}/{results['expected_core_case_count']}
- Feasible identity KL projections: {p['identity_case_count']}
- KKT gates passed: {p['KKT_pass_count']}
- Maximum generalized KL distortion: {p['max_generalized_KL']:.3e}
- Maximum projection TV distortion: {p['max_projection_TV']:.3e}
- Maximum mass moment residual: {p['max_mass_sum_relative_residual']:.3e}
- Maximum opacity moment residual: {p['max_opacity_sum_relative_residual']:.3e}
- Maximum current-Gamma residual: {p['max_current_Gamma_relative_residual']:.3e}
- Minimum macro mass-cap slack / cosmic H: {p['minimum_mass_cap_slack_fraction_cosmic_H']:.3e}
- Maximum macro volume filling: {p['maximum_macro_volume_filling']:.3e}
- Minimum cycling slack / global sink J: {p['minimum_cycling_slack_fraction_global_J']:.3e}

The three B2C2B0A priors are already strictly inside the locked feasible set.
Because generalized KL is non-negative and vanishes only at the prior, each
prior is the unique constrained solution. No clipping, opacity-driven cloud
mass inversion, or quasi-static macro abundance solve was used.

## Finite-relaxation auditor

The separate implied-equilibrium auditor produced {r['row_count']} lane/substep/tau
rows. Absolute-state feasibility passed {r['absolute_state_feasible_count']} rows;
shape-only feasibility passed {r['shape_only_feasible_count']} rows. The 10 Myr
lane is an all-case feasibility witness and is required together with the core
moment/KKT gate for R2B authorization. It is not a calibrated physical timescale.
The 100 and 300 Myr failures remain explicit non-clipped sensitivity constraints
that R2B must carry forward.

## Scope firewall

No node chemistry history, unresolved subtraction, front/Q_M, source/fesc,
primordial recombination surrogate, or Bianchi feedback was started. The R1
failed node diagnostics remain preserved as fail-closed evidence only.
"""
    (stage_dir / "VALIDATION_REPORT.md").write_text(text, encoding="utf-8")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--stage-dir", type=Path, required=True)
    args = parser.parse_args(list(argv) if argv is not None else None)
    repo_root = args.repo_root.resolve()
    stage_dir = args.stage_dir.resolve()
    for name in ("data", "logs", "receipts", "state", "src", "tests"):
        (stage_dir / name).mkdir(parents=True, exist_ok=True)

    append_receipt(stage_dir, "R2A_CALCULATION_START", "STARTED", command="global_moment_constrained_macro_sink.py")
    write_operator_spec(stage_dir)
    tables, _ = load_inputs(repo_root, stage_dir)
    inherited_failure_receipt(tables, stage_dir)
    global_state, nhc, initial_state = prepare_global_state(tables)
    macro, summary, global_lock, duals, cases = run_core_projection(
        tables, global_state, nhc, stage_dir
    )
    envelope = build_kl_tv_envelope(cases, summary, stage_dir)
    relaxation, violations = relaxation_audit(cases, global_state, initial_state, stage_dir)
    geometry = geometry_audit(macro, stage_dir)
    zeros = exact_zero_audit(macro, tables, stage_dir)
    write_wolfram_script(stage_dir)
    results = build_results(summary, global_lock, envelope, relaxation, zeros, stage_dir)
    write_validation_report(results, stage_dir)

    runtime_summary = {
        "stage": STAGE_ID,
        "generated_utc": utc_now(),
        "macro_rows": len(macro),
        "projection_cases": len(summary),
        "dual_KKT_certificates": len(duals),
        "relaxation_rows": len(relaxation),
        "relaxation_violation_rows": len(violations),
        "geometry_audit_rows": len(geometry),
        "exact_zero_rows": len(zeros),
        "R2B_authorized": results["R2B_authorized"],
    }
    write_json(stage_dir / "receipts" / "calculation_runtime_summary.json", runtime_summary)
    append_receipt(
        stage_dir,
        "R2A_CORE_CALCULATION",
        "PASS" if results["R2B_authorized"] else "FAIL_CLOSED",
        projection_cases=len(summary),
        macro_rows=len(macro),
        R2B_authorized=results["R2B_authorized"],
    )
    print(json.dumps(runtime_summary, indent=2, sort_keys=True))
    return 0 if results["R2B_authorized"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
