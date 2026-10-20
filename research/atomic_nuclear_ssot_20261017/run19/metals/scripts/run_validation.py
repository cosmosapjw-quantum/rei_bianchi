#!/usr/bin/env python3
"""Focused independent-crate compatibility tests and pointwise scan, no IVPs."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import tomllib


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--prefix", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--target-dir", type=Path, required=True)
    p.add_argument("--test-target", choices=("all", "trace_providers"), default="all")
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    a.output.mkdir(parents=True, exist_ok=False)
    a.target_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.update(PATH=str(a.prefix / "bin") + os.pathsep + env.get("PATH", ""),
               CARGO_TARGET_DIR=str(a.target_dir.resolve()), CARGO_BUILD_JOBS="2")
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    receipt = {"schema": "rei-run19-metals-focused-validation-v1", "started_utc": started,
               "crate": str(root), "python": sys.version, "platform": platform.platform(),
               "explicit_environment": {k: env[k] for k in ("CARGO_TARGET_DIR", "CARGO_BUILD_JOBS")},
               "prefix": str(a.prefix), "commands": [], "status": "IN_PROGRESS",
               "whole_gas_or_radiation_runs": 0, "trajectory_integrations": 0}
    receipt_path = a.output / "EXECUTION_RECEIPT.json"

    def write_receipt():
        receipt_path.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")

    def command(name, argv):
        before = time.perf_counter()
        result = subprocess.run(argv, cwd=root, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=120, check=False)
        wall = time.perf_counter() - before
        (a.output / (name + ".stdout")).write_bytes(result.stdout)
        (a.output / (name + ".stderr")).write_bytes(result.stderr)
        receipt["commands"].append({"name": name, "argv": [str(x) for x in argv],
            "cwd": str(root), "exit_code": result.returncode, "wall_seconds": wall,
            "stdout": name + ".stdout", "stderr": name + ".stderr"})
        write_receipt()
        if result.returncode:
            receipt["status"] = "FAILED"
            write_receipt()
            raise RuntimeError(f"{name} failed: {result.returncode}; see preserved stderr")
        return result

    try:
        command("rustc_version", [str(a.prefix / "bin/rustc"), "--version", "--verbose"])
        command("cargo_version", [str(a.prefix / "bin/cargo"), "--version", "--verbose"])
        if not (root / "Cargo.lock").exists():
            command("generate_lockfile", [str(a.prefix / "bin/cargo"), "generate-lockfile", "--offline"])
        selection = ["--tests"] if a.test_target == "all" else ["--test", a.test_target]
        command("focused_tests", [str(a.prefix / "bin/cargo"), "test", "--offline", "--locked",
                                  *selection, "--", "--nocapture"])
        command("build_scan", [str(a.prefix / "bin/cargo"), "build", "--offline", "--locked",
                               "--release", "--example", "temperature_scan"])
        binary = a.target_dir / "release/examples/temperature_scan"
        result = command("temperature_scan", [str(binary), "--output", str(a.output / "scan")])
        summary = json.loads(result.stdout)
        (a.output / "NUMERICAL_SUMMARY.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
        receipt["binary"] = {"path": str(binary), "bytes": binary.stat().st_size,
                              "sha256": hashlib.sha256(binary.read_bytes()).hexdigest()}
        native = json.loads((root / "provenance/NATIVE_OWNER_BEFORE.json").read_text())
        before_files = native["files"]
        cargo = tomllib.loads((root / "Cargo.toml").read_text())
        dependency = cargo["dependencies"]["rei_iso_couple_reference"]["path"]
        native_root = (root / dependency).resolve()
        receipt["native_dependency_path"] = str(native_root)
        changed = []
        for e in before_files:
            b = (native_root / e["path"]).read_bytes()
            if len(b) != e["bytes"] or hashlib.sha256(b).hexdigest() != e["sha256"]:
                changed.append(e["path"])
        receipt["native_owner_original_files"] = len(before_files)
        receipt["native_owner_changed_files"] = changed
        if changed:
            raise RuntimeError("unexpected mutation of frozen native dependency")
        receipt["test_scope"] = {"preserved_donor_tests_executed": 4 if a.test_target == "all" else 0,
                                 "new_integration_tests_executed": 6,
                                 "dependency_native_test_suite_run": False}
        receipt["status"] = "PASS_SCOPED"
        receipt["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        write_receipt()
        print(json.dumps({"receipt": str(receipt_path), "status": receipt["status"],
                          "numerical_summary": summary}, indent=2))
    except Exception as exc:
        receipt["status"] = "FAILED"
        receipt["failure"] = repr(exc)
        write_receipt()
        raise


if __name__ == "__main__":
    main()
