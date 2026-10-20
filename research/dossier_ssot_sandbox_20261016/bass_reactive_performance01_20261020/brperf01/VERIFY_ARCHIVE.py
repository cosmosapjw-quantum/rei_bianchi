#!/usr/bin/env python3
"""Verify all declared payloads and optionally extract to a new directory."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument("archive", type=Path)
parser.add_argument("--extract", type=Path)
args = parser.parse_args()
with zipfile.ZipFile(args.archive) as archive:
    manifest = json.loads(archive.read("MANIFEST_SHA256.json"))
    entries = manifest["files"]
    expected = {x["path"] for x in entries} | {"MANIFEST_SHA256.json"}
    if len(expected) != len(entries) + 1 or set(archive.namelist()) != expected:
        raise SystemExit("ARCHIVE_ENTRY_SET_MISMATCH")
    for row in entries:
        name = PurePosixPath(row["path"])
        if name.is_absolute() or ".." in name.parts:
            raise SystemExit("UNSAFE_ARCHIVE_PATH")
        data = archive.read(row["path"])
        if len(data) != row["bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise SystemExit("ARCHIVE_PAYLOAD_HASH_MISMATCH: " + row["path"])
    if args.extract:
        args.extract.mkdir(parents=True, exist_ok=False)
        for row in entries:
            path = args.extract / row["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(archive.read(row["path"]))
        (args.extract / "MANIFEST_SHA256.json").write_bytes(archive.read("MANIFEST_SHA256.json"))
print(json.dumps({"status":"PASS", "payloads":len(entries), "archive_sha256":hashlib.sha256(args.archive.read_bytes()).hexdigest(), "extract":str(args.extract) if args.extract else None}))
