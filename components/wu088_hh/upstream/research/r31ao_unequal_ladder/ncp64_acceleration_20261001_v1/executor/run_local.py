#!/usr/bin/env python3
"""ProcessPool fallback; only metadata crosses process boundaries."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import multiprocessing
import time
from core import collect, load_manifest, prepare_manifest, run_task, ContractError


def run_local(manifest_path, workers=1):
    if type(workers) is not int or not 1 <= workers <= 63:
        raise ContractError("WORKERS_1_TO_63_REQUIRED")
    plan = load_manifest(manifest_path)
    prepared = prepare_manifest(manifest_path)
    if prepared["status"] != "READY":
        return prepared
    order = plan["dispatch_order"]
    started = time.monotonic()
    count = min(workers, len(order))
    if count == 1:
        receipts = [run_task(manifest_path, i) for i in order]
    else:
        with ProcessPoolExecutor(max_workers=count, mp_context=multiprocessing.get_context("spawn")) as pool:
            futures = [pool.submit(run_task, manifest_path, i) for i in order]
            receipts = [future.result() for future in futures]
    result = collect(manifest_path)
    result["local_execution"] = {"workers": count, "requested_workers": workers,
                                 "wall_seconds": time.monotonic() - started,
                                 "dispatch_order": order,
                                 "task_statuses": [r["status"] for r in receipts],
                                 "timing_includes": "dispatch, subprocesses, identity verification and collection; excludes fixture planning/build"}
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--workers", type=int, default=1)
    a = p.parse_args()
    try:
        r = run_local(a.manifest, a.workers)
    except (ContractError, OSError, ValueError) as exc:
        r = {"status": "INCONCLUSIVE", "reason": str(exc)}
    print(json.dumps(r, sort_keys=True))
    return 0 if r["status"] == "COLLECTED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
