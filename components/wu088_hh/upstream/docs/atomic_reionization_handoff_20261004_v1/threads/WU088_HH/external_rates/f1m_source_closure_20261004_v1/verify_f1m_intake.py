#!/usr/bin/env python3
"""Close the pinned F1M source intake without importing or executing its code."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import sys
from zipfile import ZipFile

F1M = (84346, "186e1169a7265a8b83108dab654f9e40d1817c790d6a3c234ec2c27514fa91e0", "WU088_HH_FAST_F1M_20261004_v1", 54)
F1P = (89773, "35e64c16be7d8fda86f4f2b35a88fdffd0d7721276e92316f4371ae35a14c8d1", "WU088_HH_FAST_F1P_20261004_v1", 59)
MISSING = "sources/WU088_HH_FAST_F1P_DELIVERY_20261004_v1/WU088_HH_FAST_F1P_20261004_v1/DELIVERY_MANIFEST.json"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check(data, row):
    if len(data) != row["bytes"] or digest(data) != row["sha256"]:
        raise ValueError("FILE_IDENTITY_MISMATCH:" + row["path"])


def archive(path, pin):
    size, sha, prefix, count = pin
    data = path.read_bytes()
    if len(data) != size or digest(data) != sha:
        raise ValueError("ARCHIVE_IDENTITY_MISMATCH:" + prefix)
    with ZipFile(io.BytesIO(data)) as z:
        names = z.namelist()
        if len(set(names)) != len(names):
            raise ValueError("DUPLICATE_ARCHIVE_MEMBER")
        for name in names:
            parts = PurePosixPath(name)
            if parts.is_absolute() or ".." in parts.parts or parts.parts[0] != prefix:
                raise ValueError("UNSAFE_ARCHIVE_MEMBER")
        if z.testzip() is not None:
            raise ValueError("ARCHIVE_CRC_FAILURE")
        files = {name[len(prefix) + 1:]: z.read(name) for name in names}
    manifest = json.loads(files["DELIVERY_MANIFEST.json"])
    rows = manifest["files"]
    if len(rows) != count or len({r["path"] for r in rows}) != count:
        raise ValueError("PAYLOAD_MANIFEST_COUNT_OR_DUPLICATE")
    if set(files) != {r["path"] for r in rows} | {"DELIVERY_MANIFEST.json"}:
        raise ValueError("UNDECLARED_OR_MISSING_PAYLOAD")
    for row in rows:
        check(files[row["path"]], row)
    return files, {"bytes": size, "sha256": sha, "payloads_verified": count, "crc_verified": True,
                   "delivery_manifest_sha256": digest(files["DELIVERY_MANIFEST.json"])}


def verify(f1m, f1p=None):
    files, identity = archive(f1m, F1M)
    parent, parent_identity = archive(f1p, F1P) if f1p is not None else (None, None)
    rows = json.loads(files["SOURCE_LOCK.json"])["files"]
    if len(rows) != 17 or len({r["path"] for r in rows}) != 17:
        raise ValueError("SOURCE_LOCK_COUNT_OR_DUPLICATE")
    verified, missing, recoveries = [], [], []
    for row in rows:
        data = files.get(row["path"])
        origin = "F1M"
        if data is None and row["path"] == MISSING and parent is not None:
            data = parent["DELIVERY_MANIFEST.json"]
            origin = "F1P"
            recoveries.append({"source_path": row["path"], "archive_sha256": F1P[1], "member": F1P[2] + "/DELIVERY_MANIFEST.json"})
        if data is None:
            missing.append(row)
            continue
        check(data, row)
        verified.append({**row, "origin": origin})
    complete = not missing
    return {"schema": "wu088.f1m.source_intake.v1", "status": "SOURCE_CLOSURE_VERIFIED" if complete else "SOURCE_CLOSURE_INCOMPLETE",
            "source_lock_scope": "F1M_DIRECT_17_FILES_ONLY", "source_lock_sha256": digest(files["SOURCE_LOCK.json"]),
            "F1M": identity, "F1P": parent_identity, "sources_verified": len(verified), "sources_required": 17,
            "verified_sources": verified, "missing_sources": missing, "explicit_recoveries": recoveries,
            "source_archives_modified": False, "science_executions": 0, "physical_admission": False}, 0 if complete else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--f1m", type=Path, required=True)
    parser.add_argument("--f1p", type=Path)
    args = parser.parse_args()
    try:
        result, code = verify(args.f1m, args.f1p)
    except (ValueError, OSError, KeyError) as error:
        result, code = {"status": "INTAKE_REJECTED", "reason": str(error), "science_executions": 0}, 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
