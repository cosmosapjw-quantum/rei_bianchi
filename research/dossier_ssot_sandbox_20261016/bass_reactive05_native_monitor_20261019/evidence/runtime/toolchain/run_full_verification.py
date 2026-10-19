#!/usr/bin/env python3
"""Actual BR05 full test/Clippy gate and release build at frozen identities."""

from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import subprocess
import time
import tomllib


WORK = Path("/workspace/scratch/996fc62899da")
UNIT = WORK / "repo/research/dossier_ssot_sandbox_20261016/bass_reactive05_native_monitor_20261019"
OUT = UNIT / "evidence/runtime"
PREFIX = WORK / "toolchains/rust-1.94.1"
TARGET = WORK / "br05_work/runtime/full_target_20261019"
FROZEN_PATH = WORK / "br05_work/implementation/SOURCE_IDENTITY_FINAL.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if TARGET.exists():
        raise RuntimeError("fresh verification target already exists; inspect before reuse")
    frozen = json.loads(FROZEN_PATH.read_text())
    parents = json.loads((UNIT / "contracts/PARENT_INPUT_SHA256.json").read_text())
    expected = dict(parents)
    expected.update(frozen["new_files"])
    before = {name: sha(UNIT / name) for name in expected}
    if before != expected or len(parents) != 125:
        raise RuntimeError("source identity differs before full verification")
    old_manifest = tomllib.loads((UNIT / "br04/Cargo.toml").read_text())
    new_manifest = tomllib.loads((UNIT / "br05/Cargo.toml").read_text())
    old_targets = {item["name"]: item["path"] for item in old_manifest["test"]}
    new_targets = {item["name"]: item["path"] for item in new_manifest["test"]}
    if any(new_targets.get(name) != path for name, path in old_targets.items()):
        raise RuntimeError("an inherited explicit test target was removed or redirected")
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    write_json(OUT / "FULL_CHECK_START_IDENTITY.json", {
        "started_utc": started,
        "frozen_source_contract": str(FROZEN_PATH),
        "frozen_source_contract_sha256": sha(FROZEN_PATH),
        "parent_inputs": len(parents),
        "new_source_files": len(frozen["new_files"]),
        "all_hashes_match_before": True,
        "source_sha256": before,
        "inherited_test_targets": old_targets,
        "new_explicit_test_targets": new_targets,
        "fresh_cargo_target": str(TARGET),
    })
    env = os.environ.copy()
    env["PATH"] = str(PREFIX / "bin") + ":" + env["PATH"]
    env["LD_LIBRARY_PATH"] = str(PREFIX / "lib") + (
        ":" + env["LD_LIBRARY_PATH"] if env.get("LD_LIBRARY_PATH") else ""
    )
    env["CARGO_HOME"] = str(WORK / "toolchains/cargo-home")
    env["CARGO_TARGET_DIR"] = str(TARGET)
    env["RUSTC"] = str(PREFIX / "bin/rustc")
    env["RUSTDOC"] = str(PREFIX / "bin/rustdoc")
    common = ["--manifest-path", str(UNIT / "br05/Cargo.toml"), "--offline", "--locked"]
    commands = [
        ("ALL_RUST_TESTS", ["cargo", "test", *common, "--all-targets", "--jobs", "2", "--", "--test-threads", "2"]),
        ("STRICT_CLIPPY", ["cargo", "clippy", *common, "--all-targets", "--jobs", "2", "--", "-D", "warnings"]),
        ("RELEASE_NATIVE_BUILD", ["cargo", "build", *common, "--release", "--example", "native_birth_monitor_driver", "--jobs", "2"]),
    ]
    executions = []
    for name, command in commands:
        print(json.dumps({"stage": name, "status": "STARTED"}), flush=True)
        log = OUT / (name + ".log")
        begin = time.monotonic()
        with log.open("xb") as stream:
            completed = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT,
                                       env=env, cwd=UNIT, check=False)
            stream.flush()
            os.fsync(stream.fileno())
        item = {
            "name": name, "command": command, "exit_code": completed.returncode,
            "wall_s": time.monotonic() - begin, "log": log.name,
            "log_sha256": sha(log),
        }
        executions.append(item)
        print(json.dumps(item), flush=True)
        if completed.returncode != 0:
            break

    after = {name: sha(UNIT / name) for name in expected}
    log_text = (OUT / "ALL_RUST_TESTS.log").read_text()
    counts = [tuple(map(int, match)) for match in re.findall(
        r"test result: \w+\. (\d+) passed; (\d+) failed;", log_text
    )]
    good = len(executions) == len(commands) and all(item["exit_code"] == 0 for item in executions)
    binary = TARGET / "release/examples/native_birth_monitor_driver"
    result = {
        "status": "PASS_SOURCE_FROZEN" if good and before == after else "FAILED_OR_SOURCE_CHANGED",
        "started_utc": started,
        "completed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parent_files_verified": len(parents),
        "new_source_files_verified": len(frozen["new_files"]),
        "source_unchanged": before == after,
        "source_sha256_before": before,
        "source_sha256_after_if_changed": None if before == after else after,
        "actual_full_test_counts": {
            "passed": sum(count[0] for count in counts),
            "failed": sum(count[1] for count in counts),
            "harness_groups": len(counts),
        },
        "executions": executions,
        "native_release_binary": str(binary) if binary.exists() else None,
        "native_release_binary_sha256": sha(binary) if binary.exists() else None,
        "native_release_binary_bytes": binary.stat().st_size if binary.exists() else None,
        "native_history_executions": 0,
        "scope": "Actual full all-target tests and strict Clippy on the frozen new source; release build does not execute the native history.",
    }
    write_json(OUT / "FULL_RUST_CLIPPY_VERIFICATION.json", result)
    print(json.dumps({key: result[key] for key in [
        "status", "actual_full_test_counts", "source_unchanged",
        "native_release_binary", "native_release_binary_sha256",
    ]}), flush=True)
    return 0 if result["status"] == "PASS_SOURCE_FROZEN" else 2


if __name__ == "__main__":
    raise SystemExit(main())
