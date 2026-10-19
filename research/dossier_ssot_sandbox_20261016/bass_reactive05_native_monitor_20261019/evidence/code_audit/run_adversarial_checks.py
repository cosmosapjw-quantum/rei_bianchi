#!/usr/bin/env python3
"""Read-only BR05 review: private CSV mutations against a pinned root auditor."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def input_identity(unit, work):
    parent = json.loads((unit / "contracts/PARENT_INPUT_SHA256.json").read_text())
    frozen = json.loads((work / "implementation/SOURCE_IDENTITY_FINAL.json").read_text())["new_files"]
    expected = {**parent, **frozen}
    actual = {name: sha(unit / name) for name in expected}
    assert actual == expected
    return {"parent_count": len(parent), "new_count": len(frozen), "hashes": actual}


def physical_body(text, start):
    first = text.index(start)
    last = text.index("\n    }\n", first) + len("\n    }\n")
    return text[first:last]


def run_one(snapshot, monitor, native, output, log):
    command = [sys.executable, str(snapshot / "audit_native_monitor.py"), "--monitor", str(monitor),
               "--native", str(native), "--output", str(output)]
    begin = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            timeout=120, check=False)
    log.write_text(result.stdout)
    return {"command": command, "started_utc": begin,
            "completed_utc": datetime.now(timezone.utc).isoformat(),
            "returncode": result.returncode, "log": str(log), "log_sha256": sha(log)}, result.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    unit, work, output = args.unit.resolve(), args.work.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc).isoformat()
    before = input_identity(unit, work)
    sample = work / "implementation/sample_final"
    originals = {str(p): sha(p) for p in [sample / "native.csv", *sorted((sample / "monitor").glob("*.csv"))]}
    snapshot = output / "auditor_snapshot"
    snapshot.mkdir()
    for name in ("audit_native_monitor.py", "monitor_reference.py"):
        shutil.copy2(unit / "scripts" / name, snapshot / name)
        assert sha(snapshot / name) == sha(unit / "scripts" / name)
    snapshot_identity = {name: sha(snapshot / name) for name in ("audit_native_monitor.py", "monitor_reference.py")}

    old = (unit / "crate/ap_midpoint.rs").read_text()
    new = (unit / "crate/monitored_midpoint.rs").read_text()
    physical_bodies = {}
    for name, marker in (("emit_births", "    pub fn emit_births("), ("photo", "    fn photo(")):
        left, right = physical_body(old, marker), physical_body(new, marker)
        assert left == right, name
        physical_bodies[name] = {"byte_identical": True, "sha256": hashlib.sha256(left.encode()).hexdigest()}
    proof = json.loads((work / "implementation/MECHANICAL_HOOK_PROOF_FINAL.json").read_text())
    reconstructed = old
    for edit in proof["edits"]:
        assert reconstructed.count(edit["old"]) == edit["count"]
        reconstructed = reconstructed.replace(edit["old"], edit["new"])
    recovered = reconstructed
    for edit in reversed(proof["edits"]):
        assert recovered.count(edit["new"]) == edit["count"]
        recovered = recovered.replace(edit["new"], edit["old"])
    assert recovered == old
    assert proof["generated_file_sha256"] == sha(unit / "crate/monitored_midpoint.rs")
    assert proof["scoped_rustfmt_verified"]

    baseline, baseline_text = run_one(snapshot, sample / "monitor", sample / "native.csv",
                                      output / "baseline_analysis", output / "baseline.log")
    assert baseline["returncode"] == 0, baseline_text
    baseline_verification = json.loads((output / "baseline_analysis/MONITOR_INDEPENDENT_VERIFICATION.json").read_text())
    assert baseline_verification["status"] == "PASS_SCOPED"
    baseline["status"] = "PASS_SCOPED"
    baseline["verification_sha256"] = sha(output / "baseline_analysis/MONITOR_INDEPENDENT_VERIFICATION.json")

    mutations = []
    definitions = (
        ("cohort_append_join", "cohort_index", "cohort appendindex join"),
        ("killing_constant", "K1_ev_scale", "Killing_birth_constant"),
        ("source_birth_weight", "born_count_com3", "born_source_weight"),
    )
    for name, column, expected_message in definitions:
        case = output / name
        case.mkdir()
        shutil.copytree(sample / "monitor", case / "monitor")
        shutil.copy2(sample / "native.csv", case / "native.csv")
        target = case / "monitor/MONITOR_BIRTHS.csv"
        with target.open(newline="") as stream:
            reader = csv.DictReader(stream)
            fields = reader.fieldnames
            rows = list(reader)
        saved = [dict(row) for row in rows]
        index = next(i for i, row in enumerate(rows) if column == "cohort_index" or float(row[column]) != 0)
        old_value = rows[index][column]
        if column == "cohort_index":
            new_value = str(int(old_value) + 1)
        else:
            new_value = format(float(old_value) * (1.01 if column == "K1_ev_scale" else 1.02), ".17e")
        rows[index][column] = new_value
        changed = [(i, key) for i, (a, b) in enumerate(zip(saved, rows)) for key in fields if a[key] != b[key]]
        assert changed == [(index, column)]
        with target.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        execution, text = run_one(snapshot, case / "monitor", case / "native.csv",
                                  case / "analysis", case / "audit.log")
        caught = execution["returncode"] != 0 and expected_message in text
        assert caught, (name, text)
        mutations.append({"id": name, "column": column, "zero_based_row": index,
                          "old_value": old_value, "new_value": new_value,
                          "changed_cells": 1, "mutated_csv_sha256": sha(target),
                          "expected_failure_message": expected_message, "caught": caught,
                          "successful_verification_written": (case / "analysis/MONITOR_INDEPENDENT_VERIFICATION.json").exists(),
                          **execution})

    after = input_identity(unit, work)
    assert before == after
    assert all(sha(Path(path)) == expected for path, expected in originals.items())
    parent_auditor_changed = {name: sha(unit / "scripts" / name) != expected for name, expected in snapshot_identity.items()}
    result = {"schema": "rei.br05.code_audit.adversarial.v1", "status": "PASS_SCOPED",
              "started_utc": started, "completed_utc": datetime.now(timezone.utc).isoformat(),
              "reviewer": "/root/birth_implementation", "reviewer_authored_rust_code": True,
              "independence": "New CSV fault-injection executions against byte-identical snapshots of the root-authored Python auditor; not independent personnel review.",
              "rust_tests_executed_in_this_audit": 0, "source_modified": False,
              "source_identity": before, "source_unchanged_after": True,
              "sample_input_identity": originals, "sample_unchanged_after": True,
              "auditor_snapshot": snapshot_identity, "parent_auditor_changed_during_execution": parent_auditor_changed,
              "physical_bodies": physical_bodies, "mechanical_proof_recovered": True,
              "baseline": baseline, "mutations": mutations, "all_mutations_caught": all(x["caught"] for x in mutations),
              "harness_sha256": sha(Path(__file__))}
    write_json(output / "ADVERSARIAL_EXECUTION.json", result)
    print(json.dumps({"status": result["status"], "mutations": len(mutations),
                      "all_caught": result["all_mutations_caught"], "source_files_unchanged": len(before["hashes"]),
                      "output": str(output / "ADVERSARIAL_EXECUTION.json")}, indent=2))


if __name__ == "__main__":
    main()
