"""Linux affinity/cgroup-aware inventory, plus a subprocess resource wrapper."""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import resource
import sys


def parse_cpu_list(value: str) -> set[int]:
    result = set()
    for part in value.strip().split(","):
        if not part:
            continue
        bounds = part.split("-")
        if len(bounds) == 1:
            result.add(int(bounds[0]))
        elif len(bounds) == 2:
            lo, hi = map(int, bounds)
            if lo < 0 or hi < lo:
                raise ValueError("invalid CPU range")
            result.update(range(lo, hi + 1))
        else:
            raise ValueError("invalid CPU list")
    if any(x < 0 for x in result):
        raise ValueError("negative CPU number")
    return result


def _read(path):
    try:
        return Path(path).read_text().strip()
    except (OSError, UnicodeError):
        return None


def _cgroup_paths():
    """Visible cgroup v2 ancestry; cgroup v1 is explicitly not certified."""
    root = Path("/sys/fs/cgroup")
    value = _read("/proc/self/cgroup") or ""
    for line in value.splitlines():
        if line.startswith("0::"):
            relative = line[3:].lstrip("/")
            candidate = root / relative
            # Namespaced mounts may expose the task cgroup directly at root.
            if not candidate.is_dir() or ".." in Path(relative).parts:
                candidate = root
            return [p for p in (candidate, *candidate.parents) if p == root or root in p.parents]
    return []


def probe_host() -> dict:
    affinity = set(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else set(range(os.cpu_count() or 1))
    allowed = set(affinity)
    quotas, memory_limits, memory_remaining, cgroups = [], [], [], []
    for folder in _cgroup_paths():
        entry = {"path": str(folder)}
        cpuset = _read(folder / "cpuset.cpus.effective")
        if cpuset:
            allowed &= parse_cpu_list(cpuset)
            entry["cpuset.cpus.effective"] = cpuset
        cpu_max = _read(folder / "cpu.max")
        if cpu_max:
            entry["cpu.max"] = cpu_max
            quota, period = cpu_max.split()
            if quota != "max":
                quotas.append(int(quota) / int(period))
        mem_max, mem_current = _read(folder / "memory.max"), _read(folder / "memory.current")
        if mem_max and mem_max != "max":
            limit = int(mem_max)
            memory_limits.append(limit)
            entry["memory.max"] = limit
            if mem_current:
                entry["memory.current"] = int(mem_current)
                memory_remaining.append(max(0, limit - int(mem_current)))
        cgroups.append(entry)
    if not allowed:
        raise RuntimeError("empty affinity/cgroup CPU intersection")
    topology = []
    topology_complete = True
    for cpu in sorted(allowed):
        base = Path(f"/sys/devices/system/cpu/cpu{cpu}/topology")
        package, core = _read(base / "physical_package_id"), _read(base / "core_id")
        if package is None or core is None:
            topology_complete = False
        topology.append({"logical_cpu": cpu, "package_id": package, "core_id": core})
    physical = len({(t["package_id"], t["core_id"]) for t in topology}) if topology_complete else None
    quota = min(quotas) if quotas else None
    # A sub-one-CPU quota can run one process, with reduced time allocation.
    logical_budget = min(len(allowed), max(1, math.floor(quota))) if quota is not None else len(allowed)
    core_budget = min(logical_budget, physical) if physical is not None else None
    meminfo = {}
    for line in (_read("/proc/meminfo") or "").splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[0] in ("MemAvailable:", "MemTotal:"):
            meminfo[fields[0][:-1]] = int(fields[1]) * 1024
    available_values = memory_remaining + ([meminfo["MemAvailable"]] if "MemAvailable" in meminfo else [])
    available = min(available_values) if available_values else None
    return {
        "schema": 1,
        "logical_cpu_count_os": os.cpu_count(),
        "affinity_cpus": sorted(affinity),
        "allowed_logical_cpus": sorted(allowed),
        "allowed_logical_cpu_count": len(allowed),
        "observed_physical_core_count": physical,
        "cpu_quota_cores": quota,
        "logical_cpu_budget": logical_budget,
        "core_binding_cpu_budget": core_budget,
        "topology": topology,
        "cgroup_v2": cgroups,
        "cgroup_status": "V2_VISIBLE_ANCESTRY_INSPECTED" if cgroups else "V2_UNAVAILABLE_V1_NOT_CERTIFIED",
        "host_memory_total_bytes": meminfo.get("MemTotal"),
        "host_memory_available_bytes": meminfo.get("MemAvailable"),
        "cgroup_memory_limit_bytes": min(memory_limits) if memory_limits else None,
        "memory_available_budget_bytes": available,
        "memory_evidence": "SNAPSHOT_NOT_RESERVATION",
        "topology_evidence": "GUEST_OS_REPORTED_NOT_NCP_PHYSICAL_HARDWARE_CERTIFICATE",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--memory-limit-bytes", type=int)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.memory_limit_bytes is None:
        if args.command:
            parser.error("command requires --memory-limit-bytes")
        print(json.dumps(probe_host(), indent=2, sort_keys=True))
        return 0
    if args.memory_limit_bytes <= 0:
        parser.error("positive memory limit required")
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("missing command")
    resource.setrlimit(resource.RLIMIT_AS, (args.memory_limit_bytes, args.memory_limit_bytes))
    os.execvpe(command[0], command, os.environ.copy())
    return 127


if __name__ == "__main__":
    raise SystemExit(main())
