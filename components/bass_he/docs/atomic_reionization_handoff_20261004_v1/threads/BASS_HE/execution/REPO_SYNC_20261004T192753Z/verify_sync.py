"""Pinned-input audit only. Does not execute Rust, MPFI, or scientific suites."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile

import jsonschema
from domain_guard import validate_gate

BASE = Path(__file__).resolve().parent
THREAD = BASE.parents[1]
ROOT = next(p for p in BASE.parents if (p / ".git").exists())
COMMON = "docs/atomic_reionization_handoff_20261004_v1/"
RETURN_ROOT = COMMON + "runtime_returns/"
CERT_ROOT = "runs/rei_fastest_v1/map_certificate/"
MODEL = "REI_FT03_HG_RATE_MOMENT_CASE_A_CONTROLLED_V1"


def read(path):
    return json.loads((BASE / path).read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bind_selected_artifacts(unique, expected, historical):
    """Keep the single proven old lib snapshot separate from current artifacts."""
    matched, old_snapshots = [], []
    for path, record in unique.items():
        if path not in expected:
            continue
        if record["sha256"] != expected[path]:
            require(path == "rust/rei_microphysics/src/lib.rs", "F04 artifact mismatch: " + path)
            require(historical["commit"] == "6279036f06c9ba4d47574beab90b48fc2c6f9ba7"
                    and historical["path"] == path
                    and historical["sha256"] == expected[path]
                    and historical["matches_F04_top_level_artifact"] is True,
                    "unresolved historical library identity")
            old_snapshots.append({"path": path, "current_sha256": record["sha256"],
                                  "receipt_sha256": expected[path], "snapshot_commit": historical["commit"]})
        else:
            matched.append(path)
    return matched, old_snapshots


def main():
    # Reuse the unchanged, tested byte verifier without rerunning its suite.
    spec = importlib.util.spec_from_file_location("prior_intake", THREAD / "execution/HE_F2C_20261005T001658KST/rct_intake.py")
    prior = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prior)
    observations = []
    for path in ["INPUT_IDENTITY.json", "CERTIFICATE_INPUT_DELTA.json", "PARENT_SOURCE_IDENTITY.json"]:
        observations += read(path)["observations"]
    prior.verify_saved(BASE, observations)
    unique = {r["path"]: r for r in observations}
    receipts = {key: read("consumer/" + RETURN_ROOT + "REI-" + key + ".json") for key in ["F04", "F06", "F07"]}
    schema = json.loads((ROOT / COMMON / "common/RETURN_CONTRACT.schema.json").read_text())
    for key, receipt in receipts.items():
        jsonschema.Draft202012Validator(schema).validate(receipt)
        require(receipt["task_id"] == "REI-" + key and receipt["state"] == "completed", key + " receipt state")
        require(receipt["scientific_admission"] == "HOLD", key + " physical promotion")
    # Bind only selected changed F04 artifacts, not all historical receipts.
    expected = {a["path"]: a["sha256"] for a in receipts["F04"]["artifacts"]}
    matched, old_snapshots = bind_selected_artifacts(unique, expected, read("HISTORICAL_LIB_RESOLUTION.json"))
    certificate = read("consumer/" + CERT_ROOT + "certificate.json")
    parent = read("consumer/" + CERT_ROOT + "parent_manifest.json")
    checker = read("consumer/" + CERT_ROOT + "checker_receipt.json")
    closeout = read("consumer/" + RETURN_ROOT + "evidence/F04_certificate/closeout.json")
    require(certificate["schema"] == "rei.actual-static-map-certificate.v1", "wrong certificate scope")
    require(certificate["producer_data"]["parent_manifest_sha256"] == unique[CERT_ROOT + "parent_manifest.json"]["sha256"], "parent manifest hash")
    require(certificate["producer_data"]["parent_center_bits"] == parent["actual_center_and_model_bits"]["center_bits"], "center bits")
    proof = certificate["bound_proof"]
    require(proof["status"] == checker["status"] == "PASS", "reported certificate failure")
    require(proof["model_id"] == checker["model_id"] == parent["model_id"] == MODEL, "certificate model")
    require(checker["production_evaluator_called"] is False, "checker independence contract")
    require(proof["scientific_admission"] == checker["scientific_admission"] == closeout["scientific_admission"] == "HOLD", "certificate promotion")
    require(closeout["expandingS0_certificate"] == "NOT_RUN", "expanded scope")
    require(closeout["final_bytes_independently_reviewed"] is False, "review provenance")
    require(proof["strict_local_limit"] == parent["strict_local_error_limit"] == 0.0002, "local tolerance changed")
    require(proof["strict_public_width_limit"] == parent["strict_public_width_limit"] == 0.002, "public tolerance changed")
    require(proof["joint_full_half_local_bounds"] == checker["local_bounds"] == closeout["joint_local_bounds"], "reported bounds conflict")
    for path, sha in parent["source_identity"].items():
        require(unique[path]["sha256"] == sha, "parent source changed: " + path)
    old = json.loads((THREAD / "execution/HE_F2C_20261005T001658KST/consumer/evidence/FINAL_INTEGRATION.json").read_text())
    stable = {}
    for name in ["he_rct.rs", "ft03_controlled.rs", "ft03_rates.rs"]:
        path = "rust/rei_microphysics/src/" + name
        identity = next(r["sha256"] for r in old["file_identities"] if r["path"] == "coding/rei_crate/src/" + name)
        require(unique[path]["sha256"] == identity, "accepted RHS source changed: " + name)
        stable[path] = identity
    gate_path = THREAD / "runs/HE-F2C_20261005/HE_F3_DOMAIN_GATE.json"
    gate = validate_gate(json.loads(gate_path.read_text()))
    result = {"status": "PASS", "verification_scope": "IDENTITY_SCHEMA_AND_CLAIM_BOUNDARY_ONLY",
        "supplier_head": read("INPUT_IDENTITY.json")["supplier_head"],
        "consumer_head": read("INPUT_IDENTITY.json")["consumer_head"],
        "saved_inputs_verified": len(unique), "F04_selected_artifacts_hash_bound": matched,
        "F04_historical_artifact_excluded_from_current_binding": old_snapshots,
        "F04_whole_latest_crate_receipt_accepted": False,
        "F04_parent_sources_verified": 5, "accepted_RCT_RHS_sources_unchanged": stable,
        "lib_rs_changed": "new exports; old 116-test evidence remains scoped to 41e4592, not the latest crate",
        "domain_gate_sha256": hashlib.sha256(gate_path.read_bytes()).hexdigest(), "domain_gate": gate,
        "F04_received_status": "ACTUAL_STATIC_FT03_MAP_CERTIFICATE_PASS",
        "F04_received_claim_ceiling": receipts["F04"]["claim"]["ceiling"],
        "F04_proof_recomputed_here": False, "F04_final_bytes_independently_reviewed": False,
        "source_physical_admission": False, "RCT_time_stepper_admission": False,
        "HE_F2_global_completed": False, "scientific_runs_this_loop": 0,
        "external_F06_F07": "receipt schemas and HOLD inspected; not independently scientifically verified",
        "supplier_reference_9_tests": "reported existing evidence; not rerun",
        "archive_restored_here": False, "ChatGPT_direct_delivery_verified": False}
    fd, temporary = tempfile.mkstemp(dir=BASE, prefix=".verification-")
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, BASE / "VERIFICATION.json")
        directory = os.open(BASE, os.O_DIRECTORY | os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        os.unlink(temporary)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
