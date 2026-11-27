#!/usr/bin/env python3
"""Build a create-only source ZIP from one exact committed BASS_HE snapshot.

This is packaging and byte/dependency verification only. It never imports or
runs scientific code and never uploads files or reads untracked source bytes.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import zipfile


NEW = "research/program_expansion_20261025/continuation_20261027"
OLD = "research/program_expansion_20261025/continuation_20261025"
HE34 = "research/he34_sandbox_certified_relaxation_20261022"
HE101 = "research/he_ang_finitemass_cba_20261025"
EXPANSION = "research/program_expansion_20261025"
BASELINE_COMMIT = "ac6042a6b0610b09d0576538767ee0299389a5eb"
EXTRA_REQUIRED = (
    "AGENTS.md",
    f"{EXPANSION}/HANDOFF_KO.md",
    f"{EXPANSION}/REPO_CHARTER_KO.md",
    f"{EXPANSION}/TASK_ASSIGNMENT.json",
    f"{EXPANSION}/CENTRAL_REFERENCE.json",
    f"{HE34}/src/neutral_transport.py",
    f"{HE34}/data/NEUTRAL_H_HE_TRANSPORT_SUBSET.json",
    f"{HE34}/results/NEUTRAL_TRANSPORT.json",
    f"{HE101}/CLAIM_GATE.json",
    f"{HE101}/evidence/execution/RESOURCE_LEDGER.json",
)
REQUIRED = EXTRA_REQUIRED + (
    f"{NEW}/RESULT.json", f"{NEW}/HANDOFF_KO.md", f"{NEW}/DAG.json",
    f"{NEW}/MODEL_CONTRACT.json", f"{NEW}/VALIDATION_CONTRACT.json",
    f"{NEW}/sources/TESTED_DEPENDENCIES_01.json",
    f"{NEW}/evidence/validation/01_tests/START.json",
    f"{NEW}/evidence/validation/01_tests/FINISH.json",
    f"{NEW}/evidence/validation/RESOURCE_LEDGER.json",
    f"{OLD}/run_validation.py",
    f"{OLD}/exchange/exchange_closure.py",
    f"{OLD}/pair_source/h_he_intake.py",
    f"{OLD}/pair_source/upstream/COPYING",
    f"{OLD}/pair_source/upstream/COPYING.LESSER",
)


def git(repo, *args):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout


def tree(repo, sha, *pathspec):
    data = git(repo, "ls-tree", "-r", "-z", "--full-tree", sha, "--", *pathspec)
    result = {}
    for record in data.split(b"\0"):
        if not record:
            continue
        head, path_bytes = record.split(b"\t", 1)
        mode, kind, blob = head.decode("ascii").split()
        path = path_bytes.decode("utf-8")
        parts = PurePosixPath(path).parts
        if path.startswith("/") or ".." in parts or "\\" in path:
            raise ValueError(f"Unsafe archive path: {path}")
        if kind != "blob" or mode not in ("100644", "100755"):
            raise ValueError(f"Non-regular source entry: {path} ({mode}, {kind})")
        if (path.lower().endswith((".pdf", ".pyc", ".pyo", ".tmp", ".swp"))
                or any(part in ("__pycache__", ".git", ".pytest_cache") for part in parts)
                or any(part.startswith(".tmp") for part in parts)):
            raise ValueError(f"Excluded data found inside the requested source scope: {path}")
        result[path] = {"path": path, "mode": mode, "git_blob": blob}
    return result


def blob_identity(content):
    return hashlib.sha1(b"blob " + str(len(content)).encode("ascii") + b"\0" + content).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def assert_dependency(files, path, expected_hash, expected_bytes=None, expected_blob=None):
    if path not in files:
        raise ValueError(f"Required dependency absent from archive: {path}")
    data = files[path]
    if hashlib.sha256(data).hexdigest() != expected_hash:
        raise ValueError(f"Dependency SHA256 mismatch: {path}")
    if expected_bytes is not None and len(data) != expected_bytes:
        raise ValueError(f"Dependency byte count mismatch: {path}")
    if expected_blob is not None and blob_identity(data) != expected_blob:
        raise ValueError(f"Dependency Git blob mismatch: {path}")


def check_dependencies(files, repo):
    checks = []
    # Bind the actually tested implementation, inherited runner and old ledgers.
    for path in sorted(files):
        if path.startswith(f"{NEW}/sources/TESTED_DEPENDENCIES_") and path.endswith(".json"):
            document = json.loads(files[path])
            for row in document["files"]:
                assert_dependency(files, row["path"], row["sha256"], row.get("bytes"))
            checks.append({"kind": "tested_dependency_manifest", "path": path,
                           "rows_verified": len(document["files"])})
    preservation_path = f"{NEW}/evidence/INHERITED_PRESERVATION.json"
    preservation = json.loads(files[preservation_path])
    for row in preservation["files"]:
        assert_dependency(files, row["path"], row["sha256"])
        if row["unchanged"] is not True:
            raise ValueError("An inherited preservation row is not unchanged")
    checks.append({"kind": "preserved_inherited_files", "path": preservation_path,
                   "rows_verified": len(preservation["files"])})
    # Every successful source test START binds its local test/source inputs.
    for path in sorted(files):
        if path.startswith(f"{NEW}/evidence/validation/") and path.endswith("/START.json"):
            start = json.loads(files[path])
            for relative, expected in start["source_sha256"].items():
                assert_dependency(files, f"{NEW}/{relative}", expected)
            checks.append({"kind": "recorded_START_inputs", "path": path,
                           "rows_verified": len(start["source_sha256"])})
    source_manifest_path = f"{NEW}/sources/SOURCE_MANIFEST.json"
    source_manifest = json.loads(files[source_manifest_path])
    for row in source_manifest["files"]:
        assert_dependency(files, f"{NEW}/sources/{row['local_path']}", row["sha256"],
                          row.get("bytes"), row.get("git_blob"))
    checks.append({"kind": "imported_source_manifest", "path": source_manifest_path,
                   "rows_verified": len(source_manifest["files"])})
    diagnostic_path = f"{NEW}/evidence/SOURCE_DIAGNOSTIC.json"
    diagnostic = json.loads(files[diagnostic_path])
    if "selected_source_diagnostic" in diagnostic:
        diagnostic = diagnostic["selected_source_diagnostic"]
    for row in diagnostic["evidence"]:
        source_path = Path(row["path"])
        if source_path.is_absolute():
            source_path = source_path.relative_to(repo)
        assert_dependency(files, source_path.as_posix(), row["sha256"])
    checks.append({"kind": "source_diagnostic_dependencies", "path": diagnostic_path,
                   "rows_verified": len(diagnostic["evidence"])})
    return checks


def make_zip(files, modes):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
        for path in sorted(files):
            member = zipfile.ZipInfo(path, (1980, 1, 1, 0, 0, 0))
            member.create_system = 3
            member.compress_type = zipfile.ZIP_STORED
            member.external_attr = int(modes.get(path, "100644"), 8) << 16
            archive.writestr(member, files[path])
    return buffer.getvalue()


def create_or_reuse_identical(path, content):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent,
                                         prefix=".archive_write_", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)  # Atomic create, never replaces an existing file.
            directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
            return "CREATED"
        except FileExistsError:
            if path.read_bytes() != content:
                raise ValueError(f"An unequal artifact already exists: {path}")
            return "REUSED_IDENTICAL_LOCAL_BYTES"
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--source", required=True, help="Exact 40-hex source commit SHA")
    parser.add_argument("--output-directory", type=Path, required=True)
    args = parser.parse_args()
    if re.fullmatch(r"[0-9a-f]{40}", args.source) is None:
        raise ValueError("An exact lowercase 40-hex commit SHA is required")
    repo = args.repo.resolve()
    resolved = git(repo, "rev-parse", "--verify", args.source + "^{commit}").decode().strip()
    if resolved != args.source:
        raise ValueError("Source does not identify the requested commit exactly")
    metadata = git(repo, "show", "-s", "--format=%H%n%T%n%P%n%ct", args.source).decode().splitlines()
    source_sha, source_tree, parents, epoch = metadata
    entries = tree(repo, source_sha, NEW, OLD, *EXTRA_REQUIRED)
    missing = sorted(set(REQUIRED) - set(entries))
    if missing:
        raise ValueError(f"Required committed source files are absent: {missing}")
    inherited = {p: v for p, v in entries.items() if p.startswith(OLD + "/")}
    if inherited != tree(repo, BASELINE_COMMIT, OLD):
        raise ValueError("The complete inherited INTAKE01 tree changed from the baseline")
    source_files, rows, modes = {}, [], {}
    for path, item in sorted(entries.items()):
        content = git(repo, "show", f"{source_sha}:{path}")
        if blob_identity(content) != item["git_blob"]:
            raise ValueError(f"Git blob identity mismatch: {path}")
        source_files[path] = content
        modes[path] = item["mode"]
        rows.append({**item, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
    dependency_checks = check_dependencies(source_files, repo)
    result = json.loads(source_files[f"{NEW}/RESULT.json"])
    context = {
        "schema": "HE_DRIFT02_SOURCE_ARCHIVE_CONTEXT_V1",
        "unit_id": result["unit_id"],
        "repository": "cosmosapjw-quantum/BASS_HE",
        "source_commit": source_sha,
        "source_tree": source_tree,
        "source_parents": parents.split(),
        "source_commit_time_utc": datetime.fromtimestamp(int(epoch), timezone.utc).isoformat(),
        "inherited_baseline_commit": BASELINE_COMMIT,
        "scope": "Reproducible task source snapshot and required unchanged dependencies; not whole repository or Git history",
        "source_layout": "BASS_HE-relative paths, with no wrapper directory",
        "science_reexecuted": False,
        "untracked_files_included": False,
        "upstream_license_paths": [f"{OLD}/pair_source/upstream/COPYING",
                                   f"{OLD}/pair_source/upstream/COPYING.LESSER"],
        "restore": ["Extract into a new empty directory while preserving member paths.",
                    "Read the new unit HANDOFF_KO.md, RESULT.json, validation evidence and independent review.",
                    "Reuse the recorded successful checks and unchanged dependencies; do not rerun old suites by default.",
                    "Read later delivery metadata overlays separately from this immutable source snapshot."],
        "zip_format": {"compression": "ZIP_STORED", "member_order": "lexicographic",
                       "member_timestamp": "1980-01-01T00:00:00", "unix_file_modes": True},
    }
    context_content = json_bytes(context)
    manifest = {
        "schema": "HE_DRIFT02_SOURCE_ARCHIVE_MANIFEST_V1",
        "source_commit": source_sha, "source_tree": source_tree,
        "source_file_count": len(rows), "source_files": rows,
        "inherited_tree_file_count": len(inherited),
        "inherited_tree_byte_identity": "PASS_UNCHANGED_COMMITTED_TREE",
        "dependency_checks": dependency_checks,
        "derived_context": {"path": "ARCHIVE_CONTEXT.json", "bytes": len(context_content),
                            "sha256": hashlib.sha256(context_content).hexdigest()},
        "manifest_self_hash": "Excluded to avoid self-reference; outer archive receipt binds this member",
    }
    files = {**source_files, "ARCHIVE_CONTEXT.json": context_content,
             "SOURCE_MANIFEST.json": json_bytes(manifest)}
    archive_bytes = make_zip(files, modes)
    # Pure packaging reproducibility; no code/module from the source is executed.
    if make_zip(files, modes) != archive_bytes:
        raise ValueError("Deterministic ZIP reconstruction differs")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        if archive.testzip() is not None or sorted(archive.namelist()) != sorted(files):
            raise ValueError("ZIP CRC or complete member listing differs")
        for path, content in files.items():
            if archive.read(path) != content:
                raise ValueError(f"ZIP member bytes differ: {path}")
    args.output_directory.mkdir(parents=True, exist_ok=True)
    filename = f"BASS_HE_HE_EXP_DRIFT02_SOURCE_20261027_{source_sha[:8]}.zip"
    archive_path = args.output_directory.resolve() / filename
    local_action = create_or_reuse_identical(archive_path, archive_bytes)
    receipt = {
        "schema": "HE_DRIFT02_SOURCE_ARCHIVE_RECEIPT_V1",
        "status": "PASS_ARCHIVE_BYTES_AND_DEPENDENCIES_ONLY",
        "source_commit": source_sha, "source_tree": source_tree, "source_parents": parents.split(),
        "archive": {"filename": filename, "local_path": str(archive_path),
                    "bytes": len(archive_bytes), "sha256": hashlib.sha256(archive_bytes).hexdigest(),
                    "source_file_count": len(rows), "zip_member_count": len(files)},
        "inherited_tree_file_count": len(inherited), "dependency_checks": dependency_checks,
        "checks": {"git_blob_identity": True, "manifest_SHA256_and_bytes": True,
                   "all_required_dependencies_included": True, "inherited_tree_unchanged": True,
                   "zip_CRC": True, "zip_member_bytes": True, "deterministic_rebuild_byte_identity": True},
        "scientific_executions": 0, "uploads": 0,
        "builder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    receipt_path = archive_path.with_suffix(".receipt.json")
    create_or_reuse_identical(receipt_path, json_bytes(receipt))
    manifest_path = archive_path.with_suffix(".manifest.json")
    create_or_reuse_identical(manifest_path, json_bytes(manifest))
    print(json.dumps({"status": receipt["status"], "local_action": local_action,
                      **receipt["archive"], "receipt_path": str(receipt_path),
                      "manifest_path": str(manifest_path),
                      "dependency_groups_verified": len(dependency_checks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
