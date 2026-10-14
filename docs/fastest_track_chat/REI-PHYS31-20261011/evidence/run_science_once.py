#!/usr/bin/env python3
"""Single explicitly requested PHYS31 process with detached execution evidence.

This driver performs no physical arithmetic and never retries. Its unique
record directory preserves an attempted invocation, stdout, stderr and exit.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys
import time


def identity(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": sha256(data).hexdigest()}


def write_json(path, data):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--record-dir", required=True)
    parser.add_argument("--kind", choices=["first", "replay"], required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    output = Path(args.output).resolve()
    records = Path(args.record_dir).resolve()
    if records.exists() or output.exists():
        raise FileExistsError("An execution record or result already exists; no retry")
    frozen_path = root / "contributions/numerics/PREEXECUTION_FREEZE.json"
    frozen = json.loads(frozen_path.read_text())
    relative_files = sorted(set(frozen["files"]) | {"contributions/numerics/PREEXECUTION_FREEZE.json"})
    before = {relative: identity(root / relative) for relative in relative_files}
    for relative, expected in frozen["files"].items():
        if before[relative] != expected:
            raise ValueError("Pre-invocation frozen-byte mismatch: " + relative)
    records.mkdir(parents=True)
    entry = root / "contributions/numerics/quartic_profile_split.py"
    argv = ["python3", "contributions/numerics/quartic_profile_split.py", "--output", str(output.relative_to(root))]
    started = datetime.now(timezone.utc).isoformat()
    write_json(records / "ATTEMPT_STARTED.json", {"task": "REI-PHYS31-20261011", "kind": args.kind, "started_utc": started, "argv": argv, "cwd": str(root), "automatic_retry": False})
    begin = time.monotonic()
    timed_out = False
    try:
        process = subprocess.run(argv, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60, check=False)
        stdout, stderr, exit_code = process.stdout, process.stderr, process.returncode
    except subprocess.TimeoutExpired as error:
        timed_out = True
        stdout, stderr, exit_code = error.stdout or b"", error.stderr or b"", 124
    ended = datetime.now(timezone.utc).isoformat()
    wall_seconds = time.monotonic() - begin
    (records / "stdout.txt").write_bytes(stdout)
    (records / "stderr.txt").write_bytes(stderr)
    after = {relative: identity(root / relative) for relative in relative_files}
    raw = json.loads(output.read_text()) if output.is_file() else None
    passed = exit_code == 0 and not timed_out and before == after and raw is not None and raw.get("status") == "PASS_SCOPED"
    receipt = {"task": "REI-PHYS31-20261011", "kind": args.kind, "status": "PASS_SCOPED" if passed else "FAIL", "argv": argv, "cwd": str(root), "started_utc": started, "ended_utc": ended, "wall_seconds": wall_seconds, "timeout_seconds": 60, "timed_out": timed_out, "exit_code": exit_code, "new_scientific_main_invocations": 1, "automatic_retries": 0, "python_version": platform.python_version(), "raw_result": {"path": str(output), **identity(output)} if output.is_file() else None, "stdout": identity(records / "stdout.txt"), "stderr": identity(records / "stderr.txt"), "runtime_files_before": before, "runtime_files_after": after, "runtime_bytes_preserved": before == after, "actual_summary": raw.get("summary") if raw else None, "actual_counts": raw.get("actual_counts") if raw else None, "independent_physical_data_credit": 0}
    write_json(records / "EXECUTION.json", receipt)
    print(json.dumps({key: receipt[key] for key in ["task", "kind", "status", "started_utc", "ended_utc", "wall_seconds", "exit_code", "runtime_bytes_preserved", "actual_summary", "actual_counts"]}, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
