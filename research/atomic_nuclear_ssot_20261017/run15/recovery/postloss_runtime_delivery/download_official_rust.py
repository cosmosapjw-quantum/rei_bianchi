#!/usr/bin/env python3
"""Download and inspect exact official Rust components; do not install or compile."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import posixpath
import re
import tarfile
import urllib.request
from pathlib import Path, PurePosixPath

VERSION = "1.94.1"
TARGET = "x86_64-unknown-linux-gnu"
ARTIFACTS = [
    ("rustc", 78645148, "0a6b16ca476461c6238f48efcb74a7aa08a3983e61adf587f208ba48504d87e1"),
    ("cargo", 10972128, "03595624775204f80ff3a67986f69c8918e4cd311877ced635108888013a1e39"),
    ("rust-std", 29846424, "74109ee2c19098f1d7122087dd338a8f643203b3ce678c9d58169db733e17a03"),
]


def save_new(path: Path, obj: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(obj, stream, indent=2)
        stream.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.absolute()
    if root.exists() or root.is_symlink():
        raise ValueError("output root must be new")
    root.mkdir(parents=True)
    download_root = root / "downloads"
    extract_root = root / "extracted"
    download_root.mkdir()
    extract_root.mkdir()
    records = []
    for component, expected_bytes, expected_hash in ARTIFACTS:
        name = f"{component}-{VERSION}-{TARGET}"
        url = f"https://static.rust-lang.org/dist/{name}.tar.xz"
        print(json.dumps({"component": component, "status": "DOWNLOAD_STARTED", "expected_bytes": expected_bytes}), flush=True)
        with urllib.request.urlopen(url + ".sha256", timeout=30) as response:
            checksum_bytes = response.read(4097)
        if len(checksum_bytes) > 4096:
            raise ValueError("unexpected checksum length")
        checksum_line = checksum_bytes.decode("ascii").strip()
        fields = checksum_line.split()
        if len(fields) != 2 or fields[0] != expected_hash or fields[1] != name + ".tar.xz":
            raise ValueError("official checksum text changed or malformed")
        checksum_path = download_root / (name + ".tar.xz.sha256")
        with checksum_path.open("xb") as stream:
            stream.write(checksum_bytes)
        archive = download_root / (name + ".tar.xz")
        partial = archive.with_suffix(archive.suffix + ".part")
        digest = hashlib.sha256()
        count = 0
        with urllib.request.urlopen(url, timeout=30) as response, partial.open("xb") as stream:
            content_length = response.headers.get("Content-Length")
            if content_length is not None and int(content_length) != expected_bytes:
                raise ValueError("official artifact size changed")
            headers = {key: response.headers.get(key) for key in ("Content-Length", "Last-Modified", "ETag")}
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                count += len(chunk)
                if count > expected_bytes:
                    raise ValueError("download exceeded exact expected size")
                digest.update(chunk)
                stream.write(chunk)
        actual_hash = digest.hexdigest()
        if count != expected_bytes or actual_hash != expected_hash:
            raise ValueError(f"download identity mismatch: {component}: {count}, {actual_hash}")
        partial.rename(archive)
        entries = []
        seen = set()
        expanded_bytes = 0
        with tarfile.open(archive, mode="r:xz") as tar:
            members = tar.getmembers()
            if len(members) > 60000:
                raise ValueError("too many tar members")
            for item in members:
                path = PurePosixPath(item.name)
                if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != name:
                    raise ValueError(f"unsafe member path: {item.name}")
                normalized = str(path)
                if normalized in seen:
                    raise ValueError(f"duplicate member: {normalized}")
                seen.add(normalized)
                if not (item.isdir() or item.isfile() or item.issym() or item.islnk()):
                    raise ValueError(f"unsupported tar member type: {item.name}")
                if item.size < 0 or item.mode & 0o6000:
                    raise ValueError(f"unsafe member size or privileged mode: {item.name}")
                if item.issym() or item.islnk():
                    target = PurePosixPath(item.linkname)
                    if target.is_absolute():
                        raise ValueError("absolute link target")
                    joined = posixpath.normpath(str(path.parent / target) if item.issym() else str(target))
                    if not (joined == name or joined.startswith(name + "/")):
                        raise ValueError(f"escaping link target: {item.name}")
                expanded_bytes += item.size
                if expanded_bytes > 2 * 1024**3:
                    raise ValueError("expanded component exceeds 2 GiB bound")
                entries.append({"path": item.name, "bytes": item.size, "mode": oct(item.mode), "type": item.type.decode("ascii"), "link": item.linkname or None})
            tar.extractall(extract_root, members=members, filter="data")
        record = {
            "component": component,
            "url": url,
            "checksum_url": url + ".sha256",
            "bytes": count,
            "sha256": actual_hash,
            "http_headers": headers,
            "archive_safety": "ALL_ENTRIES_ACCEPTED",
            "member_count": len(entries),
            "expanded_file_bytes": expanded_bytes,
            "archive": str(archive),
            "extracted_root": str(extract_root / name),
            "signature_verification": "NOT_PERFORMED",
        }
        save_new(root / f"{component}_archive_manifest.json", entries)
        save_new(root / f"{component}_receipt.json", record)
        records.append(record)
        print(json.dumps({"component": component, "status": "SHA256_AND_SAFE_EXTRACTION_COMPLETE", "bytes": count, "expanded_file_bytes": expanded_bytes, "sha256": actual_hash}), flush=True)
    save_new(root / "OFFICIAL_COMPONENTS_RECEIPT.json", {
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "DOWNLOADED_HASH_CHECKED_AND_SAFE_EXTRACTED",
        "total_download_bytes": sum(row[1] for row in ARTIFACTS),
        "components": records,
        "installations": 0,
        "builds": 0,
        "ivps": 0,
    })


if __name__ == "__main__":
    main()
