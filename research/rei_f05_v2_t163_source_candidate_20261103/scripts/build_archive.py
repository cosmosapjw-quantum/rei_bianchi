#!/usr/bin/env python3
"""Build a deterministic source-inclusive T163 evidence ZIP from public/private trees."""
from __future__ import annotations
import argparse, hashlib, json, os
from pathlib import Path
import zipfile

FIXED_TIME = (2026, 11, 3, 0, 0, 0)
STORE_SUFFIXES = (".zip", ".npz", ".gz", ".whl", ".tar", ".png", ".pdf")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def gather(root: Path, prefix: str):
    root = Path(root).resolve()
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise RuntimeError("SYMLINK_NOT_ALLOWED:" + str(path))
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        name = prefix + "/" + rel
        if name.startswith("/") or ".." in Path(name).parts:
            raise RuntimeError("UNSAFE_ARCHIVE_PATH:" + name)
        data = path.read_bytes()
        rows.append((name, data))
    return rows


def add_bytes(zf: zipfile.ZipFile, name: str, data: bytes):
    info = zipfile.ZipInfo(name, FIXED_TIME)
    info.create_system = 3
    info.external_attr = (0o100644 & 0xFFFF) << 16
    info.flag_bits = 0
    info.compress_type = zipfile.ZIP_STORED if name.lower().endswith(STORE_SUFFIXES) else zipfile.ZIP_DEFLATED
    zf.writestr(info, data, compress_type=info.compress_type, compresslevel=9)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--public-root", required=True)
    p.add_argument("--private-root", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--source-commit", required=True)
    a = p.parse_args()
    output = Path(a.output).resolve()
    temp = output.with_suffix(output.suffix + ".tmp")
    if output.exists() or temp.exists():
        raise FileExistsError("NO_OVERWRITE_EXISTING_ARCHIVE")
    rows = gather(Path(a.public_root), "public") + gather(Path(a.private_root), "private")
    rows.sort(key=lambda row: row[0])
    manifest = {
        "schema": "REI_F05_V2_T163_IMMUTABLE_ARCHIVE_MANIFEST_V1",
        "source_commit": a.source_commit,
        "fixed_zip_timestamp": "2026-11-03T00:00:00",
        "compression_policy": "store already-compressed binary; deflate text at level 9",
        "files": [{"path": name, "size_bytes": len(data), "sha256": sha(data)} for name, data in rows],
    }
    manifest_bytes = (json.dumps(manifest, allow_nan=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        with zipfile.ZipFile(temp, "w", allowZip64=True) as zf:
            for name, data in rows:
                add_bytes(zf, name, data)
            add_bytes(zf, "MANIFEST.json", manifest_bytes)
        with zipfile.ZipFile(temp, "r") as zf:
            bad = zf.testzip()
            if bad is not None:
                raise RuntimeError("ZIP_CRC_FAILURE:" + bad)
        os.replace(temp, output)
    except Exception:
        if temp.exists():
            temp.unlink()
        raise
    print(json.dumps({"output": str(output), "size_bytes": output.stat().st_size,
                      "sha256": sha(output.read_bytes()), "member_count": len(rows) + 1,
                      "crc": "PASS"}, sort_keys=True))

if __name__ == "__main__":
    main()
