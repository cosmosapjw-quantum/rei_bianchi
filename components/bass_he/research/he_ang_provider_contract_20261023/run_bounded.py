#!/usr/bin/env python3
"""Bounded, serialized HE-ANG execution. BUDGET/CONTRACT stay immutable.
Only the supplied child command executes science. No automatic retry.
"""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import sys
import time
import uuid

WRAPPER_CLOCK_START = time.monotonic()
SCHEMA = "he_ang.resource_events.v1"


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def atom(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def cpu(r):
    return r.ru_utime + r.ru_stime


def default_unit():
    here = Path(__file__).resolve().parent
    return next((p for p in (here, *here.parents)
                 if (p / "BUDGET.json").is_file()), here)


def fixed_inputs(unit):
    return {name: digest(unit / name) for name in ("BUDGET.json", "CONTRACT.json")}


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RuntimeError(label + " must be a finite nonnegative number")
    if not math.isfinite(value) or value < 0:
        raise RuntimeError(label + " must be a finite nonnegative number")
    return float(value)


def reconcile(unit, ledger, budget):
    """Read existing immutable START/FINISH records; never reset a debit."""
    if ledger.get("schema") != SCHEMA or ledger.get("frozen_inputs") != fixed_inputs(unit):
        raise RuntimeError("ledger schema or frozen BUDGET/CONTRACT identity changed")
    if budget.get("unknown_cost_records"):
        raise RuntimeError("frozen budget contains unknown costs")
    if budget.get("executions") or budget.get("known_consumed_cpu_s", 0) != 0:
        raise RuntimeError("this fresh-unit runner requires the frozen zero-attempt baseline")
    if budget.get("known_consumed_wall_s", 0) != 0:
        raise RuntimeError("nonzero frozen baseline requires explicit reconciliation")
    starts, finishes, charged_cpu, charged_wall = {}, {}, 0.0, 0.0
    for event in ledger["events"]:
        ident = event["attempt_id"]
        path = unit / event["record"]
        if digest(path) != event["sha256"]:
            raise RuntimeError("record identity mismatch: " + str(path))
        rec = read(path)
        if rec["attempt_id"] != ident:
            raise RuntimeError("attempt identity mismatch")
        if event["event"] == "START":
            if ident in starts:
                raise RuntimeError("duplicate START")
            starts[ident] = rec
        elif event["event"] == "FINISH":
            if ident not in starts or ident in finishes:
                raise RuntimeError("unmatched or duplicate FINISH")
            if rec.get("cost_status") != "KNOWN_CHILD_REAPED":
                raise RuntimeError("unknown child cost blocks further execution")
            charged_cpu += number(rec["cpu_charge_s"], "CPU charge")
            charged_wall += number(rec["wall_charge_s"], "wall charge")
            finishes[ident] = rec
        else:
            raise RuntimeError("unknown ledger event")
    if starts.keys() != finishes.keys():
        raise RuntimeError("running/unresolved START blocks further execution")
    for path in (unit / "evidence" / "execution" / "attempts").glob("*/START.json"):
        if read(path)["attempt_id"] not in starts:
            raise RuntimeError("orphan START requires preserved-cost reconciliation")
    remaining_cpu = number(budget["cap"]["cpu_s"], "CPU cap") - charged_cpu
    remaining_wall = number(budget["cap"]["wall_s"], "wall cap") - charged_wall
    return charged_cpu, charged_wall, remaining_cpu, remaining_wall


def code_identity(unit, command):
    files = {Path(__file__).resolve()}
    executable = shutil.which(command[0])
    if executable:
        files.add(Path(executable).resolve())
    for arg in command[1:]:
        path = Path(arg)
        if not path.is_absolute():
            path = unit / path
        if path.is_file():
            files.add(path.resolve())
    for dirname in ("code", "theory"):
        folder = unit / dirname
        if folder.exists():
            files.update(p.resolve() for p in folder.rglob("*.py"))
    return {str(p): digest(p) for p in sorted(files)}


def group_alive(pid):
    try:
        os.killpg(pid, 0)
        return True
    except ProcessLookupError:
        return False


def kill_group(pid):
    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit", type=Path, default=default_unit())
    parser.add_argument("--label", required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    unit = args.unit.resolve()
    execution = unit / "evidence" / "execution"
    execution.mkdir(parents=True, exist_ok=True)
    lock = (execution / "RESOURCE.lock").open("a+")
    attempt = None
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if not command or not args.label or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in args.label):
            raise RuntimeError("supply a command and an alphanumeric/underscore/hyphen label")
        budget = read(unit / "BUDGET.json")
        ledger_path = unit / "RESOURCE_LEDGER.json"
        if ledger_path.exists():
            ledger = read(ledger_path)
        else:
            if list((execution / "attempts").glob("*/START.json")):
                raise RuntimeError("missing ledger with saved attempts: do not reset")
            ledger = {"schema": SCHEMA, "created_utc": utc(),
                      "frozen_inputs": fixed_inputs(unit), "events": []}
        spent_cpu, spent_wall, remaining_cpu, remaining_wall = reconcile(unit, ledger, budget)
        code_before = code_identity(unit, command)
        env = os.environ.copy()
        env.update({"OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1",
                    "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1",
                    "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"})
        # Integer RLIMIT_CPU is rounded DOWN, never above remaining allocation.
        wrapper_used = cpu(resource.getrusage(resource.RUSAGE_SELF))
        cpu_limit = math.floor(min(number(budget["per_invocation"]["cpu_s"], "child CPU"),
                                   remaining_cpu - wrapper_used))
        wall_limit = min(number(budget["per_invocation"]["wall_s"], "child wall"),
                         remaining_wall - (time.monotonic() - WRAPPER_CLOCK_START))
        as_limit = int(budget["cap"]["peak_address_space_bytes"])
        if cpu_limit < 1 or wall_limit <= 0 or as_limit <= 0:
            raise RuntimeError("insufficient remaining budget before child launch")
        ident = "{:03d}_{}_{}".format(len(ledger["events"]) // 2 + 1,
                                     args.label, uuid.uuid4().hex[:12])
        attempt = execution / "attempts" / ident
        attempt.mkdir(parents=True, exist_ok=False)
        env["HEANG_ATTEMPT_DIR"] = str(attempt)
        recorded_env = {k: env.get(k) for k in (
            "PATH", "PYTHONPATH", "PYTHONHASHSEED", "PYTHONDONTWRITEBYTECODE",
            "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS", "LANG", "LC_ALL", "TZ", "HEANG_ATTEMPT_DIR")}
        start = {"attempt_id": ident, "label": args.label, "state": "START",
                 "created_utc": utc(), "cwd": str(unit), "command": command,
                 "environment_selected": recorded_env,
                 "environment_scope": "numerical/runtime allowlist; secrets not copied",
                 "frozen_inputs": fixed_inputs(unit), "code_sha256": code_before,
                 "limits": {"cpu_s": cpu_limit, "wall_s": wall_limit,
                            "address_space_bytes": as_limit},
                 "prior_consumed_cpu_s": spent_cpu, "prior_consumed_wall_s": spent_wall}
        atom(attempt / "START.json", start)
        ledger["events"].append({"event": "START", "attempt_id": ident,
                                 "record": str((attempt / "START.json").relative_to(unit)),
                                 "sha256": digest(attempt / "START.json")})
        atom(ledger_path, ledger)

        def child_limits():
            resource.setrlimit(resource.RLIMIT_AS, (as_limit, as_limit))
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

        def terminated(signum, _frame):
            raise InterruptedError("wrapper received signal " + str(signum))

        signal.signal(signal.SIGTERM, terminated)
        before_children = resource.getrusage(resource.RUSAGE_CHILDREN)
        child_begin = time.monotonic()
        process, failure, timed_out, unknown = None, None, False, False
        returncode = None
        with (attempt / "stdout.txt").open("wb") as out, (attempt / "stderr.txt").open("wb") as err:
            try:
                process = subprocess.Popen(command, cwd=unit, env=env, stdout=out,
                                           stderr=err, preexec_fn=child_limits,
                                           start_new_session=True)
                timeout = max(0.0, wall_limit - (time.monotonic() - child_begin))
                returncode = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                failure = "wall timeout; process group killed"
            except BaseException as exc:
                failure = type(exc).__name__ + ": " + str(exc)
            finally:
                if process is not None:
                    child_still_running = process.poll() is None
                    live_group = group_alive(process.pid)
                    if not child_still_running and live_group:
                        unknown = True
                        failure = (failure or "") + "; descendant outlived direct child; complete descendant cost unknown"
                    if child_still_running or live_group:
                        kill_group(process.pid)
                    try:
                        returncode = process.wait(timeout=1.0)
                    except BaseException as exc:
                        unknown = True
                        failure = (failure or "") + "; reap failed: " + repr(exc)
                    if group_alive(process.pid):
                        unknown = True
                        failure = (failure or "") + "; surviving/unreaped process-group member"
                out.flush()
                err.flush()
                os.fsync(out.fileno())
                os.fsync(err.fileno())
        child_end = time.monotonic()
        after_children = resource.getrusage(resource.RUSAGE_CHILDREN)
        child_cpu = cpu(after_children) - cpu(before_children)
        outputs = {str(p.relative_to(attempt)): {"bytes": p.stat().st_size, "sha256": digest(p)}
                   for p in sorted(attempt.rglob("*"))
                   if p.is_file() and p.name not in ("START.json", "FINISH.json")}
        code_after = code_identity(unit, command)
        measurement_end = time.monotonic()
        wrapper_rusage = resource.getrusage(resource.RUSAGE_SELF)
        wrapper_cpu_known = cpu(wrapper_rusage)
        cpu_charge = child_cpu + wrapper_cpu_known
        wall_charge = measurement_end - WRAPPER_CLOCK_START
        within = spent_cpu + cpu_charge <= budget["cap"]["cpu_s"] and spent_wall + wall_charge <= budget["cap"]["wall_s"]
        passed = returncode == 0 and not failure and not unknown and within and code_before == code_after
        finish = {"attempt_id": ident, "label": args.label,
                  "state": "PASS" if passed else "FAILED_PRESERVED",
                  "returncode": returncode, "failure": failure, "timed_out": timed_out,
                  "cost_status": "UNKNOWN_BLOCKED" if unknown else "KNOWN_CHILD_REAPED",
                  "child_cpu_s": child_cpu, "child_wall_s": child_end - child_begin,
                  "wrapper_cpu_known_s": wrapper_cpu_known,
                  "wrapper_wall_observed_s": wall_charge,
                  "cpu_charge_s": cpu_charge, "wall_charge_s": wall_charge,
                  "cpu_charge_scope": "whole reaped child RUSAGE_CHILDREN delta plus wrapper RUSAGE_SELF through measurement_end",
                  "wall_charge_scope": "wrapper module clock through measurement_end, includes whole child startup/wait/exit",
                  "measurement_end_utc": utc(),
                  "post_measurement_scope": "FINISH/ledger persistence and wrapper exit are non-scientific bookkeeping; not claimed measured",
                  "child_peak_rss_KiB": after_children.ru_maxrss,
                  "child_peak_rss_scope": "RUSAGE_CHILDREN max in this fresh wrapper; not a subtraction of maxima",
                  "wrapper_peak_rss_KiB": wrapper_rusage.ru_maxrss,
                  "limits": start["limits"], "within_cumulative_cap": within,
                  "code_unchanged": code_before == code_after,
                  "outputs": outputs, "output_scope": "stdout/stderr and files in HEANG_ATTEMPT_DIR",
                  "frozen_inputs": start["frozen_inputs"]}
        atom(attempt / "FINISH.json", finish)
        ledger["events"].append({"event": "FINISH", "attempt_id": ident,
                                 "record": str((attempt / "FINISH.json").relative_to(unit)),
                                 "sha256": digest(attempt / "FINISH.json")})
        ledger["known_consumed_cpu_s"] = spent_cpu + cpu_charge
        ledger["known_consumed_wall_s"] = spent_wall + wall_charge
        ledger["remaining_cpu_s"] = budget["cap"]["cpu_s"] - ledger["known_consumed_cpu_s"]
        ledger["remaining_wall_s"] = budget["cap"]["wall_s"] - ledger["known_consumed_wall_s"]
        ledger["unknown_cost_records"] = [ident] if unknown else []
        atom(ledger_path, ledger)
        print(json.dumps({"state": finish["state"], "attempt": str(attempt),
                          "cpu_charge_s": cpu_charge, "wall_charge_s": wall_charge,
                          "remaining_cpu_s": ledger["remaining_cpu_s"],
                          "remaining_wall_s": ledger["remaining_wall_s"]}))
        return 0 if passed else 1
    except BaseException as exc:
        # A START without FINISH deliberately blocks the next invocation.
        blocked = {"state": "BLOCKED_NO_ADDITIONAL_SCIENCE", "created_utc": utc(),
                   "reason": type(exc).__name__ + ": " + str(exc),
                   "attempt": str(attempt) if attempt else None,
                   "cost_scope": "preflight/finalization bookkeeping; any existing unresolved START remains blocking"}
        try:
            atom(execution / ("BLOCKED_" + uuid.uuid4().hex + ".json"), blocked)
        except OSError:
            pass
        print(json.dumps(blocked), file=sys.stderr)
        return 2
    finally:
        lock.close()


if __name__ == "__main__":
    raise SystemExit(main())
