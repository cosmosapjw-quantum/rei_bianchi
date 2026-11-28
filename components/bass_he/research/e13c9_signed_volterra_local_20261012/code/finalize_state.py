#!/usr/bin/env python3
"""Write the scientific closeout from saved evidence; no numerical runs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def read(relative):
    return json.loads((ROOT / relative).read_bytes())


def pin(relative):
    data = (ROOT / relative).read_bytes()
    return {"relative_path": relative, "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest()}


def write(relative, value):
    with (ROOT / relative).open("x", encoding="utf-8") as target:
        json.dump(value, target, ensure_ascii=False, indent=2, sort_keys=True)
        target.write("\n")


def main():
    decision = read("review/independent/INDEPENDENT_DECISION.json")
    analysis = read("analysis/ACTUAL_PORTABLE/LOCAL_ANALYSIS.json")
    assert decision["decision"] == "PROMOTE_SCOPED_LOCAL_SIGNED_VOLTERRA"
    assert pin("review/independent/INDEPENDENT_DECISION.json")["sha256"] == "6d4ad71a803c5fd4d4a7fa8c08157e9bd2ec2a28698ae6578d474a6f9641d303"
    assert pin("analysis/ACTUAL_PORTABLE/LOCAL_ANALYSIS.json")["sha256"] == "b72a54d62fa1ebd11fbe67d5e3681001730a820d9170fba07fbffef2e67a5870"
    assert analysis["required_count"] == analysis["selected_mixed_resolution_nested_count"] == analysis["selected_mixed_resolution_nonincreasing_count"] == 170
    assert decision["NCP_disposition"]["new_jobs"] == 0
    evidence = {key: pin(key) for key in (
        "review/independent/INDEPENDENT_DECISION.json",
        "review/independent/INDEPENDENT_REVIEW_KO.md",
        "analysis/ACTUAL_PORTABLE/LOCAL_ANALYSIS.json",
        "analysis/ACTUAL_PORTABLE/BOUND_ALLOCATION.json",
        "analysis/ACTUAL_PORTABLE/SELECTED_CANDIDATE.json",
        "code/signed_volterra.py", "SOURCE_LOCK.json", "WORK_PLAN.json",
        "SCIENTIFIC_CONTRACT.md", "tests/MANUFACTURED/EXEC01/RECEIPT.json")}
    validation = {key: value for key, value in decision["validation"].items()
                  if not isinstance(value, (dict, list))}
    current = {
        "schema": "bass-he-e13c9-current-state-v1",
        "node": "HE_E13C9_SIGNED_VOLTERRA_LOCAL01",
        "updated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "SCIENTIFIC_LOOP_COMPLETE", "decision": decision["decision"],
        "scope": {"selected_nodes": analysis["selected_nodes"], "segments": 12,
                  "selected_M": {"1": 128, "1162": 256, "1976": 128, "1620": 128, "2344": 128},
                  "baseline_N": {"1": 1024, "1162": 1024, "1976": 1024, "1620": 512, "2344": 512},
                  "interval_precision": 60, "raw_intervals": 170,
                  "nested": 170, "nonincreasing": 170,
                  "raw_intersections": 0, "old_interval_fallbacks": 0},
        "selected_weighted_widths": {key: {name: value[name] for name in (
            "baseline_width_display", "candidate_width_display", "gain_percent_display")}
            for key, value in analysis["selected_aggregate_summary"].items()},
        "claim_ceiling": decision["claim_ceiling"], "resources": analysis["resources"],
        "validation": validation, "authoritative_evidence": evidence,
        "saved_status_policy": "Original pre-review candidate/analysis statuses remain unchanged; the recorded independent decision is authoritative for adoption.",
        "NCP_action": "CLOSED_NO_NEW_HEAVY_TASK", "new_NCP_work_units": [],
        "next_local_question": "Reduce the inherited first-midpoint enclosure bound with a separately justified rule and independent local controls.",
        "publication": "Actual remote ACK/readback and draft PR identities are recorded by the external delivery receipt after this immutable package is built."
    }
    write("CURRENT_STATE.json", current)
    write("NCP_ACTION.json", {
        "schema": "bass-he-e13c9-ncp-action-v1", "action": "CLOSED_NO_NEW_HEAVY_TASK",
        "new_jobs": 0, "work_units": [],
        "decision_sha256": evidence["review/independent/INDEPENDENT_DECISION.json"]["sha256"],
        "reason": decision["NCP_disposition"]["reason"],
        "new_budget_physics_full_first2_N512_N1024_M256_bulk_MPI_native_benchmark_invocations": 0,
        "completed_E13C8_batch_replay_required": False, "current_E13C9_local_replay_required": False,
        "restore_only_if_actual_files_missing": True,
        "new_compute_host_or_server_state_change_required": False,
        "scope_ceiling": decision["claim_ceiling"],
        "ack": "ACK_E13C9_CLOSED; NEW_HEAVY_TASKS=0; E13C8_FULL_FINITE_UNCHANGED; E13C9_LOCAL5_ADMITTED; FULL_SECOND_CORRECTION=NOT_RUN"
    })
    write("NEXT_DAG.json", {
        "schema": "bass-he-e13c9-next-dag-v1",
        "completed": ["E13C8_FULL_FINITE_CAPTURED_OFF", "HE_E13C9_SIGNED_VOLTERRA_LOCAL01"],
        "next_node": {
            "id": "HE_E13C10_FIRST_MIDPOINT_BOUND_LOCAL01", "status": "PROPOSED_NOT_RUN", "location": "HERE_LOCAL",
            "question": "Can a rigorously bounded first-variation integration rule reduce the dominant inherited midpoint width with lower local cost?",
            "motivation": "Inherited midpoint and propagated carry account for approximately 97.81% of selected P and 98.09% of selected H positive halfwidth bounds; these are bounds, not measured errors.",
            "required_work": ["Derive the rule and needed derivative or remainder bounds from the immutable coefficient contract.",
                              "Use independent closed-form oracles for sign, zero, species cancellation, incoming uncertainty, and event cases.",
                              "Run the shortest discriminating captured paths locally with raw interval admission and resource receipts.",
                              "Decide whether a concrete full-population accuracy objective requires a new heavy work list."],
            "restriction": "Jet2 alone does not justify an unproved higher-order Simpson/Gauss remainder; completed numerical workloads stay closed."
        },
        "future_NCP_gate": {"status": "NO_CONTRACT_NO_WORK_UNITS", "jobs": 0,
            "needed_before_new_handoff": ["Explicit full-population numerical accuracy objective", "Locally validated method and immutable source/input/work lock", "Not-yet-executed independent work units", "Measured cost and useful parallel acceleration", "Memory and thread policy based on measured resources"]},
        "physical_continuum_production_receiver": "HOLD"
    })
    initial = ROOT / "state/RUN_STATE.json"
    preserved = ROOT / "evidence/INITIAL_RUN_STATE.json"
    assert not preserved.exists()
    shutil.copyfile(initial, preserved)
    final_state = {key: current[key] for key in (
        "node", "updated_utc", "status", "decision", "scope", "claim_ceiling", "resources", "NCP_action", "new_NCP_work_units", "publication")}
    final_state.update({"phase": "CLOSEOUT_COMPLETE", "model": "GPT-6 Astra Pro",
                        "model_identity_source": "trusted developer metadata",
                        "harness_version": "GPT-6 Astra research+coding v4.0.0 20260908",
                        "initial_state_preserved": "evidence/INITIAL_RUN_STATE.json"})
    initial.write_text(json.dumps(final_state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write("state/CLOSEOUT.json", {
        "schema": "bass-he-e13c9-scientific-closeout-v1", "status": "COMPLETE",
        "scientific_decision": decision["decision"], "blocking_findings": decision["unresolved_blocking_findings"],
        "necessary_gates_closed": True, "additional_optional_numerical_testing": "STOP",
        "NCP_new_jobs": 0, "source_failures_and_amendments_preserved": True,
        "current_state": pin("CURRENT_STATE.json"), "next_dag": pin("NEXT_DAG.json"),
        "NCP_action": pin("NCP_ACTION.json"),
        "transport_publication_authority": "External delivery receipt; no upload or PR success is fabricated by this scientific closeout."
    })
    print(json.dumps({"status": "SCIENTIFIC_CLOSEOUT_WRITTEN", "new_scientific_calls": 0,
                      "new_NCP_jobs": 0, "current_state": pin("CURRENT_STATE.json")}, indent=2))


if __name__ == "__main__":
    main()
