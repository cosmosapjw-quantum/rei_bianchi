#!/usr/bin/env python3
"""Read-only byte/CRC/path/mode validation for a RUN16 delta archive."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import zipfile


def verify(path, expected_sha256=None):
    path = Path(path)
    archive_sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if expected_sha256 is not None and archive_sha != expected_sha256:
        raise ValueError("archive SHA-256 mismatch")
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or len(names) > 1000:
            raise ValueError("duplicate or excessive archive entries")
        if sum(info.file_size for info in infos) > 128 * 1024 * 1024:
            raise ValueError("RUN16 delta uncompressed size exceeds declared cap")
        for info in infos:
            name = info.filename
            if (not name or "\\" in name or PurePosixPath(name).is_absolute()
                    or any(part in ("", ".", "..") for part in name.split("/"))):
                raise ValueError("noncanonical archive path")
            mode = info.external_attr >> 16
            if info.is_dir() or not stat.S_ISREG(mode) or info.flag_bits & 1:
                raise ValueError("only unencrypted regular-file entries allowed")
        if archive.testzip() is not None:
            raise ValueError("archive CRC mismatch")
        manifest_bytes = archive.read("ARCHIVE_MANIFEST.json")
        manifest = json.loads(manifest_bytes)
        if manifest.get("schema") != "rei.run16.delta-archive-manifest.v1":
            raise ValueError("unsupported archive manifest")
        rows = manifest["files"]
        expected_names = [row["path"] for row in rows]
        if (len(expected_names) != len(set(expected_names))
                or set(names) != set(expected_names) | {"ARCHIVE_MANIFEST.json"}):
            raise ValueError("manifest/archive membership mismatch")
        for row in rows:
            raw = archive.read(row["path"])
            actual = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                      "mode": oct(archive.getinfo(row["path"]).external_attr >> 16)}
            if any(actual[key] != row[key] for key in actual):
                raise ValueError("payload identity/mode mismatch: " + row["path"])
        identity = json.loads(archive.read("ARCHIVE_IDENTITY.json"))
    return {"schema": "rei.run16.delta-archive-verification.v1",
            "archive_file": str(path.resolve()), "archive_bytes": path.stat().st_size,
            "archive_sha256": archive_sha, "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "payload_files": len(rows), "archive_entries": len(names),
            "uncompressed_payload_bytes": sum(row["bytes"] for row in rows),
            "all_paths_regular_safe": True, "all_CRCs_match": True,
            "all_manifest_payload_hashes_and_modes_match": True,
            "science_commit": identity["science_commit"], "extracted_files": 0,
            "scientific_calculations": 0, "scope": "Byte delivery only, no execution or semantic certificate"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--sha256")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify(args.archive, args.sha256)
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        with args.output.open("x") as stream:
            stream.write(text)
    print(text, end="")


if __name__ == "__main__":
    main()
