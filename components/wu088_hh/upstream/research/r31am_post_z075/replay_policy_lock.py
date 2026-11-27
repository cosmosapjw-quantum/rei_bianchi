"""Read-only R31AM policy replay; no producer or direct-output access."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import numpy as np


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open("x") as f:
        f.write(json.dumps(value, indent=2, allow_nan=False) + "\n")


def array_sha(arrays):
    h = hashlib.sha256()
    for a in arrays:
        h.update(np.asarray(a, dtype="<c16", order="C").tobytes(order="C"))
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True, type=Path)
    a = ap.parse_args()
    repo = Path(__file__).resolve().parents[2]
    out = a.outdir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    al = repo / "research/r31al_z075_gate/ncp_followup_20260930"
    ak = repo / "research/r31ak_eight_node/ncp_followup_20260930"
    expected = {
        al / "AUTHORIZATION_SCOPE_CANONICAL.json": "2f22f11f279b8d7f98efb2a4bff1fbfb79145f7f5010ce5081ca6ebfcc147357",
        ak / "NEXT_VALIDATION_PREREGISTRATION.json": "44b2273afeddb4a6befa73ce485ae84d8f8777a92ac75c4de2fd90d0fea74b81",
        al / "SECONDARY_REFINEMENT_PREREGISTRATION.json": "956bdbb6a4138f7f1117cbf98b47ce80d8c1cb76fcbf3401a76105cb4873612a",
        al / "Z075_REFINEMENT_PRE_OUTPUT_LOCK.json": "93f895b7436ca4e4f82fb8a28d66acb2bd745fc39067571297292c62445b87c1",
    }
    lock = json.loads((al / "Z075_REFINEMENT_PRE_OUTPUT_LOCK.json").read_text())
    for record in lock["locked_files"].values():
        expected[repo / record["path"]] = record["sha256"]
    verified = []
    for path, digest in expected.items():
        actual = sha(path)
        if actual != digest:
            raise ValueError("parent identity drift: " + str(path))
        verified.append({"path": str(path.relative_to(repo)), "sha256": actual, "bytes": path.stat().st_size})
    scope = json.loads((al / "AUTHORIZATION_SCOPE.json").read_text())
    canonical = json.dumps(scope, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")
    if canonical != (al / "AUTHORIZATION_SCOPE_CANONICAL.json").read_bytes():
        raise ValueError("scope canonical representation drift")
    if lock["execution_authorized"] or lock["direct_output_accessed"]:
        raise ValueError("parent pre-output status drift")
    arrays_verified = {}
    with np.load(ak / "FROZEN_HOLDOUT_PREDICTIONS.npz", allow_pickle=False) as f:
        for name, target in (("R31AK", "66ff922f687a796417e23147e5720af9a467ef7d988b490a2709e0a2967c4010"),
                             ("R31Z", "4f7738094bf83c8ad6f01febabdc11f899465957a38a7e65632d63389a68d41c")):
            actual = array_sha([f[f"z0p75_{name}_{k}"] for k in ("O", "dotO", "Dcol", "Drow", "K")])
            if actual != target:
                raise ValueError(name + " selected prediction drift")
            arrays_verified[name] = actual
    with np.load(al / "Z075_COARSE_PREDICTION.npz", allow_pickle=False) as f:
        actual = array_sha([f["z0p75_R31AD_" + k] for k in ("O", "dotO", "Dcol", "Drow", "K")])
    if actual != "cabb469bbfd5a2c7724850d60c6bf065afa538fc5ff277e04cda30a380927029":
        raise ValueError("R31AD selected prediction drift")
    arrays_verified["R31AD"] = actual
    parent_commit = "799797778d01edf74e73c1faf4dcf15bd41e3df2"
    altered = subprocess.check_output(["git", "diff", "--name-only", parent_commit, "HEAD", "--",
                                       "research/r31al_z075_gate", "research/r31ak_eight_node", "research/r31ad_five_node",
                                       "research/r31z_source_bound", "native/reference", "vendor/orchestration"], cwd=repo, text=True)
    if altered.strip():
        raise ValueError("parent source changed: " + altered)
    pins = json.loads((repo / "research/r31am_post_z075/SOURCE_PINS.json").read_text())
    return_path = al / "RETURN.json"
    git_blob = subprocess.check_output(["git", "hash-object", str(return_path)], cwd=repo, text=True).strip()
    if pins["parent_return_sha256"] != git_blob:
        raise ValueError("parent RETURN Git blob pin drift")
    write(out / "PARENT_LOCK_VERIFICATION.json", {
        "schema": "WU088_R31AM_PARENT_LOCK_VERIFICATION_V1", "status": "UNCHANGED_VERIFIED",
        "files": verified, "selected_prediction_array_sha256": arrays_verified,
        "scope_canonical_bytes_unchanged": True, "parent_source_diff": [],
        "source_pins_field_clarification": {"field": "parent_return_sha256", "declared_value": pins["parent_return_sha256"],
                                           "actual_identity_type": "GIT_BLOB_SHA1", "verified_git_blob": git_blob,
                                           "actual_file_sha256": sha(return_path)},
        "direct_z075_output_accessed": False, "execution_authorized": False})
    here = repo / "research/r31am_post_z075"
    helper_path = here / "post_z075_policy.py"
    spec = importlib.util.spec_from_file_location("r31am_frozen_policy", helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    policy_path = here / "POST_Z075_DECISION_POLICY.json"
    policy = json.loads(policy_path.read_text())
    rows = helper.policy_table()
    declared = {(x["primary"], x["secondary"]): x["action"] for x in policy["action_matrix"]}
    replayed = {(x["primary"], x["secondary"]): x["action"] for x in rows}
    if len(rows) != 9 or len(declared) != 9 or replayed != declared:
        raise ValueError("action matrix contract mismatch")
    for row in rows:
        for field in ("auto_consume_z075_as_training", "auto_add_knot", "auto_execute_next_node"):
            if row[field] is not False or row[field] != policy[field]:
                raise ValueError("universal stop mismatch")
        if row["primary_secondary_independent_evidence_count"] != 1 or not row["shared_direct_geometry"]:
            raise ValueError("evidence counting mismatch")
    aliases = {"PARETO_SUPPORTED_AT_SELECTED_HOLDOUT": "PARETO_SUPPORTED_AT_Z075",
               "GLOBAL_SUPPORTED_AT_SELECTED_HOLDOUT": "GLOBAL_SUPPORTED_AT_Z075",
               "TRADEOFF_UNRESOLVED": "TRADEOFF_UNRESOLVED"}
    write(out / "POLICY_REPLAY.json", {
        "schema": "WU088_R31AM_POLICY_REPLAY_V1", "status": "PASS", "action_matrix": rows,
        "all_nine_outcomes_match_frozen_policy": True, "parent_primary_verdict_semantic_aliases": aliases,
        "aliases_do_not_change_parent_comparator_or_verdict": True,
        "evidence_count_per_future_shared_direct_geometry": 1, "actual_validation_evidence_count_this_handoff": 0,
        "reference_sensitivity_calculated": False, "source_accuracy_bound_status": "SOURCE_ACCURACY_BOUND_UNAVAILABLE",
        "epsilon_substitutes_prohibited": ["1e-10 decision tolerance", "metric residual", "bridge tolerance"],
        "claim_admission": {k: False for k in ("interval_wide_accuracy", "all_cell_refinement_gain", "source_accuracy",
                                               "transition_error", "full_cell", "trajectory", "H_skip", "production")},
        "strong_success_next_research_axes_require_separate_decision": ["source_accuracy_bound", "B_order_reference_discretization_certification",
             "full_cell_authority", "complete_HH_fixed_Q_physical_invariance", "BR01_BR02", "independent_project_review", "production_claim_audit"],
        "direct_z075_output_accessed": False, "science_producer_command_count": 0, "science_node_count": 0})
    write(out / "POLICY_LOCK.json", {
        "schema": "WU088_R31AM_POST_Z075_POLICY_LOCK_V1", "frozen_before_direct_output": True,
        "policy_path": str(policy_path.relative_to(repo)), "policy_sha256": sha(policy_path),
        "helper_path": str(helper_path.relative_to(repo)), "helper_sha256": sha(helper_path),
        "replay_sha256": sha(out / "POLICY_REPLAY.json"), "parent_lock_verification_sha256": sha(out / "PARENT_LOCK_VERIFICATION.json"),
        "R31AL_authorization_scope_sha256": sha(al / "AUTHORIZATION_SCOPE_CANONICAL.json"),
        "execution_authorized": False, "direct_z075_output_accessed": False, "science_node_count": 0})
    print(json.dumps({"status": "PASS", "outcomes": len(rows), "policy_sha256": sha(policy_path),
                      "parent_locks": "UNCHANGED_VERIFIED", "science_node_count": 0, "direct_z075_output_accessed": False}, indent=2))


if __name__ == "__main__":
    main()
