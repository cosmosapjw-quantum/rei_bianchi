#!/usr/bin/env python3
"""Use the published group watchdog with unchanged a5 packed entrypoints.

The wrapper only replaces the imported run_process binding.  The a5 builder,
runner, worker argv, scientific preflight and numerical method remain unchanged.
Separate arguments for this wrapper and the original target with ``--``.
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

PACKED_REVISION = "a5d4711460c09b310b78c9692aa62534b7a843d3"
CONTROLLER_REVISION = "ed5adca43f474553a9bce7f5de45d464be5905cb"
HE29_REL = Path("research/he29_survival_budget_20261018")
TARGET_PATHS = {
    "build": HE29_REL / "optimization_20261020/ncp/build_bridge.py",
    "preflight": HE29_REL / "optimization_20261020/src/run_packed.py",
    "canary": HE29_REL / "optimization_20261020/src/run_packed.py",
}
CONTROLLER_PATH = HE29_REL / "orchestration_20261020/src/continue_missing_references.py"
EXECUTION_PATH = Path("research/he28_strip_refinement_20261018/src/execution.py")
SOURCE_SHA256 = {
    "build": "0f1012c0b550c04d35455450c46acb3931d48b0e5b54f1cc0a19dafddbfbe708",
    "preflight": "803e192709a1b5ff9a0732c806a7cff91fd8fe3af69d03e3885efaffe4f388ea",
    "canary": "803e192709a1b5ff9a0732c806a7cff91fd8fe3af69d03e3885efaffe4f388ea",
    "controller": "70d38312c288533b829eadbab8037cc09b4218247ebd6262318fc25cb9f0baad",
    "execution": "876e43d76f0773a8d2c38e262902442c614a68334561f5e2a78024c659edb1c4",
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path, data):
    """Create one boundary receipt atomically, without replacing prior bytes."""
    path = Path(path)
    temp = path.with_name(path.name + ".partial")
    with temp.open("x") as out:
        json.dump(data, out, indent=2, sort_keys=True, allow_nan=False)
        out.write("\n")
        out.flush()
        os.fsync(out.fileno())
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
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True,
        text=True, timeout=30,
    ).stdout.strip()


def checked_root(path, revision):
    root = Path(path).resolve(strict=True)
    if not root.is_dir() or Path(query(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise ValueError("HE29_PACKED_ENTRY_GIT_ROOT")
    if query(root, "rev-parse", "HEAD") != revision:
        raise ValueError("HE29_PACKED_ENTRY_GIT_REVISION")
    if query(root, "status", "--porcelain=v1", "--untracked-files=no"):
        raise ValueError("HE29_PACKED_ENTRY_TRACKED_DIRTY")
    return root, {"root": str(root), "head": revision,
                  "tree": query(root, "rev-parse", "HEAD^{tree}"),
                  "tracked_clean": True}


def checked_source(root, relative, expected):
    path = root / relative
    if (path.is_symlink() or not path.is_file()
            or not path.resolve().is_relative_to(root) or digest(path) != expected):
        raise ValueError("HE29_PACKED_ENTRY_SOURCE_IDENTITY: " + str(relative))
    return path


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError("HE29_PACKED_ENTRY_IMPORT_SPEC")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def parse_arguments(argv):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("mode", choices=tuple(TARGET_PATHS))
    parser.add_argument("--packed-root", required=True)
    parser.add_argument("--controller-root", required=True)
    parser.add_argument("--boundary-out", required=True)
    if "--" not in argv:
        parser.error("separate wrapper options and original target arguments with --")
    split = argv.index("--")
    args = parser.parse_args(argv[:split])
    target_args = list(argv[split + 1:])
    target = argparse.ArgumentParser(prog="pinned " + args.mode, allow_abbrev=False)
    target.add_argument("--out", required=True)
    target.add_argument("--source-revision", required=True)
    if args.mode == "build":
        target.add_argument("--vigilode-checkout")
        target.add_argument("--cargo")
        target.add_argument("--rustc")
        target.add_argument("--offline", action="store_true")
    else:
        for name in ("baseline-campaign", "binary", "owner-receipt", "library", "bridge-receipt"):
            target.add_argument("--" + name, required=True)
        target.add_argument("--wall-s", type=float, default=900.)
    options = target.parse_args(target_args)
    if options.source_revision != PACKED_REVISION:
        target.error("source-revision must be the fixed a5 packed code pin")
    if args.mode != "build" and (not math.isfinite(options.wall_s) or not 0 < options.wall_s <= 3600):
        target.error("wall budget must be finite, positive and <=3600 seconds")
    return args, target_args, Path(options.out).resolve()


def main(argv=None):
    original_args = list(sys.argv[1:] if argv is None else argv)
    args, target_args, target_out = parse_arguments(original_args)
    boundary = Path(args.boundary_out).resolve()
    roots = [Path(args.packed_root).resolve(), Path(args.controller_root).resolve()]
    if (any(boundary.is_relative_to(root) or target_out.is_relative_to(root) for root in roots)
            or boundary.is_relative_to(target_out) or target_out.is_relative_to(boundary)):
        raise ValueError("HE29_PACKED_ENTRY_OUTPUTS_MUST_BE_SEPARATE_OUTSIDE_CHECKOUTS")
    boundary.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    atomic_json(boundary / "STARTED.json", {
        "schema": "he29.packed_entry.boundary.v1", "mode": args.mode,
        "wrapper_sha256": digest(__file__), "wrapper_argv": original_args,
        "target_out": str(target_out), "python": sys.version,
        "scientific_admission": "READ_UNCHANGED_TARGET_RESULTS_SEPARATELY",
    })
    old_argv, old_path = sys.argv[:], sys.path[:]
    try:
        if target_out.exists() or target_out.is_symlink():
            raise FileExistsError("HE29_PACKED_ENTRY_TARGET_ALREADY_EXISTS: " + str(target_out))
        packed, packed_id = checked_root(args.packed_root, PACKED_REVISION)
        controller, controller_id = checked_root(args.controller_root, CONTROLLER_REVISION)
        target_path = checked_source(packed, TARGET_PATHS[args.mode], SOURCE_SHA256[args.mode])
        watchdog_path = checked_source(controller, CONTROLLER_PATH, SOURCE_SHA256["controller"])
        execution_path = checked_source(packed, EXECUTION_PATH, SOURCE_SHA256["execution"])
        target_argv = [str(target_path)]
        if args.mode != "build":
            target_argv.append(args.mode)
        target_argv.extend(target_args)
        atomic_json(boundary / "SOURCE_IDENTITY.json", {
            "packed": packed_id, "controller": controller_id,
            "target_path": str(target_path), "target_sha256": digest(target_path),
            "watchdog_path": str(watchdog_path), "watchdog_sha256": digest(watchdog_path),
            "execution_path": str(execution_path), "execution_sha256": digest(execution_path),
            "target_argv": target_argv,
            "replacement": "target.run_process = partial(ed5.run_process_group, execution=original_execution)",
            "original_source_files_modified": False,
        })
        watchdog = load_module(watchdog_path, "_he29_packed_entry_watchdog")
        execution = load_module(execution_path, "_he29_packed_entry_execution")
        # Direct script execution adds the target's directory to sys.path.
        sys.path.insert(0, str(target_path.parent))
        target = load_module(target_path, "_he29_packed_entry_target")
        target.run_process = functools.partial(watchdog.run_process_group, execution=execution)
        sys.argv = target_argv
        try:
            target.main()
        except SystemExit as exc:
            if exc.code not in (None, 0):
                raise
        atomic_json(boundary / "RECEIPT.json", {
            "status": "UNCHANGED_TARGET_RETURNED_SUCCESS", "mode": args.mode,
            "wall_s": time.monotonic() - start,
            "watchdog_source": CONTROLLER_REVISION, "packed_source": PACKED_REVISION,
            "scientific_admission": "READ_UNCHANGED_TARGET_RESULTS_SEPARATELY",
        })
        return 0
    except BaseException as exc:
        atomic_json(boundary / "FAILURE.json", {
            "status": "HOLD_FIRST_BOUNDARY_OR_TARGET_FAILURE", "mode": args.mode,
            "error": repr(exc), "traceback": traceback.format_exc(),
            "wall_s": time.monotonic() - start, "target_out": str(target_out),
            "existing_target_evidence_preserved": True,
        })
        raise
    finally:
        sys.argv, sys.path = old_argv, old_path


if __name__ == "__main__":
    raise SystemExit(main())
