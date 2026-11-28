#!/usr/bin/env python3
"""HEAVY_NUMERICS_V2 durable orchestrator for an existing wide-H scientific runner.

The legacy runner remains the scientific authority: its pair(), init(), grid,
provider, assembler, and source hashes are reused.  This wrapper changes only
process orchestration and checkpoint durability.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import multiprocessing
import os
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO_ROOT/"src"), str(REPO_ROOT/"vendor/orchestration")]

from heavy_numerics_v2 import (
    LeaseBusyError,
    RunLease,
    append_delta_queue,
    choose_worker_count,
    create_delta_archive,
    detect_affinity_count,
    detect_cpu_quota_cores,
    estimate_remaining_cpu_seconds,
    pending_delta_hashes,
    recover_orphan_pairs,
    sha256_file,
    should_checkpoint,
    should_handoff_local,
)

from wu088_hh.scheduler import order_tasks, predict_costs, verify_profile
from wu088_hh.hardware import inspect_host, partition_affinity_groups
from wu088_hh.autotune import validate_tuning_profile

POLICY = "HEAVY_NUMERICS_V2_COST_ORDER_V1"
PAIR_INTERVAL = 8
SECONDS_INTERVAL = 180.0
LOCAL_HANDOFF_CPU_SECONDS = 600.0


def _load_legacy(path: Path):
    spec = importlib.util.spec_from_file_location("hh_legacy_wide_runner", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load legacy runner: {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _read_events(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def _append_event(path: Path, row: dict) -> None:
    with path.open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _next_delta_sequence(delta_dir: Path) -> int:
    mx = 0
    for p in delta_dir.glob("delta_*.zip"):
        m = re.match(r"delta_(\d{4})_", p.name)
        if m:
            mx = max(mx, int(m.group(1)))
    return mx + 1


def _policy_description(requested_workers: int | None, tuning_profile: dict | None = None) -> dict:
    if tuning_profile is not None:
        selected = tuning_profile.get("selected") or {}
        processes = int(selected.get("processes", 0))
        threads = int(selected.get("kernel_threads", 0))
        use_smt = bool(selected.get("use_smt", False))
        if processes < 1 or threads < 1:
            raise ValueError("invalid tuning profile selected configuration")
        build_key = os.environ.get("WU088_R31M_BUILD_KEY", "")
        hw = inspect_host(requested_workers=processes, kernel_threads=threads, use_smt=use_smt)
        validate_tuning_profile(tuning_profile, hw, build_key)
        if requested_workers not in (None, processes):
            raise ValueError("--workers conflicts with tuning profile")
        effective = processes
        kernel_threads = threads
    else:
        hw = inspect_host(requested_workers=requested_workers or 12)
        quota = hw["quota_cores"]
        affinity = len(hw["cpus"])
        effective = choose_worker_count(
            requested_workers,
            cpu_count=os.cpu_count() or 1,
            affinity_count=affinity,
            quota_cores=quota,
        )
        kernel_threads = 1
    quota = hw["quota_cores"]
    affinity = len(hw["cpus"])
    return {
        "policy": POLICY,
        "hardware": hw,
        "requested_workers": requested_workers,
        "effective_workers": effective,
        "kernel_threads": kernel_threads,
        "tuning_profile_active": tuning_profile is not None,
        "cpu_count": os.cpu_count(),
        "affinity_count": affinity,
        "quota_cores": quota,
        "pair_checkpoint_interval": PAIR_INTERVAL,
        "seconds_checkpoint_interval": SECONDS_INTERVAL,
        "lease_mode": "NONBLOCKING",
        "dual_backup_ack_required_before_resume": True,
        "local_handoff_cpu_seconds": LOCAL_HANDOFF_CPU_SECONDS,
        "scientific_kernel_mutation": False,
    }


def _legacy_identity(legacy, args, h, d, t, W, gs, gw, length) -> dict:
    if hasattr(legacy, "build_identity_for_orchestrator"):
        return legacy.build_identity_for_orchestrator(args, h, d, t, W, gs, gw, length)
    ah = lambda x: hashlib.sha256(x.tobytes()).hexdigest()
    return {
        "producer": "wide_hybrid12_R30_v1",
        "n": args.n,
        "g": args.g,
        "z": float(args.z),
        "z_hex": float(args.z).hex(),
        "gamma_scale": args.gamma_scale,
        "gamma_scale_length": length,
        "model_sha256": legacy.sha(
            legacy.ROOT
            / "inputs/extracted/WU088_HH_R10_FULL_MIXED_BLOCK_OHD_PARTIAL_20260922_v1/inputs/FROZEN_INPUTS.npz"
        ),
        "native": h.identity,
        # Preserve the legacy scientific-driver identity.  The orchestrator is
        # recorded separately and does not rewrite existing checkpoint identity.
        "driver": legacy.sha(legacy.__file__),
        "assembler": legacy.sha(legacy.MIXED / "run.py"),
        "grid_source": legacy.sha(legacy.MIXED / "native.py"),
        "weights_source": legacy.sha(legacy.ROOT / "exact_weights/exact_laplace_weights.py"),
        "grid_sha256": {k: ah(v) for k, v in dict(t=t, W=W, gs=gs, gw=gw).items()},
        "sumabs_semantics": "triangle/L1 upper diagnostic, no outward rounding",
        "claim_ceiling": "H source computation only; requires B160/B192 convergence and later O/D/JVP/ionic full-matrix admission.",
    }


def _write_json_atomic(path: Path, data: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)


def _emit_delta(folder: Path, rows: list[dict], parent_sha: str | None) -> dict:
    delta_dir = folder / "durable_deltas"
    seq = _next_delta_sequence(delta_dir)
    delta = create_delta_archive(
        folder=folder,
        committed_rows=rows,
        delta_dir=delta_dir,
        sequence=seq,
        parent_checkpoint_sha256=parent_sha,
    )
    h = append_delta_queue(folder, delta)
    return {
        "status": "BOUNDED_CHECKPOINT_READY",
        "delta_path": str(delta),
        "delta_sha256": h,
        "delta_bytes": delta.stat().st_size,
        "new_pairs": len(rows),
        "resume_blocked_until_dual_backup_ack": True,
    }


def _make_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, choices=(160, 192))
    ap.add_argument("--g", type=int, default=80)
    ap.add_argument("--z", type=float)
    ap.add_argument("--gamma-scale", choices=("unit", "R"), default="unit")
    ap.add_argument("--workers", type=int, default=0, help="0=auto, capped by affinity/cgroup quota")
    ap.add_argument("--max-new-pairs", type=int, default=PAIR_INTERVAL)
    ap.add_argument("--max-wall-seconds", type=float, default=SECONDS_INTERVAL)
    ap.add_argument("--execution-lane", choices=("auto", "cloud", "local"), default="auto")
    ap.add_argument("--force-bounded-cloud", action="store_true")
    ap.add_argument("--parent-checkpoint-sha256")
    ap.add_argument("--legacy-runner", type=Path, default=Path(__file__).with_name("wide_hybrid_run.py"))
    ap.add_argument("--describe", action="store_true")
    ap.add_argument("--policy-describe", action="store_true")
    ap.add_argument("--cost-profile", type=Path, default=REPO_ROOT / "data/pair_cost_profile.json")
    ap.add_argument("--tuning-profile", type=Path)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = _make_parser().parse_args(argv)
    requested = None if args.workers <= 0 else args.workers
    tuning_profile = None
    if args.tuning_profile is not None:
        tuning_profile = json.loads(args.tuning_profile.read_text())
    policy = _policy_description(requested, tuning_profile)
    if args.policy_describe:
        print(json.dumps(policy, indent=2, sort_keys=True))
        return 0
    if args.n is None or args.z is None:
        raise SystemExit("--n and --z are required unless --policy-describe is used")
    if not 1 <= args.max_new_pairs <= 12 or not math.isfinite(args.max_wall_seconds) or args.max_wall_seconds <= 0:
        raise SystemExit("invalid bounded-checkpoint settings")
    if not args.legacy_runner.exists():
        raise SystemExit(f"legacy runner not found: {args.legacy_runner}")

    # Restrict only this process and its children, not the user desktop.
    os.sched_setaffinity(0, policy["hardware"]["cpus"])
    requested = policy["effective_workers"]
    legacy = _load_legacy(args.legacy_runner.resolve())
    legacy.provider_gate()
    folder = legacy.folder_for(args.n, args.g, args.z, args.gamma_scale)
    if args.describe:
        print(
            json.dumps(
                {
                    "status": "READY_POLICY_V2",
                    "folder": str(folder),
                    "n": args.n,
                    "g": args.g,
                    "z": args.z,
                    "z_hex": float(args.z).hex(),
                    "gamma_scale": args.gamma_scale,
                    **policy,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    folder.mkdir(parents=True, exist_ok=True)
    lease_meta = {
        "policy": POLICY,
        "orchestrator_sha256": sha256_file(__file__),
        "legacy_runner_sha256": sha256_file(args.legacy_runner),
        "n": args.n,
        "g": args.g,
        "z": float(args.z),
    }
    try:
        with RunLease(folder / "RUN.lock", folder / "RUN_STATE.json", metadata=lease_meta) as lease:
            pending_uploads = pending_delta_hashes(folder)
            if pending_uploads:
                print(
                    json.dumps(
                        {
                            "status": "BLOCKED_PENDING_DUAL_BACKUP_ACK",
                            "pending_delta_sha256": pending_uploads,
                        },
                        indent=2,
                    )
                )
                return 74

            h = legacy.Hybrid12()
            d, t, W, gs, gw, length = legacy.configuration(args.n, args.g, args.z, args.gamma_scale)
            identity = _legacy_identity(legacy, args, h, d, t, W, gs, gw, length)
            ip = folder / "IDENTITY.json"
            if ip.exists():
                if json.loads(ip.read_text()) != identity:
                    raise RuntimeError("checkpoint source/grid/geometry changed")
            else:
                _write_json_atomic(ip, identity)

            orchestration = {
                "policy": POLICY,
                "orchestrator_sha256": sha256_file(__file__),
                "legacy_driver_sha256": identity["driver"],
                "scientific_identity_sha256": sha256_file(ip),
                **policy,
            }
            _write_json_atomic(folder / "ORCHESTRATION_POLICY.json", orchestration)

            events = folder / "events.jsonl"
            recovered = recover_orphan_pairs(folder, events)
            if recovered:
                out = _emit_delta(folder, recovered, args.parent_checkpoint_sha256)
                out["status"] = "RECOVERED_ORPHANS_CHECKPOINT_READY"
                print(json.dumps(out, indent=2, sort_keys=True))
                return 0

            rows = _read_events(events)
            old = {(int(r["ia"]), int(r["ib"])): str(r["sha256"]) for r in rows if "ia" in r}
            tasks = []
            for ia in range(12):
                for ib in range(12):
                    p = folder / f"pair_{ia:02}_{ib:02}.npz"
                    if p.exists():
                        if old.get((ia, ib)) != sha256_file(p):
                            raise RuntimeError(f"changed pair checkpoint: {p}")
                    else:
                        tasks.append((ia, ib, str(p)))

            if not tasks and (folder / "RESULTS.json").is_file():
                saved = json.loads((folder / "RESULTS.json").read_text())
                if saved["identity_sha256"] != sha256_file(ip) or saved["sha256"] != sha256_file(folder / "ASSEMBLED.npz"):
                    raise RuntimeError("completed source identity changed")
                print(json.dumps({"status": "SOURCE_COMPLETE_REUSED_NOT_REASSEMBLED", "result": saved}))
                return 0

            profile = json.loads(args.cost_profile.read_text())
            verify_profile(profile, driver_sha=identity["driver"], model_sha=identity["model_sha256"],
                           g=args.g, gamma_scale=args.gamma_scale)
            costs, prediction = predict_costs(profile, n=args.n, z=args.z)
            tasks = order_tasks(tasks, costs)
            scheduling = {"scheduler": "MEASURED_COST_DESCENDING_CANONICAL_TIES", "profile_sha256": sha256_file(args.cost_profile),
                          "prediction": prediction, "ordered_pairs": [[x[0],x[1]] for x in tasks],
                          "kernel_changed": False, "max_unacked_new_pairs": args.max_new_pairs}
            _write_json_atomic(folder / "SCHEDULE_PLAN.json", scheduling)
            estimated_cpu = estimate_remaining_cpu_seconds(rows, len(tasks))
            if (
                args.execution_lane in ("auto", "cloud")
                and estimated_cpu is not None
                and should_handoff_local(estimated_cpu, threshold_seconds=LOCAL_HANDOFF_CPU_SECONDS)
                and not args.force_bounded_cloud
            ):
                print(
                    json.dumps(
                        {
                            "status": "HANDOFF_LOCAL_REQUIRED",
                            "estimated_remaining_cpu_seconds": estimated_cpu,
                            "pending_pairs": len(tasks),
                            "threshold_seconds": LOCAL_HANDOFF_CPU_SECONDS,
                            "resume_command": f"python {Path(__file__).name} --n {args.n} --g {args.g} --z {args.z!r} --gamma-scale {args.gamma_scale} --execution-lane local",
                        },
                        indent=2,
                        sort_keys=True,
                    )
                )
                return 78

            workers = choose_worker_count(
                requested,
                cpu_count=os.cpu_count() or 1,
                affinity_count=detect_affinity_count(),
                quota_cores=detect_cpu_quota_cores(),
            )
            start = time.monotonic()
            new_rows: list[dict] = []
            print(
                json.dumps(
                    {
                        "status": "RUN_STARTED",
                        "pending_pairs": len(tasks),
                        "requested_workers": args.workers,
                        "effective_workers": workers,
                        "max_new_pairs": args.max_new_pairs,
                        "max_wall_seconds": args.max_wall_seconds,
                    }
                ),
                flush=True,
            )

            while tasks:
                remaining_budget = max(1, args.max_new_pairs - len(new_rows))
                wave_limit = min(remaining_budget, len(tasks))
                wave, later = tasks[:wave_limit], tasks[wave_limit:]
                pool_workers = min(workers, len(wave))
                batch_rows: list[dict] = []
                batch_started = time.monotonic()
                first_completed = None
                next_task = 0
                stop_scheduling = False
                executor_kwargs = dict(
                    max_workers=pool_workers,
                    initializer=legacy.init,
                    initargs=(args.n, args.g, args.z, args.gamma_scale),
                )
                if tuning_profile is not None:
                    if not hasattr(legacy, "tuned_init"):
                        raise RuntimeError("tuned profile requires legacy.tuned_init")
                    topology = {int(k): tuple(v) for k, v in policy["hardware"]["topology"].items()}
                    l3_by_cpu = {int(k): v for k, v in policy["hardware"]["l3_by_cpu"].items()}
                    groups = partition_affinity_groups(
                        topology, set(policy["hardware"]["allowed_logical_cpus"]),
                        workers=pool_workers, kernel_threads=policy["kernel_threads"],
                        use_smt=bool(tuning_profile["selected"].get("use_smt", False)), l3_by_cpu=l3_by_cpu)
                    ctx = multiprocessing.get_context("fork")
                    counter, lock, barrier = ctx.Value("i", 0), ctx.Lock(), ctx.Barrier(pool_workers)
                    executor_kwargs.update(
                        initializer=legacy.tuned_init,
                        initargs=(args.n, args.g, args.z, args.gamma_scale, [sorted(g) for g in groups], counter, lock, barrier),
                        mp_context=ctx,
                    )
                with ProcessPoolExecutor(**executor_kwargs) as pool:
                    pending = {}
                    while next_task < len(wave) and len(pending) < pool_workers:
                        task = wave[next_task]; next_task += 1
                        pending[pool.submit(legacy.pair, task)] = task
                    while pending:
                        fut = next(as_completed(tuple(pending)))
                        pending.pop(fut)
                        row = fut.result()
                        if first_completed is None:
                            first_completed = time.monotonic()
                        row.update(
                            completed_this_invocation=len(new_rows) + len(batch_rows) + 1,
                            elapsed_wall_seconds=time.monotonic() - start,
                            orchestrator_policy=POLICY,
                        )
                        _append_event(events, row)
                        batch_rows.append(row)
                        lease.heartbeat(
                            committed_pairs_total=len(old) + len(new_rows) + len(batch_rows),
                            committed_pairs_this_invocation=len(new_rows) + len(batch_rows),
                        )
                        print(json.dumps(row), flush=True)
                        if time.monotonic() - start >= args.max_wall_seconds:
                            stop_scheduling = True
                        if not stop_scheduling and next_task < len(wave):
                            task = wave[next_task]; next_task += 1
                            pending[pool.submit(legacy.pair, task)] = task
                # Any task not submitted because the time budget expired remains pending, in original cost order.
                tasks = wave[next_task:] + later
                batch_finished = time.monotonic()
                _append_event(folder / "ORCHESTRATION_TELEMETRY.jsonl", {
                    "phase": "COMPUTE_WAVE", "worker_slots": pool_workers, "pairs": len(batch_rows),
                    "wave_wall_seconds": batch_finished-batch_started,
                    "first_completion_seconds": None if first_completed is None else first_completed-batch_started,
                    "drain_tail_seconds": 0 if first_completed is None else batch_finished-first_completed,
                    "sum_pair_cpu_seconds": sum(float(r.get("cpu_seconds",0)) for r in batch_rows),
                    "persistent_pool": True, "submitted_pairs": next_task,
                    "timestamp_unix": time.time(), "profile_sha256": scheduling["profile_sha256"],
                })
                new_rows.extend(batch_rows)
                elapsed = time.monotonic() - start
                if tasks and should_checkpoint(
                    len(new_rows),
                    elapsed,
                    pair_interval=args.max_new_pairs,
                    seconds_interval=args.max_wall_seconds,
                ):
                    out = _emit_delta(folder, new_rows, args.parent_checkpoint_sha256)
                    out.update(remaining_pairs=len(tasks), elapsed_wall_seconds=elapsed)
                    print(json.dumps(out, indent=2, sort_keys=True), flush=True)
                    return 0

            # All pairs complete.  Preserve the legacy scientific assembly path.
            result = legacy.assemble(folder, args.z)
            result.update(
                status="COMPUTED_WIDE_HYBRID12_H_NOT_ADMITTED",
                producer="wide_hybrid12_R30_v1",
                n=args.n,
                g=args.g,
                z=float(args.z),
                z_hex=float(args.z).hex(),
                gamma_scale=args.gamma_scale,
                wall_seconds_this_invocation=time.monotonic() - start,
                identity_sha256=sha256_file(ip),
                quadrature_admitted=False,
                trajectory_admitted=False,
                orchestrator_policy=POLICY,
            )
            rp = folder / "RESULTS.json"
            if rp.exists():
                saved = json.loads(rp.read_text())
                if saved["sha256"] != result["sha256"] or saved["identity_sha256"] != result["identity_sha256"]:
                    raise RuntimeError("completed result changed")
            else:
                _write_json_atomic(rp, result)
            if new_rows:
                out = _emit_delta(folder, new_rows, args.parent_checkpoint_sha256)
                out.update(final_local_result=True, results_sha256=sha256_file(rp))
                print(json.dumps(out, indent=2, sort_keys=True), flush=True)
            print(json.dumps(result, sort_keys=True), flush=True)
            return 0
    except LeaseBusyError as exc:
        print(json.dumps({"status": "BUSY_ACTIVE_RUN", "error": str(exc)}))
        return 73


if __name__ == "__main__":
    raise SystemExit(main())
