#!/usr/bin/env python3
"""Verify or safely restore a RUN17 delta archive; execute no scientific code."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import stat
import zipfile

GAS_SHA = "3454e9e401560df188c7410de29d0712c4afe235e9899021e5314766ab778c8b"
GAS_BYTES = 571904
RUN16_HEAD = "45ee7192b9d405214ec2650185aeaaa635e0fa13"
RUN15_HEAD = "c875005e30d9de1ce7f426898e46fe912068412c"
MAX_FILES = 2000
MAX_UNCOMPRESSED_BYTES = 100 * 1024 * 1024
MAX_ARCHIVE_BYTES = MAX_UNCOMPRESSED_BYTES + 1024 * 1024
ALLOWED_MODES = {stat.S_IFREG | 0o644, stat.S_IFREG | 0o755}
BASELINE_IDENTITY = {
    "schema": "rei.run17.delta-baselines.v1",
    "repository": "cosmosapjw-quantum/rei_bianchi",
    "run16_git_commit": RUN16_HEAD,
    "run16_science_commit": "b808f9afddf3943eb0533bf86596d8bebb911ddd",
    "run16_archive": {
        "filename": "REI_RUN16_GAS_PATH_SENSITIVITY_20261019_100933Z.zip",
        "bytes": 2717511,
        "sha256": "fd4d51fb205944b35bdc59a452be6d9b4c0c794c14aa9f5da404633cbc990a51",
        "google_drive_url": "https://drive.google.com/file/d/1TT9-bLPv6OdgmEuR33y2PWAiDHgbz3TY/view",
        "dropbox_id": "id:BSpOijBcT10AAAAAAD_QvA",
    },
    "run15_git_commit": RUN15_HEAD,
    "run15_archive": {
        "filename": "REI_RUN15_RECOVERY_FIXED_GAS_NATIVE_20261019_085443Z.zip",
        "bytes": 41913080,
        "sha256": "8729696dbb1efb7a7a76f59b12afacaa22d9481210b505c3b674b201b7b89dcb",
        "google_drive_url": "https://drive.google.com/file/d/1oDJIWU2oqE7ABG8z2CNoLQOmz9TP_fXO/view",
        "dropbox_id": "id:BSpOijBcT10AAAAAAD_Qfw",
    },
    "run13_recovery_git_commit": "3dcb5f7aed8d33ff64f7952e9465f4239a216c89",
    "original_m2_packet_sha256": "67ec6958ac6f662125e049003d785c917c89e832b6bcbbd026ab8a332870b88a",
    "original_gas_binary_sha256": GAS_SHA,
    "baseline_evidence": "Pinned identities inherited from RUN16 delivery; this package does not rerun baseline calculations or redownload old archives.",
    "restore_choice": "Native sources and original inputs are available in pinned Git. Prior archives are recovery alternatives; neither old full archive is duplicated here.",
}


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def check_hex(value, length, label):
    if not isinstance(value, str) or len(value) != length or any(c not in "0123456789abcdef" for c in value):
        raise ValueError(label + " must be a full lowercase hexadecimal identity")


def safe_name(name):
    if (not isinstance(name, str) or not name or "\\" in name or ":" in name
            or any(ord(c) < 32 or ord(c) == 127 for c in name)
            or PurePosixPath(name).is_absolute()
            or any(part in ("", ".", "..") for part in name.split("/"))):
        raise ValueError("noncanonical relative path: " + repr(name))
    return name


def json_value(raw):
    def invalid(value):
        raise ValueError("nonfinite JSON constant: " + value)
    return json.loads(raw, parse_constant=invalid)


def science_rows(manifest):
    if (manifest.get("schema") != "rei.run17.complete-science-manifest.v1"
            or manifest.get("excludes_itself") is not True):
        raise ValueError("unsupported or self-referential science manifest")
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows or len(rows) > MAX_FILES - 6:
        raise ValueError("invalid science manifest row count")
    out = {}
    for row in rows:
        path = safe_name(row["path"])
        if path == "SCIENCE_MANIFEST.json" or path in out:
            raise ValueError("duplicate/self science manifest entry")
        if type(row["bytes"]) is not int or row["bytes"] < 0:
            raise ValueError("invalid science byte count")
        check_hex(row["sha256"], 64, "science SHA256")
        check_hex(row["git_blob"], 40, "science Git blob")
        if row["git_mode"] not in ("100644", "100755"):
            raise ValueError("science entry is not an ordinary Git file")
        out[path] = row
    if manifest.get("file_count_excluding_this_manifest") != len(out):
        raise ValueError("science manifest file count mismatch")
    if manifest.get("payload_bytes_excluding_this_manifest") != sum(r["bytes"] for r in out.values()):
        raise ValueError("science manifest total byte mismatch")
    return out


def _load(path, expected_sha256=None):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError("archive must be an ordinary file within the size cap")
    raw_zip = path.read_bytes()
    if len(raw_zip) > MAX_ARCHIVE_BYTES:
        raise ValueError("archive grew beyond its size cap")
    archive_sha = sha256(raw_zip)
    if expected_sha256 is not None:
        check_hex(expected_sha256, 64, "expected archive SHA256")
        if archive_sha != expected_sha256:
            raise ValueError("archive SHA256 mismatch")
    payload = {}
    with zipfile.ZipFile(io.BytesIO(raw_zip)) as archive:
        infos = archive.infolist()
        if any(info.orig_filename != info.filename for info in infos):
            raise ValueError("ZIP filename was truncated or normalized by the parser")
        names = [safe_name(i.filename) for i in infos]
        if len(names) != len(set(names)) or not 6 <= len(names) <= MAX_FILES:
            raise ValueError("duplicate or invalid number of archive entries")
        if sum(i.file_size for i in infos) > MAX_UNCOMPRESSED_BYTES:
            raise ValueError("RUN17 delta exceeds the 100 MiB uncompressed cap")
        info_map = {i.filename: i for i in infos}
        for info in infos:
            if (info.is_dir() or info.flag_bits & 1 or info.external_attr >> 16 not in ALLOWED_MODES
                    or info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)):
                raise ValueError("only unencrypted ordinary 0644/0755 ZIP files are allowed")
            payload[info.filename] = archive.read(info)
        # ZipFile.read verifies each member CRC; every member was read above.
        manifest_raw = payload["ARCHIVE_MANIFEST.json"]
        manifest = json_value(manifest_raw)
        if (manifest.get("schema") != "rei.run17.delta-archive-manifest.v1"
                or manifest.get("manifest_excludes_itself") is not True):
            raise ValueError("unsupported archive manifest")
        rows = manifest["files"]
        listed = [safe_name(r["path"]) for r in rows]
        if (len(listed) != len(set(listed)) or "ARCHIVE_MANIFEST.json" in listed
                or set(names) != set(listed) | {"ARCHIVE_MANIFEST.json"}):
            raise ValueError("manifest/archive membership mismatch")
        for row in rows:
            data = payload[row["path"]]
            actual = {"bytes": len(data), "sha256": sha256(data),
                      "mode": oct(info_map[row["path"]].external_attr >> 16)}
            if any(actual[k] != row[k] for k in actual):
                raise ValueError("manifest byte/mode mismatch: " + row["path"])
        if info_map["ARCHIVE_MANIFEST.json"].external_attr >> 16 != stat.S_IFREG | 0o644:
            raise ValueError("archive manifest must be an ordinary 0644 file")
        identity = json_value(payload["ARCHIVE_IDENTITY.json"])
        if identity.get("schema") != "rei.run17.delta-archive-identity.v1":
            raise ValueError("unsupported archive identity")
        check_hex(identity["science_commit"], 40, "science commit")
        check_hex(identity["science_tree"], 40, "science tree")
        if json_value(payload["BASELINE_IDENTITY.json"]) != BASELINE_IDENTITY:
            raise ValueError("pinned baseline identities changed")
        if (len(payload["runtime/gas_rhs_server"]) != GAS_BYTES
                or sha256(payload["runtime/gas_rhs_server"]) != GAS_SHA
                or info_map["runtime/gas_rhs_server"].external_attr >> 16 != stat.S_IFREG | 0o755):
            raise ValueError("original gas executable identity/mode mismatch")
        frozen_manifest = payload["run17/SCIENCE_MANIFEST.json"]
        frozen_rows = science_rows(json_value(frozen_manifest))
        expected = {"run17/" + p for p in frozen_rows} | {"run17/SCIENCE_MANIFEST.json"}
        metadata = {"ARCHIVE_MANIFEST.json", "ARCHIVE_IDENTITY.json", "BASELINE_IDENTITY.json",
                    "RESTORE_COMMANDS.md", "runtime/gas_rhs_server"}
        if set(names) != expected | metadata or sha256(frozen_manifest) != identity["science_manifest_sha256"]:
            raise ValueError("archive/frozen science membership or manifest identity mismatch")
        for rel, row in frozen_rows.items():
            name = "run17/" + rel
            data = payload[name]
            mode = "100755" if info_map[name].external_attr >> 16 == stat.S_IFREG | 0o755 else "100644"
            if (len(data) != row["bytes"] or sha256(data) != row["sha256"]
                    or git_blob(data) != row["git_blob"] or mode != row["git_mode"]):
                raise ValueError("frozen science byte/Git identity mismatch: " + rel)
        modes = {n: stat.S_IMODE(info_map[n].external_attr >> 16) for n in names}
    result = {
        "schema": "rei.run17.delta-archive-verification.v1",
        "archive_file": str(path.absolute()), "archive_bytes": len(raw_zip),
        "archive_sha256": archive_sha, "manifest_sha256": sha256(manifest_raw),
        "science_manifest_sha256": sha256(frozen_manifest),
        "payload_files": len(rows), "archive_entries": len(names),
        "science_files_including_manifest": len(expected),
        "uncompressed_bytes_including_manifest": sum(len(b) for b in payload.values()),
        "uncompressed_limit_bytes": MAX_UNCOMPRESSED_BYTES,
        "all_paths_regular_safe": True, "all_CRCs_match": True,
        "all_manifest_payload_hashes_and_modes_match": True,
        "all_frozen_science_hashes_Git_blobs_modes_match": True,
        "original_gas_binary_sha256": GAS_SHA, "baseline_identities_match": True,
        "science_commit": identity["science_commit"], "science_tree": identity["science_tree"],
        "extracted_files": 0, "scientific_calculations": 0,
        "scope": "Byte delivery only; no native execution or scientific accuracy certificate",
    }
    return result, payload, modes


def verify(path, expected_sha256=None):
    return _load(path, expected_sha256)[0]


def restore(path, destination, expected_sha256=None):
    result, payload, modes = _load(path, expected_sha256)
    destination = Path(destination).absolute()
    if os.path.lexists(destination):
        raise ValueError("restore destination must be new")
    if not destination.parent.is_dir():
        raise ValueError("restore parent must already exist")
    for p in [destination.parent, *destination.parent.parents]:
        if p.is_symlink():
            raise ValueError("restore parent path contains a symlink")
    destination.mkdir(mode=0o700)
    for name in sorted(payload):
        target = destination.joinpath(*PurePosixPath(name).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(payload[name])
        target.chmod(modes[name])
        if target.read_bytes() != payload[name] or stat.S_IMODE(target.stat().st_mode) != modes[name]:
            raise ValueError("restored byte/mode mismatch: " + name)
    result.update({"restore_destination": str(destination), "extracted_files": len(payload),
                   "all_restored_bytes_and_modes_match": True, "overwritten_files": 0,
                   "automatic_native_or_test_execution": False})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--sha256")
    parser.add_argument("--restore-to", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output is not None and os.path.lexists(args.output):
        raise ValueError("receipt output already exists")
    result = (restore(args.archive, args.restore_to, args.sha256) if args.restore_to
              else verify(args.archive, args.sha256))
    text = encoded(result)
    if args.output:
        with args.output.open("xb") as stream:
            stream.write(text)
    print(text.decode(), end="")


if __name__ == "__main__":
    main()
