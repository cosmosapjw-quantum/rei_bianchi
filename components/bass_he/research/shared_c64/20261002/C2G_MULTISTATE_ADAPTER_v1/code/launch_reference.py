#!/usr/bin/env python3
"""Create-only bounded launcher for the reviewed C2g finite-basis reference pilot."""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import secrets
import subprocess
import sys
import traceback

from launch_manufactured import (OWNER_ENV, OwnedProcessGuard, monitor_process,
                                 reserve_output, resolve_mpiexec)
from physical_contract import (SCOPE, approved_inputs, native_identity,
                               source_identity, validate_registered_layout, validate_request)
from runtime_support import (GIB, ContractError, atomic_create, execution_environment,
                             file_identity, host_preflight, sha256_file)


def execute(args, output, companion):
    manifest, inputs, review = approved_inputs(args.manifest, args.review)
    host = host_preflight()
    native = str(Path(args.native_library).resolve(strict=True)) if args.native_library else None
    validate_request(manifest, args.execution, args.backend, native,
                     args.ranks, args.threads, args.binding, host)
    layout_id = validate_registered_layout(inputs["preregistration"]["path"], args.execution,
                                            args.backend, args.ranks, args.threads, args.binding)
    native_binding = native_identity(native)
    env = execution_environment(args.threads, args.binding)
    env[OWNER_ENV] = secrets.token_hex(32)
    # Never let an inherited library variable silently choose a kernel.
    env.pop("BASS_NATIVE_LIBRARY", None)
    env.pop("BASS_NATIVE_EXPECTED_SHA256", None)
    if native:
        env["BASS_NATIVE_LIBRARY"] = native
        env["BASS_NATIVE_EXPECTED_SHA256"] = native_binding["library"]["sha256"]
    worker_output = companion / "worker_result.json"
    context_path = companion / "launch_context.json"
    task_directory = companion / "tasks"
    task_directory.mkdir(mode=0o700)
    code_dir = Path(__file__).resolve().parent
    context = {"schema": "bass-he.c2g.physical-launch-context.v1", "physical_launch_enabled": True,
               "inputs": inputs, "source": source_identity(code_dir), "native_identity": native_binding,
               "host_preflight": host, "worker_output": str(worker_output),
               "task_directory": str(task_directory),
               "launch": {"execution": args.execution, "backend": args.backend,
                          "native_library": native, "ranks": args.ranks,
                          "threads": args.threads, "binding": args.binding, "layout_id": layout_id},
               "mpi": None, "serial_affinity_cpus": None,
               "evidence_scope": SCOPE,
               "quota_scope": "this_run_only_campaign_two_run_ledger_owned_by_caller"}
    prefix = []
    preexec = None
    if args.execution == "mpi":
        mpiexec, context["mpi"] = resolve_mpiexec(args.mpiexec, env)
        prefix = [mpiexec, "-np", str(args.ranks), "--host",
                  f"localhost:{math.floor(host['effective_cpu_budget'])}", "--nooversubscribe"]
        if args.binding == "core":
            prefix += ["--map-by", f"slot:PE={args.threads}", "--bind-to", "core"]
        else:
            prefix += ["--map-by", "slot", "--bind-to", "none"]
    elif args.binding == "core":
        cores = list(host["physical_cores_in_affinity"].values())[:args.threads]
        selected = sorted(cpu for core in cores for cpu in core)
        context["serial_affinity_cpus"] = selected
        def set_affinity():
            os.sched_setaffinity(0, selected)
        preexec = set_affinity
    atomic_create(context_path, context)
    command = prefix + [sys.executable, str(code_dir / "run_reference.py"),
                       "--context", str(context_path), "--context-sha256", sha256_file(context_path),
                       "--execution", args.execution, "--backend", args.backend, "--output", str(worker_output)]
    if native:
        command += ["--native-library", native]
    recorded_env = ("OMP_NUM_THREADS", "OMP_DYNAMIC", "OMP_PROC_BIND", "OMP_PLACES",
                    "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "BLIS_NUM_THREADS",
                    "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "BASS_NATIVE_LIBRARY",
                    "BASS_NATIVE_EXPECTED_SHA256")
    atomic_create(companion / "command.json", {"argv": command, "cwd": str(code_dir),
                 "environment_overrides": {key: env.get(key) for key in recorded_env}})
    with (companion / "stdout.txt").open("xb") as stdout, (companion / "stderr.txt").open("xb") as stderr:
        proc = subprocess.Popen(command, cwd=code_dir, env=env, stdout=stdout, stderr=stderr,
                                start_new_session=True, preexec_fn=preexec)
        guard = OwnedProcessGuard(proc, env[OWNER_ENV])
        try:
            process = monitor_process(proc, guard, manifest["limits"]["wall_seconds"],
                                      manifest["limits"]["memory_gib"] * GIB)
        except BaseException:
            guard.stop()
            raise
        finally:
            guard.close()
            stdout.flush()
            os.fsync(stdout.fileno())
            stderr.flush()
            os.fsync(stderr.fileno())
    worker = json.loads(worker_output.read_text()) if worker_output.is_file() else None
    post_error = None
    try:
        for identity in inputs.values():
            if file_identity(identity["path"]) != identity:
                raise ContractError("reviewed inputs changed during bounded execution")
        if source_identity(code_dir) != context["source"] or native_identity(native) != native_binding:
            raise ContractError("source or native dependency changed during bounded execution")
    except Exception as exc:
        post_error = {"type": type(exc).__name__, "message": str(exc)}
    status = ("PASS" if process["returncode"] == 0 and process["termination"] is None
              and worker and worker.get("status") == "PASS" and post_error is None else "FAIL")
    receipts = [file_identity(path) for path in sorted(task_directory.glob("*.json"))]
    report = {"schema": "bass-he.c2g.physical-launch-result.v1", "status": status,
              "physical_launch_enabled": True, "evidence_scope": SCOPE,
              "NCP64_actual_scaling": "NOT_CLAIMED", "context": file_identity(context_path),
              "inputs": inputs, "reviewer": review["reviewer"], "process": process,
              "worker_result": file_identity(worker_output) if worker else None,
              "worker_status": worker.get("status") if worker else "MISSING",
              "task_count": len(manifest["tasks"]),
              "requested_eigenstate_count": sum(task["nroots"] for task in manifest["tasks"]),
              "backend": args.backend, "execution": args.execution, "ranks": args.ranks,
              "threads_per_rank": args.threads, "binding": args.binding, "layout_id": layout_id,
              "runtime_directory": str(companion), "task_receipts": receipts,
              "post_identity_error": post_error,
              "stdout": file_identity(companion / "stdout.txt"),
              "stderr": file_identity(companion / "stderr.txt"),
              "scientific_acceptance": "SEPARATE_REGISTERED_ANALYSIS_REQUIRED",
              "quota_scope": context["quota_scope"]}
    atomic_create(output, report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--review", required=True)
    parser.add_argument("--execution", required=True, choices=("serial", "mpi"))
    parser.add_argument("--backend", required=True, choices=("numpy", "native"))
    parser.add_argument("--native-library")
    parser.add_argument("--ranks", required=True, type=int)
    parser.add_argument("--threads", required=True, type=int)
    parser.add_argument("--binding", required=True, choices=("none", "core"))
    parser.add_argument("--mpiexec", default="auto")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        output, companion = reserve_output(args.output)
    except Exception as exc:
        print(f"CREATE_ONLY_OUTPUT_REJECTED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    try:
        report = execute(args, output, companion)
    except (Exception, KeyboardInterrupt) as exc:
        report = {"schema": "bass-he.c2g.physical-launch-result.v1", "status": "FAIL",
                  "stage": "LAUNCH_OR_PREFLIGHT", "runtime_directory": str(companion),
                  "error": {"type": type(exc).__name__, "message": str(exc),
                            "traceback": traceback.format_exc()}}
        atomic_create(output, report)
    print(json.dumps({"status": report["status"], "output": str(output)}, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
