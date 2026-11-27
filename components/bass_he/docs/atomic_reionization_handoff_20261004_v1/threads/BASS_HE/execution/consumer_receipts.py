"""Verify imported REI-F00 execution evidence before advancing local task state.

The caller supplies bytes retrieved from one pinned consumer commit. This module
does not download, run kernels, decide photon closure, or admit a provider.
"""
import copy
import hashlib
import json
import re

PACKET = "docs/atomic_reionization_handoff_20261004_v1/"
INPUTS = {
    PACKET + "runtime_inputs/rei_model_lock.json",
    PACKET + "runtime_inputs/closure_process_decision.json",
    PACKET + "runtime_inputs/parent_and_lane_applicability.json",
}


def import_scope_lock(state, receipt_bytes, files, publication_commit):
    """Return a new state with verified F00 completion and its declared scope."""
    if not isinstance(publication_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", publication_commit):
        raise ValueError("Require an exact consumer publication commit")
    try:
        receipt = json.loads(receipt_bytes)
        required = {"task_id", "state", "input_identity", "changed_paths", "commands", "artifacts", "claim", "next_task"}
        if not required <= receipt.keys() or receipt["task_id"] != "REI-F00" or receipt["state"] != "completed":
            raise ValueError("Require a completed REI-F00 return envelope")
        if any(not isinstance(receipt["claim"][key], str) or not receipt["claim"][key] for key in ("basis", "ceiling")):
            raise ValueError("Require the consumer receipt's declared claim basis and ceiling")
        paths = [a["path"] for a in receipt["artifacts"]]
        if len(paths) != len(set(paths)) or set(paths) != INPUTS:
            raise ValueError("Require exactly the three distinct F00 contract artifacts")
        artifacts = {}
        for artifact in receipt["artifacts"]:
            data = files[artifact["path"]]
            if hashlib.sha256(data).hexdigest() != artifact["sha256"]:
                raise ValueError("Consumer artifact SHA256 mismatch: " + artifact["path"])
            artifacts[artifact["path"]] = json.loads(data)
        if not receipt["commands"]:
            raise ValueError("Missing consumer verification commands")
        for command in receipt["commands"]:
            if not command["command"] or type(command["exit_code"]) is not int or command["exit_code"] != 0:
                raise ValueError("Consumer verification did not succeed")
            if not files[command["evidence_path"]]:
                raise ValueError("Missing consumer command evidence")
        model = artifacts[PACKET + "runtime_inputs/rei_model_lock.json"]
        closure = artifacts[PACKET + "runtime_inputs/closure_process_decision.json"]
        for artifact in artifacts.values():
            if artifact["task_id"] != "REI-F00" or not artifact["model_id"] or artifact["model_id"] != model["model_id"]:
                raise ValueError("Consumer contract task/model mismatch")
        for key in ("source_commit", "source_snapshot_commit", "fixture_path", "fixture_sha256"):
            if receipt["input_identity"][key] != model["identity"][key]:
                raise ValueError("Receipt/model input identity mismatch: " + key)
        fixture = files[model["identity"]["fixture_path"]]
        if hashlib.sha256(fixture).hexdigest() != model["identity"]["fixture_sha256"]:
            raise ValueError("Fixture SHA256 mismatch")
        rct_enabled = closure["processes"]["He2_H_CX_RCT"]
        admitted = closure["physical_provider_admitted"]
        if type(rct_enabled) is not bool or type(admitted) is not bool:
            raise ValueError("Require explicit boolean consumer process/admission flags")
        if model["provider_selection"]["physical_admitted"] is not admitted:
            raise ValueError("Consumer admission declarations disagree")
        record = {
            "task_id": "REI-F00", "evidence_kind": "verified_imported_completion_receipt",
            "published_commit": publication_commit,
            "receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
            "artifact_sha256": {a["path"]: a["sha256"] for a in receipt["artifacts"]},
            "scope": {"model_id": model["model_id"], "rct_enabled": rct_enabled,
                      "physical_provider_admitted": admitted, "claim": receipt["claim"]},
            "suite_reexecuted": False,
        }
        result = copy.deepcopy(state)
        prior = [r for r in result["runtime_results"] if r["task_id"] == "REI-F00"]
        if prior and prior != [record]:
            raise ValueError("Existing F00 evidence differs; preserve it in a separate state")
        if "REI-F00" in result["completed_task_ids"] and not prior:
            raise ValueError("Existing completion has no matching verified receipt")
        if not prior:
            result["runtime_results"].append(record)
            result["completed_task_ids"].append("REI-F00")
        return result
    except (KeyError, TypeError, AttributeError, json.JSONDecodeError) as error:
        raise ValueError("Malformed or missing consumer evidence: " + str(error)) from error
