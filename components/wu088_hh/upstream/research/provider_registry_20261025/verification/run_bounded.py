"""Measured, append-only lightweight implementation validation runner."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parents[1]


def limits():
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2, 512 * 1024**2))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--attempt", required=True)
    p.add_argument("command", nargs=argparse.REMAINDER)
    args = p.parse_args()
    if not args.attempt.replace("_", "").isalnum():
        raise ValueError("SIMPLE_ATTEMPT_IDENTIFIER_REQUIRED")
    dest = BASE / "raw" / args.attempt
    if dest.exists():
        raise ValueError("ATTEMPT_ALREADY_EXISTS_NO_REPLAY")
    dest.mkdir(parents=True)
    cmd = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not cmd:
        raise ValueError("EXPLICIT_COMMAND_REQUIRED")
    hashes = {str(f.relative_to(BASE)): hashlib.sha256(f.read_bytes()).hexdigest()
              for f in BASE.rglob("*.py") if "__pycache__" not in f.parts}
    request = {"command": cmd, "cwd": str(BASE), "code_sha256": hashes,
               "python": platform.python_version(), "cpu_cap_s": 30, "wall_cap_s": 120,
               "memory_MiB": 512, "workers": 1, "threads": 1}
    (dest / "REQUEST.json").write_text(json.dumps(request, indent=2) + "\n")
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.monotonic()
    env = dict(os.environ)
    env.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONDONTWRITEBYTECODE": "1"})
    with (dest / "stdout.txt").open("w") as out, (dest / "stderr.txt").open("w") as err:
        child = subprocess.Popen(cmd, cwd=BASE, env=env, stdout=out, stderr=err, preexec_fn=limits)
        timed_out = False
        try:
            code = child.wait(timeout=120)
        except subprocess.TimeoutExpired:
            timed_out = True
            child.kill()
            code = child.wait()
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt = {**request, "exit_code": code, "timed_out": timed_out,
               "cpu_s": after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime,
               "wall_s": time.monotonic() - start, "max_RSS_KiB": after.ru_maxrss,
               "new_rate_evaluations": 0, "new_IVP": 0, "historical_science_replays": 0,
               "stdout_sha256": hashlib.sha256((dest / "stdout.txt").read_bytes()).hexdigest(),
               "stderr_sha256": hashlib.sha256((dest / "stderr.txt").read_bytes()).hexdigest()}
    (dest / "RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in ("exit_code", "cpu_s", "wall_s", "max_RSS_KiB", "timed_out")}))
    print((dest / "stdout.txt").read_text())
    if code:
        print((dest / "stderr.txt").read_text(), file=sys.stderr)
    raise SystemExit(0 if code == 0 else 1)


if __name__ == "__main__":
    main()
