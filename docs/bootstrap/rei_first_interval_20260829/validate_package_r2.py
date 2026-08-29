#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
REI_HEAD = "ace7d91af35bfefcc3a9bd7e83076aa8f8bf557e"
REI_TREE = "c8167922076f52628b1f7243c9ebd8b40ebe7508"
REC_PACKAGE = "47e19df30a5e71e536d3d5167ffa3b78638a59c5"
REC_TREE = "e7400fda8511e582f5bc4944b96183977412f4f3"


def fail(message: str) -> None:
    raise SystemExit("FAIL: " + message)


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "--no-replace-objects", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=45,
    )
    if result.returncode:
        fail("git " + " ".join(args) + ": " + result.stderr.strip())
    return result.stdout.removesuffix("\n")


def validate_local() -> None:
    package = json.loads((ROOT / "PACKAGE_R2.json").read_text())
    units = json.loads((ROOT / "WORK_UNITS_R2.json").read_text())
    compatibility = json.loads((ROOT / "ODE_AUDIT_COMPATIBILITY_R2.json").read_text())
    if package["package_id"] != "REI-BIANCHI-FIRST-INTERVAL-BOOTSTRAP-20260829-R2":
        fail("package id")
    if package["source"]["head"] != REI_HEAD or package["source"]["tree"] != REI_TREE:
        fail("rei source identity")
    if package["rec_dependency"]["immutable_package_commit"] != REC_PACKAGE:
        fail("rec package identity")
    if package["rec_dependency"]["immutable_package_tree"] != REC_TREE:
        fail("rec package tree")
    if package["rec_dependency"]["numerical_import"] is not False:
        fail("rec numerical import firewall")
    if units["exact_next_action"] != "REI-AUDIT-COMPAT-00_THEN_REI-INTERVAL-02":
        fail("work-unit next action")
    if compatibility["copy_candidate_wholesale"] != "FORBIDDEN":
        fail("ODE shadow firewall")


def validate_live(repo: Path, rec_repo: Path | None) -> None:
    root = Path(git(repo, "rev-parse", "--show-toplevel"))
    head = git(root, "rev-parse", "--verify", "refs/remotes/origin/audit/ode-four-loop-external-20260823")
    if head != REI_HEAD or git(root, "rev-parse", head + "^{tree}") != REI_TREE:
        fail("rei audit source moved")
    if rec_repo is not None:
        rec_root = Path(git(rec_repo, "rev-parse", "--show-toplevel"))
        if git(rec_root, "rev-parse", REC_PACKAGE + "^{commit}") != REC_PACKAGE:
            fail("rec package commit absent")
        if git(rec_root, "rev-parse", REC_PACKAGE + "^{tree}") != REC_TREE:
            fail("rec package tree mismatch")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--rec-repo")
    args = parser.parse_args()
    validate_local()
    if args.live:
        validate_live(Path(args.repo), Path(args.rec_repo) if args.rec_repo else None)
    print(json.dumps({
        "status": "PASS",
        "package_id": "REI-BIANCHI-FIRST-INTERVAL-BOOTSTRAP-20260829-R2",
        "rei_head": REI_HEAD,
        "rei_tree": REI_TREE,
        "rec_package_commit": REC_PACKAGE,
        "rec_package_tree": REC_TREE,
        "exact_next_action": "REI-AUDIT-COMPAT-00_THEN_REI-INTERVAL-02",
        "claim": "NO_FULL_FIRST_INTERVAL_YET",
        "live": args.live,
    }, sort_keys=True))
