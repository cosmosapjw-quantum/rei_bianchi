#!/usr/bin/env python3
"""Compare a separate source restoration and its raw outputs to the executed unit.

This checker reads both sides and only writes the requested report. It excludes
explicit execution/cache fields; every remaining native CSV field is exact.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import re

CASES = ["off_gl2_n32", "ap_n32_r2", "ap_n32_r4", "ap_n32_r2_plus", "ap_cx_worklimit", "ap_n32_r2_spectrum"]
IGNORED_NATIVE_FIELDS = ["wall_s", "hits", "misses", "cache_size"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(path, allow_empty=False):
    if allow_empty and path.stat().st_size == 0:
        return [], []
    with path.open() as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    if fields is None or len(fields) != len(set(fields)):
        raise ValueError(f"missing or duplicate headers: {path}")
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError(f"malformed data row: {path}")
    return fields, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit", type=Path, required=True)
    parser.add_argument("--fresh-source", type=Path, required=True)
    parser.add_argument("--initial-run", type=Path, required=True)
    parser.add_argument("--native-run", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    output = {"status": "PENDING", "source": [], "tests": {}, "frozen": [], "native": [], "failures": []}
    for path in sorted(args.fresh_source.rglob("*")):
        if not path.is_file():
            continue
        name = path.relative_to(args.fresh_source).as_posix()
        if not (name.startswith(("crate/", "ap/", "donor_input/", "scripts/")) or name == "contracts/PARENT_97_SOURCE_SHA256.json"):
            continue
        reference = args.unit / name
        actual = sha(path)
        expected = sha(reference)
        equal = actual == expected
        output["source"].append({"path": name, "fresh_sha256": actual, "main_sha256": expected, "byte_equal": equal})
        if not equal:
            output["failures"].append(f"source bytes differ: {name}")
    completed = json.loads((args.initial_run / "RUN_COMPLETION.json").read_text())
    initial_log = args.initial_run / "logs/all_rust_tests.log"
    counts = [tuple(map(int, m)) for m in re.findall(r"test result: ok\. (\d+) passed; (\d+) failed;", initial_log.read_text())]
    passed, failed = sum(x[0] for x in counts), sum(x[1] for x in counts)
    clippy_command = json.loads((args.initial_run / "logs/strict_clippy.command.json").read_text())["argv"]
    if (passed, failed) != (209, 0) or "--all-targets" not in clippy_command or "warnings" not in clippy_command or "-D" not in clippy_command:
        output["failures"].append("full tests or strict Clippy invocation differs from the required fresh gate")
    if completed["status"] != "REQUESTED_REPRODUCTION_STAGES_COMPLETED":
        output["failures"].append("initial fresh runner did not complete")
    output["tests"] = {"passed": passed, "failed": failed, "all_targets": True,
                       "rust_tests_log_sha256": sha(initial_log), "strict_clippy_argv": clippy_command,
                       "strict_clippy_log_sha256": sha(args.initial_run / "logs/strict_clippy.log"),
                       "completion_receipt_sha256": sha(args.initial_run / "RUN_COMPLETION.json")}
    for path in sorted((args.initial_run / "frozen").glob("*.csv")):
        name = path.name
        reference = args.unit / "evidence/frozen" / name
        _, rows = table(path)
        actual, expected = sha(path), sha(reference)
        equal = actual == expected
        output["frozen"].append({"file": name, "rows": len(rows), "fresh_sha256": actual, "main_sha256": expected, "byte_equal": equal})
        if not equal:
            output["failures"].append(f"frozen/scalar bytes differ: {name}")
    if len(output["frozen"]) != 4:
        output["failures"].append("incomplete frozen/scalar output set")
    for name in CASES:
        fresh = args.native_run / "native" / name
        reference = args.unit / "evidence/native" / name
        ajson = json.loads(fresh.with_suffix(".json").read_text())
        bjson = json.loads(reference.with_suffix(".json").read_text())
        def expected_empty(record):
            return record.get("status") == "RESOURCE_LIMIT_CX" and record.get("rows") == 0 and record.get("exit_code") == 2
        afields, arows = table(fresh.with_suffix(".csv"), expected_empty(ajson))
        bfields, brows = table(reference.with_suffix(".csv"), expected_empty(bjson))
        if afields != bfields or len(arows) != len(brows):
            output["failures"].append(f"header or row count differs: {name}")
        scientific = [field for field in afields if field not in IGNORED_NATIVE_FIELDS]
        mismatches = []
        for index, (a, b) in enumerate(zip(arows, brows), 1):
            for field in scientific:
                if a[field] != b[field]:
                    mismatches.append({"row": index, "field": field, "fresh": a[field], "main": b[field]})
        keys = ["status", "rows", "exit_code", "failure_class"]
        outcome_equal = all(ajson.get(key) == bjson.get(key) for key in keys)
        record = {"name": name, "fresh_rows": len(arows), "main_rows": len(brows),
                  "compared_fields": scientific, "excluded_fields": IGNORED_NATIVE_FIELDS,
                  "compared_cells": len(arows) * len(scientific), "mismatches": mismatches,
                  "outcome_equal": outcome_equal,
                  "fresh_outcome": {key: ajson.get(key) for key in keys},
                  "main_outcome": {key: bjson.get(key) for key in keys},
                  "fresh_csv_sha256": sha(fresh.with_suffix(".csv")), "main_csv_sha256": sha(reference.with_suffix(".csv")),
                  "fresh_binary_sha256": ajson["binary_sha256"], "main_binary_sha256": bjson["binary_sha256"]}
        output["native"].append(record)
        if mismatches or not outcome_equal:
            output["failures"].append(f"native data or outcome differs: {name}")
    native_receipt = args.native_run / "RUN_COMPLETION.json"
    if not native_receipt.exists():
        output["failures"].append("native runner has not committed its completion receipt")
    else:
        output["native_completion_sha256"] = sha(native_receipt)
    output["status"] = "PASS_SCOPED_FRESH_REPRODUCTION" if not output["failures"] else "FAIL_OR_INCOMPLETE_FRESH_REPRODUCTION"
    output["summary"] = {"source_files": len(output["source"]), "rust_tests_passed": passed,
                         "native_cases": len(output["native"]), "native_rows": sum(x["fresh_rows"] for x in output["native"]),
                         "compared_scientific_cells": sum(x["compared_cells"] for x in output["native"]),
                         "scientific_mismatches": sum(len(x["mismatches"]) for x in output["native"])}
    args.report.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"status": output["status"], **output["summary"], "failures": output["failures"]}, indent=2))
    if output["failures"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
