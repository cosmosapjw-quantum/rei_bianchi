"""Durable orchestration primitives for long-running H-H numerical jobs.

This module intentionally contains no scientific kernels.  It controls leases,
CPU-quota-aware worker counts, crash recovery of completed pair checkpoints,
and small create-only delta archives.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import math
import os
import re
import socket
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np

_PAIR_RE = re.compile(r"^pair_(\d{2})_(\d{2})\.npz$")
_AUTO = object()


def sha256_file(path: Path | str) -> str:
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def cpu_quota_cores_from_text(text: str) -> int | None:
    fields = text.strip().split()
    if len(fields) < 2 or fields[0] == "max":
        return None
    quota = int(fields[0])
    period = int(fields[1])
    if quota <= 0 or period <= 0:
        return None
    return max(1, math.floor(quota / period))


def detect_cpu_quota_cores(path: Path | str = "/sys/fs/cgroup/cpu.max") -> int | None:
    try:
        return cpu_quota_cores_from_text(Path(path).read_text())
    except (OSError, ValueError):
        return None


def detect_affinity_count() -> int | None:
    try:
        return len(os.sched_getaffinity(0))
    except (AttributeError, OSError):
        return None


def choose_worker_count(
    requested: int | None,
    *,
    cpu_count: int | None = None,
    affinity_count: int | None | object = _AUTO,
    quota_cores: int | None | object = _AUTO,
    hard_cap: int = 64,
) -> int:
    cpu_count = cpu_count if cpu_count is not None else (os.cpu_count() or 1)
    if affinity_count is _AUTO:
        affinity_count = detect_affinity_count()
    if quota_cores is _AUTO:
        quota_cores = detect_cpu_quota_cores()
    limits = [max(1, int(cpu_count)), max(1, int(hard_cap))]
    if affinity_count is not None:
        limits.append(max(1, int(affinity_count)))
    if quota_cores is not None:
        limits.append(max(1, int(quota_cores)))
    available = min(limits)
    if requested is None or requested <= 0:
        return available
    return max(1, min(int(requested), available))


class LeaseBusyError(RuntimeError):
    pass


@dataclass
class RunLease:
    lock_path: Path | str
    state_path: Path | str
    metadata: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        self.lock_path = Path(self.lock_path)
        self.state_path = Path(self.state_path)
        self._fh = None

    def _write_state(self, status: str, **extra: object) -> None:
        data = {
            "status": status,
            "pid": os.getpid(),
            "pgid": os.getpgid(0) if hasattr(os, "getpgid") else None,
            "hostname": socket.gethostname(),
            "timestamp_unix": time.time(),
            **dict(self.metadata or {}),
            **extra,
        }
        tmp = self.state_path.with_suffix(self.state_path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        os.replace(tmp, self.state_path)

    def __enter__(self) -> "RunLease":
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = self.lock_path.open("a+")
        try:
            fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            self._fh.close()
            self._fh = None
            raise LeaseBusyError(f"active run already holds lease: {self.lock_path}") from exc
        self._write_state("ACTIVE", started_unix=time.time(), heartbeat_unix=time.time())
        return self

    def heartbeat(self, **extra: object) -> None:
        if self._fh is None:
            raise RuntimeError("lease is not active")
        self._write_state("ACTIVE", heartbeat_unix=time.time(), **extra)

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._fh is None:
            return
        self._write_state(
            "RELEASED" if exc_type is None else "FAILED",
            released_unix=time.time(),
            error=None if exc is None else repr(exc),
        )
        fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
        self._fh.close()
        self._fh = None


def should_checkpoint(
    completed_since_delta: int,
    elapsed_seconds: float,
    *,
    pair_interval: int = 8,
    seconds_interval: float = 180.0,
) -> bool:
    return completed_since_delta >= pair_interval or elapsed_seconds >= seconds_interval


def should_handoff_local(estimated_cpu_seconds: float, *, threshold_seconds: float = 600.0) -> bool:
    return float(estimated_cpu_seconds) > float(threshold_seconds)


def _event_rows(events_path: Path) -> list[dict]:
    if not events_path.exists():
        return []
    rows = []
    for line in events_path.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def recover_orphan_pairs(folder: Path | str, events_path: Path | str) -> list[dict]:
    folder = Path(folder)
    events_path = Path(events_path)
    rows = _event_rows(events_path)
    committed = {(int(r["ia"]), int(r["ib"])) for r in rows if "ia" in r and "ib" in r}
    recovered: list[dict] = []
    for p in sorted(folder.glob("pair_??_??.npz")):
        m = _PAIR_RE.match(p.name)
        if not m:
            continue
        ia_name, ib_name = map(int, m.groups())
        key = (ia_name, ib_name)
        if key in committed:
            continue
        try:
            with np.load(p, allow_pickle=False) as z:
                ia = int(np.asarray(z["ia"]).item())
                ib = int(np.asarray(z["ib"]).item())
        except Exception as exc:
            raise RuntimeError(f"cannot validate orphan pair checkpoint: {p}") from exc
        if (ia, ib) != key:
            raise RuntimeError(
                f"pair identity mismatch for {p}: filename={key}, payload={(ia, ib)}"
            )
        row = {
            "ia": ia,
            "ib": ib,
            "path": p.name,
            "sha256": sha256_file(p),
            "recovered_uncommitted_pair": True,
            "recovered_unix": time.time(),
        }
        with events_path.open("a") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        committed.add(key)
        recovered.append(row)
    return recovered


def _zip_write_bytes(zf: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name)
    info.date_time = (1980, 1, 1, 0, 0, 0)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    zf.writestr(info, data)


def create_delta_archive(
    *,
    folder: Path | str,
    committed_rows: Sequence[Mapping[str, object]],
    delta_dir: Path | str,
    sequence: int,
    parent_checkpoint_sha256: str | None,
) -> Path:
    folder = Path(folder)
    delta_dir = Path(delta_dir)
    delta_dir.mkdir(parents=True, exist_ok=True)
    identity = folder / "IDENTITY.json"
    if not identity.exists():
        raise RuntimeError(f"missing identity file: {identity}")
    rows = [dict(r) for r in committed_rows]
    if not rows:
        raise ValueError("delta archive requires at least one committed pair")
    pair_paths: list[Path] = []
    for row in rows:
        ia, ib = int(row["ia"]), int(row["ib"])
        p = folder / f"pair_{ia:02}_{ib:02}.npz"
        if not p.exists():
            raise RuntimeError(f"missing committed pair: {p}")
        actual = sha256_file(p)
        expected = str(row["sha256"])
        if actual != expected:
            raise RuntimeError(f"pair hash mismatch for delta: {p}")
        pair_paths.append(p)
    events_delta = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows).encode()
    manifest = {
        "schema": "HEAVY_NUMERICS_V2_DELTA_1",
        "sequence": int(sequence),
        "pair_count": len(rows),
        "pairs": [
            {
                "ia": int(r["ia"]),
                "ib": int(r["ib"]),
                "filename": p.name,
                "bytes": p.stat().st_size,
                "sha256": sha256_file(p),
            }
            for r, p in zip(rows, pair_paths)
        ],
        "identity_sha256": sha256_file(identity),
        "parent_checkpoint_sha256": parent_checkpoint_sha256,
        "created_unix": time.time(),
    }
    name = f"delta_{sequence:04d}_{len(rows):02d}pairs.zip"
    out = delta_dir / name
    tmp = out.with_suffix(out.suffix + ".tmp")
    with zipfile.ZipFile(tmp, "w", allowZip64=True) as zf:
        _zip_write_bytes(zf, "IDENTITY.json", identity.read_bytes())
        _zip_write_bytes(zf, "events_delta.jsonl", events_delta)
        for p in pair_paths:
            _zip_write_bytes(zf, p.name, p.read_bytes())
        _zip_write_bytes(
            zf,
            "DELTA_MANIFEST.json",
            (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode(),
        )
    os.replace(tmp, out)
    return out


def _jsonl_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def append_delta_queue(folder: Path | str, delta_path: Path | str) -> str:
    folder = Path(folder)
    delta_path = Path(delta_path)
    if not delta_path.exists():
        raise FileNotFoundError(delta_path)
    h = sha256_file(delta_path)
    q = folder / "DURABLE_UPLOAD_QUEUE.jsonl"
    existing = _jsonl_rows(q)
    if not any(r.get("delta_sha256") == h for r in existing):
        row = {
            "delta_sha256": h,
            "delta_path": str(delta_path),
            "bytes": delta_path.stat().st_size,
            "queued_unix": time.time(),
        }
        with q.open("a") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
    return h


def record_dual_backup_ack(
    folder: Path | str,
    delta_sha256: str,
    *,
    drive: Mapping[str, object] | None,
    dropbox: Mapping[str, object] | None,
) -> None:
    if not drive or not dropbox:
        raise ValueError("both providers are required for durable acknowledgement")
    folder = Path(folder)
    pending = set(pending_delta_hashes(folder))
    if delta_sha256 not in pending:
        raise ValueError("delta is not pending or is already acknowledged")
    path = folder / "DURABLE_ACKS.jsonl"
    row = {
        "delta_sha256": delta_sha256,
        "drive": dict(drive),
        "dropbox": dict(dropbox),
        "acked_unix": time.time(),
    }
    with path.open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def pending_delta_hashes(folder: Path | str) -> list[str]:
    folder = Path(folder)
    queued = _jsonl_rows(folder / "DURABLE_UPLOAD_QUEUE.jsonl")
    acked = {r.get("delta_sha256") for r in _jsonl_rows(folder / "DURABLE_ACKS.jsonl")}
    return [str(r["delta_sha256"]) for r in queued if r.get("delta_sha256") not in acked]


def estimate_remaining_cpu_seconds(event_rows: Sequence[Mapping[str, object]], pending_pairs: int) -> float | None:
    vals = [float(r["cpu_seconds"]) for r in event_rows if r.get("cpu_seconds") is not None]
    if not vals:
        return None
    return (sum(vals) / len(vals)) * int(pending_pairs)
