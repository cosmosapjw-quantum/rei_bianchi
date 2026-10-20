#!/usr/bin/env python3
"""Restore the exact tested workspace layout from this Git subtree plus BR06 ZIP.

Usage: python MATERIALIZE_GIT.py BR06_FULL_ZIP NEW_WORKSPACE
The supplied BR06 ZIP is required because Git intentionally stores source diffs
and bounded evidence, while the archive carries all large scientific inputs.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import sys
import zipfile

if len(sys.argv) != 3:
    raise SystemExit(__doc__)
archive_path, destination = map(lambda x:Path(x).resolve(), sys.argv[1:])
expected = "3137ad8903ef62073485a18e78b84966d3a9d09b9a60698dddfd492876432135"
if hashlib.sha256(archive_path.read_bytes()).hexdigest() != expected:
    raise SystemExit("BR06_ARCHIVE_SHA_MISMATCH")
destination.mkdir(parents=True, exist_ok=False)
source = Path(__file__).resolve().parent
shutil.copytree(source, destination / "brperf01", ignore=shutil.ignore_patterns("target", "__pycache__", "runtime", "outputs", "publication_payload", "git_delivery", "private"))
base = destination / "repo/research/dossier_ssot_sandbox_20261016/bass_reactive06_vigilode_reference_20261019"
base.mkdir(parents=True)
with zipfile.ZipFile(archive_path) as archive:
    manifest = json.loads(archive.read("MANIFEST_SHA256.json"))
    for row in manifest["files"]:
        name = PurePosixPath(row["path"])
        if name.is_absolute() or ".." in name.parts:
            raise SystemExit("UNSAFE_BR06_ARCHIVE_PATH")
        data = archive.read(row["path"])
        if hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise SystemExit("BR06_PAYLOAD_SHA_MISMATCH")
        path = base / row["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    (base / "MANIFEST_SHA256.json").write_bytes(archive.read("MANIFEST_SHA256.json"))
print(json.dumps({"status":"PASS", "workspace":str(destination), "br06_payloads":len(manifest["files"])}))
