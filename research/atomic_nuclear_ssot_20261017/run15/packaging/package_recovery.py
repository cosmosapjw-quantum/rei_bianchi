#!/usr/bin/env python3
"""Create a deterministic, hashed recovery archive without mutating inputs.

The input root may be a canonical Git staging tree. Its relative paths are
preserved under run15/; no local-to-Git path remapping is performed here.
"""
import argparse
import hashlib
import json
import os
import stat
import zipfile
from pathlib import Path

EXCLUDED_DIRECTORY_NAMES = frozenset({"target", "cargo_home", "source_copy", "__pycache__", ".git"})
EXCLUDED_SUBTREES = (
    Path("recovery/toolchain"),
    Path("recovery/postloss_native_build"),
    Path("recovery/postloss_gas_build"),
)
EXCLUDED_EXACT_FILES = frozenset({"recovery/POSTLOSS_NATIVE_SOURCE_AND_EVIDENCE.zip"})
EXCLUDED_SUFFIXES = frozenset({".pyc", ".pyo", ".xz"})
CURATED_RUNTIME_PREFIX = Path("recovery/postloss_runtime_delivery")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def exclusion_reason(rel):
    if any(part in EXCLUDED_DIRECTORY_NAMES for part in rel.parts):
        return "runtime cache or duplicate source-copy directory"
    for subtree in EXCLUDED_SUBTREES:
        if rel == subtree or subtree in rel.parents:
            return "large runtime or duplicate build working subtree"
    # Curated runtime delivery contains small official checksum/JSON evidence
    # under a directory also named toolchain. Preserve those records.
    in_curated_runtime = rel == CURATED_RUNTIME_PREFIX or CURATED_RUNTIME_PREFIX in rel.parents
    if "toolchain" in rel.parts and not in_curated_runtime:
        return "unbundled toolchain directory"
    if rel.as_posix() in EXCLUDED_EXACT_FILES:
        return "intermediate archive duplicating retained source and evidence"
    if rel.name.startswith("SALVAGE_PUBLICATION_"):
        return "superseded intermediate publication receipt"
    if rel.suffix in EXCLUDED_SUFFIXES:
        return "bytecode or compressed toolchain download"
    return None


def collect_payload(root, only):
    payload = []
    excluded = []
    for directory, dirs, files in os.walk(root, followlinks=False):
        current = Path(directory)
        admitted_dirs = []
        for name in sorted(dirs):
            path = current / name
            rel = path.relative_to(root)
            reason = exclusion_reason(rel)
            if reason is not None:
                excluded.append({"path": rel.as_posix(), "reason": reason})
            elif path.is_symlink():
                raise ValueError("symlink not admitted: " + str(rel))
            else:
                admitted_dirs.append(name)
        dirs[:] = admitted_dirs
        for name in sorted(files):
            path = current / name
            rel = path.relative_to(root)
            reason = exclusion_reason(rel)
            if reason is not None:
                excluded.append({"path": rel.as_posix(), "reason": reason})
                continue
            if only and rel.parts[0] not in only and rel.as_posix() != "INCIDENT_AND_RESULTS_20261019.json":
                continue
            if path.is_symlink() or not path.is_file():
                raise ValueError("non-regular source not admitted: " + str(rel))
            executable_binary = rel.parts[0] == "bin" and bool(path.stat().st_mode & 0o111)
            mode = 0o755 if executable_binary else 0o644
            payload.append(("run15/" + rel.as_posix(), path.read_bytes(), mode))
    payload.sort(key=lambda item: item[0])
    excluded.sort(key=lambda item: item["path"])
    return payload, excluded


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--original-run13", type=Path)
    parser.add_argument("--git-head", required=True)
    parser.add_argument("--only", action="append", default=[])
    options = parser.parse_args()
    root = options.root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("root must be a directory")
    manifest_path = options.output.with_suffix(".manifest.json")
    receipt_path = options.output.with_suffix(".receipt.json")
    if any(path.exists() or path.is_symlink() for path in [options.output, manifest_path, receipt_path]):
        raise ValueError("archive and sidecar paths must all be new")
    payload, excluded = collect_payload(root, options.only)
    if options.original_run13:
        data = options.original_run13.read_bytes()
        if len(data) != 41075268 or sha(data) != "6912c7f90dedaaee312d3fdc3248e4e8839409c0fb2944262de945e1b2f34e96":
            raise ValueError("original RUN13 archive identity mismatch")
        payload.append(("original/REI_ATOMIC_NUCLEAR_RUN13_M2_CONVERGENCE_20261018.zip", data, 0o644))
    meta = {
        "schema": "rei.run15.recovery_archive.v1",
        "git_checkpoint": options.git_head,
        "original_RUN15_four_case_raw_states_included": False,
        "scope": "Read per-file evidence admission; partial source and transcript records are not recovered raw IVP states.",
        "archive_policy": {
            "relative_layout": "run15/<root-relative-path>",
            "excluded_directory_names": sorted(EXCLUDED_DIRECTORY_NAMES),
            "excluded_subtrees": [path.as_posix() for path in EXCLUDED_SUBTREES],
            "excluded_exact_files": sorted(EXCLUDED_EXACT_FILES),
            "excluded_suffixes": sorted(EXCLUDED_SUFFIXES),
            "excluded_name_prefix": "SALVAGE_PUBLICATION_",
            "curated_toolchain_evidence_exception": CURATED_RUNTIME_PREFIX.as_posix(),
            "mode_policy": "0755 for executable files under bin/; 0644 for all other files; no privileged mode bits",
        },
        "excluded_paths": excluded,
        "files": [{"path": name, "bytes": len(data), "sha256": sha(data), "mode": format(mode, "04o")}
                  for name, data, mode in payload],
    }
    manifest = (json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode()
    payload.append(("MANIFEST.json", manifest, 0o644))
    names = [name for name, _, _ in payload]
    if len(names) != len(set(names)):
        raise ValueError("duplicate archive member name")
    with zipfile.ZipFile(options.output, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, data, mode in payload:
            info = zipfile.ZipInfo(name, (2026, 10, 19, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | mode) << 16
            archive.writestr(info, data, compresslevel=6)
    with zipfile.ZipFile(options.output) as archive:
        if archive.testzip() is not None:
            raise ValueError("archive CRC check failed")
        if archive.read("MANIFEST.json") != manifest:
            raise ValueError("stored manifest bytes changed")
        for entry in meta["files"]:
            data = archive.read(entry["path"])
            if len(data) != entry["bytes"] or sha(data) != entry["sha256"]:
                raise ValueError("archive member identity mismatch: " + entry["path"])
            mode = (archive.getinfo(entry["path"]).external_attr >> 16) & 0o777
            if mode != int(entry["mode"], 8):
                raise ValueError("archive member mode mismatch: " + entry["path"])
    receipt = {
        "archive": str(options.output.resolve()), "bytes": options.output.stat().st_size,
        "sha256": sha(options.output.read_bytes()), "manifest_sha256": sha(manifest),
        "payload_file_count": len(meta["files"]), "CRC_and_all_manifest_files": "PASS",
        "all_recorded_modes_verified": True, "git_checkpoint": options.git_head,
        "original_RUN15_four_case_raw_states_included": False,
    }
    with manifest_path.open("xb") as stream:
        stream.write(manifest)
    with receipt_path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
