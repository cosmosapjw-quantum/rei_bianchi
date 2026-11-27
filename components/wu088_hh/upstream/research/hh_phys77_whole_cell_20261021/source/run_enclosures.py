"""Pending-only, source-bound finite-cell certificate jobs; no ODE entry point.

Run --preflight first. --run requires an explicit finite --max-new-cases.
The scientific engine is only cell_enclosure.certify_request(request_dict).
COMPLETED denotes PASS_REQUESTED_PREFIX for the explicitly requested finite
prefix, not production admission or a continuum/physical-truncation certificate.
NOT_CERTIFIED_REQUESTED_PREFIX is preserved and requires an explicit retry.

The shared HH74 lease protocol is advisory, not a kernel CPU/RAM reservation.
No peer is signalled. No process is killed, including an overdue own worker.
"""
from __future__ import annotations

import os
for _key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS"):
    os.environ[_key] = "1"

import argparse
import contextlib
import fcntl
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import multiprocessing
from pathlib import Path, PurePosixPath
import platform
import re
import sys
import time
import traceback
import uuid


HERE = Path(__file__).resolve().parent
RESOURCE_SHA256 = "7e2902c015aaae0d7ebd496b2f3dc9c5476bb48aff7b5f6d57ad6652313da8a3"
TRANSPORT_SHA256 = "c8b21a2dfdb7ec5810710d2fda6d98922656ecf6d6ae86c82632caab3e227ce6"
TRANSPORT_RELATIVE = "../../hh_phys76_time_transport_20261021/source/interval_transport.py"
DEFAULT_RESOURCES = HERE.parents[1] / "hh_phys74_rei_pilot_20261021/resources.py"
DEFAULT_LEASES = "/tmp/rei-bianchi-cooperative-leases"
GIB = 1024**3
MAX_CPUS, MAX_MEMORY_GIB = 64, 128.0
MAX_REQUEST_BYTES, MAX_REQUESTS = 32 * 1024**2, 100_000
LOCK_SCHEMA = "PHYS77_ENCLOSURE_RUNNER_SOURCE_LOCK_V1"
CASE_SCHEMA = "PHYS77_ENCLOSURE_CASE_IDENTITY_V1"
RUNNER_NAME = "run_enclosures.py"
_HEX = re.compile(r"^[0-9a-f]{64}$")
_CASE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.+\-]{0,199}$")


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode()


def request_canonical(value):
    """Exactly export_owner.canonical: ASCII JSON, no trailing newline."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def read_regular(path, *, limit=None):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("NOT_REGULAR_FILE:" + str(path))
    if limit is not None and path.stat().st_size > limit:
        raise ValueError("FILE_SIZE_LIMIT:" + str(path))
    data = path.read_bytes()
    if limit is not None and len(data) > limit:
        raise ValueError("FILE_SIZE_LIMIT:" + str(path))
    return data


def checked(path, expected, *, limit=None):
    data = read_regular(path, limit=limit)
    if not isinstance(expected, str) or not _HEX.fullmatch(expected) or sha_bytes(data) != expected:
        raise ValueError("SOURCE_OR_INPUT_SHA256_MISMATCH:" + str(path))
    return data


def safe_relative(root, rel):
    p = PurePosixPath(rel)
    if p.is_absolute() or not p.parts or any(x in (".", "..") for x in p.parts):
        raise ValueError("UNSAFE_RELATIVE_PATH")
    root = Path(root).resolve()
    out = root.joinpath(*p.parts)
    if not out.resolve().is_relative_to(root):
        raise ValueError("SOURCE_PATH_ESCAPES_ROOT")
    return out


def mkdir_safe(path):
    path = Path(path)
    if path.is_symlink():
        raise ValueError("SYMLINK_OUTPUT_DIRECTORY:" + str(path))
    path.mkdir(parents=True, exist_ok=True)


def write_new(path, data):
    """Atomic create-only publication; no existing artifact is replaced."""
    path = Path(path)
    raw = data if isinstance(data, bytes) else canonical(data)
    temp = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    try:
        with temp.open("xb") as f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
        os.link(temp, path)  # fails if final name exists, including a symlink
    finally:
        temp.unlink(missing_ok=True)


def runtime_identity():
    versions = {}
    for name in ("numpy", "scipy", "mpmath", "python-flint"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return {"python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "distributions": versions}


def load_source_lock(lock_path, resources_path=DEFAULT_RESOURCES):
    lock_path = Path(lock_path).resolve()
    raw = read_regular(lock_path, limit=1024**2)
    doc = json.loads(raw)
    if (doc.get("schema") != LOCK_SCHEMA or doc.get("entry_file") != "cell_enclosure.py"
            or doc.get("entry_function") != "certify_request"):
        raise ValueError("WRONG_SOURCE_LOCK_OR_ENTRYPOINT")
    files = doc.get("files")
    if not isinstance(files, dict) or not {RUNNER_NAME, "cell_enclosure.py"} <= files.keys():
        raise ValueError("SOURCE_LOCK_MUST_PIN_RUNNER_AND_ENGINE")
    for rel, digest in files.items():
        if not isinstance(rel, str):
            raise ValueError("INVALID_SOURCE_MANIFEST")
        checked(safe_relative(lock_path.parent, rel), digest)
    external = doc.get("external_files", {})
    expected_external = {"interval_transport.py": {
        "path": TRANSPORT_RELATIVE, "sha256": TRANSPORT_SHA256}}
    if "owner_interval.py" in files and external != expected_external:
        raise ValueError("PINNED_OWNER_REQUIRES_EXACT_EXTERNAL_TRANSPORT_LOCK")
    if external and external != expected_external:
        raise ValueError("UNRECOGNIZED_EXTERNAL_SOURCE_LOCK")
    external_paths = {}
    for name, record in external.items():
        path = lock_path.parent / record["path"]
        checked(path, record["sha256"])
        external_paths[name] = str(path.resolve())
    if files[RUNNER_NAME] != sha_bytes(read_regular(__file__)):
        raise ValueError("EXECUTING_RUNNER_NOT_PINNED_VERSION")
    checked(resources_path, RESOURCE_SHA256)
    runtime = runtime_identity()
    if "expected_runtime" in doc and doc["expected_runtime"] != runtime:
        raise ValueError("SOURCE_LOCK_RUNTIME_MISMATCH")
    return {"source_root": str(lock_path.parent), "lock_path": str(lock_path),
            "lock_sha256": sha_bytes(raw), "files": files,
            "external_files": external, "external_paths": external_paths,
            "resources_path": str(Path(resources_path).resolve()),
            "resources_sha256": RESOURCE_SHA256, "runtime": runtime}


def verify_sources(guard):
    checked(guard["lock_path"], guard["lock_sha256"])
    for rel, digest in guard["files"].items():
        checked(safe_relative(guard["source_root"], rel), digest)
    for name, record in guard["external_files"].items():
        checked(guard["external_paths"][name], record["sha256"])
    checked(__file__, guard["files"][RUNNER_NAME])
    checked(guard["resources_path"], guard["resources_sha256"])
    if runtime_identity() != guard["runtime"]:
        raise ValueError("RUNTIME_CHANGED_AFTER_PREFLIGHT")


def load_requests(directory, guard):
    root = Path(directory).resolve()
    if not root.is_dir():
        raise ValueError("REQUESTS_DIRECTORY_MISSING")
    paths = sorted(root.glob("*.json"))
    if len(paths) > MAX_REQUESTS:
        raise ValueError("TOO_MANY_REQUESTS")
    rows, case_ids, raw_ids = [], set(), set()
    for path in paths:
        raw = read_regular(path, limit=MAX_REQUEST_BYTES)
        request = json.loads(raw, parse_constant=lambda v: (_ for _ in ()).throw(ValueError("NONFINITE_JSON")))
        if not isinstance(request, dict):
            raise ValueError("REQUEST_MUST_BE_ONE_JSON_OBJECT:" + str(path))
        if request.get("schema") != "PHYS77_ENCLOSURE_REQUEST_V1":
            raise ValueError("WRONG_REQUEST_SCHEMA")
        try:
            case_id = request["table"]["provenance"]["case_identity"]["case_id"]
            count = request["config"]["max_cells"]
            nodes = len(request["predictor"]["x"])
        except (KeyError, TypeError):
            raise ValueError("MISSING_NESTED_CASE_ID_OR_PREFIX_CONFIG") from None
        if (type(count) is not int or not 1 <= count <= 4096 or count >= nodes
                or ("case_id" in request and request["case_id"] != case_id)):
            raise ValueError("INVALID_EXPLICIT_PREFIX_OR_CONFLICTING_CASE_ID")
        if not isinstance(case_id, str) or not _CASE.fullmatch(case_id) or case_id in case_ids:
            raise ValueError("INVALID_OR_DUPLICATE_CASE_ID")
        digest = sha_bytes(raw)
        if digest in raw_ids:
            raise ValueError("DUPLICATE_EXACT_REQUEST_BYTES")
        case_ids.add(case_id)
        raw_ids.add(digest)
        identity = {"schema": CASE_SCHEMA, "case_id": case_id,
                    "request_sha256": digest, "request_canonical_sha256": sha_bytes(request_canonical(request)),
                    "source_lock_sha256": guard["lock_sha256"], "source_files": guard["files"],
                    "external_source_files": guard["external_files"], "requested_cells": count,
                    "resources_sha256": guard["resources_sha256"], "runtime": guard["runtime"],
                    "entrypoint": "cell_enclosure.certify_request", "HH_R10": "OFF",
                    "production_admission": "NOT_ISSUED"}
        rows.append({"case_id": case_id, "request_path": str(path), "request_bytes": len(raw),
                     "identity": identity, "identity_sha256": sha_bytes(canonical(identity))})
    return rows


def case_directory(output, row):
    return Path(output) / "cases" / row["case_id"] / row["identity_sha256"]


def inspect_case(directory, row):
    """Read-only resume; corrupt completion is blocked, never silently replayed."""
    directory = Path(directory)
    if not directory.exists():
        return {"status": "PENDING"}
    if directory.is_symlink():
        raise ValueError("SYMLINK_CASE_DIRECTORY")
    completed = []
    attempts = sorted(directory.glob("attempt-*"))
    for attempt in attempts:
        if attempt.is_symlink() or not attempt.is_dir():
            raise ValueError("INVALID_ATTEMPT_DIRECTORY")
        end = attempt / "COMPLETED.json"
        failed_science = attempt / "NOT_CERTIFIED.json"
        if end.exists() and failed_science.exists():
            raise ValueError("CONFLICTING_TERMINAL_RECEIPTS")
        if not end.exists() and not failed_science.exists():
            continue
        accepted = end.exists()
        end = end if accepted else failed_science
        seal = end.with_suffix(".sha256")
        receipt_raw = read_regular(end)
        if read_regular(seal).decode().strip() != sha_bytes(receipt_raw):
            raise ValueError("TERMINAL_RECEIPT_SEAL_MISMATCH")
        receipt = json.loads(receipt_raw)
        required_status = "COMPLETED" if accepted else "NOT_CERTIFIED_PRESERVED"
        if (receipt.get("status") != required_status or receipt.get("identity") != row["identity"]
                or receipt.get("identity_sha256") != row["identity_sha256"]
                or receipt.get("attempt") != attempt.name or (attempt / "FAILED.json").exists()):
            raise ValueError("COMPLETED_IDENTITY_MISMATCH")
        for name in ("REQUEST.json", "IDENTITY.json", "RESULT_UNVERIFIED.json", "result.json"):
            checked(attempt / name, receipt["artifacts"][name])
        if receipt["artifacts"]["RESULT_UNVERIFIED.json"] != receipt["artifacts"]["result.json"]:
            raise ValueError("COMPLETED_RETURNED_RESULT_MISMATCH")
        if receipt["artifacts"]["REQUEST.json"] != row["identity"]["request_sha256"]:
            raise ValueError("COMPLETED_INPUT_MISMATCH")
        if receipt["artifacts"]["IDENTITY.json"] != sha_bytes(canonical(row["identity"])):
            raise ValueError("COMPLETED_IDENTITY_ARTIFACT_MISMATCH")
        result = json.loads(read_regular(attempt / "result.json"))
        validate_result(result, row)
        if (receipt.get("scientific_status") != result["status"] or accepted != (
                result["status"] == "PASS_REQUESTED_PREFIX")):
            raise ValueError("TERMINAL_SCIENTIFIC_STATUS_MISMATCH")
        if accepted:
            completed.append({"status": "SKIPPED_COMPLETED", "attempt": attempt.name,
                              "receipt_sha256": sha_bytes(receipt_raw),
                              "scientific_status": receipt["scientific_status"]})
    if len(completed) > 1:
        raise ValueError("MULTIPLE_COMPLETED_ATTEMPTS")
    if completed:
        return completed[0]
    if attempts:
        return {"status": "PRIOR_ATTEMPT_PRESERVED", "attempts": [a.name for a in attempts]}
    return {"status": "PENDING"}


def validate_result(result, row):
    if (not isinstance(result, dict) or result.get("status") not in (
            "PASS_REQUESTED_PREFIX", "NOT_CERTIFIED_REQUESTED_PREFIX")):
        raise ValueError("UNRECOGNIZED_CERTIFY_REQUEST_STATUS")
    if (result.get("case_id") != row["case_id"] or result.get("request_sha256") !=
            row["identity"]["request_canonical_sha256"]):
        raise ValueError("ENGINE_RESULT_REQUEST_IDENTITY_MISMATCH")
    count = row["identity"]["requested_cells"]
    enclosed = result.get("enclosed_cells")
    if (result.get("requested_cells") != count or type(enclosed) is not int
            or not 0 <= enclosed <= count or (result["status"] == "PASS_REQUESTED_PREFIX") != (
                enclosed == count)):
        raise ValueError("ENGINE_RESULT_PREFIX_COVERAGE_MISMATCH")


@contextlib.contextmanager
def case_lock(directory):
    mkdir_safe(directory)
    path = Path(directory) / "case.lock"
    if path.is_symlink():
        raise ValueError("SYMLINK_CASE_LOCK")
    with path.open("a+b") as f:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def _engine(guard):
    root = Path(guard["source_root"])
    for rel in guard["files"]:
        p = PurePosixPath(rel)
        if len(p.parts) == 1 and p.suffix == ".py" and p.stem in sys.modules:
            loaded = getattr(sys.modules[p.stem], "__file__", None)
            if p.stem != "run_enclosures" and (loaded is None or Path(loaded).resolve() != root / rel):
                raise ValueError("FOREIGN_PINNED_MODULE_ALREADY_IMPORTED:" + p.stem)
    sys.path.insert(0, str(root))
    path = root / "cell_enclosure.py"
    spec = importlib.util.spec_from_file_location("_phys77_engine_" + guard["lock_sha256"], path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    allowed = {safe_relative(root, rel).resolve() for rel in guard["files"]}
    for imported in tuple(sys.modules.values()):
        filename = getattr(imported, "__file__", None)
        if filename:
            path = Path(filename).resolve()
            if path.is_relative_to(root) and path.suffix == ".py" and path not in allowed:
                raise ValueError("UNPINNED_LOCAL_MODULE_IMPORTED:" + str(path))
    verify_sources(guard)
    function = getattr(module, "certify_request", None)
    if not callable(function):
        raise ValueError("MISSING_CERTIFY_REQUEST")
    return function


def execute_case(task, *, worker=None):
    """worker injection is solely for fake-worker tests, never a CLI option."""
    row, guard = task["row"], task["guard"]
    directory = case_directory(task["output"], row)
    try:
        with case_lock(directory):
            previous = inspect_case(directory, row)
            if previous["status"] == "SKIPPED_COMPLETED":
                return {"case_id": row["case_id"], **previous, "new_enclosure_calls": 0}
            if previous["status"] == "PRIOR_ATTEMPT_PRESERVED" and not task.get("retry_failed", False):
                return {"case_id": row["case_id"], **previous, "new_enclosure_calls": 0}
            attempt = directory / ("attempt-" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-" + uuid.uuid4().hex)
            attempt.mkdir(exist_ok=False)
            start, cpu = time.monotonic(), time.process_time()
            base = {"schema": "PHYS77_ENCLOSURE_ATTEMPT_V1", "identity": row["identity"],
                    "identity_sha256": row["identity_sha256"], "attempt": attempt.name,
                    "started_utc": utc(), "pid": os.getpid(), "new_ODE_calls": 0,
                    "execution_site_label": task.get("site", "local"),
                    "host": platform.node(),
                    "engine_NCP_jobs_is_not_runner_dispatch_count": True,
                    "costs_are_execution_accounting_not_benchmark": True}
            write_new(attempt / "STARTED.json", {**base, "status": "STARTED"})
            calls = 0
            try:
                verify_sources(guard)
                raw = checked(row["request_path"], row["identity"]["request_sha256"], limit=MAX_REQUEST_BYTES)
                request = json.loads(raw)
                write_new(attempt / "REQUEST.json", raw)
                write_new(attempt / "IDENTITY.json", row["identity"])
                function = worker if worker is not None else _engine(guard)
                calls = 1
                result = function(request)  # the only scientific entry point; no ODE dispatch
                result_raw = canonical(result)
                # Preserve the first JSON result before any post-call check.
                # A changing input/source or a malformed scientific identity
                # must not erase the computed result or silently adopt it.
                write_new(attempt / "RESULT_UNVERIFIED.json", result_raw)
                validate_result(result, row)
                verify_sources(guard)
                checked(row["request_path"], row["identity"]["request_sha256"], limit=MAX_REQUEST_BYTES)
                write_new(attempt / "result.json", result_raw)
                accepted = result["status"] == "PASS_REQUESTED_PREFIX"
                status = "COMPLETED" if accepted else "NOT_CERTIFIED_PRESERVED"
                terminal = "COMPLETED" if accepted else "NOT_CERTIFIED"
                receipt = {**base, "status": status, "finished_utc": utc(),
                           "new_enclosure_calls": calls, "scientific_status": result["status"],
                           "scope": "EXPLICIT_REQUESTED_PREFIX_OF_PINNED_FINITE_OWNER_ONLY",
                           "full_trajectory_or_physical_truncation_admission": False,
                           "explicit_retry_required": not accepted,
                           "case_wall_s": time.monotonic() - start, "case_cpu_s": time.process_time() - cpu,
                           "artifacts": {"REQUEST.json": sha_bytes(raw),
                                         "IDENTITY.json": sha_bytes(canonical(row["identity"])),
                                         "RESULT_UNVERIFIED.json": sha_bytes(result_raw),
                                         "result.json": sha_bytes(result_raw)}}
                receipt_raw = canonical(receipt)
                write_new(attempt / (terminal + ".json"), receipt_raw)
                write_new(attempt / (terminal + ".sha256"), (sha_bytes(receipt_raw) + "\n").encode())
                return {"case_id": row["case_id"], "status": status, "attempt": attempt.name,
                        "new_enclosure_calls": calls, "scientific_status": result["status"],
                        "receipt_sha256": sha_bytes(receipt_raw)}
            except BaseException as exc:
                failure = {**base, "status": "FAILED_PRESERVED", "finished_utc": utc(),
                           "new_enclosure_calls": calls, "error_type": type(exc).__name__,
                           "error": str(exc), "traceback": traceback.format_exc(),
                           "case_wall_s": time.monotonic() - start, "case_cpu_s": time.process_time() - cpu}
                provisional = attempt / "RESULT_UNVERIFIED.json"
                if provisional.is_file():
                    failure["unverified_result_sha256"] = sha_bytes(read_regular(provisional))
                    failure["unverified_result_is_not_accepted"] = True
                write_new(attempt / "FAILED.json", failure)
                return {"case_id": row["case_id"], "status": "FAILED_PRESERVED", "attempt": attempt.name,
                        "new_enclosure_calls": calls, "error": str(exc)}
    except BlockingIOError:
        return {"case_id": row["case_id"], "status": "PENDING_CASE_LOCK", "new_enclosure_calls": 0}
    except Exception as exc:
        return {"case_id": row["case_id"], "status": "BLOCKED_CORRUPT_OR_UNSAFE_OUTPUT",
                "new_enclosure_calls": 0, "error": str(exc)}


def resource_slots(*, affinity_cpus, quota_cpus, busy_cores, load1, host_cpus,
                   available_gib, capacity_gib, reserve_gib, job_gib,
                   leased_cpus=0, leased_gib=0.0):
    """Conservative admission estimate; shared leases remain a separate guard."""
    if (not math.isfinite(reserve_gib) or reserve_gib < 0
            or not math.isfinite(job_gib) or job_gib <= 0):
        raise ValueError("INVALID_MEMORY_BUDGET")
    cap = min(MAX_CPUS, max(0, int(affinity_cpus)))
    if quota_cpus is not None:
        cap = min(cap, max(0, math.floor(quota_cpus)))
    capacity = min(MAX_MEMORY_GIB, capacity_gib)
    # Global load is an approximate constraint, scaled to this CPU allocation.
    # It is not interpreted as the load of this cgroup or of other users' jobs.
    projected_load = max(0.0, load1) * cap / max(1, host_cpus)
    affinity_idle = max(0.0, affinity_cpus - max(0.0, busy_cores))
    cpus = min(max(0, cap - leased_cpus), math.floor(affinity_idle),
               max(0, math.floor(cap - projected_load)))
    memory = min(max(0.0, available_gib - reserve_gib),
                 max(0.0, capacity - reserve_gib - leased_gib))
    return max(0, min(cpus, math.floor(memory / job_gib)))


def _resource_module(path):
    checked(path, RESOURCE_SHA256)
    spec = importlib.util.spec_from_file_location("_phys77_hh74_resources", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sample_resources(module, reserve_gib, job_gib):
    affinity = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count() or 1
    quota = None
    quota_paths = []
    for p in module._cgroups():
        try:
            q, period = (p / "cpu.max").read_text().split()
            if q != "max":
                value = int(q) / int(period)
                quota = value if quota is None else min(quota, value)
                quota_paths.append({"path": str(p / "cpu.max"), "cores": value})
        except (OSError, ValueError, ZeroDivisionError):
            pass
    free, capacity = module.memory_available()
    try:
        load = os.getloadavg()[0]
    except OSError:
        load = 0.0
    observation = {"affinity_cpus": affinity, "quota_cpus": quota,
                   "busy_cores": module.busy_cores(), "load1": load,
                   "host_cpus": os.cpu_count() or 1, "available_gib": free / GIB,
                   "capacity_gib": capacity / GIB, "reserve_gib": reserve_gib,
                   "job_gib": job_gib}
    observation["admissible_slots"] = resource_slots(**observation)
    observation.update(observed_utc=utc(), quota_paths=quota_paths,
                       admission_CPU_ceiling=MAX_CPUS, admission_RAM_ceiling_gib=MAX_MEMORY_GIB)
    return observation


class SharedAdmission:
    def __init__(self, resources_path, lease_dir, reserve_gib, job_gib):
        self.module = _resource_module(resources_path)
        if self.module._start(os.getpid()) in (None, "DEAD"):
            raise RuntimeError("SHARED_PID_NAMESPACE_LIVENESS_UNOBSERVABLE")
        self.reserve, self.job = reserve_gib, job_gib
        base = self.module.LeasePool

        class NonblockingPool(base):
            @contextlib.contextmanager
            def locked(self):
                with (self.path / "leases.lock").open("a+") as stream:
                    fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    try:
                        yield
                    finally:
                        fcntl.flock(stream, fcntl.LOCK_UN)

        self.pool = NonblockingPool(lease_dir, max_cpus=MAX_CPUS,
                                    memory_gib=MAX_MEMORY_GIB, reserve_gib=reserve_gib, job_gib=job_gib)
        # HH74 acquire uses capacity, not cap. Keep the shared source immutable.
        self.pool.capacity = min(MAX_CPUS, self.pool.capacity)
        self.pool.cap = min(MAX_CPUS, self.pool.cap)

    def acquire(self, task):
        try:
            obs = sample_resources(self.module, self.reserve, self.job)
            if obs["admissible_slots"] == 0:
                return None, obs
            key, lease_obs = self.pool.acquire(task)
            return key, {**obs, "shared_lease_observation": lease_obs}
        except (OSError, ValueError, RuntimeError) as exc:
            return None, {"status": "PENDING_SHARED_LEASE_OR_RESOURCE_OBSERVATION", "error": str(exc)}

    def handoff(self, key, child_pid):
        """Bind liveness to the actual worker before it can call the engine."""
        with self.pool.locked():
            path = self.pool.path / ("lease-" + key + ".json")
            record = json.loads(path.read_text())
            if record["owner"] != self.pool.owner:
                raise RuntimeError("FOREIGN_LEASE_HANDOFF_REFUSED")
            tick = self.module._start(child_pid)
            if tick in (None, "DEAD"):
                raise RuntimeError("WORKER_LIVENESS_NOT_OBSERVED")
            record.update(pid=child_pid, start=tick, dispatcher_pid=os.getpid(), worker_handoff=True)
            tmp = path.with_name(path.name + ".own-" + uuid.uuid4().hex)
            try:
                with tmp.open("x") as stream:
                    json.dump(record, stream, sort_keys=True)
                    stream.write("\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(tmp, path)  # own ephemeral lease only, not science artifacts
            finally:
                tmp.unlink(missing_ok=True)

    def release(self, key):
        try:
            self.pool.release(key)
            return None
        except (OSError, ValueError, RuntimeError) as exc:
            return str(exc)  # worker is joined; source protocol later prunes dead lease


def preflight(requests, output, source_lock, resources_path=DEFAULT_RESOURCES,
              *, retry_failed=False):
    guard = load_source_lock(source_lock, resources_path)
    rows = load_requests(requests, guard)
    states = []
    for row in rows:
        try:
            current = inspect_case(case_directory(output, row), row)
        except Exception as exc:
            current = {"status": "BLOCKED_CORRUPT_OR_UNSAFE_OUTPUT", "error": str(exc)}
        current = {"case_id": row["case_id"], "identity_sha256": row["identity_sha256"], **current}
        current["eligible"] = current["status"] == "PENDING" or (
            retry_failed and current["status"] == "PRIOR_ATTEMPT_PRESERVED")
        states.append(current)
    return {"guard": guard, "rows": rows, "states": states,
            "status": "PREFLIGHT_COMPLETE_NO_ENGINE_IMPORT_NO_ODE",
            "eligible_cases": sum(s["eligible"] for s in states),
            "completed_skipped": sum(s["status"] == "SKIPPED_COMPLETED" for s in states),
            "blocked_or_prior": sum(not s["eligible"] and s["status"] != "SKIPPED_COMPLETED" for s in states)}


def _child(task, gate, sender):
    try:
        # Cooperative handshake only; no engine import before worker lease handoff.
        if not gate.wait(timeout=10.0):
            result = {"case_id": task["row"]["case_id"], "status": "PENDING_LEASE_HANDOFF",
                      "new_enclosure_calls": 0}
        else:
            result = execute_case(task)
        sender.send(result)
    finally:
        sender.close()


def run_batch(bundle, output, *, workers, max_new_cases, memory_reserve_gib=16.0,
              job_memory_gib=1.0, lease_dir=DEFAULT_LEASES, retry_failed=False,
              admission=None, max_dispatch_seconds=300.0, site="local"):
    if not isinstance(workers, int) or workers < 1:
        raise ValueError("WORKERS_MUST_BE_POSITIVE")
    if not isinstance(max_new_cases, int) or not 0 <= max_new_cases <= MAX_REQUESTS:
        raise ValueError("EXPLICIT_FINITE_MAX_NEW_CASES_REQUIRED")
    if not math.isfinite(max_dispatch_seconds) or max_dispatch_seconds <= 0:
        raise ValueError("INVALID_DISPATCH_HORIZON")
    if site not in ("local", "ncp") or (site == "ncp" and memory_reserve_gib < 16):
        raise ValueError("INVALID_SITE_OR_NCP_RESERVE_BELOW_16_GIB")
    resource_slots(affinity_cpus=1, quota_cpus=1, busy_cores=0, load1=0, host_cpus=1,
                   available_gib=128, capacity_gib=128, reserve_gib=memory_reserve_gib,
                   job_gib=job_memory_gib)
    verify_sources(bundle["guard"])
    cap = min(MAX_CPUS, workers)
    eligible = {s["case_id"] for s in bundle["states"] if s["eligible"]}
    pending = [r for r in bundle["rows"] if r["case_id"] in eligible]
    summary = {"schema": "PHYS77_ENCLOSURE_RUN_CHECKPOINT_V1", "started_utc": utc(),
               "requested_workers": workers, "worker_ceiling": cap, "max_new_cases": max_new_cases,
               "prior_states": bundle["states"], "results": [], "resource_observations": [],
               "launched_jobs": 0, "new_ODE_calls": 0, "max_active_observed": 0,
               "execution_site_label": site, "host": platform.node(),
               "site_label_is_operator_assertion_not_remote_host_verification": True,
               "engine_NCP_jobs_is_not_runner_dispatch_count": True,
               "memory_reserve_gib": memory_reserve_gib, "job_memory_gib": job_memory_gib,
               "resource_limits_are_advisory_not_kernel_reservation": True,
               "HH_R10": "OFF", "production_admission": "NOT_ISSUED",
               "costs_are_execution_accounting_not_benchmark": True,
               "dispatch_horizon_is_not_worker_hard_timeout": True}
    output = Path(output).resolve()
    mkdir_safe(output / "checkpoints")
    run_id = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-" + uuid.uuid4().hex
    write_new(output / "checkpoints" / (run_id + "-STARTED.json"), summary)
    started = time.monotonic()
    if pending and max_new_cases:
        if admission is None:
            try:
                admission = SharedAdmission(bundle["guard"]["resources_path"], lease_dir,
                                            memory_reserve_gib, job_memory_gib)
            except (OSError, ValueError, RuntimeError) as exc:
                summary["deferral"] = "PENDING_SHARED_LEASE_UNAVAILABLE_NO_UNCOORDINATED_FALLBACK"
                summary["resource_error"] = str(exc)
    active, launched, dispatch_allowed = {}, 0, True
    ctx = multiprocessing.get_context("spawn")
    while ((pending and launched < max_new_cases and admission is not None and dispatch_allowed) or active):
        while (pending and launched < max_new_cases and len(active) < cap and dispatch_allowed
               and time.monotonic() - started < max_dispatch_seconds):
            try:
                verify_sources(bundle["guard"])
            except Exception as exc:
                summary["deferral"] = "SOURCE_CHANGED_STOP_NEW_DISPATCH_PRESERVE_ACTIVE"
                summary["source_error"] = str(exc)
                dispatch_allowed = False
                break
            row = pending[0]
            key, observation = admission.acquire("PHYS77_ENCLOSURE:" + row["case_id"])
            summary["resource_observations"].append(observation)
            if key is None:
                summary["deferral"] = "PENDING_RESOURCE_SHARE_OTHER_WORK_CONTINUES"
                break
            receiver, sender = ctx.Pipe(duplex=False)
            gate = ctx.Event()
            task = {"row": row, "guard": bundle["guard"], "output": str(output),
                    "retry_failed": retry_failed, "site": site}
            process = ctx.Process(target=_child, args=(task, gate, sender))
            try:
                process.start()
                sender.close()
            except BaseException as exc:
                sender.close()
                receiver.close()
                admission.release(key)
                summary["deferral"] = "WORKER_START_FAILED_NO_ENGINE_CALL"
                summary["start_error"] = repr(exc)
                dispatch_allowed = False
                break
            active[process.pid] = {"process": process, "receiver": receiver,
                                   "key": key, "row": row, "payload": None, "gate": gate}
            pending.pop(0)
            launched += 1
            try:
                admission.handoff(key, process.pid)
                gate.set()
            except (OSError, ValueError, RuntimeError) as exc:
                summary["resource_observations"].append({"status": "HANDOFF_DEFERRED_NO_ENGINE_CALL",
                                                         "case_id": row["case_id"], "error": str(exc)})
                # Gate stays closed; child returns pending after its bounded10s wait.
            summary["max_active_observed"] = max(summary["max_active_observed"], len(active))
        if not active:
            break
        for pid, item in list(active.items()):
            process, receiver = item["process"], item["receiver"]
            if item["payload"] is None and receiver.poll():
                try:
                    item["payload"] = receiver.recv()
                except EOFError:
                    item["payload"] = {"case_id": item["row"]["case_id"],
                                       "status": "WORKER_EXIT_WITHOUT_RECEIPT_PRESERVED"}
            if process.exitcode is not None:
                process.join(timeout=0.05)
                if item["payload"] is None and receiver.poll(0.05):
                    try:
                        item["payload"] = receiver.recv()
                    except EOFError:
                        pass
                result = item["payload"] or {"case_id": item["row"]["case_id"],
                                              "status": "WORKER_EXIT_WITHOUT_RECEIPT_PRESERVED"}
                result["worker_exit_code"] = process.exitcode
                summary["results"].append(result)
                release_error = admission.release(item["key"])
                if release_error:
                    summary["resource_observations"].append({"dead_worker_lease_cleanup_deferred": release_error})
                receiver.close()
                process.close()
                del active[pid]
        if active:
            time.sleep(0.05)
        if time.monotonic() - started >= max_dispatch_seconds:
            summary["deferral"] = "DISPATCH_HORIZON_REACHED_ACTIVE_WORK_FINISHES"
            if not active:
                break
    summary.update(finished_utc=utc(), invocation_wall_s=time.monotonic() - started,
                   launched_jobs=launched, undispatched_cases=[r["case_id"] for r in pending],
                   new_enclosure_calls=sum(r.get("new_enclosure_calls", 0) for r in summary["results"]))
    bad = any(s["status"] == "BLOCKED_CORRUPT_OR_UNSAFE_OUTPUT" for s in bundle["states"]) or any(
        r["status"] in ("FAILED_PRESERVED", "BLOCKED_CORRUPT_OR_UNSAFE_OUTPUT", "WORKER_EXIT_WITHOUT_RECEIPT_PRESERVED")
        for r in summary["results"])
    deferred = bool(pending or bundle["blocked_or_prior"] or any(
        r["status"].startswith(("PENDING", "PRIOR")) for r in summary["results"]))
    uncertified = any(r["status"] == "NOT_CERTIFIED_PRESERVED" for r in summary["results"])
    summary["status"] = ("PARTIAL_FAILURE_PRESERVED" if bad else "NONCERTIFIED_ATTEMPTS_PRESERVED"
                         if uncertified else "PENDING_CHECKPOINT" if deferred else "COMPLETE_SELECTED_REQUESTS")
    summary["accepted_completions"] = sum(r["status"] == "COMPLETED" for r in summary["results"])
    summary["noncertified_attempts"] = sum(r["status"] == "NOT_CERTIFIED_PRESERVED" for r in summary["results"])
    write_new(output / "checkpoints" / (run_id + "-FINISHED.json"), summary)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--run", action="store_true")
    parser.add_argument("--requests", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-lock", type=Path, default=HERE / "RUNNER_SOURCE_LOCK.json")
    parser.add_argument("--resources-file", type=Path, default=DEFAULT_RESOURCES)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--memory-reserve-gib", type=float, default=16.0)
    parser.add_argument("--job-memory-gib", type=float, default=1.0)
    parser.add_argument("--max-new-cases", type=int)
    parser.add_argument("--max-dispatch-seconds", type=float, default=300.0)
    parser.add_argument("--lease-dir", default=DEFAULT_LEASES)
    parser.add_argument("--site", choices=("local", "ncp"), default="local",
                        help="Recorded execution-site assertion; NCP requires at least 16 GiB reserve.")
    parser.add_argument("--retry-failed", action="store_true",
                        help="Explicit distinct attempt for failed/interrupted/noncertified requests; completed/corrupt results never replay.")
    args = parser.parse_args(argv)
    if args.run and args.max_new_cases is None:
        parser.error("--run requires explicit --max-new-cases (0 is allowed)")
    if args.site == "ncp" and args.memory_reserve_gib < 16:
        parser.error("--site ncp requires --memory-reserve-gib of at least 16")
    bundle = preflight(args.requests, args.output, args.source_lock, args.resources_file,
                       retry_failed=args.retry_failed)
    if args.preflight:
        result = {k: v for k, v in bundle.items() if k != "rows"}
        module = _resource_module(args.resources_file)
        result["resource_snapshot"] = sample_resources(module, args.memory_reserve_gib, args.job_memory_gib)
        result["resource_snapshot"]["shared_pid_liveness_observed"] = module._start(os.getpid()) not in (None, "DEAD")
        result["resource_snapshot"]["lease_path_not_mutated_or_acquired_in_preflight"] = True
        result["execution_site_label"] = args.site
    else:
        result = run_batch(bundle, args.output, workers=args.workers,
                           max_new_cases=args.max_new_cases, memory_reserve_gib=args.memory_reserve_gib,
                           job_memory_gib=args.job_memory_gib, lease_dir=args.lease_dir,
                           retry_failed=args.retry_failed, max_dispatch_seconds=args.max_dispatch_seconds,
                           site=args.site)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 1 if result.get("status") == "PARTIAL_FAILURE_PRESERVED" else 2 if result.get(
        "status") == "NONCERTIFIED_ATTEMPTS_PRESERVED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
