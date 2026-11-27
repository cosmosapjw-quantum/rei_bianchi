"""Linux direct-process lifetime boundary; frozen numerical driver is unchanged.

Each launch is exec-only through a checked PDEATHSIG launcher. Native processes
add a seccomp creation-syscall prohibition. This is not MPI or a cgroup sandbox.
The dispatcher and workers must be single-threaded at spawn (no preexec_fn).
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import tempfile
import threading
import time

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
MAX_JSON = 16 * 1024 * 1024
FLAGS = ["-std=c11", "-O2", "-Wall", "-Wextra", "-Werror"]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def sources():
    files = {name: digest((HERE / name).read_bytes()) for name in ("host.py", "guarded_exec.c")}
    return {"files": files, "sha256": digest(canonical(files))}


def _read_json(path):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError("duplicate JSON key")
            value[key] = item
        return value
    return json.loads(Path(path).read_bytes(), object_pairs_hook=pairs)


def build():
    BUILD.mkdir(exist_ok=False)
    compiler = Path("/usr/bin/gcc").resolve(strict=True)
    command = [str(compiler), *FLAGS, str(HERE / "guarded_exec.c"), "-o", str(BUILD / "guarded_exec")]
    compiled = subprocess.run(command, capture_output=True, text=True, timeout=30)
    if compiled.returncode:
        raise ValueError("host launcher compile failed: " + compiled.stderr)
    body = {"schema": "WU088_PROCESS_HOST_BUILD_V1", "source": sources(),
            "compiler": str(compiler), "compiler_sha256": digest(compiler.read_bytes()),
            "compiler_version": subprocess.check_output([str(compiler), "--version"], text=True).splitlines()[0],
            "command": command, "flags": FLAGS, "machine": platform.machine(),
            "launcher_sha256": digest((BUILD / "guarded_exec").read_bytes()),
            "native_kernel_recompiled": False, "mpi_execution": False}
    body["manifest_sha256"] = digest(canonical(body))
    with (BUILD / "BUILD.json").open("x") as stream:
        json.dump(body, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return identity()


def identity():
    manifest = _read_json(BUILD / "BUILD.json")
    body = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    if manifest.get("schema") != "WU088_PROCESS_HOST_BUILD_V1" or digest(canonical(body)) != manifest.get("manifest_sha256"):
        raise ValueError("process host build manifest mismatch")
    if manifest.get("source") != sources() or manifest.get("flags") != FLAGS:
        raise ValueError("process host source changed since build")
    if digest((BUILD / "guarded_exec").read_bytes()) != manifest.get("launcher_sha256"):
        raise ValueError("process host launcher changed")
    return {"schema": "WU088_PROCESS_HOST_IDENTITY_V1", "source": sources(),
            "build_manifest_sha256": manifest["manifest_sha256"],
            "launcher_sha256": manifest["launcher_sha256"]}


def _single_thread():
    if threading.current_thread() is not threading.main_thread() or threading.active_count() != 1:
        raise ValueError("process host launch requires the single main Python thread")


def _launch(command, *, stdout, stderr, env, memory_mib, cpu_seconds, nofork):
    _single_thread()
    authority = identity()
    if not isinstance(command, list) or not command or not all(type(item) is str for item in command):
        raise ValueError("explicit argv list required")
    if not Path(command[0]).is_absolute():
        raise ValueError("absolute executable required")
    if type(memory_mib) is not int or not 16 <= memory_mib <= 1536:
        raise ValueError("host memory cap outside 16..1536 MiB")
    if type(cpu_seconds) is not int or not 1 <= cpu_seconds <= 180:
        raise ValueError("host CPU cap outside 1..180 seconds")
    launcher = [str(BUILD / "guarded_exec"), str(os.getpid()), str(memory_mib * 1024 * 1024),
                str(MAX_JSON), str(cpu_seconds), "1" if nofork else "0", "0", "--", *command]
    process = subprocess.Popen(launcher, stdout=stdout, stderr=stderr, env=env,
                               start_new_session=True, close_fds=True)
    process.wu088_host_identity = authority
    return process


def spawn_guarded(command, *, stdout=None, stderr=None, env=None, memory_mib=1024):
    """Spawn one Python worker; caller must wait/kill at its 180-second wall cap."""
    return _launch(command, stdout=stdout, stderr=stderr, env=env, memory_mib=memory_mib,
                   cpu_seconds=180, nofork=False)


def _sidecars(out):
    path = Path(out).resolve()
    return Path(str(path) + ".stdout"), Path(str(path) + ".stderr")


def validate_receipt(record, *, command, limits, output_path):
    expected_keys = {"schema", "identity", "executor_override", "process_model", "pdeath_signal",
                     "parent_pid_race_checked", "native_descendant_creation", "native_process_pid",
                     "wall_cap_seconds", "cpu_cap_seconds", "memory_mib", "file_bytes",
                     "native_command_sha256", "stdout", "stderr", "native_wait_completed", "timed_out",
                     "mpi_execution", "cgroup_containment", "native_execution_evidence"}
    if type(record) is not dict or set(record) != expected_keys:
        raise ValueError("process host receipt schema mismatch")
    expected = {"schema": "WU088_PROCESS_HOST_EXECUTION_V1", "identity": identity(),
                "executor_override": "execute_bound_native_ONLY_FROZEN_RUN_TASK_VALIDATION_RETAINED",
                "process_model": "DIRECT_EXEC_SINGLE_NATIVE_PROCESS",
                "pdeath_signal": "SIGKILL", "parent_pid_race_checked": True,
                "native_descendant_creation": "SECCOMP_DENY_FORK_VFORK_CLONE_CLONE3",
                "wall_cap_seconds": limits["wall_seconds"] + 5,
                "cpu_cap_seconds": limits["wall_seconds"] + 5,
                "memory_mib": limits["memory_mib"], "file_bytes": MAX_JSON,
                "native_command_sha256": digest(canonical(command)),
                "native_wait_completed": True, "mpi_execution": False, "cgroup_containment": False}
    for key, value in expected.items():
        if type(record[key]) is not type(value) or record[key] != value:
            raise ValueError("process host receipt mismatch: " + key)
    if type(record["native_process_pid"]) is not int or record["native_process_pid"] <= 0 or type(record["timed_out"]) is not bool:
        raise ValueError("process host PID/timeout mismatch")
    if record["native_execution_evidence"] not in ("SOURCE_BOUND_NATIVE_STDOUT", "NO_NATIVE_STDOUT_ATTESTATION"):
        raise ValueError("process host native execution evidence mismatch")
    for kind, path in zip(("stdout", "stderr"), _sidecars(output_path)):
        sidecar = record[kind]
        if type(sidecar) is not dict or set(sidecar) != {"path", "sha256", "size"} or sidecar["path"] != str(path):
            raise ValueError("process host sidecar path mismatch")
        if not path.is_file() or path.stat().st_size > MAX_JSON:
            raise ValueError("process host bounded sidecar missing")
        data = path.read_bytes()
        if type(sidecar["size"]) is not int or sidecar["size"] != len(data) or sidecar["sha256"] != digest(data):
            raise ValueError("process host sidecar bytes changed")
    return record


def install(driver):
    """Explicitly substitute this audited host executor, keeping native math frozen."""
    authority = identity()

    def execute(command, env, limits, binding, out, plan, task, manifest):
        if identity() != authority:
            raise driver.DriverError("host changed after install")
        output_paths = _sidecars(out)
        if any(os.path.lexists(path) for path in output_paths):
            raise driver.DriverError("raw native sidecar exists; no rerun")
        timed_out = False
        host_record = {"schema": "WU088_PROCESS_HOST_EXECUTION_V1", "identity": authority,
                       "executor_override": "execute_bound_native_ONLY_FROZEN_RUN_TASK_VALIDATION_RETAINED",
                       "process_model": "DIRECT_EXEC_SINGLE_NATIVE_PROCESS", "pdeath_signal": "SIGKILL",
                       "parent_pid_race_checked": True,
                       "native_descendant_creation": "SECCOMP_DENY_FORK_VFORK_CLONE_CLONE3",
                       "wall_cap_seconds": limits["wall_seconds"] + 5,
                       "cpu_cap_seconds": limits["wall_seconds"] + 5,
                       "memory_mib": limits["memory_mib"], "file_bytes": MAX_JSON,
                       "native_command_sha256": digest(canonical(command)),
                       "mpi_execution": False, "cgroup_containment": False}
        with tempfile.TemporaryDirectory(prefix="wu088-guarded-native-") as temporary:
            with (Path(temporary) / "stdout").open("w+b") as so, (Path(temporary) / "stderr").open("w+b") as se:
                started = time.monotonic_ns()
                process = None
                try:
                    process = _launch(command, stdout=so, stderr=se, env=env,
                                      memory_mib=limits["memory_mib"], cpu_seconds=limits["wall_seconds"] + 5,
                                      nofork=True)
                    # A Popen PID initially identifies the launcher, not yet the
                    # HH executable. Source-bound native output attests below.
                    binding["native_execution_observed"] = False
                    host_record["native_process_pid"] = process.pid
                    try:
                        code = process.wait(timeout=limits["wall_seconds"] + 5)
                    except subprocess.TimeoutExpired:
                        timed_out = True
                        process.kill()
                        code = process.wait()
                except BaseException:
                    if process is not None and process.poll() is None:
                        process.kill()
                        process.wait()
                    raise
                finally:
                    binding["elapsed_wall_ns"] = time.monotonic_ns() - started
                binding["returncode"] = code
                so.seek(0); payload = so.read(MAX_JSON + 1)
                se.seek(0); stderr = se.read(MAX_JSON + 1)
        if len(payload) > MAX_JSON or len(stderr) > MAX_JSON:
            raise driver.DriverError("native output exceeded host file cap")
        for kind, path, data in zip(("stdout", "stderr"), output_paths, (payload, stderr)):
            with path.open("xb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            host_record[kind] = {"path": str(path), "sha256": digest(data), "size": len(data)}
        host_record["native_wait_completed"] = True
        host_record["timed_out"] = timed_out
        observed = False
        try:
            native = driver.parse_json(payload)
            observed = (type(native) is dict and
                        native.get("schema") == "WU088_LOG2_RANGE_INTERIOR_RESULT_V1" and
                        native.get("index") == task["index"] and
                        native.get("task_sha256") == task["task_sha256"] and
                        native.get("plan_sha256") == plan["plan_sha256"] and
                        native.get("archive_sha256") == manifest["archive_sha256"] and
                        native.get("input_record_sha256") == manifest["input_record_sha256"] and
                        native.get("build_source_sha256") == manifest["source"]["sha256"])
        except (ValueError, TypeError, KeyError):
            pass
        binding["native_execution_observed"] = observed
        host_record["native_execution_evidence"] = "SOURCE_BOUND_NATIVE_STDOUT" if observed else "NO_NATIVE_STDOUT_ATTESTATION"
        binding["process_host"] = host_record
        binding["native_stdout_sha256"] = digest(payload)
        binding["native_stderr_sha256"] = digest(stderr)
        failure = "EXTERNAL_WALL_CAP" if timed_out else ("NONZERO_NATIVE_EXIT" if code else None)
        if not failure:
            try:
                result = driver.validate_result(driver.parse_json(payload), plan=plan, task=task,
                                                manifest=manifest, limits=limits)
            except (ValueError, TypeError, KeyError) as exc:
                failure = "INVALID_NATIVE_OUTPUT"
                binding["validation_error"] = str(exc)
        if failure:
            rejection = {"schema": "WU088_LOG2_NATIVE_INTERIOR_REJECTION_V1", "reason": failure,
                         "returncode": code, "index": task["index"], "plan_sha256": plan["plan_sha256"],
                         "task_sha256": task["task_sha256"],
                         "native_stdout": payload.decode("utf-8", "replace"),
                         "native_stderr": stderr.decode("utf-8", "replace"), "wrapper": binding,
                         "accepted": False, "scientific_admission": False, "production_admission": False}
            rejection["result_sha256"] = digest(canonical(rejection))
            driver.write_new(out, rejection)
            raise driver.DriverError("NATIVE_REJECTED " + failure + " exit " + str(code))
        result["wrapper"] = binding
        result["result_sha256"] = digest(canonical(result))
        driver.write_new(out, result)
        return result

    driver.execute_bound_native = execute
    return authority


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "identity"))
    args = parser.parse_args()
    print(json.dumps(build() if args.action == "build" else identity(), indent=2, sort_keys=True))
