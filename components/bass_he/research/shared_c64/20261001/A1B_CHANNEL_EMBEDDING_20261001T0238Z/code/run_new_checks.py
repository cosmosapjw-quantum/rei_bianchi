"""Run only the eight new A1b checks and preserve create-only evidence."""

import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone

import numpy as np


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_create(path, data):
    # Hard-link publication is atomic and refuses to replace an existing record.
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    try:
        with temporary.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def main():
    code = Path(__file__).resolve().parent
    evidence = code.parent / "evidence" / "newtest"
    evidence.mkdir(parents=True, exist_ok=True)
    log_path = evidence / "A1B_ALGEBRA_TEST_LOG.txt"
    result_path = evidence / "A1B_ALGEBRA_TEST_RESULT.json"
    if log_path.exists() or result_path.exists():
        raise SystemExit("Refusing to overwrite existing A1b evidence")
    command = [sys.executable, "-B", "-m", "unittest", "-v", "test_channel_embedding_algebra.py"]
    started = datetime.now(timezone.utc).isoformat()
    tic = time.perf_counter()
    run = subprocess.run(command, cwd=code, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    wall_seconds = time.perf_counter() - tic
    atomic_create(log_path, run.stdout)
    record = {
        "scope": "NEW_A1B_MATRIX_ALGEBRA_ONLY",
        "physical_collision_solver_executed": False,
        "unchanged_A1_tests_rerun": False,
        "command": command,
        "cwd": str(code),
        "started_at_utc": started,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "wall_seconds": wall_seconds,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "exit_code": run.returncode,
        "declared_test_count": 8,
        "unittest_summary_present": b"Ran 8 tests" in run.stdout,
        "status": "PASS" if run.returncode == 0 and b"Ran 8 tests" in run.stdout else "FAIL",
        "assertion_absolute_tolerance": 2e-12,
        "assertion_relative_tolerance": 0,
        "delta_rejection_tolerance": 1e-12,
        "input_file_identities": [
            {"path": p.name, "bytes": p.stat().st_size, "sha256": sha256(p)}
            for p in sorted(code.iterdir()) if p.is_file()
        ],
        "log_identity": {"path": log_path.name, "bytes": log_path.stat().st_size, "sha256": sha256(log_path)},
        "claim_ceiling": "implementation checks of supplied finite-dimensional algebra; no orbital/ETF selection or collision accuracy certification",
    }
    atomic_create(result_path, (json.dumps(record, indent=2) + "\n").encode())
    print(json.dumps({key: record[key] for key in ("status", "exit_code", "declared_test_count", "wall_seconds")}))
    return run.returncode


if __name__ == "__main__":
    raise SystemExit(main())
