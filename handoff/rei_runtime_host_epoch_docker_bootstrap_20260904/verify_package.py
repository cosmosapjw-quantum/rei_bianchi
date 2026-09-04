#!/usr/bin/env python3
"""Verify the Docker-bootstrap handoff package by exact Git blob identity."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


PACKAGE = Path(__file__).resolve().parent
INDEX = PACKAGE / "PACKAGE_INDEX.json"


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def main() -> int:
    try:
        value = json.loads(INDEX.read_text(encoding="utf-8"))
        if value.get("schema") != "rei-runtime-host-epoch-docker-bootstrap-package-index/v1":
            raise ValueError("PACKAGE_INDEX_SCHEMA_INVALID")
        entries = value.get("entries")
        if not isinstance(entries, list) or not entries:
            raise ValueError("PACKAGE_INDEX_ENTRIES_INVALID")
        for entry in entries:
            path = PACKAGE / entry["path"]
            actual = git_blob_sha1(path.read_bytes())
            if actual != entry["git_blob_sha1"]:
                raise ValueError(f"PACKAGE_BLOB_MISMATCH:{entry['path']}")
        print(
            json.dumps(
                {
                    "status": "PASS_03A4_HOST_EPOCH_DOCKER_BOOTSTRAP_PACKAGE",
                    "entries": len(entries),
                    "native_runtime": "NOT_RUN",
                    "global_attempt_ref": "ABSENT_REQUIRED",
                },
                sort_keys=True,
            )
        )
        return 0
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"STOP_INVALID:{exc}", file=sys.stderr)
        return 65


if __name__ == "__main__":
    raise SystemExit(main())
