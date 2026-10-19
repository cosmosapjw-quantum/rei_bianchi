#!/usr/bin/env python3
"""Restore exact files from raw Git-transport chunks without overwriting files.

This is byte transport, not source reconstruction or scientific recalculation.
All parts and whole-file SHA-256 / Git blob SHA-1 identities are checked before
any target is created. Existing targets must already match exactly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tempfile

SCHEMA = "rei.lossless.git.byte_chunks.v1"
BLOCK = 1024 * 1024


def relative_path(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("nonempty POSIX relative path required")
    if any(part in ("", ".", "..") for part in value.split("/")):
        raise ValueError("noncanonical or unsafe relative path")
    path = PurePosixPath(value)
    if path.is_absolute():
        raise ValueError("absolute path forbidden")
    return path


def inside(root: Path, relative: str) -> Path:
    path = root.joinpath(*relative_path(relative).parts)
    resolved = path.resolve()
    if root != resolved and root not in resolved.parents:
        raise ValueError("path escapes its declared root")
    return path


def positive_size(value: int) -> int:
    if type(value) is not int or value < 0:
        raise ValueError("nonnegative integer byte count required")
    return value


def file_hashes(path: Path) -> dict:
    size = path.stat().st_size
    sha256 = hashlib.sha256()
    git = hashlib.sha1(b"blob " + str(size).encode() + b"\0")
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(BLOCK), b""):
            sha256.update(block)
            git.update(block)
    return {"bytes": size, "sha256": sha256.hexdigest(), "git_blob_sha1": git.hexdigest()}


def expected_identity(row: dict) -> dict:
    size = positive_size(row["bytes"])
    for key, length in (("sha256", 64), ("git_blob_sha1", 40)):
        value = row[key]
        if not isinstance(value, str) or len(value) != length or any(c not in "0123456789abcdef" for c in value):
            raise ValueError(f"invalid {key}")
    return {"bytes": size, "sha256": row["sha256"], "git_blob_sha1": row["git_blob_sha1"]}


def validate_parts(manifest_path: Path) -> tuple[dict, list[dict]]:
    manifest_path = manifest_path.resolve()
    manifest = json.loads(manifest_path.read_bytes())
    if manifest.get("schema") != SCHEMA or manifest.get("encoding") != "raw-byte-concatenation":
        raise ValueError("unsupported transport manifest")
    if not isinstance(manifest.get("files"), list) or not manifest["files"]:
        raise ValueError("nonempty file inventory required")
    root = manifest_path.parent
    prepared, targets = [], set()
    for row in manifest["files"]:
        target = str(relative_path(row["target"]))
        if target in targets:
            raise ValueError("duplicate target path")
        targets.add(target)
        expected = expected_identity(row)
        if row.get("mode", "100644") not in ("100644", "100755"):
            raise ValueError("unsupported target mode")
        if not isinstance(row.get("parts"), list) or not row["parts"]:
            raise ValueError("nonempty ordered parts required")
        whole = hashlib.sha256()
        whole_git = hashlib.sha1(b"blob " + str(expected["bytes"]).encode() + b"\0")
        offset, paths = 0, []
        for part in row["parts"]:
            if type(part.get("offset")) is not int or part["offset"] != offset:
                raise ValueError("parts must be contiguous and in exact byte order")
            path = inside(root, part["path"])
            if path.is_symlink() or not path.is_file():
                raise ValueError("chunk must be an existing ordinary file")
            part_expected = expected_identity(part)
            if file_hashes(path) != part_expected:
                raise ValueError(f"chunk identity mismatch: {part['path']}")
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(BLOCK), b""):
                    whole.update(block)
                    whole_git.update(block)
            offset += part_expected["bytes"]
            paths.append(path)
        actual = {"bytes": offset, "sha256": whole.hexdigest(), "git_blob_sha1": whole_git.hexdigest()}
        if actual != expected:
            raise ValueError(f"whole-file identity mismatch: {target}")
        prepared.append({"row": row, "target": target, "parts": paths, "identity": expected})
    return manifest, prepared


def restore(manifest_path: Path, destination_root: Path, verify_only: bool = False) -> dict:
    manifest, prepared = validate_parts(manifest_path)
    root = destination_root.resolve()
    # Validate all existing targets before creating any output file.
    for item in prepared:
        target = inside(root, item["target"])
        if target.is_symlink():
            raise ValueError("refusing symlink target")
        if target.exists():
            if not target.is_file() or file_hashes(target) != item["identity"]:
                raise ValueError(f"refusing to overwrite differing target: {item['target']}")
        elif verify_only:
            raise ValueError(f"target missing during verify-only: {item['target']}")
        item["output"] = target
    results = []
    for item in prepared:
        target = item["output"]
        existed = target.exists()
        if not existed:
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="wb", prefix=target.name + ".part-", dir=target.parent, delete=False) as stream:
                temporary = Path(stream.name)
                try:
                    for part in item["parts"]:
                        with part.open("rb") as source:
                            for block in iter(lambda: source.read(BLOCK), b""):
                                stream.write(block)
                    stream.flush()
                    os.fsync(stream.fileno())
                except BaseException:
                    temporary.unlink(missing_ok=True)
                    raise
            try:
                if file_hashes(temporary) != item["identity"]:
                    raise ValueError("chunk bytes changed while restoring")
                temporary.chmod(0o755 if item["row"].get("mode") == "100755" else 0o644)
                # Atomic add-only publication: link fails if the target appeared.
                os.link(temporary, target)
            finally:
                temporary.unlink(missing_ok=True)
        actual = file_hashes(target)
        if actual != item["identity"]:
            raise ValueError("target identity changed during restoration")
        results.append({"target": item["target"], **actual,
                        "status": "EXISTING_EXACT" if existed else "RESTORED_EXACT"})
    return {"schema": "rei.lossless.git.byte_chunks.restoration.v1", "manifest": str(manifest_path.resolve()),
            "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            "destination_root": str(root), "verify_only": verify_only,
            "files": results, "all_parts_and_full_files_verified": True,
            "overwritten_files": 0, "scientific_recalculations": 0}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("MANIFEST.json"))
    parser.add_argument("--destination-root", type=Path, required=True)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    print(json.dumps(restore(args.manifest, args.destination_root, args.verify_only), indent=2))


if __name__ == "__main__":
    main()
