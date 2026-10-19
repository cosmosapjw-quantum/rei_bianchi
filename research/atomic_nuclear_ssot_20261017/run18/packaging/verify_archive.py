#!/usr/bin/env python3
"""Verify or safely restore a RUN18 delta archive; execute no scientific code."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import stat
import zipfile

MAX_FILES = 2000
MAX_UNCOMPRESSED_BYTES = 100 * 1024 * 1024
MAX_ARCHIVE_BYTES = MAX_UNCOMPRESSED_BYTES
ALLOWED_MODES = {stat.S_IFREG | 0o644, stat.S_IFREG | 0o755}
SCIENCE_GIT_PREFIX = "research/atomic_nuclear_ssot_20261017/run18"
BASELINE_IDENTITY = {
    "schema": "rei.run18.delta-baselines.v1",
    "repository": "cosmosapjw-quantum/rei_bianchi",
    "run17_science_commit": "589ffbaff7b74a6cf1dbaf797285f15a58131dbd",
    "run17_science_tree": "b2c5d15e8f4baf0fc12d03ac40a86110c187a37e",
    "run17_science_manifest_sha256": "256b084717e1039da6cdc1ac53d44d726c0f0a85f06a02387639a0db53dfaae7",
    "run17_archive": {
        "filename": "REI_RUN17_FIRST_BIRTH_RESIDUAL_20261019_125500Z.zip",
        "bytes": 4247502,
        "sha256": "2392f298e8c93aaba0bd802a14c0b34c142bf2c848fbae83d6aa80302de1f523",
    },
    "baseline_is_immediate_parent": False,
    "baseline_scope": "Pinned science reference; a later RUN17 delivery commit may be the explicit RUN18 immediate parent.",
    "original_gas_binary_duplicated": False,
    "runtime_scope": "RUN18 exact adapter binary and official crate archives are already in the frozen science payload.",
    "baseline_evidence": "Exact identity read from the preserved RUN17 packaging receipt; no baseline download or scientific rerun during RUN18 packaging.",
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
    if (manifest.get("schema") != "rei.run18.complete-science-manifest.v1"
            or manifest.get("excludes_itself") is not True):
        raise ValueError("unsupported or self-referential science manifest")
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows or len(rows) > MAX_FILES - 5:
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
            raise ValueError("RUN18 delta exceeds the 100 MiB uncompressed cap")
        info_map = {i.filename: i for i in infos}
        for info in infos:
            if (info.is_dir() or info.flag_bits & 1 or info.external_attr >> 16 not in ALLOWED_MODES
                    or info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)):
                raise ValueError("only unencrypted ordinary 0644/0755 ZIP files are allowed")
            data = archive.read(info)
            if len(data) != info.file_size:
                raise ValueError("ZIP member size mismatch")
            payload[info.filename] = data
        # ZipFile.read verifies each member CRC; every member was read above.
        manifest_raw = payload["ARCHIVE_MANIFEST.json"]
        manifest = json_value(manifest_raw)
        if (manifest.get("schema") != "rei.run18.delta-archive-manifest.v1"
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
        if identity.get("schema") != "rei.run18.delta-archive-identity.v1":
            raise ValueError("unsupported archive identity")
        check_hex(identity["science_commit"], 40, "science commit")
        check_hex(identity["science_tree"], 40, "science tree")
        check_hex(identity["parent_commit"], 40, "immediate parent commit")
        if identity.get("git_source_checked_before_archive") is not True:
            raise ValueError("archive lacks the required committed-source gate record")
        if json_value(payload["BASELINE_IDENTITY.json"]) != BASELINE_IDENTITY:
            raise ValueError("pinned baseline identities changed")
        frozen_manifest = payload["run18/SCIENCE_MANIFEST.json"]
        frozen_rows = science_rows(json_value(frozen_manifest))
        expected = {"run18/" + p for p in frozen_rows} | {"run18/SCIENCE_MANIFEST.json"}
        metadata = {"ARCHIVE_MANIFEST.json", "ARCHIVE_IDENTITY.json", "BASELINE_IDENTITY.json",
                    "RESTORE_COMMANDS.md"}
        if set(names) != expected | metadata or sha256(frozen_manifest) != identity["science_manifest_sha256"]:
            raise ValueError("archive/frozen science membership or manifest identity mismatch")
        for rel, row in frozen_rows.items():
            name = "run18/" + rel
            data = payload[name]
            mode = "100755" if info_map[name].external_attr >> 16 == stat.S_IFREG | 0o755 else "100644"
            if (len(data) != row["bytes"] or sha256(data) != row["sha256"]
                    or git_blob(data) != row["git_blob"] or mode != row["git_mode"]):
                raise ValueError("frozen science byte/Git identity mismatch: " + rel)
        modes = {n: stat.S_IMODE(info_map[n].external_attr >> 16) for n in names}
    result = {
        "schema": "rei.run18.delta-archive-verification.v1",
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
        "baseline_identities_match": True, "extra_gas_binary_added": False,
        "science_commit": identity["science_commit"], "science_tree": identity["science_tree"],
        "parent_commit": identity["parent_commit"],
        "git_source_gate_recorded_by_creator": True,
        "remote_Git_or_prior_archive_requeried_by_verifier": False,
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
