"""Post-process completed AXBI cold histories; no solver edits, no warm-source reuse.

Proper time in s, proper densities cm^-3, sigma_T in m^2, c in m/s.
Full native history required; results are exploratory quadrature of stored rows.
"""
from __future__ import annotations
import argparse
import csv
from hashlib import sha256
import json
import math
from pathlib import Path
import statistics
import time
import numpy as np

from optical_depth import C_M_S, SIGMA_T_M2, electron_density_cm3, cumulative_tau_trapezoid
from streaming import cumulative_tau_chunked

HE_TO_H = 1227 / 15092  # Y_He=.2454, X_H=.7546, He/H = Y/(4X)
FIELDS = ("time_s", "a", "zbar", "nH_proper_cm3", "ne_proper_cm3",
          "x_HII", "x_HeII", "x_HeIII")
OPACITY_FACTOR = C_M_S * SIGMA_T_M2 * 1e6


def file_sha256(path: Path) -> str:
    hashobj = sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(2**20), b""):
            hashobj.update(block)
    return hashobj.hexdigest()


def read_history(path: Path):
    manifest_path = path.with_name("COMPLETED_CASE_INPUT.json")
    if not manifest_path.is_file():
        raise ValueError(f"Missing provenance manifest: {manifest_path}")
    metadata = json.loads(manifest_path.read_text())
    expected_sha = metadata["history"]["sha256"]
    actual_sha = file_sha256(path)
    if actual_sha != expected_sha:
        raise ValueError(f"Byte identity mismatch for {path.name}: {actual_sha} != {expected_sha}")
    before = path.stat()
    columns = {x: [] for x in FIELDS}
    case_name = None
    with path.open("r", newline="") as src:
        reader = csv.reader(src)
        header = next(reader)
        positions = {name: header.index(name) for name in FIELDS}
        case_idx = header.index("case_id")
        for row in reader:
            if not row:
                continue
            case = row[case_idx]
            if case_name is None:
                case_name = case
            elif case != case_name:
                raise ValueError("Mixed cases in one history")
            for name, i in positions.items():
                columns[name].append(float(row[i]))
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError("Source history changed while reading")
    data = {name: np.asarray(v, dtype=np.float64) for name, v in columns.items()}
    n = len(data["time_s"])
    if n < 2 or any(a.shape != (n,) or not np.all(np.isfinite(a)) for a in data.values()):
        raise ValueError("Nonfinite or inconsistent history")
    if np.any(np.diff(data["time_s"]) <= 0):
        raise ValueError("Proper-time history not strictly increasing")
    if np.any(np.diff(data["a"]) < -1e-14):
        raise ValueError("Mean scale factor decreases in stored history")
    if np.any(data["nH_proper_cm3"] <= 0) or np.any(data["ne_proper_cm3"] < 0):
        raise ValueError("Negative proper density")
    return case_name, data, actual_sha, metadata


def run(path: Path, dest: Path, reps: int = 3, chunksize: int = 16384):
    wall_start = time.perf_counter()
    case, d, hsh, metadata = read_history(path)
    t = d["time_s"]
    nh = d["nH_proper_cm3"]; src_ne = d["ne_proper_cm3"]
    x = d["x_HII"]; y = d["x_HeII"]; z = d["x_HeIII"]
    computed_ne = electron_density_cm3(nh, x, y, z, HE_TO_H)
    mismatch = abs(computed_ne - src_ne) / nh
    max_err = float(np.max(mismatch))
    if max_err > 1e-10:
        raise ValueError(f"Native electron census mismatch: max |ne_census-ne_source|/nH = {max_err}")
    times = {"direct_source": [], "vectorized_census": [], "chunked_census": []}
    last_values = {}
    for label, fn in {
        "direct_source": lambda: np.r_[0, np.cumsum(
            np.diff(t) * (OPACITY_FACTOR / 2) * (src_ne[:-1] + src_ne[1:]))],
        "vectorized_census": lambda: cumulative_tau_trapezoid(t, nh, x, y, z, HE_TO_H),
        "chunked_census": lambda: cumulative_tau_chunked(
            t, nh, x, y, z, HE_TO_H, chunksize),
    }.items():
        for _ in range(reps):
            tick = time.perf_counter()
            result = fn()
            times[label].append(time.perf_counter()-tick)
        last_values[label] = result
    cumulative = last_values["direct_source"]
    steps = np.diff(t) * (OPACITY_FACTOR/2) * (src_ne[:-1] + src_ne[1:])
    fsum_value = math.fsum(float(v) for v in steps)
    if not np.all(np.diff(cumulative) >= 0):
        raise ValueError("Nonmonotonic optical depth")
    decimated = {}
    for stride in (2, 4, 8):
        index = np.arange(0, len(t), stride, dtype=int)
        if index[-1] != len(t)-1:
            index = np.r_[index, len(t)-1]
        ds = np.diff(t[index]) * (OPACITY_FACTOR/2) * (
            src_ne[index[:-1]] + src_ne[index[1:]])
        decimated[str(stride)] = float(math.fsum(float(q) for q in ds))
    out = dest / case
    out.mkdir(parents=True, exist_ok=True)
    i_sample = np.unique(np.linspace(0, len(t)-1, 1025, dtype=int))
    with (out/"tau_samples.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["row","time_s","a","zbar","ne_proper_cm3","tau_from_z20"])
        for i in i_sample:
            writer.writerow([int(i),format(t[i],".17g"),format(d["a"][i],".17g"),
                             format(d["zbar"][i],".17g"),format(src_ne[i],".17g"),
                             format(cumulative[i],".17g")])
    report = {
        "schema": "axbi.he18.cold_history_tau.v1",
        "status": "NUMERICAL_DIAGNOSTIC_NOT_CERTIFIED",
        "model": "cold Plancklike_MD14_BB50K AXBI; not warm BASS_HE FT03/HM12",
        "case_id": case,
        "history_file": str(path),
        "history_sha256": hsh,
        "manifest_sha256": file_sha256(path.with_name("COMPLETED_CASE_INPUT.json")),
        "rows": len(t),
        "accepted_intervals": len(t)-1,
        "time_origin": "elapsed proper seconds since zbar20",
        "end_proper_s": float(t[-1]),
        "end_a": float(d["a"][-1]),
        "end_zbar": float(d["zbar"][-1]),
        "helium_number_ratio": "1227/15092",
        "max_electron_census_difference_over_nH": max_err,
        "tau_trap_from_native_ne": float(cumulative[-1]),
        "tau_trap_from_census": float(last_values["vectorized_census"][-1]),
        "tau_chunked_from_census": float(last_values["chunked_census"][-1]),
        "tau_fsum_native_ne": float(fsum_value),
        "integration_diagnostic_decimated": decimated,
        "median_wall_seconds": {key:float(statistics.median(value)) for key,value in times.items()},
        "proper_density_units": "cm^-3",
        "clock_units": "s",
        "integrated_tau_scope": "zbar=20 to terminal zbar only, excluding 0<=zbar<terminal",
        "scientific_admission": "HOLD",
        "source_ode_replayed": False,
        "interval_bound_proven": False,
        "elapsed_including_io_sha_seconds": time.perf_counter()-wall_start,
    }
    (out/"RESULT.json").write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n")
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--history", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--reps", type=int, default=3)
    p.add_argument("--chunk-size", type=int, default=16384)
    args = p.parse_args()
    if args.reps < 1 or args.chunk_size < 2:
        p.error("reps >= 1 and chunk-size >= 2 required")
    print(json.dumps(run(args.history, args.out, args.reps, args.chunk_size),
                     indent=2, ensure_ascii=False))


if __name__=="__main__":
    main()
