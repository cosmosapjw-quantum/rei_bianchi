"""Single-attempt bounded presentation run, to be used only after authorization."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

UNIT = Path(__file__).resolve().parents[1]
OUT = UNIT / "outputs"
CASE = "grid044_M4_nominal"
ADDRESS_SPACE_LIMIT_BYTES = 3 * 1024**3


def bound_child(cpu_limit):
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
    resource.setrlimit(resource.RLIMIT_AS, (ADDRESS_SPACE_LIMIT_BYTES, ADDRESS_SPACE_LIMIT_BYTES))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tests-only", action="store_true")
    args = parser.parse_args()
    own_before = resource.getrusage(resource.RUSAGE_SELF)
    label = "TEST" if args.tests_only else "PLOT"
    cpu_limit, wall_limit = (1, 10) if args.tests_only else (3, 30)
    OUT.mkdir(parents=True, exist_ok=True)
    marker = OUT / f"{label}_ATTEMPT_STARTED.json"
    try:
        fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise SystemExit("bounded attempt already started; no automatic rerun") from exc
    command = ([sys.executable, "-m", "unittest", "discover", "-s", str(Path(__file__).parent),
                "-p", "test_projection.py"] if args.tests_only else
               [sys.executable, str(Path(__file__).with_name("project_saved.py")),
                "--case", CASE, "--output-dir", str(OUT)])
    with os.fdopen(fd, "w") as f:
        json.dump({"command": command, "cpu_limit_s": cpu_limit,
                   "wall_limit_s": wall_limit,
                   "address_space_limit_bytes": ADDRESS_SPACE_LIMIT_BYTES}, f, indent=2)
        f.write("\n")
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.monotonic()
    status = "COMPLETED"
    try:
        child_env = os.environ.copy()
        child_env["OPENBLAS_NUM_THREADS"] = "1"
        child_env["OMP_NUM_THREADS"] = "1"
        result = subprocess.run(command, cwd=UNIT, text=True, capture_output=True,
                                timeout=wall_limit, preexec_fn=lambda: bound_child(cpu_limit), env=child_env)
        code = result.returncode
        stdout, stderr = result.stdout, result.stderr
        if code != 0:
            status = "FAILED"
    except subprocess.TimeoutExpired as exc:
        status, code = "WALL_LIMIT", None
        stdout = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    except Exception as exc:
        status, code, stdout, stderr = "LAUNCH_ERROR", None, "", repr(exc)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    (OUT / f"{label}_attempt_stdout.txt").write_text(stdout)
    (OUT / f"{label}_attempt_stderr.txt").write_text(stderr)
    own_after = resource.getrusage(resource.RUSAGE_SELF)
    receipt = {"status": status, "returncode": code,
               "child_cpu_s": after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime,
               "wrapper_cpu_s_observed_after_start": own_after.ru_utime + own_after.ru_stime - own_before.ru_utime - own_before.ru_stime,
               "wall_s": time.monotonic() - start, "case": None if args.tests_only else CASE,
               "cpu_limit_s": cpu_limit, "wall_limit_s": wall_limit,
               "address_space_limit_bytes": ADDRESS_SPACE_LIMIT_BYTES}
    (OUT / f"{label}_ATTEMPT_RESULT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))
    if status != "COMPLETED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
