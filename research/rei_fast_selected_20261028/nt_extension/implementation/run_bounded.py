"""One-attempt CPU, wall and address-space wrapper for saved n/T presentation."""

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
LIMITS = {"check": (1, 10), "plot": (2, 30), "plot_repair": (1, 30)}
MEMORY_BYTES = 3 * 1024**3


def limit_child(cpu_s: int) -> None:
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_s, cpu_s))
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_BYTES, MEMORY_BYTES))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=LIMITS)
    args = parser.parse_args()
    phase = args.phase
    cpu_s, wall_s = LIMITS[phase]
    command = [sys.executable, str(Path(__file__).with_name("phase_check.py" if phase == "check" else "plot_saved.py"))]
    OUT.mkdir(parents=True, exist_ok=True)
    marker = OUT / f"{phase.upper()}_ATTEMPT_STARTED.json"
    try:
        fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise SystemExit("attempt already started; no automatic retry") from exc
    with os.fdopen(fd, "w") as stream:
        json.dump({"command": command, "cpu_limit_s": cpu_s, "wall_limit_s": wall_s, "address_space_limit_bytes": MEMORY_BYTES}, stream, indent=2)
        stream.write("\n")
    child_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    own_before = resource.getrusage(resource.RUSAGE_SELF)
    start = time.monotonic()
    env = os.environ.copy()
    env.update({"OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"})
    status, code, stdout, stderr = "LAUNCH_ERROR", None, "", ""
    try:
        completed = subprocess.run(command, cwd=UNIT, env=env, text=True, capture_output=True,
                                   timeout=wall_s, preexec_fn=lambda: limit_child(cpu_s))
        code, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
        status = "COMPLETED" if code == 0 else "FAILED"
    except subprocess.TimeoutExpired as exc:
        status = "WALL_LIMIT"
        stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    except Exception as exc:
        stderr = repr(exc)
    child_after = resource.getrusage(resource.RUSAGE_CHILDREN)
    own_after = resource.getrusage(resource.RUSAGE_SELF)
    (OUT / f"{phase.upper()}_attempt_stdout.txt").write_text(stdout, encoding="utf-8")
    (OUT / f"{phase.upper()}_attempt_stderr.txt").write_text(stderr, encoding="utf-8")
    receipt = {
        "phase": phase, "status": status, "returncode": code,
        "child_cpu_s": child_after.ru_utime + child_after.ru_stime - child_before.ru_utime - child_before.ru_stime,
        "wrapper_cpu_s_observed_after_start": own_after.ru_utime + own_after.ru_stime - own_before.ru_utime - own_before.ru_stime,
        "wall_s": time.monotonic() - start, "cpu_limit_s": cpu_s, "wall_limit_s": wall_s,
        "address_space_limit_bytes": MEMORY_BYTES,
    }
    (OUT / f"{phase.upper()}_ATTEMPT_RESULT.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if status != "COMPLETED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
