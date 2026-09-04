#!/usr/bin/env python3
"""Verify every independent-readback source byte against HEAD."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "docs" / "rei_runtime_bridge_03a3r3_independent_readback"
INDEX = PACKAGE / "SOURCE_INDEX.json"
EXTERNAL = {
    ".github/workflows/rei-runtime-attempt-ref-ruleset-readback-red.yml",
    ".github/workflows/rei-runtime-attempt-ref-ruleset-readback-green.yml",
    ".github/workflows/rei-runtime-independent-readback-get-normalization.yml",
    "tests/governance/test_rei_runtime_attempt_ref_ruleset_independent_readback_red.py",
    "tests/governance/test_rei_runtime_independent_readback_get_normalization.py",
}


def git_text(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "GIT_FAILED:" + " ".join(args) + ":" + completed.stderr.strip()
        )
    return completed.stdout.strip()


def main() -> int:
    try:
        value = json.loads(INDEX.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"STOP_INVALID: SOURCE_INDEX_UNREADABLE:{exc}", file=sys.stderr)
        return 65
    if (
        set(value) != {"schema", "git_object_format", "entries"}
        or value.get("schema")
        != "rei-runtime-03a3r3-independent-readback-source-index/v1"
        or value.get("git_object_format") != "sha1"
        or not isinstance(value.get("entries"), list)
    ):
        print("STOP_INVALID: SOURCE_INDEX_SCHEMA", file=sys.stderr)
        return 65
    indexed = set()
    for row in value["entries"]:
        if not isinstance(row, dict) or set(row) != {"path", "blob_sha", "role"}:
            print("STOP_INVALID: SOURCE_INDEX_ROW", file=sys.stderr)
            return 65
        raw = row.get("path")
        blob = row.get("blob_sha")
        pure = PurePosixPath(raw) if isinstance(raw, str) else None
        if (
            pure is None
            or pure.is_absolute()
            or ".." in pure.parts
            or str(pure) != raw
            or not isinstance(blob, str)
            or len(blob) != 40
            or any(character not in "0123456789abcdef" for character in blob)
            or raw in indexed
        ):
            print("STOP_INVALID: SOURCE_INDEX_ENTRY_INVALID", file=sys.stderr)
            return 65
        indexed.add(raw)
        target = ROOT / raw
        if not target.is_file() or target.is_symlink():
            print(f"STOP_INVALID: SOURCE_FILE_INVALID:{raw}", file=sys.stderr)
            return 65
        try:
            worktree_blob = git_text("hash-object", raw)
            head_blob = git_text("rev-parse", f"HEAD:{raw}")
        except RuntimeError as exc:
            print(f"STOP_INVALID: {exc}", file=sys.stderr)
            return 65
        if worktree_blob != blob or head_blob != blob:
            print(f"STOP_INVALID: SOURCE_BLOB_MISMATCH:{raw}", file=sys.stderr)
            return 65
    expected = {
        path.relative_to(ROOT).as_posix()
        for path in PACKAGE.iterdir()
        if path.is_file()
        and path.name != "SOURCE_INDEX.json"
        and path.suffix != ".pyc"
    }
    expected.update(EXTERNAL)
    if indexed != expected:
        print("STOP_INVALID: SOURCE_INDEX_SCOPE", file=sys.stderr)
        print("missing=" + ",".join(sorted(expected - indexed)), file=sys.stderr)
        print("extra=" + ",".join(sorted(indexed - expected)), file=sys.stderr)
        return 65
    print(
        json.dumps(
            {
                "status": "PASS_INDEPENDENT_READBACK_SOURCE_INDEX",
                "entries": len(indexed),
                "network_surface": "GET_ONLY",
                "repository_ruleset": "NOT_MUTATED",
                "global_attempt_ref": "ABSENT_REQUIRED",
                "native_runtime": "NOT_RUN",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
