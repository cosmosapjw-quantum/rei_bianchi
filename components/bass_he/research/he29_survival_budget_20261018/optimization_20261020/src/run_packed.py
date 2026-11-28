"""One opt-in ABI2 HE29 r4/table512 canary after four admitted references.

Reuse the original baseline, microphysics, table and admission contracts.  The
controller bounds the entire POSIX process group.  It never launches baseline
solvers, old transport cases, old tests, parallel canaries or a wider grid.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

LANE = Path(__file__).resolve().parents[1]
HE29 = LANE.parent
REPO = HE29.parents[1]
OLD_LANE = HE29 / "vigilode_20261019"
sys.path.insert(0, str(HE29 / "src"))
sys.path.insert(0, str(OLD_LANE / "src"))
from reference_runner import (check_sources, NativeOwner, GridSpec, THREADS,
    check_result, admit_pair, atomic_json, digest, manifest, run_process)
from reference_contract import JOBS
from run_vigilode import baseline_contract as original_baseline_contract
from optimized_model import OptimizedRefinedSourceModel
from packed_reference import PackedBridge, solve_packed, verify_build

WORKER_FLAG = "HE29_PACKED_PROCESS_GROUP_WORKER"
CASE = dict(m=8, r=4, angles=4, q=0., table_nodes=512)
REUSED_ADAPTERS = ("run_vigilode.py", "vigilode_callbacks.py", "vigilode_reference.py")


def query(argv, *, strip=True):
    text = subprocess.run(argv, check=True, capture_output=True, text=True,
                          timeout=30).stdout
    return text.strip() if strip else text


def baseline_contract(root, current):
    """Original four-pair admission, with runtime equality for every pair."""
    root = Path(root)
    result, reused = original_baseline_contract(root, current)
    receipts = {}
    for r, nodes in JOBS:
        case = root / f"m8_r{r}_table{nodes}"
        identity = json.loads((case / "IDENTITY.json").read_text())
        for key in ("python", "numpy", "scipy"):
            if identity.get("runtime", {}).get(key) != current["runtime"][key]:
                raise ValueError("HE29_OPT_BASELINE_RUNTIME: " + case.name + ": " + key)
        receipts[case.name] = {name: digest(case / name)
            for name in ("IDENTITY.json", "RESULT.json", "TABLE.json")}
    return result, {**reused, "all_pair_receipts": receipts,
                    "runtime_matched_pairs": 4,
                    "source_binary_input_thread_matched_pairs": 4}


def publication_contract(revision, build, current):
    if (len(revision) != 40
            or any(c not in "0123456789abcdef" for c in revision)):
        raise ValueError("HE29_OPT_SOURCE_REVISION_REQUIRES_FULL_SHA")
    if build.get("bass_publication_head") != revision:
        raise ValueError("HE29_OPT_BUILD_PUBLICATION_MISMATCH")
    head = query(["git", "-C", str(REPO), "rev-parse", "HEAD"])
    if head != revision:
        raise ValueError("HE29_OPT_RUN_PUBLICATION_MISMATCH")
    status = query(["git", "-C", str(REPO), "status", "--porcelain=v1",
                    "--untracked-files=all", "-z"], strip=False)
    if status and not status.endswith("\0"):
        raise ValueError("HE29_OPT_RUN_GIT_STATUS_FORMAT")
    allowed = {str((HE29 / path).relative_to(REPO)): sha
               for path, sha in current["input_sources"].items()}
    restored = {}
    for record in status.split("\0")[:-1]:
        if not record.startswith("?? "):
            raise ValueError("HE29_OPT_RUN_TRACKED_SOURCE_DIRTY")
        path = record[3:]
        if path not in allowed or digest(REPO / path) != allowed[path]:
            raise ValueError("HE29_OPT_RUN_UNVERIFIED_UNTRACKED_FILE: " + path)
        restored[path] = allowed[path]
    return {"source_revision_argument": revision, "head": head,
            "tree": query(["git", "-C", str(REPO), "rev-parse", "HEAD^{tree}"]),
            "tracked_clean": True, "verified_untracked_input_data": restored,
            "clean_except_verified_input_data": True}


def preflight(args):
    current = check_sources(args.binary, args.owner_receipt)
    prior, reused = baseline_contract(args.baseline_campaign, current)
    build = verify_build(args.library, args.bridge_receipt)
    publication = publication_contract(args.source_revision, build, current)
    return current, prior, reused, build, publication


def run_case(args):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    try:
        current, prior, reused, build, publication = preflight(args)
        if any(os.environ.get(k) != v for k, v in THREADS.items()):
            raise ValueError("HE29_SINGLE_THREAD_ENV_REQUIRED")
        if os.environ.get("RAYON_NUM_THREADS") != "1":
            raise ValueError("HE29_OPT_SINGLE_RAYON_THREAD_REQUIRED")
        identity = {**current, **CASE, "bridge": build, "reused": reused,
            "publication": publication,
            "new_adapter_sources": manifest(sorted((LANE / "src").glob("*.py")), LANE),
            "reused_adapter_sources": manifest(
                [OLD_LANE / "src" / name for name in REUSED_ADAPTERS], OLD_LANE.parent),
            "rayon_num_threads": "1", "packed_threads": 1,
            "source_table_budget": {"wall_s": 600., "estimated_allocation_bytes": 2*1024**3,
                                    "whole_process_rss_bound": False}}
        atomic_json(out / "IDENTITY.json", identity)
        bridge = PackedBridge(args.library, args.bridge_receipt)
        with NativeOwner(args.binary, evidence_path=out / "native.jsonl.gz",
                         expected_binary_sha256=current["binary_sha256"]) as owner:
            model = OptimizedRefinedSourceModel(owner,
                GridSpec(m=8, angles=4, q=0., strips=4), tabulate=True,
                source_table_nodes=512, max_table_bytes=2*1024**3,
                max_table_wall_s=600.)
            table = model.source_table_sha256
            atomic_json(out / "TABLE.json", {"source_table_sha256": table,
                                            "diagnostics": model.source_table_diagnostics})
            if table != prior["table_sha256"]:
                raise ValueError("HE29_OPT_REBUILT_TABLE_MISMATCH")
            with (out / "SEGMENT_ENDPOINTS.jsonl").open("x") as trace:
                def checkpoint(row):
                    text = json.dumps(row, allow_nan=False, separators=(",", ":")) + "\n"
                    if trace.tell() + len(text.encode()) > 128*1024**2:
                        raise RuntimeError("HE29_OPT_ENDPOINT_TRACE_BUDGET")
                    trace.write(text)
                    trace.flush()
                    os.fsync(trace.fileno())
                result = solve_packed(model, bridge, checkpoint)
            # Keep actual output before the unchanged physical/method gates.
            atomic_json(out / "PACKED_RAW.json", {"result": result,
                        "native_calls": owner.calls, "wall_s": time.monotonic() - start})
            check_result(result)
            comparisons = {method: admit_pair(result, prior["results"][method])
                           for method in ("Radau", "DOP853")}
            calls = owner.calls
        atomic_json(out / "RESULT.json", {
            "schema": "he29.optimized.canary.v1", "status": "CANARY_COMPLETED_SCOPED",
            "case": CASE, "table_sha256": table, "result": result,
            "comparison_to_saved_baseline": comparisons,
            "native_calls": calls, "wall_s": time.monotonic() - start,
            "baseline_pairs_reused": 4, "new_baseline_pairs": 0,
            "transport_replays": 0, "source_only_suites_replayed": 0,
            "packed_threads": 1, "continuous_spectrum": "HOLD", "full_eor": "HOLD",
            "global_gas_temperature_bound": "HOLD",
            "upstream_grackle_whole_runtime_equivalence": "HOLD",
            "observational_bianchi_cmb": "HOLD"})
    except BaseException as exc:
        atomic_json(out / "FAILURE.json", {"status": "HOLD_FIRST_FAILURE", "error": repr(exc),
            "traceback": traceback.format_exc(), "wall_s": time.monotonic() - start,
            "baseline_pairs_created": 0, "transport_replays": 0,
            "retained_raw_files": [name for name in
                ("TABLE.json", "SEGMENT_ENDPOINTS.jsonl", "PACKED_RAW.json", "native.jsonl.gz")
                if (out / name).exists()]})
        raise


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=("preflight", "canary", "_worker"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--baseline-campaign", required=True)
    ap.add_argument("--binary", required=True)
    ap.add_argument("--owner-receipt", required=True)
    ap.add_argument("--library", required=True)
    ap.add_argument("--bridge-receipt", required=True)
    ap.add_argument("--source-revision", required=True,
                    help="exact published code_commit from this lane's DELIVERY.json")
    ap.add_argument("--wall-s", type=float, default=900.)
    args = ap.parse_args()
    if not math.isfinite(args.wall_s) or not 0 < args.wall_s <= 3600:
        ap.error("wall budget must be finite, positive and <=3600 seconds")
    if args.mode == "_worker":
        if os.environ.get(WORKER_FLAG) != "1":
            ap.error("use canary mode for enforced process-group timeout")
        run_case(args)
        return
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    try:
        current, prior, reused, build, publication = preflight(args)
        atomic_json(out / "PREFLIGHT.json", {"status": "PASS", "reused": reused,
            "bridge": build, "publication": publication, "native_solver_calls": 0})
        if args.mode == "preflight":
            return
        argv = [sys.executable, str(Path(__file__).resolve()), "_worker",
                "--out", str(out / "case"), "--source-revision", args.source_revision]
        for option, value in (("baseline-campaign", args.baseline_campaign), ("binary", args.binary),
                ("owner-receipt", args.owner_receipt), ("library", args.library),
                ("bridge-receipt", args.bridge_receipt)):
            argv += ["--" + option, str(Path(value).resolve())]
        os.environ["RAYON_NUM_THREADS"] = "1"
        os.environ[WORKER_FLAG] = "1"
        receipt = run_process(argv, out / "process", args.wall_s)
        atomic_json(out / "SUMMARY.json", {
            "new_canary_cases": int(receipt["returncode"] == 0 and not receipt["timed_out"]),
            "requested_canary_cases": 1, "new_baseline_pairs": 0,
            "transport_replays": 0, "packed_threads": 1, **receipt})
        if receipt["returncode"] != 0 or receipt["timed_out"]:
            raise SystemExit(1)
    except BaseException as exc:
        if not (out / "FAILURE.json").exists():
            atomic_json(out / "FAILURE.json", {"status": "HOLD_FIRST_FAILURE", "error": repr(exc),
                "traceback": traceback.format_exc(), "native_submission_claimed": False})
        raise


if __name__ == "__main__":
    main()
