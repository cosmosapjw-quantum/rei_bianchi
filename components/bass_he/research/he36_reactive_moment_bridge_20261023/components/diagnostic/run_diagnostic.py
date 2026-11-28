#!/usr/bin/env python3
"""Bounded, finite-source CCC moment diagnostic; never an IVP.

Run once with OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1.
Verified completed outputs are reused rather than replayed.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import resource
import sys
import tempfile
import time
import traceback

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "vendor"))
from maxwellian_moments import (A0_M, EV_J, KB_J_K, ME_KG,
                               PreparedMaxwellianMoments)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def atomic_write(path, content):
    """Publish complete bytes with fsync; never replace an existing attempt."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(path)
    data = content.encode() if isinstance(content, str) else content
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        # link fails if another invocation already completed this filename.
        os.link(temp, path)
        os.unlink(temp)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def write_json(path, value):
    atomic_write(path, json.dumps(value, indent=2, sort_keys=True,
                                 ensure_ascii=False, allow_nan=False) + "\n")


def environment():
    info = {
        "python": sys.version, "python_executable": sys.executable,
        "numpy": np.__version__, "platform": platform.platform(),
        "machine": platform.machine(), "cpu_count": os.cpu_count(),
        "processor_affinity": sorted(os.sched_getaffinity(0)),
        "thread_environment": {key: os.environ.get(key) for key in
            ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
             "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS")},
        "clock": vars(time.get_clock_info("perf_counter")),
    }
    cpu = Path("/proc/cpuinfo").read_text()
    info["cpu_model"] = next((s.split(":", 1)[1].strip() for s in
        cpu.splitlines() if s.startswith("model name")), None)
    for name, file in (("cgroup_cpu_max", "/sys/fs/cgroup/cpu.max"),
                       ("cgroup_memory_max", "/sys/fs/cgroup/memory.max")):
        info[name] = Path(file).read_text().strip() if Path(file).exists() else None
    try:
        from threadpoolctl import threadpool_info
        info["threadpools"] = threadpool_info()
    except ImportError:
        info["threadpools"] = "threadpoolctl unavailable"
    return info


FLOAT_FIELDS = (
    "moments_SI", "log_moments_SI", "dlogT_moments_SI",
    "dlogT_log_abs_SI", "logarithmic_slopes", "conditional_mean_energy_J",
)
FLAG_FIELDS = ("underflow", "subnormal", "derivative_underflow")


def compare_outputs(vector, scalars, gate):
    """Comparison is outside the timed sections; no kernel is evaluated here."""
    assert all(s.identity == vector.identity for s in scalars)
    details = {}
    for key in FLOAT_FIELDS:
        reference = getattr(vector, key)
        observed = np.concatenate([getattr(s, key) for s in scalars], axis=0)
        assert np.isfinite(reference).all() and np.isfinite(observed).all(), key
        scale = np.maximum(np.abs(reference), np.abs(observed))
        relative = np.zeros_like(scale)
        np.divide(np.abs(observed - reference), scale, out=relative, where=scale > 0)
        maximum = float(relative.max())
        assert maximum <= gate, (key, maximum, gate)
        details[key] = maximum
    for key in FLAG_FIELDS:
        observed = np.concatenate([getattr(s, key) for s in scalars], axis=0)
        assert np.array_equal(getattr(vector, key), observed), key
    return {"maximum_relative_difference": max(details.values()),
            "by_field": details, "flags_exact": True,
            "all_129_temperatures": True, "status": "PASS"}


def distribution(values):
    arr = np.asarray(values, dtype=float)
    return {"median": float(np.median(arr)), "minimum": float(arr.min()),
            "maximum": float(arr.max()), "range": float(np.ptp(arr)),
            "sample_standard_deviation": float(np.std(arr, ddof=1))}


def main():
    start_utc = utc_now()
    start_ns = time.perf_counter_ns()
    contract = json.loads((ROOT / "CONTRACT.json").read_text())
    module_sha = sha(ROOT / "vendor/maxwellian_moments.py")
    table_sha = sha(ROOT / "data/CCC_TICS_1S.txt")
    assert module_sha == contract["frozen_module_sha256"]
    assert table_sha == contract["source_sha256"]
    if any(os.environ.get(k) != "1" for k in
           ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")):
        raise RuntimeError("Set OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1")
    identities = {"script_sha256": sha(__file__), "module_sha256": module_sha,
                  "source_sha256": table_sha,
                  "contract_sha256": sha(ROOT / "CONTRACT.json"),
                  "python": platform.python_version(), "numpy": np.__version__}
    identity = hashlib.sha256(json.dumps(identities, sort_keys=True).encode()).hexdigest()
    complete = ROOT / "outputs/DIAGNOSTIC.json"
    if complete.exists():
        prior = json.loads(complete.read_text())
        assert prior["identity"] == identity, "completed identity differs; preserve it"
        for row in prior["payloads"]:
            assert sha(ROOT / row["path"]) == row["sha256"]
        print(json.dumps({"status": "REUSED_COMPLETE_DIAGNOSTIC",
                          "identity": identity, "new_evaluations": 0,
                          "new_benchmarks": 0, "new_IVPs": 0}))
        return

    raw_rows = []
    for line in (ROOT / "data/CCC_TICS_1S.txt").read_text().splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            fields = line.split()
            raw_rows.append((float(fields[0]), float(fields[1])))
    table = np.asarray(raw_rows)
    assert table.shape == (87, 2)
    assert table[0, 0] == 13.6058 and table[-1, 0] == 968.61
    assert table[0, 1] == 0.0
    temperature = np.geomspace(2000.0, 200000.0, 129)
    unmodified_midpoint = float(temperature[64])
    temperature[64] = 20000.0
    assert len(np.unique(temperature)) == 129 and np.all(np.diff(temperature) > 0)

    prepare_start = time.perf_counter_ns()
    kernel = PreparedMaxwellianMoments(table[:, 0], table[:, 1] * A0_M ** 2,
        threshold_eV=13.6058, source_id="CCC87:" + table_sha,
        reduced_mass_kg=ME_KG, energy_mapping="heavy_fixed_target_incident_electron",
        temperature_domain_K=(2000.0, 200000.0), quadrature_order=16)
    preparation_ns = time.perf_counter_ns() - prepare_start

    def vector_path():
        return kernel.evaluate(temperature, batch_size=129)

    def scalar_path():
        return [kernel.evaluate(float(t), batch_size=129) for t in temperature]

    # One warmup per path is also the diagnostic output and initial parity gate.
    result = vector_path()
    warmup_parity = compare_outputs(result, scalar_path(),
                                   contract["benchmark"]["parity_relative_gate"])
    times = []
    for pair in range(5):
        order = ("vector", "scalar") if pair % 2 == 0 else ("scalar", "vector")
        outputs = {}
        elapsed = {}
        for name in order:
            before = time.perf_counter_ns()
            outputs[name] = vector_path() if name == "vector" else scalar_path()
            elapsed[name] = time.perf_counter_ns() - before
        parity = compare_outputs(outputs["vector"], outputs["scalar"],
                                 contract["benchmark"]["parity_relative_gate"])
        times.append({"pair": pair + 1, "execution_order": list(order),
                      "vector_ns": elapsed["vector"], "scalar_ns": elapsed["scalar"],
                      "scalar_over_vector": elapsed["scalar"] / elapsed["vector"],
                      "parity": parity})

    alpha, beta, gamma, delta = result.moments_SI.T
    theta = KB_J_K * temperature
    selection = (beta / alpha) / theta
    k1_ratio = (2.0 / 3.0) * selection
    k2_ratio = (4.0 / 15.0) * ((gamma / alpha) / theta) / theta
    mean_eV = result.conditional_mean_energy_J / EV_J
    feasibility = k2_ratio - (3.0 / 5.0) * k1_ratio ** 2
    cmoment = 1.0 - 2.0 * k1_ratio + k2_ratio
    variance_eV2 = (gamma / alpha) / EV_J ** 2 - mean_eV ** 2
    # These are finite positive-kernel identities, not source-accuracy gates.
    assert np.isfinite(result.moments_SI).all() and np.all(result.moments_SI > 0)
    assert not result.underflow.any() and not result.subnormal.any()
    assert np.all(mean_eV >= 13.6058) and np.all(mean_eV <= 968.61)
    assert np.all(feasibility >= 0) and np.all(variance_eV2 >= 0)
    columns = [
        ("temperature_K", "K", temperature),
        ("alpha_partial_m3_s", "m^3/s", alpha),
        ("beta_partial_J_m3_s", "J m^3/s", beta),
        ("gamma_partial_J2_m3_s", "J^2 m^3/s", gamma),
        ("delta_partial_J3_m3_s", "J^3 m^3/s", delta),
        ("kappa1_partial_m3_s", "m^3/s", alpha * k1_ratio),
        ("kappa2_incoming_loss_partial_m3_s", "m^3/s", alpha * k2_ratio),
        ("kappa1_over_alpha", "1", k1_ratio),
        ("kappa2_over_alpha", "1", k2_ratio),
        ("reaction_weighted_mean_energy_eV", "eV", mean_eV),
        ("energy_selection_beta_over_theta_alpha", "1", selection),
        ("C_moment", "1", cmoment),
        ("feasibility_margin", "1", feasibility),
        ("reaction_weighted_energy_variance_eV2", "eV^2", variance_eV2),
        ("log_alpha_SI", "natural log of alpha numerical SI value", result.log_moments_SI[:, 0]),
    ]
    rows = [{name: float(array[i]) for name, _, array in columns} for i in range(129)]
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow([name for name, _, _ in columns])
    writer.writerows([[format(float(array[i]), ".17g") for _, _, array in columns]
                     for i in range(129)])
    atomic_write(ROOT / "outputs/ccc_moments.csv", stream.getvalue())
    write_json(ROOT / "outputs/ccc_moments.json", {
        "schema": "he36.ccc_partial_moments.v1", "identity": identity,
        "coverage": kernel.coverage(), "definitions": contract["definitions"],
        "column_units": {name: unit for name, unit, _ in columns},
        "physical_scope": contract["physical_scope"], "rows": rows})
    vector_seconds = [r["vector_ns"] / 1e9 for r in times]
    scalar_seconds = [r["scalar_ns"] / 1e9 for r in times]
    benchmark = {
        "schema": "he36.same_kernel_paired_benchmark.v1", "identity": identity,
        "started_utc": start_utc, "completed_utc": utc_now(),
        "environment": environment(), "contract": contract["benchmark"],
        "kernel_identity": kernel.identity, "preparation_ns_excluded": preparation_ns,
        "node_count": len(kernel.node_energy_eV), "temperatures_per_path": 129,
        "moment_orders_both_paths": [0, 1, 2, 3],
        "warmup_parity": warmup_parity, "raw_pairs": times,
        "vector_seconds": distribution(vector_seconds),
        "scalar_seconds": distribution(scalar_seconds),
        "paired_speedup": distribution([r["scalar_over_vector"] for r in times]),
        "ratio_of_medians": float(np.median(scalar_seconds) / np.median(vector_seconds)),
        "interpretation": "Observed speedup measures temperature batching in the same GL16 prepared kernel only. It is not an ODE comparison or an increase in physical accuracy.",
        "excluded_from_timings": ["table parsing", "GL preparation", "file output",
            "parity comparisons", "scalar result concatenation for comparison", "plotting"],
        "limitations": ["single process and host", "five paired trials", "shared-host scheduling may vary", "no confidence interval or cross-machine claim"],
    }
    write_json(ROOT / "outputs/BENCHMARK.json", benchmark)
    payloads = [{"path": str(path.relative_to(ROOT)), "sha256": sha(path),
                 "bytes": path.stat().st_size} for path in
                (ROOT / "outputs/ccc_moments.csv", ROOT / "outputs/ccc_moments.json",
                 ROOT / "outputs/BENCHMARK.json")]
    summary = {
        "schema": "he36.finite_ccc_diagnostic_receipt.v1", "status": "PASS_SCOPED",
        "identity": identity, "inputs": identities, "started_utc": start_utc,
        "completed_utc": utc_now(), "elapsed_seconds": (time.perf_counter_ns() - start_ns) / 1e9,
        "peak_rss_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "coverage": kernel.coverage(), "physical_scope": contract["physical_scope"],
        "grid": {"rows": 129, "unique_rows": 129, "minimum_K": 2000.0,
            "maximum_K": 200000.0, "exact_20000K_index": 64,
            "unmodified_geomspace_midpoint_K": unmodified_midpoint,
            "sha256_little_endian_float64": hashlib.sha256(temperature.astype("<f8").tobytes()).hexdigest()},
        "checks": {"all_numeric_fields_finite": True, "all_four_moments_positive": True,
            "underflow_or_subnormal_count": 0,
            "all_mean_energies_inside_source_interval": True,
            "minimum_feasibility_margin": float(feasibility.min()),
            "minimum_energy_variance_eV2": float(variance_eV2.min()),
            "maximum_vector_scalar_relative_difference": max(warmup_parity["maximum_relative_difference"],
                *[r["parity"]["maximum_relative_difference"] for r in times]),
            "vector_scalar_relative_gate": contract["benchmark"]["parity_relative_gate"],
            "flags_exact": True},
        "representative_rows": [rows[i] for i in (0, 64, 128)],
        "execution_counts": {"new_finite_diagnostic_runs": 1, "new_benchmark_experiments": 1,
            "paired_timing_trials": 5, "kernel_preparations": 1,
            "untimed_vector_calls": 1, "untimed_scalar_calls": 129,
            "timed_vector_calls": 5, "timed_scalar_calls": 645,
            "total_evaluate_calls": 780, "total_temperature_evaluations": 1548,
            "new_IVPs": 0, "completed_donor_suite_replays": 0,
            "new_GL32_or_adaptive_quadrature_checks": 0,
            "new_renders_in_this_script": 0},
        "payloads": payloads,
    }
    write_json(complete, summary)
    print(json.dumps({"status": summary["status"], "rows": 129, "identity": identity,
        "elapsed_seconds": summary["elapsed_seconds"],
        "maximum_parity_relative": summary["checks"]["maximum_vector_scalar_relative_difference"],
        "median_paired_batching_speedup": benchmark["paired_speedup"]["median"],
        "representative_rows": summary["representative_rows"]}, allow_nan=False))


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        receipt = ROOT / "receipts" / ("DIAGNOSTIC_FAILURE_" + str(time.time_ns()) + ".json")
        write_json(receipt, {"status": "FAIL_PRESERVED", "utc": utc_now(),
            "script_sha256": sha(__file__), "traceback": traceback.format_exc()})
        raise
