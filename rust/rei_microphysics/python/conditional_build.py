#!/usr/bin/env python3
"""Clean-build receipt and prelaunch checks for the conditional production binary.

This binds a local research execution to its source and build. It does not
admit a physical model, execute the binary, or certify historical P01 outputs.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

SCHEMA = "rei-conditional-clean-build-v1"
CRATE = Path(__file__).resolve().parents[1]
BUILD_ENV_KEYS = (
    "RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "RUSTC", "RUSTC_WRAPPER",
    "RUSTC_WORKSPACE_WRAPPER", "CARGO_BUILD_TARGET", "CARGO_BUILD_RUSTFLAGS",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes(crate: Path) -> dict[str, str]:
    """The finite source set for this dependency-free crate and its launcher."""
    fixed = ["Cargo.toml", "Cargo.lock", "python/source_bound_interval.py",
             "python/conditional_build.py"]
    paths = [crate / name for name in fixed]
    paths.extend(sorted((crate / "src").rglob("*.rs")))
    if (crate / "build.rs").exists():
        paths.append(crate / "build.rs")
    if not any(path.name == "axisym_conditional.rs" for path in paths):
        raise ValueError("BUILD_SOURCE_SET_MISSING")
    try:
        return {str(path.relative_to(crate)): sha256(path) for path in paths}
    except FileNotFoundError as error:
        raise ValueError("BUILD_SOURCE_FILE_MISSING") from error


def _git(crate: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(crate), *args], text=True).strip()


def clean_revision(crate: Path, sources: dict[str, str]) -> dict:
    root = Path(_git(crate, "rev-parse", "--show-toplevel"))
    if _git(root, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("CLEAN_BUILD_REQUIRES_CLEAN_COMMITTED_REVISION")
    # Ignored files are excluded from status; consumed source must still be
    # tracked in the exact revision recorded by the receipt.
    tracked = set(_git(root, "ls-files").splitlines())
    for name in sources:
        if str((crate / name).relative_to(root)) not in tracked:
            raise ValueError("BUILD_SOURCE_NOT_TRACKED: " + name)
    return {"commit": _git(root, "rev-parse", "HEAD"),
            "tree": _git(root, "rev-parse", "HEAD^{tree}"),
            "clean": True, "repository": str(root)}


def _command(command: list[str], cwd: Path, output: Path, label: str,
             timeout: int = 120) -> dict:
    start = time.monotonic()
    try:
        result = subprocess.run(command, cwd=cwd, text=True, capture_output=True,
                                timeout=timeout, check=False)
        stdout, stderr, code = result.stdout, result.stderr, result.returncode
        status = "EXITED"
    except subprocess.TimeoutExpired as error:
        stdout, stderr = error.stdout or b"", error.stderr or b""
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")
        code, status = None, "TIMEOUT"
    (output / f"{label}.stdout.log").write_text(stdout)
    (output / f"{label}.stderr.log").write_text(stderr)
    return {"command": command, "cwd": str(cwd), "status": status,
            "exit_code": code, "wall_seconds": time.monotonic() - start,
            "stdout_file": f"{label}.stdout.log",
            "stderr_file": f"{label}.stderr.log"}


def build_receipt(crate: Path, output: Path) -> dict:
    """Compile only; never launch the resulting executable or a solver."""
    crate, output = crate.resolve(), output.resolve()
    sources = source_hashes(crate)
    revision = clean_revision(crate, sources)
    # Evidence is first produced outside the checkout so it cannot dirty the
    # source revision during the observed build. It may be published later.
    if output.is_relative_to(Path(revision["repository"])):
        raise ValueError("BUILD_OUTPUT_MUST_BE_OUTSIDE_SOURCE_CHECKOUT")
    output.mkdir(parents=True, exist_ok=False)
    receipt = {"schema": SCHEMA, "status": "BUILD_PENDING",
               "created_utc": datetime.now(timezone.utc).isoformat(),
               "revision": revision, "source_sha256": sources,
               "build_environment": {key: os.environ.get(key, "") for key in BUILD_ENV_KEYS},
               "solver_intervals": 0, "binary_launches": 0,
               "scientific_admission": "HOLD"}
    try:
        cargo = shutil.which("cargo")
        rustc = shutil.which(os.environ.get("RUSTC", "rustc"))
        if cargo is None or rustc is None:
            raise ValueError("BUILD_TOOLCHAIN_UNAVAILABLE")
        receipt["toolchain"] = {}
        for name, executable in (("cargo", cargo), ("rustc", rustc)):
            result = _command([executable, "-Vv"], crate, output, name, 30)
            receipt["toolchain"][name] = result
            if result["exit_code"] != 0:
                raise ValueError("BUILD_TOOLCHAIN_IDENTITY_FAILED")
        target = output / "target"
        if target.exists():
            raise ValueError("BUILD_TARGET_NOT_FRESH")
        command = [cargo, "build", "--locked", "--offline", "--release",
                   "--bin", "axisym_conditional", "--manifest-path",
                   str(crate / "Cargo.toml"), "--target-dir", str(target),
                   "--message-format=json-render-diagnostics"]
        receipt["build"] = _command(command, crate, output, "build")
        receipt["build"]["fresh_target"] = True
        if receipt["build"]["exit_code"] != 0:
            raise ValueError("CLEAN_BUILD_FAILED")
        artifacts = []
        for line in (output / "build.stdout.log").read_text().splitlines():
            row = json.loads(line)
            if (row.get("reason") == "compiler-artifact"
                    and row.get("target", {}).get("name") == "axisym_conditional"
                    and row.get("executable")):
                artifacts.append(Path(row["executable"]).resolve())
        if len(artifacts) != 1 or not artifacts[0].is_relative_to(target):
            raise ValueError("BUILD_EXECUTABLE_NOT_IDENTIFIED")
        if source_hashes(crate) != sources or clean_revision(crate, sources) != revision:
            raise ValueError("SOURCE_CHANGED_DURING_BUILD")
        binary = artifacts[0]
        receipt["binary"] = {"path": str(binary), "sha256": sha256(binary),
                             "bytes": binary.stat().st_size}
        receipt["status"] = "BUILD_PASS"
    except Exception as error:
        receipt["status"] = "BUILD_FAIL"
        receipt["failure"] = {"type": type(error).__name__, "message": str(error)}
        raise
    finally:
        (output / "BUILD_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def validate_build_receipt(crate: Path, binary: Path, receipt_path: Path | None) -> dict:
    """Fail before native launch when a recorded build no longer matches."""
    if receipt_path is None or not receipt_path.is_file():
        raise ValueError("BUILD_RECEIPT_REQUIRED")
    try:
        receipt = json.loads(receipt_path.read_text())
        if (receipt["schema"] != SCHEMA or receipt["status"] != "BUILD_PASS"
                or receipt["revision"]["clean"] is not True
                or receipt["build"]["exit_code"] != 0
                or receipt["build"]["fresh_target"] is not True):
            raise ValueError("BUILD_RECEIPT_NOT_PASS")
        expected_sources = receipt["source_sha256"]
        expected_binary = receipt["binary"]["sha256"]
    except (KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValueError("BUILD_RECEIPT_INVALID") from error
    current = source_hashes(crate)
    if current != expected_sources:
        raise ValueError("BUILD_SOURCE_SHA_MISMATCH")
    if not binary.is_file() or sha256(binary) != expected_binary:
        raise ValueError("BUILD_BINARY_SHA_MISMATCH")
    return {"status": "PRELAUNCH_BUILD_PASS", "receipt_sha256": sha256(receipt_path),
            "source_revision": receipt["revision"], "source_sha256": current,
            "binary_sha256": expected_binary, "binary_path": str(binary.resolve())}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_receipt(CRATE, args.output)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
