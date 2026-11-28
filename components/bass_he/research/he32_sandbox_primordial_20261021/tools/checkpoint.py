#!/usr/bin/env python3
"""Create an immutable, content-bound HE32 stage snapshot using the stdlib.

Examples (from the unit directory)::

    python tools/checkpoint.py --stage O.C1 --status COMPLETE_SCOPED
    python tools/checkpoint.py --stage F.C10 --include . --include-large \
        --label final --publication-state PENDING

Default snapshots contain public source/configuration/tests/input/evidence and
top-level documents. Results and plots are opt-in. Files larger than 2 MiB are
hashed but represented by references unless --include-large is specified. A
reference is not a restorable payload; the receipt distinguishes these counts.
Archive bytes never contain their own digest or a predicted provider receipt.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import sys
import tarfile
import tempfile
import time


STAGES = tuple(
    [f"O.C{i}" for i in range(1, 11)]
    + [f"P.R{i}" for i in range(1, 11)]
    + [f"F.C{i}" for i in range(1, 11)]
)
DEFAULT_DIRS = ("src", "configs", "data", "tests", "tools", "vendor", "inputs", "evidence")
TOP_SUFFIXES = {".md", ".json", ".toml", ".txt", ".sh", ".py", ".yaml", ".yml"}
EXCLUDED_PARTS = {
    ".git", ".ssh", ".aws", ".codex", ".agents", ".venv", "venv",
    "__pycache__", ".pytest_cache", ".mypy_cache", "node_modules",
    "checkpoints", "delivery", "target", "build", ".cache",
}
PRIVATE_NAME = re.compile(r"(?:^|[_.-])(?:private|credentials|secrets?|tokens?|keys?)(?:$|[_.-])", re.I)
ARCHIVE_ENDINGS = (".tar", ".tar.gz", ".tgz", ".tar.xz", ".tar.zst", ".zip", ".pyc", ".pyo")
SENSITIVE_TEXT = re.compile(
    rb"(?:-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    rb"[\"'](?:download_url|access_token|refresh_token|authorization|api_key|secret_access_key|private_key)[\"']\s*:)" , re.I
)


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def ignored(relative: Path) -> str | None:
    for part in relative.parts:
        if part in EXCLUDED_PARTS or part.startswith("."):
            return "excluded_directory_or_hidden_path"
        if PRIVATE_NAME.search(part):
            return "private_or_credential_filename"
    if relative.name.lower().endswith(ARCHIVE_ENDINGS):
        return "archive_or_bytecode_not_recursively_embedded"
    return None


def selected_files(unit: Path, requested: list[str], output: Path) -> tuple[list[Path], dict[str, int]]:
    """Walk only selected roots and never follow symlinks outside the unit."""
    roots = [unit / x for x in DEFAULT_DIRS if (unit / x).is_dir()]
    roots += [x for x in unit.iterdir() if x.is_file() and x.suffix.lower() in TOP_SUFFIXES]
    if requested:
        roots = []
        for value in requested:
            rel = Path(value)
            if rel.is_absolute() or ".." in rel.parts:
                raise ValueError(f"--include must be a unit-relative path: {value!r}")
            candidate = unit / rel
            if not candidate.exists():
                raise FileNotFoundError(f"selected input does not exist: {value}")
            roots.append(candidate)
    found: set[Path] = set()
    counts: dict[str, int] = {}

    def reject(reason: str) -> None:
        counts[reason] = counts.get(reason, 0) + 1

    def visit(path: Path) -> None:
        if path == output or output in path.parents:
            reject("checkpoint_output_directory")
            return
        relative = path.relative_to(unit)
        reason = ignored(relative)
        if reason:
            reject(reason)
            return
        if path.is_symlink():
            reject("symlink_not_followed")
            return
        if path.is_dir():
            for child in sorted(path.iterdir()):
                visit(child)
        elif path.is_file():
            found.add(path)
        else:
            reject("non_regular_file")

    for root in roots:
        visit(root)
    return sorted(found, key=lambda x: x.relative_to(unit).as_posix()), counts


def stable_copy(source: Path, destination: Path | None) -> tuple[int, str, int, bool]:
    """Hash the exact frozen bytes, rejecting a concurrent source modification."""
    h = hashlib.sha256()
    size = 0
    sensitive = False
    tail = b""
    if destination:
        destination.parent.mkdir(parents=True, exist_ok=True)
    output = destination.open("xb") if destination else None
    try:
        with source.open("rb") as f:
            before = os.fstat(f.fileno())
            if not stat.S_ISREG(before.st_mode):
                raise ValueError("selected source is no longer a regular file")
            for block in iter(lambda: f.read(1024 * 1024), b""):
                h.update(block)
                size += len(block)
                if output:
                    output.write(block)
                # Catch private-key material and obvious credential JSON fields.
                # Filename allowlists remain the primary selection boundary.
                sensitive |= SENSITIVE_TEXT.search(tail + block) is not None
                tail = block[-256:]
            after = os.fstat(f.fileno())
        identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if identity(before) != identity(after) or size != before.st_size:
            raise RuntimeError(f"source changed while snapshotting: {source.name}; retry with a new label")
        if output:
            output.flush()
            os.fsync(output.fileno())
        return size, h.hexdigest(), 0o755 if before.st_mode & 0o111 else 0o644, sensitive
    finally:
        if output:
            output.close()


def atomic_new(path: Path, data: bytes) -> None:
    """Publish a fully fsynced file with an exclusive hard-link operation."""
    fd, temporary = tempfile.mkstemp(prefix=".checkpoint-", dir=path.parent)
    tmp = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.link(tmp, path)  # fails instead of replacing an existing path
        fsync_dir(path.parent)
    finally:
        tmp.unlink(missing_ok=True)


def fsync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def add_bytes(archive: tarfile.TarFile, name: str, data: bytes, mode: int = 0o644) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mode = mode
    info.mtime = 0
    archive.addfile(info, io.BytesIO(data))


def checkpoint(args: argparse.Namespace) -> dict:
    started = time.monotonic()
    unit = args.unit.resolve(strict=True)
    if not unit.is_dir():
        raise ValueError("unit must be a directory")
    output = (args.output or unit / "checkpoints").resolve()
    output.mkdir(parents=True, exist_ok=True)
    stem = args.stage.replace(".", "-") + ("_" + args.label if args.label else "")
    target = output / (stem + ".tar.gz")
    receipt_path = output / (stem + ".receipt.json")
    manifest_path = output / (stem + ".manifest.json")
    for path in (target, receipt_path, manifest_path):
        if path.exists():
            raise FileExistsError(f"checkpoint already exists: {path}; choose a new --label")
    # Exclusive reservation prevents two writers publishing one stage identity.
    reservation = output / ("." + stem + ".reservation")
    rfd = os.open(reservation, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(rfd, "w") as f:
        f.write(f"pid={os.getpid()}\n")
        f.flush()
        os.fsync(f.fileno())
    try:
        paths, excluded = selected_files(unit, args.include, output)
        if not paths:
            raise ValueError("snapshot selection contains no public regular files")
        with tempfile.TemporaryDirectory(prefix=".snapshot-", dir=output) as tempdir:
            temp = Path(tempdir)
            records = []
            for source in paths:
                rel = source.relative_to(unit).as_posix()
                include = args.include_large or source.stat().st_size <= args.max_inline_bytes
                dest = temp / "payload" / rel if include else None
                size, digest, mode, sensitive = stable_copy(source, dest)
                if sensitive:
                    if dest:
                        dest.unlink()
                    excluded["sensitive_content_key_or_field"] = excluded.get("sensitive_content_key_or_field", 0) + 1
                    continue
                records.append({"path": rel, "bytes": size, "sha256": digest, "mode": oct(mode),
                                "included": include, "storage": "archive_payload" if include else "hash_reference_only"})
            if not any(x["included"] for x in records):
                raise ValueError("snapshot contains no included payload after exclusions")
            position = STAGES.index(args.stage)
            manifest = {
                "schema": "he32.stage.snapshot.manifest.v1", "stage": args.stage,
                "stage_status_provided": args.status, "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "unit": unit.name, "next_dag_stage": STAGES[position + 1] if position + 1 < len(STAGES) else None,
                "selection": args.include or {"directories": list(DEFAULT_DIRS), "top_level_document_suffixes": sorted(TOP_SUFFIXES)},
                "max_inline_bytes": args.max_inline_bytes, "include_large": args.include_large,
                "excluded_counts": excluded, "files": records,
                "interpretation": "Stage evidence snapshot; supplied status is recorded, not scientifically certified by this tool. Hash-only references require their original payload for restoration.",
            }
            manifest_data = json_bytes(manifest)
            packed = temp / "snapshot.tar.gz"
            with packed.open("xb") as raw:
                with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as gz:
                    with tarfile.open(fileobj=gz, mode="w") as archive:
                        add_bytes(archive, "SNAPSHOT_MANIFEST.json", manifest_data)
                        for item in records:
                            if not item["included"]:
                                continue
                            info = tarfile.TarInfo("payload/" + item["path"])
                            info.size, info.mode, info.mtime = item["bytes"], int(item["mode"], 8), 0
                            with (temp / "payload" / item["path"]).open("rb") as f:
                                archive.addfile(info, f)
                raw.flush()
                os.fsync(raw.fileno())
            # Verify packaging against frozen bytes, not changing working files.
            with tarfile.open(packed, "r:gz") as archive:
                if archive.extractfile("SNAPSHOT_MANIFEST.json").read() != manifest_data:
                    raise RuntimeError("manifest readback mismatch")
                for item in records:
                    if item["included"]:
                        f = archive.extractfile("payload/" + item["path"])
                        h = hashlib.sha256()
                        for block in iter(lambda: f.read(1024 * 1024), b""):
                            h.update(block)
                        if h.hexdigest() != item["sha256"]:
                            raise RuntimeError("archive member hash mismatch: " + item["path"])
            receipt = {
                "schema": "he32.stage.snapshot.receipt.v1", "stage": args.stage,
                "status": "LOCAL_SNAPSHOT_READBACK_COMPLETE", "archive": target.name,
                "archive_bytes": packed.stat().st_size, "archive_sha256": sha256_file(packed),
                "manifest": manifest_path.name, "manifest_sha256": hashlib.sha256(manifest_data).hexdigest(),
                "payload_files": sum(x["included"] for x in records),
                "hash_only_references": sum(not x["included"] for x in records),
                "payload_bytes": sum(x["bytes"] for x in records if x["included"]),
                "publication_state_provided": args.publication_state,
                "publication_ref_provided_not_verified": args.publication_ref,
                "remote_backup_status": "NOT_UPLOADED_BY_THIS_TOOL", "next_dag_stage": manifest["next_dag_stage"],
                "wall_seconds": time.monotonic() - started,
                "restore_scope": "All included payload members verified against manifest; hash-only references are not embedded.",
            }
            os.link(packed, target)
            fsync_dir(output)
            atomic_new(manifest_path, manifest_data)
            atomic_new(receipt_path, json_bytes(receipt))
            return receipt
    finally:
        reservation.unlink(missing_ok=True)
        fsync_dir(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--stage", required=True, choices=STAGES)
    parser.add_argument("--unit", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, help="local create-only snapshot directory (default: UNIT/checkpoints)")
    parser.add_argument("--include", action="append", default=[], metavar="RELATIVE_PATH", help="replace default selection; repeat to choose public inputs/results/plots")
    parser.add_argument("--include-large", action="store_true", help="embed selected large files instead of their hash references")
    parser.add_argument("--max-inline-bytes", type=int, default=2 * 1024 * 1024)
    parser.add_argument("--label", default="", help="unique retry/checkpoint label; old checkpoints are preserved")
    parser.add_argument("--status", default="CHECKPOINT_ONLY", help="DAG status supplied by the controller")
    parser.add_argument("--publication-state", default="NOT_PUBLISHED")
    parser.add_argument("--publication-ref", default=None, help="optional already observed ref; this local tool does not verify a remote ref")
    args = parser.parse_args()
    if args.max_inline_bytes < 0 or not re.fullmatch(r"[A-Za-z0-9_-]*", args.label):
        parser.error("max-inline-bytes must be nonnegative and label must contain only letters, digits, underscore or hyphen")
    try:
        receipt = checkpoint(args)
    except (OSError, ValueError, RuntimeError, tarfile.TarError) as error:
        print(f"checkpoint: {error}", file=sys.stderr)
        return 2
    print(json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
