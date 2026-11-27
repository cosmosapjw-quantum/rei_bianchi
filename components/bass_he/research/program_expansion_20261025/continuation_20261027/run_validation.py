"""Reuse INTAKE01's measured runner for a separately recorded new work unit."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PREVIOUS = ROOT.parent / "continuation_20261025"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repair-reason", default=None)
    parser.add_argument("--test-name", action="append", default=[])
    args = parser.parse_args()
    path = PREVIOUS / "run_validation.py"
    expected = "b0f36cb3ee2f79d4fc29fa6596be37b829d299694f3fd167bf40460a3b976e8f"
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise RuntimeError("Inherited runner identity changed")
    spec = importlib.util.spec_from_file_location("he_intake01_recorded_runner", path)
    runner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = runner
    spec.loader.exec_module(runner)
    runner.ROOT = ROOT
    runner.OUT = ROOT / "evidence" / "validation"
    # The inherited runner records tests/ and sources/. Bind the new src/ and
    # the reused implementation bytes in sources/ without changing that runner.
    dependencies = [Path(__file__), ROOT / "VALIDATION_CONTRACT.json", path]
    dependencies.extend(sorted((ROOT / "src").glob("*.py")))
    dependencies.extend(sorted((ROOT / "tests").glob("test_*.py")))
    repo = ROOT.parents[2]
    baseline = json.loads((ROOT / "evidence" / "BASELINE.json").read_text())
    dependencies.extend(repo / item["path"] for item in baseline["identities"])
    if (ROOT / "sources" / "SOURCE_MANIFEST.json").exists():
        dependencies.append(ROOT / "sources" / "SOURCE_MANIFEST.json")
    manifest = {"schema": "HE_DRIFT02_TESTED_DEPENDENCIES_V1",
                "measurement_boundary": "preparation hashing occurs before the inherited measured test interval",
                "files": [{"path": str(p.relative_to(repo)),
                           "bytes": p.stat().st_size,
                           "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                          for p in sorted(set(dependencies))]}
    ledger_path = runner.OUT / "RESOURCE_LEDGER.json"
    sequence = len(json.loads(ledger_path.read_text())["attempts"]) + 1 if ledger_path.exists() else 1
    destination = ROOT / "sources" / f"TESTED_DEPENDENCIES_{sequence:02d}.json"
    if destination.exists() and json.loads(destination.read_text()) != manifest:
        raise RuntimeError("A prepared dependency record already exists with different bytes")
    runner.save(destination, manifest)
    return runner.run("tests", args.repair_reason, tuple(args.test_name))


if __name__ == "__main__":
    raise SystemExit(main())
