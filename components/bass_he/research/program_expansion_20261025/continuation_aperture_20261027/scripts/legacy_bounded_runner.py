"""Bounded, recorded validation of the new interfaces; no historical science runs."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "evidence" / "validation"


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)


def utc():
    return datetime.now(timezone.utc).isoformat()


def run(scope, reason, selected_tests=(), verification_of=None):
    policy = json.loads((ROOT / "VALIDATION_CONTRACT.json").read_text())
    cap = policy["implementation_validation_cap"]
    OUT.mkdir(parents=True, exist_ok=True)
    ledger_path = OUT / "RESOURCE_LEDGER.json"
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {
        "unit_id": policy["unit_id"], "scope": "new implementation validation only",
        "attempts": [], "cpu_s": 0.0, "wall_s": 0.0,
        "HE101_START_count": 0, "historical_suite_replay_count": 0,
        "physical_campaign_START_count": 0, "repair_used": 0,
        "preparation_remote_model_IO_cost": "UNKNOWN_NOT_ZERO; outside measured test envelope",
        "end_to_end_cap_claimed": False,
    }
    if any(x["status"] == "STARTED" for x in ledger["attempts"]):
        raise RuntimeError("Incomplete START retained; diagnose before any further test start")
    previous = [x for x in ledger["attempts"] if x["scope"] == scope]
    if previous:
        if verification_of:
            addendum = json.loads((ROOT / "VALIDATION_ADDENDUM_01.json").read_text())
            used = ledger.get("verification_continuations", 0)
            if (not reason or verification_of != addendum["parent_attempt_id"] or
                    previous[-1]["id"] != verification_of or previous[-1]["status"] != "FAIL" or
                    list(selected_tests) != addendum["allowed_tests"] or
                    used >= addendum["max_continuation_starts"]):
                raise RuntimeError("Verification continuation exceeds the diagnosed addendum")
            ledger["verification_continuations"] = used + 1
        else:
            if not reason or ledger["repair_used"] >= cap["targeted_repair_reserve"]:
                raise RuntimeError("Repeated scope requires concrete diagnosis and remaining reserve")
            ledger["repair_used"] += 1
    elif verification_of:
        raise RuntimeError("Verification continuation needs an existing failed attempt")
    remaining_cpu = cap["cpu_s"] - ledger["cpu_s"]
    remaining_wall = cap["wall_s"] - ledger["wall_s"]
    if remaining_cpu <= 0 or remaining_wall <= 0:
        raise RuntimeError("Validation allocation exhausted")
    if not list((ROOT / scope).glob("test_*.py")):
        raise RuntimeError("No targeted test files; input preparation is incomplete")
    if selected_tests:
        if not reason:
            raise RuntimeError("Selected repair controls require the concrete diagnosis")
        command = [sys.executable, "-B", "-m", "unittest", "-v", *selected_tests]
        command_cwd = ROOT / scope
    else:
        command = [sys.executable, "-B", "-m", "unittest", "discover", "-s", str(ROOT / scope), "-p", "test_*.py", "-v"]
        command_cwd = ROOT
    attempt_id = f"{len(ledger['attempts']) + 1:02d}_{scope}"
    target = OUT / attempt_id
    target.mkdir()
    inputs = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted((ROOT / scope).rglob("*")) if p.is_file() and "__pycache__" not in p.parts}
    for p in sorted((ROOT / "sources").rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            inputs[str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
    record = {"id": attempt_id, "scope": scope, "status": "STARTED", "start_utc": utc(),
              "command": command, "command_cwd": str(command_cwd), "source_sha256": inputs,
              "repair_reason": reason, "selected_tests": list(selected_tests), "verification_of": verification_of,
              "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "contract_sha256": hashlib.sha256((ROOT / "VALIDATION_CONTRACT.json").read_bytes()).hexdigest(),
              "remaining_before": {"cpu_s": remaining_cpu, "wall_s": remaining_wall},
              "child_cpu_limit_s": min(3, max(1, math.floor(remaining_cpu))),
              "child_wall_limit_s": min(10, remaining_wall), "memory_bytes": cap["memory_bytes"]}
    ledger["attempts"].append(record)
    save(ledger_path, ledger)
    save(target / "START.json", record)

    def limits():
        resource.setrlimit(resource.RLIMIT_AS, (cap["memory_bytes"], cap["memory_bytes"]))
        limit = record["child_cpu_limit_s"]
        resource.setrlimit(resource.RLIMIT_CPU, (limit, limit))

    env = os.environ.copy()
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        env[name] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    cpu0, wall0 = time.process_time(), time.monotonic()
    children0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    timed_out = False
    launch_error = None
    code = None
    stdout = stderr = b""
    try:
        child = subprocess.Popen(command, cwd=command_cwd, env=env, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, start_new_session=True, preexec_fn=limits)
        try:
            stdout, stderr = child.communicate(timeout=record["child_wall_limit_s"])
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(child.pid, signal.SIGKILL)
            stdout, stderr = child.communicate()
        code = child.returncode
    except (OSError, subprocess.SubprocessError) as exc:
        launch_error = repr(exc)
    children1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    child_cpu = children1.ru_utime + children1.ru_stime - children0.ru_utime - children0.ru_stime
    parent_cpu = time.process_time() - cpu0
    wall = time.monotonic() - wall0
    (target / "stdout.txt").write_bytes(stdout)
    (target / "stderr.txt").write_bytes(stderr)
    ledger["cpu_s"] += parent_cpu + child_cpu
    ledger["wall_s"] += wall
    overshoot = ledger["cpu_s"] > cap["cpu_s"] or ledger["wall_s"] > cap["wall_s"]
    record.update({"status": "PASS" if code == 0 and not timed_out and not launch_error and not overshoot else "FAIL",
                   "end_utc": utc(), "returncode": code, "timed_out": timed_out,
                   "launch_error": launch_error, "child_cpu_s": child_cpu, "parent_cpu_s": parent_cpu,
                   "wall_s": wall, "cumulative_cap_overshoot": overshoot,
                   "stdout_sha256": hashlib.sha256(stdout).hexdigest(), "stderr_sha256": hashlib.sha256(stderr).hexdigest()})
    save(target / "FINISH.json", record)
    save(ledger_path, ledger)
    print(json.dumps({"attempt": record, "cumulative_cpu_s": ledger["cpu_s"], "cumulative_wall_s": ledger["wall_s"]}, indent=2))
    sys.stdout.write(stdout.decode(errors="replace"))
    sys.stderr.write(stderr.decode(errors="replace"))
    return 0 if record["status"] == "PASS" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("scope", choices=("species", "pair_source", "exchange"))
    parser.add_argument("--repair-reason", default=None)
    parser.add_argument("--test-name", action="append", default=[])
    parser.add_argument("--verification-of", default=None)
    args = parser.parse_args()
    raise SystemExit(run(args.scope, args.repair_reason, args.test_name, args.verification_of))
