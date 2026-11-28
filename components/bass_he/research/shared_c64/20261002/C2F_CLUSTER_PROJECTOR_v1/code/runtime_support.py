"""Bounded manufactured-work runtime helpers; no physical launch interface."""
from __future__ import annotations
import hashlib
import json
import math
import os
from pathlib import Path
import re
import socket
import tempfile
import time

SCHEMA = "bass-he.c2f.manufactured.v1"
GIB = 1024**3
BLAS_ENV = ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS")

class ContractError(ValueError):
    pass


def _keys(value, expected, where):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ContractError(f"{where}: exact keys required: {sorted(expected)}")


def _integer(value, lo, hi, where):
    if type(value) is not int or not lo <= value <= hi:
        raise ContractError(f"{where}: integer in [{lo}, {hi}] required")


def _finite(value, lo, hi, where, positive=False):
    if type(value) not in (int, float) or not math.isfinite(value) or not lo <= value <= hi or (positive and value <= 0):
        raise ContractError(f"{where}: finite number in [{lo}, {hi}] required")


def validate_manifest(value):
    """Closed schema. These bounds authorize manufactured matrices only."""
    _keys(value, ("schema", "physical_launch_enabled", "cases", "limits"), "manifest")
    if value["schema"] != SCHEMA or value["physical_launch_enabled"] is not False:
        raise ContractError("manufactured schema and literal physical_launch_enabled=false required")
    cases = value["cases"]
    if not isinstance(cases, list) or not 1 <= len(cases) <= 64:
        raise ContractError("cases: list of 1..64 cases required")
    seen = set()
    for i, case in enumerate(cases):
        label = f"cases[{i}]"
        _keys(case, ("case_id", "seed", "n_rows", "rank", "angle"), label)
        cid = case["case_id"]
        if not isinstance(cid, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", cid) or cid in seen:
            raise ContractError(f"{label}: safe unique ASCII case_id required")
        seen.add(cid)
        _integer(case["seed"], 0, 2**63-1, label + ".seed")
        _integer(case["rank"], 1, 6, label + ".rank")
        _integer(case["n_rows"], 2*case["rank"]+1, 65536, label + ".n_rows")
        _finite(case["angle"], 0, 1.2, label + ".angle")
    limits = value["limits"]
    _keys(limits, ("wall_seconds", "memory_gib", "max_ranks", "max_threads_per_rank"), "limits")
    _finite(limits["wall_seconds"], 0, 86400, "limits.wall_seconds", positive=True)
    _finite(limits["memory_gib"], 0, 128, "limits.memory_gib", positive=True)
    _integer(limits["max_ranks"], 1, 64, "limits.max_ranks")
    _integer(limits["max_threads_per_rank"], 1, 64, "limits.max_threads_per_rank")
    return value


def load_manifest(path):
    def reject_constant(token):
        raise ContractError(f"nonfinite JSON token: {token}")
    def unique_keys(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ContractError(f"duplicate JSON key: {key}")
            value[key] = item
        return value
    return validate_manifest(json.loads(Path(path).read_text(), parse_constant=reject_constant, object_pairs_hook=unique_keys))


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def file_identity(path):
    p = Path(path).resolve(strict=True)
    if not p.is_file():
        raise ContractError(f"regular file required: {p}")
    return {"path": str(p), "bytes": p.stat().st_size, "sha256": sha256_file(p)}


def code_identity(code_dir):
    return {p.name: file_identity(p) for p in sorted(Path(code_dir).glob("*.py"))}


def atomic_create(path, value):
    """Create-only durable JSON: fsync temporary bytes, link, fsync directory."""
    p = Path(path)
    payload = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode()
    fd, temp = tempfile.mkstemp(prefix=f".{p.name}.pending-", dir=p.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temp, p)
        dfd = os.open(p.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        os.unlink(temp)


def _text(path):
    try:
        return Path(path).read_text().strip()
    except (FileNotFoundError, PermissionError):
        return None


def _cgroup_v2_paths():
    """Current membership plus visible ancestors, including namespaced root."""
    membership = _text("/proc/self/cgroup") or ""
    rel = next((row[3:] for row in membership.splitlines() if row.startswith("0::")), None)
    root = Path("/sys/fs/cgroup")
    if rel is None or not root.exists():
        return []
    current = (root / rel.lstrip("/")).resolve()
    if not current.is_relative_to(root):
        raise ContractError("cgroup membership outside visible root")
    if not current.exists():
        raise ContractError("cgroup membership not visible; cannot measure limits")
    return [current, *[p for p in current.parents if p == root or p.is_relative_to(root)]]


def host_preflight():
    if not hasattr(os, "sched_getaffinity"):
        raise ContractError("Linux sched_getaffinity is required")
    affinity = sorted(os.sched_getaffinity(0))
    if not affinity:
        raise ContractError("empty CPU affinity")
    quota_limits, memory_limits, evidence = [], [], []
    cgroups = _cgroup_v2_paths()
    # This runner is explicitly validated for Linux cgroup v2. Refuse a v1-only
    # container rather than silently treating an invisible quota as unlimited.
    cgroup_text = _text("/proc/self/cgroup") or ""
    if cgroup_text.strip() and not cgroups:
        raise ContractError("cgroup v1 or inaccessible cgroup limits unsupported")
    for path in cgroups:
        cpu, memory, current = (_text(path / name) for name in ("cpu.max", "memory.max", "memory.current"))
        evidence.append({"path": str(path), "cpu.max": cpu, "memory.max": memory, "memory.current": current})
        if cpu and not cpu.startswith("max "):
            quota, period = map(int, cpu.split())
            if quota <= 0 or period <= 0:
                raise ContractError("invalid cgroup CPU quota")
            quota_limits.append(quota/period)
        if memory and memory != "max":
            if current is None:
                raise ContractError("finite cgroup memory.max without memory.current")
            memory_limits.append((int(memory), max(0, int(memory)-int(current))))
    meminfo = {}
    for row in Path("/proc/meminfo").read_text().splitlines():
        parts = row.split()
        if len(parts) >= 2 and parts[0] in ("MemTotal:", "MemAvailable:"):
            meminfo[parts[0][:-1]] = int(parts[1])*1024
    if "MemAvailable" not in meminfo:
        raise ContractError("MemAvailable unavailable")
    cores = {}
    for cpu in affinity:
        topo = Path(f"/sys/devices/system/cpu/cpu{cpu}/topology")
        package, core = _text(topo / "physical_package_id"), _text(topo / "core_id")
        if package is not None and core is not None:
            cores.setdefault(f"{package}:{core}", []).append(cpu)
    budget = min([float(len(affinity)), *quota_limits])
    return {
        "hostname": socket.gethostname(), "affinity_cpus": affinity,
        "affinity_count": len(affinity), "physical_cores_in_affinity": cores,
        "cgroup_evidence": evidence, "cpu_quota_cores": min(quota_limits) if quota_limits else None,
        "effective_cpu_budget": budget,
        "memory_total_bytes": min([meminfo["MemTotal"], *[x[0] for x in memory_limits]]),
        "memory_available_bytes": min([meminfo["MemAvailable"], *[x[1] for x in memory_limits]]),
        "captured_unix_seconds": time.time(),
        "NCP64_actual_scaling": "NOT_CLAIMED",
    }


def validate_request(manifest, execution, backend, native_library, ranks, threads, binding, host):
    validate_manifest(manifest)
    if execution not in ("serial", "mpi") or backend not in ("reference", "native"):
        raise ContractError("explicit execution and backend required; no fallback")
    if binding not in ("none", "core"):
        raise ContractError("binding must be none or core")
    if execution == "serial" and ranks != 1:
        raise ContractError("serial execution requires exactly one rank")
    lim = manifest["limits"]
    _integer(ranks, 1, lim["max_ranks"], "requested ranks")
    _integer(threads, 1, lim["max_threads_per_rank"], "requested threads")
    if ranks * threads > host["effective_cpu_budget"]:
        raise ContractError("rank×thread request exceeds pre-MPI host CPU budget")
    if binding == "core" and len(host["physical_cores_in_affinity"]) < ranks*threads:
        raise ContractError("not enough measured physical cores for core binding")
    if lim["memory_gib"]*GIB > host["memory_available_bytes"]:
        raise ContractError("memory budget exceeds current measured available host memory")
    if backend == "native":
        if not native_library:
            raise ContractError("native backend requires an explicit native library")
        file_identity(native_library)
    elif native_library is not None:
        raise ContractError("reference backend must not receive a native library")


def execution_environment(threads, binding):
    env = os.environ.copy()
    env.update({name: "1" for name in BLAS_ENV})
    env.update({"OMP_NUM_THREADS": str(threads), "OMP_DYNAMIC": "FALSE",
                "OMP_PROC_BIND": "FALSE" if binding == "none" else "close", "OMP_PLACES": "cores"})
    return env


def verify_thread_environment(threads, binding):
    expected = {name: "1" for name in BLAS_ENV}
    expected.update({"OMP_NUM_THREADS": str(threads), "OMP_DYNAMIC": "FALSE",
                     "OMP_PROC_BIND": "FALSE" if binding == "none" else "close", "OMP_PLACES": "cores"})
    if any(os.environ.get(k) != v for k, v in expected.items()):
        raise ContractError("worker thread environment differs from explicit launch context")
    return expected
