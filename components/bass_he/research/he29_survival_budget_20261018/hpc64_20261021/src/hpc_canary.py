#!/usr/bin/env python3
"""One prepared HE29 canary with pinned a5 numerics and new I/O/table adapters.

The enclosing launcher owns the host lease and whole-process-group watchdog.
This worker does not build, submit other jobs, retry, or execute reference pairs.
Source/manifest contracts come from the clean a5 checkout; restored DATA may be
read from a separate verified HE29 data root.  The new adapter Git pin is a
separate identity from the a5 bridge publication pin.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

sys.dont_write_bytecode = True
LANE = Path(__file__).resolve().parents[1]
HE29 = LANE.parent
REPO = HE29.parents[1]
HE29_REL = Path("research/he29_survival_budget_20261018")
PACKED_REVISION = "a5d4711460c09b310b78c9692aa62534b7a843d3"
PACKED_RUNNER_SHA256 = "803e192709a1b5ff9a0732c806a7cff91fd8fe3af69d03e3885efaffe4f388ea"
TABLE_SHA256 = "919ca6f42028bffc37cb208916ee5a9927356eb99344fe467f9b98e30e9fddcd"
WORKER_FLAG = "HE29_HPC64_PROCESS_GROUP_WORKER"
CASE = dict(m=8, r=4, angles=4, q=0., table_nodes=512)
_A5 = None


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_json(path, value):
    """Create-only startup/failure receipt, including before pinned imports."""
    path = Path(path)
    temp = path.with_name(path.name + ".partial")
    with temp.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.link(temp, path)
    finally:
        temp.unlink()
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def query(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
        capture_output=True, text=True, timeout=30).stdout.strip()


def checked_checkout(root, revision):
    if (not isinstance(revision, str) or len(revision) != 40
            or any(c not in "0123456789abcdef" for c in revision)):
        raise ValueError("HE29_HPC_FULL_SOURCE_REVISION_REQUIRED")
    root = Path(root).resolve(strict=True)
    if (not root.is_dir()
            or Path(query(root, "rev-parse", "--show-toplevel")).resolve() != root):
        raise ValueError("HE29_HPC_GIT_ROOT")
    if query(root, "rev-parse", "HEAD") != revision:
        raise ValueError("HE29_HPC_GIT_REVISION")
    if query(root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise ValueError("HE29_HPC_CHECKOUT_NOT_CLEAN")
    return {"root": str(root), "head": revision,
            "tree": query(root, "rev-parse", "HEAD^{tree}"), "clean": True}


def load_a5(packed_root):
    """Import a5 before adapters; reject mixed cached module origins."""
    global _A5
    root = Path(packed_root).resolve(strict=True)
    checked_checkout(root, PACKED_REVISION)
    if _A5 is not None:
        if Path(_A5.REPO).resolve() != root:
            raise ValueError("HE29_HPC_CACHED_A5_ROOT")
        return _A5
    source = root / HE29_REL / "optimization_20261020/src/run_packed.py"
    if (source.is_symlink() or not source.resolve().is_relative_to(root)
            or digest(source) != PACKED_RUNNER_SHA256):
        raise ValueError("HE29_HPC_A5_RUNNER_SOURCE")
    for name in ("reference_runner", "optimized_model", "packed_reference",
                 "refined_source", "reference_contract", "run_vigilode"):
        existing = sys.modules.get(name)
        if existing is not None and not Path(existing.__file__).resolve().is_relative_to(root):
            raise ValueError("HE29_HPC_MIXED_IMPORTED_SOURCE: " + name)
    sys.path.insert(0, str(source.parent))
    spec = importlib.util.spec_from_file_location("he29_hpc_a5_run_packed", source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    for name in ("reference_runner", "optimized_model", "packed_reference",
                 "refined_source", "reference_contract", "run_vigilode"):
        if not Path(sys.modules[name].__file__).resolve().is_relative_to(root):
            raise ValueError("HE29_HPC_IMPORTED_SOURCE_OUTSIDE_A5: " + name)
    _A5 = module
    return module


def check_sources_external(reference_runner, binary, receipt, data_root):
    """The original check_sources, with only DATA's verification root moved.

    PARENT_SHA256, INPUT_SHA256 and source_files remain in the pinned a5 tree.
    The returned current identity keeps the original keys and values so the
    unchanged four-pair baseline contract can compare it directly.
    """
    rr = reference_runner
    data_root = Path(data_root).resolve(strict=True)
    parents = json.loads((rr.ROOT / "provenance/PARENT_SHA256.json").read_text())
    inputs = json.loads((rr.ROOT / "provenance/INPUT_SHA256.json").read_text())
    if len(inputs) != 22 or any(not name.startswith("inputs/") for name in inputs):
        raise ValueError("HE29_HPC_INPUT_MANIFEST_SCOPE")
    rr.verify_manifest(parents, rr.REPO)
    rr.verify_manifest(inputs, data_root)
    state = {"owner_source": rr.OWNER, "parent_sources": parents, "input_sources": inputs,
        "source_files": rr.manifest(sorted((rr.ROOT / "src").glob("*.py")), rr.ROOT),
        "numerical_thread_environment": dict(rr.THREADS),
        "runtime": {"python": rr.sys.version, "numpy": rr.np.__version__,
                    "scipy": rr.scipy.__version__, "platform": rr.platform.platform()}}
    data = json.loads(Path(receipt).read_text())
    server = "research/he25_proper_birth_20261016/src/owner_server.rs"
    binary_sha = rr.digest(binary)
    if (data.get("owner_source") != rr.OWNER or data.get("binary_sha256") != binary_sha
            or data.get("server_source_sha256") != parents[server]):
        raise ValueError("HE29_NATIVE_BUILD_IDENTITY")
    state.update(binary_sha256=binary_sha, build_receipt=data)
    return state, {"data_root": str(data_root), "data_files_sha_verified": len(inputs),
        "manifest_root": str(rr.ROOT), "source_root": str(rr.REPO),
        "input_manifest_sha256": rr.digest(rr.ROOT / "provenance/INPUT_SHA256.json"),
        "parent_manifest_sha256": rr.digest(rr.ROOT / "provenance/PARENT_SHA256.json"),
        "archive_used_as_execution_source": False}


def validate_options(args):
    if type(args.table_workers) is not int or not 1 <= args.table_workers <= 48:
        raise ValueError("HE29_HPC_TABLE_WORKER_BUDGET")
    if type(args.sync_every) is not int or not 1 <= args.sync_every <= 256:
        raise ValueError("HE29_HPC_SYNC_EVERY_BUDGET")
    out, cache = Path(args.out).resolve(), Path(args.table_cache).resolve()
    protected = [REPO.resolve(), Path(args.packed_root).resolve(),
                 Path(args.baseline_campaign).resolve(), Path(args.data_root).resolve()]
    for target in (out, cache):
        if any(target.is_relative_to(root) or root.is_relative_to(target) for root in protected):
            raise ValueError("HE29_HPC_OUTPUT_INSIDE_SOURCE_OR_BASELINE")
    if out.is_relative_to(cache) or cache.is_relative_to(out):
        raise ValueError("HE29_HPC_OUTPUT_CACHE_OVERLAP")


def preflight(args):
    """Read-only full preflight; no CDLL load, native process, or table build."""
    validate_options(args)
    adapter_publication = checked_checkout(REPO, args.source_revision)
    packed_publication = checked_checkout(args.packed_root, PACKED_REVISION)
    runner = load_a5(args.packed_root)
    rr = sys.modules["reference_runner"]
    current, data_provenance = check_sources_external(rr, args.binary,
                                                      args.owner_receipt, args.data_root)
    if any(os.environ.get(k) != v for k, v in runner.THREADS.items()):
        raise ValueError("HE29_SINGLE_THREAD_ENV_REQUIRED")
    if os.environ.get("RAYON_NUM_THREADS") != "1":
        raise ValueError("HE29_OPT_SINGLE_RAYON_THREAD_REQUIRED")
    prior, reused = runner.baseline_contract(args.baseline_campaign, current)
    if prior.get("table_sha256") != TABLE_SHA256:
        raise ValueError("HE29_HPC_SAVED_TABLE_IDENTITY")
    build = runner.verify_build(args.library, args.bridge_receipt)
    original_publication = runner.publication_contract(PACKED_REVISION, build, current)
    return {"schema": "he29.hpc64.preflight.v1", "status": "PASS", "current": current,
        "prior": prior, "reused": reused, "build": build,
        "packed_checkout": packed_publication, "packed_publication": original_publication,
        "adapter_publication": adapter_publication, "data_provenance": data_provenance,
        "new_adapter_sources": runner.manifest(sorted((LANE / "src").glob("*.py")), LANE),
        "native_solver_calls": 0, "source_tables_built": 0}


def load_adapters():
    # The pinned original modules are already loaded by preflight/load_a5.
    sys.path.insert(0, str(LANE / "src"))
    from parallel_source import HPC64RefinedSourceModel
    from batched_native import BatchedNativeOwner
    return HPC64RefinedSourceModel, BatchedNativeOwner


def checked_evidence(owner, path):
    evidence = owner.evidence_telemetry()
    counts = ((evidence.get("records_written"), evidence.get("records_durable"),
               evidence.get("verified_records")),
              (evidence.get("point_records_written"), evidence.get("point_records_durable"),
               evidence.get("verified_point_records"), owner.calls))
    if (evidence.get("complete_gzip_readback") is not True
            or evidence.get("published") is not True or evidence.get("owner_failed") is not False
            or evidence.get("trace_error") is not None
            or any(any(type(v) is not int or v < 0 for v in row) or len(set(row)) != 1
                   for row in counts)
            or Path(path).is_symlink() or not Path(path).is_file()):
        raise ValueError("HE29_HPC_NATIVE_EVIDENCE_NOT_COMPLETE")
    return {**evidence, "gzip_sha256": digest(path), "gzip_bytes": Path(path).stat().st_size}


def run_case(args):
    validate_options(args)
    if os.environ.get(WORKER_FLAG) != "1":
        raise ValueError("HE29_HPC_PARENT_WATCHDOG_REQUIRED")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    owner = None
    try:
        prepared = preflight(args)
        runner = load_a5(args.packed_root)
        model_class, owner_class = load_adapters()
        current, prior = prepared["current"], prepared["prior"]
        phases = {"preflight_s": time.monotonic() - start}
        identity = {**current, **CASE, "bridge": prepared["build"], "reused": prepared["reused"],
            "packed_publication": prepared["packed_publication"],
            "adapter_publication": prepared["adapter_publication"],
            "data_provenance": prepared["data_provenance"],
            "new_adapter_sources": prepared["new_adapter_sources"],
            "rayon_num_threads": "1", "packed_threads": 1,
            "table_workers_limit": args.table_workers, "sync_every_points": args.sync_every,
            "hardkill_unsynchronized_successful_point_bound": args.sync_every - 1,
            "source_table_budget": {"wall_s": 600., "estimated_allocation_bytes": 2*1024**3,
                                    "whole_process_rss_bound": False}}
        runner.atomic_json(out / "IDENTITY.json", identity)
        tick = time.monotonic()
        bridge = runner.PackedBridge(args.library, args.bridge_receipt)
        phases["bridge_load_s"] = time.monotonic() - tick
        owner = owner_class(args.binary, evidence_path=out / "native.jsonl.gz",
                            expected_binary_sha256=current["binary_sha256"],
                            sync_every=args.sync_every)
        with owner:
            tick = time.monotonic()
            model = model_class(owner, runner.GridSpec(m=8, angles=4, q=0., strips=4),
                cache_dir=args.table_cache, max_workers=args.table_workers, chunk_rows=64,
                tabulate=True, source_table_nodes=512, max_table_bytes=2*1024**3,
                max_table_wall_s=600., expected_table_sha256=prior["table_sha256"])
            phases["source_model_and_cache_s"] = time.monotonic() - tick
            table = model.source_table_sha256
            runner.atomic_json(out / "TABLE.json", {"source_table_sha256": table,
                "diagnostics": model.source_table_diagnostics,
                "cache": model.source_table_cache, "execution": model.source_table_execution,
                "execution_scope": "For HIT_VERIFIED, execution describes the saved original cache build."})
            if table != prior["table_sha256"]:
                raise ValueError("HE29_OPT_REBUILT_TABLE_MISMATCH")
            tick = time.monotonic()
            with (out / "SEGMENT_ENDPOINTS.jsonl").open("x") as trace:
                def checkpoint(row):
                    text = json.dumps(row, allow_nan=False, separators=(",", ":")) + "\n"
                    if trace.tell() + len(text.encode()) > 128*1024**2:
                        raise RuntimeError("HE29_OPT_ENDPOINT_TRACE_BUDGET")
                    owner.flush_evidence("segment_checkpoint")
                    trace.write(text)
                    trace.flush()
                    os.fsync(trace.fileno())
                result = runner.solve_packed(model, bridge, checkpoint)
            phases["packed_solve_and_checkpoints_s"] = time.monotonic() - tick
            owner.flush_evidence("before_raw_result")
            runner.atomic_json(out / "PACKED_RAW.json", {"result": result,
                "native_calls": owner.calls, "wall_s": time.monotonic() - start,
                "evidence_before_close": owner.evidence_telemetry()})
            runner.check_result(result)
            comparisons = {method: runner.admit_pair(result, prior["results"][method])
                           for method in ("Radau", "DOP853")}
            calls = owner.calls
            tick = time.monotonic()
        phases["owner_close_and_gzip_readback_s"] = time.monotonic() - tick
        evidence = checked_evidence(owner, out / "native.jsonl.gz")
        runner.atomic_json(out / "NATIVE_EVIDENCE.json", evidence)
        runner.atomic_json(out / "RESULT.json", {
            "schema": "he29.hpc64.canary.v1", "status": "CANARY_COMPLETED_SCOPED",
            "case": CASE, "table_sha256": table, "result": result,
            "comparison_to_saved_baseline": comparisons,
            "native_calls": calls, "wall_s": time.monotonic() - start, "phase_wall_s": phases,
            "native_evidence": evidence, "source_table_cache": model.source_table_cache,
            "source_table_execution": model.source_table_execution,
            "baseline_pairs_reused": 4, "new_baseline_pairs": 0,
            "transport_replays": 0, "source_only_suites_replayed": 0,
            "packed_threads": 1, "continuous_spectrum": "HOLD", "full_eor": "HOLD",
            "global_gas_temperature_bound": "HOLD",
            "upstream_grackle_whole_runtime_equivalence": "HOLD",
            "observational_bianchi_cmb": "HOLD"})
    except BaseException as exc:
        telemetry = None
        if owner is not None:
            try:
                telemetry = owner.evidence_telemetry()
                if not (out / "NATIVE_EVIDENCE.json").exists():
                    atomic_json(out / "NATIVE_EVIDENCE.json", telemetry)
            except BaseException as telemetry_exc:
                telemetry = {"capture_error": repr(telemetry_exc)}
        atomic_json(out / "FAILURE.json", {"status": "HOLD_FIRST_FAILURE", "error": repr(exc),
            "traceback": traceback.format_exc(), "wall_s": time.monotonic() - start,
            "baseline_pairs_created": 0, "transport_replays": 0, "native_evidence": telemetry,
            "retained_raw_files": [name for name in ("TABLE.json", "SEGMENT_ENDPOINTS.jsonl",
                "PACKED_RAW.json", "native.jsonl.gz", "native.jsonl.gz.partial", "NATIVE_EVIDENCE.json")
                if (out / name).exists()]})
        raise


def parse_arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("mode", choices=("preflight", "worker"))
    for name in ("packed-root", "baseline-campaign", "binary", "owner-receipt", "library",
                 "bridge-receipt", "data-root", "out", "table-cache", "source-revision"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--table-workers", type=int, required=True)
    parser.add_argument("--sync-every", type=int, default=256)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_arguments(argv)
    if args.mode == "worker":
        run_case(args)
        return
    validate_options(args)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    try:
        atomic_json(out / "PREFLIGHT.json", preflight(args))
    except BaseException as exc:
        atomic_json(out / "FAILURE.json", {"status": "HOLD_PREFLIGHT", "error": repr(exc),
            "traceback": traceback.format_exc(), "native_solver_calls": 0})
        raise


if __name__ == "__main__":
    main()
