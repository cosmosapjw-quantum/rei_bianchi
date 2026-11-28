"""Read-only Linux resource/process observations and one stable HE29 lease.

Resource admission and process admission are separate; the launcher must require
both execution_allowed values.  Affinity limits placement, not CPU ownership.
Memory estimates below are scheduling estimates, never measured RSS bounds.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import errno
import fcntl
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import re
import socket
import stat

GIB = 1024**3
DEFAULT_LEASE = Path("/tmp/BASS_HE_HE29_NATIVE.lock")
HE29_SCRIPTS = frozenset(("reference_runner.py", "run_packed.py", "run_vigilode.py",
    "hpc_canary.py", "batch_entry.py", "continue_missing_references.py"))
NAMESPACES = ("BASS_HE", "VigilODE", "REI", "REC", "HH", "BASS", "bass_cr")
CGROUP_ROOT_PROOF = {
    "documentation": "https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html",
    "source": "https://github.com/torvalds/linux/blob/v6.8/kernel/cgroup/cgroup.c",
    "source_blob": "a66c088c851cfb87036ccc93317f7357769cb268",
    "rule": "cgroup.type CFTYPE_NOT_ON_ROOT is filtered by actual cgroup_parent, not a namespace-relative slash",
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def read_observation(path):
    try:
        return {"status": "OBSERVED", "value": Path(path).read_text().strip()}
    except PermissionError as exc:
        return {"status": "PERMISSION_DENIED", "error": str(exc)}
    except FileNotFoundError as exc:
        return {"status": "NOT_FOUND", "error": str(exc)}
    except OSError as exc:
        return {"status": "READ_ERROR", "error": str(exc)}


def unescape_mount(value):
    return re.sub(r"\\([0-7]{3})", lambda m: chr(int(m.group(1), 8)), value)


def cgroup_observation(proc_root):
    membership = read_observation(proc_root / "self/cgroup")
    mounts = read_observation(proc_root / "self/mountinfo")
    result = {"membership": membership, "mountinfo_status": mounts["status"],
              "ancestors": [], "visibility": "visible cgroup v2 mount and ancestors only"}
    if membership["status"] != "OBSERVED" or mounts["status"] != "OBSERVED":
        result["status"] = "UNKNOWN"
        return result
    unified = [line.split(":", 2)[2] for line in membership["value"].splitlines()
               if line.startswith("0::")]
    candidates = []
    for line in mounts["value"].splitlines():
        fields = line.split()
        if "-" not in fields:
            continue
        split = fields.index("-")
        if split + 1 < len(fields) and fields[split + 1] == "cgroup2" and len(fields) >= 6:
            candidates.append((Path(unescape_mount(fields[3])), Path(unescape_mount(fields[4]))))
    if len(unified) != 1 or not candidates:
        result["status"] = "UNKNOWN_NO_UNIFIED_CGROUP"
        return result
    group = Path(unified[0])
    applicable = [(root, mount) for root, mount in candidates if group.is_relative_to(root)]
    if not applicable:
        result["status"] = "UNKNOWN_MEMBERSHIP_OUTSIDE_VISIBLE_MOUNT"
        return result
    root, mount = max(applicable, key=lambda pair: len(pair[0].parts))
    leaf = mount / group.relative_to(root)
    result.update(status="OBSERVED", membership_path=str(group), mount_root=str(root),
                  mount_point=str(mount), leaf=str(leaf))
    for path in (leaf, *leaf.parents):
        if not path.is_relative_to(mount):
            break
        result["ancestors"].append({"path": str(path),
            **{name: read_observation(path / name)
               for name in ("cpu.max", "memory.max", "memory.current")}})
        if path == mount:
            break
    core = {name: read_observation(mount / name) for name in ("cgroup.controllers", "cgroup.type")}
    mounted = result["ancestors"][-1]
    global_signature = (core["cgroup.controllers"]["status"] == "OBSERVED"
        and core["cgroup.type"]["status"] == "NOT_FOUND"
        and mounted["cpu.max"]["status"] == mounted["memory.max"]["status"] == "NOT_FOUND")
    classification = ("ACTUAL_GLOBAL_ROOT_SIGNATURE" if global_signature else
        "ACTUAL_NONROOT_NAMESPACE_OR_SUBTREE_MOUNT" if core["cgroup.type"]["status"] == "OBSERVED"
        else "ROOT_KIND_UNPROVEN")
    result["mount_root_identity"] = {"classification": classification,
        "core_files": core, "proof_basis": CGROUP_ROOT_PROOF,
        "slash_path_alone_used_as_root_proof": False}
    return result


def observe_host(*, proc_root=Path("/proc"), sys_root=Path("/sys"), affinity=None):
    """Observe this process's Linux limits; no affinity changes or job starts."""
    proc_root, sys_root = Path(proc_root), Path(sys_root)
    errors = []
    if affinity is None:
        try:
            affinity = sorted(os.sched_getaffinity(0))
            affinity_source = "os.sched_getaffinity(0)"
        except (AttributeError, OSError) as exc:
            affinity, affinity_source = [], "UNOBSERVED"
            errors.append("AFFINITY_UNOBSERVED: " + str(exc))
    else:
        affinity, affinity_source = sorted(affinity), "explicit fixture override"
    meminfo = read_observation(proc_root / "meminfo")
    memory = {"status": meminfo["status"]}
    if meminfo["status"] == "OBSERVED":
        for line in meminfo["value"].splitlines():
            match = re.fullmatch(r"(MemTotal|MemAvailable):\s+(\d+)\s+kB", line)
            if match:
                memory[match.group(1) + "_bytes"] = int(match.group(2)) * 1024
    else:
        memory["error"] = meminfo.get("error")
    topology = []
    for cpu in affinity:
        entry = {"cpu": cpu}
        path = sys_root / f"devices/system/cpu/cpu{cpu}/topology"
        for name in ("physical_package_id", "core_id", "thread_siblings_list"):
            observed = read_observation(path / name)
            entry[name] = observed
        topology.append(entry)
    return {"schema": "he29.hpc64.host_observation.v1", "observed_utc": utc_now(),
        "hostname": socket.gethostname(), "pid": os.getpid(), "kernel_release": os.uname().release,
        "affinity": {"cpu_ids": affinity, "source": affinity_source},
        "memory": memory, "cgroup_v2": cgroup_observation(proc_root),
        "physical_core_mapping": topology, "errors": errors,
        "process_scan": "separate active_he29_processes result required by launcher",
        "scope": "read-only local Linux observation; no NCP identity or process execution claimed"}


def choose_resources(host, max_table_workers=48, max_build_jobs=8, reserve_cpus=8,
                     reserve_memory_gib=16, worker_estimate_gib=1):
    """Conservative resource plan under all observed ancestor quotas/headroom."""
    for name, value, low in (("max_table_workers", max_table_workers, 1),
                             ("max_build_jobs", max_build_jobs, 1), ("reserve_cpus", reserve_cpus, 0)):
        if type(value) is not int or value < low:
            raise ValueError("HE29_HOST_ARGUMENT: " + name)
    if max_table_workers > 48 or max_build_jobs > 8:
        raise ValueError("HE29_HOST_MAX_CONCURRENCY")
    for name, value, positive in (("reserve_memory_gib", reserve_memory_gib, False),
                                  ("worker_estimate_gib", worker_estimate_gib, True)):
        if (type(value) not in (int, float) or not math.isfinite(value)
                or value < 0 or (positive and value == 0)):
            raise ValueError("HE29_HOST_ARGUMENT: " + name)
    reasons = list(host.get("errors", []))
    affinity = host.get("affinity", {}).get("cpu_ids", [])
    if not affinity or any(type(x) is not int or x < 0 for x in affinity) or len(set(affinity)) != len(affinity):
        reasons.append("AFFINITY_NOT_OBSERVED")
        affinity = []
    protected = [55] if 55 in affinity else []
    eligible = sorted(set(affinity) - set(protected))
    cgroup = host.get("cgroup_v2", {})
    ancestors = cgroup.get("ancestors", [])
    quotas, memory_limits, headrooms = [], [], []
    if cgroup.get("status") != "OBSERVED" or not ancestors:
        reasons.append("CGROUP_V2_LIMITS_UNOBSERVED")
    for entry in ancestors:
        label = entry.get("path", "unknown ancestor")
        cpu = entry.get("cpu.max", {})
        actual_global_root = (label == cgroup.get("mount_point")
            and cgroup.get("mount_root_identity", {}).get("classification") == "ACTUAL_GLOBAL_ROOT_SIGNATURE")
        try:
            if actual_global_root and cpu.get("status") == "NOT_FOUND":
                quota, period = "max", 1
            elif cpu.get("status") == "OBSERVED":
                quota, period = cpu["value"].split()
                period = int(period)
            else:
                raise ValueError("not observed")
            if period <= 0:
                raise ValueError("period")
            if quota != "max":
                quota = int(quota)
                if quota <= 0:
                    raise ValueError("quota")
                quotas.append(Fraction(quota, period))
        except (KeyError, TypeError, ValueError):
            reasons.append("CPU_QUOTA_UNOBSERVED_OR_INVALID: " + label)
        limit, used = entry.get("memory.max", {}), entry.get("memory.current", {})
        try:
            if actual_global_root and limit.get("status") == "NOT_FOUND":
                maximum_text = "max"
            elif limit.get("status") == "OBSERVED":
                maximum_text = limit["value"]
            else:
                raise ValueError("limit unobserved")
            if maximum_text != "max":
                maximum = int(maximum_text)
                if maximum <= 0 or used.get("status") != "OBSERVED":
                    raise ValueError("finite limit/headroom unobserved")
                current = int(used["value"])
                if current < 0:
                    raise ValueError("current")
                memory_limits.append(maximum)
                headrooms.append(max(0, maximum - current))
        except (KeyError, TypeError, ValueError):
            reasons.append("MEMORY_LIMIT_OR_HEADROOM_UNOBSERVED: " + label)
    memory = host.get("memory", {})
    total, available = memory.get("MemTotal_bytes"), memory.get("MemAvailable_bytes")
    if (type(total) is not int or type(available) is not int
            or not 0 < available <= total):
        reasons.append("MEMTOTAL_OR_MEMAVAILABLE_UNOBSERVED")
        total = available = 0
    quota = min(quotas) if quotas else None
    cpu_capacity = min(len(eligible), quota.numerator // quota.denominator if quota else len(eligible))
    cpu_slots = max(0, cpu_capacity - reserve_cpus)
    capacity = min([total, *memory_limits])
    available_bytes = min([available, *headrooms])
    memory_reserve = max(math.ceil(reserve_memory_gib * GIB), (capacity + 4) // 5)
    fixed_overhead = 2 * GIB
    worker_estimate = math.ceil(worker_estimate_gib * GIB)
    distributable = max(0, available_bytes - memory_reserve - fixed_overhead)
    memory_slots = distributable // worker_estimate
    build_memory_slots = distributable // (2 * GIB)
    if cpu_slots < 1:
        reasons.append("CPU_CAPACITY_EXHAUSTED_AFTER_RESERVE")
    if memory_slots < 1 or build_memory_slots < 1:
        reasons.append("MEMORY_HEADROOM_EXHAUSTED_AFTER_RESERVE")
    # Prefer one logical CPU per observed physical core before SMT siblings.
    topology = {}
    for entry in host.get("physical_core_mapping", []):
        try:
            package, core = entry["physical_package_id"], entry["core_id"]
            if package["status"] == core["status"] == "OBSERVED":
                topology[entry["cpu"]] = (int(package["value"]), int(core["value"]))
        except (KeyError, TypeError, ValueError):
            pass
    seen, primary, siblings = set(), [], []
    for cpu in eligible:
        key = topology.get(cpu, ("unobserved", cpu))
        (siblings if key in seen else primary).append(cpu)
        seen.add(key)
    order = primary + siblings
    table_workers = min(max_table_workers, cpu_slots, memory_slots)
    build_jobs = min(max_build_jobs, cpu_slots, build_memory_slots)
    supplied_process_scan = host.get("process_observation")
    if supplied_process_scan is not None and supplied_process_scan.get("execution_allowed") is not True:
        reasons.extend(supplied_process_scan.get("hold_reasons", ["PROCESS_OBSERVATION_HOLD"]))
    reasons = list(dict.fromkeys(reasons))
    allowed = not reasons
    ids = order[:max(table_workers, build_jobs)] if allowed else []
    return {"schema": "he29.hpc64.resource_plan.v1", "observed_utc": host.get("observed_utc"),
        "execution_allowed": allowed, "hold_reasons": reasons, "cpu_ids": ids,
        "table_workers": table_workers if allowed else 0, "build_jobs": build_jobs if allowed else 0,
        "affinity_cpu_count": len(affinity), "eligible_cpu_count": len(eligible),
        "protected_cpu_ids": protected, "reserved_cpu_count": reserve_cpus,
        "effective_cpu_capacity": cpu_capacity, "cpu_slots_after_reserve": cpu_slots,
        "ancestor_min_cpu_quota_cores": None if quota is None else float(quota),
        "ancestor_min_cpu_quota_fraction": None if quota is None else str(quota),
        "mount_root_classification": cgroup.get("mount_root_identity", {}).get("classification", "UNOBSERVED"),
        "absent_control_files_unlimited_only_for_actual_global_root": True,
        "effective_memory_capacity_bytes": capacity, "effective_memory_available_bytes": available_bytes,
        "reserved_memory_bytes": memory_reserve, "fixed_overhead_estimate_bytes": fixed_overhead,
        "worker_estimate_bytes": worker_estimate, "build_job_estimate_bytes": 2 * GIB,
        "memory_available_for_workers_bytes": distributable,
        "topology_observed_cpu_count": len(topology), "cpu_order": "one per observed core before SMT siblings",
        "rss_bound_measured": False, "process_admission_required_separately": supplied_process_scan is None,
        "parallel_phases": "build and table generation are sequential phases; no summed concurrent jobs"}


def parse_stat(text):
    # comm can contain spaces or parentheses; fields after the final ')' are fixed.
    fields = text[text.rfind(")") + 2:].split()
    if len(fields) < 2:
        raise ValueError("HE29_PROC_STAT_FORMAT")
    return {"state": fields[0], "ppid": int(fields[1]),
            "start_ticks": int(fields[19]) if len(fields) > 19 else None}


def ancestor_pids(proc_root):
    pids, pid = set(), os.getpid()
    while pid > 0 and pid not in pids:
        pids.add(pid)
        try:
            pid = parse_stat((proc_root / str(pid) / "stat").read_text())["ppid"]
        except (OSError, ValueError):
            break
    return pids


def namespace_of(token):
    for part in Path(token).parts:
        for namespace in sorted(NAMESPACES, key=len, reverse=True):
            if re.fullmatch(re.escape(namespace) + r"(?:[0-9]+)?(?:[_-].*)?", part, flags=re.IGNORECASE):
                return namespace
    return None


def active_he29_processes(binary, proc_root=Path("/proc")):
    """Read actual cmdline tokens; exclude self/ancestors; never signal a PID."""
    proc_root = Path(proc_root)
    excluded = ancestor_pids(proc_root)
    binary_path = str(Path(binary).resolve()) if binary is not None else None
    matches, others, denied, vanished, errors, zombies = [], [], [], [], [], []
    try:
        pids = sorted(int(p.name) for p in proc_root.iterdir() if p.name.isdigit() and int(p.name) > 0)
    except OSError as exc:
        return {"schema": "he29.hpc64.process_observation.v1", "observed_utc": utc_now(),
            "execution_allowed": False, "hold_reasons": ["PROC_ENUMERATION_FAILED"],
            "matches": [], "other_scientific_matches": [],
            "permission_denied": [{"path": str(proc_root), "error": str(exc)}],
            "vanished_pids": [], "read_errors": [], "excluded_pids": sorted(excluded)}
    for pid in pids:
        if pid in excluded:
            continue
        folder = proc_root / str(pid)
        try:
            raw = (folder / "cmdline").read_bytes()
            tokens = [part.decode("utf-8", "surrogateescape") for part in raw.split(b"\0") if part]
            if not tokens:
                continue
            state = parse_stat((folder / "stat").read_text())
            if state["state"] in ("Z", "X", "x"):
                zombies.append(pid)
                continue
        except PermissionError as exc:
            denied.append({"pid": pid, "path": str(exc.filename or folder), "error": str(exc)})
            continue
        except FileNotFoundError:
            vanished.append(pid)
            continue
        except (OSError, ValueError) as exc:
            errors.append({"pid": pid, "error": str(exc)})
            continue
        matched_tokens = [token for token in tokens if Path(token).name in HE29_SCRIPTS]
        binary_match = binary_path is not None and binary_path in tokens
        executable = Path(tokens[0]).name
        if binary_path is not None and executable == Path(binary_path).name:
            try:
                actual_exe = os.readlink(folder / "exe").removesuffix(" (deleted)")
                binary_match = binary_match or actual_exe == binary_path
            except PermissionError as exc:
                denied.append({"pid": pid, "path": str(folder / "exe"), "error": str(exc)})
            except FileNotFoundError:
                vanished.append(pid)
                continue
            except OSError as exc:
                errors.append({"pid": pid, "path": str(folder / "exe"), "error": str(exc)})
        namespace_tokens = [(namespace_of(token), token) for token in tokens]
        namespace_tokens = [(namespace, token) for namespace, token in namespace_tokens if namespace]
        record = {"pid": pid, "ppid": state["ppid"], "state": state["state"],
            "start_ticks": state["start_ticks"], "executable_token": tokens[0],
            "cmdline_sha256": hashlib.sha256(raw).hexdigest()}
        if matched_tokens or binary_match:
            matches.append({**record, "namespace": "HE29", "matched_script_tokens": matched_tokens,
                            "owner_binary_match": binary_match})
        else:
            interpreter = bool(re.fullmatch(r"python(?:\d+(?:\.\d+)*)?|pypy\d*|Rscript|R|julia|mpiexec|mpirun|srun|cargo|rustc", executable))
            utility = executable in ("git", "cat", "rg", "ls", "find", "bash", "sh", "zsh",
                "less", "head", "tail", "sed", "awk", "sleep", "timeout", "tee", "cp", "mv", "tar", "gzip")
            cwd, cwd_namespace = None, None
            # Relative scientific commands often carry no repo name in argv.
            # Observe their actual cwd instead of treating that as absence.
            if not namespace_tokens and not utility:
                try:
                    cwd = os.readlink(folder / "cwd").removesuffix(" (deleted)")
                    cwd_namespace = namespace_of(cwd)
                except PermissionError as exc:
                    denied.append({"pid": pid, "path": str(folder / "cwd"), "error": str(exc)})
                except FileNotFoundError:
                    vanished.append(pid)
                    continue
                except OSError as exc:
                    errors.append({"pid": pid, "path": str(folder / "cwd"), "error": str(exc)})
            scientific_native = not utility and (namespace_of(tokens[0]) is not None or cwd_namespace is not None)
            if (namespace_tokens or cwd_namespace) and (interpreter or scientific_native):
                namespaces = {item[0] for item in namespace_tokens}
                if cwd_namespace is not None:
                    namespaces.add(cwd_namespace)
                others.append({**record, "namespaces": sorted(namespaces),
                    "matched_namespace_tokens": [item[1] for item in namespace_tokens][:8],
                    "observed_cwd": cwd, "namespace_from_cwd": cwd_namespace,
                    "classification": "live scientific/build candidate; activity or idle state not inferred"})
    reasons = []
    if matches:
        reasons.append("ACTIVE_HE29_PROCESS_OBSERVED")
    if others:
        reasons.append("OTHER_SCIENTIFIC_PROCESS_OBSERVED")
    if denied or errors:
        reasons.append("PROC_VISIBILITY_INCOMPLETE")
    return {"schema": "he29.hpc64.process_observation.v1", "observed_utc": utc_now(),
        "execution_allowed": not reasons, "hold_reasons": reasons, "matches": matches,
        "other_scientific_matches": others, "permission_denied": denied,
        "vanished_pids": sorted(set(vanished)), "read_errors": errors,
        "zombie_pids_ignored": zombies, "excluded_pids": sorted(excluded),
        "pids_enumerated": len(pids), "scope": "observable local /proc cmdline tokens; no remote or all-history absence claim",
        "kill_or_signal_calls": 0}


def write_lease_record(fd, value):
    data = json.dumps(value, sort_keys=True, allow_nan=False).encode() + b"\n"
    os.lseek(fd, 0, os.SEEK_SET)
    os.ftruncate(fd, 0)  # Caller has already acquired the exclusive flock.
    while data:
        written = os.write(fd, data)
        if written <= 0:
            raise OSError("HE29_LEASE_SHORT_WRITE")
        data = data[written:]
    os.fsync(fd)


@contextmanager
def host_execution_lease(path=DEFAULT_LEASE):
    """Lock the shared stable inode. No truncation before lock, no unlink ever."""
    path = Path(path)
    if path.is_symlink():
        raise ValueError("HE29_LEASE_SYMLINK")
    flags = os.O_RDWR | os.O_CREAT | os.O_CLOEXEC | os.O_NOFOLLOW
    try:
        fd = os.open(path, flags, 0o600)
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise ValueError("HE29_LEASE_SYMLINK") from exc
        raise
    acquired = False
    record = None
    body_failed = True
    try:
        inode = os.fstat(fd)
        if not stat.S_ISREG(inode.st_mode) or inode.st_nlink != 1:
            raise ValueError("HE29_LEASE_NOT_SINGLE_REGULAR_INODE")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("HE29_HOST_EXECUTION_LEASE_BUSY") from exc
        acquired = True
        visible = path.lstat()
        if (stat.S_ISLNK(visible.st_mode)
                or (visible.st_dev, visible.st_ino) != (inode.st_dev, inode.st_ino)):
            raise ValueError("HE29_LEASE_INODE_CHANGED")
        record = {"schema": "he29.hpc64.host_lease.v1", "state": "ACTIVE",
            "hostname": socket.gethostname(), "pid": os.getpid(), "acquired_utc": utc_now(),
            "path": str(path.absolute()), "device": inode.st_dev, "inode": inode.st_ino,
            "locking": "flock LOCK_EX|LOCK_NB; stable inode retained on release"}
        write_lease_record(fd, record)
        yield dict(record)
        body_failed = False
    finally:
        try:
            if acquired and record is not None:
                write_lease_record(fd, {**record, "state": "RELEASED", "released_utc": utc_now(),
                                        "body_failed": body_failed})
        finally:
            if acquired:
                fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
