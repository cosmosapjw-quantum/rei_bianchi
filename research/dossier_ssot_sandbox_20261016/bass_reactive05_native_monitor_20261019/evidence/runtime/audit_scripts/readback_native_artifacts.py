#!/usr/bin/env python3
"""Read-only structural/provenance audit after the one BR05 native invocation.

This does not evaluate the physical accuracy of any numerical value.  The
independent scientific audit is a separate artifact owned by the parent task.
"""
import argparse
import csv
import datetime
import hashlib
import json
import os
from pathlib import Path
import re


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def csv_shape(path):
    with path.open(newline="") as stream:
        reader = csv.reader(stream)
        header = next(reader)
        count = 0
        wrong_width_rows = []
        last = None
        for number, row in enumerate(reader, 1):
            count += 1
            if len(row) != len(header):
                wrong_width_rows.append(number)
            last = row
    return {
        "columns": len(header),
        "header": header,
        "rows": count,
        "wrong_width_rows": wrong_width_rows,
        "last": dict(zip(header, last)) if last is not None else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.unit_root.resolve()
    native = root / "evidence/native"
    runtime = root / "evidence/runtime"
    receipt_path = native / "ap_n16_r8.json"
    receipt = json.loads(receipt_path.read_text())
    gate_path = runtime / "FULL_RUST_CLIPPY_VERIFICATION.json"
    gate = json.loads(gate_path.read_text())
    checks = {}
    checks["native_completed_once"] = (
        receipt["status"] == "COMPLETED"
        and receipt["exit_code"] == 0
        and receipt["native_process_invocations"] == 1
        and receipt["failure_class"] is None
    )
    source_mismatches = [
        rel
        for rel, expected in receipt["source_sha256"].items()
        if digest(root / rel) != expected
    ]
    checks["all_source_current_hashes_match_run"] = not source_mismatches
    checks["inherited_125_before_after"] = (
        receipt["parent_inputs_checked"] == 125
        and receipt["parent_inputs_match_before"]
        and receipt["parent_inputs_match_after"]
        and receipt["source_unchanged_during_run"]
    )
    binary_hash = digest(Path(receipt["command"][0]))
    checks["built_run_after_and_current_binary_match"] = (
        binary_hash
        == receipt["binary_sha256"]
        == receipt["binary_sha256_after"]
        == gate["native_release_binary_sha256"]
    )
    normal_path = native / "ap_n16_r8.csv"
    normal_hash = digest(normal_path)
    normal = csv_shape(normal_path)
    checks["normal_csv_hash_before_rename_receipt_and_current"] = (
        normal_hash == receipt["csv_sha256"] == receipt["csv_sha256_before_rename"]
    )
    checks["normal_csv_16_rows_54_columns_and_receipt_final"] = (
        normal["rows"] == receipt["rows"] == receipt["planned_rows"] == 16
        and normal["columns"] == 54
        and not normal["wrong_width_rows"]
        and normal["last"] == receipt["final"]
        and int(normal["last"]["step"]) == 16
    )
    original_driver = (root / "crate/ap_native_driver.rs").read_text()
    original_header_match = re.search(r'"(case,grid,nsteps[^"\n]+)"', original_driver)
    checks["original_54column_header_exact"] = (
        original_header_match is not None
        and normal["header"] == original_header_match.group(1).split(",")
    )
    stderr_path = native / "ap_n16_r8.stderr"
    checks["stderr_receipt_matches_current"] = stderr_path.read_text() == receipt["stderr"]
    checks["stderr_monitor_completion_no_solver_failure"] = (
        receipt["stderr"]
        == "MONITOR_COMPLETE accepted_steps=16 birth_rows=314624 final_cohorts=314624\n"
    )
    monitor_files = []
    for file in receipt["monitor"]["files"]:
        path = native / "monitor_n16_r8" / file["path"]
        shape = csv_shape(path)
        shape.pop("last")
        shape.pop("header")
        current_hash = digest(path)
        valid = (
            current_hash == file["sha256"]
            and path.stat().st_size == file["bytes"]
            and not shape["wrong_width_rows"]
        )
        checks["monitor_file_" + file["path"]] = valid
        monitor_files.append({**file, **shape, "current_sha256": current_hash, "valid": valid})
    monitor_by_name = {entry["path"]: entry for entry in monitor_files}
    checks["monitor_structural_cardinality"] = (
        monitor_by_name["MONITOR_BIRTHS.csv"]["rows"]
        == monitor_by_name["MONITOR_FINAL_COHORTS.csv"]["rows"]
        == int(receipt["final"]["cohorts"])
        == 314624
        and monitor_by_name["MONITOR_STEPS.csv"]["rows"] == 16
    )
    test_log = (runtime / "ALL_RUST_TESTS.log").read_text()
    test_counts = re.findall(r"test result: ok\. (\d+) passed; (\d+) failed;", test_log)
    parsed_counts = {
        "passed": sum(int(passed) for passed, _ in test_counts),
        "failed": sum(int(failed) for _, failed in test_counts),
        "harness_groups": len(test_counts),
    }
    checks["full_test_counts_from_current_log"] = (
        parsed_counts == gate["actual_full_test_counts"]
        == {"passed": 233, "failed": 0, "harness_groups": 60}
    )
    checks["all_gate_exit_and_log_hashes"] = all(
        stage["exit_code"] == 0
        and digest(runtime / stage["log"]) == stage["log_sha256"]
        for stage in gate["executions"]
    )
    checks["gate_source_frozen"] = gate["status"] == "PASS_SOURCE_FROZEN" and gate["source_unchanged"]
    orphan_paths = list(native.glob("ap_n16_r8.running.*"))
    report = {
        "status": ("PASS_FINAL_ARTIFACT_PROVENANCE_WITH_ORPHAN_FILES" if orphan_paths else "PASS_ARTIFACT_PROVENANCE_ONLY") if all(checks.values()) else "FAIL_ARTIFACT_PROVENANCE",
        "completed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "scope": "Read-only raw-byte readback, CSV dimensions, receipt consistency and source/binary identities. This is not a numerical-accuracy or convergence certificate.",
        "native_receipt_sha256": digest(receipt_path),
        "full_gate_receipt_sha256": digest(gate_path),
        "auditor_sha256": digest(Path(__file__)),
        "checks": checks,
        "observations": {
            "unclaimed_intermediate_paths_present": [str(path.relative_to(root)) for path in orphan_paths],
            "orphan_classification": "evidence/runtime/orphan_snapshot/ORPHAN_CLASSIFICATION.json",
            "orphan_origin": "UNKNOWN. Complete artifacts and stale intermediate paths are assessed separately; originals are untouched.",
            "initial_auditor_defect": "The first audit searched for println! while the inherited driver uses writeln!. Only that audit expression was corrected; the actual header is compared byte-for-byte after splitting.",
            "initial_audit_preserved": "evidence/runtime/NATIVE_ARTIFACT_READBACK.json",
        },
        "source_files_checked": len(receipt["source_sha256"]),
        "source_mismatches": source_mismatches,
        "native_csv": {"path": str(normal_path.relative_to(root)), "bytes": normal_path.stat().st_size, "sha256": normal_hash, "rows": normal["rows"], "columns": normal["columns"]},
        "monitor_files": monitor_files,
        "monitor_total_bytes": sum(file["bytes"] for file in monitor_files),
        "actual_full_test_counts": parsed_counts,
        "native_wall_s": receipt["wall_s"],
        "native_process_invocations": receipt["native_process_invocations"],
        "progress_observations": [
            {"observed_utc": "2026-10-19T09:51:56.498710+00:00", "rows": 5, "first_step_wall_s": 0.879082389, "last_step": 5, "last_driver_wall_s": 6.161298558, "cohorts": 98320},
            {"observed_utc": "2026-10-19T09:52:22.571078+00:00", "rows": 13, "last_step": 13, "last_driver_wall_s": 29.46413632, "cohorts": 255632},
        ],
    }
    output = runtime / "NATIVE_ARTIFACT_READBACK_FINAL.json"
    with output.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps({"status": report["status"], "output": str(output), "sha256": digest(output), "monitor_rows": {file["path"]: file["rows"] for file in monitor_files}, "failed_checks": [key for key, passed in checks.items() if not passed]}))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
