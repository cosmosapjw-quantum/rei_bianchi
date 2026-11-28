#!/usr/bin/env python3
"""Restore the exact completed band archive; reuse identical files, never overwrite."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=ROOT)
    args = parser.parse_args()
    metadata = ROOT/"research/hh_phys69_20261019/band"
    contract = json.loads((metadata/"PAYLOAD_RESTORE.json").read_text())
    expected = json.loads((metadata/"PAYLOAD_SHA256SUMS.json").read_text())
    if hashlib.sha256(args.archive.read_bytes()).hexdigest() != contract["sha256"]:
        raise ValueError("archive SHA256 mismatch")
    base = args.repo/contract["member_paths_relative_to"]
    prepared, reused = [], 0
    with zipfile.ZipFile(args.archive) as archive:
        if len(archive.namelist()) != len(expected) or set(archive.namelist()) != set(expected):
            raise ValueError("archive member coverage mismatch")
        for name, sha in expected.items():
            relative = PurePosixPath(name)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("unsafe archive path")
            data = archive.read(name)
            if hashlib.sha256(data).hexdigest() != sha:
                raise ValueError("payload SHA256 mismatch")
            target = base/name
            if any(parent.is_symlink() for parent in [target, *target.parents]):
                raise ValueError("symlink restore target refused")
            if target.exists():
                if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != sha:
                    raise ValueError(f"changed existing evidence refused: {name}")
                reused += 1
            else:
                prepared.append((target, data))
    for path, data in prepared:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(data)
    print(json.dumps({"status": "RESTORED_OR_REUSED_EXACT_COMPLETED_EVIDENCE",
                      "created": len(prepared), "reused": reused,
                      "physical_integrations": 0, "archive_sha256": contract["sha256"]}))


if __name__ == "__main__":
    main()
