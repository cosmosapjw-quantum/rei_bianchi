"""Cooperative, pending-only Linux execution of the HE30 continuation cases.

The science API owns input identity and result validation. This coordinator owns
only admission, shared CPU/case leases, child lifetimes and durable run receipts.
An observed memory-available value already includes active workers' allocations.
The per-worker RAM allowance is an admission budget, not a measured RSS limit.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import traceback
import uuid

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_ROOT = ROOT.parent / "he29_rei_pilot_20261021" / "vendor" / "resources"
sys.path.insert(0, str(RESOURCE_ROOT))
from c21k_scheduler import resource_snapshot, acquire_cpu, THREAD_ENV
from bass_resources import _cpu_counters

GIB = 1 << 30
LEASES = Path("/tmp/cosmosapjw_hpc64_cpu_leases")
SAFE_ID = re.compile(r"[A-Za-z0-9_-]+\Z")


def utc():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, value, *, replace=True):
    """Write+fsync in the same directory; immutable writes use atomic link."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    fd, name = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if replace:
            os.replace(temporary, path)
        else:
            os.link(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)


def _quota_usage(snapshot):
    result = {}
    for item in snapshot.get("cgroup_observations", []):
        maximum = (item.get("cpu.max") or "max 100000").split()
        if maximum[0] == "max":
            continue
        try:
            values = dict(line.split() for line in
                          (Path(item["path"]) / "cpu.stat").read_text().splitlines())
            result[item["path"]] = (float(maximum[0]) / float(maximum[1]),
                                    int(values["usage_usec"]))
        except (OSError, ValueError, KeyError, IndexError):
            continue
    return result


def observe(sample_seconds=.12):
    snapshot = resource_snapshot()
    cpus = snapshot["affinity_cpu_ids"]
    counters = _cpu_counters(cpus)
    quotas = _quota_usage(snapshot)
    start = time.monotonic()
    time.sleep(max(.02, sample_seconds))
    after = _cpu_counters(cpus)
    after_quota = _quota_usage(snapshot)
    elapsed = time.monotonic() - start
    busy = {}
    for cpu in cpus:
        a, b = counters.get(cpu), after.get(cpu)
        busy[cpu] = (max(0., min(1., 1. - (b[1] - a[1]) / (b[0] - a[0])))
                     if a and b and b[0] > a[0] else 1.)
    quota_samples = []
    for path, (limit, usage) in quotas.items():
        if path in after_quota:
            used = max(0., (after_quota[path][1] - usage) / (elapsed * 1e6))
            quota_samples.append({"path": path, "quota": limit,
                                  "busy_equivalents": used,
                                  "headroom": max(0., limit - used)})
    # Refresh memory after the observation interval, rather than retaining the
    # pre-sample value while active workers may still be allocating their input.
    latest = resource_snapshot()
    snapshot.update(memory_available_bytes=latest["memory_available_bytes"],
                    memory_limit_bytes=latest["memory_limit_bytes"],
                    cpu_busy=busy, cpu_sample_seconds=elapsed,
                    quota_samples=quota_samples, load_average=list(os.getloadavg()))
    if quota_samples:
        snapshot["cpu_quota_headroom"] = min(q["headroom"] for q in quota_samples)
    return snapshot


def capacity(snapshot, pending, active=0, max_workers=64, reserve_cpus=2,
             reserve_gib=16., per_worker_gib=1.):
    """Return NEW admissions; physical load and cgroup load are separate caps.

    Existing active worker counts enter the maximum-concurrency cap once.
    Their actual CPU/RAM usage is already in the observed headroom and must not
    be subtracted a second time. On small hosts the requested reserve is clamped
    to at most total RAM/8 and to CPU ceiling-1, allowing one small-host worker.
    """
    if (pending < 0 or active < 0 or not 1 <= max_workers <= 64 or reserve_cpus < 0
            or not math.isfinite(reserve_gib) or reserve_gib < 0
            or not math.isfinite(per_worker_gib) or per_worker_gib <= 0):
        raise ValueError("invalid resource contract")
    def activity(cpu):
        return max(0., min(1., float(snapshot["cpu_busy"].get(
            cpu, snapshot["cpu_busy"].get(str(cpu), 1.)))))
    cpus = sorted(set(snapshot["affinity_cpu_ids"]), key=lambda c: (activity(c), c))
    quota = snapshot["cpu_quota"]
    ceiling = min(64, len(cpus), math.floor(quota) if quota is not None else len(cpus))
    cpu_reserve = min(reserve_cpus, max(0, ceiling - 1))
    idle = sum(1. - activity(c) for c in cpus)
    physical_new = max(0, math.floor(idle - cpu_reserve + 1e-12))
    quota_headroom = snapshot.get("cpu_quota_headroom")
    quota_new = (max(0, math.floor(quota_headroom - cpu_reserve + 1e-12))
                 if quota_headroom is not None else ceiling)
    total = min(128 * GIB, max(0, int(snapshot["memory_limit_bytes"])))
    ram_reserve = min(int(reserve_gib * GIB), total // 8)
    available = min(total, max(0, int(snapshot["memory_available_bytes"])))
    ram_new = max(0, available - ram_reserve) // math.ceil(per_worker_gib * GIB)
    new = min(pending, max(0, max_workers - active),
              max(0, ceiling - cpu_reserve - active), physical_new, quota_new, ram_new)
    return {"cpu_ids": cpus, "new_workers": int(new), "cpu_ceiling": ceiling,
            "cpu_reserve": cpu_reserve, "memory_reserve_bytes": ram_reserve,
            "per_worker_budget_bytes": math.ceil(per_worker_gib * GIB),
            "observed_idle_cpu_equivalents": idle,
            "observed_quota_headroom": quota_headroom,
            "available_memory_new_slots": int(ram_new),
            "policy": "observed headroom; active RAM is not charged twice; no fixed CPU exclusion"}


def identity_token(identity):
    if not isinstance(identity, str) or not identity:
        raise ValueError("case_identity must return a nonempty string")
    return identity if re.fullmatch(r"[0-9a-f]{64}", identity) else hashlib.sha256(identity.encode()).hexdigest()


def acquire_job(directory, identity):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    handle = (directory / ("rei_job_" + identity_token(identity) + ".lock")).open("a+b")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        return None
    return handle


def select_cpu(directory, cpus, occupied=()):
    for cpu in cpus:
        if cpu in occupied:
            continue
        lease = acquire_cpu(directory, cpu)
        if lease is not None:
            return cpu, lease
    return None


def _api(module="continuation"):
    return importlib.import_module(module)


def reusable(config, path, api):
    try:
        return bool(api.completed_result(config, Path(path)))
    except (OSError, ValueError, KeyError, TypeError, AssertionError):
        return False


def classify(config, out, lease_dir, api):
    """Read exact science result first; never overwrite partial/failed attempts."""
    identity = api.case_identity(config)
    token = identity_token(identity)
    local = Path(out) / (config["case_id"] + ".json")
    if reusable(config, local, api):
        return {"status": "REUSED_COMPLETE", "path": str(local), "identity": identity}
    registry = Path(lease_dir) / ("rei_" + token + ".receipt.json")
    if registry.exists():
        try:
            record = json.loads(registry.read_text())
        except (OSError, ValueError):
            return {"status": "PRIOR_RECEIPT_INVALID", "path": str(registry), "identity": identity}
        if (not isinstance(record, dict) or record.get("identity") != identity
                or not isinstance(record.get("path"), str) or not record["path"]):
            return {"status": "PRIOR_RECEIPT_INVALID", "path": str(registry), "identity": identity}
        path = Path(record["path"])
        if reusable(config, path, api):
            return {"status": "REUSED_COMPLETE", "path": str(path), "identity": identity}
        # Even an unfamiliar or formerly complete receipt is evidence of an
        # earlier attempt. Failed validation never grants overwrite permission.
        return {"status": "PRIOR_ATTEMPT_PRESERVED", "path": str(registry),
                "identity": identity, "prior_status": record.get("status")}
    if local.exists() or (Path(out) / ".runner_attempts" / token).exists():
        return {"status": "PARTIAL_OUTPUT_PRESERVED", "path": str(local), "identity": identity}
    return None


def _worker(config_path, out, cpu, module):
    os.environ.update(THREAD_ENV)
    os.sched_setaffinity(0, {cpu})
    config = json.loads(Path(config_path).read_text())
    try:
        _api(module).write_case(config, Path(out))
    except BaseException as error:
        atomic_json(Path(config_path).parent / "WORKER_FAILURE.json",
                    {"status": "FAILED", "utc": utc(), "error": repr(error),
                     "traceback": traceback.format_exc()}, replace=False)
        raise


def run(out, max_workers=64, seconds=60., dry_plan=False, lease_dir=LEASES,
        reserve_cpus=2, reserve_gib=16., *, api_module="continuation"):
    if not math.isfinite(seconds) or not 0 < seconds <= 3600:
        raise ValueError("bounded time budget (0,3600] required")
    os.environ.update(THREAD_ENV)
    api = _api(api_module)
    cases = api.case_grid()
    ids = [c["case_id"] for c in cases]
    if (any(not isinstance(k, str) or not SAFE_ID.fullmatch(k) for k in ids)
            or len(ids) != len(set(ids))):
        raise ValueError("unique safe case_id values required")
    out, lease_dir = Path(out).resolve(), Path(lease_dir).resolve()
    statuses, pending = {}, []
    for config in cases:
        record = classify(config, out, lease_dir, api)
        if record is not None:
            statuses[config["case_id"]] = record
        else:
            pending.append(config)
    snapshot = observe()
    plan = capacity(snapshot, len(pending), 0, max_workers, reserve_cpus, reserve_gib)
    if dry_plan:
        return {"status": "DRY_PLAN", "pending": len(pending), "statuses": statuses,
                "snapshot": snapshot, "capacity": plan, "worker_starts": 0}
    out.mkdir(parents=True, exist_ok=True)
    lease_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    deadline = started + seconds
    campaign_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:12]
    report_path = out / ".runner_campaigns" / (campaign_id + ".json")
    active = {}
    launched = 0
    interrupted = False

    def checkpoint(final=False):
        report = {"schema": "HE30_SHARED_RUNNER_V1", "campaign_id": campaign_id,
                  "updated_utc": utc(), "final": final, "statuses": dict(statuses),
                  "active": list(active), "pending": [c["case_id"] for c in pending],
                  "snapshot": snapshot, "capacity": plan, "worker_starts": launched,
                  "elapsed_seconds": time.monotonic() - started,
                  "time_budget_seconds": seconds, "other_jobs_signalled": 0,
                  "semantics": "cooperative leases plus observed load; only owned direct children signalled"}
        atomic_json(report_path, report)
        atomic_json(out / "RUNNER_REPORT.json", report)
        return report

    def finish(key, task, forced_status=None):
        proc, cpu_lock, job_lock, config, registry, attempt, stdout, stderr = task
        path = out / (key + ".json")
        valid = reusable(config, path, api)
        state = forced_status or ("COMPLETE" if proc.returncode == 0 and valid else "FAILED")
        record = {"status": state, "identity": api.case_identity(config), "path": str(path),
                  "attempt": str(attempt), "exitcode": proc.returncode,
                  "result_valid": valid, "finished_utc": utc(), "pid": proc.pid}
        statuses[key] = record
        try:
            atomic_json(attempt / "RECEIPT.json", record, replace=False)
            atomic_json(registry, record)
        finally:
            stdout.close()
            stderr.close()
            cpu_lock.close()
            job_lock.close()

    try:
        checkpoint()
        while pending or active:
            for key, task in list(active.items()):
                if task[0].poll() is not None:
                    del active[key]
                    finish(key, task)
            if time.monotonic() >= deadline:
                break
            snapshot = observe(min(.12, max(.02, deadline - time.monotonic())))
            plan = capacity(snapshot, len(pending), len(active), max_workers, reserve_cpus, reserve_gib)
            admitted = 0
            for config in list(pending):
                key = config["case_id"]
                identity = api.case_identity(config)
                job_lock = acquire_job(lease_dir, identity)
                if job_lock is None:
                    # A busy case is skipped, not a stop for the remaining grid.
                    statuses[key] = {"status": "DEFERRED", "reason": "same_identity_running"}
                    continue
                record = classify(config, out, lease_dir, api)
                if record is not None:
                    statuses[key] = record
                    pending.remove(config)
                    job_lock.close()
                    continue
                if admitted >= plan["new_workers"] or time.monotonic() >= deadline:
                    job_lock.close()
                    continue
                selected = select_cpu(lease_dir, plan["cpu_ids"],
                                      [t[0]._he30_cpu for t in active.values()])
                if selected is None:
                    job_lock.close()
                    continue
                cpu, cpu_lock = selected
                token = identity_token(identity)
                attempt = out / ".runner_attempts" / token
                registry = lease_dir / ("rei_" + token + ".receipt.json")
                stdout = stderr = None
                try:
                    attempt.mkdir(parents=True, exist_ok=False)
                    config_path = attempt / "CONFIG.json"
                    atomic_json(config_path, config, replace=False)
                    atomic_json(registry, {"status": "STARTED", "identity": identity,
                                          "path": str(out / (key + ".json")),
                                          "attempt": str(attempt), "started_utc": utc()})
                    stdout = (attempt / "stdout.log").open("xb")
                    stderr = (attempt / "stderr.log").open("xb")
                    env = dict(os.environ, **THREAD_ENV)
                    api_dir = str(Path(api.__file__).resolve().parent)
                    env["PYTHONPATH"] = os.pathsep.join([api_dir, str(ROOT / "src"), env.get("PYTHONPATH", "")])
                    command = [sys.executable, str(Path(__file__).resolve()), "--_worker-config", str(config_path),
                               "--out", str(out), "--_worker-cpu", str(cpu), "--_worker-module", api_module]
                    # Inherited descriptors retain flock leases if the coordinator
                    # exits unexpectedly; the child owns them through process exit.
                    proc = subprocess.Popen(command, env=env, stdin=subprocess.DEVNULL,
                                            stdout=stdout, stderr=stderr,
                                            pass_fds=(cpu_lock.fileno(), job_lock.fileno()))
                    proc._he30_cpu = cpu
                except BaseException as error:
                    failure = {"status": "START_FAILED", "identity": identity,
                               "path": str(out / (key + ".json")), "error": repr(error), "utc": utc()}
                    statuses[key] = failure
                    try:
                        atomic_json(attempt / "RECEIPT.json", failure, replace=False)
                        atomic_json(registry, failure)
                    except OSError as receipt_error:
                        failure["receipt_error"] = repr(receipt_error)
                    finally:
                        for handle in (stdout, stderr, cpu_lock, job_lock):
                            if handle is not None:
                                handle.close()
                    pending.remove(config)
                    if not isinstance(error, Exception):
                        raise
                    continue
                active[key] = (proc, cpu_lock, job_lock, config, registry, attempt, stdout, stderr)
                statuses[key] = {"status": "RUNNING", "pid": proc.pid, "cpu": cpu, "identity": identity}
                pending.remove(config)
                admitted += 1
                launched += 1
            checkpoint()
            if pending or active:
                time.sleep(min(.05, max(0., deadline - time.monotonic())))
    except BaseException:
        interrupted = True
        raise
    finally:
        for key, task in list(active.items()):
            del active[key]
            proc = task[0]
            forced = None
            if proc.poll() is None:
                forced = "INTERRUPTED" if interrupted else "TIMED_OUT"
                proc.terminate()
                try:
                    proc.wait(timeout=2.)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=2.)
            finish(key, task, forced)
        for config in pending:
            statuses[config["case_id"]] = {"status": "DEFERRED", "reason": "bounded_budget_or_capacity"}
        report = checkpoint(final=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "cases")
    parser.add_argument("--max-workers", type=int, default=64)
    parser.add_argument("--time-budget-seconds", type=float, default=60.)
    parser.add_argument("--dry-plan", action="store_true")
    parser.add_argument("--lease-dir", type=Path, default=LEASES)
    parser.add_argument("--reserve-cpus", type=int, default=2)
    parser.add_argument("--reserve-gib", type=float, default=16.)
    parser.add_argument("--_worker-config", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--_worker-cpu", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--_worker-module", default="continuation", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args._worker_config is not None:
        _worker(args._worker_config, args.out, args._worker_cpu, args._worker_module)
        return 0
    if (not 1 <= args.max_workers <= 64 or not math.isfinite(args.time_budget_seconds)
            or not 0 < args.time_budget_seconds <= 3600 or args.reserve_cpus < 0
            or not math.isfinite(args.reserve_gib) or args.reserve_gib < 0):
        parser.error("workers 1..64, seconds (0,3600], finite nonnegative reserves required")
    report = run(args.out, args.max_workers, args.time_budget_seconds, args.dry_plan,
                 args.lease_dir, args.reserve_cpus, args.reserve_gib)
    print(json.dumps(report, indent=2, allow_nan=False))
    if args.dry_plan:
        return 0
    return 0 if all(v["status"] in {"COMPLETE", "REUSED_COMPLETE"}
                    for v in report["statuses"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
