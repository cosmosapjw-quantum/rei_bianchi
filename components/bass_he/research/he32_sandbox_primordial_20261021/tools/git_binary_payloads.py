#!/usr/bin/env python3
"""Prepare/record Git blob publication without credentials or network access.

The connector caller supplies the returned blob SHA. This helper never creates
commits or refs. Chunk payloads are transport data, not report content.
"""
from __future__ import annotations

import argparse
import base64
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile
import sys
from datetime import datetime, timezone

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
DELIVERY = UNIT / "delivery"
INVENTORY = DELIVERY / "BINARY_PUBLICATION_INVENTORY.json"
MANIFEST = DELIVERY / "FINAL_BINARY_BLOBS.json"
REPOSITORY = "cosmosapjw-quantum/BASS_HE"


def utc():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        Path(name).unlink(missing_ok=True)


def safe_file(relative):
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError("repository-relative path required")
    path = REPO / rel
    if path.is_symlink() or UNIT not in path.resolve().parents:
        raise ValueError("regular HE32 unit file required")
    if path.suffix not in {".npz", ".png"}:
        raise ValueError("only NPZ and PNG payloads are accepted")
    return path


def describe(path):
    data = path.read_bytes()
    return dict(path=path.relative_to(REPO).as_posix(), mode="100644", type="blob",
                size=len(data), sha=hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest(),
                sha256=hashlib.sha256(data).hexdigest())


def inventory(partial=False, limit=12):
    if not partial:
        catalog = json.loads((UNIT / "results/CATALOG.json").read_text())
        if catalog.get("count") != 392 or len(catalog["cases"]) != 392:
            raise ValueError("complete 392-case catalog required")
    sys.path.insert(0, str(UNIT / "src"))
    import coupled_pilot as science
    rows = []
    for path in sorted((UNIT / "results/cases").glob("*.npz")):
        if partial and not path.with_suffix(".json").exists():
            continue
        receipt = json.loads(path.with_suffix(".json").read_text())
        if partial and receipt.get("status") != "completed":
            continue
        row = describe(path)
        if (receipt.get("status") != "completed" or len(receipt.get("checks", {})) != 9
                or any(v is not True for v in receipt["checks"].values())
                or receipt.get("npz_sha256") != row["sha256"]):
            raise ValueError("incomplete or unmatched trajectory: " + path.name)
        if not science.completed_result(receipt["config"], path.with_suffix(".json")):
            raise ValueError("science completed_result rejected: " + path.name)
        row.update(case_identity=receipt["identity"], source="completed_science_receipt")
        rows.append(row)
    if not partial and len(rows) != 394:
        raise ValueError("392 nominal plus 2 guard trajectories required")
    figures = UNIT / "results/figures"
    figure_manifest = figures / "FIGURE_MANIFEST.json"
    manifest = json.loads(figure_manifest.read_text()) if figure_manifest.exists() else {}
    if not partial and (manifest.get("status") != "completed" or len(manifest["figures"]) != 6):
        raise ValueError("six completed figures required")
    for figure in manifest.get("figures", []) if manifest.get("status") == "completed" else []:
        for item in figure["files"]:
            if Path(item["path"]).suffix == ".png":
                row = describe(figures / item["path"])
                if row["sha256"] != item["sha256"]:
                    raise ValueError("figure hash mismatch")
                row.update(source="completed_figure_manifest")
                rows.append(row)
    if not partial and len(rows) != 400:
        raise ValueError("400 total binary payloads required")
    result = dict(schema="he32.git_binary_inventory.v1", repository=REPOSITORY,
                  created_utc=utc(), count=len(rows), bytes=sum(r["size"] for r in rows),
                  status="partial" if partial else "complete", files=rows)
    if INVENTORY.exists():
        prior = json.loads(INVENTORY.read_text())
        current = {r["path"]: r for r in result["files"]}
        if any(current.get(r["path"]) != r for r in prior["files"]):
            raise ValueError("previously inventoried binary changed or disappeared")
        result["created_utc"] = prior["created_utc"]
    atomic_json(INVENTORY, result)
    uploaded = {r["path"] for r in json.loads(MANIFEST.read_text())["files"]} if MANIFEST.exists() else set()
    pending = [r for r in rows if r["path"] not in uploaded]
    print(json.dumps(dict(count=len(rows), bytes=result["bytes"], uploaded=len(uploaded),
                         pending_count=len(pending), pending=pending[:limit])))


def chunk(relative, offset, length):
    if offset < 0 or offset % 3 or length <= 0 or length > 60000 or length % 3:
        raise ValueError("aligned chunks, at most 60000 bytes, required")
    path = safe_file(relative)
    with path.open("rb") as stream:
        stream.seek(offset)
        data = stream.read(length)
    print(json.dumps(dict(path=relative, offset=offset, bytes=len(data),
                         base64=base64.b64encode(data).decode())))


def record(value):
    item = json.loads(value)
    expected = {r["path"]: r for r in json.loads(INVENTORY.read_text())["files"]}[item["path"]]
    if item["returned_sha"] != expected["sha"]:
        raise ValueError("GitHub blob SHA does not match local Git object SHA")
    if describe(safe_file(item["path"])) != {k: expected[k] for k in ("path", "mode", "type", "size", "sha", "sha256")}:
        raise ValueError("immutable local binary changed during upload")
    DELIVERY.mkdir(parents=True, exist_ok=True)
    with (DELIVERY / ".binary_publication.lock").open("a+b") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        result = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else dict(
            schema="he32.git_binary_blobs.v1", repository=REPOSITORY, files=[])
        rows = {r["path"]: r for r in result["files"]}
        if item["path"] in rows:
            if rows[item["path"]]["sha"] != item["returned_sha"]:
                raise ValueError("existing publication receipt differs")
        else:
            rows[item["path"]] = dict(expected, returned_sha=item["returned_sha"],
                verified=True, uploaded_utc=utc(), publication="Git object created; branch publication by parent remains separate")
        result.update(files=[rows[k] for k in sorted(rows)], count=len(rows),
                      bytes=sum(r["size"] for r in rows.values()), updated_utc=utc())
        atomic_json(MANIFEST, result)
    print(json.dumps(dict(count=result["count"], path=item["path"], sha=item["returned_sha"], verified=True)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("inventory")
    p.add_argument("--partial", action="store_true")
    p.add_argument("--limit", type=int, default=12)
    p = sub.add_parser("chunk")
    p.add_argument("path")
    p.add_argument("offset", type=int)
    p.add_argument("length", type=int, nargs="?", default=60000)
    p = sub.add_parser("record")
    p.add_argument("json")
    args = parser.parse_args()
    if args.action == "inventory": inventory(args.partial, args.limit)
    elif args.action == "chunk": chunk(args.path, args.offset, args.length)
    elif args.action == "record": record(args.json)


if __name__ == "__main__":
    main()
