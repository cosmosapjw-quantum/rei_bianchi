#!/usr/bin/env python3
"""Worker entry point. Use launch_manufactured.py for bounded execution."""
from __future__ import annotations
import argparse
import importlib
import json
import os
from pathlib import Path
import socket
import sys
import time
import traceback

from runtime_support import (ContractError, atomic_create, code_identity, file_identity,
    host_preflight, load_manifest, sha256_file, validate_request, verify_thread_environment)


def _error(exc):
    return {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}


def run_assigned(cases, rank, size, callback, backend, native_library):
    """Rank-strided ownership; summaries only. Exceptions remain explicit failures."""
    summaries = []
    for index in range(rank, len(cases), size):
        case = cases[index]
        started = time.monotonic()
        row = {"case_index": index, "case_id": case["case_id"], "rank": rank}
        try:
            result = callback(case, backend=backend, native_library=native_library)
            encoded = json.dumps(result, allow_nan=False, sort_keys=True).encode()
            if len(encoded) > 65536:
                raise ContractError("callback result exceeds 64KiB summary-only budget")
            row.update({"status": "PASS", "result": result})
        except Exception as exc:
            row.update({"status": "FAIL", "error": _error(exc)})
        row["wall_seconds"] = time.monotonic() - started
        summaries.append(row)
    return summaries


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", required=True)
    parser.add_argument("--context-sha256", required=True)
    parser.add_argument("--execution", required=True, choices=("serial", "mpi"))
    parser.add_argument("--backend", required=True, choices=("reference", "native"))
    parser.add_argument("--native-library")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    rank, size, comm, mpi_version = 0, 1, None, None
    try:
        if args.execution == "mpi":
            import mpi4py
            mpi4py.rc.thread_level = "funneled"
            from mpi4py import MPI
            comm = MPI.COMM_WORLD
            rank, size = comm.Get_rank(), comm.Get_size()
            mpi_version = MPI.Get_library_version().strip()
            if not mpi_version.startswith("Open MPI"):
                raise ContractError("MPI runtime is not Open MPI; no fallback")
            if MPI.Query_thread() < MPI.THREAD_FUNNELED:
                raise ContractError("MPI thread support below THREAD_FUNNELED")
        elif any(int(os.environ.get(name, "1")) > 1 for name in ("OMPI_COMM_WORLD_SIZE", "PMI_SIZE", "PMIX_SIZE")):
            raise ContractError("serial execution nested inside multi-rank MPI is forbidden")
    except Exception as exc:
        # mpi4py import can fail before rank is known; Open MPI exports rank.
        if int(os.environ.get("OMPI_COMM_WORLD_RANK", "0")) == 0:
            atomic_create(args.output, {"status": "FAIL", "stage": "MPI_INITIALIZATION", "error": _error(exc), "physical_launch_enabled": False})
        return 1

    started = time.monotonic()
    context, manifest, callback, local_error = None, None, None, None
    worker = {"rank": rank, "size": size, "hostname": socket.gethostname(), "mpi_library_version": mpi_version,
              "pid": os.getpid(), "pgid": os.getpgrp(), "sid": os.getsid(0)}
    try:
        if sha256_file(args.context) != args.context_sha256:
            raise ContractError("launch context SHA256 mismatch")
        context = json.loads(Path(args.context).read_text())
        if context["schema"] != "bass-he.c2f.launch-context.v1":
            raise ContractError("invalid launch context schema")
        launch = context["launch"]
        if args.execution != launch["execution"] or args.backend != launch["backend"] or args.native_library != launch["native_library"]:
            raise ContractError("worker CLI differs from pinned launch context")
        if str(Path(args.output).resolve()) != context["worker_output"]:
            raise ContractError("worker output differs from launch context")
        manifest = load_manifest(context["manifest"]["path"])
        if file_identity(context["manifest"]["path"]) != context["manifest"]:
            raise ContractError("manifest identity mismatch")
        actual_code = code_identity(Path(__file__).parent)
        if actual_code != context["code"]:
            raise ContractError("code identity mismatch")
        native_identity = file_identity(args.native_library) if args.native_library else None
        if native_identity != context["native_library_identity"]:
            raise ContractError("native library identity mismatch")
        if size != launch["ranks"]:
            raise ContractError("actual MPI size differs from requested ranks")
        validate_request(manifest, args.execution, args.backend, args.native_library,
                         launch["ranks"], launch["threads"], launch["binding"], context["host_preflight"])
        worker["thread_environment"] = verify_thread_environment(launch["threads"], launch["binding"])
        observed = host_preflight()
        worker["host_preflight"] = observed
        affinity = set(observed["affinity_cpus"])
        if not affinity.issubset(context["host_preflight"]["affinity_cpus"]):
            raise ContractError("worker affinity escaped parent pre-MPI affinity")
        if len(affinity) < launch["threads"]:
            raise ContractError("worker affinity is narrower than requested threads")
        if launch["binding"] == "core" and len(observed["physical_cores_in_affinity"]) < launch["threads"]:
            raise ContractError("worker binding lacks requested physical core count")
        if observed["hostname"] != context["host_preflight"]["hostname"]:
            raise ContractError("worker is not on captured single host")
        worker["identity"] = {"manifest_sha256": context["manifest"]["sha256"],
                              "code_sha256": {k: v["sha256"] for k, v in actual_code.items()},
                              "native_sha256": native_identity["sha256"] if native_identity else None,
                              "context_sha256": args.context_sha256}
        callback = importlib.import_module("manufactured_cases").run_case
    except Exception as exc:
        local_error = _error(exc)
    worker["preflight_error"] = local_error
    workers = comm.allgather(worker) if comm else [worker]
    preflight_errors = [w for w in workers if w["preflight_error"] is not None]
    if not preflight_errors:
        baseline = workers[0]["identity"]
        if any(w["identity"] != baseline for w in workers):
            preflight_errors.append({"stage": "CROSS_RANK_IDENTITY", "message": "rank input/code/native identities differ"})
        if context["launch"]["binding"] == "core":
            occupied = set()
            for w in workers:
                affinity = set(w["host_preflight"]["affinity_cpus"])
                if occupied & affinity:
                    preflight_errors.append({"stage": "CORE_BINDING", "message": "rank CPU affinities overlap"})
                occupied |= affinity
    if preflight_errors:
        if rank == 0:
            atomic_create(args.output, {"schema": "bass-he.c2f.worker-result.v1", "status": "FAIL", "stage": "PREFLIGHT",
                         "workers": workers, "errors": preflight_errors, "physical_launch_enabled": False})
        return 1

    local_results = run_assigned(manifest["cases"], rank, size, callback, args.backend, args.native_library)
    post_error = None
    try:
        if code_identity(Path(__file__).parent) != context["code"] or file_identity(context["manifest"]["path"]) != context["manifest"]:
            raise ContractError("code or manifest changed during execution")
        if (file_identity(args.native_library) if args.native_library else None) != context["native_library_identity"]:
            raise ContractError("native library changed during execution")
    except Exception as exc:
        post_error = _error(exc)
    gathered = comm.gather({"rank": rank, "results": local_results, "post_identity_error": post_error}, root=0) if comm else [{"rank": rank, "results": local_results, "post_identity_error": post_error}]
    status = "PASS"
    if rank == 0:
        results = sorted((row for batch in gathered for row in batch["results"]), key=lambda row: row["case_index"])
        if [row["case_index"] for row in results] != list(range(len(manifest["cases"]))) or any(row["rank"] != row["case_index"] % size for row in results):
            status = "FAIL"
        if any(row["status"] != "PASS" for row in results) or any(batch["post_identity_error"] for batch in gathered):
            status = "FAIL"
        atomic_create(args.output, {"schema": "bass-he.c2f.worker-result.v1", "status": status,
                     "physical_launch_enabled": False, "execution": args.execution, "backend": args.backend,
                     "workers": workers, "results": results,
                     "post_identity_errors": [b for b in gathered if b["post_identity_error"]],
                     "task_ownership": "case_index % mpi_size", "gather_policy": "summaries_only",
                     "wall_seconds": time.monotonic()-started,
                     "evidence_scope": "manufactured_implementation_only"})
    if comm:
        status = comm.bcast(status, root=0)
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
