#!/usr/bin/env python3
"""Restore PHYS83_CONT_BYTE_EXPORT_V1 bytes without importing scientific code.

Usage: python verify_archive_restore.py ORIGINAL.zip DOWNLOADED.zip NEW_OUTPUT_DIR
         --provider Drive --repo /path/to/WU088_HH
         --phys82-manifest /path/to/SCIENCE_PAYLOAD_MANIFEST.json

NEW_OUTPUT_DIR must not exist. All output is create-only. RESULT.json records
success or the first failure and partial counts; extracted/ contains actual
regular files, including BYTE_MANIFEST.json. --repo requires its current HEAD
to equal the archive commit. The optional PHYS82 check is a separate byte check,
never a scientific callback. A previous SCIENCE_FREEZE_CHECK.json is identified
as historical evidence and does not substitute for the current 51-file check.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat
import subprocess
import sys
import zipfile
import zlib


SCHEMA = "PHYS83_CONT_BYTE_EXPORT_V1"
REPO_UNIT = "research/hh_phys83_ce_completion_20261023"
PHYS82_UNIT = "research/hh_phys82_li_threshold_sensitivity_20261023"
PHYS82_ID = "caae042b139373a10c516d759854ad117d807e9f7ace8c365529a1621419b73f"
MANIFEST_NAME = "BYTE_MANIFEST.json"
PARENT_PINS = {
    "parent_recovery/PHYS82_FINAL_20261023_ca9d53983459.zip": (
        883808, "427427e8d809943e225d89b138cfe93761efd39d2d7fc787a733da92aed3da61"),
    "parent_recovery/PHYS82_FINAL_DELIVERY_20261023.json": (
        217324, "19eecc88f4a297ad8347678b8d08a0c6cd68581255538ec1f462d530280ee054"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def checked_hex(value, digits, label):
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{%d}" % digits, value),
            "INVALID_" + label)
    return value


def safe_name(name):
    require(isinstance(name, str) and name, "EMPTY_OR_NONSTRING_MEMBER_NAME")
    require("\\" not in name and not any(ord(c) < 32 for c in name),
            "UNSAFE_MEMBER_CHARACTERS: " + repr(name))
    parts = name.split("/")
    require(not any(p in ("", ".", "..") for p in parts),
            "NONCANONICAL_MEMBER_PATH: " + repr(name))
    require(not PurePosixPath(name).is_absolute() and not PureWindowsPath(name).drive,
            "ABSOLUTE_OR_DRIVE_MEMBER_PATH: " + repr(name))
    require(PurePosixPath(name).as_posix() == name, "NONCANONICAL_MEMBER_PATH")
    return name


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "DUPLICATE_JSON_KEY: " + key)
        result[key] = value
    return result


def read_json_bytes(data):
    def bad_constant(value):
        raise ValueError("NONFINITE_JSON_CONSTANT: " + value)
    result = json.loads(data.decode("utf-8"), object_pairs_hook=unique_object,
                        parse_constant=bad_constant)
    require(isinstance(result, dict), "JSON_OBJECT_REQUIRED")
    return result


def create_json(path, value):
    data = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def compare_complete_files(original, downloaded, result):
    require(original.is_file() and downloaded.is_file(), "BOTH_INPUTS_MUST_BE_FILES")
    require(not os.path.samefile(original, downloaded), "DISTINCT_ORIGINAL_AND_DOWNLOAD_REQUIRED")
    before = [p.stat() for p in (original, downloaded)]
    hashes = [hashlib.sha256(), hashlib.sha256()]
    counts = [0, 0]
    equal = True
    with original.open("rb") as left, downloaded.open("rb") as right:
        while True:
            blocks = (left.read(1024 * 1024), right.read(1024 * 1024))
            if not blocks[0] and not blocks[1]:
                break
            equal = equal and blocks[0] == blocks[1]
            for i, block in enumerate(blocks):
                hashes[i].update(block)
                counts[i] += len(block)
    result["complete_archive_bytes"] = {
        "original": {"path": str(original), "bytes": counts[0], "SHA256": hashes[0].hexdigest()},
        "downloaded": {"path": str(downloaded), "bytes": counts[1], "SHA256": hashes[1].hexdigest()},
        "byte_for_byte_equal": equal,
        "size_equal": counts[0] == counts[1],
        "SHA256_equal": hashes[0].digest() == hashes[1].digest(),
    }
    for i, path in enumerate((original, downloaded)):
        after = path.stat()
        require((before[i].st_dev, before[i].st_ino, before[i].st_size, before[i].st_mtime_ns)
                == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns),
                "INPUT_CHANGED_DURING_FULL_READ: " + str(path))
        require(counts[i] == before[i].st_size, "FULL_READ_SIZE_MISMATCH")
    require(equal and counts[0] == counts[1] and hashes[0].digest() == hashes[1].digest(),
            "DOWNLOADED_ARCHIVE_DOES_NOT_MATCH_ORIGINAL")
    result["complete_archive_bytes"]["status"] = "PASS"


def checked_members(archive):
    entries = archive.infolist()
    names = {}
    for item in entries:
        name = safe_name(item.filename)
        require(name == item.orig_filename, "ZIP_MEMBER_NAME_WAS_NORMALIZED")
        require(name not in names, "DUPLICATE_ZIP_MEMBER: " + name)
        require(not item.is_dir() and not (item.flag_bits & 1),
                "DIRECTORY_OR_ENCRYPTED_MEMBER_NOT_IN_EXPORT_SCHEMA: " + name)
        file_type = stat.S_IFMT(item.external_attr >> 16)
        require(file_type in (0, stat.S_IFREG), "NONREGULAR_ZIP_MEMBER: " + name)
        require(item.file_size >= 0 and item.compress_size >= 0, "NEGATIVE_MEMBER_SIZE")
        names[name] = item
    for name in names:
        for parent in PurePosixPath(name).parents:
            require(parent.as_posix() not in names, "FILE_DIRECTORY_MEMBER_COLLISION: " + name)
    return names


def checked_rows(rows, repository=False):
    require(isinstance(rows, list), "MANIFEST_FILE_LIST_REQUIRED")
    result = {}
    for row in rows:
        require(isinstance(row, dict), "MANIFEST_ROW_MUST_BE_OBJECT")
        name = safe_name(row.get("path"))
        require(name != MANIFEST_NAME and name not in result, "DUPLICATE_OR_SELF_MANIFEST_ROW")
        require(type(row.get("bytes")) is int and row["bytes"] >= 0, "INVALID_PAYLOAD_BYTE_COUNT")
        checked_hex(row.get("SHA256"), 64, "PAYLOAD_SHA256")
        if repository:
            checked_hex(row.get("git_blob_SHA1"), 40, "GIT_BLOB_SHA1")
        result[name] = row
    return result


def git(repo, *arguments):
    return subprocess.check_output(["git", "-C", str(repo), *arguments], stderr=subprocess.PIPE)


def prepare_git_check(repo, manifest, repo_rows, result):
    head = git(repo, "rev-parse", "--verify", "HEAD").decode("ascii").strip()
    require(head == manifest["commit"], "LOCAL_HEAD_DIFFERS_FROM_ARCHIVE_COMMIT")
    require(git(repo, "cat-file", "-t", head).strip() == b"commit", "LOCAL_HEAD_IS_NOT_COMMIT")
    commit_data = git(repo, "cat-file", "-p", head)
    tree_line = commit_data.split(b"\n", 1)[0]
    require(tree_line == ("tree " + manifest["tree"]).encode("ascii"), "LOCAL_COMMIT_TREE_MISMATCH")
    tree_rows = {}
    listing = git(repo, "ls-tree", "-rz", "--full-tree", head, "--", REPO_UNIT)
    for record in listing.split(b"\0"):
        if not record:
            continue
        spec, path = record.split(b"\t", 1)
        mode, kind, blob = spec.decode("ascii").split()
        name = safe_name(path.decode("utf-8"))
        require(kind == "blob", "NONBLOB_GIT_TREE_MEMBER: " + name)
        tree_rows[name] = {"mode": mode, "blob": blob}
    require(set(tree_rows) == set(repo_rows), "MANIFEST_DOES_NOT_COVER_EXACT_UNIT_GIT_TREE")
    for name, row in repo_rows.items():
        require(tree_rows[name] == {"mode": row["mode"], "blob": row["git_blob_SHA1"]},
                "GIT_TREE_PATH_MODE_OR_BLOB_MISMATCH: " + name)
    result["local_git"] = {"status": "HEAD_TREE_PASS_BLOB_READBACK_PENDING", "repo": str(repo),
                           "HEAD": head, "tree": manifest["tree"],
                           "unit_tree_rows": len(tree_rows), "claim": "local Git objects only"}


def restore_archive(original, downloaded, output, repo, result):
    counts = result["counts"]
    with zipfile.ZipFile(original) as original_zip, zipfile.ZipFile(downloaded) as downloaded_zip:
        original_members = checked_members(original_zip)
        members = checked_members(downloaded_zip)
        require(set(original_members) == set(members), "ZIP_MEMBER_SETS_DIFFER")
        require(MANIFEST_NAME in members, "BYTE_MANIFEST_MISSING")
        counts["zip_entries_expected"] = len(members)
        manifest = read_json_bytes(downloaded_zip.read(members[MANIFEST_NAME]))
        require(manifest.get("schema") == SCHEMA, "UNSUPPORTED_ARCHIVE_SCHEMA")
        checked_hex(manifest.get("commit"), 40, "COMMIT_SHA1")
        checked_hex(manifest.get("tree"), 40, "TREE_SHA1")
        require(manifest.get("HH_R10") == "OFF" and manifest.get("production_admission") == "NOT_ISSUED",
                "ARCHIVE_ADMISSION_SCOPE_MISMATCH")
        repo_rows = checked_rows(manifest.get("repository_files"), repository=True)
        private_rows = checked_rows(manifest.get("private_evidence_files"))
        require(repo_rows and not (set(repo_rows) & set(private_rows)), "OVERLAPPING_OR_EMPTY_REPOSITORY_ROWS")
        for name, row in repo_rows.items():
            require(name.startswith(REPO_UNIT + "/"), "REPOSITORY_PATH_OUTSIDE_EXPORTED_UNIT")
            require(row.get("mode") in ("100644", "100755"), "NONREGULAR_GIT_MODE")
        for name in private_rows:
            require(name.startswith(("private_evidence/", "parent_recovery/")), "INVALID_PRIVATE_EVIDENCE_PREFIX")
        payload = {**repo_rows, **private_rows}
        require(set(members) == set(payload) | {MANIFEST_NAME}, "PAYLOAD_MANIFEST_COVERAGE_MISMATCH")
        require(set(PARENT_PINS) <= set(private_rows), "PINNED_PARENT_RECOVERY_FILES_MISSING")
        counts.update(payload_entries_excluding_manifest_expected=len(payload),
                      repository_git_blobs_expected=len(repo_rows),
                      private_evidence_entries_expected=len(private_rows))
        result["archive_identity"] = {"schema": SCHEMA, "stage": manifest.get("stage"),
                                      "commit": manifest["commit"], "tree": manifest["tree"]}
        if repo is not None:
            prepare_git_check(repo, manifest, repo_rows, result)
        extract_root = output / "extracted"
        extract_root.mkdir()
        result["extraction_root"] = str(extract_root)
        result["entry_checks"] = []
        result["parent_recovery_bytes"] = []
        for name in sorted(members):
            item, original_item = members[name], original_members[name]
            expected = original_zip.read(original_item)
            require(len(expected) == original_item.file_size
                    and (zlib.crc32(expected) & 0xffffffff) == original_item.CRC,
                    "ORIGINAL_CRC_OR_SIZE_FAILURE: " + name)
            counts["original_crc_entries_verified"] += 1
            data = downloaded_zip.read(item)
            require(len(data) == item.file_size and (zlib.crc32(data) & 0xffffffff) == item.CRC,
                    "DOWNLOADED_CRC_OR_SIZE_FAILURE: " + name)
            counts["downloaded_crc_entries_verified"] += 1
            require(data == expected, "UNCOMPRESSED_BYTES_DIFFER_FROM_ORIGINAL: " + name)
            digest = sha256(data)
            detail = {"path": name, "bytes": len(data), "SHA256": digest,
                      "CRC32": f"{item.CRC:08x}", "status": "PASS"}
            if name != MANIFEST_NAME:
                row = payload[name]
                require(len(data) == row["bytes"] and digest == row["SHA256"],
                        "PAYLOAD_SHA256_OR_SIZE_MISMATCH: " + name)
                counts["payload_sha256_size_verified"] += 1
            if name in repo_rows:
                blob = git_blob_sha1(data)
                require(blob == repo_rows[name]["git_blob_SHA1"], "RECOMPUTED_GIT_BLOB_MISMATCH: " + name)
                detail["git_blob_SHA1"] = blob
                counts["repository_git_blobs_recomputed_verified"] += 1
                if repo is not None:
                    git_data = git(repo, "cat-file", "blob", manifest["commit"] + ":" + name)
                    require(git_data == data, "LOCAL_GIT_CAT_FILE_BYTES_MISMATCH: " + name)
                    counts["local_git_cat_file_blobs_verified"] += 1
            if name in PARENT_PINS:
                require((len(data), digest) == PARENT_PINS[name], "USER_PINNED_PARENT_BYTES_MISMATCH: " + name)
                result["parent_recovery_bytes"].append({"path": name, "bytes": len(data),
                                                        "SHA256": digest, "status": "PASS"})
            destination = extract_root.joinpath(*PurePosixPath(name).parts)
            require(destination.resolve().is_relative_to(extract_root.resolve()), "EXTRACTION_PATH_ESCAPE")
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("xb") as stream:
                stream.write(data)
            if name in repo_rows:
                os.chmod(destination, int(repo_rows[name]["mode"], 8) & 0o777)
                require(stat.S_IMODE(destination.stat().st_mode)
                        == (int(repo_rows[name]["mode"], 8) & 0o777),
                        "EXTRACTED_GIT_MODE_MISMATCH: " + name)
                detail["restored_git_mode"] = repo_rows[name]["mode"]
            counts["actual_files_extracted"] += 1
            require(destination.read_bytes() == expected, "EXTRACTED_FILE_BYTES_MISMATCH: " + name)
            counts["extracted_bytes_compared_to_original_verified"] += 1
            result["entry_checks"].append(detail)
        for key in ("original_crc_entries_verified", "downloaded_crc_entries_verified",
                    "actual_files_extracted", "extracted_bytes_compared_to_original_verified"):
            require(counts[key] == len(members), "INCOMPLETE_ENTRY_COUNT: " + key)
        require(counts["payload_sha256_size_verified"] == len(payload), "INCOMPLETE_PAYLOAD_COUNT")
        require(counts["repository_git_blobs_recomputed_verified"] == len(repo_rows), "INCOMPLETE_GIT_BLOB_COUNT")
        if repo is not None:
            require(counts["local_git_cat_file_blobs_verified"] == len(repo_rows), "INCOMPLETE_GIT_READBACK_COUNT")
            require(git(repo, "rev-parse", "--verify", "HEAD").decode("ascii").strip() == manifest["commit"],
                    "LOCAL_HEAD_CHANGED_DURING_RESTORE")
            result["local_git"]["status"] = "PASS"


def verify_phys82_current_bytes(repo, manifest_path, result):
    raw_manifest = manifest_path.read_bytes()
    manifest = read_json_bytes(raw_manifest)
    require(manifest.get("schema") == "PHYS82_FROZEN_SCIENCE_PAYLOAD_V1"
            and manifest.get("science_id") == PHYS82_ID, "PHYS82_FROZEN_IDENTITY_MISMATCH")
    rows = checked_rows(manifest.get("files"), repository=True)
    require(len(rows) == 51, "PHYS82_EXPECTED_EXACTLY_51_FROZEN_SCIENCE_FILES")
    section = {"status": "RUNNING", "scope": "current local PHYS82 unit bytes vs frozen manifest; separate from ZIP restoration counts",
               "manifest_path": str(manifest_path), "manifest_bytes": len(raw_manifest),
               "manifest_SHA256": sha256(raw_manifest), "science_id": PHYS82_ID,
               "expected_files": 51, "verified_files": 0, "scientific_callbacks": 0, "files": []}
    result["phys82_science51_preservation"] = section
    root = repo / PHYS82_UNIT
    for name, row in rows.items():
        path = root.joinpath(*PurePosixPath(name).parts)
        require(not path.is_symlink() and path.resolve().is_relative_to(root.resolve()), "PHYS82_NONREGULAR_OR_ESCAPING_PATH")
        require(path.is_file(), "PHYS82_FROZEN_FILE_MISSING: " + name)
        data = path.read_bytes()
        require(len(data) == row["bytes"] and sha256(data) == row["SHA256"]
                and git_blob_sha1(data) == row["git_blob_SHA1"], "PHYS82_FROZEN_BYTES_CHANGED: " + name)
        section["verified_files"] += 1
        section["files"].append({"path": name, "bytes": len(data), "SHA256": row["SHA256"],
                                 "git_blob_SHA1": row["git_blob_SHA1"], "status": "PASS"})
    prior = manifest_path.with_name("SCIENCE_FREEZE_CHECK.json")
    if prior.is_file():
        prior_raw = prior.read_bytes()
        section["previous_freeze_receipt"] = {
            "path": str(prior), "bytes": len(prior_raw), "SHA256": sha256(prior_raw),
            "content": read_json_bytes(prior_raw), "scope": "historical receipt read only; current result computed above"}
    section["status"] = "PASS"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("original_zip", type=Path)
    parser.add_argument("downloaded_zip", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--provider", default="UNSPECIFIED", help="Receipt label only; does not establish download provenance")
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--phys82-manifest", type=Path)
    args = parser.parse_args(argv)
    if args.phys82_manifest is not None and args.repo is None:
        parser.error("--phys82-manifest requires --repo")
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    result = {
        "schema": "PHYS83_FULL_BYTE_RESTORATION_V1", "status": "RUNNING", "started_utc": utc_now(),
        "provider_label": args.provider, "verifier_path": str(Path(__file__).resolve()),
        "verifier_SHA256": sha256(Path(__file__).read_bytes()),
        "scientific_callbacks": 0, "scientific_module_imports": 0, "historical_science_replays": 0,
        "scope": "full local original/download byte comparison and actual extraction; upload ACK and remote Git readback are separate receipts",
        "counts": {name: 0 for name in (
            "zip_entries_expected", "original_crc_entries_verified", "downloaded_crc_entries_verified",
            "payload_entries_excluding_manifest_expected", "payload_sha256_size_verified",
            "repository_git_blobs_expected", "repository_git_blobs_recomputed_verified",
            "private_evidence_entries_expected", "local_git_cat_file_blobs_verified",
            "actual_files_extracted", "extracted_bytes_compared_to_original_verified")},
        "local_git": {"status": "NOT_REQUESTED"},
        "phys82_science51_preservation": {"status": "NOT_REQUESTED"},
        "HH_R10": "OFF", "production_admission": "NOT_ISSUED",
    }
    try:
        original, downloaded = args.original_zip.resolve(strict=True), args.downloaded_zip.resolve(strict=True)
        repo = args.repo.resolve(strict=True) if args.repo is not None else None
        compare_complete_files(original, downloaded, result)
        restore_archive(original, downloaded, output, repo, result)
        if args.phys82_manifest is not None:
            verify_phys82_current_bytes(repo, args.phys82_manifest.resolve(strict=True), result)
        result["status"] = "PASS_FULL_BYTE_RESTORATION"
    except Exception as exc:
        result["status"] = "FAIL"
        result["error"] = {"type": type(exc).__name__, "message": str(exc)}
    result["finished_utc"] = utc_now()
    result_path = output / "RESULT.json"
    create_json(result_path, result)
    print(json.dumps({"status": result["status"], "result_json": str(result_path),
                      "counts": result["counts"], "local_git": result["local_git"]["status"],
                      "phys82_science51": result["phys82_science51_preservation"]["status"],
                      "error": result.get("error")}, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS_FULL_BYTE_RESTORATION" else 2


if __name__ == "__main__":
    sys.exit(main())
