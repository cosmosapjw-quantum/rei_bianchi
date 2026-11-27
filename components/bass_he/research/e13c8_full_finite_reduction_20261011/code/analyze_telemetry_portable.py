#!/usr/bin/env python3
"""Analyze saved E13C7 MPI telemetry; no imports from scientific code or execution.

Elapsed-time accounting and overlapping task envelopes are not CPU utilization
or serial-versus-parallel speedup. This distinction is part of every output.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import heapq
import json
from pathlib import Path
import statistics
import sys
import time


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def pin(path: Path):
    h = hashlib.sha256()
    n = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            n += len(chunk)
            h.update(chunk)
    return {"bytes": n, "sha256": h.hexdigest()}


def elapsed_fraction(value):
    """Exactly interpret the published decimal spelling, not its unknown clock."""
    return Fraction(str(value))


def ratio(numerator, denominator):
    value = elapsed_fraction(numerator) / elapsed_fraction(denominator)
    return {"ratio": float(value), "exact_published_decimal_ratio": str(value)}


EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def utc_us(value):
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise ValueError("naive UTC timestamp")
    d = dt.astimezone(timezone.utc) - EPOCH
    return (d.days * 86400 + d.seconds) * 1_000_000 + d.microseconds


def distribution(values):
    ordered = sorted(values)
    def quantile(p):
        # Linear interpolation between adjacent order statistics, indices 0..n-1.
        position = (len(ordered) - 1) * p
        low = int(position)
        high = min(low + 1, len(ordered) - 1)
        return ordered[low] + (ordered[high] - ordered[low]) * (position - low)
    return {"count": len(ordered), "min": ordered[0], "max": ordered[-1],
            "sum": float(sum(map(elapsed_fraction, ordered), Fraction())),
            "mean": statistics.mean(ordered), "median": statistics.median(ordered),
            "p90": quantile(.9), "p95": quantile(.95), "p99": quantile(.99),
            "population_stdev": statistics.pstdev(ordered),
            "quantile_convention": "linear interpolation at (n-1)*p"}


def occupancy(intervals, slots):
    """Sweep recorded UTC envelopes. Includes blocking, scheduling and I/O."""
    events = defaultdict(int)
    for start, end in intervals:
        if not start <= end:
            raise ValueError("negative UTC envelope")
        events[start] += 1
        events[end] -= 1
    times = sorted(events)
    counts = Counter()
    current = 0
    previous = times[0]
    for stamp in times:
        counts[current] += stamp - previous
        current += events[stamp]
        if not 0 <= current <= slots:
            raise ValueError("overlapping same-rank work or invalid envelope")
        previous = stamp
    if current != 0:
        raise ValueError("unclosed UTC interval")
    span = times[-1] - times[0]
    area = sum(level * microseconds for level, microseconds in counts.items())
    if area != sum(end - start for start, end in intervals):
        raise ValueError("UTC sweep failed its direct sum identity")
    return {"status": "RECORDED_TASK_ENVELOPES_ONLY_NOT_CPU_UTILIZATION",
            "clock_caveat": "same-host UTC timestamps; no independent clock-adjustment telemetry",
            "span_seconds": span / 1e6,
            "summed_envelope_seconds": area / 1e6,
            "max_simultaneous_envelopes": max(k for k, v in counts.items() if v > 0),
            "mean_simultaneous_envelopes": ratio(area, span),
            "slot_envelope_coverage": ratio(area, slots * span),
            "seconds_by_simultaneous_envelopes": {str(k): v / 1e6 for k, v in sorted(counts.items()) if v},
            "seconds_at_all_slots": counts[slots] / 1e6,
            "seconds_at_least_60_slots": sum(v for k, v in counts.items() if k >= 60) / 1e6,
            "no_CPU_time_or_busy_sampling_inferred": True}


def write_new(path, data):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        if isinstance(data, str):
            stream.write(data)
        else:
            json.dump(data, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--return-dir", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    start_clock = time.perf_counter()
    returned, package, out = args.return_dir.resolve(strict=True), args.package.resolve(strict=True), args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    for name in ("PERFORMANCE_ANALYSIS.json", "PERFORMANCE_NOTES_KO.md", "PERFORMANCE_IDENTITY.json"):
        if (out / name).exists():
            raise FileExistsError("fresh outputs required: " + str(out / name))
    batch_dir = returned / "BATCH"
    batch = load(batch_dir / "BATCH_COMPLETE.json")
    manifest = load(batch_dir / "EXECUTION_MANIFEST.json")
    host = load(batch_dir / "HOST_PREFLIGHT.json")
    execution = load(batch_dir / "EXECUTION_RECEIPT.json")
    launcher = load(batch_dir / "LAUNCH_PROCESS_RECEIPT.json")
    attempt = load(returned / "ATTEMPT_COMPLETE.json")
    attempt_start = load(returned / "ATTEMPT_START.json")
    index = load(package / "inputs/INPUT_INDEX.json")["records"]
    forecast = load(package / "analysis/RESOURCE_ALLOCATION.json")
    plan = load(returned / "PINNED_EXECUTION/inputs/WORK_PLAN.json")
    ranks = manifest["ranks"]
    assert ranks == host["selected_ranks"] == launcher["rank_count"] == 64
    assert execution["exit_code"] == attempt["mpi_child_exit_code"] == 0
    assert launcher["exit_codes"] == [0]
    assert manifest["transport"] == launcher["transport"] == "mpi"
    assert attempt_start["provider_attestation"] == "NOT_ASSERTED"
    ordered = {row["node"]: row for row in batch["ordered_paths"]}
    nodes = sorted(ordered)
    assert nodes == sorted(manifest["work"]["nodes"]) == sorted(plan["ncp_nodes"])
    assert len(nodes) == len(batch["ordered_paths"]) == 2331
    assert batch["reused_completed_paths"] == 0
    assert all(row["reused"] is False for row in ordered.values())
    assert sum(row["summary"]["new_coefficient_evaluations"] for row in ordered.values()) == 9547776
    evidence = {}
    def record_pin(base, relative, namespace):
        key = namespace + "/" + relative
        value = pin(base / relative)
        evidence[key] = value
        return value
    for name in ("BATCH_COMPLETE.json", "EXECUTION_MANIFEST.json", "HOST_PREFLIGHT.json", "EXECUTION_RECEIPT.json", "LAUNCH_PROCESS_RECEIPT.json", "START.json", "LAUNCH_0000_STARTED.json"):
        record_pin(batch_dir, name, "return/BATCH")
    for name in ("ATTEMPT_COMPLETE.json", "ATTEMPT_START.json", "PINNED_EXECUTION/inputs/WORK_PLAN.json"):
        record_pin(returned, name, "return")
    for name in ("inputs/INPUT_INDEX.json", "analysis/RESOURCE_ALLOCATION.json", "code/parallel_batch.py", "code/off_path_worker.py"):
        record_pin(package, name, "original_package")
    path_rows, rank_rows, rank_intervals, job_intervals = [], [], [], []
    assigned_all = []
    class_times = defaultdict(list)
    per_path_pins = hashlib.sha256(b"bass-he-e13c8-performance-telemetry-v1\n")
    for rank in range(ranks):
        rank_relative = f"ranks/rank_{rank:04d}"
        rank_dir = batch_dir / rank_relative
        st = load(rank_dir / "START.json")
        rc = load(rank_dir / "RECEIPT.json")
        record_pin(batch_dir, rank_relative + "/START.json", "return/BATCH")
        record_pin(batch_dir, rank_relative + "/RECEIPT.json", "return/BATCH")
        assert rc == batch["rank_receipts"][rank]
        assigned = st["assigned_nodes"]
        assert assigned == manifest["schedule"]["shards"][rank] == rc["completed_nodes"] == rc["reserved_nodes"]
        assert len(assigned) == rc["reserved_path_calls"] == rc["validated_completed_path_calls"]
        assert rc["exit_code"] == 0 and rc["failure"] is None and not rc["unresolved_reserved_nodes"]
        assert st["rank"] == rc["rank"] == rank
        assert st["cpu_affinity"] == [manifest["rank_cpu_ids"][rank]] and st["thread_count"] == 1
        assert st["hostname"] == host["hostname"]
        assert st["address_space_bytes"] == 1 << 30
        assigned_all.extend(assigned)
        rank_start, rank_end = utc_us(st["utc"]), utc_us(rc["utc"])
        rank_intervals.append((rank_start, rank_end))
        elapsed_total, envelope_total = Fraction(), 0
        class_counts = Counter()
        previous_end = rank_start
        rank_paths = []
        for position, node in enumerate(assigned, 1):
            reserve_relative = rank_relative + f"/PATH_{node:06d}_RESERVED.json"
            progress_relative = rank_relative + f"/PROGRESS_{position:06d}.json"
            start_relative = f"paths/node_{node:06d}/START.json"
            completion_relative = f"paths/node_{node:06d}/COMPLETE.json"
            reserve, progress, path_start, complete = [load(batch_dir / rel) for rel in (reserve_relative, progress_relative, start_relative, completion_relative)]
            for rel in (reserve_relative, progress_relative, start_relative, completion_relative):
                item = {"relative_path": rel, **pin(batch_dir / rel)}
                per_path_pins.update(json.dumps(item, sort_keys=True, separators=(",", ":")).encode() + b"\n")
            summary = progress["summary"]
            assert summary == ordered[node]["summary"]
            assert {k: complete[k] for k in summary} == summary
            assert reserve["node"] == progress["node"] == summary["node"] == node
            assert reserve["rank"] == progress["rank"] == rank
            assert progress["completed_in_rank"] == position
            assert path_start["cpu_affinity"] == st["cpu_affinity"]
            assert path_start["automatic_retries"] == 0 and reserve["automatic_retry"] is False
            assert path_start["purpose"] == "ncp" and summary["N"] == 1024 and summary["precision"] == 60
            assert index[str(node)]["path_input_sha256"] == summary["path_input_sha256"]
            a, b = utc_us(reserve["utc"]), utc_us(progress["utc"])
            assert previous_end <= a <= utc_us(path_start["started_utc"]) <= b <= rank_end
            previous_end = b
            job_intervals.append((a, b))
            envelope_total += b - a
            dt = elapsed_fraction(summary["elapsed_seconds"])
            elapsed_total += dt
            active = int(index[str(node)]["active_species"])
            class_counts[active] += 1
            class_times[active].append(float(dt))
            row = {"node": node, "rank": rank, "active_species": active,
                   "path_reported_elapsed_seconds": float(dt),
                   "reservation_to_validation_progress_seconds": (b - a) / 1e6,
                   "reservation_utc": reserve["utc"], "validation_progress_utc": progress["utc"],
                   "rank_process_high_water_RSS_at_path_KiB": summary["peak_RSS_KiB"]}
            path_rows.append(row)
            rank_paths.append(row)
        rank_rows.append({"rank": rank, "cpu_id": st["cpu_affinity"][0], "thread_count": st["thread_count"],
                          "path_count": len(assigned), "active_species_counts": dict(sorted(class_counts.items())),
                          "rank_reported_elapsed_seconds": rc["elapsed_seconds"],
                          "rank_start_to_receipt_utc_seconds": (rank_end - rank_start) / 1e6,
                          "sum_path_reported_elapsed_seconds": float(elapsed_total),
                          "sum_reserved_to_progress_seconds": envelope_total / 1e6,
                          "rank_wall_minus_sum_path_wall_seconds": float(elapsed_fraction(rc["elapsed_seconds"]) - elapsed_total),
                          "rank_start_utc": st["utc"], "rank_receipt_utc": rc["utc"],
                          "peak_RSS_KiB": rc["peak_RSS_KiB"],
                          "max_path_high_water_RSS_KiB": max(row["rank_process_high_water_RSS_at_path_KiB"] for row in rank_paths),
                          "new_coefficient_evaluations": rc["new_coefficient_evaluations_from_validated_outputs"]})
    assert len(assigned_all) == len(set(assigned_all)) == 2331 and sorted(assigned_all) == nodes
    assert sorted(row["cpu_id"] for row in rank_rows) == list(range(64))
    assert sum(row["new_coefficient_evaluations"] for row in rank_rows) == 9547776
    assert all(row["peak_RSS_KiB"] >= row["max_path_high_water_RSS_KiB"] for row in rank_rows)
    ptime = distribution([row["path_reported_elapsed_seconds"] for row in path_rows])
    rtime = distribution([row["rank_reported_elapsed_seconds"] for row in rank_rows])
    rsums = distribution([row["sum_path_reported_elapsed_seconds"] for row in rank_rows])
    forecast_n1024 = next(row for row in forecast["scenarios"] if row["N"] == 1024)
    class_forecasts = {str(active): {"count": len(values), "parallel_observed_path_seconds": distribution(values),
                        "earlier_local_N1024_class_mean_seconds": forecast_n1024["class_local_seconds"][str(active)],
                        "earlier_NCP_class_mean_estimate_seconds": forecast_n1024["class_local_seconds"][str(active)] * forecast["same_work_host_calibration"]["ratio"],
                        "observed_parallel_mean_over_prior_NCP_estimate": statistics.mean(values) / (forecast_n1024["class_local_seconds"][str(active)] * forecast["same_work_host_calibration"]["ratio"])}
                       for active, values in sorted(class_times.items())}
    hypothetical = [(Fraction(), rank) for rank in range(ranks)]
    heapq.heapify(hypothetical)
    for row in sorted(path_rows, key=lambda item: (-item["path_reported_elapsed_seconds"], item["node"])):
        total, rank = heapq.heappop(hypothetical)
        heapq.heappush(hypothetical, (total + elapsed_fraction(row["path_reported_elapsed_seconds"]), rank))
    hypothetical_max = max(total for total, _ in hypothetical)
    result = {
      "schema": "bass-he-e13c8-actual-performance-v1",
      "scope": "one completed E13C7 N1024/P60 OFF batch; saved telemetry only; no kernel or benchmark replay",
      "provenance": {"provider_attestation": "NOT_ASSERTED", "host": host["hostname"],
                     "reported_visible_logical_CPUs": host["topology"]["logical_cpus"],
                     "reported_visible_physical_core_count": host["topology"]["physical_core_count"],
                     "hardware_provider_or_entitlement_attestation": "NOT_ASSERTED",
                     "topology_complete": host["topology"]["topology_complete"],
                     "python": host["python"], "platform": host["platform"], "open_mpi": host["open_mpi"],
                     "execution_lock_sha256": manifest["execution_lock_sha256"],
                     "return_collection_semantic_sha256": batch["collection_semantic_sha256"],
                     "per_path_telemetry_ordered_pin_sha256": per_path_pins.hexdigest(),
                     "per_path_telemetry_pin_file_count": len(path_rows) * 4,
                     "direct_evidence_pins": evidence},
      "work": {"rank_count": ranks, "computing_rank_count": sum(row["path_count"] > 0 for row in rank_rows),
               "controller_only_MPI_rank_count": 0, "observed_rank_CPU_ids": sorted(row["cpu_id"] for row in rank_rows),
               "single_thread_per_rank_verified_start_and_each_completed_path_in_locked_runtime": True,
               "paths": len(path_rows), "new_coefficient_evaluations": 9547776, "reused_paths": 0,
               "automatic_retries": 0, "per_rank_path_count_distribution": dict(sorted(Counter(row["path_count"] for row in rank_rows).items())),
               "per_active_species_path_counts": {str(k): len(v) for k, v in sorted(class_times.items())}},
      "wall_times": {"wrapper_attempt_seconds": attempt["elapsed_seconds"],
                     "controller_batch_seconds": execution["elapsed_seconds"],
                     "MPI_launcher_seconds": launcher["elapsed_seconds"],
                     "wrapper_attempt_minutes": attempt["elapsed_seconds"] / 60,
                     "controller_batch_minutes": execution["elapsed_seconds"] / 60,
                     "MPI_launcher_minutes": launcher["elapsed_seconds"] / 60,
                     "controller_outside_launcher_seconds": execution["elapsed_seconds"] - launcher["elapsed_seconds"],
                     "sum_parallel_path_elapsed_seconds": ptime["sum"],
                     "sum_parallel_path_elapsed_hours": ptime["sum"] / 3600,
                     "sum_parallel_path_time_is_measured_serial_runtime": False,
                     "path_elapsed_scope": "Context.run start through result timer capture; includes path input checks and enclosure computation; excludes subsequent comparison, serialization and completed-output validation",
                     "rank_elapsed_scope": "rank initialization through end of assigned path processing and validation; perf_counter, not process CPU time",
                     "per_path_seconds": ptime, "per_rank_seconds": rtime,
                     "per_rank_sum_path_seconds": rsums},
      "CPU_telemetry": {"process_user_system_CPU_seconds": "NOT_RECORDED", "CPU_time_over_wall_utilization": "NOT_MEASURED",
                        "cgroup_CPU_usage_and_throttling_delta": "NOT_RECORDED", "instantaneous_CPU_busy_samples": "NOT_RECORDED",
                        "measured_same_work_serial_speedup": "NOT_ESTABLISHED",
                        "reason": "locked worker and launcher record perf_counter and ru_maxrss, not ru_utime/ru_stime or cpu.stat deltas; task envelope overlap cannot replace CPU telemetry"},
      "task_envelope_accounting": {"rank_lifetime_UTC": occupancy(rank_intervals, ranks),
                                   "path_reservation_through_validation_UTC": occupancy(job_intervals, ranks),
                                   "sum_path_perf_counter_over_64_launcher_wall": ratio(ptime["sum"], ranks * launcher["elapsed_seconds"]),
                                   "sum_path_perf_counter_over_64_controller_wall": ratio(ptime["sum"], ranks * execution["elapsed_seconds"]),
                                   "claim_ceiling": "elapsed-work coverage only; not measured CPU utilization or parallel efficiency"},
      "balance": {"rank_wall_max_minus_min_seconds": rtime["max"] - rtime["min"],
                  "rank_wall_mean_over_max": ratio(rtime["mean"], rtime["max"]),
                  "rank_path_sum_mean_over_max": ratio(rsums["mean"], rsums["max"]),
                  "max_rank_wall_minus_mean_seconds": rtime["max"] - rtime["mean"],
                  "mean_rank_wall_minus_sum_path_wall_seconds": statistics.mean(row["rank_wall_minus_sum_path_wall_seconds"] for row in rank_rows),
                  "retrospective_fixed_duration_LPT": {"status": "OFFLINE_ARITHMETIC_NOT_EXECUTED_SCHEDULE",
                       "assumption": "each path keeps the elapsed duration observed under the actual 64-rank execution, ignores changed contention and rank overhead",
                       "observed_shard_max_sum_path_seconds": rsums["max"],
                       "hypothetical_max_sum_path_seconds": float(hypothetical_max),
                       "possible_shard_tail_reduction_seconds_under_assumption": rsums["max"] - float(hypothetical_max),
                       "fraction_of_observed_controller_wall": (rsums["max"] - float(hypothetical_max)) / execution["elapsed_seconds"]},
                  "claim_ceiling": "load balance of wall-accounted work, no serial speedup inference"},
      "memory": {"per_rank_peak_RSS_KiB": distribution([row["peak_RSS_KiB"] for row in rank_rows]),
                 "sum_rank_individual_high_water_RSS_KiB": sum(row["peak_RSS_KiB"] for row in rank_rows),
                 "sum_rank_individual_high_water_RSS_GiB": sum(row["peak_RSS_KiB"] for row in rank_rows) / 2**20,
                 "controller_peak_RSS_KiB": execution["controller_peak_RSS_KiB"],
                 "sum_rank_plus_controller_individual_high_water_RSS_GiB": (sum(row["peak_RSS_KiB"] for row in rank_rows) + execution["controller_peak_RSS_KiB"]) / 2**20,
                 "simultaneous_global_peak_RSS": "NOT_MEASURED",
                 "high_water_sum_semantics": "sum of different processes' lifetime RSS maxima, with shared pages potentially counted repeatedly; excludes MPI daemons, wrapper, page cache and unrelated processes; not a simultaneous or machine-wide memory measurement",
                 "path_RSS_semantics": "same rank process is reused across paths, so per-path ru_maxrss is cumulative process high-water and must not be summed over 2331 paths",
                 "rank_address_space_limit_bytes": 1 << 30,
                 "preflight_host_MemTotal_bytes": host["host_memory_bytes"]["MemTotal"],
                 "preflight_host_MemAvailable_bytes": host["host_memory_bytes"]["MemAvailable"],
                 "preflight_reserved_memory_bytes": host["reserved_memory_bytes"],
                 "earlier_64_times_local_max_RSS_GiB_scenario": forecast["64_times_max_local_RSS_GiB_scenario"],
                 "memory_fill_goal": False},
      "forecast_comparison": {"original_N1024_forecast": forecast_n1024,
                 "observed_controller_minutes": execution["elapsed_seconds"] / 60,
                 "controller_over_80_percent_scenario": ratio(execution["elapsed_seconds"] / 60, forecast_n1024["64_rank_80_percent_efficiency_minutes_scenario"]),
                 "controller_over_ideal_64_scenario": ratio(execution["elapsed_seconds"] / 60, forecast_n1024["ideal_64_computing_rank_minutes_estimate"]),
                 "observed_parallel_path_elapsed_sum_over_estimated_single_worker_work": ratio(ptime["sum"], forecast_n1024["recorded_NCP_single_worker_equivalent_seconds_estimate"]),
                 "per_class": class_forecasts,
                 "claim_ceiling": "forecast residual, not an empirical parallel efficiency or serial runtime measurement; old four-HI-path host calibration did not measure the actual full batch serially"},
      "recommendations": ["Completed 2331 paths must not be replayed for a benchmark or as another refinement batch without a new scientific gate.",
          "All 64 ranks performed scientific paths; no MPI rank was reserved only as a controller. Saved task envelopes support broad concurrent activity, while actual CPU utilization remains unmeasured.",
          "Existing static LPT distribution already has modest tail imbalance; compare quantified tail headroom with engineering and validation cost before adding dynamic scheduling.",
          "Use actual completed per-node or per-class timings to plan a scientifically necessary future batch, with explicit warning that different N, geometry, load and contention change costs.",
          "If a new useful heavy batch is approved, add low-overhead process user/system CPU-time deltas and start/end memory/cgroup observations to that new run instead of launching a calibration replay.",
          "Do not fill 128 GB artificially or reserve memory based on a sum of 2331 per-path ru_maxrss values; these values repeat the same 64 processes' high-water marks."]}
    result["per_rank"] = rank_rows
    result["per_path"] = sorted(path_rows, key=lambda row: row["node"])
    result["analysis_execution"] = {"actual_analysis_wall_seconds_before_serialization": time.perf_counter() - start_clock,
             "scientific_kernel_calls": 0, "MPI_launches": 0, "benchmark_replays": 0,
             "argv": sys.argv, "python": sys.version, "script": pin(Path(__file__))}
    write_new(out / "PERFORMANCE_ANALYSIS.json", result)
    mem = result["memory"]
    occ = result["task_envelope_accounting"]["path_reservation_through_validation_UTC"]
    notes = f"""# E13C8 실제 병렬 실행 성능 분석

## 결론

2,331개 OFF 경로의 N1024/P60 계산은 64개 MPI rank에서 실제로 완료되었다. 전체 controller wall은 **{execution['elapsed_seconds']/60:.6f}분**, MPI launcher wall은 **{launcher['elapsed_seconds']/60:.6f}분**이다. 64개 rank 전부 과학 경로를 계산했으며 각 rank가 CPU 0–63 중 하나에 고정되었다. MPI rank 하나를 controller 전용으로 비워 두지 않았다. [원자료: `BATCH/EXECUTION_RECEIPT.json`, `BATCH/LAUNCH_PROCESS_RECEIPT.json`, `BATCH/ranks/rank_*/START.json`, `BATCH/ranks/rank_*/RECEIPT.json`]

## 실제 관측과 계산한 비율

| 항목 | 실제 결과 |
|---|---:|
| 새 경로 / 계수 평가 | 2,331 / 9,547,776 |
| rank당 경로 수 | {min(row['path_count'] for row in rank_rows)}–{max(row['path_count'] for row in rank_rows)} |
| rank wall 최솟값 / 최댓값 | {rtime['min']:.6f} / {rtime['max']:.6f} s |
| rank wall 평균 / 최댓값 | {rtime['mean']/rtime['max']*100:.6f}% |
| 모든 경로의 보고된 wall 합계 | {ptime['sum']:.6f} s ({ptime['sum']/3600:.6f} h) |
| 예약부터 완료 검증까지의 동시 경로 수 평균 | {occ['mean_simultaneous_envelopes']['ratio']:.6f} |
| 64개 경로 예약 구간이 겹친 시간 | {occ['seconds_at_all_slots']:.6f} s |
| controller에서 launcher 밖에 쓴 시간 | {execution['elapsed_seconds']-launcher['elapsed_seconds']:.6f} s |

각 경로의 wall 합계는 **동일 작업의 직렬 실행시간이 아니다**. 경로 실행 중의 대기·스케줄링·I/O·64-rank 환경의 경쟁이 포함된다. UTC 예약→검증 완료 구간이 겹쳤다는 사실 역시 CPU가 실제로 바빴다는 샘플이 아니다. 저장된 runtime은 `perf_counter`와 `ru_maxrss`를 기록하며, user/system CPU-time이나 `cpu.stat` 변화량을 기록하지 않았다. 따라서 **CPU 이용률과 같은 작업의 직렬 대비 speedup은 NOT_MEASURED/NOT_ESTABLISHED**다. [원자료: 잠긴 `code/off_path_worker.py`, `code/parallel_batch.py`; 직접 계산: `PERFORMANCE_ANALYSIS.json`]

## 부하 분산과 예측 오차

rank wall의 최대−최소 차이는 {rtime['max']-rtime['min']:.6f} s다. 실제 관측된 각 경로의 시간을 고정해 다시 분배하는 사후 산술 LPT 모형에서는 가장 긴 shard의 경로시간 합계가 {rsums['max']:.6f} s에서 {float(hypothetical_max):.6f} s로 줄어든다. 가능한 차이 {rsums['max']-float(hypothetical_max):.6f} s는 실제 controller wall의 {(rsums['max']-float(hypothetical_max))/execution['elapsed_seconds']*100:.6f}%다. 이 값은 실행한 새 scheduler의 성능이 아니라, 경로시간이 재배치 후에도 같다고 가정한 사후 계산이다. 현재 자료는 동적 scheduler로 전면 교체할 큰 이득을 보여 주지 않는다. [원자료 및 계산: `PERFORMANCE_ANALYSIS.json#/balance`, `#/per_rank`, `#/per_path`]

기존 N1024 예측은 이상적인 64-rank {forecast_n1024['ideal_64_computing_rank_minutes_estimate']:.6f}분, 가정한 80% 시나리오 {forecast_n1024['64_rank_80_percent_efficiency_minutes_scenario']:.6f}분, 50% 시나리오 {forecast_n1024['64_rank_50_percent_efficiency_minutes_scenario']:.6f}분이었다. 실제 {execution['elapsed_seconds']/60:.6f}분은 80% 시나리오보다 {(execution['elapsed_seconds']/60/forecast_n1024['64_rank_80_percent_efficiency_minutes_scenario']-1)*100:.6f}% 길며, 두 시나리오 사이에 있다. 이것은 **예측 오차 비교**이며 측정한 병렬 효율로 이름 붙이지 않는다. 각 종 수별 실제 64-rank 경로시간 평균은 JSON에 별도로 보존했다. [원자료: E13C7 `analysis/RESOURCE_ALLOCATION.json`; 실제 실행 영수증]

## 메모리

rank별 lifetime 최대 RSS 중 가장 큰 값은 {mem['per_rank_peak_RSS_KiB']['max']} KiB이다. 64개 rank 각각의 최대 RSS를 합하면 **{mem['sum_rank_individual_high_water_RSS_GiB']:.6f} GiB**, controller의 개별 최대 RSS까지 합하면 **{mem['sum_rank_plus_controller_individual_high_water_RSS_GiB']:.6f} GiB**다. 이 합은 시점이 서로 다른 최대값의 합이며, 공유 페이지 중복 집계 가능성이 있고 MPI daemon·wrapper·page cache·다른 프로세스는 포함하지 않는다. 따라서 실제 동시 전체 메모리 peak로 표기할 수 없다. 경로별 `ru_maxrss`는 같은 rank 프로세스의 누적 최대값이므로 2,331개 값을 합하면 잘못된 수치가 된다. [원자료: rank 및 controller receipt; 메서드: 잠긴 runtime의 `resource.getrusage(RUSAGE_SELF).ru_maxrss`]

이번 작업은 메모리 용량이 주된 병목이라는 증거가 없다. 128 GB를 채우려는 계산은 추가하지 않는다. 64개 계산 rank와 작고 균형 잡힌 tail을 사용한 이번 중량 실행을 마친 뒤, 다음 과학적 판단과 경량 합산을 여기서 처리하는 것이 사용자 정책에 맞는다. 새로 필요한 중량 작업이 생기면 이번 실제 시간 분포로 계획하고, 그 작업에 저비용 CPU-time 관측을 함께 기록하면 된다. 이미 끝난 경로를 성능 측정만을 위해 반복할 이유는 없다.

## 재현 범위

이 분석은 실제 저장한 JSON만 읽었다. 과학 커널 호출, MPI 실행, benchmark replay는 모두 **0**이다. 입력 identity와 64개 rank 및 2,331개 경로의 연결을 검사하고, UTC 겹침의 sweep 합계가 각 구간 길이의 직접 합과 일치함을 확인했다. 비율의 exact 필드는 관측 파일에 기록된 십진 시간값의 정확한 비율이며 물리적 시간 측정의 무한 정밀도를 뜻하지 않는다. Provider attestation은 **NOT_ASSERTED**다. 입력 pin과 재현 명령은 `PERFORMANCE_ANALYSIS.json#/provenance`와 `#/analysis_execution`에 있다.
"""
    write_new(out / "PERFORMANCE_NOTES_KO.md", notes)
    write_new(out / "PERFORMANCE_IDENTITY.json", {"schema": "bass-he-e13c8-performance-identity-v1",
              "source_script": pin(Path(__file__)),
              "files": {name: pin(out / name) for name in ("PERFORMANCE_ANALYSIS.json", "PERFORMANCE_NOTES_KO.md")},
              "completed_analysis_wall_seconds": time.perf_counter() - start_clock,
              "scientific_kernel_calls": 0, "MPI_launches": 0, "actual_exit": 0})
    print(json.dumps({"status": "COMPLETE_SAVED_TELEMETRY_ANALYSIS", "paths": len(path_rows), "ranks": ranks,
                      "controller_minutes": execution["elapsed_seconds"] / 60,
                      "CPU_utilization": "NOT_MEASURED", "serial_speedup": "NOT_ESTABLISHED",
                      "analysis_wall_seconds": time.perf_counter() - start_clock, "output_dir": str(out)}, sort_keys=True))


if __name__ == "__main__":
    main()
