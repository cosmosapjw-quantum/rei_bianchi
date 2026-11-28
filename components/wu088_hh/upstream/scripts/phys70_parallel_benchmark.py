#!/usr/bin/env python3
"""Bounded independent-trajectory Rayon comparison, with immutable evidence.

Four performance requests, one batch each at 1, 2 and 4 threads. This measures
new thread configurations; it never starts a historical production campaign.
One sample per configuration is a parity/scaling probe, not a timing statistic.
The default is a read-only preflight. No existing output is overwritten.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
import os
from pathlib import Path
import struct
import sys

import phys69_vigilode as reference
import phys70_ncp as runner

ROOT = Path(__file__).resolve().parents[1]


def bits(states: list[list[float]]) -> bytes:
    return b"".join(struct.pack("!d", x) for row in states for x in row)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    binary = args.binary.resolve()
    seed, source, cert = reference.DEFAULT_SEED, reference.DEFAULT_SOURCE, reference.DEFAULT_CERT
    for path, expected in [(seed, reference.SEED_L28_SHA), (source, reference.SOURCE_SHA),
                           (cert, reference.CERT_SHA)]:
        if runner.sha(path) != expected:
            raise ValueError(f"inherited immutable input mismatch: {path}")
    identity = {"binary_sha256": runner.binary_digest(binary),
                "engine_files_sha256": runner.engine_identity(),
                "benchmark_script_sha256": runner.sha(Path(__file__)),
                "seed_sha256": runner.sha(seed), "source_sha256": runner.sha(source),
                "reference_certificate_sha256": runner.sha(cert),
                "runtime": runner.runtime_record()}
    base = reference.read(ROOT / "research/hh_phys69_20261019/vigilode/REQUEST_L28.json")
    requests = [{"schema": "PHYS70_OPTIMIZED_REQUEST_V1", "engine": "block_simd",
                 "physics_request": {**base, "rtol": rtol, "atol": rtol / 100}, "HH_R10": "OFF"}
                for rtol in (3e-9, 3e-10, 3e-11, 3e-12)]
    for request in requests:
        runner.validate_request(request)
    if not args.run:
        print(json.dumps({"status": "READY_NOT_RUN", "identity": identity,
                          "threads": [1, 2, 4], "jobs_per_batch": 4,
                          "new_integrations": 0, "HH_R10": "OFF"}, indent=2))
        return 0
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    runner.create_json(out / "IDENTITY.json", identity)
    request_path = out / "REQUEST_LIST.json"
    runner.create_bytes(request_path, (json.dumps(requests, indent=2, allow_nan=False) + "\n").encode())
    env = {**os.environ, **runner.THREAD_ENV}
    rows, reference_bits = [], None
    for threads in (1, 2, 4):
        directory = out / f"threads_{threads}"
        directory.mkdir()
        command = [str(binary), "batch", str(request_path), str(seed), str(source), str(threads)]
        execution = runner.execute(command, directory, "BATCH", env, 60, 4)
        if execution.get("exit_code") != 0 or execution.get("timed_out") is not False:
            raise RuntimeError(f"partial batch preserved: {directory}")
        raw = (directory / "BATCH.stdout.txt").read_bytes()
        runner.create_bytes(directory / "RESULT.json", raw)
        result = runner.decode(raw)
        if (result.get("schema") != "PHYS70_INDEPENDENT_BATCH_V1" or result.get("complete") is not True
                or result.get("threads") != threads or result.get("requests") != 4
                or result.get("request_list_sha256") != runner.sha(request_path)
                or result.get("ordered_results") is not True or result.get("parallel_radial_carry") is not False
                or result.get("HH_R10") != "OFF" or len(result.get("results", [])) != 4):
            raise ValueError("native batch completion/order/identity mismatch")
        states, checks = [], []
        for index, (request, item) in enumerate(zip(requests, result["results"])):
            # Native per-item digests name serde_json's canonical serialization,
            # while the exact input list bytes are independently pinned above.
            digest = item.get("request_sha256", "")
            if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
                raise ValueError("invalid canonical per-request digest")
            runner.validate_result(item, request, digest, identity["seed_sha256"])
            goal = Fraction(str(request["physics_request"]["rtol"]))
            check = reference.compare_certificate({**item, "request": request["physics_request"]},
                                                  cert, relative_goal=goal)
            runner.create_json(directory / f"POINT_ERROR_{index}.json", check)
            if check.get("goal_met") is not True:
                raise ValueError(f"stored endpoint misses requested comparison goal: {threads}/{index}")
            error = check["relative_error_upper"]
            checks.append({"job": index, "rtol": float(goal),
                           "true_relative_error_upper": float(Fraction(int(error["numerator"]), int(error["denominator"]))),
                           "accepted_steps": item["accepted_steps"], "rejected_steps": item["rejected_steps"],
                           "integration_elapsed_seconds": item["integration_elapsed_seconds"]})
            states.append(bits(item["observed_states_scaled"]))
        if reference_bits is None:
            reference_bits = states
        if states != reference_bits:
            raise ValueError("independent thread configurations changed state bits or output order")
        runner.create_json(directory / "CHECKSUMS.json", {"files": runner.payload_hashes(directory)})
        rows.append({"threads": threads, "batch_seconds": result["wall_seconds"],
                     "process_wall_seconds": execution["elapsed_seconds"],
                     "all_state_bits_equal_to_threads_1": True, "jobs": checks,
                     "result_sha256": runner.sha(directory / "RESULT.json")})
    for row in rows:
        row["speedup_vs_threads_1"] = rows[0]["batch_seconds"] / row["batch_seconds"]
    summary = {"schema": "PHYS70_PARALLEL_TRAJECTORY_SUMMARY_V1", "status": "PASS_SCOPED",
               "rows": rows, "new_performance_integrations": 12, "old_completed_campaign_replays": 0,
               "samples_per_thread_configuration": 1,
               "timing_scope": "native batch after pool construction; process wall retained separately",
               "parallel_axis": "independent complete trajectories; sequential radial carry per job",
               "numerical_scope": "stored finite-L28 D2 point comparisons, not a uniform integrator certificate",
               "HH_R10": "OFF"}
    runner.create_json(out / "SUMMARY.json", summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
