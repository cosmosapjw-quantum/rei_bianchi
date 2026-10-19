#!/usr/bin/env python3
"""Create a deterministic, frozen RUN17 delta ZIP without scientific execution."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import platform
import stat
import sys
import tempfile
import zipfile
import zlib

from verify_archive import (BASELINE_IDENTITY, GAS_BYTES, GAS_SHA, MAX_FILES,
                            MAX_UNCOMPRESSED_BYTES, check_hex, encoded, git_blob,
                            json_value, safe_name, science_rows, sha256, verify)

ZIP_STAMP = (1980, 1, 1, 0, 0, 0)


def source_payload(root):
    if root.is_symlink() or not root.is_dir():
        raise ValueError("science root must be an ordinary directory")
    data = {}
    total = 0
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("symlink in frozen science source")
        name = safe_name(path.relative_to(root).as_posix())
        if (any(p.startswith(".") or p == "__pycache__" for p in Path(name).parts)
                or path.suffix == ".pyc"):
            raise ValueError("pending/hidden/cache source must not enter the frozen archive")
        if path.is_dir():
            continue
        if not stat.S_ISREG(path.stat().st_mode):
            raise ValueError("nonordinary frozen science source")
        total += path.stat().st_size
        if total > MAX_UNCOMPRESSED_BYTES or len(data) >= MAX_FILES - 6:
            raise ValueError("science payload exceeds the declared delta cap")
        raw = path.read_bytes()
        mode = stat.S_IFREG | (0o755 if path.stat().st_mode & 0o111 else 0o644)
        data[name] = (raw, mode)
    manifest_raw = data["SCIENCE_MANIFEST.json"][0]
    rows = science_rows(json_value(manifest_raw))
    if set(data) != set(rows) | {"SCIENCE_MANIFEST.json"}:
        raise ValueError("science files differ from the frozen science manifest")
    for name, row in rows.items():
        raw, mode = data[name]
        actual_mode = "100755" if mode & 0o111 else "100644"
        if (len(raw) != row["bytes"] or sha256(raw) != row["sha256"]
                or git_blob(raw) != row["git_blob"] or actual_mode != row["git_mode"]):
            raise ValueError("science manifest byte/Git/mode mismatch: " + name)
    return data, manifest_raw


def restore_commands(science_commit):
    return ("# RUN17 delta restoration\n\n"
            "This archive contains the frozen RUN17 source/results and the original gas binary. "
            "Original native source and earlier inputs come from the pinned Git history. "
            "The previous full archives are optional recovery alternatives.\n\n"
            "ZIP timestamps are fixed serialization metadata, not execution dates. "
            "The archive SHA256 is supplied by the external delivery receipt.\n\n"
            "## Clean pinned Git checkout\n\n```sh\n"
            "git init /tmp/rei_run17_clean_source\n"
            "git -C /tmp/rei_run17_clean_source remote add origin https://github.com/cosmosapjw-quantum/rei_bianchi.git\n"
            "git -C /tmp/rei_run17_clean_source sparse-checkout init --cone\n"
            "git -C /tmp/rei_run17_clean_source sparse-checkout set research/atomic_nuclear_ssot_20261017/run10 research/atomic_nuclear_ssot_20261017/run13 research/atomic_nuclear_ssot_20261017/run15 research/atomic_nuclear_ssot_20261017/run16 research/atomic_nuclear_ssot_20261017/run17\n"
            f"git -C /tmp/rei_run17_clean_source fetch --depth=1 --filter=blob:none origin {science_commit} {BASELINE_IDENTITY['run16_git_commit']}\n"
            f"git -C /tmp/rei_run17_clean_source checkout --detach {science_commit}\n"
            "```\n\n## Verify and restore this delta to a new directory\n\n"
            "Set RUN17_ARCHIVE and RUN17_ARCHIVE_SHA256 from the external delivery record.\n\n```sh\n"
            "python3 -B /tmp/rei_run17_clean_source/research/atomic_nuclear_ssot_20261017/run17/packaging/verify_archive.py \"$RUN17_ARCHIVE\" --sha256 \"$RUN17_ARCHIVE_SHA256\" --restore-to /tmp/rei_run17_delta_restore\n"
            "```\n\n## Optional original RUN13 byte completion\n\n"
            "Only the two existing lossless Git transport objects need joining; this executes no IVP.\n\n```sh\n"
            "python3 -B /tmp/rei_run17_clean_source/research/atomic_nuclear_ssot_20261017/run13/git_transport/restore.py --destination-root /tmp/rei_run17_clean_source/research/atomic_nuclear_ssot_20261017/run13/recovered\n"
            "```\n\n## Scoped Python checks and saved-state analysis\n\n"
            "Use the frozen RUN17 REPRODUCE_KO.md for the exact core-module/unit and archived-state postprocessing commands. "
            "Those commands and their source filenames belong to the final science payload. "
            "Archive verification/restoration itself never launches them, a native binary, or a campaign. "
            "The packaged gas binary is runtime/gas_rhs_server, SHA256 " + GAS_SHA + ".\n"
            "Any compiler or toolchain recovery follows the pinned baseline reproduction receipt. "
            "The toolchain itself is not duplicated in this delta.\n").encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run17-root", type=Path, required=True)
    parser.add_argument("--gas-binary", type=Path, required=True)
    parser.add_argument("--science-commit", required=True)
    parser.add_argument("--science-tree", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    check_hex(args.science_commit, 40, "science commit")
    check_hex(args.science_tree, 40, "science tree")
    if args.run17_root.is_symlink() or args.gas_binary.is_symlink():
        raise ValueError("source root and gas binary cannot be symlinks")
    root = args.run17_root.resolve()
    binary = args.gas_binary.resolve()
    output = args.output.absolute()
    receipt = args.receipt.absolute() if args.receipt else output.with_suffix(output.suffix + ".receipt.json")
    if output == receipt or os.path.lexists(output) or os.path.lexists(receipt):
        raise ValueError("archive and receipt must be distinct new paths")
    if output.is_relative_to(root) or receipt.is_relative_to(root):
        raise ValueError("archive/receipt cannot be inside the frozen science root")
    if not output.parent.is_dir() or not receipt.parent.is_dir():
        raise ValueError("output parents must already exist")
    source, science_manifest_raw = source_payload(root)
    if not binary.is_file() or not stat.S_ISREG(binary.stat().st_mode) or binary.stat().st_size != GAS_BYTES:
        raise ValueError("original gas executable must be an ordinary file of the expected size")
    gas = binary.read_bytes()
    if len(gas) != GAS_BYTES or sha256(gas) != GAS_SHA:
        raise ValueError("original gas executable byte identity required")
    payload = {"run17/" + p: item for p, item in source.items()}
    payload["runtime/gas_rhs_server"] = (gas, stat.S_IFREG | 0o755)
    payload["BASELINE_IDENTITY.json"] = (encoded(BASELINE_IDENTITY), stat.S_IFREG | 0o644)
    payload["RESTORE_COMMANDS.md"] = (restore_commands(args.science_commit), stat.S_IFREG | 0o644)
    identity = {
        "schema": "rei.run17.delta-archive-identity.v1",
        "repository": "cosmosapjw-quantum/rei_bianchi",
        "science_commit": args.science_commit, "science_tree": args.science_tree,
        "science_manifest_sha256": sha256(science_manifest_raw),
        "kind": "Entire frozen RUN17 source/results plus original gas executable; pinned earlier baselines are external",
        "science_files_including_manifest": len(source),
        "zip_fixed_timestamp": list(ZIP_STAMP),
        "zip_timestamp_is_execution_time": False,
        "self_reference_policy": "Archive hash, actual creation environment/argv/time and upload/download receipts are external records made after immutable archive construction.",
    }
    payload["ARCHIVE_IDENTITY.json"] = (encoded(identity), stat.S_IFREG | 0o644)
    manifest = {"schema": "rei.run17.delta-archive-manifest.v1",
                "manifest_excludes_itself": True,
                "files": [{"path": p, "bytes": len(raw), "sha256": sha256(raw), "mode": oct(mode)}
                          for p, (raw, mode) in sorted(payload.items())]}
    payload["ARCHIVE_MANIFEST.json"] = (encoded(manifest), stat.S_IFREG | 0o644)
    if len(payload) > MAX_FILES or sum(len(r) for r, _ in payload.values()) > MAX_UNCOMPRESSED_BYTES:
        raise ValueError("final delta exceeds its entry/100 MiB uncompressed cap")
    pending = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".run17-", suffix=".pending", dir=output.parent, delete=False) as stream:
            pending = Path(stream.name)
            with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
                for name, (raw, mode) in sorted(payload.items()):
                    info = zipfile.ZipInfo(name, ZIP_STAMP)
                    info.create_system = 3
                    info.external_attr = mode << 16
                    info.compress_type = zipfile.ZIP_DEFLATED
                    archive.writestr(info, raw, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
            stream.flush()
            os.fsync(stream.fileno())
        result = verify(pending)
        # Detect source edits while packaging; bytes/modes and membership must stay frozen.
        if source_payload(root)[0] != source or binary.read_bytes() != gas:
            raise ValueError("science source or gas binary changed during packaging")
        os.link(pending, output)  # Atomic create-only; never replace an existing archive.
        result["archive_file"] = str(output)
        result.update({"created_at_utc": datetime.now(timezone.utc).isoformat(),
                       "exact_command_argv": [sys.executable, *sys.argv],
                       "environment": {"python": sys.version, "platform": platform.platform(),
                                       "zlib_build": zlib.ZLIB_VERSION, "zlib_runtime": zlib.ZLIB_RUNTIME_VERSION},
                       "frozen_source_unchanged_during_packaging": True,
                       "determinism_scope": "Fixed payload/commit/tree and serialization settings within the same zlib implementation; creation date/argv/environment remain outside the archive.",
                       "archive_self_reference": False, "overwritten_files": 0})
        with receipt.open("xb") as stream:
            stream.write(encoded(result))
        print(encoded(result).decode(), end="")
    finally:
        if pending is not None:
            pending.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
