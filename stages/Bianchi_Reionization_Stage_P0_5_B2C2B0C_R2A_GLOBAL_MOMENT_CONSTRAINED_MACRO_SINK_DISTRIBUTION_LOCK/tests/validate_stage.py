#!/usr/bin/env python3
"""Independent fail-closed validator for the R2A durable stage."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent
REPO = STAGE.parents[1]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


# Frozen pre-calculation scaffold consistency.
pre = json.loads((STAGE / "state" / "PRECALC_MANIFEST.json").read_text())
checksum_lines = {
    line.split(maxsplit=1)[1]: line.split(maxsplit=1)[0]
    for line in (STAGE / "state" / "PRECALC_SHA256SUMS").read_text().splitlines()
    if line.strip()
}
require(len(pre["files"]) == pre["file_count"] == len(checksum_lines), "precalc inventory count mismatch")
for item in pre["files"]:
    require(checksum_lines[item["path"]] == item["sha256"], f"precalc checksum ledger mismatch: {item['path']}")
snapshot_root = STAGE / "state" / "PRECALC_SNAPSHOT"
for item in pre["files"]:
    snapshot = snapshot_root / item["path"]
    require(snapshot.exists(), f"missing precalc snapshot: {item['path']}")
    require(sha(snapshot) == item["sha256"], f"precalc snapshot hash mismatch: {item['path']}")
# The calculation input lock itself remains immutable after initialization.
input_lock_pre = next(x["sha256"] for x in pre["files"] if x["path"] == "INPUT_LOCK.json")
require(sha(STAGE / "INPUT_LOCK.json") == input_lock_pre, "live INPUT_LOCK changed after calculation start")

# External recombination firewall.
rec_lock = json.loads((REPO / "external" / "rec_bianchi.lock.json").read_text())
require(rec_lock["status"] in {"REMOTE_UNAVAILABLE", "LOCKED"}, "unexpected rec_bianchi lock status")
require(rec_lock.get("head_sha") is None or len(rec_lock["head_sha"]) == 40, "invalid rec_bianchi SHA")
input_lock = json.loads((STAGE / "INPUT_LOCK.json").read_text())
require(input_lock["external_recombination_lock"]["surrogate_forbidden"] is True, "surrogate firewall missing")

# Core outputs.
results = json.loads((STAGE / "results.json").read_text())
summary = pd.read_csv(STAGE / "data" / "projection_gate_summary.csv")
macro = pd.read_csv(STAGE / "data" / "macro_projection.csv")
global_lock = pd.read_csv(STAGE / "data" / "global_moment_lock.csv")
zeros = pd.read_csv(STAGE / "data" / "exact_zero_audit.csv")
relax = pd.read_csv(STAGE / "data" / "finite_relaxation_feasibility.csv")
require(len(global_lock) == 10, "global substep count")
require(len(summary) == 30, "projection case count")
require(len(macro) == 540, "macro row count")
require(summary["feasible"].all() and summary["KKT_gate"].all(), "core feasibility/KKT failure")
require(summary["identity_projection"].all(), "locked inputs should be identity I-projections")
require(float(summary["generalized_KL_total"].max()) == 0.0, "KL optimum not exact zero")
require(float(summary[["TV_mass", "TV_G1", "TV_G2a"]].to_numpy().max()) == 0.0, "operator TV distortion not zero")
require(float(summary["mass_sum_relative_residual"].max()) <= 5e-13, "mass moment")
require(float(summary["kappa_sum_relative_residual_max"].max()) <= 5e-13, "opacity moment")
require(float(summary["J_sum_relative_residual_max"].max()) <= 5e-13, "J moment")
require(float(summary["current_Gamma_relation_relative_residual_max"].max()) <= 5e-13, "current Gamma")
require(float(summary["volume_filling_max"].max()) <= 1.0, "volume cap")
require(float(summary["mass_cap_slack_min_fraction_cosmic_H"].min()) >= 0.0, "mass cap")
require(float(summary["cycling_slack_min_fraction_of_global_J"].min()) >= 0.0, "cycling capacity")
require((macro["geometry_mass_inversion_used"] == False).all(), "Jeans opacity mass inversion used")  # noqa: E712
require((macro["volume_filling_macro"] <= 1.0 + 1e-13).all(), "macro volume")
require((macro["mass_cap_slack_cMpc3"] >= -1e-9).all(), "macro mass cap")
require((macro["cycling_capacity_slack_s_inv_cMpc3"] >= -1e35).all(), "macro cycling cap")
# Scale-aware cycling check.
for _, frame in macro.groupby(["shape_lane", "interval_index", "substep"]):
    scale = max(abs(frame["J_sink_macro_total_s_inv_cMpc3"]).sum(), 1.0)
    require(frame["cycling_capacity_slack_s_inv_cMpc3"].min() / scale >= -5e-13, "scaled cycling cap")

# Exact-zero lock must be inherited from canonical inputs, not only assigned in output.
require(len(zeros) == 90, "exact zero row count")
require(zeros["source_lock_exact_zero"].all(), "canonical source exact-zero lock failed")
require(zeros["exact_zero"].all(), "output exact-zero failed")
require((zeros["sum"] == 0.0).all() and (zeros["source_lock_value"] == 0.0).all(), "nonzero structural channel")

# Finite-relaxation auditor is separate. The 10 Myr lane must be feasible in all cases;
# slower lanes remain explicit nonblocking sensitivity failures rather than being clipped.
tau10 = relax[np.isclose(relax["tau_Myr"], 10.0)]
require(len(tau10) == 30, "tau=10 auditor count")
require(tau10["absolute_state_feasible"].all() and tau10["shape_only_feasible"].all(), "tau=10 relaxation lane")
require((relax["blocking_for_R2B_core_gate"] == False).all(), "relaxation auditor unexpectedly blocking")  # noqa: E712
require((~relax[np.isclose(relax["tau_Myr"], 300.0)]["absolute_state_feasible"]).any(), "tau=300 sensitivity unexpectedly all pass")

# Exact photon-ledger bytes and R1 fail-closed inheritance.
receipt = json.loads((STAGE / "receipts" / "canonical_runtime_input_receipt.json").read_text())
require(sha(STAGE / "data" / "inherited_exact_photon_ledger.csv") == receipt["inherited_exact_photon_ledger_sha256"], "photon ledger byte hash")
r1 = json.loads((STAGE / "receipts" / "R1_fail_closed_inheritance.json").read_text())
require(r1["diagnostic_node_history_promoted"] is False, "R1 diagnostic promoted")
require(r1["independent_quasistatic_macro_cloud_abundance_used"] is False, "forbidden R1 closure reused")

# No forbidden new science products.
for path in (STAGE / "data").iterdir():
    lower = path.name.lower()
    require("node_chemistry_history" not in lower, "node chemistry started")
    require("unresolved_subtraction" not in lower, "unresolved subtraction started")
    require("front_q" not in lower and "source_fesc" not in lower, "forbidden source/front work")

# Operator unit tests: identity, mass-cap Farkas, and cycling Farkas.
module_path = STAGE / "src" / "global_moment_constrained_macro_sink.py"
spec = importlib.util.spec_from_file_location("r2a_operator", module_path)
operator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = operator
spec.loader.exec_module(operator)
p1 = np.array([0.3, 0.7])
p2 = np.array([0.5, 0.5])
q = {"G1": 0.6, "G2a": 0.4}
pm = q["G1"] * p1 + q["G2a"] * p2
identity, audit = operator.project_case(pm, {"G1": p1, "G2a": p2}, np.array([1.0, 1.0]), 1.2, q)
require(audit["feasible"] and identity.identity_projection and identity.objective == 0.0, "identity projection unit test")
cap_fail = operator.numerical_projection(pm, {"G1": p1, "G2a": p2}, np.array([0.2, 0.2]), 1.2, q)
require(not cap_fail.feasible and any(c["type"] == "FARKAS_MASS_OR_VOLUME_CAP_SUM" for c in cap_fail.certificates), "mass Farkas unit test")
rho_fail = operator.numerical_projection(pm, {"G1": p1, "G2a": p2}, np.array([1.0, 1.0]), 0.8, q)
require(not rho_fail.feasible and any(c["type"] == "FARKAS_CYCLING_CAPACITY_SUM" for c in rho_fail.certificates), "cycling Farkas unit test")

symbolic = json.loads((STAGE / "data" / "symbolic_validation_results.json").read_text())
require(symbolic["overall_pass"] is True, "exact symbolic fallback failed")
require(results["R2B_authorized"] is True and results["B2C2B_authorized"] is False, "authorization state")

report = {
    "stage": results["stage"],
    "status": "PASS",
    "core_cases": len(summary),
    "macro_rows": len(macro),
    "tau10_all_feasible": True,
    "symbolic_fallback": "PASS",
    "operator_unit_tests": "PASS",
    "R2B_authorized": True,
    "B2C2B_authorized": False,
}
(STAGE / "receipts" / "independent_validation.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
print(json.dumps(report, indent=2, sort_keys=True))
