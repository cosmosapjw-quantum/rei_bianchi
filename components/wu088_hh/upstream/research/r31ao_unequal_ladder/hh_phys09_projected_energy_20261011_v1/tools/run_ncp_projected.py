#!/usr/bin/env python3
"""One bounded NCP build and saved-input PHYS09 gate/consumer execution.

READY_NOT_RUN in the PHYS09 research host. Existing rustc only; no installation,
Cargo, native producer, reference replay, root solve, or PHYS08 task dispatch.
Every command keeps raw logs and its first outcome. No automatic retry.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/projected_first"
LOG_LIMIT = 16 * 1024 * 1024
BOUND_RELATIVE = (
    "src/projected_gate.rs", "tests/projected_gate_tests.rs",
    "diagnostics/check_projected_rust.py", "tools/run_ncp_projected.py",
    "diagnostics/analyze_projected_exports.py", "src/exact_weighted.py",
    "results/projected_first/GATE_INPUTS.tsv", "results/projected_first/GOLDEN_ORACLE.json",
    "results/projected_first/PROJECTED_RESULTS.json", "SCIENTIFIC_CONTRACT.md",
    "GATE_INTERFACE.md", "NCP_TASKS.json", "inputs/ncp07/SOURCE_INTAKE_MANIFEST.json",
)


def now():
    return datetime.now(timezone.utc).isoformat()


def identity(path):
    path = Path(path)
    digest, size = hashlib.sha256(), 0
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
            size += len(chunk)
    return {"path": str(path.resolve()), "bytes": size, "sha256": digest.hexdigest()}


def emit(path, obj):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(obj, stream, indent=2, allow_nan=False)
        stream.write("\n")


def snapshot_inputs():
    result = []
    for name in BOUND_RELATIVE:
        try:
            item = identity(ROOT / name)
            item["relative_path"] = name
        except OSError as error:
            item = {"relative_path": name, "error": type(error).__name__, "message": str(error)}
        result.append(item)
    return result


def command(dest, argv, wall, memory):
    """Linux/POSIX wait4 records this child; kill its process group on timeout."""
    dest.mkdir(exist_ok=False)
    started, tick = now(), time.monotonic()
    timed_out, exit_code, wait_status, usage, process_id = False, 127, None, None, None
    launch_error = None

    def limits():
        resource.setrlimit(resource.RLIMIT_AS, (memory * 1024**2,) * 2)
        resource.setrlimit(resource.RLIMIT_FSIZE, (LOG_LIMIT,) * 2)
        resource.setrlimit(resource.RLIMIT_CPU, (wall,) * 2)

    with (dest / "stdout.txt").open("xb") as out, (dest / "stderr.txt").open("xb") as err:
        process = None
        try:
            process = subprocess.Popen(argv, cwd=ROOT, stdin=subprocess.DEVNULL,
                stdout=out, stderr=err, start_new_session=True, preexec_fn=limits,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "RAYON_NUM_THREADS": "1"})
            process_id = process.pid
            deadline = tick + wall
            while True:
                pid, status, stats = os.wait4(process.pid, os.WNOHANG)
                if pid == process.pid:
                    wait_status, usage = status, stats
                    process.returncode = os.waitstatus_to_exitcode(status)
                    exit_code = process.returncode
                    break
                if time.monotonic() >= deadline:
                    timed_out = True
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    _, status, stats = os.wait4(process.pid, 0)
                    wait_status, usage = status, stats
                    process.returncode = os.waitstatus_to_exitcode(status)
                    exit_code = 124
                    break
                time.sleep(min(0.02, max(0.0, deadline - time.monotonic())))
        except (OSError, subprocess.SubprocessError) as error:
            launch_error = {"class": type(error).__name__, "message": str(error)}
            err.write((type(error).__name__ + ": " + str(error) + "\n").encode())
            if process is not None and process.returncode is None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                try:
                    _, status, stats = os.wait4(process.pid, 0)
                    wait_status, usage = status, stats
                    process.returncode = os.waitstatus_to_exitcode(status)
                except ChildProcessError:
                    pass
    logs = [identity(dest / "stdout.txt"), identity(dest / "stderr.txt")]
    record = {"argv": argv, "cwd": str(ROOT), "started_utc": started, "finished_utc": now(),
        "elapsed_seconds": time.monotonic() - tick, "exit_code": exit_code,
        "actual_wait_exit_code": os.waitstatus_to_exitcode(wait_status) if wait_status is not None else None,
        "wait_status": wait_status, "pid": process_id, "timeout": timed_out,
        "launch_error": launch_error,
        "limits": {"wall_seconds": wall, "CPU_seconds": wall,
                   "address_space_MiB": memory, "file_MiB_each": 16},
        "user_seconds": usage.ru_utime if usage is not None else None,
        "system_seconds": usage.ru_stime if usage is not None else None,
        "maxrss_KiB_linux_wait4": usage.ru_maxrss if usage is not None else None,
        "rusage_basis": "os.wait4 for the named child, including its waited-for descendants",
        "logs": logs, "logs_within_limit": all(log["bytes"] <= LOG_LIMIT for log in logs)}
    emit(dest / "EXECUTION.json", record)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    requested = Path(args.run_dir).expanduser()
    if not requested.is_absolute():
        parser.error("--run-dir must be absolute")
    dest = requested.resolve()
    if dest == ROOT or ROOT in dest.parents:
        parser.error("--run-dir must be outside the frozen PHYS09 package")
    dest.mkdir(parents=True, exist_ok=False)
    records, failures = [], []
    before, after = [], []
    binary_before = binary_after = compiler_before = compiler_after = None
    rustc = shutil.which("rustc")
    binary = dest / "projected_gate_tests"
    emit(dest / "HOST.json", {"created_utc": now(), "platform": platform.platform(),
        "machine": platform.machine(), "python": sys.version, "python_executable": sys.executable,
        "rustc_path": rustc, "cargo_invoked": False,
        "cpu_affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
        "inherited_RUSTFLAGS": os.environ.get("RUSTFLAGS"),
        "inherited_RUSTFLAGS_applied_by_wrapper": False,
        "scope": "Dependency-free offline saved-data gate; no native producer, solver, or PHYS08 dispatch."})

    def fail(code, **details):
        failures.append({"code": code, "details": details, "created_utc": now()})

    def run(label, argv, wall, memory):
        record = command(dest / label, argv, wall, memory)
        records.append({"label": label, **record})
        if record["exit_code"] != 0 or not record["logs_within_limit"]:
            fail(label.upper() + "_FAILED_PRESERVE_NO_AUTO_RETRY", exit_code=record["exit_code"])

    try:
        before = snapshot_inputs()
        if any("error" in item for item in before):
            fail("REQUIRED_SOURCE_OR_INPUT_UNREADABLE")
        if not sys.platform.startswith("linux") or not hasattr(os, "wait4"):
            fail("UNSUPPORTED_RESOURCE_RECEIPT_PLATFORM")
        if rustc is None:
            fail("RUSTC_NOT_AVAILABLE_NO_INSTALL_ATTEMPT")
        if not failures:
            compiler_before = identity(rustc)
            run("compiler_identity", [rustc, "-vV"], 10, 512)
        if not failures:
            run("build_first", [rustc, "--edition=2021", "-C", "opt-level=0",
                "-C", "codegen-units=1", "-C", "overflow-checks=yes",
                str(ROOT / "tests/projected_gate_tests.rs"), "-o", str(binary)], 60, 512)
        if not failures:
            binary_before = identity(binary)
            run("gate_first", [str(binary), "--vectors", str(RESULTS / "GATE_INPUTS.tsv")], 15, 256)
        if not failures:
            run("consumer_first", [sys.executable, str(ROOT / "diagnostics/check_projected_rust.py"),
                "--oracle", str(RESULTS / "GOLDEN_ORACLE.json"),
                "--vectors", str(RESULTS / "GATE_INPUTS.tsv"),
                "--output", str(dest / "gate_first/stdout.txt"),
                "--report", str(dest / "ORACLE_CHECK.json")], 15, 256)
    except Exception as error:
        fail("WRAPPER_RUNTIME_FAILURE", exception=type(error).__name__, message=str(error))
    finally:
        after = snapshot_inputs()
        try:
            if compiler_before is not None:
                compiler_after = identity(rustc)
            if binary_before is not None:
                binary_after = identity(binary)
        except OSError as error:
            fail("PINNED_EXECUTABLE_UNREADABLE", exception=type(error).__name__, message=str(error))
        if before != after:
            fail("SOURCE_OR_INPUT_MUTATED")
        if compiler_before != compiler_after:
            fail("COMPILER_MUTATED")
        if binary_before != binary_after:
            fail("GATE_BINARY_MUTATED")

    if not failures:
        try:
            check = json.loads((dest / "ORACLE_CHECK.json").read_text())
            if check.get("status") != "PASS_SCOPED_OUTPUT_CONTAINMENT":
                raise ValueError("CONSUMER_EXIT_STATUS_CONFLICT")
            source = json.loads((RESULTS / "PROJECTED_RESULTS.json").read_text())
            details = {row["stage"]: row for row in source["details"]}
            emit(dest / "PROJECTED_ENERGY_SIDECAR.json", {
                "schema": "WU088_HH_PHYS09_NCP_PROJECTED_ENERGY_SIDECAR_V1",
                "status": "RUST_SAVED_JET_CONSUMER_VALIDATED", "created_utc": now(),
                "arithmetic_authority": "This NCP binary consumes the prebound 12594 signed saved-input interval rows.",
                "mathematical_authority": "Conditional source-family identity and exact-rational oracle, inherited source inclusion/C2 premises.",
                "projected_energy_claim": check["projected_energy_claim"],
                "rows": [{"stage": row["stage"], "input_exports": details[row["stage"]]["input_exports"],
                          "rust_stage_output": row["rust_stage_output"],
                          "projected_energy_actual_sign": row["projected_energy_actual_sign"]}
                         for row in check["stages"]],
                "oracle_check_identity": identity(dest / "ORACLE_CHECK.json"),
                "fresh_native_source_execution": False, "native_implicit_authority": False,
                "actual_native_root": None, "actual_native_U": None, "actual_native_V": None,
                "actual_native_W": None, "actual_native_I": None,
                "open": ["native implicit issuer authority", "carried second half", "paired defect",
                         "time and continuum remainder", "full49", "production"],
                "PHYS08_pending_task_invoked": False})
        except (OSError, ValueError, KeyError, TypeError) as error:
            fail("SIDECAR_INTEGRATION_FAILURE", exception=type(error).__name__, message=str(error))

    final = {"schema": "WU088_HH_PHYS09_NCP_PROJECTED_SAVED_GATE_RUN_V1",
        "status": "PASS_SCOPED" if not failures else "BLOCKED",
        "first_failure": failures[0] if failures else None, "failures": failures,
        "created_utc": now(), "records": records,
        "source_inputs_before": before, "source_inputs_after": after,
        "source_inputs_unchanged": before == after and not any("error" in item for item in before),
        "compiler_before": compiler_before, "compiler_after": compiler_after,
        "binary_before": binary_before, "binary_after": binary_after,
        "compiler_identity_invocations": sum(row["label"] == "compiler_identity" for row in records),
        "rust_build_invocations": sum(row["label"] == "build_first" for row in records),
        "gate_invocations": sum(row["label"] == "gate_first" for row in records),
        "oracle_consumer_invocations": sum(row["label"] == "consumer_first" for row in records),
        "fresh_native_source_routes": 0, "root_solver_routes": 0, "PHYS08_dispatches": 0,
        "counter_basis": "No such routes exist in this wrapper. Inherited producer/solver counters were not sampled.",
        "inherited_uninstrumented_counters": None,
        "native_implicit_authority": False, "automatic_retry": False, "installation_attempted": False}
    emit(dest / "NCP_RUN.json", final)
    print(json.dumps({"status": final["status"], "first_failure": final["first_failure"], "run_dir": str(dest)}))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
