#!/usr/bin/env python3
"""Verify the frozen all-file predecessor SHA-256 inventory."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


STAGE = Path(__file__).resolve().parent.parent
REPO = STAGE.parents[1]
MANIFEST = STAGE / "PREDECESSOR_SHA256SUMS.txt"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect() -> dict[str, object]:
    rows: list[tuple[str, str]] = []
    declared_count = None
    for line in MANIFEST.read_text("utf-8").splitlines():
        if line.startswith("# FILE_COUNT "):
            declared_count = int(line.split()[-1])
        elif line and not line.startswith("#"):
            expected, relative = line.split("  ", 1)
            rows.append((expected, relative))
    failures = []
    for expected, relative in rows:
        path = REPO / relative
        if not path.is_file():
            failures.append({"path": relative, "reason": "MISSING_OR_NOT_FILE"})
            continue
        actual = _sha256(path)
        if actual != expected:
            failures.append(
                {
                    "actual_sha256": actual,
                    "expected_sha256": expected,
                    "path": relative,
                    "reason": "SHA256_MISMATCH",
                }
            )
    return {
        "checked_file_count": len(rows),
        "declared_file_count": declared_count,
        "failures": failures,
        "manifest_sha256": _sha256(MANIFEST),
        "passed": not failures and declared_count == len(rows),
        "schema": "rei-predecessor-manifest-verification/v1",
    }


def main() -> int:
    result = collect()
    print(json.dumps(result, allow_nan=False, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
