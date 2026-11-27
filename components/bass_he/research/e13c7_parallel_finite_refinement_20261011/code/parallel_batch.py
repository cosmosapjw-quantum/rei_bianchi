#!/usr/bin/env python3
"""Identity-bound, single-host Open MPI map for independent E13C7 OFF paths.

The production transport is MPI. ``local`` is an explicitly selected, bounded
protocol/pilot transport, never an MPI fallback. Scientific work and admission
are provided by the separately pinned off_path_worker module. This module does
not import a numerical kernel before resource, scope and identity preflight.
"""

import argparse
from datetime import datetime, timezone
import decimal
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path, PurePosixPath
import platform
import re
import resource
import shutil
import signal
import stat
import subprocess
import sys
import time
import traceback
import uuid


SCHEMA = "bass-he-e13c7-parallel-v1"
THREAD_ENV = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
REQUIRED = {"SOURCE_LOCK.json", "inputs/WORK_PLAN.json", "code/parallel_batch.py",
            "code/off_path_worker.py"}
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
NODE_NAME = re.compile(r"node_([0-9]{6})\Z")
FORBIDDEN = {"automatic_retries": 0, "ODE_solves": 0, "native_runs": 0,
             "gas_advances": 0, "full_first2_reruns": 0, "old_budget_reruns": 0,
             "hidden_transport_fallbacks": 0, "scientific_benchmark_replays": 0}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def utc():
    return datetime.now(timezone.utc).isoformat()


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(part)
    return value.hexdigest()


def no_duplicates(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, "duplicate JSON key: " + key)
        obj[key] = value
    return obj


def read_json(path):
    def reject(value):
        raise ValueError("non-finite JSON literal: " + value)
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream, object_pairs_hook=no_duplicates,
                         parse_constant=reject)


def fsync_dir(directory):
    descriptor = os.open(str(directory), os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def save_bytes_new(path, raw):
    """Atomic create-only installation; no rename-overwrite or silent fallback."""
    path = Path(path)
    temporary = path.parent / (".pending_" + uuid.uuid4().hex)
    try:
        with temporary.open("xb") as stream:
            require(stream.write(raw) == len(raw), "short file write")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
        fsync_dir(path.parent)
    finally:
        if temporary.exists():
            temporary.unlink()
            fsync_dir(path.parent)


def save_new(path, obj):
    save_bytes_new(path, json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                   indent=2, allow_nan=False).encode("utf-8") + b"\n")


def safe_file(root, name):
    require(isinstance(name, str) and name and "\\" not in name,
            "invalid pinned path")
    relative = PurePosixPath(name)
    require(not relative.is_absolute() and
            all(part not in ("", ".", "..") for part in name.split("/")),
            "noncanonical or escaping pinned path: " + name)
    path = root
    for part in relative.parts:
        path /= part
        require(not path.is_symlink(), "symlink in pinned path: " + name)
    require(path.is_file() and stat.S_ISREG(path.stat().st_mode),
            "missing or nonregular pinned file: " + name)
    return path


def verify_inventory(root, records):
    require(isinstance(records, dict) and records, "empty/malformed inventory")
    observed = {}
    for name, pin in sorted(records.items()):
        require(isinstance(pin, dict) and type(pin.get("bytes")) is int and
                pin["bytes"] >= 0 and isinstance(pin.get("sha256"), str) and
                HEX64.fullmatch(pin["sha256"]), "malformed file pin: " + str(name))
        path = safe_file(root, name)
        actual = {"bytes": path.stat().st_size, "sha256": digest(path)}
        require(actual == {"bytes": pin["bytes"], "sha256": pin["sha256"]},
                "pinned file mismatch: " + name)
        observed[name] = actual
    return observed


def verify_closure(package, expected_sha):
    require(isinstance(expected_sha, str) and HEX64.fullmatch(expected_sha),
            "external execution-lock SHA must contain 64 lowercase hex digits")
    path = safe_file(package, "EXECUTION_LOCK.json")
    require(digest(path) == expected_sha, "EXECUTION_LOCK SHA mismatch")
    lock = read_json(path)
    require(lock.get("schema") == "bass-he-e13c7-execution-lock-v1",
            "unsupported execution-lock schema")
    files = lock.get("files")
    require(isinstance(files, dict) and REQUIRED <= set(files),
            "execution lock omits a required runtime/plan file")
    runtime = {p.relative_to(package).as_posix()
               for p in (package / "code").rglob("*.py")}
    require(runtime <= set(files), "execution lock omits runtime Python files")
    observed = verify_inventory(package, files)
    source = read_json(package / "SOURCE_LOCK.json")
    require(source.get("schema") == "bass-he-e13c7-source-lock-v1",
            "unsupported source-lock schema")
    source_actual = verify_inventory(package, source.get("files"))
    require(set(source_actual) <= set(observed) and
            all(observed[name] == pin for name, pin in source_actual.items()),
            "execution lock fails to close the scientific source inventory")
    return {"execution_lock_sha256": expected_sha,
            "source_lock_sha256": observed["SOURCE_LOCK.json"]["sha256"],
            "files": observed}


def unique_nodes(values, label):
    require(isinstance(values, list) and
            all(type(node) is int and 0 <= node < 1000000 for node in values),
            "invalid node list: " + label)
    require(len(set(values)) == len(values), "duplicate nodes: " + label)
    return sorted(values)


def positive_int(value, label):
    require(type(value) is int and value > 0, "invalid positive integer: " + label)
    return value


def plan_limits(plan):
    supplied = plan.get("limits", {})
    require(isinstance(supplied, dict), "malformed plan limits")
    require(supplied.get("automatic_retries", 0) == 0, "automatic retries forbidden")
    memory = supplied.get("memory_bytes_per_process",
                          supplied.get("per_rank_address_space_bytes", 1024 ** 3))
    local = supplied.get("max_local_workers", supplied.get("local_max_ranks", 4))
    maximum = supplied.get("max_ncp_ranks", supplied.get("max_ranks", 64))
    seconds = supplied.get("seconds_per_path", supplied.get("per_path_wall_seconds", 180))
    reserve = Fraction(str(supplied.get("memory_reserve_fraction", "0.2")))
    require(Fraction(1, 5) <= reserve < 1, "memory reserve must be at least 20%")
    return {"max_local_workers": positive_int(local, "max_local_workers"),
            "max_ncp_ranks": positive_int(maximum, "max_ncp_ranks"),
            "memory_bytes_per_process": positive_int(memory, "memory_bytes_per_process"),
            "controller_memory_bytes": positive_int(
                supplied.get("launcher_memory_reserve_bytes", 512 * 1024 ** 2),
                "launcher_memory_reserve_bytes"),
            "memory_reserve_fraction": str(reserve),
            "seconds_per_path": positive_int(seconds, "seconds_per_path"),
            "batch_wall_seconds": positive_int(supplied.get("batch_wall_seconds", 7200),
                                               "batch_wall_seconds"),
            "automatic_retries": 0}


def select_work(plan, scope, requested_nodes, subdivisions=None, precision_override=None):
    require(plan.get("mode") == "OFF", "this runner supports only the frozen OFF plan")
    n = positive_int(plan.get("primary_N"), "primary_N")
    precision = positive_int(plan.get("precision"), "precision")
    if subdivisions is not None:
        positive_int(subdivisions, "requested subdivisions")
        require(scope == "local" or subdivisions == n,
                "NCP subdivisions must equal the sealed primary_N")
        n = subdivisions
    if precision_override is not None:
        positive_int(precision_override, "requested precision")
        require(scope == "local" or precision_override == precision,
                "NCP precision must equal the sealed plan precision")
        precision = precision_override
    ncp = unique_nodes(plan.get("ncp_nodes"), "ncp_nodes")
    local = unique_nodes(plan.get("local_primary_nodes"), "local_primary_nodes")
    prior = unique_nodes(plan.get("prior_admitted_nodes"), "prior_admitted_nodes")
    zero = unique_nodes(plan.get("zero_nodes"), "zero_nodes")
    groups = [set(ncp), set(local), set(prior), set(zero)]
    require(all(not (a & b) for i, a in enumerate(groups) for b in groups[i + 1:]),
            "NCP/local/prior/zero partitions overlap")
    require(scope in ("ncp", "local"), "unsupported work scope")
    nodes = ncp if scope == "ncp" else local
    if requested_nodes is not None:
        selected = unique_nodes(requested_nodes, "requested nodes")
        require(scope == "local" and set(selected) <= set(local),
                "node subsets are allowed only for the local pilot set")
        nodes = selected
    require(nodes, "empty selected work")
    return {"mode": "OFF", "N": n, "precision": precision,
            "scope": scope, "nodes": nodes}


def scheduling_cost(plan, node):
    records = plan.get("input_records", {})
    require(isinstance(records, dict), "input_records must map node IDs to records")
    record = records.get(str(node), {})
    require(isinstance(record, dict), "malformed node input record")
    for key in ("estimated_cost_seconds", "estimated_seconds", "scheduling_weight"):
        if key in record:
            value = Fraction(str(record[key]))
            require(value > 0, "nonpositive scheduling cost")
            return value, key
    active = record.get("active_species_count", record.get("active_species"))
    if isinstance(active, (list, tuple, dict)):
        active = len(active)
    if active is None and isinstance(record.get("mask"), dict):
        active = sum(bool(value) for value in record["mask"].values())
    if active is None:
        active = 1
    value = Fraction(str(active))
    require(value > 0, "nonpositive active-species scheduling heuristic")
    return value, "active_species_heuristic_unmeasured"


def lpt_shards(plan, nodes, ranks):
    require(ranks > 0 and ranks <= len(nodes), "invalid shard count")
    weights = {node: scheduling_cost(plan, node) for node in nodes}
    shards = [[] for _ in range(ranks)]
    loads = [Fraction(0) for _ in range(ranks)]
    for node in sorted(nodes, key=lambda item: (-weights[item][0], item)):
        rank = min(range(ranks), key=lambda item: (loads[item], item))
        shards[rank].append(node)
        loads[rank] += weights[node][0]
    return {"shards": shards, "predicted_rank_costs": [str(value) for value in loads],
            "node_costs": {str(node): {"value": str(weights[node][0]),
                                        "source": weights[node][1]}
                           for node in sorted(nodes)},
            "method": "deterministic LPT, descending cost then node; min load then rank"}


def read_text_optional(path):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return None


def mount_unescape(value):
    return re.sub(r"\\([0-7]{3})", lambda match: chr(int(match.group(1), 8)), value)


def cgroup_observation():
    """Observe visible v1/v2 limits; absent root files never mean unlimited."""
    membership_text = read_text_optional("/proc/self/cgroup")
    mount_text = read_text_optional("/proc/self/mountinfo")
    memberships, mounts = [], []
    for line in (membership_text or "").splitlines():
        parts = line.split(":", 2)
        require(len(parts) == 3, "malformed /proc/self/cgroup row")
        memberships.append({"controllers": set(filter(None, parts[1].split(","))),
                            "path": parts[2], "version": 2 if parts[0] == "0" and not parts[1] else 1})
    for line in (mount_text or "").splitlines():
        before, separator, after = line.partition(" - ")
        if not separator:
            continue
        right, left = after.split(), before.split()
        if len(right) >= 3 and len(left) >= 5 and right[0] in ("cgroup", "cgroup2"):
            mounts.append({"version": 2 if right[0] == "cgroup2" else 1,
                           "root": mount_unescape(left[3]), "mountpoint": mount_unescape(left[4]),
                           "controllers": set(right[2].split(","))})
    levels, resolved = [], []
    for member in memberships:
        for mounted in mounts:
            common = member["controllers"] & mounted["controllers"]
            if member["version"] != mounted["version"] or (member["version"] == 1 and
                    not common.intersection({"cpu", "cpuacct", "memory", "cpuset"})):
                continue
            mount = Path(mounted["mountpoint"])
            if not mount.is_dir():
                continue
            member_path, mount_root = PurePosixPath(member["path"]), PurePosixPath(mounted["root"])
            relative = None
            if ".." not in member_path.parts and member_path.is_relative_to(mount_root):
                relative = member_path.relative_to(mount_root)
            candidate = mount.joinpath(*relative.parts) if relative is not None else mount
            # Container cgroup namespaces can expose the current group as their
            # mount root even when /proc records a host-relative membership.
            leaf = candidate if candidate.is_dir() else mount
            require(leaf.is_relative_to(mount), "cgroup path escaped its observed mount")
            mapping = {"version": member["version"], "membership_path": member["path"],
                       "mount_root": mounted["root"], "mountpoint": str(mount),
                       "observed_leaf": str(leaf), "controllers": sorted(common),
                       "mapping": "membership_relative_to_mount" if leaf == candidate and relative is not None
                       else "visible_namespace_mount_root_only"}
            resolved.append(mapping)
            path = leaf
            while True:
                values = {name: None for name in ("cpu.max", "cpuset.cpus.effective", "memory.max",
                                                  "memory.current", "memory.high", "memory.events")}
                raw = {}
                if member["version"] == 2:
                    raw = {name: read_text_optional(path / name) for name in values}
                    values.update(raw)
                else:
                    if "cpu" in common or "cpuacct" in common:
                        for name in ("cpu.cfs_quota_us", "cpu.cfs_period_us"):
                            raw[name] = read_text_optional(path / name)
                        quota, period = raw["cpu.cfs_quota_us"], raw["cpu.cfs_period_us"]
                        if quota is not None and period is not None:
                            require(int(quota) == -1 or int(quota) > 0, "invalid v1 CPU quota")
                            values["cpu.max"] = ("max" if int(quota) == -1 else quota) + " " + period
                    if "memory" in common:
                        for old_name, normalized in (("memory.limit_in_bytes", "memory.max"),
                                ("memory.usage_in_bytes", "memory.current"),
                                ("memory.soft_limit_in_bytes", "memory.high")):
                            raw[old_name] = read_text_optional(path / old_name)
                            values[normalized] = raw[old_name]
                    if "cpuset" in common:
                        raw["cpuset.cpus"] = read_text_optional(path / "cpuset.cpus")
                        values["cpuset.cpus.effective"] = raw["cpuset.cpus"]
                levels.append({"directory": str(path), "version": member["version"],
                               "controllers": sorted(common), "values": values, "raw_files": raw})
                if path == mount:
                    break
                path = path.parent
    cpu_visible = any(row["values"]["cpu.max"] is not None for row in levels)
    memory_visible = any(row["values"]["memory.max"] is not None for row in levels)
    return {"status": "VISIBLE_HIERARCHIES_OBSERVED" if resolved else "HIERARCHY_UNOBSERVED",
            "proc_membership": membership_text, "mount_resolution": resolved, "levels": levels,
            "cpu_quota_file_observation": "OBSERVED" if cpu_visible else "UNOBSERVED",
            "memory_limit_file_observation": "OBSERVED" if memory_visible else "UNOBSERVED",
            "missing_limit_file_semantics": "UNOBSERVED, never assumed unlimited; use affinity and host "
                "memory bounds with the pinned rank/memory caps. Hidden ancestor limits are not attested."}


def cpu_topology(affinity):
    rows = []
    for cpu in affinity:
        root = Path("/sys/devices/system/cpu") / ("cpu" + str(cpu)) / "topology"
        socket = read_text_optional(root / "physical_package_id")
        core = read_text_optional(root / "core_id")
        rows.append({"cpu": cpu, "physical_package_id": socket, "core_id": core,
                     "thread_siblings_list": read_text_optional(root / "thread_siblings_list")})
    first, siblings, seen = [], [], set()
    for row in rows:
        key = (row["physical_package_id"], row["core_id"])
        if None in key:
            first.append(row["cpu"])
        elif key not in seen:
            first.append(row["cpu"])
            seen.add(key)
        else:
            siblings.append(row["cpu"])
    complete = all(row["core_id"] is not None and
                   row["physical_package_id"] is not None for row in rows)
    return {"logical_cpus": len(rows), "physical_core_count": len(seen) if complete else None,
            "topology_complete": complete, "rows": rows,
            "cpu_selection_order": first + siblings}


def root_launch_choice(requested, transport, effective_uid):
    require(not requested or transport == "mpi", "Open MPI root option is invalid for local transport")
    require(not requested or effective_uid == 0, "Open MPI root option requires an observed effective uid of 0")
    return {"effective_uid": effective_uid, "allow_openmpi_root_explicitly_requested": bool(requested),
            "mechanism": "mpiexec --allow-run-as-root" if requested else "no root override added",
            "authorization_boundary": "operator explicitly selects this option for the authorized compute host"}


def mpi_command(executable, hostfile, ranks, base, allow_root):
    return [executable] + (["--allow-run-as-root"] if allow_root else []) + [
        "--hostfile", str(hostfile), "--nooversubscribe", "--bind-to", "none",
        "--map-by", "slot", "-n", str(ranks)] + base


def host_preflight(limits, scope, requested_ranks, pending_count, transport,
                   provider_evidence=None):
    require(platform.system() == "Linux" and platform.python_implementation() == "CPython" and
            sys.version_info[:2] == (3, 12), "runtime requires Linux CPython 3.12.x")
    require(not os.environ.get("OMPI_COMM_WORLD_RANK"),
            "nested MPI launch is outside this single-host protocol")
    affinity = sorted(os.sched_getaffinity(0))
    require(affinity, "empty CPU affinity")
    cgroup = cgroup_observation()
    cpu_quotas, memory_limits, available_limits = [], [], []
    for level in cgroup["levels"]:
        values = level["values"]
        if values["cpu.max"]:
            quota, period = values["cpu.max"].split()
            if quota != "max":
                require(int(quota) > 0 and int(period) > 0, "invalid CPU cgroup quota")
                cpu_quotas.append(Fraction(int(quota), int(period)))
        raw_limit, raw_current = values["memory.max"], values["memory.current"]
        if raw_limit and raw_limit != "max":
            limit = int(raw_limit)
            require(limit > 0, "invalid memory cgroup limit")
            memory_limits.append(limit)
            if raw_current is not None:
                current = int(raw_current)
                require(current >= 0, "invalid memory cgroup current usage")
                available_limits.append(max(0, limit - current))
    memory_info = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, value = line.split(":", 1)
        if key in ("MemTotal", "MemAvailable"):
            memory_info[key] = int(value.strip().split()[0]) * 1024
    require(set(memory_info) == {"MemTotal", "MemAvailable"}, "host memory availability unobserved")
    effective_total = min([memory_info["MemTotal"]] + memory_limits)
    effective_available = min([memory_info["MemAvailable"]] + available_limits)
    reserve = Fraction(limits["memory_reserve_fraction"])
    reserved_bytes = math.ceil(effective_total * reserve)
    usable_bytes = max(0, min(effective_total - reserved_bytes,
                            effective_available - reserved_bytes))
    memory_rank_cap = max(0, (usable_bytes - limits["controller_memory_bytes"]) //
                          limits["memory_bytes_per_process"])
    effective_cpu = min([Fraction(len(affinity))] + cpu_quotas)
    cpu_cap = effective_cpu.numerator // effective_cpu.denominator
    scope_cap = limits["max_ncp_ranks"] if scope == "ncp" else limits["max_local_workers"]
    cap = min(cpu_cap, memory_rank_cap, scope_cap, pending_count)
    if pending_count == 0:
        ranks = 0
    elif requested_ranks == "auto":
        require(cap >= 1, "insufficient CPU/memory budget for one rank")
        ranks = cap
    else:
        ranks = int(requested_ranks)
        require(0 < ranks <= cap,
                "requested ranks exceed effective CPU/memory/task/plan capacity: " + str(cap))
    address_limit = resource.getrlimit(resource.RLIMIT_AS)
    require(address_limit[1] == resource.RLIM_INFINITY or
            address_limit[1] >= limits["memory_bytes_per_process"],
            "inherited address-space hard limit prevents the per-rank cap")
    topology = cpu_topology(affinity)
    provider = {"status": "NOT_ASSERTED", "reason": "hostname is not provider attestation"}
    if provider_evidence:
        path = Path(provider_evidence)
        require(path.is_file() and not path.is_symlink(), "provider evidence is not a regular file")
        provider = {"status": "SUPPLIED_EVIDENCE_RECORDED_NOT_INDEPENDENTLY_VERIFIED",
                    "filename": path.name, "bytes": path.stat().st_size, "sha256": digest(path)}
    mpi = {"status": "NOT_RUN_LOCAL_TRANSPORT"}
    if transport == "mpi" and ranks:
        executable = shutil.which("mpiexec")
        require(executable is not None, "Open MPI mpiexec is unavailable; no fallback")
        executable = str(Path(executable).resolve(strict=True))
        version = subprocess.run([executable, "--version"], text=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 timeout=10, check=False)
        combined = version.stdout + "\n" + version.stderr
        require(version.returncode == 0 and
                re.search(r"Open\s*(MPI|RTE)|OpenRTE", combined, re.IGNORECASE),
                "mpiexec is not a verified Open MPI executable")
        mpi = {"status": "VERSION_PREFLIGHT_ONLY", "executable": executable,
               "sha256": digest(executable), "version_exit_code": version.returncode,
               "version_stdout": version.stdout, "version_stderr": version.stderr}
    return {"hostname": platform.node(), "platform": platform.platform(),
            "python": sys.version, "decimal_libmpdec_version": decimal.__libmpdec_version__,
            "cpu_affinity": affinity, "effective_cpu_quota": str(min(cpu_quotas)) if cpu_quotas else None,
            "visible_cpu_or_affinity_rank_bound": str(effective_cpu),
            "cpu_quota_observation": "FINITE_VISIBLE_LIMIT" if cpu_quotas else
                ("VISIBLE_FILES_NO_FINITE_LIMIT" if cgroup["cpu_quota_file_observation"] == "OBSERVED"
                 else "UNOBSERVED"),
            "cpu_allocation_attestation": "NOT_ASSERTED",
            "cpu_quota_rank_cap": cpu_cap, "topology": topology,
            "selected_ranks": ranks, "rank_cpu_ids": topology["cpu_selection_order"][:ranks],
            "cgroup": cgroup, "host_memory_bytes": memory_info,
            "effective_memory_total_bytes": effective_total,
            "effective_memory_available_bytes": effective_available,
            "reserved_memory_bytes": reserved_bytes, "usable_worker_and_controller_bytes": usable_bytes,
            "memory_rank_cap": memory_rank_cap, "inherited_RLIMIT_AS": list(address_limit),
            "limits": limits, "open_mpi": mpi, "provider_attestation": provider}


def load_worker(package):
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(package / "code"))
    spec = importlib.util.spec_from_file_location("off_path_worker", package / "code/off_path_worker.py")
    require(spec is not None and spec.loader is not None, "cannot load pinned worker module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    require(callable(getattr(module, "validate_completed", None)) and
            callable(getattr(module, "Context", None)), "pinned worker lacks required API")
    return module, module.Context(package)


def path_directory(output, node):
    return output / "paths" / ("node_%06d" % node)


def validated_summary(module, ctx, work, node, path):
    summary = module.validate_completed(ctx, node, work["N"], work["precision"], path)
    require(isinstance(summary, dict) and summary.get("node") == node and
            summary.get("N") == work["N"] and summary.get("precision") == work["precision"],
            "worker validator returned a different path work identity")
    require(isinstance(summary.get("semantic_sha256"), str) and
            HEX64.fullmatch(summary["semantic_sha256"]), "invalid path semantic digest")
    require(type(summary.get("new_coefficient_evaluations")) is int and
            summary["new_coefficient_evaluations"] >= 0, "invalid coefficient counter")
    for field in ("elapsed_seconds", "peak_RSS_KiB"):
        require(isinstance(summary.get(field), (int, float)) and
                not isinstance(summary[field], bool) and math.isfinite(summary[field]) and
                summary[field] >= 0, "invalid worker resource summary: " + field)
    return summary


def copy_complete_tree(source, destination):
    """Copy evidence into this attempt; completion marker is installed last."""
    require(source.is_dir() and not source.is_symlink(), "unsafe resume path")
    destination.mkdir()
    files = []
    for path in sorted(source.rglob("*")):
        require(not path.is_symlink(), "symlink in resume evidence")
        relative = path.relative_to(source)
        if path.is_dir():
            (destination / relative).mkdir()
        else:
            require(path.is_file() and stat.S_ISREG(path.stat().st_mode),
                    "nonregular resume evidence")
            files.append((relative.as_posix(), path))
    for name, path in sorted(files, key=lambda pair: (pair[0] == "COMPLETE.json", pair[0])):
        save_bytes_new(destination / name, path.read_bytes())
    fsync_dir(destination)


def prepare_resume(package, output, prior, work, work_id, execution_sha, retry_nodes):
    if prior is None:
        require(not retry_nodes, "retry list requires explicit --resume-from")
        return {"source": None, "reused_nodes": [], "explicitly_restarted_nodes": []}
    prior = Path(prior).resolve(strict=True)
    require(prior != output and prior.is_dir(), "invalid prior attempt directory")
    manifest_path = safe_file(prior, "EXECUTION_MANIFEST.json")
    old = read_json(manifest_path)
    require(old.get("schema") == SCHEMA and old.get("work_id") == work_id and
            old.get("execution_lock_sha256") == execution_sha and old.get("work") == work,
            "resume identity differs from the pinned work/code/input/N/P")
    expected = set(work["nodes"])
    existing = set()
    root = prior / "paths"
    require(root.is_dir() and not root.is_symlink(), "prior path store is missing or unsafe")
    for path in root.iterdir():
        match = NODE_NAME.fullmatch(path.name)
        require(match is not None and path.is_dir() and not path.is_symlink(),
                "unexpected item in prior path store")
        existing.add(int(match.group(1)))
    require(existing <= expected, "prior store contains unplanned nodes")
    attempted = set()
    for path in (prior / "ranks").glob("rank_*/PATH_*_RESERVED.json"):
        record = read_json(path)
        require(record.get("work_id") == work_id and record.get("node") in expected,
                "prior reservation identity mismatch")
        attempted.add(record["node"])
    module, ctx = load_worker(package)
    complete, incomplete = {}, []
    for node in sorted(existing):
        source = path_directory(prior, node)
        if (source / "COMPLETE.json").exists():
            complete[node] = validated_summary(module, ctx, work, node, source)
        else:
            incomplete.append(node)
    incomplete = sorted(set(incomplete) | (attempted - set(complete)))
    require(set(retry_nodes) == set(incomplete),
            "incomplete/attempted paths require their exact explicit --retry-incomplete-nodes list: " +
            ",".join(map(str, incomplete)))
    for node in sorted(complete):
        copy_complete_tree(path_directory(prior, node), path_directory(output, node))
        require(validated_summary(module, ctx, work, node, path_directory(output, node)) == complete[node],
                "copied resume evidence differs from validated source")
    return {"source": str(prior), "source_manifest_sha256": digest(manifest_path),
            "reused_nodes": sorted(complete), "explicitly_restarted_nodes": incomplete,
            "source_outcome_sha256": digest(prior / "EXECUTION_RECEIPT.json")
            if (prior / "EXECUTION_RECEIPT.json").is_file() else None}


def verify_manifest(output, expected_sha):
    path = safe_file(output, "EXECUTION_MANIFEST.json")
    require(digest(path) == expected_sha, "execution manifest SHA mismatch")
    manifest = read_json(path)
    require(manifest.get("schema") == SCHEMA, "unsupported parallel manifest")
    work = manifest["work"]
    nodes = unique_nodes(work["nodes"], "manifest work")
    pending = unique_nodes(manifest["pending_nodes"], "manifest pending")
    reused = unique_nodes(manifest["resume"]["reused_nodes"], "manifest reused")
    require(not (set(pending) & set(reused)) and sorted(pending + reused) == nodes,
            "manifest pending/reused partition mismatch")
    shards = manifest["schedule"]["shards"]
    require(len(shards) == manifest["ranks"] and
            sorted(node for shard in shards for node in shard) == pending,
            "manifest shard coverage/uniqueness mismatch")
    cpus = manifest["rank_cpu_ids"]
    require(len(cpus) == manifest["ranks"] and len(set(cpus)) == len(cpus),
            "manifest rank CPU allocation overlaps")
    return manifest


def alarm_expired(signum, frame):
    raise TimeoutError("pinned per-path wall timeout expired")


def termination_requested(signum, frame):
    raise InterruptedError("termination signal received: " + str(signum))


def rank_main(args):
    output = Path(args.output_dir).resolve(strict=True)
    manifest = verify_manifest(output, args.manifest_sha256)
    package = Path(manifest["package"]).resolve(strict=True)
    if manifest["transport"] == "mpi":
        require(args.rank is None, "MPI rank is supplied only by the Open MPI environment")
        rank = int(os.environ["OMPI_COMM_WORLD_RANK"])
        require(int(os.environ["OMPI_COMM_WORLD_SIZE"]) == manifest["ranks"] and
                int(os.environ["OMPI_COMM_WORLD_LOCAL_SIZE"]) == manifest["ranks"],
                "Open MPI world/local size differs from the single-host manifest")
        require(platform.node() == manifest["hostname"], "MPI rank ran on a different host")
    else:
        require(args.rank is not None and "OMPI_COMM_WORLD_RANK" not in os.environ,
                "local rank requires an explicit rank and no MPI rank environment")
        rank = args.rank
    require(0 <= rank < manifest["ranks"], "rank outside manifest range")
    rank_dir = output / "ranks" / ("rank_%04d" % rank)
    rank_dir.mkdir()
    fsync_dir(rank_dir.parent)
    start = time.perf_counter()
    completed, reserved, failure = [], [], None
    exit_code = 0
    signal.signal(signal.SIGTERM, termination_requested)
    try:
        cpu = manifest["rank_cpu_ids"][rank]
        require(cpu in os.sched_getaffinity(0), "assigned CPU is outside rank's inherited affinity")
        os.sched_setaffinity(0, {cpu})
        require(all(os.environ.get(name) == "1" for name in THREAD_ENV),
                "single-thread environment is not fixed")
        require(len(list(Path("/proc/self/task").iterdir())) == 1, "rank already has multiple threads")
        limit = manifest["limits"]["memory_bytes_per_process"]
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
        lock_path = safe_file(package, "EXECUTION_LOCK.json")
        require(digest(lock_path) == manifest["execution_lock_sha256"], "rank execution lock changed")
        locked = read_json(lock_path)["files"]
        runtime = {name: pin for name, pin in locked.items()
                   if name.startswith("code/") and name.endswith(".py")}
        verify_inventory(package, runtime)
        save_new(rank_dir / "START.json", {"schema": SCHEMA, "utc": utc(), "rank": rank,
                 "pid": os.getpid(), "hostname": platform.node(), "transport": manifest["transport"],
                 "work_id": manifest["work_id"], "cpu_affinity": sorted(os.sched_getaffinity(0)),
                 "thread_count": 1, "address_space_bytes": limit,
                 "assigned_nodes": manifest["schedule"]["shards"][rank]})
        module, ctx = load_worker(package)
        signal.signal(signal.SIGALRM, alarm_expired)
        for position, node in enumerate(manifest["schedule"]["shards"][rank]):
            destination = path_directory(output, node)
            require(not destination.exists(), "path destination collision; no implicit skip")
            record = {"schema": SCHEMA, "utc": utc(), "work_id": manifest["work_id"],
                      "rank": rank, "node": node, "N": manifest["work"]["N"],
                      "precision": manifest["work"]["precision"], "automatic_retry": False}
            save_new(rank_dir / ("PATH_%06d_RESERVED.json" % node), record)
            reserved.append(node)
            signal.setitimer(signal.ITIMER_REAL, manifest["limits"]["seconds_per_path"])
            try:
                module_result = ctx.run(node, manifest["work"]["N"], manifest["work"]["precision"],
                                        destination, manifest["work"]["scope"])
                summary = validated_summary(module, ctx, manifest["work"], node, destination)
                require(isinstance(module_result, dict) and
                        module_result.get("semantic_sha256") == summary["semantic_sha256"],
                        "worker return disagrees with validated completed output")
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
            require(sorted(os.sched_getaffinity(0)) == [cpu] and
                    len(list(Path("/proc/self/task").iterdir())) == 1,
                    "rank CPU/thread invariant changed")
            completed.append(summary)
            save_new(rank_dir / ("PROGRESS_%06d.json" % (position + 1)),
                     {"schema": SCHEMA, "utc": utc(), "rank": rank, "node": node,
                      "work_id": manifest["work_id"], "completed_in_rank": len(completed),
                      "summary": summary})
    except BaseException as exc:
        exit_code = 1
        failure = {"type": type(exc).__name__, "message": str(exc),
                   "traceback": traceback.format_exc(), "failure_layer": "RUNTIME_OR_WORKER_VALIDATION"}
        save_new(rank_dir / "FAILURE.json", failure)
        print("rank %d failed: %s" % (rank, str(exc)), file=sys.stderr, flush=True)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        receipt = {"schema": SCHEMA, "utc": utc(), "rank": rank,
                   "work_id": manifest["work_id"], "exit_code": exit_code,
                   "status": "COMPLETE_SCOPED" if exit_code == 0 else "FAILED_PRESERVED",
                   "reserved_nodes": reserved, "completed_nodes": [row["node"] for row in completed],
                   "validated_completed_path_calls": len(completed),
                   "reserved_path_calls": len(reserved),
                   "unresolved_reserved_nodes": sorted(set(reserved) - {row["node"] for row in completed}),
                   "new_coefficient_evaluations_from_validated_outputs":
                       sum(row["new_coefficient_evaluations"] for row in completed),
                   "elapsed_seconds": time.perf_counter() - start,
                   "peak_RSS_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   "forbidden_invocations": FORBIDDEN, "failure": failure}
        save_new(rank_dir / "RECEIPT.json", receipt)
    return exit_code


def stop_processes(processes):
    for process in processes:
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
    deadline = time.monotonic() + 5
    while any(process.poll() is None for process in processes) and time.monotonic() < deadline:
        time.sleep(0.1)
    for process in processes:
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    for process in processes:
        process.wait(timeout=5)


def execute_ranks(package, output, manifest, manifest_sha, host):
    ranks = manifest["ranks"]
    if not ranks:
        return {"launcher_processes_started": 0, "transport": manifest["transport"],
                "exit_codes": [], "elapsed_seconds": 0, "rank_count": 0}
    environment = os.environ.copy()
    environment.update({name: "1" for name in THREAD_ENV})
    environment.update({"OMP_DYNAMIC": "FALSE", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"})
    base = [sys.executable, str(package / "code/parallel_batch.py"), "rank-worker",
            "--output-dir", str(output), "--manifest-sha256", manifest_sha]
    if manifest["transport"] == "mpi":
        hostfile = output / "MPI_HOSTFILE"
        save_bytes_new(hostfile, ("localhost slots=%d max_slots=%d\n" % (ranks, ranks)).encode("ascii"))
        commands = [mpi_command(host["open_mpi"]["executable"], hostfile, ranks, base,
                                manifest["root_launch_choice"]["allow_openmpi_root_explicitly_requested"])]
    else:
        commands = [base + ["--rank", str(rank)] for rank in range(ranks)]
    processes, streams = [], []
    start = time.perf_counter()
    try:
        for index, command in enumerate(commands):
            save_new(output / ("LAUNCH_%04d_RESERVED.json" % index),
                     {"utc": utc(), "argv": command, "transport": manifest["transport"],
                      "automatic_retry": False, "manifest_sha256": manifest_sha})
            stdout = (output / ("LAUNCH_%04d.stdout.log" % index)).open("xb")
            stderr = (output / ("LAUNCH_%04d.stderr.log" % index)).open("xb")
            streams.extend([stdout, stderr])
            process = subprocess.Popen(command, stdout=stdout, stderr=stderr,
                                       cwd=str(package), env=environment, start_new_session=True)
            processes.append(process)
            save_new(output / ("LAUNCH_%04d_STARTED.json" % index),
                     {"utc": utc(), "pid": process.pid, "argv": command})
        deadline = time.monotonic() + manifest["limits"]["batch_wall_seconds"]
        next_progress = time.monotonic() + 10
        while any(process.poll() is None for process in processes):
            require(not any(process.poll() not in (None, 0) for process in processes),
                    "a rank/launcher failed; remaining processes are stopped without retry")
            require(not any((output / "ranks").glob("rank_*/FAILURE.json")),
                    "a rank recorded a failure; remaining processes are stopped without retry")
            if time.monotonic() >= deadline:
                raise TimeoutError("pinned batch wall timeout expired")
            if time.monotonic() >= next_progress:
                count = sum(1 for _ in (output / "paths").glob("node_*/COMPLETE.json"))
                print(json.dumps({"event": "batch_progress", "elapsed_seconds": time.perf_counter() - start,
                                  "completion_markers_observed_not_yet_admitted": count,
                                  "expected_paths": len(manifest["work"]["nodes"])}), flush=True)
                next_progress = time.monotonic() + 10
            time.sleep(0.2)
        codes = [process.wait() for process in processes]
        require(all(code == 0 for code in codes), "rank/launcher exit is not zero")
        receipt = {"transport": manifest["transport"], "rank_count": ranks,
                   "launcher_processes_started": len(processes), "exit_codes": codes,
                   "elapsed_seconds": time.perf_counter() - start,
                   "MPI_execution_status": "EXECUTED" if manifest["transport"] == "mpi" else "NOT_RUN"}
        save_new(output / "LAUNCH_PROCESS_RECEIPT.json", receipt)
        return receipt
    except BaseException:
        stop_processes(processes)
        save_new(output / "LAUNCH_PROCESS_RECEIPT.json",
                 {"transport": manifest["transport"], "rank_count": ranks,
                  "launcher_processes_started": len(processes),
                  "exit_codes": [process.poll() for process in processes],
                  "elapsed_seconds": time.perf_counter() - start, "status": "FAILED_PRESERVED"})
        raise
    finally:
        for stream in streams:
            stream.flush()
            os.fsync(stream.fileno())
            stream.close()


def collect_completed(package, output, manifest):
    expected = set(manifest["work"]["nodes"])
    entries = list((output / "paths").iterdir())
    require(all(NODE_NAME.fullmatch(path.name) and path.is_dir() and not path.is_symlink()
                for path in entries), "unexpected item in completed path store")
    actual = {int(NODE_NAME.fullmatch(path.name).group(1)) for path in entries}
    require(actual == expected, "completed path coverage differs from expected nodes")
    rank_receipts = []
    for rank in range(manifest["ranks"]):
        row = read_json(output / "ranks" / ("rank_%04d" % rank) / "RECEIPT.json")
        assigned = manifest["schedule"]["shards"][rank]
        require(row["rank"] == rank and row["work_id"] == manifest["work_id"] and
                row["exit_code"] == 0 and row["completed_nodes"] == assigned and
                row["reserved_nodes"] == assigned and not row["unresolved_reserved_nodes"],
                "rank completion receipt disagrees with its exact shard")
        require(row["forbidden_invocations"] == FORBIDDEN, "rank forbidden invocation mismatch")
        rank_receipts.append(row)
    module, ctx = load_worker(package)
    paths = []
    reused = set(manifest["resume"]["reused_nodes"])
    for node in sorted(expected):
        directory = path_directory(output, node)
        summary = validated_summary(module, ctx, manifest["work"], node, directory)
        paths.append({"node": node, "relative_directory": directory.relative_to(output).as_posix(),
                      "reused": node in reused, "summary": summary,
                      "files": {name: {"bytes": (directory / name).stat().st_size,
                                        "sha256": digest(directory / name)}
                                for name in ("RESULT.json", "ADMISSION.json", "COMPLETE.json")}})
    semantic = {"work": manifest["work"], "execution_lock_sha256": manifest["execution_lock_sha256"],
                "paths": [{"node": row["node"], "semantic_sha256": row["summary"]["semantic_sha256"]}
                          for row in paths]}
    return {"schema": SCHEMA, "work_id": manifest["work_id"], "work": manifest["work"],
            "execution_lock_sha256": manifest["execution_lock_sha256"],
            "status": "COMPLETE_PATHS_AWAIT_EXACT_REDUCTION_AND_INDEPENDENT_REVIEW",
            "collection_semantic_sha256": hashlib.sha256(
                b"bass-he-e13c7-ordered-path-collection-v1\n" + canonical(semantic)).hexdigest(),
            "ordered_paths": paths, "rank_receipts": rank_receipts,
            "new_validated_path_calls": len(paths) - len(reused), "reused_completed_paths": len(reused),
            "new_coefficient_evaluations": sum(row["summary"]["new_coefficient_evaluations"]
                                                for row in paths if not row["reused"]),
            "forbidden_invocations": FORBIDDEN,
            "physical": "HOLD", "continuum": "HOLD", "production": "HOLD", "receiver": "HOLD"}


def parse_node_argument(value):
    require(bool(value), "empty node argument")
    return unique_nodes([int(item) for item in value.split(",")], "node argument")


def launch_main(args):
    package = Path(args.package).resolve(strict=True)
    output = Path(args.output_dir).resolve()
    require(not output.exists(), "output directory already exists; no implicit resume or overwrite")
    require(output != package and not package.is_relative_to(output), "output may not contain the package")
    output.mkdir(parents=True)
    (output / "paths").mkdir()
    (output / "ranks").mkdir()
    fsync_dir(output.parent)
    started = time.perf_counter()
    stage, manifest, failure, complete, exit_code = "PREFLIGHT", None, None, None, 0
    signal.signal(signal.SIGTERM, termination_requested)
    save_new(output / "START.json", {"schema": SCHEMA, "utc": utc(), "pid": os.getpid(),
             "argv": sys.argv, "execution_lock_sha256": args.execution_lock_sha256,
             "automatic_retry": False, "provider": "NOT_ASSERTED"})
    try:
        require(args.transport in ("mpi", "local"), "unsupported transport")
        require(args.scope != "ncp" or args.transport == "mpi",
                "NCP primary work requires MPI; local transport is pilot-only")
        root_choice = root_launch_choice(args.allow_openmpi_root, args.transport, os.geteuid())
        before = verify_closure(package, args.execution_lock_sha256)
        save_new(output / "SOURCE_AND_INPUT_BEFORE.json", before)
        plan = read_json(package / "inputs/WORK_PLAN.json")
        nodes = parse_node_argument(args.nodes) if args.nodes is not None else None
        work = select_work(plan, args.scope, nodes, args.subdivisions, args.precision)
        limits = plan_limits(plan)
        work_id = hashlib.sha256(b"bass-he-e13c7-parallel-work-v1\n" + canonical(
            {"work": work, "execution_lock_sha256": args.execution_lock_sha256})).hexdigest()
        retry = parse_node_argument(args.retry_incomplete_nodes) if args.retry_incomplete_nodes else []
        stage = "RESUME_VALIDATION"
        resume = prepare_resume(package, output, args.resume_from, work, work_id,
                                args.execution_lock_sha256, retry)
        pending = sorted(set(work["nodes"]) - set(resume["reused_nodes"]))
        stage = "HOST_PREFLIGHT"
        host = host_preflight(limits, args.scope, args.ranks, len(pending), args.transport,
                              args.provider_evidence)
        save_new(output / "HOST_PREFLIGHT.json", host)
        ranks = host["selected_ranks"]
        schedule = lpt_shards(plan, pending, ranks) if pending else {
            "shards": [], "predicted_rank_costs": [], "node_costs": {}, "method": "no pending work"}
        manifest = {"schema": SCHEMA, "utc": utc(), "package": str(package),
                    "hostname": host["hostname"], "work": work, "work_id": work_id,
                    "execution_lock_sha256": args.execution_lock_sha256,
                    "source_lock_sha256": before["source_lock_sha256"],
                    "transport": args.transport, "ranks": ranks,
                    "rank_cpu_ids": host["rank_cpu_ids"], "schedule": schedule,
                    "pending_nodes": pending, "resume": resume, "limits": limits,
                    "root_launch_choice": root_choice,
                    "forbidden_invocations": FORBIDDEN}
        save_new(output / "EXECUTION_MANIFEST.json", manifest)
        manifest_sha = digest(output / "EXECUTION_MANIFEST.json")
        save_new(output / "MANIFEST_IDENTITY.json", {"sha256": manifest_sha,
                 "bytes": (output / "EXECUTION_MANIFEST.json").stat().st_size})
        stage = "RANK_EXECUTION"
        execute_ranks(package, output, manifest, manifest_sha, host)
        stage = "PATH_COLLECTION"
        complete = collect_completed(package, output, manifest)
        stage = "POST_IDENTITY"
        after = verify_closure(package, args.execution_lock_sha256)
        require(before == after, "source/input closure changed during execution")
        save_new(output / "SOURCE_AND_INPUT_AFTER.json", after)
        save_new(output / "BATCH_COMPLETE.json", complete)
        stage = "COMPLETE"
    except BaseException as exc:
        exit_code = 1
        failure = {"schema": SCHEMA, "utc": utc(), "stage": stage,
                   "type": type(exc).__name__, "message": str(exc),
                   "traceback": traceback.format_exc(), "failure_preserved": True}
        save_new(output / "FAILURE.json", failure)
        print(json.dumps({"status": "FAILED_PRESERVED", "stage": stage,
                          "error": str(exc), "output_directory": str(output)}), file=sys.stderr, flush=True)
        # A failed run still attempts the identity readback, without another kernel call.
        try:
            after = verify_closure(package, args.execution_lock_sha256)
            if not (output / "SOURCE_AND_INPUT_AFTER.json").exists():
                save_new(output / "SOURCE_AND_INPUT_AFTER.json", after)
        except BaseException as post_exc:
            save_new(output / "SOURCE_AND_INPUT_AFTER_FAILURE.json",
                     {"type": type(post_exc).__name__, "message": str(post_exc)})
    finally:
        reservations = sorted(path.name for path in (output / "ranks").glob("rank_*/PATH_*_RESERVED.json"))
        validated_new = complete["new_validated_path_calls"] if complete and exit_code == 0 else None
        receipt = {"schema": SCHEMA, "utc": utc(), "status": "COMPLETE_SCOPED" if exit_code == 0
                   else "FAILED_PRESERVED", "stage": stage, "exit_code": exit_code,
                   "execution_lock_sha256": args.execution_lock_sha256,
                   "work_id": manifest["work_id"] if manifest else None,
                   "transport": args.transport, "MPI_execution_claim":
                       "EXECUTED_SUCCESSFULLY" if exit_code == 0 and manifest and
                       manifest["ranks"] and args.transport == "mpi" else "NOT_ESTABLISHED",
                   "effective_uid": os.geteuid(),
                   "allow_openmpi_root_explicitly_requested": args.allow_openmpi_root,
                   "reserved_new_path_calls": len(reservations),
                   "new_validated_path_calls": validated_new,
                   "new_coefficient_evaluations": complete["new_coefficient_evaluations"]
                       if complete and exit_code == 0 else None,
                   "failed_count_note": "On failure, inspect worker/rank receipts; unresolved reservations "
                       "are not claimed as zero or as complete scientific invocations.",
                   "elapsed_seconds": time.perf_counter() - started,
                   "controller_peak_RSS_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   "forbidden_invocations": FORBIDDEN, "failure": failure,
                   "physical": "HOLD", "continuum": "HOLD", "production": "HOLD", "receiver": "HOLD"}
        save_new(output / "EXECUTION_RECEIPT.json", receipt)
    if exit_code == 0:
        print(json.dumps({"status": receipt["status"], "output_directory": str(output),
                          "new_paths": receipt["new_validated_path_calls"],
                          "reused_paths": complete["reused_completed_paths"],
                          "elapsed_seconds": receipt["elapsed_seconds"]}), flush=True)
    return exit_code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    launch = sub.add_parser("launch")
    launch.add_argument("--package", required=True)
    launch.add_argument("--output-dir", required=True)
    launch.add_argument("--execution-lock-sha256", required=True)
    launch.add_argument("--transport", choices=("mpi", "local"), required=True)
    launch.add_argument("--scope", choices=("ncp", "local"), required=True)
    launch.add_argument("--ranks", default="auto")
    launch.add_argument("--nodes")
    launch.add_argument("--subdivisions", type=int)
    launch.add_argument("--precision", type=int)
    launch.add_argument("--resume-from")
    launch.add_argument("--retry-incomplete-nodes")
    launch.add_argument("--provider-evidence")
    launch.add_argument("--allow-openmpi-root", action="store_true")
    rank = sub.add_parser("rank-worker")
    rank.add_argument("--output-dir", required=True)
    rank.add_argument("--manifest-sha256", required=True)
    rank.add_argument("--rank", type=int)
    args = parser.parse_args()
    try:
        return launch_main(args) if args.command == "launch" else rank_main(args)
    except BaseException as exc:
        print(json.dumps({"status": "FAILED_BEFORE_RECEIPT_DIRECTORY", "type": type(exc).__name__,
                          "error": str(exc)}), file=sys.stderr, flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
