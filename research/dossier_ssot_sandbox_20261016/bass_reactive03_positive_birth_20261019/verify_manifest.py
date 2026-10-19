#!/usr/bin/env python3
"""Verify archived bytes and the immutable parent-source contract; no extraction.

The default manifest is standard sha256sum text: ``HASH  relative/path``.
This verifies byte identity, not the physical interpretation of any result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

LINE = re.compile(r"^([0-9a-fA-F]{64}) [ *](.+)$")
HEX = re.compile(r"^[0-9a-fA-F]{64}$")


class VerificationError(Exception):
    def __init__(self, category: str, message: str):
        self.category = category
        super().__init__(message)


def safe_file(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise VerificationError("INVALID_MANIFEST_PATH", repr(relative))
    path = PurePosixPath(relative)
    if path.is_absolute() or str(path) != relative or any(p in (".", "..") for p in path.parts):
        raise VerificationError("INVALID_MANIFEST_PATH", relative)
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise VerificationError("SYMLINK_NOT_ADMITTED", relative)
    try:
        resolved = current.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise VerificationError("INPUT_DEPENDENCY_MISSING", relative) from exc
    if not resolved.is_file():
        raise VerificationError("INPUT_DEPENDENCY_MISSING", relative)
    return resolved


def file_hash(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    count = 0
    before = path.stat()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
            count += len(chunk)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns, before.st_ino) != (
        after.st_size, after.st_mtime_ns, after.st_ino
    ) or count != after.st_size:
        raise VerificationError("PAYLOAD_CHANGED_DURING_VERIFICATION", str(path))
    return digest.hexdigest(), count


def read_text_manifest(root: Path, relative: str) -> dict[str, str]:
    path = safe_file(root, relative)
    entries: dict[str, str] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        match = LINE.fullmatch(line)
        if not match:
            raise VerificationError("INVALID_MANIFEST_FORMAT", f"{relative}:{line_number}")
        digest, name = match.groups()
        if name in entries:
            raise VerificationError("DUPLICATE_MANIFEST_ENTRY", name)
        if name == relative:
            raise VerificationError("MANIFEST_SELF_REFERENCE", name)
        safe_file(root, name)
        entries[name] = digest.lower()
    if not entries:
        raise VerificationError("EMPTY_MANIFEST", relative)
    return entries


def read_parent_contract(root: Path, relative: str) -> dict[str, str]:
    raw = json.loads(safe_file(root, relative).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or len(raw) != 97:
        raise VerificationError("INVALID_PARENT_CONTRACT", f"{relative}: expected exactly 97 original source entries")
    out: dict[str, str] = {}
    for name, digest in raw.items():
        if not isinstance(name, str) or not isinstance(digest, str) or not HEX.fullmatch(digest):
            raise VerificationError("INVALID_PARENT_CONTRACT", relative)
        # Validate each raw parent path before adding the fixed crate prefix.
        p = PurePosixPath(name)
        if p.is_absolute() or str(p) != name or "\\" in name or ".." in p.parts:
            raise VerificationError("INVALID_MANIFEST_PATH", name)
        out[f"crate/{name}"] = digest.lower()
    return out


def verify(root: Path, entries: dict[str, str]) -> dict[str, object]:
    errors = []
    total_bytes = 0
    for relative, expected in entries.items():
        try:
            actual, size = file_hash(safe_file(root, relative))
            total_bytes += size
            if actual != expected:
                errors.append({"path": relative, "category": "SHA256_MISMATCH", "expected": expected, "actual": actual})
        except VerificationError as exc:
            errors.append({"path": relative, "category": exc.category, "detail": str(exc)})
    return {"entries": len(entries), "bytes_hashed": total_bytes, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--manifest", default="MANIFEST.sha256")
    parser.add_argument("--parent-contract", default="contracts/PARENT_97_SOURCE_SHA256.json")
    parser.add_argument("--skip-parent-contract", action="store_true", help="Only for generic manifest diagnostics; not final restoration admission.")
    args = parser.parse_args()
    try:
        root = args.root.resolve(strict=True)
        payload = verify(root, read_text_manifest(root, args.manifest))
        parent = None if args.skip_parent_contract else verify(root, read_parent_contract(root, args.parent_contract))
        errors = payload["errors"] + ([] if parent is None else parent["errors"])
        result = {
            "status": "ARTIFACT_INTEGRITY_FAILURE" if errors else "VERIFIED_PAYLOAD_BYTES",
            "root": str(root),
            "manifest": args.manifest,
            "manifest_sha256": file_hash(safe_file(root, args.manifest))[0],
            "payload": payload,
            "immutable_parent_source": parent,
            "scope": "Checks listed byte identities only; no scientific convergence claim and no claim about unlisted files.",
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if errors else 0
    except (VerificationError, OSError, ValueError) as exc:
        print(json.dumps({
            "status": "ARTIFACT_VERIFICATION_BLOCKED",
            "category": getattr(exc, "category", "INPUT_OR_PARSER_ERROR"),
            "detail": str(exc),
        }, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    sys.exit(main())
