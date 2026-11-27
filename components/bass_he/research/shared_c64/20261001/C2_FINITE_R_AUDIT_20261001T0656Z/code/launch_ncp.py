"""Validate a bounded single-host OpenMPI layout; print command by default."""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys

from host_probe import probe_host
from mpi_batch import child_environment, read_manifest


def is_openmpi_launcher(version):
    """OpenMPI 4.x launchers may identify the historical OpenRTE runtime."""
    return any(label in version for label in ("Open MPI", "OpenMPI", "OpenRTE"))


def validate_layout(host, ranks, threads, per_worker_memory_gib, controller_memory_gib=0.5, reserve_fraction=0.2):
    for key, value in (("ranks", ranks), ("threads", threads)):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{key} must be a positive integer")
    for key, value in (("per_worker_memory_gib", per_worker_memory_gib), ("controller_memory_gib", controller_memory_gib)):
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"{key} must be positive and finite")
    if not 0.2 <= reserve_fraction < 1:
        raise ValueError("reserve_fraction must preserve at least 20% headroom")
    budget = host.get("core_binding_cpu_budget")
    if budget is None:
        raise ValueError("physical-core topology unavailable: cannot certify --bind-to core budget")
    if ranks * threads > budget:
        raise ValueError(f"requested {ranks * threads} core slots exceeds detected budget {budget}")
    if host.get("cgroup_status") == "V2_UNAVAILABLE_V1_NOT_CERTIFIED":
        raise ValueError("cgroup v2 resource limit visibility required; cgroup v1 is unsupported")
    memory = host.get("memory_available_budget_bytes")
    if memory is None or memory <= 0:
        raise ValueError("available memory budget could not be established")
    worker_bytes = int(per_worker_memory_gib * 2**30)
    if worker_bytes <= 0:
        raise ValueError("worker memory limit rounds below one byte")
    workers = ranks - 1 if ranks > 1 else 1
    controller_bytes = int(controller_memory_gib * 2**30) if ranks > 1 else 0
    usable = int(memory * (1 - reserve_fraction))
    maximum_workers = max(0, (usable - controller_bytes) // worker_bytes)
    if workers > maximum_workers:
        raise ValueError(f"{workers} workers exceed memory cap {maximum_workers}; reduce ranks or establish a smaller measured per-worker envelope")
    return {"ranks": ranks, "threads_per_rank": threads, "workers": workers,
            "controller_rank": 0 if ranks > 1 else None, "reserved_core_slots": ranks * threads,
            "core_slot_budget": budget, "per_worker_memory_bytes": worker_bytes,
            "per_worker_memory_evidence": "CONFIGURED_RLIMIT_AS_NOT_MEASURED_PEAK_RSS",
            "controller_memory_budget_bytes": controller_bytes,
            "usable_memory_bytes": usable, "memory_headroom_fraction": reserve_fraction,
            "maximum_workers_from_memory": maximum_workers,
            "estimated_worker_memory_bytes": workers * worker_bytes}


def build_command(mpirun, python, manifest, output_dir, backend, ranks, threads):
    return [mpirun, "--host", f"localhost:{ranks * threads}", "--np", str(ranks), "--map-by", f"slot:PE={threads}", "--bind-to", "core",
            "--nooversubscribe", "--report-bindings", python,
            str(Path(__file__).with_name("mpi_batch.py").resolve()), "--manifest", str(Path(manifest).resolve()),
            "--output-dir", str(Path(output_dir).resolve()), "--backend", backend, "--python", python]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--backend", choices=("native", "reference"), required=True)
    parser.add_argument("--ranks", type=int, required=True)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--mpirun", default="mpirun", help="OpenMPI launcher name or explicit executable path")
    parser.add_argument("--execute", action="store_true", help="explicitly execute the validated command")
    parser.add_argument("--reserve-fraction", type=float, default=0.2)
    args = parser.parse_args(argv)
    manifest, manifest_sha, _ = read_manifest(args.manifest)
    host = probe_host()
    layout = validate_layout(host, args.ranks, args.threads,
                             manifest["limits"]["per_worker_memory_gib"], reserve_fraction=args.reserve_fraction)
    if Path(args.output_dir).exists():
        raise FileExistsError("output directory exists; create-only runs cannot resume or overwrite")
    mpirun = shutil.which(args.mpirun)
    if mpirun is None:
        raise RuntimeError("OpenMPI mpirun not found")
    version = subprocess.run([mpirun, "--version"], text=True, capture_output=True, check=True).stdout
    if not is_openmpi_launcher(version):
        raise RuntimeError("launcher must use OpenMPI mpirun")
    resolved_python = shutil.which(args.python)
    if resolved_python is None:
        raise RuntimeError("requested Python executable not found")
    python = str(Path(resolved_python).resolve())
    command = build_command(mpirun, python, args.manifest, args.output_dir, args.backend, args.ranks, args.threads)
    environment = child_environment()
    environment["OMP_NUM_THREADS"] = str(args.threads)
    output = {"schema": 1, "action": "EXECUTE" if args.execute else "COMMAND_ONLY_NOT_EXECUTED",
              "manifest_sha256": manifest_sha, "host": host, "layout": layout, "openmpi_version": version.strip(),
              "command_argv": command,
              "environment": {k: environment[k] for k in ("OMP_NUM_THREADS", "OMP_PLACES", "OMP_PROC_BIND", "OMP_DYNAMIC", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS")},
              "scope": "SINGLE_HOST; rank0 is controller when ranks>1; no physical 64-core assumption"}
    print(json.dumps(output, indent=2, sort_keys=True), flush=True)
    if args.execute:
        return subprocess.run(command, env=environment, check=False).returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
