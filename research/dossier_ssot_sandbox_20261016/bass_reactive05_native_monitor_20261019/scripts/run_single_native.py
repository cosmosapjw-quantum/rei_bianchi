#!/usr/bin/env python3
"""Record the single coordinated BR05 Nt16/r8 history and monitor sidecar.

This wrapper never retries a driver invocation.  An exclusive intent record
prevents an accidental second execution under the same output name.
"""

import argparse
import csv
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import time


CASE_NAME = "ap_n16_r8"
NORMAL_ARGS = [
    "SIGNED_MINUS", "121", "16", "0", "8e12", "false", "false",
    "2", "4", "1e-12", "8",
]
HEADER = (
    "case,grid,nsteps,t0,duration,split,frozen,step,time_s,T_K,DII_m3,"
    "photons_com3,absorbed_com3,HI,HeI,HeII,DI,source_count,source_energy,"
    "geom_work,q2,H_perp,H_parallel,volume,cohorts,maxN,maxE,maxW,RR,CX_abs,"
    "FF,CMB_abs,hits,misses,cache_size,birth_gl,opacity,cx_rtol,cx_atol,"
    "threshold_crossings,wall_s,birth_mode,refinement,thermal_change_com3,"
    "chemical_change_com3,photo_energy_com3,survivor_age_com_s,"
    "survivor_age2_com_s2,photon_energy_com3,gas_thermal_com3,gas_binding_com3,"
    "escaped_com3,cmb_reservoir_com3,initial_total_energy_com3"
).split(",")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sync_directory(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_json_exclusive(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    sync_directory(path.parent)


def source_hashes(root):
    parent_contract = root / "contracts" / "PARENT_INPUT_SHA256.json"
    parent_paths = json.loads(parent_contract.read_text())
    paths = {root / path for path in parent_paths}
    paths.update((root / "crate").rglob("*.rs"))
    paths.update([root / "br05" / "Cargo.toml", root / "br05" / "Cargo.lock",
                  parent_contract])
    return {str(path.relative_to(root)): sha256(path) for path in sorted(paths)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--unit-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--monitor-output", type=Path, required=True)
    parser.add_argument("--expected-binary-sha256", required=True)
    parser.add_argument("--timeout", type=float, default=600.0)
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("timeout must be finite and positive")

    binary = args.binary.resolve(strict=True)
    root = args.unit_root.resolve(strict=True)
    output = args.output.resolve()
    monitor_output = args.monitor_output.resolve()
    if not binary.is_file() or not os.access(binary, os.X_OK):
        parser.error("binary must be an executable file")
    binary_hash = sha256(binary)
    if binary_hash != args.expected_binary_sha256:
        parser.error("binary SHA256 does not match the coordinated build")
    if monitor_output.exists():
        parser.error("monitor output must be a new directory")
    output.mkdir(parents=True, exist_ok=True)
    target = output / (CASE_NAME + ".csv")
    receipt = output / (CASE_NAME + ".json")
    stderr_target = output / (CASE_NAME + ".stderr")
    live = output / (CASE_NAME + ".running.csv")
    live_err = output / (CASE_NAME + ".running.stderr")
    intent = output / (CASE_NAME + ".execution_intent.json")
    for path in [target, receipt, stderr_target, live, live_err, intent]:
        if path.exists():
            parser.error(f"refusing a repeated or overlapping execution: {path}")

    code_before = source_hashes(root)
    parent_expected = json.loads((root / "contracts" / "PARENT_INPUT_SHA256.json").read_text())
    parent_mismatches = [path for path, expected in parent_expected.items()
                         if code_before[path] != expected]
    if parent_mismatches:
        parser.error(f"inherited input identity differs: {parent_mismatches}")
    wrapper_hash = sha256(Path(__file__).resolve())
    command = [str(binary), *NORMAL_ARGS, str(monitor_output)]
    started_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    write_json_exclusive(intent, {
        "name": CASE_NAME,
        "status": "SINGLE_DRIVER_EXECUTION_INTENT_RECORDED",
        "started_utc": started_utc,
        "command": command,
        "normal_arguments": NORMAL_ARGS,
        "additional_monitor_arguments": [str(monitor_output)],
        "binary_sha256": binary_hash,
        "source_sha256": code_before,
        "parent_inputs_checked": len(parent_expected),
        "parent_inputs_match_before": True,
        "wrapper_sha256": wrapper_hash,
        "wall_budget_s": args.timeout,
        "retry_policy": "Never retry automatically; preserve this intent record.",
    })
    print(json.dumps({"name": CASE_NAME, "status": "STARTING_ONCE", "wall_budget_s": args.timeout}), flush=True)

    start = time.monotonic()
    timed_out = False
    launch_error = None
    with live.open("xb") as stdout, live_err.open("xb") as stderr:
        try:
            done = subprocess.run(command, stdout=stdout, stderr=stderr,
                                  timeout=args.timeout, check=False)
            code = done.returncode
        except subprocess.TimeoutExpired:
            timed_out, code = True, -9
        except OSError as error:
            code = None
            launch_error = repr(error)
        stdout.flush()
        os.fsync(stdout.fileno())
        stderr.flush()
        os.fsync(stderr.fileno())
    wall = time.monotonic() - start
    raw_error = live_err.read_text()
    rows = []
    parse_error = None
    try:
        with live.open() as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != HEADER:
                raise ValueError("stdout header differs from the original 54-field contract")
            rows = list(reader)
            if any(None in row or any(value is None for value in row.values()) for row in rows):
                raise ValueError("stdout contains an incomplete or extra-field row")
            if any(int(row["step"]) != i + 1 for i, row in enumerate(rows)):
                raise ValueError("accepted-step numbering is inconsistent")
    except (ValueError, csv.Error) as error:
        parse_error = repr(error)

    if timed_out:
        status, failure = "RESOURCE_LIMIT_WALL", "BOUNDED_WALL_BUDGET_EXHAUSTED"
    elif launch_error:
        status, failure = "LAUNCH_FAILED", "RUNTIME_LAUNCH_FAILURE"
    elif code == 2 and "Cx(WorkLimit)" in raw_error:
        status, failure = "RESOURCE_LIMIT_CX", "NUMERICAL_WORK_BUDGET_EXHAUSTED_NOT_PHYSICAL_NO_SOLUTION"
    elif code == 0 and len(rows) == 16 and parse_error is None:
        status, failure = "COMPLETED", None
    else:
        status, failure = "EXECUTION_FAILED", "NONZERO_EXIT_OR_INCOMPLETE_ROWS"

    raw_hash_before = sha256(live)
    os.replace(live, target)
    os.replace(live_err, stderr_target)
    sync_directory(output)
    raw_hash_after = sha256(target)
    code_after = source_hashes(root)
    binary_after = sha256(binary)
    provenance_unchanged = code_before == code_after and binary_hash == binary_after
    if raw_hash_before != raw_hash_after or not provenance_unchanged:
        status, failure = "ARTIFACT_IDENTITY_FAILURE", "SOURCE_BINARY_OR_OUTPUT_IDENTITY_CHANGED"

    monitor_files = []
    if monitor_output.exists():
        for path in sorted(monitor_output.rglob("*")):
            if path.is_file():
                with path.open("rb") as stream:
                    os.fsync(stream.fileno())
                monitor_files.append({
                    "path": str(path.relative_to(monitor_output)),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                })
        sync_directory(monitor_output)

    result = {
        "name": CASE_NAME,
        "command": command,
        "exit_code": code,
        "wall_s": wall,
        "rows": len(rows),
        "planned_rows": 16,
        "status": status,
        "failure_class": failure,
        "stderr": raw_error,
        "binary_sha256": binary_hash,
        "binary_sha256_after": binary_after,
        "source_sha256": code_before,
        "parent_inputs_checked": len(parent_expected),
        "parent_inputs_match_before": True,
        "parent_inputs_match_after": all(code_after[path] == expected
                                          for path, expected in parent_expected.items()),
        "wrapper_sha256": wrapper_hash,
        "source_unchanged_during_run": code_before == code_after,
        "source_hashes_after_if_changed": None if code_before == code_after else code_after,
        "csv_sha256": raw_hash_after,
        "csv_sha256_before_rename": raw_hash_before,
        "final": rows[-1] if rows else None,
        "started_utc": started_utc,
        "completed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "launch_error": launch_error,
        "parse_error": parse_error,
        "physics": "Original BR03 evolution operations selected by existing arguments; instrumented driver supplies a read-only monitor sidecar. Physical parity is supported by separate preexecution tests.",
        "monitor": {
            "mode": "ON",
            "output_directory": str(monitor_output),
            "additional_arguments": [str(monitor_output)],
            "status": "OUTPUTS_RECORDED_PENDING_INDEPENDENT_AUDIT" if monitor_files else "NO_FILES_RECORDED",
            "files": monitor_files,
        },
        "native_process_invocations": 1,
        "retry_policy": "No automatic retry; execution intent remains preserved.",
    }
    pending = output / (CASE_NAME + ".receipt_pending.json")
    write_json_exclusive(pending, result)
    os.replace(pending, receipt)
    sync_directory(output)
    print(json.dumps({key: result[key] for key in [
        "name", "status", "rows", "wall_s", "csv_sha256", "binary_sha256",
    ]}), flush=True)
    return 0 if status == "COMPLETED" and monitor_files else 2


if __name__ == "__main__":
    raise SystemExit(main())
