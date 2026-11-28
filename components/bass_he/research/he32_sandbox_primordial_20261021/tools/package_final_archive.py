#!/usr/bin/env python3
"""Freeze the complete public HE32 unit into a verified, immutable archive.

Run only after the coordinating task declares FINAL_FREEZE. This program does
not execute physics, modify Git, or upload anything. Cloud ACKs are later
sidecars; the archive never claims its own upload has completed.
"""
from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile

from checkpoint import (
    PRIVATE_NAME, STAGES, add_bytes, atomic_new, fsync_dir, json_bytes,
    sha256_file, stable_copy,
)


SKIP_PARTS = {"__pycache__", "node_modules", "venv", "build", "target"}
ARCHIVE_ENDINGS = (".tar", ".tar.gz", ".tgz", ".zip", ".tar.xz", ".tar.zst")
TEXT_SUFFIXES = {".json", ".md", ".txt", ".csv", ".tsv", ".py", ".sh", ".toml", ".yaml", ".yml"}
TEMPORARY_URL = re.compile(
    rb"https?://[^\s\"'<>]*(?:dl\.dropboxusercontent\.com|"
    rb"files\.oaiusercontent\.com|[?&](?:X-Amz-Signature|access_token)=)", re.I
)


def public_files(unit: Path) -> tuple[list[Path], dict[str, int]]:
    selected: list[Path] = []
    omitted: Counter[str] = Counter()

    def visit(path: Path) -> None:
        rel = path.relative_to(unit)
        if any(p.startswith(".") or p in SKIP_PARTS for p in rel.parts):
            omitted["hidden_or_cache_path"] += 1
            return
        if any(PRIVATE_NAME.search(p) for p in rel.parts):
            omitted["private_or_credential_filename"] += 1
            return
        if path.is_symlink():
            raise ValueError(f"symlink is outside the public packaging contract: {rel}")
        if path.is_dir():
            for child in sorted(path.iterdir()):
                visit(child)
            return
        if not path.is_file():
            raise ValueError(f"non-regular path cannot be packaged: {rel}")
        if path.suffix.lower() in {".pyc", ".pyo", ".tmp", ".partial"}:
            omitted["bytecode_or_temporary_file"] += 1
            return
        if path.name.lower().endswith(ARCHIVE_ENDINGS):
            if rel.parent != Path("checkpoints") or not path.name.endswith(".tar.gz"):
                omitted["nested_phase_or_delivery_archive"] += 1
                return
        selected.append(path)

    for child in sorted(unit.iterdir()):
        visit(child)
    return sorted(selected), dict(omitted)


def verify_stages(unit: Path, paths: list[Path]) -> list[dict]:
    archives = [p for p in paths if p.parent == unit / "checkpoints" and p.name.endswith(".tar.gz")]
    records: list[dict] = []
    seen: set[str] = set()
    for archive in archives:
        stem = archive.name.removesuffix(".tar.gz")
        receipt_path = archive.with_name(stem + ".receipt.json")
        receipt = json.loads(receipt_path.read_text())
        stage = receipt["stage"]
        if stage in seen:
            raise ValueError(f"duplicate stage archive: {stage}")
        seen.add(stage)
        if receipt["archive"] != archive.name or receipt["archive_bytes"] != archive.stat().st_size:
            raise ValueError(f"stage archive identity mismatch: {stage}")
        digest = sha256_file(archive)
        if digest != receipt["archive_sha256"]:
            raise ValueError(f"stage archive digest mismatch: {stage}")
        manifest = archive.with_name(receipt["manifest"])
        if sha256_file(manifest) != receipt["manifest_sha256"]:
            raise ValueError(f"stage manifest digest mismatch: {stage}")
        records.append({"stage": stage, "archive": str(archive.relative_to(unit)),
                        "bytes": archive.stat().st_size, "sha256": digest,
                        "receipt_sha256": sha256_file(receipt_path),
                        "manifest_sha256": receipt["manifest_sha256"]})
    if seen != set(STAGES):
        raise ValueError(f"expected all 30 unique stages; missing={sorted(set(STAGES)-seen)}, extra={sorted(seen-set(STAGES))}")
    return sorted(records, key=lambda r: STAGES.index(r["stage"]))


def dropbox_content_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(4 * 1024 * 1024), b""):
            h.update(hashlib.sha256(block).digest())
    return h.hexdigest()


def package(args: argparse.Namespace) -> dict:
    if args.freeze != "FINAL_FREEZE":
        raise ValueError("explicit --freeze FINAL_FREEZE is required")
    unit = args.unit.resolve(strict=True)
    repo = unit.parents[1]
    unit_relative = unit.relative_to(repo)
    output = args.output.resolve()
    if output == unit or unit in output.parents:
        raise ValueError("archive output must be outside the source unit")
    output.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = "BASS_HE_HE32_FINAL_SANDBOX_PILOT_" + stamp
    target = output / (stem + ".tar.gz")
    partial = output / (stem + ".tar.gz.partial")
    if target.exists() or partial.exists():
        raise FileExistsError("unique final archive name already exists")
    selected, omitted = public_files(unit)
    stages = verify_stages(unit, selected)
    npz = [p for p in selected if p.suffix == ".npz" and unit / "results" in p.parents]
    figure_paths = [p for p in selected if p.parent == unit / "results" / "figures" and p.suffix in {".png", ".svg"}]
    figure_stems = {p.stem for p in figure_paths}
    if len(npz) != args.expected_result_npz:
        raise ValueError(f"expected {args.expected_result_npz} result NPZ files, found {len(npz)}")
    if len(figure_stems) != args.expected_figure_pairs or any(
        {p.suffix for p in figure_paths if p.stem == stem} != {".png", ".svg"}
        for stem in figure_stems
    ):
        raise ValueError("expected six figures, each in PNG and SVG")
    head = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    print(json.dumps({"state": "FREEZING", "payload_files": len(selected),
                      "stage_archives": len(stages), "result_npz": len(npz),
                      "figure_pairs": len(figure_stems), "git_head": head}), flush=True)
    entries: list[dict] = []
    try:
        with tempfile.TemporaryDirectory(prefix="he32-final-", dir=output) as staging:
            staging_path = Path(staging)
            for source in selected:
                rel = source.relative_to(unit)
                frozen = staging_path / rel
                size, digest, mode, sensitive = stable_copy(source, frozen)
                if sensitive:
                    raise ValueError(f"credential-like text in public file: {rel}")
                if source.suffix.lower() in TEXT_SUFFIXES and TEMPORARY_URL.search(frozen.read_bytes()):
                    raise ValueError(f"temporary private URL in public file: {rel}")
                entries.append({"path": (unit_relative / rel).as_posix(), "bytes": size,
                                "sha256": digest, "mode": oct(mode),
                                "role": "stage_archive" if source in [unit / s["archive"] for s in stages]
                                else "public_unit_payload"})
            manifest = {
                "schema": "he32.final.full.archive_manifest.v1",
                "created_utc": stamp, "freeze_authorization": "FINAL_FREEZE",
                "git_head_at_freeze": head, "unit": unit_relative.as_posix(),
                "scope": "Complete public unit, including source, input data, tests, evidence, documentation, all final case JSON/NPZ, six PNG/SVG figures, and all 30 unique stage snapshots. P1/P2 outer archives, hidden attempt directories, caches, credentials, and temporary URLs excluded. Cloud completion ACKs follow separately.",
                "payload_files": len(entries), "payload_bytes": sum(e["bytes"] for e in entries),
                "maximum_payload_file": max(entries, key=lambda e: e["bytes"]),
                "result_npz_files": len(npz), "figure_pairs": len(figure_stems),
                "stage_archives": stages, "omitted_reason_counts": omitted,
                "source_files": [e for e in entries if Path(e["path"]).relative_to(unit_relative).parts[0] == "src"],
                "files": entries,
            }
            manifest_bytes = json_bytes(manifest)
            with partial.open("xb") as raw:
                with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=6) as zipped:
                    with tarfile.open(fileobj=zipped, mode="w", format=tarfile.PAX_FORMAT) as archive:
                        for entry in entries:
                            relative = Path(entry["path"]).relative_to(unit_relative)
                            add_bytes(archive, entry["path"], (staging_path / relative).read_bytes(), int(entry["mode"], 8))
                        add_bytes(archive, "ARCHIVE_MANIFEST.json", manifest_bytes)
                raw.flush()
                os.fsync(raw.fileno())
            if public_files(unit)[0] != selected:
                raise RuntimeError("source file inventory changed during freeze")
            for source, entry in zip(selected, entries):
                if sha256_file(source) != entry["sha256"]:
                    raise RuntimeError(f"source changed during freeze: {source.relative_to(unit)}")
            with tarfile.open(partial, "r:gz") as archive:
                members = archive.getmembers()
                expected = {e["path"]: e for e in entries}
                if len(members) != len(expected) + 1 or {m.name for m in members} != set(expected) | {"ARCHIVE_MANIFEST.json"}:
                    raise RuntimeError("archive member inventory mismatch")
                for member in members:
                    if not member.isfile():
                        raise RuntimeError("archive contains a non-regular member")
                    data = archive.extractfile(member).read()
                    if member.name == "ARCHIVE_MANIFEST.json":
                        if data != manifest_bytes:
                            raise RuntimeError("archive manifest readback mismatch")
                    else:
                        entry = expected[member.name]
                        if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
                            raise RuntimeError(f"archive payload readback mismatch: {member.name}")
            receipt = {
                "schema": "he32.final.full.archive_receipt.v1",
                "status": "LOCAL_FULL_ARCHIVE_READBACK_COMPLETE",
                "archive": target.name, "bytes": partial.stat().st_size,
                "sha256": sha256_file(partial), "dropbox_content_hash": dropbox_content_hash(partial),
                "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                "payload_files": len(entries), "payload_bytes": manifest["payload_bytes"],
                "maximum_payload_file": manifest["maximum_payload_file"],
                "stage_archives": len(stages), "result_npz_files": len(npz),
                "figure_pairs": len(figure_stems), "git_head_at_freeze": head,
                "source_inventory_stable": True, "all_payload_hashes_readback_verified": True,
                "cloud_upload_status": "NOT_UPLOADED_BY_THIS_SCRIPT", "scientific_ivp_runs": 0,
            }
            os.link(partial, target)
            fsync_dir(output)
            atomic_new(output / (stem + ".manifest.json"), manifest_bytes)
            atomic_new(output / (stem + ".receipt.json"), json_bytes(receipt))
            print(json.dumps(receipt, sort_keys=True), flush=True)
            return receipt
    finally:
        partial.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--freeze", required=True, choices=["FINAL_FREEZE"])
    parser.add_argument("--expected-result-npz", type=int, default=394)
    parser.add_argument("--expected-figure-pairs", type=int, default=6)
    package(parser.parse_args())


if __name__ == "__main__":
    main()
