#!/usr/bin/env python3
"""Verify BR04 payload and immutable source contracts without executing physics."""
from pathlib import Path
import argparse
import hashlib
import json


def verify(root):
    root = root.resolve()
    manifest = root / "MANIFEST_SHA256.json"
    failures = []
    checked = 0
    if manifest.exists():
        records = json.loads(manifest.read_text())["files"]
        for record in records:
            rel = Path(record["path"])
            if rel.is_absolute() or ".." in rel.parts:
                raise ValueError("unsafe manifest path")
            p = root / rel
            if not p.is_file() or p.is_symlink():
                failures.append(str(rel)); continue
            if p.stat().st_size != record["bytes"] or hashlib.sha256(p.read_bytes()).hexdigest() != record["sha256"]:
                failures.append(str(rel))
            checked += 1
    else:
        # Source checkout verification uses the same per-file identity contracts.
        parent = json.loads((root / "contracts/PARENT_INPUT_SHA256.json").read_text())
        records = parent.get("files", parent)
        if isinstance(records, dict):
            records = [{"path": k, "sha256": v} for k, v in records.items()]
        for record in records:
            p = root / record["path"]
            if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != record["sha256"]:
                failures.append(record["path"])
            checked += 1
        identity_path = root / "evidence/implementation/SOURCE_IDENTITY_POST_REVIEW.json"
        if not identity_path.exists():
            identity_path = root / "evidence/implementation/SOURCE_IDENTITY.json"
        new = json.loads(identity_path.read_text())["new_sources"]
        for name, digest in new.items():
            if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
                failures.append(name)
            checked += 1
    result = {"status": "PASS" if not failures else "FAIL", "checked": checked, "failures": failures,
              "mode": "ARCHIVE_PAYLOAD" if manifest.exists() else "SOURCE_CONTRACT"}
    print(json.dumps(result))
    return not failures


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    raise SystemExit(0 if verify(args.root) else 1)
