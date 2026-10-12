#!/usr/bin/env python3
"""Capture a clean native build and affected tests without running a history.

The original conditional_build.py creates the BUILD_RECEIPT consumed by
NativeConsumer. Formatting failures are recorded without suppressing a build,
tests, or failure artifacts. Only temporary copies may be formatted.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import time
import traceback

sys.dont_write_bytecode = True
REPOSITORY = Path(__file__).resolve().parents[2]
CRATE = REPOSITORY / "rust/rei_microphysics"
SCHEMA = "rei-event-bridge-02-native-capture-v1"
AFFECTED_RUST = [
    "rust/rei_microphysics/src/axisym_conditional.rs",
    "rust/rei_microphysics/src/ft03_controlled.rs",
]
EXTRA_SOURCES = [
    "rust/rei_microphysics/tests/ft03_controlled.rs",
    "research/event_bridge_20261012/build_and_capture.py",
    ".github/workflows/event-bridge-02.yml",
    ".github/workflows/verify.yml",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n")


def load_build_gate():
    path = CRATE / "python/conditional_build.py"
    spec = importlib.util.spec_from_file_location("conditional_build_capture", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("CONDITIONAL_BUILD_MODULE_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(command: list[str], log_dir: Path, label: str, timeout: int) -> dict:
    start = time.monotonic()
    try:
        result = subprocess.run(command, cwd=REPOSITORY, text=True,
                                capture_output=True, check=False, timeout=timeout)
        stdout, stderr, code, state = result.stdout, result.stderr, result.returncode, "EXITED"
    except subprocess.TimeoutExpired as error:
        stdout, stderr = error.stdout or "", error.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")
        code, state = None, "TIMEOUT"
    (log_dir / f"{label}.stdout.log").write_text(stdout)
    (log_dir / f"{label}.stderr.log").write_text(stderr)
    return {"command": command, "cwd": str(REPOSITORY), "status": state,
            "exit_code": code, "wall_seconds": time.monotonic() - start,
            "stdout_file": f"logs/{label}.stdout.log",
            "stderr_file": f"logs/{label}.stderr.log"}


def frozen_packet_hashes() -> dict[str, str]:
    """Read constants without importing the NumPy/SciPy history runner."""
    module = ast.parse((CRATE / "python/source_bound_interval.py").read_text())
    values = {}
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {
                    "FROZEN_INPUTS", "REFERENCE_JSON_SHA"
                }:
                    values[target.id] = ast.literal_eval(node.value)
    required = dict(values["FROZEN_INPUTS"])
    required["evidence/extended.json"] = values["REFERENCE_JSON_SHA"]
    return {"research/physical_provider_20261010/" + name: sha
            for name, sha in required.items()}


def copy_sources(payload: Path, sources: dict[str, str]) -> None:
    for relative, expected in sources.items():
        source = REPOSITORY / relative
        if digest(source) != expected:
            raise RuntimeError("SOURCE_CHANGED_BEFORE_CAPTURE: " + relative)
        target = payload / "source_tree" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if digest(target) != expected:
            raise RuntimeError("CAPTURE_SOURCE_SHA_MISMATCH: " + relative)


def archive_payload(output: Path, payload: Path) -> dict:
    entries = []
    for path in sorted(payload.rglob("*")):
        if path.is_file():
            entries.append({"path": str(path.relative_to(payload)),
                            "sha256": digest(path), "bytes": path.stat().st_size,
                            "mode": oct(path.stat().st_mode & 0o777)})
    write_json(payload / "MANIFEST.json", {"schema": "sha256-payload-v1", "files": entries})
    archive = output / "event-bridge-02-native.tar.gz"
    with tarfile.open(archive, "w:gz") as stream:
        for path in sorted(payload.rglob("*")):
            if path.is_file():
                stream.add(path, arcname=str(path.relative_to(payload)), recursive=False)
    return {"path": str(archive), "bytes": archive.stat().st_size,
            "sha256": digest(archive), "payload_files": len(entries) + 1,
            "permission_preservation": "Native executable mode preserved inside tar"}


def capture(output: Path) -> bool:
    output = output.resolve()
    if output.is_relative_to(REPOSITORY):
        raise ValueError("CAPTURE_OUTPUT_MUST_BE_OUTSIDE_CHECKOUT")
    output.mkdir(parents=True, exist_ok=False)
    payload = output / "payload"
    logs = payload / "logs"
    logs.mkdir(parents=True)
    start = time.monotonic()
    record = {
        "schema": SCHEMA, "status": "CAPTURE_PENDING",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "declared_base_commit": "1400093cdd121d8e6adb51ffeb360102a48653bf",
        "scientific_admission": "HOLD", "scientific_history_runs": 0,
        "production_binary_launches": 0,
        "scope": "Clean release build and affected native component tests; no IVP or transport campaign",
        "github": {name: os.environ.get(name, "") for name in (
            "GITHUB_REPOSITORY", "GITHUB_SHA", "GITHUB_REF", "GITHUB_RUN_ID",
            "GITHUB_RUN_ATTEMPT", "RUNNER_OS", "RUNNER_ARCH")},
        "test_environment": {name: os.environ.get(name, "") for name in (
            "CARGO_BUILD_JOBS", "RUST_BACKTRACE", "PYTHONDONTWRITEBYTECODE")},
        "checks": [],
    }
    success = False
    try:
        gate = load_build_gate()
        build_sources = gate.source_hashes(CRATE)
        revision = gate.clean_revision(CRATE, build_sources)
        record["revision"] = revision
        expected_head = os.environ.get("GITHUB_SHA")
        if expected_head and revision["commit"] != expected_head:
            raise RuntimeError("GITHUB_CHECKOUT_HEAD_MISMATCH")
        sources = {"rust/rei_microphysics/" + name: sha
                   for name, sha in build_sources.items()}
        sources.update({name: digest(REPOSITORY / name) for name in EXTRA_SOURCES})
        physical = frozen_packet_hashes()
        for name, expected in physical.items():
            if digest(REPOSITORY / name) != expected:
                raise RuntimeError("FROZEN_PACKET_SHA_MISMATCH: " + name)
        sources.update(physical)
        record["source_sha256"] = sources
        record["frozen_physical_input_sha256"] = physical
        copy_sources(payload, sources)

        cargo = shutil.which("cargo")
        rustfmt = shutil.which("rustfmt")
        if cargo is None:
            raise RuntimeError("BUILD_TOOLCHAIN_UNAVAILABLE")
        formatting = run([cargo, "fmt", "--manifest-path", str(CRATE / "Cargo.toml"),
                          "--all", "--", "--check"], logs, "format_check", 30)
        record["formatting"] = formatting
        # A formatting-only failure must not hide build/test evidence.
        if formatting["exit_code"] != 0 and rustfmt is not None:
            copies = []
            for name in AFFECTED_RUST:
                target = payload / "formatted" / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(REPOSITORY / name, target)
                copies.append(str(target))
            record["format_temporary_copies"] = run(
                [rustfmt, "--edition", "2021", *copies], logs, "format_copies", 30)
            record["formatted_source_sha256"] = {
                name: digest(payload / "formatted" / name) for name in AFFECTED_RUST}
        if rustfmt is not None:
            record["rustfmt_identity"] = run([rustfmt, "--version"], logs, "rustfmt", 30)

        build_dir = output / "clean-build"
        build = gate.build_receipt(CRATE, build_dir)
        record["build_status"] = build["status"]
        record["build_environment"] = build["build_environment"]
        destination = payload / "binary/axisym_conditional"
        destination.parent.mkdir()
        shutil.copy2(Path(build["binary"]["path"]), destination)
        shutil.copy2(build_dir / "BUILD_RECEIPT.json", payload / "BUILD_RECEIPT.json")
        record["downloaded_layout_prelaunch_validation"] = gate.validate_build_receipt(
            CRATE, destination, payload / "BUILD_RECEIPT.json")

        target = output / "test-target"
        for label, selection in [
            ("axisym_conditional", ["--lib", "axisym_conditional"]),
            ("ft03_controlled", ["--test", "ft03_controlled"]),
        ]:
            check = run([cargo, "test", "--locked", "--offline", "--manifest-path",
                         str(CRATE / "Cargo.toml"), "--target-dir", str(target),
                         *selection, "--", "--nocapture"], logs, label, 120)
            text = (logs / f"{label}.stdout.log").read_text()
            summaries = re.findall(r"test result: (\w+)\. (\d+) passed; (\d+) failed", text)
            check["test_summaries"] = [{"status": state, "passed": int(passed),
                                         "failed": int(failed)}
                                        for state, passed, failed in summaries]
            check["passed_nonempty_target"] = (
                check["exit_code"] == 0 and bool(summaries)
                and all(state == "ok" and int(passed) > 0 and int(failed) == 0
                        for state, passed, failed in summaries))
            record["checks"].append(check)

        if gate.source_hashes(CRATE) != build_sources:
            raise RuntimeError("SOURCE_CHANGED_DURING_CAPTURE")
        if gate.clean_revision(CRATE, build_sources) != revision:
            raise RuntimeError("REVISION_CHANGED_DURING_CAPTURE")
        for name, expected in sources.items():
            if digest(REPOSITORY / name) != expected:
                raise RuntimeError("CAPTURE_INPUT_CHANGED: " + name)
        record["checkout_unchanged"] = True
        native_pass = all(check["passed_nonempty_target"] for check in record["checks"])
        success = native_pass and formatting["exit_code"] == 0
        record["status"] = (
            "CAPTURE_PASS" if success else
            "NATIVE_TESTS_PASS_FORMAT_REPAIR_REQUIRED" if native_pass else
            "NATIVE_TEST_FAILURE")
    except Exception as error:
        record["status"] = "CAPTURE_FAIL"
        record["failure"] = {"type": type(error).__name__, "message": str(error)}
        (logs / "capture_exception.log").write_text(traceback.format_exc())
    finally:
        build_dir = output / "clean-build"
        if build_dir.exists():
            for path in build_dir.glob("*.log"):
                shutil.copy2(path, logs / path.name)
            receipt = build_dir / "BUILD_RECEIPT.json"
            if receipt.is_file():
                shutil.copy2(receipt, payload / "BUILD_RECEIPT.json")
        record["wall_seconds"] = time.monotonic() - start
        write_json(payload / "CAPTURE_RECEIPT.json", record)
        archive = archive_payload(output, payload)
        write_json(output / "ARTIFACT_RECEIPT.json", archive)
        print(json.dumps({"status": record["status"], "artifact": archive}, indent=2))
    return success


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="Fresh evidence directory outside the clean checkout")
    args = parser.parse_args()
    raise SystemExit(0 if capture(args.output) else 1)


if __name__ == "__main__":
    main()
