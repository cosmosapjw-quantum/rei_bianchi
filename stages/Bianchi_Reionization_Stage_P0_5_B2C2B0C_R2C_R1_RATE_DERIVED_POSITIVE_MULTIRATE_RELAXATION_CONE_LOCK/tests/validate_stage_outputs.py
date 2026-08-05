#!/usr/bin/env python3
"""Independent output/certificate validator for the durable R2C-R1 stage.

This auditor intentionally does not import any R2C-R1 production module.  It
replays every emitted Farkas/KKT certificate from its self-contained columns,
RHS values, primal variables, and weights.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

STAGE = Path(__file__).resolve().parents[1]
DATA = STAGE / "data"
RECEIPTS = STAGE / "receipts"
OUT = RECEIPTS / "independent_stage_validation.json"
LANES = (
    "LOCAL_NEUTRAL_HAZARD_PRIMARY",
    "RECOMBINATION_WEIGHTED_AUDITOR",
    "SCRIPT_SELF_SHIELDING_AUDITOR",
)
FAMILIES = ("M", "I", "U", "C", "J_G1", "J_G2a")
KEY = ["shape_lane", "interval_index", "substep", "macro_index"]
RATE_KEY = KEY + ["family"]
REL_TOL = 1.0e-11


def require(condition: bool, message: str) -> None:
    if not bool(condition):
        raise AssertionError(message)


def close(a: float, b: float, *, rtol: float = 1.0e-12, atol: float = 1.0e-14) -> bool:
    return math.isclose(float(a), float(b), rel_tol=rtol, abs_tol=atol)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise AssertionError(f"invalid JSONL {path.name}:{line_number}: {exc}") from exc
    return records


def replay_farkas(certificate: dict[str, Any]) -> tuple[float, float, str]:
    require(certificate.get("pass") is True, "Farkas certificate not marked pass")
    require(certificate.get("type") == "SINGLE_ROW_BOX_FARKAS", "unexpected Farkas type")
    coeff = np.asarray(certificate["violated_row_coefficients"], dtype=float)
    rhs = float(certificate["violated_row_rhs"])
    require(coeff.shape == (6,), "Farkas row is not six-dimensional")
    row_minimum = float(np.sum(np.minimum(coeff, 0.0)))
    require(close(row_minimum, certificate["violated_row_box_minimum"], atol=2.0e-13), "Farkas row minimum mismatch")
    gap = row_minimum - rhs
    require(gap > 1.0e-10, f"Farkas box gap did not close: {gap}")

    terms = certificate["active_terms"]
    require(len(terms) == int(certificate["active_term_count"]), "Farkas term count mismatch")
    require(all(float(term["weight"]) >= 0.0 for term in terms), "negative Farkas weight")
    require(close(sum(float(term["weight"]) for term in terms), 1.0, atol=3.0e-15), "Farkas weights not normalized")
    dual_column = np.zeros(6, dtype=float)
    dual_rhs = 0.0
    for term in terms:
        column = np.asarray(term["column"], dtype=float)
        require(column.shape == (6,), "Farkas term column shape")
        weight = float(term["weight"])
        dual_column += weight * column
        dual_rhs += weight * float(term["rhs"])
    dual_residual = float(np.max(np.abs(dual_column)))
    require(dual_residual <= 2.0e-12, f"Farkas dual column residual {dual_residual}")
    require(dual_rhs < 0.0, "Farkas RHS is not strictly negative")
    require(close(dual_rhs, certificate["h_dot_y"], rtol=2.0e-12, atol=2.0e-15), "Farkas h.y mismatch")
    require(close(dual_residual, certificate["dual_residual_inf"], atol=2.0e-12), "Farkas residual field mismatch")
    physical_terms = [term for term in terms if term.get("constraint") not in {"LOWER_BOUND", "UPPER_BOUND"}]
    require(len(physical_terms) == 1, "single-row Farkas does not contain exactly one physical row")
    return gap, dual_rhs, str(physical_terms[0]["constraint"])


def replay_kkt(certificate: dict[str, Any]) -> tuple[float, float, float]:
    require(certificate.get("pass") is True, "KKT certificate not marked pass")
    require(certificate.get("method") == "ACTIVE_SET_NNLS", "unexpected KKT method")
    c = np.asarray(certificate["objective_vector"], dtype=float)
    x = np.asarray(certificate["primal_variables"], dtype=float)
    require(c.shape == (6,) and x.shape == (6,), "KKT primal/objective shape")
    require(np.min(x) >= -2.0e-14 and np.max(x) <= 1.0 + 2.0e-14, "KKT primal outside box")
    terms = certificate["dual_terms"]
    require(len(terms) == int(certificate["nonzero_dual_term_count"]), "KKT dual term count mismatch")
    stationarity = c.copy()
    dual_objective = 0.0
    max_comp = 0.0
    for term in terms:
        weight = float(term["weight"])
        column = np.asarray(term["column"], dtype=float)
        rhs = float(term["rhs"])
        require(weight >= 0.0 and column.shape == (6,), "invalid KKT dual term")
        slack = rhs - float(np.dot(column, x))
        require(slack >= -2.0e-10, f"negative active primal slack {slack}")
        require(close(slack, term["primal_slack"], rtol=2.0e-10, atol=2.0e-12), "KKT term slack mismatch")
        stationarity += weight * column
        dual_objective -= weight * rhs
        max_comp = max(max_comp, abs(weight * slack))
    stationarity_scale = max(1.0, float(np.max(np.abs(c))) + sum(float(term["weight"]) * float(np.max(np.abs(term["column"]))) for term in terms))
    relative_stationarity = float(np.max(np.abs(stationarity))) / stationarity_scale
    primal_objective = float(np.dot(c, x))
    relative_gap = abs(primal_objective - dual_objective) / max(1.0, abs(primal_objective), abs(dual_objective))
    require(relative_stationarity <= REL_TOL, f"KKT stationarity replay {relative_stationarity}")
    require(relative_gap <= REL_TOL, f"KKT duality-gap replay {relative_gap}")
    require(max_comp <= REL_TOL, f"KKT complementarity replay {max_comp}")
    require(close(primal_objective, certificate["primal_objective"], rtol=2.0e-12), "KKT primal objective mismatch")
    require(close(dual_objective, certificate["dual_objective"], rtol=2.0e-10, atol=2.0e-12), "KKT dual objective mismatch")
    require(close(relative_gap, certificate["relative_duality_gap"], rtol=2.0e-7, atol=2.0e-14), "KKT relative gap mismatch")
    require(max_comp <= float(certificate["max_complementarity_residual"]) + 2.0e-12, "KKT complementarity field mismatch")
    return relative_stationarity, relative_gap, max_comp


def main() -> None:
    summary = json.loads((DATA / "summary.json").read_text())
    results = pd.read_csv(DATA / "macro_case_results.csv")
    rate_lock = pd.read_csv(DATA / "rate_interval_lock.csv")
    selected = pd.read_csv(DATA / "selected_rate_solutions.csv")
    refinement = pd.read_csv(DATA / "refinement_audit.csv")
    violations = pd.read_csv(DATA / "violated_cases.csv")
    zeros = pd.read_csv(DATA / "exact_zero_audit.csv")
    dual_records = load_jsonl(DATA / "dual_farkas_kkt_certificates.jsonl")
    trajectory_records = load_jsonl(DATA / "trajectory_certificates.jsonl")

    require(len(results) == 540, f"macro result count {len(results)}")
    require(results.duplicated(KEY).sum() == 0, "duplicate macro result key")
    require(set(results["shape_lane"]) == set(LANES), "shape-lane registry mismatch")
    require((results.groupby("shape_lane").size() == 180).all(), "shape-lane case count")
    require((results.groupby(["interval_index", "substep"]).size() == 54).all(), "substep case count")

    require(len(rate_lock) == 3240, f"rate-lock row count {len(rate_lock)}")
    require(rate_lock.duplicated(RATE_KEY).sum() == 0, "duplicate rate-lock key")
    require(set(rate_lock["family"]) == set(FAMILIES), "rate family registry mismatch")
    require(set(rate_lock["status"]) == {"IDENTIFIED_INTERVAL"}, "unidentified rate interval")
    require(rate_lock["usable"].astype(bool).all(), "unusable locked rate interval")
    require(np.isfinite(rate_lock[["k_min_Myr_inv", "k_max_Myr_inv"]].to_numpy(float)).all(), "nonfinite rate box")
    require((rate_lock["k_min_Myr_inv"] > 0.0).all(), "nonpositive rate lower bound")
    require((rate_lock["k_max_Myr_inv"] >= rate_lock["k_min_Myr_inv"]).all(), "reversed rate box")
    require(not any("node_rate" in column.lower() for column in rate_lock.columns), "node-rate field in lock")

    require(len(selected) == 3240, f"selected-rate row count {len(selected)}")
    require(selected.duplicated(RATE_KEY).sum() == 0, "duplicate selected-rate key")
    merged_rates = selected.merge(
        rate_lock[RATE_KEY + ["k_min_Myr_inv", "k_max_Myr_inv"]],
        on=RATE_KEY,
        suffixes=("_selected", "_locked"),
        validate="one_to_one",
    )
    require(np.allclose(merged_rates["k_min_Myr_inv_selected"], merged_rates["k_min_Myr_inv_locked"], rtol=0.0, atol=2.0e-15), "selected lower rate box changed")
    require(np.allclose(merged_rates["k_max_Myr_inv_selected"], merged_rates["k_max_Myr_inv_locked"], rtol=0.0, atol=2.0e-15), "selected upper rate box changed")
    active_rates = merged_rates[merged_rates["selected_model"].ne("NONE")]
    inactive_rates = merged_rates[merged_rates["selected_model"].eq("NONE")]
    require(active_rates["selected_k_Myr_inv"].notna().all(), "missing selected physical rate")
    require(inactive_rates["selected_k_Myr_inv"].isna().all(), "rate selected for infeasible case")
    rate_eps = 2.0e-12 * np.maximum(1.0, active_rates["k_max_Myr_inv_locked"].abs())
    require((active_rates["selected_k_Myr_inv"] >= active_rates["k_min_Myr_inv_locked"] - rate_eps).all(), "selected rate below lock")
    require((active_rates["selected_k_Myr_inv"] <= active_rates["k_max_Myr_inv_locked"] + rate_eps).all(), "selected rate above lock")
    two_rates = active_rates[active_rates["selected_model"].eq("TWO_MODE")]
    require(two_rates["two_mode_weight_slow"].between(-2.0e-13, 1.0 + 2.0e-13).all(), "two-mode weight outside convex hull")

    result_index = {tuple(getattr(row, field) for field in KEY): row for row in results.itertuples(index=False)}
    require(len(dual_records) == 540 and len(trajectory_records) == 540, "JSONL case count")
    farkas_gaps: list[float] = []
    farkas_hdot: list[float] = []
    farkas_constraints: Counter[str] = Counter()
    kkt_stationarity: list[float] = []
    kkt_gaps: list[float] = []
    kkt_comp: list[float] = []
    json_keys: set[tuple[Any, ...]] = set()
    for record in dual_records:
        key = tuple(record[field] for field in KEY)
        require(key not in json_keys, "duplicate dual JSONL key")
        json_keys.add(key)
        row = result_index[key]
        lp = record["lp"]
        require(bool(lp["pass"]) == bool(row.lp_pass), "LP pass mismatch between CSV and JSONL")
        require(int(lp.get("node_rate_count", -1)) == 0, "node-rate fitting recorded")
        if lp["pass"]:
            require(lp["primal_gate_pass"] is True and lp["kkt_gate_pass"] is True, "LP/KKT gate not closed")
            require(float(lp["minimum_normalized_primal_slack"]) >= -REL_TOL, "primal slack gate")
            stat, gap, comp = replay_kkt(lp["active_set_dual_certificate"])
            kkt_stationarity.append(stat); kkt_gaps.append(gap); kkt_comp.append(comp)
        else:
            gap, hdot, constraint = replay_farkas(lp["farkas_certificate"])
            farkas_gaps.append(gap); farkas_hdot.append(hdot); farkas_constraints[constraint] += 1
    require(len(json_keys) == 540, "dual JSONL key coverage")
    require(len(farkas_gaps) == int((~results["lp_pass"].astype(bool)).sum()), "Farkas count mismatch")
    require(len(kkt_stationarity) == int(results["lp_pass"].astype(bool).sum()), "KKT count mismatch")

    trajectory_keys: set[tuple[Any, ...]] = set()
    cert_statuses: Counter[str] = Counter()
    interval_evaluations: list[int] = []
    maximum_depths: list[int] = []
    for record in trajectory_records:
        key = tuple(record[field] for field in KEY)
        require(key not in trajectory_keys, "duplicate trajectory JSONL key")
        trajectory_keys.add(key)
        row = result_index[key]
        require(str(record["selected_model"]) == str(row.selected_model), "trajectory model mismatch")
        if not bool(row.lp_pass):
            require(record["one_mode"] is None, "one-mode run on infeasible equilibrium")
            require(record["two_mode"].get("status") == "SKIPPED_EQUIVALENT_ATTENUATION_BOX_THEOREM", "missing fail-closed trajectory skip")
            continue
        for model_name in ("one_mode", "two_mode"):
            model = record.get(model_name)
            if not isinstance(model, dict) or "neutral" not in model:
                continue
            for cone_name in ("neutral", "cycling"):
                cert = model[cone_name]
                require(cert["certification_method"] == "CENTERED_TAYLOR_LAGRANGE_DYADIC", "trajectory method registry")
                require(int(cert["taylor_order"]) == 4, "Taylor order changed")
                require(int(cert["maximum_interval_evaluations"]) == 200000, "trajectory work lock changed")
                require(int(cert["maximum_depth_used"]) <= 24, "trajectory depth exceeded")
                require(int(cert["interval_evaluation_count"]) <= 200000, "trajectory work exceeded")
                if cert["pass"]:
                    require(cert["status"] == "CERTIFIED", "passing trajectory not certified")
                    require(float(cert["minimum_sampled_slack"]) >= -float(cert["absolute_tolerance"]) - 2.0e-12 * max(1.0, float(cert["slack_scale"])), "certified trajectory contains negative sampled slack")
                else:
                    require(cert["status"] in {"REAL_NEGATIVE_SLACK", "CERTIFICATION_WORK_LIMIT", "CERTIFICATION_AMBIGUOUS_DEPTH_LIMIT"}, "unknown trajectory failure")
                cert_statuses[str(cert["status"])] += 1
                interval_evaluations.append(int(cert["interval_evaluation_count"]))
                maximum_depths.append(int(cert["maximum_depth_used"]))
        if str(row.selected_model) == "ONE_MODE":
            require(record["one_mode"]["pass"] is True and record["two_mode"] is None, "one-mode selection inconsistency")
        elif str(row.selected_model) == "TWO_MODE":
            require(record["one_mode"]["pass"] is False and record["two_mode"]["pass"] is True, "two-mode selection inconsistency")
        else:
            raise AssertionError("feasible LP without selected trajectory model")
    require(len(trajectory_keys) == 540, "trajectory JSONL key coverage")

    require(len(refinement) == int((results["selected_model"] != "NONE").sum()) * 3, "refinement row count")
    require(set(refinement["refinement"]) == {2, 4, 8}, "refinement registry")
    require(refinement.duplicated(KEY + ["refinement"]).sum() == 0, "duplicate refinement key")
    require((refinement.groupby(KEY).size() == 3).all(), "incomplete refinement triplet")
    require((refinement[refinement["refinement"].isin([4, 8])]["cone_pass"].astype(bool)).all(), "fine refinement cone failure")
    coarse_cone_failures = int((~refinement[refinement["refinement"].eq(2)]["cone_pass"].astype(bool)).sum())

    require(len(zeros) == 540 and zeros["exact_zero_pass"].astype(bool).all(), "structural exact-zero audit")
    for column in ("effective_HI_G2b", "effective_HI_G3", "primary_HeII_G3"):
        require((zeros[column].astype(float) == 0.0).all(), f"nonzero structural lock {column}")
    require(results["H_nuclei_identity_residual"].abs().max() == 0.0, "H nuclei identity")
    require(results["He_nuclei_identity_residual"].abs().max() == 0.0, "He nuclei identity")
    require(results["node_rate_count"].max() == 0, "node-rate count nonzero")
    require(results["max_current_Gamma_relative_residual"].max() <= 1.0e-12, "current-Gamma gate")

    macro_pass_count = int(results["overall_pass"].astype(bool).sum())
    whole_lane_pass = {lane: bool(results[results["shape_lane"].eq(lane)]["overall_pass"].astype(bool).all()) for lane in LANES}
    selected_counts = results["selected_model"].value_counts().to_dict()
    require(summary["macro_case_count"] == 540, "summary macro count")
    require(summary["macro_case_pass_count"] == macro_pass_count, "summary macro pass count")
    require(summary["all_lane_pass_count"] == sum(whole_lane_pass.values()), "summary whole-lane pass count")
    require(summary["whole_lane_pass"] == whole_lane_pass, "summary whole-lane map")
    require(summary["all_lanes_pass"] is all(whole_lane_pass.values()), "summary all-lane gate")
    require(summary["lp_feasible"] == int(results["lp_pass"].astype(bool).sum()), "summary LP count")
    require(summary["equilibrium_infeasible"] == len(farkas_gaps), "summary infeasible count")
    require(summary["one_mode_selected"] == int(selected_counts.get("ONE_MODE", 0)), "summary one-mode count")
    require(summary["two_mode_selected"] == int(selected_counts.get("TWO_MODE", 0)), "summary two-mode count")
    require(summary["refinement_pass"] == int(results["refinement_pass"].astype(bool).sum()), "summary refinement count")
    require(summary["refinement_failed_after_trajectory"] == coarse_cone_failures, "summary refinement-failure count")
    require(summary["R2C_R2_authorized"] is False, "R2C-R2 incorrectly authorized")
    require(summary["B2C2B_authorized"] is False, "B2C2B incorrectly authorized")
    require(summary["production_node_chemistry_authorized"] is False, "production chemistry incorrectly authorized")
    require(summary["node_rate_fitting_used"] is False and summary["clipping_used"] is False, "forbidden fallback recorded")
    require(len(violations) == int((~results["overall_pass"].astype(bool)).sum()), "violation ledger count")

    payload = {
        "status": "PASS",
        "macro_case_count": 540,
        "macro_case_pass_count": macro_pass_count,
        "whole_lane_pass": whole_lane_pass,
        "lp_feasible_count": len(kkt_stationarity),
        "equilibrium_infeasible_count": len(farkas_gaps),
        "Farkas_constraint_counts": dict(sorted(farkas_constraints.items())),
        "minimum_Farkas_box_gap": min(farkas_gaps),
        "maximum_Farkas_h_dot_y": max(farkas_hdot),
        "maximum_replayed_KKT_relative_stationarity": max(kkt_stationarity),
        "maximum_replayed_KKT_relative_duality_gap": max(kkt_gaps),
        "maximum_replayed_KKT_complementarity": max(kkt_comp),
        "selected_model_counts": {str(k): int(v) for k, v in selected_counts.items()},
        "trajectory_certificate_status_counts": dict(sorted(cert_statuses.items())),
        "maximum_trajectory_interval_evaluations": max(interval_evaluations),
        "maximum_trajectory_depth": max(maximum_depths),
        "refinement_coarse_cone_failures": coarse_cone_failures,
        "max_endpoint_relative_residual": float(results["max_endpoint_relative_residual"].max()),
        "max_current_Gamma_relative_residual": float(results["max_current_Gamma_relative_residual"].max()),
        "exact_zero_rows": len(zeros),
        "rate_unit": "Myr^-1",
        "time_unit": "Myr",
        "attenuation_coordinates_dimensionless": True,
        "node_rate_fitting_used": False,
        "clipping_used": False,
    }
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
