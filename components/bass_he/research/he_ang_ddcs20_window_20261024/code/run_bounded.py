"""Small sequential scientific runner: immutable STARTs, measured costs, hard caps.

Run only the predeclared tests -> actual_analysis -> plot sequence. One optional
repair invocation requires an explicit root instruction reference. No retries
after a failed/overshooting run are automatic.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tempfile
import time

UNIT = Path(__file__).resolve().parents[1]
EXEC = UNIT / "evidence/execution"
LEDGER = EXEC / "RESOURCE_LEDGER.json"
COMMANDS = {"tests": "test_ddcs_window.py", "actual_analysis": "run_analysis.py", "plot": "plot_results.py"}
R6_THEORY = "21265d10608c3626002b714f18039af61d31c4bb1b538a1797811f04577e3036"
R6_CONTRACT = "72972199b9886740f9a9b1ca0275adda59b29fdad005297b9b806b9261b86b8f"


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(path):
    b = path.read_bytes()
    return {"bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}


def atomic(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(obj, f, indent=2, allow_nan=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def cpu(usage):
    return usage.ru_utime + usage.ru_stime


def main():
    p = argparse.ArgumentParser()
    p.add_argument("kind", choices=COMMANDS)
    p.add_argument("--repair-authority", help="root's explicit bounded repair instruction reference; consumes the only reserve")
    args = p.parse_args()
    EXEC.mkdir(parents=True, exist_ok=True)
    # A lock prevents concurrent run allocation; a stale lock is deliberately
    # preserved for root diagnosis instead of silently removing unknown costs.
    lock = EXEC / "RUN.lock"
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    launched = False
    completed = False
    try:
        contract = json.loads((UNIT / "CONTRACT.json").read_text())
        caps = contract["resource_budget"]
        if digest(UNIT / "THEORY_KO.md")["sha256"] != R6_THEORY or digest(UNIT / "CONTRACT.json")["sha256"] != R6_CONTRACT:
            raise RuntimeError("R6-reviewed immutable contract/theory changed; return to root")
        review = json.loads((UNIT / "evidence/review/R6_REVIEW.json").read_text())
        if review.get("status") != "PASS":
            raise RuntimeError("R6 PASS required")
        for start in EXEC.glob("*.START.json"):
            prefix = start.name[:-len(".START.json")]
            if not (EXEC / (prefix + ".FINISH.json")).exists() and not (EXEC / (prefix + ".FAIL.json")).exists():
                raise RuntimeError("UNKNOWN_NOT_ZERO interrupted START; do not replay")
        if LEDGER.exists():
            ledger = json.loads(LEDGER.read_text())
        else:
            ledger = {"unit_id": contract["unit_id"], "created_utc": stamp(), "cumulative_cpu_s": 0.0, "cumulative_wall_s": 0.0, "attempts": [],
                      "allocation": caps, "prior_Hex_costs_not_reset_or_consumed": {"cpu_s": caps["prior_hex_cpu_seconds"], "wall_s": caps["prior_hex_wall_seconds"], "ledger_sha256": caps["prior_hex_ledger_sha256"]},
                      "inherited_nontransferable": {"source_path": "../he_ang_source_hex_20261024/CONTRACT.json", "source_field": "inherited_budget", "HEANG_CONTRACT_cpu_s": 0.5922019999999999, "HEANG_CONTRACT_wall_s": 0.5168205270092585, "prior_remaining_cpu_s": 9.407798, "prior_remaining_wall_s": 29.48317947299074, "transferable": False, "HE_X1_failed_prelaunch_cpu": "UNKNOWN_NOT_ZERO", "HE38": "preserved nontransferable", "D10": "UNKNOWN_NOT_ZERO", "not_combined_with_current_allocation": True},
                      "preexisting_unknown_cost": "UNKNOWN_NOT_ZERO; separate unknown remote costs are not a complete grand total", "requested_model": "gpt-6.1-sol", "requested_reasoning_effort": "high", "observed_runtime_model": "not independently observable"}
        attempts = ledger["attempts"]
        if len(attempts) >= 4:
            raise RuntimeError("invocation cap exhausted")
        if any(a["status"] != "FINISH" for a in attempts) and not args.repair_authority:
            raise RuntimeError("previous failure/overshoot requires root bounded repair authority")
        if args.repair_authority:
            if any(a.get("repair_authority") for a in attempts):
                raise RuntimeError("repair reserve already consumed")
            reserve_cpu = reserve_wall = 0
        else:
            successful = [a["kind"] for a in attempts if a["status"] == "FINISH" and not a.get("repair_authority")]
            if len(successful) >= 3 or args.kind != ["tests", "actual_analysis", "plot"][len(successful)]:
                raise RuntimeError("planned order is tests -> actual_analysis -> plot; no replay")
            reserve_cpu, reserve_wall = 6, 20
        remain_cpu = 20 - ledger["cumulative_cpu_s"]
        remain_wall = 60 - ledger["cumulative_wall_s"]
        if remain_cpu < 6 + reserve_cpu or remain_wall < 20 + reserve_wall:
            raise RuntimeError("remaining budget cannot retain planned cap plus repair reserve")
        # RLIMIT_CPU and AS are kernel-enforced child limits; elapsed wall is
        # parent-enforced and all launched descendants share a process group.
        def limits():
            os.setsid()
            resource.setrlimit(resource.RLIMIT_CPU, (6, 6))
            resource.setrlimit(resource.RLIMIT_AS, (1073741824, 1073741824))
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        runid = f"{len(attempts) + 1:02d}_{args.kind}"
        for suffix in ("START.json", "FINISH.json", "FAIL.json", "stdout.txt", "stderr.txt"):
            if (EXEC / f"{runid}.{suffix}").exists():
                raise RuntimeError("run ID exists; no silent overwrite")
        env = os.environ.copy()
        env.update(caps["environment"])
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        freeze_paths = [UNIT / "THEORY_KO.md", UNIT / "CONTRACT.json", *sorted((UNIT / "source").glob("*")), *sorted((UNIT / "code").glob("*.py"))]
        source_freeze = {str(x.relative_to(UNIT)): digest(x) for x in freeze_paths if x.is_file()}
        record = {"run_id": runid, "kind": args.kind, "command": [sys.executable, "-B", "code/" + COMMANDS[args.kind]], "cwd": str(UNIT), "started_utc": stamp(), "status": "START",
                  "caps": {"cpu_s": 6, "wall_s": 20, "address_space_bytes": 1073741824, "threads": 1}, "environment_overrides": caps["environment"],
                  "source_freeze": source_freeze, "remaining_before_cpu_s": remain_cpu, "remaining_before_wall_s": remain_wall,
                  "repair_authority": args.repair_authority, "interrupted_START_accounting": "UNKNOWN_NOT_ZERO; blocks automatic replay"}
        atomic(EXEC / f"{runid}.START.json", record)
        before_c = resource.getrusage(resource.RUSAGE_CHILDREN)
        before_p = resource.getrusage(resource.RUSAGE_SELF)
        t0 = time.monotonic()
        error = None
        rc = None
        launched = True
        with open(EXEC / f"{runid}.stdout.txt", "xb") as stdout, open(EXEC / f"{runid}.stderr.txt", "xb") as stderr:
            try:
                child = subprocess.Popen(record["command"], cwd=UNIT, env=env, stdout=stdout, stderr=stderr, preexec_fn=limits)
                try:
                    rc = child.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    error = "WALL_LIMIT"
                    os.killpg(child.pid, signal.SIGKILL)
                    rc = child.wait()
            except Exception as exc:
                error = type(exc).__name__ + ": " + str(exc)
            stdout.flush()
            stderr.flush()
            os.fsync(stdout.fileno())
            os.fsync(stderr.fileno())
        elapsed = time.monotonic() - t0
        after_c = resource.getrusage(resource.RUSAGE_CHILDREN)
        after_p = resource.getrusage(resource.RUSAGE_SELF)
        child_cpu = cpu(after_c) - cpu(before_c)
        parent_cpu = cpu(after_p) - cpu(before_p)
        observed_cpu = child_cpu + parent_cpu
        overshoot = child_cpu > 6 or elapsed > 20 or observed_cpu + ledger["cumulative_cpu_s"] > 20 or elapsed + ledger["cumulative_wall_s"] > 60
        if rc != 0 and error is None:
            error = "CHILD_NONZERO_EXIT"
        if overshoot:
            error = "MEASURED_CAP_OVERSHOOT" + ("; " + error if error else "")
        record.update({"finished_utc": stamp(), "returncode": rc, "child_cpu_s": child_cpu, "parent_cpu_s": parent_cpu, "cpu_s": observed_cpu, "wall_s": elapsed,
                       "child_resource_usage": {"user_s": after_c.ru_utime - before_c.ru_utime, "system_s": after_c.ru_stime - before_c.ru_stime, "maxrss_KiB": after_c.ru_maxrss},
                       "status": "FINISH" if error is None else "FAIL", "failure_reason": error,
                       "stdout": digest(EXEC / f"{runid}.stdout.txt"), "stderr": digest(EXEC / f"{runid}.stderr.txt"), "measured_cap_overshoot": overshoot})
        ledger["cumulative_cpu_s"] += observed_cpu
        ledger["cumulative_wall_s"] += elapsed
        ledger["attempts"].append(record)
        atomic(EXEC / f"{runid}.{record['status']}.json", record)
        atomic(LEDGER, ledger)
        completed = True
        print(json.dumps({k: record[k] for k in ("run_id", "status", "returncode", "child_cpu_s", "parent_cpu_s", "cpu_s", "wall_s", "failure_reason")}))
        if error:
            raise SystemExit(1)
    finally:
        # An interrupted launched run keeps its lock and START for diagnosis.
        if not launched or completed:
            lock.unlink()


if __name__ == "__main__":
    main()
