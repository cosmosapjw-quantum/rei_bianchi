#!/usr/bin/env python3
"""Run scoped native receiver validation and record command exit statuses."""

from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess
import tomllib


def main() -> None:
    here = Path(__file__).resolve().parent
    evidence = here / "evidence"
    manifest = here / "Cargo.toml"
    config = tomllib.loads(manifest.read_text())
    parent = (here / config["dependencies"]["parent"]["path"]).resolve()
    pinned = json.loads((evidence / "ORIGINAL_SOURCE_IDENTITY.json").read_text())
    sources = []
    for relative, record in pinned.items():
        actual = hashlib.sha256((parent / relative).read_bytes()).hexdigest()
        sources.append({"file": relative, "sha256": actual, "matches": actual == record["sha256"]})
    if not all(record["matches"] for record in sources):
        raise SystemExit("Original source identity mismatch")
    common = ["--offline", "--locked", "--manifest-path", str(manifest)]
    commands = [
        ("TEST_DEBUG", ["cargo", "test", *common]),
        ("TEST_RELEASE", ["cargo", "test", "--release", *common]),
        ("CLIPPY", ["cargo", "clippy", "--all-targets", *common, "--", "-D", "warnings"]),
        ("RUSTFMT", ["cargo", "fmt", "--manifest-path", str(manifest), "--", "--check"]),
    ]
    environment = os.environ.copy()
    environment.setdefault("CARGO_TARGET_DIR", str(here / "target"))
    checks = []
    for name, command in commands:
        result = subprocess.run(command, cwd=here, env=environment, capture_output=True, text=True)
        (evidence / f"{name}.log").write_text(result.stdout + result.stderr)
        checks.append({"name": name, "command": command, "exit_code": result.returncode})
    result = {
        "recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "PASS" if all(check["exit_code"] == 0 for check in checks) else "FAIL",
        "source_dependency_files": sources,
        "checks": checks,
        "control_scope": {
            "test_functions_per_profile": 9,
            "direct_rhs_bitwise_comparisons": 1024,
            "midpoint_result_or_error_comparisons": 60,
            "strang_accepted_history_steps": 32,
            "table_trajectory_accuracy_claim": False,
            "expanding_photon_coupled_history_claim": False,
        },
    }
    (evidence / "VERIFICATION.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks": checks}, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
