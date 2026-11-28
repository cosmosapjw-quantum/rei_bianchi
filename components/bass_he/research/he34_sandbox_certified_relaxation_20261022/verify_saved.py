#!/usr/bin/env python3
"""Read-only HE34-SCR receipt/hash verification: no solver, render or benchmark."""
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent


def main():
    checked = set()

    def read(name):
        return json.loads((HERE / name).read_text())

    def check(name, expected):
        path = (HERE / name).resolve()
        if not path.is_relative_to(HERE):
            raise ValueError("receipt path escapes this unit: " + name)
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError("SHA256 mismatch: " + name)
        checked.add(name)

    mechanical = read("results/MECHANICAL_CONTROLS.json")
    receipt = read("results/MECHANICAL_RECEIPT.json")
    if receipt["status"] != "completed" or receipt["identity"] != mechanical["identity"]:
        raise ValueError("Mechanical completion/identity mismatch")
    for name, value in receipt["payload_sha256"].items():
        check("results/" + name, value)
    for name, value in mechanical["parameters"]["code"].items():
        check(name, value)
    check("data/SAVED_BACKGROUND.csv", mechanical["parameters"]["input"])
    background = read("evidence/BACKGROUND_INPUT.json")
    check("data/SAVED_BACKGROUND.csv", background["csv_sha256"])
    mechanical_execution = read("evidence/MECHANICAL_EXECUTION.json")
    if mechanical_execution["exit_code"] != 0:
        raise ValueError("Mechanical execution failed")
    for name, value in mechanical_execution["source_sha256"].items():
        check(name, value)

    neutral = read("results/NEUTRAL_TRANSPORT.json")
    transport_execution = read("evidence/TRANSPORT_VALIDATION.json")
    if neutral["status"] != "passed" or transport_execution["execution"]["exit_code"] != 0:
        raise ValueError("Neutral execution failed")
    check("results/NEUTRAL_TRANSPORT.json", transport_execution["result_sha256"])
    for name, value in neutral["source_sha256"].items():
        check(name, value)
    check(neutral["csv"]["path"], neutral["csv"]["sha256"])

    unit_checks = read("evidence/REDUCTION_UNIT_CHECKS.json")
    if unit_checks["status"] != "pass_scoped":
        raise ValueError("Reduction implementation checks are not accepted")
    final_attempt = unit_checks["attempts"][-1]
    check("src/certified_relaxation.py", final_attempt["source_sha256"])
    check("checks/check_relaxation.py", final_attempt["checks_sha256"])

    plots = read("evidence/PLOT_EXECUTION.json")
    if plots["status"] != "passed":
        raise ValueError("Saved plot execution failed")
    for mapping in (plots["inputs_sha256"], plots["code_sha256"]):
        for name, value in mapping.items():
            check(name, value)
    for name, info in plots["outputs"].items():
        check(name, info["sha256"])

    print(json.dumps({
        "status": "REUSED_COMPLETE_VERIFIED_PAYLOAD",
        "checked_unique_files": len(checked),
        "files": sorted(checked),
        "mechanical_identity": mechanical["identity"],
        "plot_identity": plots["cache_identity"],
        "verification_scope": "receipt completion and dependency/output SHA256; no new scientific validation",
        "new_IVPs": 0, "new_renders": 0, "new_benchmarks": 0
    }, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "failed", "error": str(error)}), file=sys.stderr)
        sys.exit(1)
