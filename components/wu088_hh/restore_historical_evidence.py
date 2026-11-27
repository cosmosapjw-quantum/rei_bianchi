"""Materialize selected historical WU result paths in an explicit directory."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
from tempfile import NamedTemporaryFile


def restore(destination: Path, prefix: str) -> int:
    root = Path(__file__).resolve().parent
    meta = json.loads((root / "UPSTREAM_COVERAGE.json").read_text())
    archive = root / meta["archive_file"]
    with archive.open("rb") as f:
        if hashlib.file_digest(f, "sha256").hexdigest() != meta["archive_sha256"]:
            raise ValueError("Historical archive SHA256 mismatch")
    with gzip.open(root / "UPSTREAM_INVENTORY.csv.gz", "rt") as stream:
        selected = {
            r["path"]: r
            for r in csv.DictReader(stream)
            if r["disposition"].startswith("archive/") and r["path"].startswith(prefix)
        }
    if not selected:
        raise ValueError("No archived paths match this prefix")
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    seen = set()
    with tarfile.open(archive, "r:gz") as source:
        for member in source:
            if member.name not in selected:
                continue
            relative = PurePosixPath(member.name)
            if (
                member.name in seen
                or not member.isfile()
                or relative.is_absolute()
                or ".." in relative.parts
            ):
                raise ValueError("Invalid persisted member " + member.name)
            out = destination.joinpath(*relative.parts)
            if out.is_symlink() or not out.resolve().is_relative_to(destination):
                raise ValueError("Unexpected existing path " + member.name)
            data = source.extractfile(member).read()
            row = selected[member.name]
            actual = hashlib.sha1(
                b"blob " + str(len(data)).encode() + b"\0" + data
            ).hexdigest()
            if actual != row["git_blob_sha1"] or len(data) != int(row["bytes"]):
                raise ValueError("Source identity mismatch " + member.name)
            if out.exists() and out.read_bytes() != data:
                raise FileExistsError(out)
            if not out.exists():
                out.parent.mkdir(parents=True, exist_ok=True)
                with NamedTemporaryFile(dir=out.parent, delete=False) as f:
                    f.write(data)
                    temp = Path(f.name)
                temp.chmod(int(row["git_mode"], 8) & 0o777)
                temp.replace(out)
            seen.add(member.name)
    if seen != set(selected):
        raise ValueError("Requested historical members are absent")
    return len(seen)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--prefix", default="")
    args = parser.parse_args()
    print(restore(args.destination, args.prefix))
