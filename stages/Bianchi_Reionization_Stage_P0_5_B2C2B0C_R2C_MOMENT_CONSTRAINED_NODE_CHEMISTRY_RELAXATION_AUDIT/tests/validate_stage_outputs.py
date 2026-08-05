#!/usr/bin/env python3
"""Independent table/ledger validator for the durable R2C result."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

STAGE = Path(__file__).resolve().parents[1]
DATA = STAGE / "data"
RECEIPTS = STAGE / "receipts"
OUT = RECEIPTS / "independent_stage_validation.json"
KEY = ["shape_lane", "interval_index", "substep", "tau_Myr"]
MACRO_KEY = KEY + ["macro_index"]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    summary = json.loads((DATA / "summary.json").read_text())
    eq = pd.read_csv(DATA / "equilibrium_feasibility.csv")
    macro = pd.read_csv(DATA / "macro_equilibrium_certificates.csv")
    violations = pd.read_csv(DATA / "violated_constraints.csv")
    substeps = pd.read_csv(DATA / "relaxation_substep_ledger.csv")
    convergence = pd.read_csv(DATA / "temporal_convergence.csv")
    zeros = pd.read_csv(DATA / "exact_zero_audit.csv", dtype={"value": str})

    require(len(eq) == 90, f"equilibrium case count {len(eq)}")
    require(len(macro) == 1620, f"macro certificate count {len(macro)}")
    require(len(zeros) == 450, f"exact-zero count {len(zeros)}")
    require(eq.duplicated(KEY).sum() == 0, "duplicate equilibrium case key")
    require(macro.duplicated(MACRO_KEY).sum() == 0, "duplicate macro key")
    require((macro.groupby(KEY).size() == 18).all(), "not every case has 18 macros")

    macro_case = macro.groupby(KEY, sort=False)["equilibrium_pass"].all().rename("macro_all")
    merged = eq.merge(macro_case.reset_index(), on=KEY, how="left", validate="one_to_one")
    require(
        np.array_equal(
            merged["node_equilibrium_all_macros_feasible"].to_numpy(bool),
            merged["macro_all"].to_numpy(bool),
        ),
        "case pass is inconsistent with macro certificates",
    )

    expected_violation_rows = 0
    violation_multiset: dict[tuple, int] = {}
    for row in macro.itertuples(index=False):
        values = [] if bool(row.equilibrium_pass) else str(row.violated_constraints).split(";")
        expected_violation_rows += len(values)
        for constraint in values:
            key = (row.shape_lane, int(row.interval_index), int(row.substep), int(row.macro_index), float(row.tau_Myr), constraint)
            violation_multiset[key] = violation_multiset.get(key, 0) + 1
    observed_multiset: dict[tuple, int] = {}
    for row in violations.itertuples(index=False):
        require(not bool(row.clipping_used), "clipping recorded in violation ledger")
        key = (row.shape_lane, int(row.interval_index), int(row.substep), int(row.macro_index), float(row.tau_Myr), row.constraint)
        observed_multiset[key] = observed_multiset.get(key, 0) + 1
    require(expected_violation_rows == len(violations), "violation row count mismatch")
    require(violation_multiset == observed_multiset, "violation multiset mismatch")

    eq_cv = eq.merge(convergence[KEY + ["convergence_pass"]], on=KEY, validate="one_to_one")
    require(
        np.array_equal(
            eq_cv["node_equilibrium_all_macros_feasible"].to_numpy(bool),
            eq_cv["convergence_pass"].to_numpy(bool),
        ),
        "a feasible case failed refinement or an infeasible case was marked converged",
    )

    passed = substeps[substeps["status"].eq("PASS")]
    skipped = substeps[substeps["status"].eq("SKIPPED_FAIL_CLOSED_EQUILIBRIUM_INFEASIBLE")]
    require(len(passed) == 4802, f"successful substep count {len(passed)}")
    require(len(skipped) == 6538, f"fail-closed skip count {len(skipped)}")
    require(set(substeps["status"].unique()) == {"PASS", "SKIPPED_FAIL_CLOSED_EQUILIBRIUM_INFEASIBLE"}, "unexpected substep status")
    require(passed["projection_pass"].astype(bool).all(), "successful substep has failed projection")
    require(passed["projection_max_column_relative_residual"].max() <= 1.0e-11, "column residual gate")
    require(passed["projection_max_capacity_relative_violation"].max() <= 1.0e-11, "capacity residual gate")
    require(passed["projection_max_stationarity_residual"].max() <= 1.0e-11, "KKT stationarity gate")
    require(passed["projection_max_complementarity_residual"].max() <= 1.0e-11, "KKT complementarity gate")
    require(passed["current_Gamma_residual_max"].max() <= 1.0e-12, "current-Gamma gate")
    require(passed["H_nuclei_identity_residual"].abs().max() == 0.0, "H nuclei identity")
    require(passed["He_nuclei_identity_residual"].abs().max() == 0.0, "He nuclei identity")
    require((passed["HI_nuclei_total"] >= 0.0).all(), "negative HI stock in successful step")
    require((passed["HII_nuclei_total"] >= 0.0).all(), "negative HII stock in successful step")

    require(zeros["exact_zero"].astype(bool).all(), "exact-zero flag failure")
    require((zeros["value"] == "0").all(), "exact-zero value is not literal zero")
    require(
        set(zeros["quantity"]) == {
            "kappa_sink_G2b_effective_HI",
            "kappa_sink_G3_effective_HI",
            "J_sink_G2b_effective_HI",
            "J_sink_G3_effective_HI",
            "HeII_G3_primary_absorption",
        },
        "exact-zero quantity registry mismatch",
    )

    initial_receipts = sorted(RECEIPTS.glob("initial_current_projection_*.json"))
    require(len(initial_receipts) == 3, "missing initial projection receipt")
    initial_digest = hashlib.sha256()
    initial_counts = {}
    for path in initial_receipts:
        payload = json.loads(path.read_text())
        require(payload["pass"] is True and payload["clipping_used"] is False, f"bad initial projection {path.name}")
        require(payload["block_count"] == 18, f"initial block count {path.name}")
        require(payload["preprojection_negative_row_count"] > 0, f"root-cause evidence absent {path.name}")
        require(payload["postprojection_negative_row_count"] == 0, f"initial projection did not close cone {path.name}")
        require(payload["max_group_total_relative_residual"] <= 3.0e-14, f"initial group total residual {path.name}")
        require(payload["maximum_block_capacity_relative_violation"] <= 1.0e-11, f"initial capacity residual {path.name}")
        initial_counts[path.stem] = payload["preprojection_negative_row_count"]
        initial_digest.update(path.read_bytes())

    recomputed_by_tau = {}
    for tau in (10.0, 100.0, 300.0):
        e = eq[np.isclose(eq["tau_Myr"], tau)]
        c = convergence[np.isclose(convergence["tau_Myr"], tau)]
        recomputed_by_tau[str(int(tau))] = {
            "case_count": int(len(e)),
            "equilibrium_feasible_case_count": int(e["node_equilibrium_all_macros_feasible"].sum()),
            "convergent_case_count": int(c["convergence_pass"].sum()),
            "all_equilibrium_feasible": bool(e["node_equilibrium_all_macros_feasible"].all()),
            "all_convergent": bool(c["convergence_pass"].all()),
        }
    require(summary["by_tau"] == recomputed_by_tau, "summary by_tau mismatch")
    require(summary["production_node_chemistry_authorized"] is False, "production incorrectly authorized")
    require(summary["B2C2B_authorized"] is False, "B2C2B incorrectly authorized")
    require(summary["tau10_all_case_existence_witness"] is False, "tau10 incorrectly promoted")
    require(summary["verdict"].startswith("DURABLE_FAIL_CLOSED"), "result is not fail-closed")
    require(summary["violated_constraint_row_count"] == len(violations), "summary violation count")
    require(summary["successful_relaxation_substeps"] == len(passed), "summary successful substeps")
    require(summary["maximum_projection_capacity_relative_violation"] <= 1.0e-11, "summary capacity gate")

    result = {
        "status": "PASS",
        "case_count": len(eq),
        "macro_certificate_count": len(macro),
        "violation_row_count": len(violations),
        "successful_substep_count": len(passed),
        "fail_closed_skip_count": len(skipped),
        "equilibrium_convergence_mismatch_count": 0,
        "by_tau": recomputed_by_tau,
        "max_projection_column_relative_residual": float(passed["projection_max_column_relative_residual"].max()),
        "max_projection_capacity_relative_violation": float(passed["projection_max_capacity_relative_violation"].max()),
        "max_KKT_stationarity_residual": float(passed["projection_max_stationarity_residual"].max()),
        "max_KKT_complementarity_residual": float(passed["projection_max_complementarity_residual"].max()),
        "max_current_Gamma_residual": float(passed["current_Gamma_residual_max"].max()),
        "initial_preprojection_negative_rows": initial_counts,
        "initial_projection_receipts_sha256": initial_digest.hexdigest(),
        "clipping_used": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
