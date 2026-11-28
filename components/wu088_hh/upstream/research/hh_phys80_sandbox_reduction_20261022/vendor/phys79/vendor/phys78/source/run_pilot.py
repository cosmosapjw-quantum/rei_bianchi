#!/usr/bin/env python3
"""Bounded, resumable PHYS78 exploratory case launcher.

One physical case is one process task. Numerical libraries use one thread. A
case's scientific identity excludes labels, plotting, orchestration and host
information; completed bytes and failed attempts are never replayed silently.
The common HH74 lease protocol is advisory: sampled kernel headroom also
constrains admission, and running peer processes are never terminated.
"""
from __future__ import annotations

import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS"):
    os.environ[_name] = "1"

import argparse
import concurrent.futures as cf
import contextlib
import fcntl
import hashlib
import importlib
import json
import math
import multiprocessing
import sys
import tempfile
import time
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GIB = 1024**3
DEFAULT_RESOLUTION = {"radial_cells": 12, "angular_cells": 12, "gauss_order": 3,
                      "rad_ang_order": 32, "mass_over_Tref": 30.0}
DEFAULT_OPTIONS = {"rtol": 2e-7, "resolution": DEFAULT_RESOLUTION, "samples": 161}
PHYSICAL_DEFAULTS = {"HII_initial": 2e-4, "T_initial_K": 300.,
                     "reservoir_initial_eV_per_H": 1000., "photon_initial_per_H": 1e-10}
REQUIRED = ("sigma0_F_signed", "A_m", "A_r", "uv_scale")
LABEL_FIELDS = {"id", "label", "description", "notes"}
SCHEMA = "phys78-science-identity-v1"


def now():
    return datetime.now(timezone.utc).isoformat()


def _json_default(value):
    if hasattr(value, "tolist"):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"JSON_UNSUPPORTED_TYPE:{type(value).__name__}")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False, default=_json_default).encode()


def sha_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _publish_bytes(path, content, *, replace=False):
    """Publish complete bytes atomically; science artifacts are create-only."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".publish-", dir=path.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if replace:
            os.replace(temp, path)
        else:
            os.link(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def _write_json(path, obj, *, replace=False):
    _publish_bytes(path, canonical(obj) + b"\n", replace=replace)


def scientific_manifest(root=ROOT):
    """Hash only local scientific implementation and the atomic input tables."""
    root = Path(root)
    excluded = {"run_pilot.py", "plot_pilot.py", "resources.py", "shared_resources.py"}
    files = sorted(p for p in (root / "source").glob("*.py") if p.name not in excluded)
    required = {"atomic_network.py", "coupled_model.py", "kinetic.py"}
    if not required.issubset({p.name for p in files}):
        raise FileNotFoundError("SCIENTIFIC_SOURCE_INCOMPLETE:" + ",".join(sorted(required - {p.name for p in files})))
    tables = sorted((root / "vendor" / "atomic").glob("*.dat"))
    if not {"photo.dat", "rec_table1.dat"}.issubset({p.name for p in tables}):
        raise FileNotFoundError("ATOMIC_SOURCE_TABLES_INCOMPLETE")
    entries = {p.relative_to(root).as_posix(): sha_file(p) for p in files + tables}
    return {"schema": SCHEMA, "files": entries,
            "sha256": hashlib.sha256(canonical(entries)).hexdigest()}


def normalize_case(case):
    missing = set(REQUIRED) - set(case)
    unknown = set(case) - set(REQUIRED) - set(PHYSICAL_DEFAULTS) - LABEL_FIELDS
    if missing or unknown:
        raise ValueError(f"CASE_FIELDS:missing={sorted(missing)},unknown={sorted(unknown)}")
    physics = {**PHYSICAL_DEFAULTS, **{k: v for k, v in case.items() if k not in LABEL_FIELDS}}
    physics = {k: float(v) if float(v) != 0 else 0.0 for k, v in physics.items()}
    if not all(math.isfinite(v) for v in physics.values()):
        raise ValueError("NONFINITE_PHYSICAL_INPUT")
    return physics


def normalize_options(options=None):
    options = options or {}
    if set(options) - {"rtol", "resolution", "samples"}:
        raise ValueError("UNKNOWN_SOLVER_OPTIONS")
    resolution = dict(DEFAULT_RESOLUTION)
    supplied = options.get("resolution") or {}
    if set(supplied) - set(resolution):
        raise ValueError("UNKNOWN_RESOLUTION_OPTIONS")
    resolution.update(supplied)
    for key, value in resolution.items():
        if key != "mass_over_Tref" and float(value) != int(value):
            raise ValueError("NONINTEGER_RESOLUTION:" + key)
    if float(options.get("samples", 161)) != int(options.get("samples", 161)):
        raise ValueError("NONINTEGER_SAMPLE_COUNT")
    resolution = {k: float(v) if k == "mass_over_Tref" else int(v) for k, v in resolution.items()}
    result = {"rtol": float(options.get("rtol", 2e-7)), "resolution": resolution,
              "samples": int(options.get("samples", 161))}
    if not 1e-10 <= result["rtol"] <= 1e-4 or not 3 <= result["samples"] <= 2001:
        raise ValueError("INVALID_SOLVER_CONTROLS")
    if any(v <= 0 or not math.isfinite(v) for v in resolution.values()):
        raise ValueError("INVALID_RESOLUTION")
    return result


def identity(case, options, manifest):
    binding = {"schema": SCHEMA, "physical_case": normalize_case(case),
               "solver": normalize_options(options), "source": manifest}
    return hashlib.sha256(canonical(binding)).hexdigest(), binding


def default_cases(case_set="pilot"):
    if case_set == "control":
        return [{"id": "control_isotropic_uv1", "sigma0_F_signed": 0.,
                 "A_m": 0., "A_r": 0., "uv_scale": 1.}]
    cases = []
    for sigma in (-.1, 0., .1):
        for am in (-.8, 0., .8):
            for ar in (-.8, 0., .8):
                cases.append({"id": f"P{len(cases):03d}", "sigma0_F_signed": sigma,
                              "A_m": am, "A_r": ar, "uv_scale": 1.})
    for sigma, uv in ((-.01, 1.), (.01, 1.), (0., .5), (0., 2.)):
        cases.append({"id": f"P{len(cases):03d}", "sigma0_F_signed": sigma,
                      "A_m": 0., "A_r": 0., "uv_scale": uv})
    return cases


def _case_paths(output, key):
    folder = Path(output) / "cases"
    return folder / (key + ".npz"), folder / (key + ".json")


def existing_case(output, key, binding):
    """A receipt or attempt is evidence to inspect, never permission to replay."""
    npz, receipt = _case_paths(output, key)
    checksum = receipt.with_suffix(".json.sha256")
    if receipt.exists():
        if not checksum.exists() or checksum.read_text().strip() != sha_file(receipt):
            raise RuntimeError("CASE_RECEIPT_INTEGRITY:" + key)
        record = json.loads(receipt.read_text())
        if record.get("science_id") != key or record.get("binding") != binding:
            raise RuntimeError("CASE_IDENTITY_MISMATCH:" + key)
        if record["status"] == "COMPLETE":
            saved = record["npz"]
            if not npz.exists() or npz.stat().st_size != saved["bytes"] or sha_file(npz) != saved["sha256"]:
                raise RuntimeError("CASE_DATA_INTEGRITY:" + key)
            return "COMPLETE", record
        return "FAILED_PREVIOUS_ATTEMPT", record
    if npz.exists() or (Path(output) / "claims" / (key + ".json")).exists():
        return "INCOMPLETE_PREVIOUS_ATTEMPT", None
    return "READY", None


def _publish_receipt(output, key, record):
    _, receipt = _case_paths(output, key)
    data = canonical(record) + b"\n"
    _publish_bytes(receipt, data)
    _publish_bytes(receipt.with_suffix(".json.sha256"), hashlib.sha256(data).hexdigest().encode() + b"\n")


def _complete(output, key, binding, case, raw_path, metadata, provenance):
    npz, _ = _case_paths(output, key)
    npz.parent.mkdir(parents=True, exist_ok=True)
    # The raw attempt and final NPZ share immutable content on this filesystem.
    try:
        os.link(raw_path, npz)
    except OSError as error:
        if error.errno != 18:  # EXDEV only; never replace an existing artifact.
            raise
        _publish_bytes(npz, Path(raw_path).read_bytes())
    record = {"status": "COMPLETE", "science_id": key, "binding": binding,
              "case": case, "completed_utc": now(), "diagnostics": metadata,
              "npz": {"sha256": sha_file(npz), "bytes": npz.stat().st_size},
              "provenance": provenance, "HH_R10": "OFF", "production_admission": False}
    _publish_receipt(output, key, record)
    return {"science_id": key, "case_id": case.get("id"), "status": "COMPLETE"}


def _get_solver():
    return importlib.import_module("coupled_model").solve_case


def _execute_case(payload):
    output, case, binding, key = Path(payload["output"]), payload["case"], payload["binding"], payload["key"]
    lease = payload.get("lease")
    attempt = output / "attempts" / key / uuid.uuid4().hex
    started = False
    solver_called = False
    try:
        if lease:
            rebind_lease(lease)
        state, _ = existing_case(output, key, binding)
        if state != "READY":
            return {"science_id": key, "case_id": case.get("id"), "status": "SKIPPED_COMPLETE" if state == "COMPLETE" else state}
        if scientific_manifest(payload.get("root", ROOT)) != binding["source"]:
            raise RuntimeError("SOURCE_CHANGED_BEFORE_EXECUTION")
        _write_json(output / "claims" / (key + ".json"),
                    {"science_id": key, "started_utc": now(), "pid": os.getpid(), "attempt": str(attempt)})
        started = True
        attempt.mkdir(parents=True)
        _write_json(attempt / "STARTED.json", {"case": case, "binding": binding, "utc": now()})
        solver_called = True
        arrays, meta = _get_solver()({**binding["physical_case"], "id": case.get("id", key)}, **binding["solver"])
        import numpy as np
        raw = attempt / "RESULT.npz"
        with raw.open("xb") as stream:
            np.savez_compressed(stream, **arrays)
        _write_json(attempt / "RESULT_METADATA.json", meta)
        if scientific_manifest(payload.get("root", ROOT)) != binding["source"]:
            raise RuntimeError("SOURCE_CHANGED_DURING_EXECUTION_RAW_RESULT_PRESERVED")
        result = _complete(output, key, binding, case, raw, meta,
                           {"kind": "new_scientific_case", "attempt": str(attempt.relative_to(output)),
                            "python": sys.version.split()[0]})
        result["new_ode_calls"] = 1
        return result
    except Exception as error:
        failure = {"status": "FAILED", "science_id": key, "binding": binding, "case": case,
                   "failed_utc": now(), "error": repr(error), "traceback": traceback.format_exc(),
                   "automatic_retry": False, "scientific_call_started": solver_called}
        attempt.mkdir(parents=True, exist_ok=True)
        _write_json(attempt / "FAILED.json", failure)
        # A prior completion/partial publish is never overwritten by this path.
        if started and not _case_paths(output, key)[1].exists():
            _publish_receipt(output, key, failure)
        return {"science_id": key, "case_id": case.get("id"), "status": "FAILED", "error": repr(error),
                "new_ode_calls": int(solver_called)}
    finally:
        if lease:
            release_lease(lease)


def adopt_completed(output, case, options, source_manifest, npz_path, metadata,
                    execution_source_manifest, *, root=ROOT):
    """Adopt a genuinely completed identical debug case without calling the solver.

    Caller must supply the manifest captured immediately before the execution.
    This checks it against the current files and the solver's returned physical
    case/options. The original trial remains in its own location.
    """
    if source_manifest != execution_source_manifest or scientific_manifest(root) != source_manifest:
        raise ValueError("ADOPTION_SOURCE_BINDING_MISMATCH")
    key, binding = identity(case, options, source_manifest)
    state, _ = existing_case(output, key, binding)
    if state == "COMPLETE":
        return {"science_id": key, "status": "SKIPPED_COMPLETE"}
    if state != "READY":
        raise RuntimeError("ADOPTION_PRIOR_ATTEMPT_REQUIRES_REVIEW:" + state)
    returned_options = {k: metadata[k] for k in ("rtol", "resolution", "samples")}
    if normalize_case(metadata["case"]) != binding["physical_case"] or normalize_options(returned_options) != binding["solver"]:
        raise ValueError("ADOPTION_PHYSICAL_INPUT_OR_SOLVER_MISMATCH")
    if metadata.get("status") != "COMPLETED_EXPLORATORY":
        raise ValueError("ADOPTION_REQUIRES_SUCCESSFUL_SOLVER_METADATA")
    # NPZ is read without pickle; corruption/object payloads are not adopted.
    import numpy as np
    with np.load(npz_path, allow_pickle=False) as data:
        if not data.files:
            raise ValueError("EMPTY_ADOPTION_ARRAYS")
        for name in data.files:
            value = data[name]
            if value.dtype.kind in "fc" and not np.isfinite(value).all():
                raise ValueError("NONFINITE_ADOPTION_ARRAY:" + name)
    _write_json(Path(output) / "claims" / (key + ".json"),
                {"science_id": key, "adopted_utc": now(), "original_npz_sha256": sha_file(npz_path)})
    return _complete(output, key, binding, case, Path(npz_path), metadata,
                     {"kind": "adopted_existing_execution", "original_npz_sha256": sha_file(npz_path),
                      "original_case_id": metadata["case"].get("id"), "new_ode_calls": 0})


def _pid_start(pid):
    try:
        text = Path(f"/proc/{int(pid)}/stat").read_text()
        return text[text.rfind(")") + 2:].split()[19]
    except (FileNotFoundError, ProcessLookupError):
        return "DEAD"
    except (OSError, IndexError, ValueError):
        return None


def _cgroups():
    root = Path("/sys/fs/cgroup")
    try:
        rel = next(line.split(":", 2)[2] for line in Path("/proc/self/cgroup").read_text().splitlines() if line.startswith("0::"))
        leaf = root / rel.lstrip("/")
        if not leaf.is_dir():
            leaf = root
        return [leaf, *[p for p in leaf.parents if p == root or root in p.parents]]
    except (OSError, StopIteration):
        return [root]


def _cpu_snapshot(ids):
    values = {}
    for line in Path("/proc/stat").read_text().splitlines():
        fields = line.split()
        tag = fields[0] if fields else ""
        if tag.startswith("cpu") and tag[3:].isdigit() and int(tag[3:]) in ids:
            v = list(map(int, fields[1:9]))
            values[tag] = (sum(v), v[3] + v[4])
    return values


def _usage(path):
    try:
        return int(dict(line.split() for line in (path / "cpu.stat").read_text().splitlines())["usage_usec"])
    except (OSError, KeyError, ValueError):
        return None


def observe_resources(site="local", interval=.08):
    """CPU quota/affinity, actual free memory and short sampled CPU headroom."""
    ids = set(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else set(range(os.cpu_count() or 1))
    cg = _cgroups()
    cap_float = float(len(ids))
    quotas = []
    for path in cg:
        limit = None
        try:
            quota, period = (path / "cpu.max").read_text().split()
            if quota != "max":
                limit = int(quota) / int(period)
                cap_float = min(cap_float, limit)
        except (OSError, ValueError):
            pass
        quotas.append(limit)
    site_cpu, site_mem = (8, 8.) if site == "local" else (64, 128.)
    cap = max(1, min(site_cpu, math.floor(cap_float)))
    info = {k: int(v.split()[0]) * 1024 for k, v in (line.split(":", 1) for line in Path("/proc/meminfo").read_text().splitlines())}
    available, capacity = info["MemAvailable"], min(info["MemTotal"], site_mem * GIB)
    for path in cg:
        try:
            limit = (path / "memory.max").read_text().strip()
            if limit != "max":
                limit, used = int(limit), int((path / "memory.current").read_text())
                capacity, available = min(capacity, limit), min(available, max(0, limit-used))
        except (OSError, ValueError):
            pass
    before = _cpu_snapshot(ids)
    ua = [_usage(p) for p in cg]
    stamp = time.monotonic()
    time.sleep(interval)
    elapsed = time.monotonic() - stamp
    after = _cpu_snapshot(ids)
    ub = [_usage(p) for p in cg]
    busy = sum(max(0., min(1., 1-(after[k][1]-v[1])/(after[k][0]-v[0])))
               for k, v in before.items() if k in after and after[k][0] > v[0])
    cgroup_samples = [None if a is None or b is None else max(0., (b-a)/1e6/elapsed)
                     for a, b in zip(ua, ub)]
    # Compare each ancestor's usage with that ancestor's quota. Subtracting a
    # broad parent's usage from a narrow child's quota would falsely starve a
    # child even while both levels retain headroom.
    quota_headroom = [max(0., quota-used) for quota, used in zip(quotas, cgroup_samples)
                      if quota is not None and used is not None]
    idle = min([max(0., len(ids)-busy), float(cap), *quota_headroom])
    cgroup_busy = cgroup_samples[0]
    return {"site": site, "cap_cpus": cap, "affinity_cpus": len(ids), "quota_cpus": cap_float,
            "sampled_busy_affinity_cpus": busy, "sampled_cgroup_busy_cpus": cgroup_busy,
            "sampled_idle_cpus": idle, "cgroup_quota_headrooms": quota_headroom,
            "available_gib": available/GIB,
            "capacity_gib": capacity/GIB, "reserve_gib": 1.5 if site == "local" else 16.,
            "reserve_cpus": 1 if cap >= 2 else 0, "job_gib": .5, "sample_interval_s": elapsed}


@contextlib.contextmanager
def _lease_lock(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    with (path / "leases.lock").open("a+") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def _live_leases(path, boot):
    live = []
    for file in Path(path).glob("lease-*.json"):
        lease = json.loads(file.read_text())
        tick = _pid_start(lease["pid"])
        stale = lease["boot"] != boot or tick == "DEAD" or (tick is not None and lease.get("start") is not None and tick != lease["start"])
        if not stale:
            live.append(lease)
    return live


def resource_slots(observation, leases):
    leased_cpu = sum(float(x["cpus"]) for x in leases)
    leased_gib = sum(float(x["gib"]) for x in leases)
    cpu = min(observation["cap_cpus"] - observation["reserve_cpus"] - leased_cpu,
              observation["sampled_idle_cpus"] - observation["reserve_cpus"])
    memory = min(observation["available_gib"] - observation["reserve_gib"],
                 observation["capacity_gib"] - observation["reserve_gib"] - leased_gib)
    return max(0, min(math.floor(cpu), math.floor(memory/observation["job_gib"])))


class LeasePool:
    def __init__(self, path="/tmp/rei-bianchi-cooperative-leases", site="local"):
        self.path, self.site = Path(path), site
        self.owner = f"{os.getpid()}-{uuid.uuid4().hex}"
        self.boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()

    def acquire(self, task):
        observation = observe_resources(self.site)
        with _lease_lock(self.path):
            live = _live_leases(self.path, self.boot)
            slots = resource_slots(observation, live)
            observation.update({"admissible_slots": slots, "live_leases": len(live)})
            if slots < 1:
                return None, observation
            key = uuid.uuid4().hex
            record = {"owner": self.owner, "pid": os.getpid(), "start": _pid_start(os.getpid()),
                      "boot": self.boot, "cpus": 1, "gib": observation["job_gib"], "task": task}
            _write_json(self.path / f"lease-{key}.json", record)
            return {"path": str(self.path), "key": key, "owner": self.owner}, observation


def rebind_lease(token):
    with _lease_lock(token["path"]):
        file = Path(token["path"]) / ("lease-" + token["key"] + ".json")
        record = json.loads(file.read_text())
        if record["owner"] != token["owner"]:
            raise RuntimeError("FOREIGN_LEASE_REBIND_REFUSED")
        record.update(pid=os.getpid(), start=_pid_start(os.getpid()))
        _write_json(file, record, replace=True)


def release_lease(token):
    with _lease_lock(token["path"]):
        file = Path(token["path"]) / ("lease-" + token["key"] + ".json")
        if file.exists():
            if json.loads(file.read_text())["owner"] != token["owner"]:
                raise RuntimeError("FOREIGN_LEASE_RELEASE_REFUSED")
            file.unlink()


def run_cases(cases, output, *, max_workers=3, site="local", options=None,
              preflight=False, resume=False, root=ROOT, admission_wait_s=30.,
              lease_dir="/tmp/rei-bianchi-cooperative-leases"):
    if site not in ("local", "ncp") or not 1 <= max_workers <= (8 if site == "local" else 64):
        raise ValueError("INVALID_SITE_OR_WORKER_LIMIT")
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest, opts = scientific_manifest(root), normalize_options(options)
    run_id, started, wall_start = uuid.uuid4().hex, now(), time.monotonic()
    results, pending, known, aliases = [], [], set(), {}
    for case in cases:
        key, binding = identity(case, opts, manifest)
        aliases.setdefault(key, []).append(case.get("id", key))
        if key in known:
            continue
        known.add(key)
        state, _ = existing_case(output, key, binding)
        if state == "READY":
            pending.append({"output": str(output), "case": case, "binding": binding,
                            "key": key, "root": str(Path(root).resolve())})
        else:
            results.append({"science_id": key, "case_id": case.get("id"),
                            "status": "SKIPPED_COMPLETE" if state == "COMPLETE" else state})
    observation = observe_resources(site)
    worker_cap = min(max_workers, max(1, observation["cap_cpus"]-observation["reserve_cpus"]))
    run = {"run_id": run_id, "status": "PREFLIGHT" if preflight else "STARTED",
           "started_utc": started, "source": manifest, "solver": opts,
           "site": site, "requested_workers": max_workers, "worker_cap": worker_cap,
           "initial_resources": observation, "planned_unique_cases": len(known),
           "aliases": aliases, "resume_requested": bool(resume),
           "reuse_policy": "always verify and skip identical COMPLETE; no automatic failed retry",
           "new_ode_calls": 0, "results": results, "pending_science_ids": [p["key"] for p in pending],
           "HH_R10": "OFF", "production_admission": False,
           "wall_time_scope": "operational diagnostic, not optimization benchmark"}
    run_path = output / "runs" / (run_id + ".json")

    def checkpoint():
        run["results"] = results
        run["pending_science_ids"] = [p["key"] for p in pending]
        run["wall_diagnostic_s"] = time.monotonic()-wall_start
        _write_json(run_path, run, replace=True)
        _write_json(output / "RUN.json", run, replace=True)

    checkpoint()
    if preflight:
        return run
    if pending:
        pool, active, idle_since = LeasePool(lease_dir, site), {}, None
        # spawn guarantees numerical-library thread controls precede imports.
        with cf.ProcessPoolExecutor(max_workers=worker_cap, mp_context=multiprocessing.get_context("spawn")) as executor:
            while pending or active:
                admitted = False
                while pending and len(active) < worker_cap:
                    lease, observation = pool.acquire(pending[0]["case"].get("id", pending[0]["key"]))
                    run["last_resources"] = observation
                    if lease is None:
                        break
                    payload = pending.pop(0)
                    payload["lease"] = lease
                    try:
                        future = executor.submit(_execute_case, payload)
                    except Exception:
                        release_lease(lease)
                        pending.insert(0, payload)
                        raise
                    active[future] = payload
                    admitted = True
                if active:
                    done, _ = cf.wait(active, timeout=.5, return_when=cf.FIRST_COMPLETED)
                    for future in done:
                        payload = active.pop(future)
                        try:
                            result = future.result()
                        except Exception as error:
                            result = {"science_id": payload["key"], "case_id": payload["case"].get("id"),
                                      "status": "WORKER_ERROR_REVIEW_REQUIRED", "error": repr(error)}
                        finally:
                            release_lease(payload["lease"])
                        results.append(result)
                    idle_since = None
                elif pending:
                    if idle_since is None:
                        idle_since = time.monotonic()
                    if time.monotonic()-idle_since >= admission_wait_s:
                        break
                    time.sleep(.25)
                if admitted or not active:
                    checkpoint()
    run["new_completed_cases"] = sum(r["status"] == "COMPLETE" for r in results)
    run["skipped_completed_cases"] = sum(r["status"] == "SKIPPED_COMPLETE" for r in results)
    run["new_ode_calls"] = sum(r.get("new_ode_calls", 0) for r in results)
    run["status"] = "COMPLETE" if not pending and all(r["status"] in ("COMPLETE", "SKIPPED_COMPLETE") for r in results) else "PARTIAL_REVIEW_REQUIRED"
    run["completed_utc"] = now()
    checkpoint()
    return run


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-workers", type=int, default=3)
    parser.add_argument("--site", choices=("local", "ncp"), default="local")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--case-set", choices=("pilot", "control"), default="pilot")
    parser.add_argument("--cases-json", type=Path)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--rtol", type=float, default=2e-7)
    parser.add_argument("--samples", type=int, default=161)
    parser.add_argument("--resolution-json", type=Path)
    args = parser.parse_args(argv)
    cases = json.loads(args.cases_json.read_text()) if args.cases_json else default_cases(args.case_set)
    if isinstance(cases, dict):
        cases = cases["cases"]
    options = {"rtol": args.rtol, "samples": args.samples,
               "resolution": json.loads(args.resolution_json.read_text()) if args.resolution_json else None}
    try:
        run = run_cases(cases, args.output, max_workers=args.max_workers, site=args.site,
                        options=options, preflight=args.preflight, resume=args.resume)
    except Exception as error:
        print(json.dumps({"status": "RUNNER_ERROR", "error": repr(error)}, sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps({k: run.get(k) for k in ("run_id", "status", "planned_unique_cases", "new_completed_cases", "skipped_completed_cases", "worker_cap")}, sort_keys=True))
    return 0 if run["status"] in ("COMPLETE", "PREFLIGHT") else 2


if __name__ == "__main__":
    raise SystemExit(main())
