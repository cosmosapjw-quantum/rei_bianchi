#!/usr/bin/env python3
"""C2g physical-sector worker; only launch_reference.py supplies reviewed input."""
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

from physical_contract import (SCOPE, SOLVER_KEYS, approved_inputs, native_identity,
                               source_identity, validate_registered_layout, validate_request)
from runtime_support import (ContractError, atomic_create, file_identity,
                             host_preflight, sha256_file, verify_thread_environment)


def _error(exc):
    return {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}


def physical_callback(task, *, backend, archive_path):
    """Resolve real provider at invocation; no import-time physical solve."""
    solver = importlib.import_module("optimized_solver")
    provider = importlib.import_module("multistate_provider")
    result = solver.solve_many(**{key: task[key] for key in SOLVER_KEYS}, backend=backend)
    archive = provider.save_sector(result, archive_path, source_id=task["task_id"])
    return {"archive": archive,
            "state_count": len(result.states),
            "energies": [float(state.energy) for state in result.states],
            "algebraic_residuals": [float(state.residual) for state in result.states],
            "actual_radial_elements": len(task["boundaries"]) - 1,
            "coefficient_shape": list(result.coefficient_vectors.shape),
            "projected_operator": result.projected_operator.tolist(),
            "mass_gram": result.mass_gram.tolist(),
            "certificate_scope": "finite_generalized_matrix_only_no_PDE_or_continuum_certificate"}


def run_assigned(tasks, rank, size, callback, backend, task_directory, input_identity):
    """Exactly one rank owns each index. Every attempted task gets a durable receipt."""
    summaries = []
    for index in range(rank, len(tasks), size):
        task = tasks[index]
        started = time.monotonic()
        archive_path = Path(task_directory) / (task["task_id"] + ".npz")
        receipt_path = Path(task_directory) / (task["task_id"] + ".json")
        row = {"schema": "bass-he.c2g.physical-task-receipt.v1", "task_index": index,
               "task_id": task["task_id"], "rank": rank, "task": task,
               "backend": backend, "input_identity": input_identity}
        try:
            if archive_path.exists() or receipt_path.exists():
                raise FileExistsError("create-only task artifact already exists")
            result = callback(task, backend=backend, archive_path=archive_path)
            encoded = json.dumps(result, allow_nan=False, sort_keys=True).encode()
            if len(encoded) > 65536:
                raise ContractError("callback result exceeds the 64KiB summary-only budget")
            if result["state_count"] != task["nroots"]:
                raise ContractError("provider returned a different number of eigenstates")
            measured = file_identity(archive_path)
            archive = result["archive"]
            if (archive["source_id"] != task["task_id"] or
                    archive["source_sha256"] != measured["sha256"] or
                    archive["source_bytes"] != measured["bytes"] or
                    str(Path(archive["source_path"]).resolve()) != str(archive_path.resolve())):
                raise ContractError("saved archive identity differs from provider receipt")
            row.update({"status": "PASS", "result": result})
        except Exception as exc:
            row.update({"status": "FAIL", "error": _error(exc)})
            if archive_path.is_file():
                row["partial_archive"] = file_identity(archive_path)
        row["wall_seconds"] = time.monotonic() - started
        try:
            atomic_create(receipt_path, row)
            row["receipt"] = file_identity(receipt_path)
        except Exception as exc:
            # In particular preserve an already existing receipt without overwrite.
            row["status"] = "FAIL"
            row["receipt_error"] = _error(exc)
        summaries.append(row)
    return summaries


def verify_identities(context):
    inputs = context["inputs"]
    for identity in inputs.values():
        if file_identity(identity["path"]) != identity:
            raise ContractError("reviewed input changed during execution")
    if source_identity(Path(__file__).parent) != context["source"]:
        raise ContractError("source identity mismatch")
    if native_identity(context["launch"]["native_library"]) != context["native_identity"]:
        raise ContractError("native library/build metadata identity mismatch")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", required=True)
    parser.add_argument("--context-sha256", required=True)
    parser.add_argument("--execution", required=True, choices=("serial", "mpi"))
    parser.add_argument("--backend", required=True, choices=("numpy", "native"))
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
                raise ContractError("MPI support below THREAD_FUNNELED")
        elif any(int(os.environ.get(name, "1")) > 1 for name in ("OMPI_COMM_WORLD_SIZE", "PMI_SIZE", "PMIX_SIZE")):
            raise ContractError("serial execution nested inside multi-rank MPI is forbidden")
    except Exception as exc:
        if int(os.environ.get("OMPI_COMM_WORLD_RANK", "0")) == 0:
            atomic_create(args.output, {"status": "FAIL", "stage": "MPI_INITIALIZATION", "error": _error(exc)})
        return 1

    started = time.monotonic()
    context, manifest, local_error = None, None, None
    worker = {"rank": rank, "size": size, "hostname": socket.gethostname(),
              "mpi_library_version": mpi_version, "pid": os.getpid(),
              "pgid": os.getpgrp(), "sid": os.getsid(0)}
    try:
        if sha256_file(args.context) != args.context_sha256:
            raise ContractError("launch context SHA256 mismatch")
        context = json.loads(Path(args.context).read_text())
        if context["schema"] != "bass-he.c2g.physical-launch-context.v1":
            raise ContractError("invalid physical launch context schema")
        launch = context["launch"]
        if (args.execution != launch["execution"] or args.backend != launch["backend"] or
                args.native_library != launch["native_library"]):
            raise ContractError("worker CLI differs from pinned launch context")
        if str(Path(args.output).resolve()) != context["worker_output"]:
            raise ContractError("worker output differs from pinned launch context")
        manifest, inputs, _ = approved_inputs(context["inputs"]["manifest"]["path"],
                                               context["inputs"]["review"]["path"])
        if inputs != context["inputs"]:
            raise ContractError("reviewed inputs differ from pinned context")
        verify_identities(context)
        if size != launch["ranks"]:
            raise ContractError("actual MPI size differs from requested ranks")
        validate_request(manifest, args.execution, args.backend, args.native_library,
                         launch["ranks"], launch["threads"], launch["binding"], context["host_preflight"])
        if validate_registered_layout(inputs["preregistration"]["path"], args.execution, args.backend,
                                      launch["ranks"], launch["threads"], launch["binding"]) != launch["layout_id"]:
            raise ContractError("worker layout differs from preregistered campaign identity")
        worker["thread_environment"] = verify_thread_environment(launch["threads"], launch["binding"])
        if args.backend == "native":
            if (os.environ.get("BASS_NATIVE_LIBRARY") != args.native_library or
                    os.environ.get("BASS_NATIVE_EXPECTED_SHA256") != context["native_identity"]["library"]["sha256"]):
                raise ContractError("native environment differs from explicit pinned library")
        elif "BASS_NATIVE_LIBRARY" in os.environ or "BASS_NATIVE_EXPECTED_SHA256" in os.environ:
            raise ContractError("numpy worker received a native library environment")
        observed = host_preflight()
        worker["host_preflight"] = observed
        affinity = set(observed["affinity_cpus"])
        if not affinity.issubset(context["host_preflight"]["affinity_cpus"]):
            raise ContractError("worker affinity escaped the parent pre-MPI affinity")
        if len(affinity) < launch["threads"]:
            raise ContractError("worker affinity narrower than requested threads")
        if launch["binding"] == "core" and len(observed["physical_cores_in_affinity"]) < launch["threads"]:
            raise ContractError("worker binding lacks requested physical cores")
        if observed["hostname"] != context["host_preflight"]["hostname"]:
            raise ContractError("worker is not on the captured single host")
        worker["identity"] = {
            "inputs": {k: v["sha256"] for k, v in inputs.items()},
            "source": {k: v["sha256"] for k, v in context["source"].items()},
            "native": context["native_identity"], "context_sha256": args.context_sha256}
        # Resolve providers before collective preflight; a missing module produces
        # a failure on every rank without entering any eigensolve.
        solver = importlib.import_module("optimized_solver")
        provider = importlib.import_module("multistate_provider")
        if not callable(getattr(solver, "solve_many", None)) or not callable(getattr(provider, "save_sector", None)):
            raise ContractError("multistate provider API is missing")
    except Exception as exc:
        local_error = _error(exc)
    worker["preflight_error"] = local_error
    workers = comm.allgather(worker) if comm else [worker]
    preflight_errors = [w for w in workers if w["preflight_error"] is not None]
    if not preflight_errors:
        if any(w["identity"] != workers[0]["identity"] for w in workers):
            preflight_errors.append({"stage": "CROSS_RANK_IDENTITY", "message": "rank identities differ"})
        if context["launch"]["binding"] == "core":
            occupied = set()
            for w in workers:
                affinity = set(w["host_preflight"]["affinity_cpus"])
                if occupied & affinity:
                    preflight_errors.append({"stage": "CORE_BINDING", "message": "rank affinities overlap"})
                occupied |= affinity
    if preflight_errors:
        if rank == 0:
            atomic_create(args.output, {"schema": "bass-he.c2g.physical-worker-result.v1", "status": "FAIL",
                         "stage": "PREFLIGHT", "workers": workers, "errors": preflight_errors,
                         "evidence_scope": SCOPE})
        return 1

    local_results = run_assigned(manifest["tasks"], rank, size, physical_callback, args.backend,
                                 context["task_directory"], worker["identity"])
    post_error = None
    try:
        verify_identities(context)
    except Exception as exc:
        post_error = _error(exc)
    batch = {"rank": rank, "results": local_results, "post_identity_error": post_error}
    gathered = comm.gather(batch, root=0) if comm else [batch]
    status = "PASS"
    if rank == 0:
        results = sorted((row for group in gathered for row in group["results"]), key=lambda row: row["task_index"])
        if ([row["task_index"] for row in results] != list(range(len(manifest["tasks"]))) or
                any(row["rank"] != row["task_index"] % size for row in results)):
            status = "FAIL"
        if any(row["status"] != "PASS" for row in results) or any(group["post_identity_error"] for group in gathered):
            status = "FAIL"
        atomic_create(args.output, {"schema": "bass-he.c2g.physical-worker-result.v1", "status": status,
                     "physical_launch_enabled": True, "execution": args.execution, "backend": args.backend,
                     "workers": workers, "results": results,
                     "post_identity_errors": [group for group in gathered if group["post_identity_error"]],
                     "task_ownership": "task_index % mpi_size", "gather_policy": "summaries_only",
                     "wall_seconds": time.monotonic() - started, "evidence_scope": SCOPE,
                     "attempted_task_count": len(results),
                     "successful_sector_count": sum(row["status"] == "PASS" for row in results),
                     "requested_eigenstate_count": sum(task["nroots"] for task in manifest["tasks"]),
                     "NCP64_actual_scaling": "NOT_CLAIMED"})
    if comm:
        status = comm.bcast(status, root=0)
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
