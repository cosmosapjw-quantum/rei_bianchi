"""Persistent bridge to the pinned original Case-A H/He point evaluator.

The native process owns cosmological densities and rates. All power inputs are
per absorber in erg/s, and all returned event/energy rates use cgs units.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import selectors
import subprocess
import time

import numpy as np

SOURCE_COMMIT = "f7830e2f55e7a1938bc3c98f61b60651f8dae474"
Y_HE = 0.2454 / (4.0 * (1.0 - 0.2454))
_FIELDS = (
    "nh", "nhe", "fraction_dt", "w_dt_ev_per_h_s", "temperature_K",
    "photo_events", "thermal_micro", "binding_micro", "escape", "cmb",
    "photo_input", "ci", "rr", "dr",
)
_WIDTHS = (1, 1, 3, 1, 1, 3, 1, 1, 1, 1, 1, 3, 3, 1)
_COUNT = sum(_WIDTHS)


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class NativeOwner:
    """One persistent binary and one in-order stdio request stream.

    evidence_path is a gzip JSONL destination. During a failed or interrupted
    session, its .partial sibling retains every completed record, fsynced after
    each write. Successful close atomically publishes the destination.
    """

    def __init__(self, binary, evidence_path=None, timeout=20.0,
                 expected_binary_sha256=None):
        self.binary = Path(binary).resolve(strict=True)
        self.binary_sha256 = _sha(self.binary)
        if expected_binary_sha256 is not None and self.binary_sha256 != expected_binary_sha256:
            raise ValueError("HE25_BINARY_SHA_MISMATCH")
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("HE25_TIMEOUT_DOMAIN")
        self.timeout = float(timeout)
        self.evidence_path = Path(evidence_path) if evidence_path is not None else None
        self._partial = None
        self._evidence = None
        self._process = None
        self._buffer = bytearray()
        self.calls = 0
        self.failed = False
        self.n_h0 = None
        self.n_he0 = None

    def _record(self, event):
        if self._evidence is None:
            return
        event.update(binary_sha256=self.binary_sha256, source_commit=SOURCE_COMMIT,
                     monotonic_ns=time.monotonic_ns())
        self._evidence.write((json.dumps(event, allow_nan=False, separators=(",", ":")) + "\n").encode())
        self._evidence.flush()
        os.fsync(self._evidence.fileobj.fileno())

    def _readline(self):
        deadline = time.monotonic() + self.timeout
        while True:
            end = self._buffer.find(b"\n")
            if end >= 0:
                line = bytes(self._buffer[:end])
                del self._buffer[:end+1]
                return line.decode("utf-8", "strict")
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("HE25_OWNER_RESPONSE_TIMEOUT")
            with selectors.DefaultSelector() as selector:
                selector.register(self._process.stdout, selectors.EVENT_READ)
                if not selector.select(remaining):
                    raise TimeoutError("HE25_OWNER_RESPONSE_TIMEOUT")
            chunk = os.read(self._process.stdout.fileno(), 4096)
            if not chunk:
                raise RuntimeError(f"HE25_OWNER_EOF: {bytes(self._buffer)!r}")
            self._buffer.extend(chunk)
            if len(self._buffer) > 16384:
                raise ValueError("HE25_OWNER_OVERSIZE_RESPONSE")

    def __enter__(self):
        if self._process is not None:
            raise RuntimeError("HE25_OWNER_ALREADY_STARTED")
        if _sha(self.binary) != self.binary_sha256:
            raise ValueError("HE25_BINARY_CHANGED")
        if self.evidence_path is not None:
            self.evidence_path.parent.mkdir(parents=True, exist_ok=True)
            self._partial = self.evidence_path.with_name(self.evidence_path.name + ".partial")
            self._evidence = gzip.open(self._partial, "xb")
        try:
            self._process = subprocess.Popen([str(self.binary)], stdin=subprocess.PIPE,
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                             bufsize=0)
            line = self._readline()
            self._record({"kind": "handshake", "response": line})
            columns = line.split("\t")
            if len(columns) != 4 or columns[:2] != ["HE25_OWNER_V1", SOURCE_COMMIT]:
                raise ValueError("HE25_OWNER_HANDSHAKE_OR_SOURCE")
            self.n_h0, self.n_he0 = map(float, columns[2:])
            self._check_density(self.n_h0, self.n_he0)
            return self
        except BaseException as exc:
            self.failed = True
            self._record({"kind": "failure", "error": repr(exc),
                          "partial_response": self._buffer.decode("utf-8", "replace")})
            self.close()
            raise

    @staticmethod
    def _check_density(nh, nhe):
        if not (math.isfinite(nh) and math.isfinite(nhe) and nh > 0 and nhe > 0):
            raise ValueError("HE25_DENSITY_DOMAIN")
        if abs(nhe / nh / Y_HE - 1.0) > 1e-9:
            raise AssertionError("HE25_HELIUM_SOURCE_MISMATCH")

    def density(self, a):
        if self._process is None or self._process.poll() is not None:
            raise RuntimeError("HE25_OWNER_CLOSED")
        a = float(a)
        if not math.isfinite(a) or not 1 / 21 <= a <= 1 / 5:
            raise ValueError("HE25_SCALE_DOMAIN")
        return self.n_h0 / a**3, self.n_he0 / a**3

    def point(self, a, gas, gamma, power):
        if self.failed:
            raise RuntimeError("HE25_OWNER_SESSION_FAILED")
        if self._process is None or self._process.poll() is not None:
            raise RuntimeError("HE25_OWNER_CLOSED")
        a = float(a)
        if not math.isfinite(a) or not 1 / 21 <= a <= 1 / 5:
            raise ValueError("HE25_SCALE_DOMAIN")
        arrays = [np.asarray(x, dtype=float) for x in (gas, gamma, power)]
        if [x.shape for x in arrays] != [(4,), (3,), (3,)]:
            raise ValueError("HE25_POINT_INPUT_SHAPE")
        if any(not np.isfinite(x).all() for x in arrays):
            raise ValueError("HE25_POINT_NONFINITE")
        if (arrays[1] < 0).any() or (arrays[2] < 0).any():
            raise ValueError("HE25_POINT_NEGATIVE_PHOTO")
        numbers = [a, *(float(x) for arr in arrays for x in arr)]
        request = "\t".join(format(x, ".17e") for x in numbers)
        try:
            self._process.stdin.write((request + "\n").encode())
            response = self._readline()
            self.calls += 1
            self._record({"kind": "point", "request": request, "response": response})
            columns = response.split("\t")
            if columns[0] == "ERROR":
                raise RuntimeError("HE25_OWNER_ERROR: " + response)
            if columns[0] != "POINT" or len(columns) != _COUNT + 1:
                raise ValueError("HE25_OWNER_POINT_SCHEMA")
            values = [float(x) for x in columns[1:]]
            if not all(math.isfinite(x) for x in values):
                raise ValueError("HE25_OWNER_NONFINITE")
            out = {}
            pos = 0
            for key, width in zip(_FIELDS, _WIDTHS):
                part = values[pos:pos+width]
                out[key] = np.array(part) if width == 3 else part[0]
                pos += width
            self._check_density(out["nh"], out["nhe"])
            expected_nh, expected_nhe = self.density(a)
            if abs(out["nh"] / expected_nh - 1) > 1e-9 or abs(out["nhe"] / expected_nhe - 1) > 1e-9:
                raise AssertionError("HE25_OWNER_DENSITY_MISMATCH")
            if not 1.0 <= out["temperature_K"] <= 1e6:
                raise ValueError("HE25_OWNER_TEMPERATURE_DOMAIN")
            return out
        except BaseException as exc:
            self.failed = True
            self._record({"kind": "failure", "request": request,
                          "error": repr(exc),
                          "partial_response": self._buffer.decode("utf-8", "replace")})
            raise

    def close(self):
        if self._process is not None:
            process = self._process
            self._process = None
            try:
                process.stdin.close()
                process.wait(timeout=self.timeout)
            except (subprocess.TimeoutExpired, OSError):
                self.failed = True
                process.kill()
                process.wait()
            finally:
                process.stdout.close()
                process.stderr.close()
            if process.returncode != 0:
                self.failed = True
        if self._evidence is not None:
            self._evidence.close()
            self._evidence = None
            if not self.failed:
                os.replace(self._partial, self.evidence_path)
                fd = os.open(self.evidence_path.parent, os.O_RDONLY)
                try:
                    os.fsync(fd)
                finally:
                    os.close(fd)

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            self.failed = True
        self.close()
        return False
