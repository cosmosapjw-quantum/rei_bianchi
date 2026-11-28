"""Linux affinity/cgroup-aware inventory, plus a subprocess resource wrapper."""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import resource
import sys


MEMORY_ACCOUNTING_POLICIES = ("raw-headroom", "clean-file-half-v1")
_CACHE_STAT_KEYS = ("file", "active_file", "inactive_file", "shmem",
                    "file_mapped", "file_dirty", "file_writeback", "unevictable")


def cgroup_memory_budget(limit, current, stat_text, protection_min, protection_low,
                         policy="raw-headroom"):
    """Snapshot estimate; clean-cache credit is not a kernel reservation.

    Linux 6.18 documents reclaimable page cache and the memory.stat categories:
    https://docs.kernel.org/6.18/admin-guide/cgroup-v2.html
    https://docs.kernel.org/6.18/admin-guide/mm/concepts.html
    Half-credit is our conservative engineering policy, not a kernel formula.
    No cgroup, limit, cache, or process state is modified.
    """
    if policy not in MEMORY_ACCOUNTING_POLICIES:
        raise ValueError("unknown memory accounting policy")
    for name, value in (("limit", limit), ("current", current)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a nonnegative integer")
    stats, stat_error = {}, None
    try:
        if not isinstance(stat_text, str) or not stat_text.strip():
            raise ValueError("memory.stat unavailable")
        for line in stat_text.splitlines():
            key, value = line.split()
            if key in stats:
                raise ValueError("duplicate memory.stat key")
            if not value.isdecimal():
                raise ValueError("invalid memory.stat counter")
            stats[key] = int(value)
        if any(key not in stats for key in _CACHE_STAT_KEYS):
            raise ValueError("required memory.stat counter missing")
    except (TypeError, ValueError) as exc:
        stat_error = str(exc)
    credit, candidate = 0, 0
    reason = "RAW_HEADROOM_DEFAULT"
    if policy == "clean-file-half-v1":
        if stat_error:
            reason = "ZERO_CREDIT_INVALID_OR_MISSING_STATS"
        elif protection_min != "0" or protection_low != "0":
            reason = "ZERO_CREDIT_PROTECTION_NONZERO_OR_UNREADABLE"
        else:
            # Deliberately subtract overlapping exclusions separately. Never
            # credit slab, swap, dirty, mapped, shmem or unevictable memory.
            excluded = sum(stats[key] for key in ("shmem", "file_mapped",
                           "file_dirty", "file_writeback", "unevictable"))
            candidate = min(current, max(0, min(stats["file"],
                            stats["active_file"] + stats["inactive_file"]) - excluded))
            credit = candidate // 2
            reason = "HALF_CLEAN_FILE_ESTIMATE_NOT_RECLAIM_GUARANTEE"
    raw = max(0, limit - current)
    # Apply the signed overage before clamping; an over-limit snapshot must
    # not receive its credit on top of an incorrectly zeroed overage.
    estimated = min(limit, max(0, limit - current + credit))
    return {"policy": policy, "raw_headroom_bytes": raw,
            "clean_file_candidate_bytes": candidate, "credited_bytes": credit,
            "available_estimate_bytes": estimated, "credit_reason": reason,
            "memory.stat.raw": stat_text, "memory.stat": stats,
            "memory.stat.error": stat_error,
            "memory.min": protection_min, "memory.low": protection_low}


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


def probe_host(memory_accounting="raw-headroom") -> dict:
    if memory_accounting not in MEMORY_ACCOUNTING_POLICIES:
        raise ValueError("unknown memory accounting policy")
    affinity = set(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else set(range(os.cpu_count() or 1))
    allowed = set(affinity)
    quotas, memory_limits, memory_remaining, raw_remaining, cgroups = [], [], [], [], []
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
            if mem_current is None:
                raise RuntimeError("finite cgroup memory limit with unreadable current usage")
            stat_text = _read(folder / "memory.stat")
            protection_min = _read(folder / "memory.min")
            protection_low = _read(folder / "memory.low")
            mem_current_after = _read(folder / "memory.current")
            if mem_current_after is None:
                raise RuntimeError("cgroup current usage became unreadable")
            current = max(int(mem_current), int(mem_current_after))
            entry["memory.current.before"] = int(mem_current)
            entry["memory.current.after"] = int(mem_current_after)
            entry["memory.current"] = current
            accounting = cgroup_memory_budget(limit, current, stat_text,
                         protection_min, protection_low, memory_accounting)
            entry["memory.accounting"] = accounting
            memory_remaining.append(accounting["available_estimate_bytes"])
            raw_remaining.append(accounting["raw_headroom_bytes"])
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
    if memory_accounting != "raw-headroom" and meminfo.get("MemAvailable", 0) <= 0:
        raise RuntimeError("cache-aware accounting requires host MemAvailable")
    available_values = memory_remaining + ([meminfo["MemAvailable"]] if "MemAvailable" in meminfo else [])
    available = min(available_values) if available_values else None
    raw_values = raw_remaining + ([meminfo["MemAvailable"]] if "MemAvailable" in meminfo else [])
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
        "memory_raw_headroom_budget_bytes": min(raw_values) if raw_values else None,
        "memory_accounting_policy": memory_accounting,
        "memory_evidence": "SNAPSHOT_NOT_RESERVATION",
        "topology_evidence": "GUEST_OS_REPORTED_NOT_NCP_PHYSICAL_HARDWARE_CERTIFICATE",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--memory-limit-bytes", type=int)
    parser.add_argument("--memory-accounting", choices=MEMORY_ACCOUNTING_POLICIES, default="raw-headroom")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.memory_limit_bytes is None:
        if args.command:
            parser.error("command requires --memory-limit-bytes")
        print(json.dumps(probe_host(args.memory_accounting), indent=2, sort_keys=True))
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
