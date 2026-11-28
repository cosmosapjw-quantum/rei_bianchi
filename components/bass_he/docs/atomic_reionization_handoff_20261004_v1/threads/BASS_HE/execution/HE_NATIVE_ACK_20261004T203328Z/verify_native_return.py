"""Verify delivered data and current dependency identities; never invoke native code."""
import hashlib
import json
import os
from pathlib import Path
import tempfile

from mixed_intake import validate, require, TEST_SHA, GOLDEN_SHA, INPUT_SHA

BASE = Path(__file__).resolve().parent
THREAD = BASE.parents[1]
PREFIX = "inputs/loop1/he_mixed/"
SUPPLIER = PREFIX + "supplier_reference/BASS_HE_FLRW02B_20261005/"


def read(path):
    return json.loads((BASE / path).read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def publish_new(path, data):
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".intake-")
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(name, path)  # Preserve previous results; never overwrite evidence.
        directory = os.open(path.parent, os.O_DIRECTORY | os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        os.unlink(name)


def main():
    inputs = read("INPUT_IDENTITY.json")
    for item in inputs["observations"]:
        path = BASE / item["local_path"]
        require(path.stat().st_size == item["bytes"] and digest(path) == item["sha256"], "saved input identity")
        if "git_blob" in item:
            raw = path.read_bytes()
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            require(blob == item["git_blob"], "saved Git blob identity")
    contract, result = read(PREFIX + "EXECUTION_CONTRACT.json"), read(PREFIX + "NATIVE_RESULT.json")
    require(digest(BASE / (PREFIX + "EXECUTION_CONTRACT.json")) == result["contract_sha256"], "contract identity")
    acceptance = validate(contract, result, read(PREFIX + "EXECUTION_LOG.json"),
                          (BASE / (PREFIX + "NATIVE_MIXED.stdout")).read_text(),
                          read(PREFIX + "NATIVE_COMPARISONS.json"), read("inputs/review/LOOP1_REVIEW.json"))
    require(digest(BASE / (SUPPLIER + "GOLDEN.json")) == GOLDEN_SHA, "GOLDEN identity")
    require(digest(BASE / (SUPPLIER + "inputs/REFERENCE_INPUT.json")) == INPUT_SHA, "reference identity")
    require(digest(BASE / (SUPPLIER + "proposed_consumer/he_flrw02_absorption.rs")) == TEST_SHA, "test identity")
    require(digest(BASE / "inputs/consumer/rust/rei_microphysics/tests/he_flrw02_absorption.rs") == TEST_SHA, "live test identity")
    sources = {i["path"]: i for i in inputs["observations"] if "git_blob" in i}
    bound = []
    for item in contract["native_sources"][:4]:
        path = "rust/rei_microphysics/" + item["path"]
        require(sources[path]["sha256"] == item["sha256"] and sources[path]["git_blob"] == item["git_blob"], "changed absorption dependency: " + path)
        bound.append(sources[path])
    # The existing RCT local-RHS result is still dependency-matched. No newer
    # whole-crate or time-stepper acceptance follows from these three hashes.
    prior = json.loads((THREAD / "execution/REPO_SYNC_20261004T192753Z/VERIFICATION.json").read_text())
    for path, sha in prior["accepted_RCT_RHS_sources_unchanged"].items():
        require(sources[path]["sha256"] == sha, "changed accepted local RHS dependency")
    original = json.loads((THREAD / "runs/HE-FLRW02B_NATIVE_20261005/RETURN.json").read_text())
    require(original["test_sha256"] == TEST_SHA and original["golden_sha256"] == GOLDEN_SHA,
            "concurrent original-input run differs")
    f05 = read("inputs/consumer/docs/atomic_reionization_handoff_20261004_v1/runtime_returns/REI-F05.json")
    require(f05["state"] == "completed" and f05["scientific_admission"] == "HOLD", "F05 scope")
    f08 = read("inputs/consumer/docs/atomic_reionization_handoff_20261004_v1/runtime_returns/evidence/F08_stage/qualification.json")
    require(f08["F08_paired_history"] == "NOT_EXECUTED" and f08["scientific_admission"] == "HOLD", "F08 scope")
    verification = {"schema": "bass-he.native-intake-verification.v1", "status": "PASS",
                    "verification_scope": "SAVED_BYTES_RAW_LOG_ARITHMETIC_AND_FROZEN_RECEIPT_SCOPE",
                    "acceptance": acceptance, "inputs_verified": len(inputs["observations"]),
                    "consumer_observed_commit": inputs["consumer_observed_commit"],
                    "executed_native_commit": contract["native_commit"],
                    "current_absorption_dependencies": bound,
                    "RCT_local_RHS_sources_unchanged": prior["accepted_RCT_RHS_sources_unchanged"],
                    "archive_payloads_verified": inputs["archive_payloads_verified"],
                    "max_source_reference_relative": result["statistics"]["FLRW02_REFERENCE"]["max_relative"]["relative"],
                    "max_ledger_scale_relative": result["statistics"]["FLRW02_RESIDUAL"]["max_relative"]["relative"],
                    "concurrent_native_run": {"commit": original["executed_consumer_commit"],
                                              "test_and_golden_same": True, "independently_reviewed_here": False,
                                              "new_scientific_milestone": False},
                    "native_runs_this_loop": 0, "historical_scientific_suites_rerun": 0,
                    "new_independent_scientific_review": False,
                    "consumer_remote_mutations": 0, "ChatGPT_direct_delivery_verified": False}
    publish_new(BASE / "VERIFICATION.json", verification)
    print(json.dumps(verification, ensure_ascii=False))


if __name__ == "__main__":
    main()
