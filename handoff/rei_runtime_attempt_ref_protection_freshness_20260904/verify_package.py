#!/usr/bin/env python3
"""Independent hosted-CI package verifier; no runtime authority effect."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
from typing import Any


PACKAGE_RELATIVE = (
    "handoff/rei_runtime_attempt_ref_protection_freshness_20260904"
)


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "GIT_FAILED")
    return completed.stdout.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--expected-head", required=True)
    options = parser.parse_args(argv)
    root = options.repo.resolve(strict=True)
    if git(root, "rev-parse", "HEAD") != options.expected_head:
        raise RuntimeError("EXPECTED_HEAD_MISMATCH")
    package = (root / PACKAGE_RELATIVE).resolve(strict=True)
    index_path = package / "PACKAGE_INDEX.json"
    index: dict[str, Any] = json.loads(index_path.read_text(encoding="utf-8"))
    if (
        index.get("schema")
        != "rei-runtime-attempt-ref-protection-freshness-package-index/v1"
        or index.get("git_object_format") != "sha1"
        or not isinstance(index.get("entries"), list)
    ):
        raise RuntimeError("PACKAGE_INDEX_INVALID")
    if git(root, "rev-parse", f"HEAD:{PACKAGE_RELATIVE}/PACKAGE_INDEX.json") != git_blob_sha1(index_path):
        raise RuntimeError("PACKAGE_INDEX_HEAD_BLOB_MISMATCH")
    expected: set[Path] = set()
    for row in index["entries"]:
        if not isinstance(row, dict) or set(row) != {"path", "blob_sha", "role"}:
            raise RuntimeError("PACKAGE_INDEX_INVALID")
        raw = row.get("path")
        pure = PurePosixPath(raw) if isinstance(raw, str) else None
        if pure is None or pure.is_absolute() or ".." in pure.parts or str(pure) != raw:
            raise RuntimeError("PACKAGE_INDEX_INVALID")
        relative = Path(raw)
        expected.add(relative)
        target = (package / relative).resolve(strict=True)
        target.relative_to(package)
        actual = git_blob_sha1(target)
        head = git(root, "rev-parse", f"HEAD:{PACKAGE_RELATIVE}/{raw}")
        if actual != row.get("blob_sha") or head != actual:
            raise RuntimeError(f"PACKAGE_BLOB_MISMATCH:{raw}")
    actual_paths = {
        path.relative_to(package)
        for path in package.rglob("*")
        if path.is_file()
        and path != index_path
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    }
    if actual_paths != expected:
        raise RuntimeError("PACKAGE_SCOPE_MISMATCH")
    print(
        json.dumps(
            {
                "status": "PASS_FRESHNESS_LIVE_READBACK_SOURCE",
                "package_entries": len(expected),
                "authority_effect": "NONE",
                "native_runtime": "NOT_RUN",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
