#!/usr/bin/env python3
"""One bounded actual source-row comparison; no native/transport/full table."""
import argparse
from dataclasses import asdict
import json
import multiprocessing as mp
import os
from pathlib import Path
import sys
import time

for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS", "RAYON_NUM_THREADS"):
    os.environ[variable] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import numpy as np
import parallel_source as p


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rows", type=int, default=256)
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args()
    if not 1 <= args.rows <= 512 or not 1 <= args.workers <= 4:
        ap.error("bounded probe: rows 1..512 and workers 1..4")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    config = {"spec": asdict(p.GridSpec(m=8, angles=4, q=0., strips=4)),
              "source_count": None, "nodes": 512}
    model = p.RefinedSourceModel(None, p.GridSpec(**config["spec"]),
                                tabulate=False, source_table_nodes=512)
    config["source_count"] = float(model.source_count)
    layout = p.table_layout(model)
    index = next(iter(layout))
    times = layout[index][:args.rows]
    tasks = [(index, first, times[first:first + 64].tolist())
             for first in range(0, len(times), 64)]
    p.initialize_worker(config, p.model_identity(model))
    serial_start = time.monotonic()
    serial_results = [p.compute_chunk(task) for task in tasks]
    serial_s = time.monotonic() - serial_start
    parallel_start = time.monotonic()
    pool = mp.get_context("spawn").Pool(args.workers, initializer=p.initialize_worker,
                                       initargs=(config, p.model_identity(model)))
    try:
        iterator = pool.imap_unordered(p.compute_chunk, tasks, chunksize=1)
        parallel_results = [iterator.next(timeout=60.) for _ in tasks]
        pool.close()
        pool.join()
    except BaseException:
        pool.terminate()
        pool.join()
        raise
    parallel_s = time.monotonic() - parallel_start
    serial_results.sort(key=lambda x: x[:2])
    parallel_results.sort(key=lambda x: x[:2])
    serial = np.concatenate([row[2] for row in serial_results])
    parallel = np.concatenate([row[2] for row in parallel_results])
    equal = serial.tobytes() == parallel.tobytes()
    report_equal = serial_results[-1][3] == parallel_results[-1][3]
    record = {"schema": "he29.table_row_probe.v1", "status": "PASS" if equal and report_equal else "FAIL",
        "runtime": p.runtime_identity(), "sources": p.source_identity(),
        "case": config["spec"], "source_table_nodes": 512, "table_interval": index,
        "rows": len(times), "columns": model.K, "chunks": len(tasks),
        "workers": args.workers, "worker_pids": sorted({x[4] for x in parallel_results}),
        "row_bytes_match": equal, "canonical_last_report_match": report_equal,
        "serial_array_sha256": p.array_sha(serial), "parallel_array_sha256": p.array_sha(parallel),
        "serial_evaluation_wall_s": serial_s, "parallel_spawn_and_evaluation_wall_s": parallel_s,
        "descriptive_ratio": serial_s / parallel_s, "rounds": 1,
        "timing_scope": "One bounded actual-row workload; serial excludes model initialization, parallel includes spawn/model initialization. Not a statistically established speedup, full-table timing or NCP prediction.",
        "full_reference_table": "NOT_BUILT_LOCAL_PYTHON_COHORT_DIFFERS_FROM_RETURN",
        "saved_reference_python": "3.12.3 (main, Jun 19 2026, 12:46:00) [GCC 13.3.0]",
        "native_calls": 0, "physical_solver_runs": 0,
        "geometry_clock": "unchanged source-model construction",
        "wall_s": time.monotonic() - start}
    p.write_json_once(out / "RESULT.json", record)
    print(json.dumps({k:record[k] for k in ("status", "rows", "workers", "row_bytes_match",
        "canonical_last_report_match", "serial_evaluation_wall_s", "parallel_spawn_and_evaluation_wall_s",
        "descriptive_ratio", "wall_s")}, indent=2))
    if record["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
