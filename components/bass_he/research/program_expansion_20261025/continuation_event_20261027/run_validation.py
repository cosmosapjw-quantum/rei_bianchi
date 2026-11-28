"""Reuse the inherited measured runner for EVENT03's single new test process.

Preparation identities are recorded before its measured interval. No old suite
or upstream compiler/native-fit execution is invoked.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
PREVIOUS=ROOT.parent/"continuation_20261025"


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--repair-reason",default=None)
    parser.add_argument("--test-name",action="append",default=[])
    args=parser.parse_args()
    path=PREVIOUS/"run_validation.py"
    expected="b0f36cb3ee2f79d4fc29fa6596be37b829d299694f3fd167bf40460a3b976e8f"
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
        raise RuntimeError("Inherited recorded runner identity changed")
    spec=importlib.util.spec_from_file_location("he_event03_intake01_runner",path)
    runner=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=runner
    spec.loader.exec_module(runner)
    runner.ROOT=ROOT
    runner.OUT=ROOT/"evidence/validation"
    repo=ROOT.parents[2]
    dependencies=[Path(__file__),path,ROOT/"MODEL_CONTRACT.json",ROOT/"VALIDATION_CONTRACT.json",ROOT/"THEORY_KO.md",PREVIOUS/"exchange/exchange_closure.py"]
    dependencies+=sorted((ROOT/"src").glob("*.py"))
    dependencies+=sorted((ROOT/"tests").glob("test_*.py"))
    dependencies+=sorted(p for p in (ROOT/"sources").rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    manifest={"schema":"HE_EVENT03_TESTED_DEPENDENCIES_V1",
        "measurement_boundary":"preparation hashing before inherited measured test interval; preparation/model/network/IO UNKNOWN_NOT_ZERO",
        "files":[{"path":str(p.relative_to(repo)),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(dependencies))]}
    ledger_path=runner.OUT/"RESOURCE_LEDGER.json"
    sequence=len(json.loads(ledger_path.read_text())["attempts"])+1 if ledger_path.exists() else 1
    destination=ROOT/"evidence"/f"TESTED_DEPENDENCIES_{sequence:02d}.json"
    if destination.exists() and json.loads(destination.read_text())!=manifest:
        raise RuntimeError("Prepared dependency record already exists with different bytes")
    runner.save(destination,manifest)
    inherited_save=runner.save
    def bound_save(destination,data):
        if isinstance(data,dict) and "source_sha256" in data:
            data["tested_dependency_manifest"]={"path":f"evidence/TESTED_DEPENDENCIES_{sequence:02d}.json",
                "sha256":hashlib.sha256((ROOT/"evidence"/f"TESTED_DEPENDENCIES_{sequence:02d}.json").read_bytes()).hexdigest()}
            data["source_sha256"].update({item["path"]:item["sha256"] for item in manifest["files"]})
        return inherited_save(destination,data)
    runner.save=bound_save
    return runner.run("tests",args.repair_reason,tuple(args.test_name))


if __name__=="__main__":
    raise SystemExit(main())
