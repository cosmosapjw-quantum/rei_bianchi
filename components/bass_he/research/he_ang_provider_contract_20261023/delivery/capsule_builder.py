#!/usr/bin/env python3
"""Bookkeeping only: package saved HE-ANG bytes; no science imports or execution."""
import argparse
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import tarfile
import uuid

OPS = ("workflow.py", "stage_note.py", "prepare_final.py", "manifests.py",
       "git_payload.py", "preflight.js", "backup.js")
STAGES = [f"R{i}" for i in range(1, 11)] + [f"C{i}" for i in range(1, 11)]
SECRET = re.compile(rb"-----BEGIN (?:[A-Z ]+)?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|Bearer [A-Za-z0-9._-]{20,}")
TEXT = {".py", ".js", ".json", ".md", ".txt", ".yaml", ".yml", ".toml", ".sh", ".log"}


def info(stream):
    h, size = hashlib.sha256(), 0
    for block in iter(lambda: stream.read(1 << 20), b""):
        h.update(block)
        size += len(block)
    return {"size": size, "sha256": h.hexdigest()}


def atomic_json(path, value):
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n"); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("unit", "archive-dir", "ops-dir", "output-dir"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--label", choices=("FINAL", "RESUME"), required=True)
    p.add_argument("--publication-json", type=Path)
    a = p.parse_args()
    unit, archives, ops, output = (x.resolve() for x in (a.unit, a.archive_dir, a.ops_dir, a.output_dir))
    if output.is_relative_to(unit):
        raise ValueError("output-dir must be outside unit; own archive/job/ACK cannot enter payload")
    sources, cache = {}, {}
    def add(name, path):
        pp = PurePosixPath(name)
        if pp.is_absolute() or ".." in pp.parts or str(pp) != name or name in sources:
            raise ValueError("unsafe or duplicate tar path: " + name)
        if path.is_symlink() or not path.is_file():
            raise ValueError("payload must be a regular non-symlink file: " + str(path))
        if path.suffix.lower() in TEXT and SECRET.search(path.read_bytes()):
            raise ValueError("credential-shaped literal found; contents not printed: " + str(path))
        sources[name] = path
        with path.open("rb") as f:
            cache[name] = info(f)
    for path in sorted(unit.rglob("*")):
        rel = path.relative_to(unit)
        if any(x in ("__pycache__", ".git", ".pytest_cache") for x in rel.parts):
            continue
        if path.is_symlink():
            raise ValueError("symlink excluded from complete capsule: " + str(rel))
        if path.is_file():
            if path.name.endswith((".pyc", ".pyo", ".tmp", ".partial", "~")) or ".tmp-" in path.name:
                continue
            if path.name == ".env" or path.name.startswith(".env.") or path.name in ("id_rsa", "id_ed25519", "credentials"):
                raise ValueError("credential file cannot enter capsule: " + str(rel))
            add("unit/" + rel.as_posix(), path)
    names = set()
    for stage in STAGES:
        ack = json.loads((unit / "delivery" / (stage + "_ACK.json")).read_text())
        name = ack["archive"]
        if ack.get("stage") != stage or Path(name).name != name or name in names:
            raise ValueError("stage ACK/archive identity conflict: " + stage)
        for provider in ("dropbox", "drive"):
            record = ack[provider]
            if record.get("status") not in ("completed", "completed_metadata_verified") or not record.get("id") or record.get("bytes") != ack["bytes"]:
                raise ValueError("incomplete stage provider ACK: " + stage + "/" + provider)
        names.add(name); add("stage_archives/" + name, archives / name)
        saved = cache["stage_archives/" + name]
        if saved["size"] != ack["bytes"] or saved["sha256"] != ack["sha256"]:
            raise ValueError("stage archive SHA256/size mismatch: " + stage)
    for name in OPS:
        add("operations/" + name, ops / name)
    if a.publication_json:
        pub = a.publication_json
        if pub.resolve().is_relative_to(unit):
            raise ValueError("publication-json must be an external saved snapshot")
        json.loads(pub.read_text()); add("publication.json", pub)
    rows = [dict(path=name, **cache[name]) for name in sorted(sources)]
    manifest = {"schema": "he_ang.complete_capsule.v1", "label": a.label,
                "files": rows, "payload_files": len(rows), "stage_archives": 20,
                "operations_allowlist": list(OPS), "self_ack_included": False,
                "self_ack_policy": "Own archive hash/upload ACK is produced later and must remain external.",
                "verification_scope": "saved bytes only; no science execution or remote readback"}
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True, exist_ok=True)
    target = output / ("BASS_HE_HEANG_" + a.label + "_" + stamp + "_" + uuid.uuid4().hex[:8] + ".tar.gz")
    tmp = target.with_name(target.name + ".partial")
    with tarfile.open(tmp, "w:gz") as tf:
        for row in rows + [{"path": "MANIFEST.json", "size": len(manifest_bytes)}]:
            header = tarfile.TarInfo(row["path"]); header.size = row["size"]; header.mode = 0o644
            if row["path"] == "MANIFEST.json":
                tf.addfile(header, io.BytesIO(manifest_bytes))
            else:
                if sources[row["path"]].stat().st_mode & 0o111: header.mode = 0o755
                with sources[row["path"]].open("rb") as f: tf.addfile(header, f)
    with tmp.open("rb") as f: os.fsync(f.fileno())
    with tarfile.open(tmp, "r:gz") as tf:
        expected = {r["path"] for r in rows} | {"MANIFEST.json"}
        if len(tf.getmembers()) != len(expected) or set(tf.getnames()) != expected:
            raise ValueError("created capsule member inventory mismatch")
        if tf.extractfile("MANIFEST.json").read() != manifest_bytes:
            raise ValueError("created capsule MANIFEST mismatch")
        for row in rows:
            if info(tf.extractfile(row["path"])) != cache[row["path"]]:
                raise ValueError("created capsule payload mismatch: " + row["path"])
    os.replace(tmp, target)
    with target.open("rb") as f: outer = info(f)
    job = {"status": "LOCAL_CAPSULE_VERIFIED", "local_path": str(target), "archive": target.name,
           "sha256": outer["sha256"], "bytes": outer["size"], "payload_files": len(rows),
           "unit_files": sum(r["path"].startswith("unit/") for r in rows), "stage_archive_files": 20,
           "operation_files": len(OPS), "publication_snapshot": bool(a.publication_json),
           "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(), "verified_payload_files": len(rows),
           "scientific_executions": 0, "network_operations": 0, "own_provider_ack": "EXTERNAL_PENDING"}
    atomic_json(target.with_suffix(target.suffix + ".job.json"), job)
    print(json.dumps(job, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
