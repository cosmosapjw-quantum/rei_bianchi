#!/usr/bin/env python3
"""Observe, reuse or compile, and run the one ready HE29 canary once.

This is a local NCP entrypoint, not a remote submission client. A shared lease,
actual Linux process/resource observation, bounded saved-result intake and the
pinned scientific gates precede execution. Existing partial runs are preserved.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import traceback

sys.dont_write_bytecode = True
from hpc_canary import (atomic_json, checked_checkout, digest, load_a5, REPO,
                        PACKED_REVISION, HE29_REL, WORKER_FLAG, check_sources_external,
                        TABLE_SHA256)
from build_parallel import watchdog_for, CONTROLLER_REVISION
from host_plan import observe_host, choose_resources, active_he29_processes, host_execution_lease

LANE = Path(__file__).resolve().parents[1]
THREAD_ENV = {key: "1" for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS", "RAYON_NUM_THREADS")}
SCAN_PREFIXES = ("HE29_PACKED_", "HE29_HPC64_", "HE29_NCP_", "HE29_REFERENCE_")


def read_json(path, limit=4*1024**2):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
        raise ValueError("HE29_HPC_RECEIPT_FILE_BUDGET: " + str(path))
    return json.loads(path.read_text())


def saved_intake(roots, excluded=(), *, max_directories=10000, max_depth=10):
    """Bounded saved-artifact observation; never infers global remote absence."""
    excluded = [Path(p).resolve() for p in excluded]
    result = {"scope_roots": [], "visited_directories": 0, "canary_evidence": [],
              "build_receipts": [], "errors": [], "complete_in_declared_scope": True}
    stack = []
    for root in roots:
        root = Path(root).resolve(strict=True)
        if not root.is_dir():
            raise ValueError("HE29_HPC_OBSERVE_ROOT_NOT_DIRECTORY")
        result["scope_roots"].append(str(root))
        # /root is intentionally not a recursive home scan.
        if root == Path("/root"):
            stack.extend((p, 0) for p in root.iterdir()
                         if p.name.startswith(SCAN_PREFIXES) and p.is_dir() and not p.is_symlink())
        else:
            stack.append((root, 0))
    while stack:
        path, depth = stack.pop()
        if path.is_symlink() or any(path.is_relative_to(p) for p in excluded):
            continue
        result["visited_directories"] += 1
        if result["visited_directories"] > max_directories:
            result["errors"].append("DIRECTORY_BUDGET_EXCEEDED")
            break
        try:
            children = sorted(path.iterdir())
        except OSError as exc:
            result["errors"].append({"path": str(path), "error": repr(exc)})
            continue
        for child in children:
            if child.is_symlink():
                continue
            if child.is_dir():
                if child.name in (".git", "venv", ".venv", "target", "site-packages", "__pycache__"):
                    continue
                # Git source is an execution source, not a saved runtime return.
                if (child / ".git").exists() or (child / ".git").is_file():
                    continue
                if child.name in ("canary", "entry_canary") and not any(child.resolve().is_relative_to(p) for p in excluded):
                    result["canary_evidence"].append({"path": str(child),
                        "status": "OCCUPIED_CANARY_PATH_PRESERVED", "admission": "NOT_INFERRED"})
                if depth >= max_depth:
                    result["errors"].append({"path": str(child), "error": "DEPTH_BUDGET"})
                else:
                    stack.append((child, depth+1))
                continue
            if child.name == "BUILD_IDENTITY.json":
                try:
                    data = read_json(child)
                    if data.get("schema") == "he29.optimized.build.v1":
                        result["build_receipts"].append(str(child))
                except (OSError, ValueError) as exc:
                    result["errors"].append({"path": str(child), "error": repr(exc)})
            if child.name not in ("PACKED_RAW.json", "RESULT.json", "IDENTITY.json", "COMMAND.json"):
                continue
            try:
                data = read_json(child)
                schema = str(data.get("schema", ""))
                argv = data.get("argv", [])
                command_canary = (isinstance(argv, list)
                    and any(Path(str(x)).name in ("run_packed.py", "hpc_canary.py", "run_vigilode.py") for x in argv)
                    and any(x in argv for x in ("canary", "worker", "_worker")))
                # IDENTITY gives a started run even before a RAW/RESULT exists.
                identity_canary = (child.name == "IDENTITY.json" and
                    (data.get("packed_threads") == 1 or "bridge" in data))
                if child.name == "PACKED_RAW.json" or ("canary" in schema) or command_canary or identity_canary:
                    result["canary_evidence"].append({"path": str(child),
                        "sha256": digest(child), "schema": schema,
                        "status": data.get("status", "EVIDENCE_PRESENT_READ_FIRST"),
                        "source_publication": data.get("publication", data.get("adapter_publication")),
                        "table_sha256": data.get("table_sha256", data.get("source_table_sha256")),
                        "binary_sha256": data.get("binary_sha256"),
                        "admission": "NOT_INFERRED_FROM_FILENAME_OR_STATUS"})
            except (OSError, ValueError, TypeError) as exc:
                # A malformed packed RAW still blocks a duplicate run.
                if child.name == "PACKED_RAW.json":
                    result["canary_evidence"].append({"path": str(child), "error": repr(exc)})
                else:
                    result["errors"].append({"path": str(child), "error": repr(exc)})
    result["complete_in_declared_scope"] = not result["errors"]
    result["execution_allowed"] = not result["errors"] and not result["canary_evidence"]
    result["absence_claim"] = "Only readable declared local roots at this observation; not all hosts/conversations."
    return result


def select_bridge(runner, receipts, explicit=None):
    candidates = [str(Path(explicit)/"BUILD_IDENTITY.json")] if explicit else sorted(set(receipts))
    inspected = []
    for filename in candidates:
        receipt = Path(filename)
        library = receipt.parent / "target/release/libhe29_optimized_bridge.so"
        try:
            value = runner.verify_build(library, receipt)
            if value.get("bass_publication_head") != PACKED_REVISION:
                raise ValueError("HE29_HPC_REUSED_BRIDGE_PUBLICATION")
            inspected.append({"receipt": str(receipt), "status": "VALID_REUSED", "library_sha256": digest(library)})
            return receipt.parent, inspected
        except (OSError, ValueError, KeyError) as exc:
            inspected.append({"receipt": str(receipt), "status": "INVALID_PRESERVED", "error": repr(exc)})
            if explicit:
                raise ValueError("HE29_HPC_EXPLICIT_BRIDGE_INVALID: " + repr(exc)) from exc
    return None, inspected


def worker_argv(args, bridge, workers, out):
    argv = [sys.executable, "-B", str(LANE / "src/hpc_canary.py"), "worker"]
    values = {"packed-root": args.packed_root, "baseline-campaign": args.baseline_campaign,
        "binary": args.binary, "owner-receipt": args.owner_receipt, "data-root": args.data_root,
        "library": str(bridge / "target/release/libhe29_optimized_bridge.so"),
        "bridge-receipt": str(bridge / "BUILD_IDENTITY.json"), "out": str(out),
        "table-cache": args.table_cache, "source-revision": args.source_revision,
        "table-workers": str(workers), "sync-every": str(args.sync_every)}
    for key, value in values.items():
        argv += ["--" + key, str(value)]
    return argv


def parse_arguments(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    ap.add_argument("mode", choices=("plan", "run"))
    for name in ("out", "packed-root", "controller-root", "baseline-campaign", "binary",
                 "owner-receipt", "data-root", "table-cache", "source-revision"):
        ap.add_argument("--" + name, required=True)
    ap.add_argument("--observe-root", action="append", required=True)
    ap.add_argument("--lease", default="/tmp/BASS_HE_HE29_NATIVE.lock")
    ap.add_argument("--bridge-build")
    ap.add_argument("--max-table-workers", type=int, default=48)
    ap.add_argument("--max-build-jobs", type=int, default=8)
    ap.add_argument("--sync-every", type=int, default=256)
    ap.add_argument("--wall-s", type=float, default=900.)
    ap.add_argument("--vigilode-checkout")
    ap.add_argument("--cargo", default="cargo")
    ap.add_argument("--rustc", default="rustc")
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args(argv)
    if not math.isfinite(args.wall_s) or not 0 < args.wall_s <= 3600:
        ap.error("canary wall budget must be finite, positive, <=3600 seconds")
    if not 1 <= args.sync_every <= 256:
        ap.error("sync-every must be 1..256")
    if not 1 <= args.max_table_workers <= 48 or not 1 <= args.max_build_jobs <= 8:
        ap.error("table/build worker limits are 48/8")
    return args


def main(argv=None):
    args = parse_arguments(argv)
    out = Path(args.out).resolve()
    protected = [REPO.resolve(), Path(args.packed_root).resolve(), Path(args.controller_root).resolve(),
                 Path(args.baseline_campaign).resolve(), Path(args.data_root).resolve(), Path(args.table_cache).resolve()]
    if any(out.is_relative_to(p) or p.is_relative_to(out) for p in protected):
        raise ValueError("HE29_HPC_BATCH_OUTPUT_OVERLAP")
    out.mkdir(parents=True, exist_ok=False)
    old_affinity = None
    activity = {"canary_workers_started": 0, "baseline_pairs_started": 0,
                "completed_suites_replayed": 0, "new_builds_started": 0}
    try:
        checked_checkout(REPO, args.source_revision)
        checked_checkout(args.packed_root, PACKED_REVISION)
        checked_checkout(args.controller_root, CONTROLLER_REVISION)
        os.environ.update(THREAD_ENV)
        os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
        with host_execution_lease(Path(args.lease)):
            host = observe_host()
            resources = choose_resources(host, max_table_workers=args.max_table_workers,
                                         max_build_jobs=args.max_build_jobs)
            processes = active_he29_processes(args.binary)
            saved = saved_intake(args.observe_root, excluded=protected + [out])
            plan = {"schema": "he29.hpc64.batch_plan.v1", "observed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "host": host, "resources": resources, "processes": processes, "saved": saved,
                "execution_allowed": bool(resources["execution_allowed"] and processes["execution_allowed"] and saved["execution_allowed"]),
                "ready_scientific_jobs": ["HE29_PACKED_R4_TABLE512"],
                "already_admitted_reference_pairs_reused": 4, "solver_threads": 1,
                "source_revision": args.source_revision, "packed_revision": PACKED_REVISION,
                "watchdog_revision": CONTROLLER_REVISION, "activity": dict(activity)}
            atomic_json(out / "PLAN.json", plan)
            if args.mode == "plan":
                return 0 if plan["execution_allowed"] else 2
            if not plan["execution_allowed"]:
                atomic_json(out / "HOLD.json", {"status": "HOLD_OBSERVATION_OR_EXISTING_RETURN", "activity": activity,
                    "next": "Read the saved evidence and host constraints; no automatic rerun or process termination."})
                return 2
            old_affinity = os.sched_getaffinity(0)
            os.sched_setaffinity(0, resources["cpu_ids"])
            runner = load_a5(args.packed_root)
            current, data_provenance = check_sources_external(sys.modules["reference_runner"],
                args.binary, args.owner_receipt, args.data_root)
            prior, reused = runner.baseline_contract(args.baseline_campaign, current)
            if prior.get("table_sha256") != TABLE_SHA256:
                raise ValueError("HE29_HPC_PRE_BUILD_TABLE_IDENTITY")
            atomic_json(out / "BASELINE_BEFORE_BUILD.json", {"current": current,
                "reused": reused, "data_provenance": data_provenance,
                "table_sha256": prior["table_sha256"], "new_native_calls": 0})
            bridge, inspected = select_bridge(runner, saved["build_receipts"], args.bridge_build)
            atomic_json(out / "BRIDGE_INTAKE.json", {"inspected": inspected,
                "action": "REUSE" if bridge is not None else "COMPILE_MISSING_ARTIFACT"})
            if bridge is None:
                from build_parallel import main as build_main
                bridge = out / "build"
                build_args = ["--packed-root", args.packed_root, "--controller-root", args.controller_root,
                    "--out", str(bridge), "--source-revision", args.source_revision,
                    "--jobs", str(resources["build_jobs"]), "--cargo", args.cargo, "--rustc", args.rustc]
                if args.vigilode_checkout:
                    build_args += ["--vigilode-checkout", args.vigilode_checkout]
                if args.offline:
                    build_args.append("--offline")
                activity["new_builds_started"] = 1
                build_main(build_args)
            # Reobserve just before dispatch; the shared lease covers both checks.
            before_dispatch = active_he29_processes(args.binary)
            atomic_json(out / "PROCESS_BEFORE_DISPATCH.json", before_dispatch)
            if not before_dispatch["execution_allowed"]:
                raise RuntimeError("HE29_HPC_PROCESS_CHANGED_BEFORE_DISPATCH")
            run_process = watchdog_for(args.packed_root, args.controller_root)
            os.environ[WORKER_FLAG] = "1"
            activity["canary_workers_started"] = 1
            receipt = run_process(worker_argv(args, bridge, resources["table_workers"], out / "case"),
                                  out / "canary_process", args.wall_s)
            success = (receipt["returncode"] == 0 and not receipt["timed_out"] and (out / "case/RESULT.json").is_file())
            atomic_json(out / "SUMMARY.json", {"schema": "he29.hpc64.batch_summary.v1",
                "status": "CANARY_COMPLETED_SCOPED" if success else "HOLD_FIRST_FAILURE",
                "activity": activity, "process_receipt": receipt, "bridge_build": str(bridge),
                "table_workers": resources["table_workers"], "build_jobs": resources["build_jobs"],
                "solver_threads": 1, "native_reference_pairs_reused": 4,
                "actual_HE29_speedup": "REQUIRES_ANALYSIS_OF_RETURNED_PHASE_TIMINGS"})
            return 0 if success else 1
    except BaseException as exc:
        atomic_json(out / "FAILURE.json", {"status": "HOLD_FIRST_FAILURE", "error": repr(exc),
            "traceback": traceback.format_exc(), "activity": activity,
            "prior_outputs_preserved": True})
        raise
    finally:
        if old_affinity is not None:
            os.sched_setaffinity(0, old_affinity)


if __name__ == "__main__":
    raise SystemExit(main())
