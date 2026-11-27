"""Opt-in batching of native evidence durability, with unchanged point semantics.

The pinned HE25 NativeOwner still owns startup, stdin framing, response parsing,
validation and binary/source checks.  Only the gzip evidence synchronization
schedule changes.  Every request/response record is written in original order.

After a process hard kill, at most ``sync_every - 1`` successfully returned point
records can lie beyond the last completed evidence fsync.  This is a bounded
unsynchronized-record window, not the original per-call durability contract or
a guarantee against filesystem/power failure.  Use sync_every=1 for that original
per-call schedule.  Checkpoints and ordinary close flush all pending records.
The parent must call flush_evidence at segment checkpoints and before admission.
Successful close reads the complete gzip/JSONL stream before create-only publish.
"""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import time

ORIGINAL_NATIVE_SHA256 = "a72767ac013fe1cfe6d4d96a335e6b3d1194ec34c3e6baa3887f5babd0aa6d9e"
_SOURCE = (Path(__file__).resolve().parents[3]
           / "he25_proper_birth_20261016/src/native.py")
if hashlib.sha256(_SOURCE.read_bytes()).hexdigest() != ORIGINAL_NATIVE_SHA256:
    raise RuntimeError("HE29_BATCHED_NATIVE_SOURCE_MISMATCH")
_SPEC = importlib.util.spec_from_file_location("he29_hpc64_original_native", _SOURCE)
_native = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_native)
OriginalNativeOwner = _native.NativeOwner
SOURCE_COMMIT = _native.SOURCE_COMMIT


class BatchedNativeOwner(OriginalNativeOwner):
    """Explicit evidence policy; no asynchronous writer and no point-result cache."""

    def __init__(self, binary, evidence_path=None, timeout=20.0,
                 expected_binary_sha256=None, startup_timeout=None, *, sync_every=256):
        if type(sync_every) is not int or sync_every < 1:
            raise ValueError("HE29_TRACE_SYNC_EVERY_POSITIVE_INTEGER")
        super().__init__(binary, evidence_path=evidence_path, timeout=timeout,
                         expected_binary_sha256=expected_binary_sha256,
                         startup_timeout=startup_timeout)
        self.sync_every = sync_every
        self._records_written = self._points_written = 0
        self._records_durable = self._points_durable = 0
        self._fsync_attempts = self._fsync_successes = 0
        self._checkpoint_calls = 0
        self._verified_records = self._verified_points = 0
        self._complete_readback = self._published = False
        self._trace_error = None
        self._closing_evidence = None
        self._close_finished = False

    def _trace(self):
        return self._evidence if self._evidence is not None else self._closing_evidence

    def _trace_failed(self, exc):
        self.failed = True
        if self._trace_error is None:
            self._trace_error = exc

    def _fsync(self, fd):
        self._fsync_attempts += 1
        try:
            os.fsync(fd)
        except BaseException as exc:
            self._trace_failed(exc)
            raise
        self._fsync_successes += 1

    def _sync_open(self):
        trace = self._trace()
        if trace is None:
            return
        try:
            trace.flush()
            self._fsync(trace.fileobj.fileno())
        except BaseException as exc:
            self._trace_failed(exc)
            raise
        self._records_durable = self._records_written
        self._points_durable = self._points_written

    def _record(self, event):
        trace = self._trace()
        if trace is None:
            return
        try:
            event.update(binary_sha256=self.binary_sha256,
                         source_commit=SOURCE_COMMIT, monotonic_ns=time.monotonic_ns())
            data = (json.dumps(event, allow_nan=False, separators=(",", ":")) + "\n").encode()
            if trace.write(data) != len(data):
                raise OSError("HE29_TRACE_SHORT_WRITE")
            self._records_written += 1
            if event.get("kind") == "point":
                self._points_written += 1
            if (event.get("kind") != "point"
                    or self._points_written - self._points_durable >= self.sync_every):
                self._sync_open()
        except BaseException as exc:
            self._trace_failed(exc)
            raise

    def flush_evidence(self, reason="checkpoint"):
        """Durability barrier. Any prior trace error stays fatal for admission."""
        if self._trace_error is not None:
            raise self._trace_error
        if self._trace() is not None and self._records_written != self._records_durable:
            self._sync_open()
        self._checkpoint_calls += 1
        return self.evidence_telemetry()

    def evidence_telemetry(self):
        return {
            "schema": "he29.batched-native-evidence.v1",
            "policy": "per_point_sync" if self.sync_every == 1 else "bounded_point_batch_sync",
            "sync_every_points": self.sync_every,
            "hardkill_unsynchronized_successful_point_bound": self.sync_every - 1,
            "bound_scope": "process hard kill; not filesystem or power-loss durability",
            "records_written": self._records_written,
            "point_records_written": self._points_written,
            "records_durable": self._records_durable,
            "point_records_durable": self._points_durable,
            "fsync_attempts": self._fsync_attempts,
            "fsync_successes": self._fsync_successes,
            "checkpoint_flush_calls": self._checkpoint_calls,
            "complete_gzip_readback": self._complete_readback,
            "verified_records": self._verified_records,
            "verified_point_records": self._verified_points,
            "published": self._published,
            "trace_error": None if self._trace_error is None else repr(self._trace_error),
            "owner_failed": self.failed,
            "original_native_sha256": ORIGINAL_NATIVE_SHA256,
            "source_commit": SOURCE_COMMIT,
            "binary_sha256": self.binary_sha256,
        }

    def _read_complete_trace(self):
        records = points = 0
        with gzip.open(self._partial, "rt", encoding="utf-8") as stream:
            for line in stream:
                event = json.loads(line)
                if (event.get("binary_sha256") != self.binary_sha256
                        or event.get("source_commit") != SOURCE_COMMIT):
                    raise ValueError("HE29_TRACE_READBACK_IDENTITY")
                records += 1
                points += event.get("kind") == "point"
        if (records, points) != (self._records_written, self._points_written):
            raise ValueError("HE29_TRACE_READBACK_RECORD_COUNT")
        self._verified_records, self._verified_points = records, points
        self._complete_readback = True

    def __enter__(self):
        try:
            return super().__enter__()
        except BaseException:
            # The original startup exception handler can itself encounter an I/O
            # failure while recording failure. Ensure its started process closes.
            self.failed = True
            try:
                self.close()
            except BaseException:
                pass  # Preserve the exception already being propagated.
            raise

    def close(self):
        if self._close_finished:
            return
        trace, process = self._evidence, self._process
        self._evidence = None
        self._closing_evidence = trace
        cleanup_error = None
        try:
            # With _evidence detached, original close performs only unchanged
            # native-process shutdown. _record still uses _closing_evidence.
            super().close()
        except BaseException as exc:
            self.failed = True
            cleanup_error = exc
        finally:
            if process is not None:
                for stream in (process.stdin, process.stdout, process.stderr):
                    if stream is not None and not stream.closed:
                        stream.close()
        if trace is not None:
            try:
                self._sync_open()
            except BaseException as exc:
                self._trace_failed(exc)
            try:
                trace.close()
                with self._partial.open("rb") as stream:
                    self._fsync(stream.fileno())  # gzip trailer is now included.
                self._records_durable = self._records_written
                self._points_durable = self._points_written
                self._read_complete_trace()
                if not self.failed:
                    os.link(self._partial, self.evidence_path)
                    self._partial.unlink()
                    self._published = True
            except BaseException as exc:
                self._trace_failed(exc)
            finally:
                self._closing_evidence = None
                try:
                    fd = os.open(self.evidence_path.parent, os.O_RDONLY)
                    try:
                        self._fsync(fd)
                    finally:
                        os.close(fd)
                except BaseException as exc:
                    self._trace_failed(exc)
        self._close_finished = True
        if self._trace_error is not None:
            raise self._trace_error
        if cleanup_error is not None:
            raise cleanup_error
