#!/usr/bin/env python3
"""Verify every admin-handoff source byte against SOURCE_INDEX and HEAD."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "rei_runtime_bridge_03a3r2_admin_ruleset"
INDEX = DOCS / "SOURCE_INDEX.json"


def git_text(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=False,
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
    value = json.loads(INDEX.read_text(encoding="utf-8"))
    if (
        set(value) != {"schema", "git_object_format", "entries"}
        or value["schema"] != "rei-runtime-03a3r2-admin-source-index/v1"
        or value["git_object_format"] != "sha1"
        or not isinstance(value["entries"], list)
    ):
        print("STOP_INVALID: SOURCE_INDEX_SCHEMA", file=sys.stderr)
        return 65
    indexed: set[str] = set()
    for row in value["entries"]:
        if not isinstance(row, dict) or set(row) != {"path", "blob_sha", "role"}:
            print("STOP_INVALID: SOURCE_INDEX_ROW", file=sys.stderr)
            return 65
        raw = row["path"]
        pure = PurePosixPath(raw)
        if pure.is_absolute() or ".." in pure.parts or str(pure) != raw:
            print("STOP_INVALID: SOURCE_INDEX_PATH", file=sys.stderr)
            return 65
        if raw in indexed:
            print("STOP_INVALID: SOURCE_INDEX_DUPLICATE", file=sys.stderr)
            return 65
        indexed.add(raw)
        target = ROOT / raw
        if not target.is_file() or target.is_symlink():
            print(f"STOP_INVALID: SOURCE_FILE_INVALID:{raw}", file=sys.stderr)
            return 65
        actual = git_text("hash-object", raw)
        head = git_text("rev-parse", f"HEAD:{raw}")
        if actual != row["blob_sha"] or head != row["blob_sha"]:
            print(f"STOP_INVALID: SOURCE_BLOB_MISMATCH:{raw}", file=sys.stderr)
            return 65
    expected = {
        path.relative_to(ROOT).as_posix()
        for path in DOCS.iterdir()
        if path.is_file() and path.name != "SOURCE_INDEX.json"
    }
    expected.update(
        {
            "tests/governance/test_rei_runtime_attempt_ref_server_ruleset_handoff.py",
            ".github/workflows/rei-runtime-attempt-ref-server-ruleset-handoff.yml",
        }
    )
    if indexed != expected:
        print("STOP_INVALID: SOURCE_INDEX_SCOPE", file=sys.stderr)
        print("missing=" + ",".join(sorted(expected - indexed)), file=sys.stderr)
        print("extra=" + ",".join(sorted(indexed - expected)), file=sys.stderr)
        return 65
    print(
        json.dumps(
            {
                "status": "PASS_ADMIN_RULESET_HANDOFF_SOURCE",
                "entries": len(indexed),
                "ruleset_mutation": "NOT_RUN",
                "global_attempt_ref": "ABSENT_REQUIRED",
                "native_runtime": "NOT_RUN",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
