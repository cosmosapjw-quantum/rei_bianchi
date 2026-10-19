#!/usr/bin/env python3
"""Create a committed, frozen RUN18 delta ZIP; never execute scientific code."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import platform
import stat
import subprocess
import sys
import tempfile
import zipfile
import zlib

from verify_archive import (BASELINE_IDENTITY, MAX_FILES, MAX_UNCOMPRESSED_BYTES,
                            SCIENCE_GIT_PREFIX, check_hex, encoded, git_blob,
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
        if (any(p in (".git", "__pycache__") for p in Path(name).parts)
                or path.suffix == ".pyc"):
            raise ValueError("Git metadata/cache cannot enter the frozen archive")
        if path.is_dir():
            continue
        if not stat.S_ISREG(path.stat().st_mode):
            raise ValueError("nonordinary frozen science source")
        total += path.stat().st_size
        if total > MAX_UNCOMPRESSED_BYTES or len(data) >= MAX_FILES - 4:
            raise ValueError("science payload exceeds the delta cap")
        raw = path.read_bytes()
        mode = stat.S_IFREG | (0o755 if path.stat().st_mode & 0o111 else 0o644)
        data[name] = (raw, mode)
    if "SCIENCE_MANIFEST.json" not in data:
        raise ValueError("SCIENCE_MANIFEST.json is required before archive creation")
    manifest_raw = data["SCIENCE_MANIFEST.json"][0]
    rows = science_rows(json_value(manifest_raw))
    if set(data) != set(rows) | {"SCIENCE_MANIFEST.json"}:
        raise ValueError("source membership differs from the frozen science manifest")
    if data["SCIENCE_MANIFEST.json"][1] != stat.S_IFREG | 0o644:
        raise ValueError("science manifest must have ordinary nonexecutable mode")
    for name, row in rows.items():
        raw, mode = data[name]
        actual_mode = "100755" if mode & 0o111 else "100644"
        if (len(raw) != row["bytes"] or sha256(raw) != row["sha256"]
                or git_blob(raw) != row["git_blob"] or actual_mode != row["git_mode"]):
            raise ValueError("science manifest byte/Git/mode mismatch: " + name)
    return data, manifest_raw


def git_read(checkout, *arguments):
    env = os.environ.copy()
    env.update({"GIT_OPTIONAL_LOCKS": "0", "GIT_NO_LAZY_FETCH": "1",
                "GIT_TERMINAL_PROMPT": "0"})
    command = ["git", "--no-replace-objects", "-C", str(checkout), *arguments]
    process = subprocess.run(command, capture_output=True, timeout=30, env=env)
    if process.returncode:
        raise ValueError("required local Git object/read is unavailable: "
                         + process.stderr.decode("utf-8", errors="replace"))
    if len(process.stdout) > MAX_UNCOMPRESSED_BYTES:
        raise ValueError("unexpectedly large local Git output")
    return process.stdout


def committed_source_gate(checkout, commit, tree, parent, source):
    """Require the real local commit and every canonical run18 blob before ZIP."""
    for value, label in [(commit, "science commit"), (tree, "science tree"),
                         (parent, "immediate parent")]:
        check_hex(value, 40, label)
    if not checkout.is_dir():
        raise ValueError("an existing local Git checkout is required")
    raw_commit = git_read(checkout, "cat-file", "commit", commit)
    import hashlib
    actual_commit = hashlib.sha1(b"commit " + str(len(raw_commit)).encode()
                                + b"\0" + raw_commit).hexdigest()
    if actual_commit != commit:
        raise ValueError("local commit object does not hash to science commit")
    headers = raw_commit.split(b"\n\n", 1)[0].splitlines()
    trees = [line[5:].decode("ascii") for line in headers if line.startswith(b"tree ")]
    parents = [line[7:].decode("ascii") for line in headers if line.startswith(b"parent ")]
    if trees != [tree] or parents != [parent]:
        raise ValueError("science tree or explicit single-parent identity differs")
    tree_rows = git_read(checkout, "ls-tree", "-rz", "--full-tree", commit,
                         "--", SCIENCE_GIT_PREFIX).split(b"\0")
    observed = {}
    prefix = SCIENCE_GIT_PREFIX + "/"
    for row in tree_rows:
        if not row:
            continue
        header, path_raw = row.split(b"\t", 1)
        mode, kind, blob = header.decode("ascii").split()
        path = path_raw.decode("utf-8", errors="strict")
        if not path.startswith(prefix) or kind != "blob" or mode not in ("100644", "100755"):
            raise ValueError("unexpected canonical committed RUN18 tree entry")
        relative = safe_name(path[len(prefix):])
        if relative in observed:
            raise ValueError("duplicate committed RUN18 path")
        observed[relative] = (mode, blob)
    expected = {name: ("100755" if mode & 0o111 else "100644", git_blob(raw))
                for name, (raw, mode) in source.items()}
    if observed != expected:
        raise ValueError("frozen source differs from actual committed RUN18 paths/blobs/modes")
    return {"checked_local_science_commit_object": True,
            "commit_object_sha1": actual_commit, "science_tree": tree,
            "parent_commit": parent, "git_prefix": SCIENCE_GIT_PREFIX,
            "committed_files_checked": len(observed),
            "all_committed_RUN18_paths_blobs_modes_match": True,
            "automatic_fetch_command": False,
            "baseline_relation": "RUN17 science reference is recorded separately from explicit immediate parent"}


def restore_commands(science_commit):
    return ("# RUN18 delta restoration\n\n"
            "This archive contains the entire frozen RUN18 source/results, its exact-arithmetic "
            "binary, and official crate archives. It adds no separate gas binary. "
            "RUN17 is a pinned external baseline, not duplicated here.\n\n"
            "ZIP timestamps are fixed serialization metadata. Archive SHA256 and creation "
            "environment/command are external receipt fields, never archive self-references.\n\n"
            "## Obtain the frozen verifier from its actual science commit\n\n```sh\n"
            "git init /tmp/rei_run18_clean_source\n"
            "git -C /tmp/rei_run18_clean_source remote add origin https://github.com/cosmosapjw-quantum/rei_bianchi.git\n"
            "git -C /tmp/rei_run18_clean_source sparse-checkout init --cone\n"
            "git -C /tmp/rei_run18_clean_source sparse-checkout set research/atomic_nuclear_ssot_20261017/run18\n"
            f"git -C /tmp/rei_run18_clean_source fetch --depth=1 origin {science_commit}\n"
            f"git -C /tmp/rei_run18_clean_source checkout --detach {science_commit}\n"
            "```\n\n## Verify and restore to a new directory\n\n"
            "Set the following archive path and SHA from the external delivery record.\n\n```sh\n"
            "python3 -B /tmp/rei_run18_clean_source/research/atomic_nuclear_ssot_20261017/run18/packaging/verify_archive.py "
            '"$rei_run18_archive" --sha256 "$rei_run18_archive_sha256" --restore-to /tmp/rei_run18_delta_restore\n'
            "```\n\n## Reproduce only the intended exact-polynomial unit\n\n"
            "Follow run18/runtime/REPRODUCE.md with an existing Rust 1.94.1 prefix and a new "
            "writable build workspace. The official crate distributions are preserved locally. "
            "Archive verification/restoration does not compile, run tests, execute a binary, "
            "download the RUN17 archive, or integrate any physical trajectory.\n").encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run18-root", type=Path, required=True)
    parser.add_argument("--git-checkout", type=Path, required=True)
    parser.add_argument("--science-commit", required=True)
    parser.add_argument("--science-tree", required=True)
    parser.add_argument("--parent-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    if args.run18_root.is_symlink():
        raise ValueError("source root cannot be a symlink")
    root = args.run18_root.resolve()
    output = args.output.absolute()
    receipt = args.receipt.absolute() if args.receipt else output.with_suffix(output.suffix + ".receipt.json")
    if output == receipt or os.path.lexists(output) or os.path.lexists(receipt):
        raise ValueError("archive and receipt must be distinct new paths")
    if output.is_relative_to(root) or receipt.is_relative_to(root):
        raise ValueError("archive/receipt cannot be inside frozen science root")
    for path in [output, receipt]:
        if not path.parent.is_dir() or any(p.is_symlink() for p in [path.parent, *path.parent.parents]):
            raise ValueError("output parents must exist without symlink components")
    source, manifest_raw = source_payload(root)
    git_gate = committed_source_gate(args.git_checkout, args.science_commit,
                                     args.science_tree, args.parent_commit, source)
    payload = {"run18/" + name: item for name, item in source.items()}
    payload["BASELINE_IDENTITY.json"] = (encoded(BASELINE_IDENTITY), stat.S_IFREG | 0o644)
    payload["RESTORE_COMMANDS.md"] = (restore_commands(args.science_commit), stat.S_IFREG | 0o644)
    identity = {"schema": "rei.run18.delta-archive-identity.v1",
        "repository": "cosmosapjw-quantum/rei_bianchi",
        "science_commit": args.science_commit, "science_tree": args.science_tree,
        "parent_commit": args.parent_commit,
        "science_manifest_sha256": sha256(manifest_raw),
        "science_files_including_manifest": len(source),
        "git_source_checked_before_archive": True, "git_source_gate": git_gate,
        "kind": "Entire frozen RUN18 delta; runtime binary/crate archives already included; no additional gas binary",
        "zip_fixed_timestamp": list(ZIP_STAMP), "zip_timestamp_is_execution_time": False,
        "self_reference_policy": "Archive SHA, actual creation time/environment/argv and later remote backup receipts are external records."}
    payload["ARCHIVE_IDENTITY.json"] = (encoded(identity), stat.S_IFREG | 0o644)
    archive_manifest = {"schema": "rei.run18.delta-archive-manifest.v1",
        "manifest_excludes_itself": True,
        "files": [{"path": name, "bytes": len(raw), "sha256": sha256(raw), "mode": oct(mode)}
                  for name, (raw, mode) in sorted(payload.items())]}
    payload["ARCHIVE_MANIFEST.json"] = (encoded(archive_manifest), stat.S_IFREG | 0o644)
    if len(payload) > MAX_FILES or sum(len(raw) for raw, _ in payload.values()) > MAX_UNCOMPRESSED_BYTES:
        raise ValueError("delta exceeds entry or 100 MiB uncompressed cap")
    pending = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".run18-", suffix=".pending", dir=output.parent, delete=False) as stream:
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
        if source_payload(root)[0] != source:
            raise ValueError("frozen source changed during archive construction")
        os.link(pending, output)  # Atomic create-only: never replace an existing ZIP.
        result["archive_file"] = str(output)
        result.update({"created_at_utc": datetime.now(timezone.utc).isoformat(),
            "exact_command_argv": [sys.executable, *sys.argv],
            "environment": {"python": sys.version, "platform": platform.platform(),
                            "zlib_build": zlib.ZLIB_VERSION, "zlib_runtime": zlib.ZLIB_RUNTIME_VERSION},
            "git_source_gate": git_gate, "frozen_source_unchanged_during_packaging": True,
            "archive_self_reference": False, "overwritten_files": 0,
            "determinism_scope": "Fixed payload, commit identities and serialization under the same zlib implementation"})
        with receipt.open("xb") as stream:
            stream.write(encoded(result))
        print(encoded(result).decode(), end="")
    finally:
        if pending is not None:
            pending.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
