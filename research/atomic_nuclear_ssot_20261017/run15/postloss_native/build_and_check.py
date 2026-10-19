#!/usr/bin/env python3
"""Offline build plus exactly three source-measure CLI controls, with receipts."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def identity(path: Path) -> dict:
    raw = path.read_bytes()
    return {"path": str(path), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crate-root", required=True, type=Path)
    parser.add_argument("--toolchain-prefix", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--generate-lock", action="store_true", help="Only for the first new-crate build when Cargo.lock is absent")
    args = parser.parse_args()
    crate = args.crate_root.resolve(strict=True)
    prefix = args.toolchain_prefix.resolve(strict=True)
    output = args.output_root.absolute()
    if output.exists() or output.is_symlink() or output == crate or crate in output.parents:
        raise ValueError("output-root must be new and external to the source crate")
    output.mkdir(parents=True)
    for name in ["logs", "target", "cargo_home"]:
        (output / name).mkdir()
    validator = Path(__file__).resolve().parent / "validate_cli.py"
    env = dict(os.environ)
    for key in list(env):
        if key.startswith("CARGO_") or key.startswith("RUSTFLAGS") or key in {
            "RUSTC", "RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER", "RUSTDOC", "RUSTDOCFLAGS", "PYTHONPATH", "PYTHONHOME"
        }:
            env.pop(key)
    env.update({"PATH": str(prefix / "bin") + os.pathsep + os.environ.get("PATH", ""),
                "LD_LIBRARY_PATH": str(prefix / "lib"), "RUSTC": str(prefix / "bin/rustc"),
                "CARGO_HOME": str(output / "cargo_home"), "CARGO_TARGET_DIR": str(output / "target"),
                "CARGO_NET_OFFLINE": "true", "PYTHONDONTWRITEBYTECODE": "1"})
    receipt = {"created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "status": "IN_PROGRESS",
               "crate_root": str(crate), "toolchain_prefix": str(prefix), "new_native_ivps": 0,
               "old_nine_tests_rerun": False, "new_cargo_test_executions": 0, "commands": [],
               "source_before": [identity(crate / name) for name in ["Cargo.toml", "src/lib.rs", "src/main.rs"]],
               "validator": identity(validator),
               "environment": {key: env[key] for key in ["PATH", "LD_LIBRARY_PATH", "RUSTC", "CARGO_HOME", "CARGO_TARGET_DIR", "CARGO_NET_OFFLINE"]}}

    def run(name: str, command: list[str], timeout: float = 180) -> str:
        started = time.monotonic()
        print(json.dumps({"stage": name, "status": "STARTED", "command": command}), flush=True)
        result = subprocess.run(command, cwd=crate, env=env, capture_output=True, timeout=timeout)
        stdout = output / "logs" / (name + ".stdout.log")
        stderr = output / "logs" / (name + ".stderr.log")
        stdout.write_bytes(result.stdout)
        stderr.write_bytes(result.stderr)
        row = {"stage": name, "command": command, "cwd": str(crate), "seconds": time.monotonic() - started,
               "returncode": result.returncode, "stdout": identity(stdout), "stderr": identity(stderr)}
        receipt["commands"].append(row)
        print(json.dumps({"stage": name, "status": "COMPLETE" if result.returncode == 0 else "FAILED", "seconds": row["seconds"]}), flush=True)
        if result.returncode:
            raise ValueError("command failed: " + name)
        return result.stdout.decode("utf-8")

    failure = None
    try:
        rustc = run("rustc_version", [str(prefix / "bin/rustc"), "--version", "--verbose"])
        cargo = run("cargo_version", [str(prefix / "bin/cargo"), "--version", "--verbose"])
        if "commit-hash: e408947bfd200af42db322daf0fadfe7e26d3bd1" not in rustc or "commit-hash: 29ea6fb6a5db279426f4cc4e17aa385f05a0cfbc" not in cargo:
            raise ValueError("expected exact Rust 1.94.1 compiler and cargo identities")
        if args.generate_lock:
            if (crate / "Cargo.lock").exists():
                raise ValueError("refusing to regenerate an existing lockfile")
            run("generate_lock", [str(prefix / "bin/cargo"), "generate-lockfile", "--offline"])
        if not (crate / "Cargo.lock").is_file():
            raise ValueError("Cargo.lock required for --locked build")
        receipt["lockfile"] = identity(crate / "Cargo.lock")
        run("release_build", [str(prefix / "bin/cargo"), "build", "--release", "--offline", "--locked", "--jobs", "2"])
        binary = output / "target/release/positive_planck_panel_postloss"
        receipt["binary"] = identity(binary)
        receipt["historical_original_binary_identity_claimed"] = False
        run("three_cli_controls", [sys.executable, "-B", str(validator), "--binary", str(binary), "--output-root", str(output / "controls")], timeout=60)
        control_path = output / "controls/THREE_CLI_CONTROLS.json"
        controls = json.loads(control_path.read_text())
        if controls["status"] != "NUMERICALLY_CHECKED" or len(controls["cases"]) != 3:
            raise ValueError("three bounded CLI controls not established")
        receipt["controls"] = identity(control_path)
        after = [identity(crate / name) for name in ["Cargo.toml", "src/lib.rs", "src/main.rs"]]
        receipt["source_unchanged_by_build"] = after == receipt["source_before"]
        if not receipt["source_unchanged_by_build"]:
            raise ValueError("source changed during the build")
        receipt["status"] = "IMPLEMENTATION_VERIFIED_WITH_THREE_NUMERICAL_CONTROLS"
    except Exception as error:
        failure = error
        receipt["status"] = "FAILED_OR_BLOCKED"
        receipt["error"] = type(error).__name__ + ": " + str(error)
    with (output / "POSTLOSS_NATIVE_BUILD_RECEIPT.json").open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"status": receipt["status"], "binary": receipt.get("binary"), "receipt": str(output / "POSTLOSS_NATIVE_BUILD_RECEIPT.json")}, indent=2))
    if failure is not None:
        raise failure


if __name__ == "__main__":
    main()
