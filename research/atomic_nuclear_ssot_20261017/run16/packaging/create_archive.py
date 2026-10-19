#!/usr/bin/env python3
"""Create a new RUN16 source/evidence delta ZIP and verify every saved byte."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import stat
import sys
import zipfile

from verify_archive import verify

GAS_SHA = "3454e9e401560df188c7410de29d0712c4afe235e9899021e5314766ab778c8b"


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run16-root", required=True, type=Path)
    parser.add_argument("--gas-binary", required=True, type=Path)
    parser.add_argument("--science-commit", required=True)
    parser.add_argument("--pull-request-url", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    if len(args.science_commit) != 40 or any(x not in "0123456789abcdef" for x in args.science_commit):
        raise ValueError("full science commit required")
    root = args.run16_root.resolve()
    binary = args.gas_binary.resolve()
    if binary.is_symlink() or hashlib.sha256(binary.read_bytes()).hexdigest() != GAS_SHA:
        raise ValueError("original gas executable byte identity required")
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    now = datetime.now(timezone.utc)
    filename = "REI_RUN16_GAS_PATH_SENSITIVITY_" + now.strftime("%Y%m%d_%H%M%SZ") + ".zip"
    payload = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("source symlink not allowed")
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part.startswith(".") or part == "__pycache__" for part in relative.parts) or path.suffix == ".pyc":
            raise ValueError("unexpected hidden/cache file in frozen research payload")
        payload.append(("run16/" + relative.as_posix(), path.read_bytes(), stat.S_IFREG | 0o644))
    payload.append(("runtime/gas_rhs_server", binary.read_bytes(), stat.S_IFREG | 0o755))
    identity = {
        "schema": "rei.run16.delta-archive-identity.v1", "created_at_utc": now.isoformat(),
        "repository": "cosmosapjw-quantum/rei_bianchi", "science_commit": args.science_commit,
        "branch": "research/rei-run16-gas-path-sensitivity-20261019", "pull_request_url": args.pull_request_url,
        "kind": "RUN16 additive source, raw evidence and original gas binary; baseline archives required for earlier input/source",
        "baseline_git_commit": "c875005e30d9de1ce7f426898e46fe912068412c",
        "baseline_run15_archive": {
            "filename": "REI_RUN15_RECOVERY_FIXED_GAS_NATIVE_20261019_085443Z.zip",
            "bytes": 41913080, "sha256": "8729696dbb1efb7a7a76f59b12afacaa22d9481210b505c3b674b201b7b89dcb",
            "google_drive_url": "https://drive.google.com/file/d/1oDJIWU2oqE7ABG8z2CNoLQOmz9TP_fXO/view",
            "dropbox_id": "id:BSpOijBcT10AAAAAAD_Qfw",
            "dropbox_path": "/BASS_DERIVATION_DOSSIERS_20260912/REI_RUN15_RECOVERY_FIXED_GAS_NATIVE_20261019_085443Z.zip",
            "verification_scope": "Inherited prior full download verification; metadata and used input byte hashes refreshed in RUN16"
        },
        "original_gas_binary": {"bytes": binary.stat().st_size, "sha256": GAS_SHA},
        "exact_packaging_argv": [sys.executable, *sys.argv],
        "environment": {"python": sys.version, "platform": platform.platform()},
        "self_reference_policy": "ZIP hash and upload/download receipts are external delivery records, created after this immutable archive"
    }
    payload.append(("ARCHIVE_IDENTITY.json", encoded(identity), stat.S_IFREG | 0o644))
    manifest = {"schema": "rei.run16.delta-archive-manifest.v1", "files": [
        {"path": name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "mode": oct(mode)}
        for name, raw, mode in payload], "manifest_excludes_itself": True}
    path = output / filename
    timestamp = now.timetuple()[:6]
    with zipfile.ZipFile(path, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, raw, mode in payload + [("ARCHIVE_MANIFEST.json", encoded(manifest), stat.S_IFREG | 0o644)]:
            info = zipfile.ZipInfo(name, timestamp)
            info.create_system = 3
            info.external_attr = mode << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, raw, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    result = verify(path)
    result["created_at_utc"] = now.isoformat()
    result["exact_command_argv"] = [sys.executable, *sys.argv]
    result["archive_baseline_dependency"] = identity["baseline_run15_archive"]
    for name, data in [("PACKAGING_RECEIPT.json", result), ("ARCHIVE_MANIFEST.json", manifest), ("ARCHIVE_IDENTITY.json", identity)]:
        with (output / name).open("xb") as stream:
            stream.write(encoded(data))
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
