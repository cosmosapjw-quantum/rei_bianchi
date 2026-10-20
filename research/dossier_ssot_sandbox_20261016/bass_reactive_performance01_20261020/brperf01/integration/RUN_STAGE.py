#!/usr/bin/env python3
"""Reproduce the fixed-volume native controls using an already selected Rust runtime.

Run from any directory. Cargo must already see the source-bound offline registry.
Each invocation writes a new output directory; source/owner paths are not edited.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--stage", choices=("science", "bench"), default="science")
    parser.add_argument("--sessions", type=int, default=5)
    parser.add_argument("--iterations", type=int, default=32768)
    parser.add_argument("--pairs", type=int, default=6)
    parser.add_argument("--skip-build", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.sessions <= 10:
        raise SystemExit("sessions must be 1..10")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    here = Path(__file__).resolve().parent
    manifest = here / "Cargo.toml"
    target = Path(os.environ.get("CARGO_TARGET_DIR", str(here / "target"))).resolve()
    env = dict(os.environ, CARGO_TARGET_DIR=str(target))
    commands = []

    def run(argv: list[str], label: str) -> None:
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with (out / f"{label}.log").open("w") as stream:
            completed = subprocess.run(argv, env=env, stdout=stream, stderr=subprocess.STDOUT)
        commands.append({"argv": argv, "started_utc": started, "returncode": completed.returncode, "log": f"{label}.log"})
        (out / "COMMANDS.json").write_text(json.dumps(commands, indent=2) + "\n")
        if completed.returncode:
            raise SystemExit(f"{label} failed with {completed.returncode}; see retained log")

    if not args.skip_build:
        run(["rustfmt", "--edition", "2024", "--check", str(here / "src/lib.rs"), str(here / "src/main.rs")], "FMT")
        run(["cargo", "clippy", "--offline", "--locked", "--manifest-path", str(manifest), "--all-targets", "--", "-D", "warnings"], "CLIPPY")
        run(["cargo", "build", "--offline", "--locked", "--release", "--manifest-path", str(manifest)], "BUILD")
    binary = target / "release/rei_brperf01_integration"
    identity = {
        "binary_sha256": sha(binary),
        "harness_sources": {str(p.relative_to(here)): sha(p) for p in [manifest, here / "Cargo.lock", here / "src/lib.rs", here / "src/main.rs", here / "ANALYZE.py"]},
        "stage": args.stage, "selected_nodes": 8193,
    }
    (out / "IDENTITY.json").write_text(json.dumps(identity, indent=2) + "\n")
    if args.stage == "science":
        for nodes in (4097, 8193):
            destination = out / f"science_{nodes}"
            run([str(binary), str(destination), "science", str(nodes)], f"SCIENCE_{nodes}")
            run(["python3", str(here / "ANALYZE.py"), "science", str(destination)], f"ANALYSIS_{nodes}")
    else:
        # Separate processes run serially; coordinate external workload before use.
        for session in range(args.sessions):
            run([str(binary), str(out / f"session_{session:02d}"), "bench", "8193", str(args.iterations), str(args.pairs)], f"BENCH_{session:02d}")
        run(["python3", str(here / "ANALYZE.py"), "bench", str(out)], "BENCH_ANALYSIS")
    print(json.dumps({"status": "PASS", "stage": args.stage, "out": str(out), "commands": len(commands)}))


if __name__ == "__main__":
    main()
