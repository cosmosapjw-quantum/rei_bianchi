"""Restore one R25 source dependency from the nested original ZIP, no substitutions.

Usage after extracting WU_R26_SOURCE_ORIGINAL_20261030.zip:
    python delivery/replay_parent_r25.py --root .

The original R25 nested ZIP is immutable; this tool only adds a missing exact
source JSON at the path expected by the published R26 code regression tests.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from zipfile import ZipFile
import hashlib

EXPECTED_PARENT_ZIP = "c00daeb40ae385f776c727a770ece0a3faee577496bcb621ae066294e94efca1"
EXPECTED_ENTRY_SHA = "c53810ebbd585a2d8d6ce46d2023644b718b8f13e2e5cfb6034ded16621bc7ad"
RELATIVE_ENTRY = "sources/GL2022_NATIVE_PRODUCT_GRID_R25.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def restore(root: Path) -> dict:
    root = Path(root).resolve()
    original = root / "parent_R25/WU_R25_SOURCE_ORIGINAL_20261029.zip"
    original_bytes = original.read_bytes()
    if sha256(original_bytes) != EXPECTED_PARENT_ZIP:
        raise ValueError("original R25 source ZIP identity mismatch")
    with ZipFile(original) as archive:
        if archive.testzip() is not None:
            raise ValueError("nested R25 ZIP CRC failed")
        payload = archive.read(RELATIVE_ENTRY)
    if sha256(payload) != EXPECTED_ENTRY_SHA:
        raise ValueError("R25 original required source entry mismatch")
    target = root / "parent_R25" / RELATIVE_ENTRY
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if sha256(target.read_bytes()) != EXPECTED_ENTRY_SHA:
            raise ValueError("existing target differs from immutable R25 original")
        status = "ALREADY_EXACT"
    else:
        with target.open("xb") as f:
            f.write(payload)
        status = "EXTRACTED_EXACT"
    return {"status": status, "target": str(target), "parent_zip_sha256": EXPECTED_PARENT_ZIP,
            "entry_sha256": EXPECTED_ENTRY_SHA, "bytes": len(payload)}


if __name__ == "__main__":
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--root", type=Path, default=Path.cwd())
    p = a.parse_args()
    print(restore(p.root))
