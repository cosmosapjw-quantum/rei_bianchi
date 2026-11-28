"""Create-only dynamic MPI task scheduler; no physics tolerance changes."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import shutil
import subprocess
import sys
import tempfile
import time

TASK_TAG, RESULT_TAG, STOP_TAG = 10, 11, 12
SAFE_TASK_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,119}\Z")


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def atomic_create(path, data):
    """Link a fsynced temporary inode without replacing an existing target."""
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix=".pending-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        os.unlink(temporary)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def validate_manifest(document):
    if not isinstance(document, dict) or set(document) != {"schema", "tasks", "limits"} or type(document["schema"]) is not int or document["schema"] != 1:
        raise ValueError("manifest requires schema=1, tasks and limits only")
    tasks, limits = document["tasks"], document["limits"]
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("nonempty task list required")
    if not isinstance(limits, dict) or set(limits) != {"per_worker_memory_gib", "task_wall_seconds"}:
        raise ValueError("limits require per_worker_memory_gib and task_wall_seconds")
    for key, value in limits.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"{key} must be positive and finite")
    if int(limits["per_worker_memory_gib"] * 2**30) <= 0:
        raise ValueError("memory limit rounds below one byte")
    identities = set()
    for task in tasks:
        if not isinstance(task, dict) or set(task) != {"task_id", "parameters"}:
            raise ValueError("task requires task_id and parameters only")
        task_id = task["task_id"]
        if not isinstance(task_id, str) or not SAFE_TASK_ID.fullmatch(task_id) or task_id in (".", ".."):
            raise ValueError("task_id must be a safe unique ASCII basename")
        if task_id in identities:
            raise ValueError(f"duplicate task_id: {task_id}")
        identities.add(task_id)
        if not isinstance(task["parameters"], dict):
            raise ValueError("parameters must be an object")
        json_bytes(task)  # Reject NaN/Infinity in arbitrarily nested inputs.
    return document


def read_manifest(path):
    raw = Path(path).read_bytes()
    parsed = json.loads(raw, object_pairs_hook=_unique_object,
                        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"non-finite JSON {value}")))
    return validate_manifest(parsed), sha256(raw), raw


def code_identity(root=None):
    root = Path(root or Path(__file__).resolve().parents[1])
    identities = {}
    for directory in ("code", "reference", "fortran", "native"):
        base = root / directory
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts and (path.name == "Makefile" or path.suffix.lower() in {".py", ".f", ".f90", ".f95", ".so", ".toml", ".json"}):
                identities[path.relative_to(root).as_posix()] = sha256(path.read_bytes())
    if "code/task_worker.py" not in identities:
        raise RuntimeError("code/task_worker.py is missing")
    return {"files": identities, "sha256": sha256(json_bytes(identities))}


def backend_identity(backend):
    if backend in ("reference", "numpy"):
        return {"backend": backend}
    default = Path(__file__).resolve().parents[1] / "native" / "build" / "libbass_element.so"
    path = Path(os.environ.get("BASS_NATIVE_LIBRARY", str(default))).expanduser().resolve(strict=True)
    digest = sha256(path.read_bytes())
    expected = os.environ.get("BASS_NATIVE_EXPECTED_SHA256")
    if expected is not None and expected.lower() != digest:
        raise RuntimeError("BASS_NATIVE_EXPECTED_SHA256 mismatch")
    metadata_path = path.with_suffix(".build.json")
    if not metadata_path.is_file():
        raise RuntimeError("native backend requires the matching build manifest")
    raw = metadata_path.read_bytes()
    metadata = json.loads(raw, object_pairs_hook=_unique_object)
    if metadata.get("library_sha256") != digest:
        raise RuntimeError("native build manifest/library hash mismatch")
    return {"backend": backend, "library_path": str(path), "library_sha256": digest,
            "build_manifest_sha256": sha256(raw), "build": metadata}


def child_environment():
    env = os.environ.copy()
    omp_threads = env.get("OMP_NUM_THREADS", "1")
    if not omp_threads.isdecimal() or int(omp_threads) < 1:
        raise ValueError("OMP_NUM_THREADS must be a positive integer")
    env.update({"OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "BLIS_NUM_THREADS": "1",
                "VECLIB_MAXIMUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1",
                "OMP_NUM_THREADS": omp_threads, "OMP_DYNAMIC": "FALSE",
                "OMP_PLACES": "cores", "OMP_PROC_BIND": "close"})
    return env


def validate_worker_artifacts(result, task_dir, identity, selected_backend):
    expected_sources = {name: digest for name, digest in identity["files"].items()
                        if name.endswith(".py") and name.count("/") == 1
                        and name.split("/")[0] in ("code", "reference")}
    if result.get("code_sha256") != expected_sources:
        raise RuntimeError("WORKER_SOURCE_IDENTITY_MISMATCH")
    name = result.get("state_file")
    if not isinstance(name, str) or Path(name).name != name or name in (".", ".."):
        raise RuntimeError("INVALID_STATE_ARTIFACT_NAME")
    state = Path(task_dir) / name
    if state.is_symlink() or not state.is_file():
        raise RuntimeError("MISSING_OR_SYMLINK_STATE_ARTIFACT")
    if state.stat().st_size != result.get("state_bytes") or sha256(state.read_bytes()) != result.get("state_sha256"):
        raise RuntimeError("STATE_ARTIFACT_IDENTITY_MISMATCH")
    if selected_backend["backend"] == "native":
        native = result.get("metadata", {}).get("native_library", {})
        if native.get("library_sha256") != selected_backend["library_sha256"] or native.get("build") != selected_backend["build"]:
            raise RuntimeError("WORKER_NATIVE_IDENTITY_MISMATCH")


def execute_task(task, output_dir, backend, python, limits, identity, rank, worker_path=None, selected_backend=None):
    task_dir = Path(output_dir) / task["task_id"]
    task_dir.mkdir(exist_ok=False)
    task_path = task_dir / "TASK_INPUT.json"
    atomic_create(task_path, json_bytes(task))
    worker = Path(worker_path or Path(__file__).with_name("task_worker.py")).resolve()
    command = [python, str(Path(__file__).with_name("host_probe.py").resolve()),
               "--memory-limit-bytes", str(int(limits["per_worker_memory_gib"] * 2**30)), "--",
               python, str(worker), "--task-json", str(task_path.resolve()),
               "--output-dir", str(task_dir.resolve()), "--backend", backend]
    record = {"schema": 1, "task_id": task["task_id"], "task_sha256": sha256(json_bytes(task)),
              "backend": backend, "code_sha256": identity["sha256"], "rank": rank,
              "command": command, "limits": limits, "status": "FAILED", "resume": "DISABLED_CREATE_ONLY"}
    started = time.monotonic()
    process = None
    try:
        selected_backend = selected_backend or backend_identity(backend)
        if code_identity() != identity or backend_identity(backend) != selected_backend:
            raise RuntimeError("CODE_OR_BACKEND_CHANGED_BEFORE_TASK")
        env = child_environment()
        if backend == "native":
            env["BASS_NATIVE_LIBRARY"] = selected_backend["library_path"]
            env["BASS_NATIVE_EXPECTED_SHA256"] = selected_backend["library_sha256"]
        record["selected_backend"] = selected_backend
        record["thread_environment"] = {k: env[k] for k in ("OMP_NUM_THREADS", "OMP_PLACES", "OMP_PROC_BIND", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_DYNAMIC")}
        with (task_dir / "STDOUT.txt").open("xb") as stdout, (task_dir / "STDERR.txt").open("xb") as stderr:
            process = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env, start_new_session=True)
            try:
                record["returncode"] = process.wait(timeout=limits["task_wall_seconds"])
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                record["returncode"] = process.wait()
                record["failure_class"] = "TASK_WALL_TIMEOUT"
            stdout.flush()
            stderr.flush()
            os.fsync(stdout.fileno())
            os.fsync(stderr.fileno())
        if "failure_class" not in record:
            if record["returncode"] == 0:
                result_path = task_dir / "RESULT.json"
                if not result_path.is_file():
                    record["failure_class"] = "MISSING_WORKER_RESULT"
                else:
                    result = json.loads(result_path.read_bytes(), object_pairs_hook=_unique_object)
                    if not isinstance(result, dict) or result.get("status") != "PASS":
                        record["failure_class"] = "WORKER_RESULT_NOT_PASS"
                    else:
                        expected_input = sha256(task_path.read_bytes())
                        if (result.get("task_id") != task["task_id"] or result.get("backend") != backend
                                or result.get("input_sha256") != expected_input
                                or result.get("parameters") != task["parameters"]):
                            record["failure_class"] = "WORKER_RESULT_IDENTITY_MISMATCH"
                        else:
                            validate_worker_artifacts(result, task_dir, identity, selected_backend)
                            if code_identity() != identity or backend_identity(backend) != selected_backend:
                                raise RuntimeError("CODE_OR_BACKEND_CHANGED_DURING_TASK")
                            record["status"] = "WORKER_RESULT_PASS"
                            record["worker_result_sha256"] = sha256(result_path.read_bytes())
            else:
                record["failure_class"] = "WORKER_NONZERO_EXIT"
    except Exception as error:
        if process is not None and process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        record["failure_class"] = "EXECUTION_BOUNDARY_EXCEPTION"
        record["error"] = f"{type(error).__name__}: {error}"
    record["wall_seconds"] = time.monotonic() - started
    record["artifacts"] = {p.name: {"bytes": p.stat().st_size, "sha256": sha256(p.read_bytes())}
                           for p in sorted(task_dir.iterdir()) if p.is_file()}
    atomic_create(task_dir / "TASK_EXECUTION.json", json_bytes(record))
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--backend", choices=("native", "numpy", "reference"), required=True)
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args(argv)
    resolved_python = shutil.which(args.python)
    if resolved_python is None:
        raise RuntimeError("requested Python executable not found")
    args.python = str(Path(resolved_python).resolve())
    try:
        from mpi4py import MPI
    except ImportError as error:
        raise RuntimeError("mpi4py linked to OpenMPI is required; no silent serial fallback") from error
    comm = MPI.COMM_WORLD
    rank, size = comm.Get_rank(), comm.Get_size()
    try:
        mpi_version = MPI.Get_library_version()
        if "Open MPI" not in mpi_version and "OpenMPI" not in mpi_version:
            raise RuntimeError("OpenMPI-linked mpi4py required")
        identity = code_identity()
        selected_backend = backend_identity(args.backend)
        manifest, manifest_sha, raw = read_manifest(args.manifest)
        local = {"ok": True, "code_sha256": identity["sha256"], "manifest_sha256": manifest_sha,
                 "backend": args.backend, "python": str(Path(args.python).resolve()), "mpi": mpi_version,
                 "output_dir": str(Path(args.output_dir).resolve()),
                 "selected_backend": selected_backend,
                 "threads": {key: value for key, value in child_environment().items()
                             if key.startswith("OMP_") or key in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "BLIS_NUM_THREADS")}}
    except Exception as error:
        local = {"ok": False, "error": f"{type(error).__name__}: {error}"}
    identities = comm.allgather(local)
    if not all(x == identities[0] and x["ok"] for x in identities):
        if rank == 0:
            print(json.dumps({"status": "IDENTITY_OR_PREFLIGHT_FAILED", "ranks": identities}), file=sys.stderr)
        return 2
    setup = None
    if rank == 0:
        try:
            out = Path(args.output_dir).resolve()
            out.mkdir(parents=True, exist_ok=False)
            atomic_create(out / "MANIFEST_INPUT.json", raw)
            atomic_create(out / "RUN_IDENTITY.json", json_bytes({"schema": 1, "rank_count": size,
                          "worker_count": size - 1 if size > 1 else 1, "manifest_sha256": manifest_sha,
                          "backend": args.backend, "code": identity, "rank_consensus": identities,
                          "selected_backend": selected_backend,
                          "order": "MANIFEST_ORDER_IN_SUMMARY_DYNAMIC_EXECUTION_ORDER", "resume": "DISABLED_CREATE_ONLY"}))
            setup = {"ok": True, "output_dir": str(out)}
        except Exception as error:
            setup = {"ok": False, "error": f"{type(error).__name__}: {error}"}
    setup = comm.bcast(setup, root=0)
    if not setup["ok"]:
        if rank == 0:
            print(json.dumps(setup), file=sys.stderr)
        return 2
    tasks = manifest["tasks"]
    started = time.monotonic()

    def run(task):
        try:
            return execute_task(task, setup["output_dir"], args.backend, args.python, manifest["limits"], identity, rank,
                                selected_backend=selected_backend)
        except Exception as error:
            # A worker failure must reach the manager instead of deadlocking it.
            return {"task_id": task["task_id"], "rank": rank, "status": "FAILED",
                    "failure_class": "TASK_ENVELOPE_EXCEPTION", "error": f"{type(error).__name__}: {error}"}

    if size == 1:
        results = {task["task_id"]: run(task) for task in tasks}
    elif rank == 0:
        results, next_index, active = {}, 0, 0
        for worker in range(1, size):
            if next_index < len(tasks):
                comm.send(tasks[next_index], dest=worker, tag=TASK_TAG)
                next_index += 1
                active += 1
            else:
                comm.send(None, dest=worker, tag=STOP_TAG)
        while active:
            status = MPI.Status()
            result = comm.recv(source=MPI.ANY_SOURCE, tag=RESULT_TAG, status=status)
            worker = status.Get_source()
            results[result["task_id"]] = result
            if next_index < len(tasks):
                comm.send(tasks[next_index], dest=worker, tag=TASK_TAG)
                next_index += 1
            else:
                comm.send(None, dest=worker, tag=STOP_TAG)
                active -= 1
    else:
        while True:
            status = MPI.Status()
            task = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
            if status.Get_tag() == STOP_TAG:
                break
            comm.send(run(task), dest=0, tag=RESULT_TAG)
    exit_code = None
    if rank == 0:
        ordered = [results[task["task_id"]] for task in tasks]
        passed = all(r["status"] == "WORKER_RESULT_PASS" for r in ordered)
        summary = {"schema": 1, "status": "ALL_WORKER_RESULTS_PASS" if passed else "TASK_FAILURES_PRESERVED",
                   "scientific_acceptance": "NOT_INFERRED_FROM_PROCESS_EXIT", "rank_count": size,
                   "worker_count": size - 1 if size > 1 else 1, "wall_seconds": time.monotonic() - started,
                   "manifest_sha256": manifest_sha, "code_sha256": identity["sha256"], "tasks": ordered}
        try:
            atomic_create(Path(setup["output_dir"]) / "BATCH_SUMMARY.json", json_bytes(summary))
            print(json.dumps({"status": summary["status"], "tasks": len(tasks), "output_dir": setup["output_dir"]}))
            exit_code = 0 if passed else 1
        except Exception as error:
            print(json.dumps({"status": "SUMMARY_WRITE_FAILED", "error": f"{type(error).__name__}: {error}"}), file=sys.stderr)
            exit_code = 2
    return comm.bcast(exit_code, root=0)


if __name__ == "__main__":
    raise SystemExit(main())
