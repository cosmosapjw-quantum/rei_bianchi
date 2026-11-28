#!/usr/bin/env python3
"""Bounded compiler parallelism around the unchanged pinned a5 builder.

Only Cargo's job budget and the already validated ed5 process watchdog are
adapted. Compiler, frozen dependency graph, bridge bytes and numeric flags
remain the original builder's responsibility. No numerical execution occurs.
"""
from __future__ import annotations

import argparse
import functools
import importlib.util
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from hpc_canary import checked_checkout, digest, REPO, HE29_REL, PACKED_REVISION

CONTROLLER_REVISION = "ed5adca43f474553a9bce7f5de45d464be5905cb"
BUILDER = HE29_REL / "optimization_20261020/ncp/build_bridge.py"
WATCHDOG = HE29_REL / "orchestration_20261020/src/continue_missing_references.py"
EXECUTION = Path("research/he28_strip_refinement_20261018/src/execution.py")
HASHES = {
    "builder": "0f1012c0b550c04d35455450c46acb3931d48b0e5b54f1cc0a19dafddbfbe708",
    "watchdog": "70d38312c288533b829eadbab8037cc09b4218247ebd6262318fc25cb9f0baad",
    "execution": "876e43d76f0773a8d2c38e262902442c614a68334561f5e2a78024c659edb1c4",
}


def load_checked(path, name, expected):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or digest(path) != expected:
        raise ValueError("HE29_HPC_BUILD_SOURCE_IDENTITY: " + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def watchdog_for(packed_root, controller_root):
    checked_checkout(packed_root, PACKED_REVISION)
    checked_checkout(controller_root, CONTROLLER_REVISION)
    execution = load_checked(Path(packed_root) / EXECUTION,
                             "he29_hpc_execution", HASHES["execution"])
    watchdog = load_checked(Path(controller_root) / WATCHDOG,
                            "he29_hpc_watchdog", HASHES["watchdog"])
    return functools.partial(watchdog.run_process_group, execution=execution)


def adapt_builder(target, jobs, revision, run_process):
    if type(jobs) is not int or not 1 <= jobs <= 8:
        raise ValueError("HE29_HPC_BUILD_JOB_BUDGET")
    original_checked, original_json = target.checked, target.atomic_json

    def checked(argv, output, label, wall):
        argv = list(argv)
        if label == "build":
            if len(argv) < 2 or argv[1] != "build" or "--jobs" in argv or "-j" in argv:
                raise ValueError("HE29_HPC_UNEXPECTED_BUILD_ARGV")
            # CLI override and environment agree; the original builder wrote 2.
            os.environ["CARGO_BUILD_JOBS"] = str(jobs)
            argv.extend(["--jobs", str(jobs)])
        return original_checked(argv, output, label, wall)

    def atomic_json(path, value):
        if Path(path).name == "BUILD_IDENTITY.json":
            if value.get("build_jobs") != 2 or value.get("physical_runs") != 0:
                raise ValueError("HE29_HPC_UNEXPECTED_BUILD_RECEIPT")
            value["build_jobs"] = jobs
            value["resource_adapter"] = {
                "source_revision": revision, "source_sha256": digest(__file__),
                "original_build_jobs": 2, "effective_build_jobs": jobs,
                "watchdog_revision": CONTROLLER_REVISION,
                "numeric_flags_or_bridge_source_modified": False,
            }
        return original_json(path, value)

    target.run_process = run_process
    target.checked = checked
    target.atomic_json = atomic_json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    for name in ("packed-root", "controller-root", "out", "source-revision"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--jobs", type=int, required=True)
    parser.add_argument("--vigilode-checkout")
    parser.add_argument("--cargo", default="cargo")
    parser.add_argument("--rustc", default="rustc")
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args(argv)
    checked_checkout(REPO, args.source_revision)
    out = Path(args.out).resolve()
    for root in (REPO, Path(args.packed_root).resolve(), Path(args.controller_root).resolve()):
        if out.is_relative_to(root) or root.is_relative_to(out):
            raise ValueError("HE29_HPC_BUILD_OUTPUT_SOURCE_OVERLAP")
    if out.exists() or out.is_symlink():
        raise FileExistsError(out)
    run_process = watchdog_for(args.packed_root, args.controller_root)
    target = load_checked(Path(args.packed_root) / BUILDER,
                          "he29_hpc_pinned_builder", HASHES["builder"])
    adapt_builder(target, args.jobs, args.source_revision, run_process)
    target_argv = [str(Path(args.packed_root) / BUILDER), "--out", str(out),
                   "--source-revision", PACKED_REVISION,
                   "--cargo", args.cargo, "--rustc", args.rustc]
    if args.vigilode_checkout:
        target_argv += ["--vigilode-checkout", args.vigilode_checkout]
    if args.offline:
        target_argv.append("--offline")
    previous = sys.argv
    try:
        sys.argv = target_argv
        target.main()
    finally:
        sys.argv = previous


if __name__ == "__main__":
    main()
