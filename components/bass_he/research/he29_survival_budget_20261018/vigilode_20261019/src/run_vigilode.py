"""One optional HE29 r4/table512 canary, only after four admitted references.

The controller enforces a POSIX process-group wall limit. It never launches
Radau, DOP853, old transport cases or a wider grid. Original sources, inputs,
binary, table and numerical Python versions must match the completed baseline.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import sys
import time
import traceback

LANE = Path(__file__).resolve().parents[1]
HE29 = LANE.parent
sys.path.insert(0, str(HE29 / "src"))
from reference_runner import (check_sources, NativeOwner, RefinedSourceModel,
                              GridSpec, THREADS, check_result, admit_pair,
                              atomic_json, digest, manifest, run_process)
from analyze_references import analyze
from vigilode_reference import VigilODEBridge, solve_vigilode, verify_build, BASELINE_CODE


def baseline_contract(root, current):
    root = Path(root)
    summary = analyze(root)
    if not summary["complete"] or summary["completed"] != 4:
        raise ValueError("HE29_VIGILODE_REQUIRES_FOUR_COMPLETED_BASELINE_PAIRS")
    case = root / "m8_r4_table512"
    identity = json.loads((case / "IDENTITY.json").read_text())
    result = json.loads((case / "RESULT.json").read_text())
    for key in ("binary_sha256", "source_files", "parent_sources", "input_sources",
                "numerical_thread_environment"):
        if identity.get(key) != current.get(key):
            raise ValueError("HE29_VIGILODE_BASELINE_IDENTITY: " + key)
    for key in ("python", "numpy", "scipy"):
        if identity.get("runtime", {}).get(key) != current["runtime"][key]:
            raise ValueError("HE29_VIGILODE_BASELINE_RUNTIME: " + key)
    return result, {"baseline_analysis": summary,
                    "case_receipt_sha256": digest(case / "RESULT.json"),
                    "case_identity_sha256": digest(case / "IDENTITY.json"),
                    "qualification": "six baseline points reused with identical binary bytes",
                    "baseline_code_revision": BASELINE_CODE}


def preflight(args):
    current = check_sources(args.binary, args.owner_receipt)
    prior, reused = baseline_contract(args.baseline_campaign, current)
    build = verify_build(args.library, args.bridge_receipt)
    return current, prior, reused, build


def run_case(args):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    try:
        current, prior, reused, build = preflight(args)
        if any(os.environ.get(k) != v for k, v in THREADS.items()):
            raise ValueError("HE29_SINGLE_THREAD_ENV_REQUIRED")
        if os.environ.get("RAYON_NUM_THREADS") != "1":
            raise ValueError("HE29_VIGILODE_SINGLE_RAYON_THREAD_REQUIRED")
        identity = {**current, "m": 8, "r": 4, "q": 0., "angles": 4, "table_nodes": 512,
                    "bridge": build, "reused": reused,
                    "new_adapter_sources": manifest(sorted((LANE / "src").glob("*.py")), LANE),
                    "rayon_num_threads": "1"}
        atomic_json(out / "IDENTITY.json", identity)
        bridge = VigilODEBridge(args.library, args.bridge_receipt)
        with NativeOwner(args.binary, evidence_path=out / "native.jsonl.gz",
                         expected_binary_sha256=current["binary_sha256"]) as owner:
            model = RefinedSourceModel(owner, GridSpec(m=8, angles=4, q=0., strips=4),
                tabulate=True, source_table_nodes=512, max_table_bytes=2*1024**3,
                max_table_wall_s=600.)
            table = model.source_table_sha256
            atomic_json(out / "TABLE.json", {"source_table_sha256": table,
                                            "diagnostics": model.source_table_diagnostics})
            if table != prior["table_sha256"]:
                raise ValueError("HE29_VIGILODE_REBUILT_TABLE_MISMATCH")
            trace_path = out / "SEGMENT_ENDPOINTS.jsonl"
            with trace_path.open("x") as trace:
                def checkpoint(row):
                    text = json.dumps(row, allow_nan=False, separators=(",", ":")) + "\n"
                    if trace.tell() + len(text.encode()) > 128*1024**2:
                        raise RuntimeError("HE29_VIGILODE_ENDPOINT_TRACE_BUDGET")
                    trace.write(text)
                    trace.flush()
                    os.fsync(trace.fileno())
                result = solve_vigilode(model, bridge, checkpoint)
            # Preserve the actual solver output before an admission failure.
            atomic_json(out / "VIGILODE_RAW.json", {"result": result,
                        "native_calls": owner.calls, "wall_s": time.monotonic() - start})
            check_result(result)
            comparisons = {method: admit_pair(result, prior["results"][method])
                           for method in ("Radau", "DOP853")}
            calls = owner.calls
        atomic_json(out / "RESULT.json", {
            "schema": "he29.vigilode.canary.v1", "status": "CANARY_COMPLETED_SCOPED",
            "case": {"m": 8, "r": 4, "angles": 4, "q": 0., "table_nodes": 512},
            "table_sha256": table, "result": result, "comparison_to_saved_baseline": comparisons,
            "native_calls": calls, "wall_s": time.monotonic() - start,
            "baseline_pairs_reused": 4, "new_baseline_pairs": 0,
            "transport_replays": 0, "source_only_suites_replayed": 0,
            "continuous_spectrum": "HOLD", "global_gas_temperature_bound": "HOLD",
            "upstream_grackle_whole_runtime_equivalence": "HOLD"})
    except BaseException as exc:
        atomic_json(out / "FAILURE.json", {"status": "HOLD_FIRST_FAILURE", "error": repr(exc),
                    "traceback": traceback.format_exc(), "wall_s": time.monotonic() - start,
                    "baseline_pairs_created": 0, "transport_replays": 0})
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
    ap.add_argument("--wall-s", type=float, default=900.)
    args = ap.parse_args()
    if not math.isfinite(args.wall_s) or not 0 < args.wall_s <= 3600:
        ap.error("wall budget must be finite, positive and <=3600 seconds")
    if args.mode == "_worker":
        if os.environ.get("HE29_VIGILODE_PROCESS_GROUP_WORKER") != "1":
            ap.error("use canary mode for enforced process-group timeout")
        run_case(args)
        return
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    try:
        current, prior, reused, build = preflight(args)
        atomic_json(out / "PREFLIGHT.json", {"status": "PASS", "reused": reused,
                                            "bridge": build, "native_solver_calls": 0})
        if args.mode == "preflight":
            return
        argv = [sys.executable, str(Path(__file__).resolve()), "_worker",
                "--out", str(out / "case")]
        for option, value in (("baseline-campaign", args.baseline_campaign), ("binary", args.binary),
            ("owner-receipt", args.owner_receipt), ("library", args.library),
            ("bridge-receipt", args.bridge_receipt)):
            argv += ["--" + option, str(Path(value).resolve())]
        # This controller is a dedicated process; child environment is recorded.
        os.environ["RAYON_NUM_THREADS"] = "1"
        os.environ["HE29_VIGILODE_PROCESS_GROUP_WORKER"] = "1"
        receipt = run_process(argv, out / "process", args.wall_s)
        atomic_json(out / "SUMMARY.json", {"new_canary_cases": int(receipt["returncode"] == 0
                    and not receipt["timed_out"]), "requested_canary_cases": 1,
                    "new_baseline_pairs": 0, "transport_replays": 0, **receipt})
        if receipt["returncode"] != 0 or receipt["timed_out"]:
            raise SystemExit(1)
    except BaseException as exc:
        if not (out / "FAILURE.json").exists():
            atomic_json(out / "FAILURE.json", {"status": "HOLD_FIRST_FAILURE", "error": repr(exc),
                        "traceback": traceback.format_exc(), "native_submission_claimed": False})
        raise


if __name__ == "__main__":
    main()
