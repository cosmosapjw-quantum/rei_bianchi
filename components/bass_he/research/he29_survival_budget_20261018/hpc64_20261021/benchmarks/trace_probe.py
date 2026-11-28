"""Bounded same-filesystem gzip/fsync benchmark, without a science process.

The workload is manufactured JSONL point evidence. The original NativeOwner
_record/close implementation and batch sizes 1/256 write the same events. Every
timed sample includes complete gzip readback; subsequent semantic hashing checks
all request/response records outside the timing window. No solver is imported or
executed. Ratios describe only this host/filesystem/workload, not HE29 or NCP.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import statistics
import sys
import time

LANE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("he29_batched_native_probe", LANE / "src/batched_native.py")
batched = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(batched)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def workload(count):
    events = [{"kind": "handshake", "phase": "startup",
               "response": "HE25_OWNER_V1\t" + batched.SOURCE_COMMIT + "\t1e-7\t8e-9"}]
    state = 123456789
    for i in range(count):
        values = []
        for _ in range(33):
            state = (1664525 * state + 1013904223) % 2**32
            values.append(format((state + 1) / 2**32, ".17e"))
        events.append({"kind": "point", "phase": "request",
                       "request": "\t".join(values[:11]),
                       "response": "POINT\t" + "\t".join(values[11:])})
    return events


def readback(path, expected_count, binary_sha):
    count = 0
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            event = json.loads(line)
            if (event["binary_sha256"] != binary_sha
                    or event["source_commit"] != batched.SOURCE_COMMIT):
                raise ValueError("TRACE_PROBE_IDENTITY")
            count += 1
    if count != expected_count:
        raise ValueError("TRACE_PROBE_COUNT")


def semantic_sha(path):
    h = hashlib.sha256()
    count = 0
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            event = json.loads(line)
            del event["monotonic_ns"]
            h.update((json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n").encode())
            count += 1
    return h.hexdigest(), count


def sample(out, label, repeat, events):
    path = out / f"{label}_{repeat}.jsonl.gz"
    cls = batched.OriginalNativeOwner if label == "original" else batched.BatchedNativeOwner
    kwargs = {} if label == "original" else {"sync_every": int(label[5:])}
    owner = cls(sys.executable, evidence_path=path, **kwargs)
    owner._partial = path.with_name(path.name + ".partial")
    count = 0
    original_fsync = os.fsync
    def counted_fsync(fd):
        nonlocal count
        count += 1
        return original_fsync(fd)  # Actual fsync; never a no-op timing surrogate.
    os.fsync = counted_fsync
    start = time.perf_counter()
    try:
        owner._evidence = gzip.open(owner._partial, "xb")
        for event in events:
            owner._record(dict(event))
        owner.close()
        if label == "original":
            readback(path, len(events), owner.binary_sha256)
        elapsed = time.perf_counter() - start
    finally:
        os.fsync = original_fsync
    semantic, records = semantic_sha(path)
    return {"label": label, "repeat": repeat, "elapsed_s": elapsed,
            "records": records, "point_records": len(events) - 1,
            "actual_fsync_calls": count, "compressed_bytes": path.stat().st_size,
            "archive_sha256": sha(path), "semantic_records_sha256": semantic,
            "complete_gzip_readback": True,
            "telemetry": None if label == "original" else owner.evidence_telemetry()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    parser.add_argument("--records", type=int, default=4096)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.records <= 16384 or not 1 <= args.repeats <= 5:
        parser.error("bounded probe requires records in1..16384 and repeats in1..5")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc).isoformat()
    receipt = {"schema": "he29.hpc64.trace-probe.v1", "started_utc": started,
               "command": [sys.executable, *sys.argv],
               "records_per_sample": args.records, "repeats": args.repeats,
               "actual_HE29_native_calls": 0, "solver_runs": 0, "NCP_execution": False,
               "scope": "Manufactured gzip/fsync I/O on this filesystem; no native process launched.",
               "timing_scope": "gzip open, identical event writes, actual flush/fsync, close and full gzip/JSONL readback; semantic hashing outside timing",
               "strict_baseline": "Original NativeOwner record/close plus complete gzip readback; batch1 is a second same-durability control.",
               "durability_tradeoff": "batch256 may leave at most255 successful point records beyond the last completed fsync after a process hard kill; all normal-close records retained. No filesystem/power-failure guarantee.",
               "hardware": {"platform": platform.platform(), "python": sys.version,
                            "logical_cpu_count": os.cpu_count(),
                            "affinity_cpu_count": len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
                            "filesystem_device": out.stat().st_dev},
               "sources": {"batched_native.py": sha(LANE / "src/batched_native.py"),
                           "trace_probe.py": sha(__file__),
                           "original_native.py": batched.ORIGINAL_NATIVE_SHA256},
               "samples": []}
    for cgroup in ("cpu.max", "memory.max"):
        path = Path("/sys/fs/cgroup") / cgroup
        if path.is_file():
            receipt["hardware"][cgroup] = path.read_text().strip()
    try:
        events = workload(args.records)
        labels = ("original", "batch1", "batch256")
        for repeat in range(args.repeats):
            order = labels[repeat % 3:] + labels[:repeat % 3]
            for label in order:
                receipt["samples"].append(sample(out, label, repeat, events))
        semantics = {x["semantic_records_sha256"] for x in receipt["samples"]}
        if len(semantics) != 1:
            raise AssertionError("TRACE_PROBE_SEMANTIC_RECORD_MISMATCH")
        medians = {label: statistics.median(x["elapsed_s"] for x in receipt["samples"]
                                           if x["label"] == label) for label in labels}
        receipt.update(status="PASS_MANUFACTURED_TRACE_IO", median_elapsed_s=medians,
                       original_over_batch256=medians["original"] / medians["batch256"],
                       batch1_over_batch256=medians["batch1"] / medians["batch256"],
                       all_semantic_records_identical=True,
                       semantic_records_sha256=next(iter(semantics)), exit_code=0)
    except BaseException as exc:
        receipt.update(status="FAIL", error=repr(exc), exit_code=1)
        raise
    finally:
        receipt["finished_utc"] = datetime.now(timezone.utc).isoformat()
        (out / "RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
