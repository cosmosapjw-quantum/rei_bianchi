"""Repeat an identical manifest across bounded layouts; never change defaults."""
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import signal
import statistics
import subprocess
import sys
import time

from host_probe import probe_host
from launch_ncp import validate_layout
from mpi_batch import atomic_create, json_bytes, read_manifest

PARITY_TOLERANCE = 2e-10


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--layouts", default="1x1,8x1,16x1,32x1,64x1,32x2,16x4")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--job-timeout-seconds", type=float, required=True)
    ap.add_argument("--backend", choices=("native", "numpy", "reference"), required=True)
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--mpirun", default="mpirun")
    ap.add_argument("--execute", action="store_true")
    a = ap.parse_args(argv)
    if a.repeats < 3 or not math.isfinite(a.job_timeout_seconds) or a.job_timeout_seconds <= 0:
        ap.error("repeats >=3 and finite positive job timeout required")
    try:
        layouts = [tuple(map(int, item.split("x"))) for item in a.layouts.split(",")]
        if any(len(x) != 2 or min(x) <= 0 for x in layouts) or len(set(layouts)) != len(layouts) or (1, 1) not in layouts:
            raise ValueError()
    except ValueError:
        ap.error("layouts must be unique positive RxT entries including 1x1")
    layouts = [(1, 1)] + [x for x in layouts if x != (1, 1)]
    python = shutil.which(a.python)
    if python is None:
        ap.error("Python executable not found")
    manifest, manifest_sha, raw = read_manifest(a.manifest)
    out, host, entries = Path(a.output_dir).resolve(), probe_host(), []
    if out.exists():
        raise FileExistsError("benchmark output must be new")
    for ranks, threads in layouts:
        entry = {"layout": f"{ranks}x{threads}", "ranks": ranks, "threads": threads, "runs": []}
        try:
            entry["resource_contract"] = validate_layout(host, ranks, threads, manifest["limits"]["per_worker_memory_gib"])
            entry["status"] = "PLANNED"
        except ValueError as error:
            entry.update(status="REJECTED_HOST_CAP", error=str(error))
        entries.append(entry)
    report = {"schema": 1, "action": "EXECUTED" if a.execute else "PLAN_ONLY_NOT_EXECUTED", "manifest_sha256": manifest_sha,
              "backend": a.backend, "repeats": a.repeats, "host": host, "layouts": entries,
              "parity_absolute_tolerance": PARITY_TOLERANCE, "state_mass_L2": "NOT_CHECKED_NO_STABLE_MASS_IN_ARTIFACT",
              "timing": "MPI_BATCH_WALL_IDENTICAL_TASK_SET; launcher/process startup also recorded separately",
              "warmup": "NONE_SEPARATE; all fresh-process runs included", "production_default_changed": False}
    if not a.execute:
        print(json.dumps(report, indent=2)); return 0
    out.mkdir(parents=True, exist_ok=False)
    pinned = out / "MANIFEST_INPUT.json"
    atomic_create(pinned, raw)
    atomic_create(out / "BENCHMARK_PLAN.json", json_bytes(report))
    baseline, baseline_code, baseline_backend = None, None, None
    for entry in entries:
        if entry["status"] != "PLANNED":
            continue
        folder = out / entry["layout"]
        folder.mkdir()
        for repeat in range(a.repeats):
            destination = folder / f"repeat_{repeat + 1:02d}"
            command = [python, str(Path(__file__).with_name("launch_ncp.py")), "--manifest", str(pinned),
                       "--output-dir", str(destination), "--backend", a.backend, "--ranks", str(entry["ranks"]),
                       "--threads", str(entry["threads"]), "--python", python, "--mpirun", a.mpirun, "--execute"]
            run = {"repeat": repeat + 1, "command_argv": command, "status": "FAILED"}
            started, process = time.monotonic(), None
            try:
                with (folder / f"repeat_{repeat + 1:02d}.log").open("xb") as log:
                    process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                    try:
                        run["returncode"] = process.wait(timeout=a.job_timeout_seconds)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL); process.wait()
                        raise RuntimeError("WHOLE_JOB_TIMEOUT")
                    log.flush(); os.fsync(log.fileno())
                if run["returncode"] != 0:
                    raise RuntimeError("LAUNCHER_OR_TASK_FAILURE")
                batch = json.loads((destination / "BATCH_SUMMARY.json").read_bytes())
                if batch["status"] != "ALL_WORKER_RESULTS_PASS" or batch["manifest_sha256"] != manifest_sha:
                    raise RuntimeError("BATCH_IDENTITY_OR_STATUS_MISMATCH")
                current = {task["task_id"]: json.loads((destination / task["task_id"] / "RESULT.json").read_bytes()) for task in manifest["tasks"]}
                selected = json.loads((destination / "RUN_IDENTITY.json").read_bytes())["selected_backend"]
                if any(not math.isfinite(float(row[field])) for row in current.values() for field in ("energy", "residual", "mass_norm")):
                    raise RuntimeError("NONFINITE_WORKER_RESULT")
                if baseline is None:
                    if entry["layout"] != "1x1":
                        raise RuntimeError("NO_PASSING_1x1_BASELINE")
                    baseline, baseline_code, baseline_backend = current, batch["code_sha256"], selected
                if batch["code_sha256"] != baseline_code or selected != baseline_backend:
                    raise RuntimeError("CODE_OR_BACKEND_CHANGED_BETWEEN_LAYOUTS")
                deltas = {field: max(abs(float(row[field]) - float(baseline[key][field])) for key, row in current.items()) for field in ("energy", "residual", "mass_norm")}
                if any(not math.isfinite(x) or x > PARITY_TOLERANCE for x in deltas.values()):
                    raise RuntimeError("BASELINE_NUMERICAL_PARITY_FAILED")
                if any(row["status"] != "PASS" or row["backend"] != a.backend or row["input_sha256"] != baseline[key]["input_sha256"] or row["residual"] > 1e-9 or abs(row["mass_norm"] - 1) > 1e-10 for key, row in current.items()):
                    raise RuntimeError("WORKER_IDENTITY_OR_FIXED_TOLERANCE_FAILED")
                wall = float(batch["wall_seconds"])
                if not math.isfinite(wall) or wall <= 0:
                    raise RuntimeError("INVALID_BATCH_TIME")
                run.update(status="PASS", batch_wall_seconds=wall, max_absolute_deltas=deltas,
                           max_worker_rss_kib=max(row["max_rss_kib"] for row in current.values()))
            except Exception as error:
                run["error"] = f"{type(error).__name__}: {error}"
                if process is not None and process.poll() is None:
                    os.killpg(process.pid, signal.SIGKILL); process.wait()
            run["whole_job_wall_seconds"] = time.monotonic() - started
            entry["runs"].append(run)
            atomic_create(folder / f"repeat_{repeat + 1:02d}_execution.json", json_bytes(run))
        entry["status"] = "PASS" if all(run["status"] == "PASS" for run in entry["runs"]) else "REJECTED_RUN_FAILURE"
        if entry["status"] == "PASS":
            times = [run["batch_wall_seconds"] for run in entry["runs"]]
            entry.update(median_batch_seconds=statistics.median(times), range_batch_seconds=[min(times), max(times)], throughput_tasks_per_second=len(manifest["tasks"]) / statistics.median(times))
    passing = [entry for entry in entries if entry["status"] == "PASS"] if entries[0]["status"] == "PASS" else []
    for entry in passing:
        entry["speedup_vs_1x1"] = entries[0]["median_batch_seconds"] / entry["median_batch_seconds"]
    report["recommended_layout_from_measured_data"] = min(passing, key=lambda entry: entry["median_batch_seconds"])["layout"] if passing else None
    report["status"] = "MEASURED_RECOMMENDATION_AVAILABLE" if passing else "NO_VALID_BASELINE_OR_LAYOUT"
    atomic_create(out / "BENCHMARK_SUMMARY.json", json_bytes(report))
    print(json.dumps(report, indent=2))
    return 0 if passing and all(entry["status"] in ("PASS", "REJECTED_HOST_CAP") for entry in entries) else 1


if __name__ == "__main__":
    raise SystemExit(main())
