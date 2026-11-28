#!/usr/bin/env python3
"""New same-host work/precision experiment; immutable PHYS69 science is reused.

Two NEW tolerance pairs and all three engines share one binary, input and host.
Three alternating samples quantify timing variability. --resume only reads
completed samples with matching code/binary/input identities. Never overwrites.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
import phys69_vigilode as reference

ROOT = Path(__file__).resolve().parents[1]

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_new(path: Path, obj: dict) -> None:
    with path.open("x") as stream:
        json.dump(obj, stream, indent=2, allow_nan=False)
        stream.write("\n")

def source_identity() -> dict:
    paths = []
    for crate in ["phys69_vigilode", "phys70_optimized"]:
        paths += [ROOT / f"native/{crate}/Cargo.toml", ROOT / f"native/{crate}/Cargo.lock"]
        paths += sorted((ROOT / f"native/{crate}/src").glob("*.rs"))
    paths += [Path(__file__).resolve(), ROOT / "scripts/phys69_vigilode.py"]
    return {str(p.relative_to(ROOT)): sha(p) for p in paths}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    if not 1 <= args.timeout <= 900:
        raise ValueError("bounded timeout 1..900 seconds required")
    binary = args.binary.resolve()
    seed, source, cert = reference.DEFAULT_SEED, reference.DEFAULT_SOURCE, reference.DEFAULT_CERT
    for path, expected in [(source, reference.SOURCE_SHA), (seed, reference.SEED_L28_SHA), (cert, reference.CERT_SHA)]:
        if sha(path) != expected:
            raise ValueError(f"immutable input mismatch: {path}")
    identity = {"binary_sha256": sha(binary), "source_pins": source_identity(),
                "seed_sha256": sha(seed), "frozen_source_sha256": sha(source), "certificate_sha256": sha(cert),
                "platform": platform.platform(), "python": platform.python_version(),
                "cpu_affinity": sorted(os.sched_getaffinity(0)),
                "cpu_quota": Path("/sys/fs/cgroup/cpu.max").read_text().strip() if Path("/sys/fs/cgroup/cpu.max").exists() else None,
                "environment_flags": {k: os.environ.get(k) for k in ["RUSTFLAGS", "RAYON_NUM_THREADS", "OMP_NUM_THREADS"]}}
    if not args.run:
        print(json.dumps({"status": "READY_NOT_RUN", "identity": identity, "new_performance_integrations": 0, "HH_R10": "OFF"}, indent=2))
        return 0
    args.out.mkdir(parents=True, exist_ok=True)
    identity_path = args.out / "IDENTITY.json"
    if identity_path.exists():
        if not args.resume or json.loads(identity_path.read_text()) != identity:
            raise ValueError("existing performance output needs exact identity --resume")
    else:
        write_new(identity_path, identity)
    base = reference.read(ROOT / "research/hh_phys69_20261019/vigilode/REQUEST_L28.json")
    rows, new_runs, reused = [], 0, 0
    for rtol, atol in [(3e-10, 3e-12), (3e-12, 3e-14)]:
        physics = {**base, "rtol": rtol, "atol": atol}
        for sample in range(3):
            engines = ["legacy_gmres", "block_scalar", "block_simd"]
            if sample % 2:
                engines.reverse()
            for engine in engines:
                directory = args.out / f"rtol_{rtol:.0e}_{engine}_sample{sample}"
                request = {"schema": "PHYS70_OPTIMIZED_REQUEST_V1", "engine": engine,
                           "physics_request": physics, "HH_R10": "OFF"}
                if directory.exists():
                    if not args.resume:
                        raise FileExistsError(directory)
                    receipt = json.loads((directory / "EXECUTION.json").read_text())
                    for name, expected in receipt["files_sha256"].items():
                        if sha(directory / name) != expected:
                            raise ValueError(f"saved sample changed: {name}")
                    if json.loads((directory / "REQUEST.json").read_text()) != request or receipt["returncode"] != 0:
                        raise ValueError("incomplete or mismatched sample cannot be reused")
                    reused += 1
                else:
                    directory.mkdir()
                    write_new(directory / "REQUEST.json", request)
                    command = [str(binary), "run", str((directory / "REQUEST.json").resolve()), str(seed), str(source)]
                    started = datetime.now(timezone.utc).isoformat()
                    clock = time.perf_counter()
                    with (directory / "RESULT.json").open("xb") as stdout, (directory / "STDERR.txt").open("xb") as stderr:
                        try:
                            result = subprocess.run(command, stdout=stdout, stderr=stderr, timeout=args.timeout, check=False)
                            returncode, status = result.returncode, "RETURNED"
                        except subprocess.TimeoutExpired:
                            returncode, status = None, "TIMEOUT_KILLED"
                    receipt = {"schema": "PHYS70_BENCHMARK_SAMPLE_EXECUTION_V1", "command": command,
                               "started_utc": started, "wall_seconds": time.perf_counter() - clock,
                               "returncode": returncode, "status": status,
                               "binary_sha256": identity["binary_sha256"],
                               "files_sha256": {name: sha(directory / name) for name in ["REQUEST.json", "RESULT.json", "STDERR.txt"]}}
                    write_new(directory / "EXECUTION.json", receipt)
                    new_runs += 1
                    if returncode != 0:
                        raise RuntimeError(f"failed sample preserved: {directory}")
                value = json.loads((directory / "RESULT.json").read_text())
                if value.get("complete") is not True or value.get("request") != request or value.get("request_sha256") != sha(directory / "REQUEST.json"):
                    raise ValueError("native completion/request mismatch")
                for key, expected in [("source_sha256", identity["frozen_source_sha256"]), ("seed_sha256", identity["seed_sha256"]),
                                      ("HH_R10", "OFF"), ("observed_times_tau", [0.0, 38.0]), ("engine", engine)]:
                    if value.get(key) != expected:
                        raise ValueError(f"native identity mismatch {key}")
                reference_input = {**value, "request": physics}
                comparison = reference.compare_certificate(reference_input, cert, Fraction(str(rtol)))
                if not comparison["goal_met"]:
                    raise ValueError(f"unchanged stored-point accuracy goal failed: {directory}")
                comparison_path = directory / "POINT_ERROR.json"
                if comparison_path.exists():
                    if json.loads(comparison_path.read_text()) != comparison:
                        raise ValueError("saved exact point-error comparison changed")
                else:
                    write_new(comparison_path, comparison)
                row = {"rtol": rtol, "atol": atol, "sample": sample, "engine": engine,
                       "elapsed_seconds": value["integration_elapsed_seconds"], "process_wall_seconds": receipt["wall_seconds"],
                       "accepted_steps": value["accepted_steps"], "rejected_steps": value["rejected_steps"],
                       "true_relative_error_upper": float(Fraction(int(comparison["relative_error_upper"]["numerator"]), int(comparison["relative_error_upper"]["denominator"]))),
                       "result_sha256": sha(directory / "RESULT.json"), "result_path": str((directory / "RESULT.json").relative_to(args.out)),
                       "counters": value["counters"], "implementation": value["implementation"]}
                rows.append(row)
                print(json.dumps({k: row[k] for k in ["rtol", "sample", "engine", "elapsed_seconds", "accepted_steps", "true_relative_error_upper"]}), flush=True)
    groups = []
    for rtol in [3e-10, 3e-12]:
        selected = [r for r in rows if r["rtol"] == rtol]
        medians = {e: statistics.median(r["elapsed_seconds"] for r in selected if r["engine"] == e) for e in ["legacy_gmres", "block_scalar", "block_simd"]}
        groups.append({"rtol": rtol, "median_seconds": medians,
                       "legacy_over_block_scalar": medians["legacy_gmres"] / medians["block_scalar"],
                       "legacy_over_block_simd": medians["legacy_gmres"] / medians["block_simd"],
                       "block_scalar_over_simd": medians["block_scalar"] / medians["block_simd"]})
    summary = {"schema": "PHYS70_WORK_PRECISION_V1", "status": "PASS_ALL_STORED_POINT_GOALS",
               "rows": rows, "groups": groups, "new_integrations_this_invocation": new_runs,
               "samples_reused_this_invocation": reused, "old_completed_scientific_campaigns_replayed": 0,
               "full_integrator_certificate": False, "performance_scope": "same binary and host, three new paired samples; not NCP timing", "HH_R10": "OFF"}
    summary_path = args.out / "SUMMARY.json"
    if not summary_path.exists():
        write_new(summary_path, summary)
    print(json.dumps({"groups": groups, "new_integrations": new_runs, "reused": reused}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
