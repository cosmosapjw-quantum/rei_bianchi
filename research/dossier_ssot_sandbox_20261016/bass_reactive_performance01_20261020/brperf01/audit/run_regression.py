#!/usr/bin/env python3
"""Run the immutable BR05/BR06 regression gate in the recovered runtime.

Invoke after sourcing ../runtime/env.sh. Only audit/ files are written. Cargo
is invoked from audit/ with explicit manifest paths, so the recovered CARGO_HOME
registry configuration is used without editing BR06's historical local config.
"""

from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import subprocess
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
UNIT = ROOT / "repo/research/dossier_ssot_sandbox_20261016/bass_reactive06_vigilode_reference_20261019"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot():
    result = {}
    for base in [UNIT / "parent/br05", UNIT / "parent/crate", UNIT / "br06"]:
        for path in sorted(base.rglob("*")):
            if path.is_file() and "target" not in path.parts:
                result[str(path.relative_to(UNIT))] = sha(path)
    return result


def dump(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + "\n")


def main():
    environment = os.environ.copy()
    environment.update({
        "CARGO_TARGET_DIR": str(HERE / "target"),
        "CARGO_BUILD_JOBS": "2",
        "CARGO_INCREMENTAL": "0",
        "CARGO_PROFILE_DEV_DEBUG": "0",
        "CARGO_PROFILE_TEST_DEBUG": "0",
        "CARGO_NET_OFFLINE": "true",
    })
    before = snapshot()
    dump("SOURCE_BEFORE.json", before)
    versions = {}
    for key, command in [
        ("rustc", ["rustc", "--version"]),
        ("cargo", ["cargo", "--version"]),
        ("clippy", ["cargo", "clippy", "--version"]),
        ("rustfmt", ["rustfmt", "--version"]),
    ]:
        versions[key] = subprocess.check_output(command, cwd=HERE, env=environment, text=True).strip()
    if not versions["rustc"].startswith("rustc 1.94.1 "):
        raise RuntimeError("Required recovered Rust 1.94.1 was not activated")
    dump("RUNTIME.json", {"versions": versions, "environment": {
        key: environment.get(key) for key in ["CARGO_HOME", "CARGO_TARGET_DIR", "CARGO_BUILD_JOBS", "CARGO_INCREMENTAL", "CARGO_PROFILE_DEV_DEBUG", "CARGO_PROFILE_TEST_DEBUG", "RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "RUSTC_WRAPPER"]
    }, "cwd": str(HERE), "registry_config_sha256": sha(Path(environment["CARGO_HOME"]) / "config.toml")})
    commands = []
    for label, manifest in [("PARENT", UNIT / "parent/br05/Cargo.toml"), ("BR06", UNIT / "br06/Cargo.toml")]:
        commands.append((label + "_TESTS", ["cargo", "test", "--locked", "--offline", "--all-targets", "--manifest-path", str(manifest)]))
    for label, manifest in [("PARENT", UNIT / "parent/br05/Cargo.toml"), ("BR06", UNIT / "br06/Cargo.toml")]:
        commands.append((label + "_CLIPPY", ["cargo", "clippy", "--locked", "--offline", "--all-targets", "--manifest-path", str(manifest), "--", "-D", "warnings"]))
    wrappers = ["fixture.rs", "quadrature.rs", "main.rs", "lib.rs", "vigilode_moments.rs", "vigilode_native.rs"]
    commands.append(("BR06_SCOPED_RUSTFMT", ["rustfmt", "--check", "--edition", "2024", "--config", "skip_children=true", *[str(UNIT / "br06/src" / name) for name in wrappers]]))
    runs = []
    for label, command in commands:
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        begin = time.monotonic()
        out = HERE / (label + ".stdout.log")
        err = HERE / (label + ".stderr.log")
        intent = {"label": label, "command": command, "cwd": str(HERE), "started_utc": started}
        dump(label + ".intent.json", intent)
        print(json.dumps({"label": label, "status": "RUNNING"}), flush=True)
        with out.open("xb") as stdout, err.open("xb") as stderr:
            try:
                result = subprocess.run(command, cwd=HERE, env=environment, stdout=stdout, stderr=stderr, timeout=600)
                code = result.returncode
                status = "PASS" if code == 0 else "COMMAND_FAILED"
            except subprocess.TimeoutExpired:
                code = None
                status = "TIMEOUT"
        record = {**intent, "exit_code": code, "status": status, "wall_seconds": time.monotonic() - begin,
                  "stdout_sha256": sha(out), "stderr_sha256": sha(err)}
        if label.endswith("_TESTS"):
            matches = re.findall(r"test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out", out.read_text())
            record["test_harness_summaries"] = len(matches)
            for index, key in enumerate(["passed", "failed", "ignored", "measured", "filtered_out"], start=1):
                record[key] = sum(int(match[index]) for match in matches)
            record["all_harness_results_ok"] = all(match[0] == "ok" for match in matches)
        dump(label + ".json", record)
        runs.append(record)
        print(json.dumps({key: record[key] for key in ["label", "status", "wall_seconds", "passed", "failed"] if key in record}), flush=True)
    after = snapshot()
    dump("SOURCE_AFTER.json", after)
    changed = sorted(key for key in before.keys() | after.keys() if before.get(key) != after.get(key))
    counts = {run["label"]: run.get("passed") for run in runs if run["label"].endswith("_TESTS")}
    verified = (all(run["status"] == "PASS" for run in runs) and not changed
                and counts == {"PARENT_TESTS": 233, "BR06_TESTS": 16}
                and all(run.get("failed", 0) == 0 for run in runs))
    summary = {"status": "COMPLETE_VERIFIED" if verified else "REVIEW_REQUIRED", "versions": versions,
               "runs": runs, "source_files_checked": len(before), "changed_source_files": changed,
               "expected_test_counts": {"PARENT_TESTS": 233, "BR06_TESTS": 16}, "actual_test_counts": counts,
               "format_scope": "Only six reconstructed BR06 wrapper/module files, skip_children=true; preserved reference/tests/large physical owners not formatted",
               "scientific_interpretation": "Current runtime full regression of preserved source; no new convergence or performance claim"}
    dump("REGRESSION_VERIFICATION.json", summary)
    print(json.dumps({"status": summary["status"], "counts": counts, "source_files_checked": len(before), "changed": changed}), flush=True)
    if not verified:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
