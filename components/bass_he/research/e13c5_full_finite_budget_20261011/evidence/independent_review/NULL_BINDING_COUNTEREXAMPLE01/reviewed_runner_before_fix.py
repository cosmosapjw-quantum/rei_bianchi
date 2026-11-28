#!/usr/bin/env python3
"""One saved-result exact budget replay; no solver, network, or native execution."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import gzip
import json
import os
from pathlib import Path, PurePosixPath
import platform
import resource
import shutil
import signal
import stat
import subprocess
import sys
import tarfile
import time
import zipfile

LOCK_SHA256 = "cdfda6cd49eeb38518b2a41156a087f744e0985e0384bf628ca8b893dbec5b3a"
SCHEMA = "bass-he-e13c5-full-finite-budget-ncp-v1"

def stamp():
    return datetime.now(timezone.utc).isoformat()

def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def canonical_sha(obj):
    value = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(value).hexdigest()

def semantic_projection(obj):
    value = dict(obj)
    if "ranking_artifact" in value:
        ranking = dict(value["ranking_artifact"])
        ranking.pop("bytes", None)
        ranking.pop("sha256", None)
        value["ranking_artifact"] = ranking
    return value

def verify_saved_outputs(budget_dir, lock):
    result_path = budget_dir / "RESULTS.json"
    projection_path = budget_dir / "NUMERICAL_PROJECTION.json"
    result = json.loads(result_path.read_text())
    projection = json.loads(projection_path.read_text())
    expected = lock["expected_projection"]
    actual_file = {"bytes": projection_path.stat().st_size, "sha256": sha(projection_path)}
    raw_match = actual_file == {"bytes": expected["bytes"], "sha256": expected["sha256"]}
    actual_semantic = canonical_sha(semantic_projection(projection))
    if actual_semantic != expected["semantic_sha256"]:
        raise ValueError("NUMERICAL_SEMANTIC_PROJECTION_PARITY_FAILURE")
    if result.get("status") != lock["expected_budget_status"]:
        raise ValueError("BUDGET_STATUS_FAILURE")
    for key, value in projection.items():
        if result.get(key) != value:
            raise ValueError("FRESH_RESULT_PROJECTION_BINDING_FAILURE: " + key)
    ranking_evidence = None
    if "expected_ranking_content" in lock:
        ranking_path = budget_dir / "WIDTH_RANKINGS.csv.gz"
        claimed = projection["ranking_artifact"]
        actual_gzip = {"bytes": ranking_path.stat().st_size, "sha256": sha(ranking_path)}
        if actual_gzip != {"bytes": claimed["bytes"], "sha256": claimed["sha256"]}:
            raise ValueError("RANKING_GZIP_IDENTITY_MISMATCH")
        target = lock["expected_ranking_content"]
        digest = hashlib.sha256()
        count = 0
        with gzip.open(ranking_path, "rb") as f:
            for block in iter(lambda: f.read(1024 * 1024), b""):
                count += len(block)
                if count > target["bytes"]:
                    raise ValueError("RANKING_CONTENT_PARITY_FAILURE")
                digest.update(block)
        actual_plain = {"bytes": count, "sha256": digest.hexdigest()}
        if actual_plain != {"bytes": target["bytes"], "sha256": target["sha256"]}:
            raise ValueError("RANKING_CONTENT_PARITY_FAILURE")
        ranking_evidence = {"gzip": actual_gzip, "uncompressed_CSV": actual_plain,
                            "uncompressed_content_parity": True}
    return {"projection_file": actual_file, "raw_projection_file_parity": raw_match,
            "canonical_object_sha256": canonical_sha(projection),
            "semantic_sha256": actual_semantic, "semantic_projection_parity": True,
            "excluded_from_semantic_projection": ["ranking_artifact.bytes", "ranking_artifact.sha256"],
            "ranking": ranking_evidence, "fresh_result_sha256": sha(result_path)}

def write_json(path, obj):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("x", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(temporary, path)

def safe_member(name):
    p = PurePosixPath(name)
    if not name or "\\" in name or p.is_absolute() or any(x in ("", ".", "..") for x in p.parts):
        raise ValueError("UNSAFE_ARCHIVE_MEMBER: " + name)
    return p

def inside(root, relative):
    p = safe_member(relative)
    target = Path(root).joinpath(*p.parts)
    if not target.resolve().is_relative_to(Path(root).resolve()):
        raise ValueError("PATH_ESCAPES_ROOT: " + relative)
    return target

def identities(root, records):
    actual = {}
    for relative, expected in records.items():
        p = inside(root, relative)
        if p.is_symlink() or not p.is_file():
            raise ValueError("LOCKED_REGULAR_FILE_MISSING: " + relative)
        found = {"bytes": p.stat().st_size, "sha256": sha(p)}
        actual[relative] = found
        if found != {"bytes": expected["bytes"], "sha256": expected["sha256"]}:
            raise ValueError("FILE_IDENTITY_MISMATCH: " + relative)
    return actual

def copy_regular(source, destination, expected_bytes):
    temporary = destination.with_name(destination.name + ".partial")
    stream = hashlib.sha256()
    count = 0
    with temporary.open("xb") as f:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            if f.write(block) != len(block):
                raise ValueError("SHORT_ARCHIVE_MEMBER_WRITE")
            stream.update(block)
            count += len(block)
        f.flush()
        os.fsync(f.fileno())
    if count != expected_bytes or temporary.stat().st_size != expected_bytes:
        raise ValueError("ARCHIVE_MEMBER_SIZE_MISMATCH")
    os.replace(temporary, destination)
    persisted = sha(destination)
    if persisted != stream.hexdigest():
        raise ValueError("PERSISTED_MEMBER_IDENTITY_MISMATCH")
    return {"bytes": count, "sha256": persisted}

def extract_dependency(archive, target, kind, expected_count, expected_bytes):
    target.mkdir(parents=True, exist_ok=False)
    seen = set()
    total = 0
    count = 0
    member_identities = {}
    if kind == "tar.gz":
        with tarfile.open(archive, "r:gz") as t:
            for entry in t:
                rel = str(safe_member(entry.name))
                if not entry.isfile() or rel in seen:
                    raise ValueError("NONREGULAR_OR_DUPLICATE_TAR_MEMBER: " + rel)
                seen.add(rel)
                total += entry.size
                count += 1
                if total > expected_bytes or count > expected_count:
                    raise ValueError("ARCHIVE_SIZE_OR_COUNT_EXCEEDED")
                dst = inside(target, rel)
                dst.parent.mkdir(parents=True, exist_ok=True)
                source = t.extractfile(entry)
                if source is None:
                    raise ValueError("MISSING_TAR_BYTES")
                with source:
                    member_identities[rel] = copy_regular(source, dst, entry.size)
    elif kind == "zip":
        with zipfile.ZipFile(archive) as z:
            for entry in z.infolist():
                rel = str(safe_member(entry.filename))
                mode = (entry.external_attr >> 16) & 0o170000
                if entry.is_dir() or mode == stat.S_IFLNK or rel in seen:
                    raise ValueError("NONREGULAR_OR_DUPLICATE_ZIP_MEMBER: " + rel)
                if mode not in (0, stat.S_IFREG):
                    raise ValueError("NONREGULAR_ZIP_MEMBER: " + rel)
                seen.add(rel)
                total += entry.file_size
                count += 1
                if total > expected_bytes or count > expected_count:
                    raise ValueError("ARCHIVE_SIZE_OR_COUNT_EXCEEDED")
                dst = inside(target, rel)
                dst.parent.mkdir(parents=True, exist_ok=True)
                with z.open(entry) as source:
                    member_identities[rel] = copy_regular(source, dst, entry.file_size)
    else:
        raise ValueError("UNKNOWN_ARCHIVE_FORMAT")
    if (count, total) != (expected_count, expected_bytes):
        raise ValueError("ARCHIVE_FINAL_SIZE_OR_COUNT_MISMATCH")
    return {"regular_files": count, "unpacked_bytes": total,
            "persisted_member_identities": member_identities}

def host_record(label):
    rec = {"declared_host_label": label, "provider_verified": False,
           "hostname": platform.node(), "python": platform.python_version(),
           "executable": sys.executable, "platform": platform.platform(),
           "machine": platform.machine(), "cpu_count": os.cpu_count(),
           "utc": stamp()}
    if hasattr(os, "sched_getaffinity"):
        rec["cpu_affinity"] = sorted(os.sched_getaffinity(0))
    return rec

def available_memory():
    values = {}
    p = Path("/proc/meminfo")
    if p.is_file():
        for line in p.read_text().splitlines():
            if line.startswith("MemAvailable:"):
                values["proc_mem_available_bytes"] = int(line.split()[1]) * 1024
    root = Path("/sys/fs/cgroup")
    mx, current = root / "memory.max", root / "memory.current"
    if mx.is_file() and current.is_file():
        text = mx.read_text().strip()
        if text != "max":
            values["cgroup_limit_bytes"] = int(text)
            values["cgroup_current_bytes"] = int(current.read_text().strip())
            values["cgroup_available_bytes"] = max(0, values["cgroup_limit_bytes"] - values["cgroup_current_bytes"])
    bounds = [v for k, v in values.items() if k.endswith("available_bytes")]
    return {"observed": values, "available_bound_bytes": min(bounds) if bounds else None}

def child_limits(memory_bytes, cpu_seconds):
    resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))

def run(package, out, execute=False, host_label="unspecified"):
    package = Path(package).resolve()
    out = Path(out).resolve()
    if out.exists():
        raise ValueError("FRESH_OUTPUT_DIRECTORY_REQUIRED")
    if out.is_relative_to(package):
        raise ValueError("OUTPUT_MUST_BE_OUTSIDE_IMMUTABLE_PACKAGE")
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    lock_path = package / "RUN_LOCK.json"
    script = Path(__file__).resolve()
    initial_self = sha(script)
    state = {"schema": SCHEMA, "status": "STARTED", "started_utc": stamp(),
             "execution_requested": execute, "host": host_record(host_label),
             "physics_invocations": 0, "full_first2_invocations": 0,
             "N512_invocations": 0, "budget_invocations": 0,
             "new_coefficient_evaluations": 0, "native_runs": 0,
             "gas_advances": 0, "old_continuous_solves": 0,
             "automatic_retry": False, "source_sha256_before": initial_self,
             "holds": ["continuum_spectral_quadrature", "physical_global_production",
                       "new_gas_evolution", "actual_photon_heat_recoil_delivery", "receiver_adoption"],
             "accuracy": "NOT_EVALUATED", "ncp_provider_verification": "NOT_EVALUATED"}
    write_json(out / "START.json", state)
    try:
        if sys.version_info[:2] != (3, 12) or platform.system() != "Linux":
            raise ValueError("REQUIRES_CPYTHON_3_12_LINUX")
        if platform.python_implementation() != "CPython":
            raise ValueError("REQUIRES_CPYTHON")
        if sha(lock_path) != LOCK_SHA256:
            raise ValueError("RUN_LOCK_IDENTITY_MISMATCH")
        lock = json.loads(lock_path.read_text())
        state["run_lock_sha256"] = LOCK_SHA256
        before = identities(package, lock["files"])
        state["locked_files_before"] = before
        disk = shutil.disk_usage(out)
        memory = available_memory()
        state["preflight"] = {"free_disk_bytes": disk.free, "memory": memory}
        if disk.free < lock["limits"]["minimum_free_disk_bytes"]:
            raise ValueError("INSUFFICIENT_FREE_DISK")
        bound = memory["available_bound_bytes"]
        if bound is None or bound < lock["limits"]["minimum_available_memory_bytes"]:
            raise ValueError("INSUFFICIENT_OR_UNKNOWN_AVAILABLE_MEMORY")
        if not execute:
            state.update({"status": "VERIFY_ONLY_READY", "reduction": "NOT_RUN",
                          "accuracy": "NOT_EVALUATED"})
        else:
            work = out / "WORK"
            work.mkdir()
            extracted = {}
            for name, dep in lock["dependencies"].items():
                target = work / name
                extracted[name] = extract_dependency(
                    package / dep["path"], target, dep["format"],
                    dep["regular_files"], dep["unpacked_bytes"])
            state["extraction"] = extracted
            input_paths = {}
            input_before = {}
            for flag, item in lock["input_map"].items():
                base = work / item["dependency"]
                p = inside(base, item["member"])
                input_before[flag] = identities(base, {item["member"]: item})[item["member"]]
                input_paths[flag] = p
            state["extracted_input_identities_before"] = input_before
            command = [sys.executable, "-B", str(package / "code/full_finite_budget.py")]
            for flag, p in input_paths.items():
                command.extend(["--" + flag, str(p)])
            command.extend(["--contract", str(package / "SCIENTIFIC_CONTRACT.json"),
                            "--out", str(out / "BUDGET")])
            state["command_argv"] = command
            state["budget_invocations"] = 1
            write_json(out / "CHECKPOINT.json", state)
            env = os.environ.copy()
            env.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
                        "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1",
                        "PYTHONDONTWRITEBYTECODE": "1"})
            child_wall = lock["limits"]["child_wall_seconds"]
            child_start = time.monotonic()
            usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
            timed_out = False
            with (out / "stdout.log").open("xb") as stdout, (out / "stderr.log").open("xb") as stderr:
                process = subprocess.Popen(
                    command, stdout=stdout, stderr=stderr, env=env,
                    start_new_session=True,
                    preexec_fn=lambda: child_limits(lock["limits"]["child_address_space_bytes"],
                                                   lock["limits"]["child_cpu_seconds"]))
                try:
                    exit_code = process.wait(timeout=child_wall)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        exit_code = process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        exit_code = process.wait(timeout=5)
            usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
            state["child"] = {"exit_code": exit_code, "timed_out": timed_out,
                              "wall_seconds": time.monotonic() - child_start,
                              "user_cpu_seconds": usage_after.ru_utime - usage_before.ru_utime,
                              "system_cpu_seconds": usage_after.ru_stime - usage_before.ru_stime,
                              "max_rss_KiB": usage_after.ru_maxrss}
            # Check lock bytes and extracted inputs against the original expectations,
            # even when a child failed. Do not reload a changed lock to weaken the pins.
            if sha(lock_path) != LOCK_SHA256:
                raise ValueError("RUN_LOCK_CHANGED_DURING_RUN")
            state["locked_files_after"] = identities(package, lock["files"])
            input_after = {}
            for flag, item in lock["input_map"].items():
                base = work / item["dependency"]
                input_after[flag] = identities(base, {item["member"]: item})[item["member"]]
            state["extracted_input_identities_after"] = input_after
            if timed_out or exit_code != 0:
                raise ValueError("BUDGET_CHILD_FAILED")
            parity = verify_saved_outputs(out / "BUDGET", lock)
            state.update({"status": "PASS_SCOPED_SAVED_FULL_FINITE_BUDGET_PARITY",
                          "accuracy": "EXACT_NUMERICAL_PROJECTION_AND_RANKING_CONTENT_PARITY",
                          "reduction": "EXECUTED_ON_RECORDED_HOST",
                          "parity": parity,
                          "full_finite_cover": "DONE_INHERITED_PR20",
                          "two_OFF_N512": "DONE_INHERITED_PR19_REFINEMENT"})
        if sha(lock_path) != LOCK_SHA256:
            raise ValueError("RUN_LOCK_CHANGED")
        state["locked_files_after"] = identities(package, lock["files"])
        if sha(script) != initial_self:
            raise ValueError("RUNNER_SOURCE_CHANGED")
        state["source_sha256_after"] = sha(script)
    except Exception as exc:
        state.update({"status": "FAIL_STOP_PRESERVE", "error_type": type(exc).__name__,
                      "error": str(exc), "accuracy": "NOT_ADMITTED"})
    state["finished_utc"] = stamp()
    state["wrapper_wall_seconds"] = time.monotonic() - start
    write_json(out / "RUN_RECEIPT.json", state)
    print(json.dumps({k: state[k] for k in ("status", "budget_invocations", "physics_invocations", "accuracy")}))
    return 0 if state["status"] in ("VERIFY_ONLY_READY", "PASS_SCOPED_SAVED_FULL_FINITE_BUDGET_PARITY") else 1

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--package", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--execute", action="store_true")
    p.add_argument("--host-label", default="unspecified")
    a = p.parse_args()
    return run(a.package, a.out, a.execute, a.host_label)

if __name__ == "__main__":
    raise SystemExit(main())

