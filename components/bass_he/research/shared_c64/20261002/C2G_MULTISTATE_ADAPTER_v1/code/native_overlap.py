"""Explicit, identity-bound ctypes adapter for the C2f Fortran overlap kernel.

Only native complex128 frames / float64 weights are accepted. The kernel does
not rescale data to prevent overflow: nonfinite results are errors, never an
implicit fallback. Column-major copies cost O(N(k+l)), not O(Nkl).
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import os
from pathlib import Path
import re

import numpy as np


class NativeOverlapError(RuntimeError):
    """Explicit backend contract or runtime failure."""


def _digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _threads():
    raw = os.environ.get("OMP_NUM_THREADS", "")
    if not re.fullmatch(r"[1-9][0-9]*", raw):
        raise NativeOverlapError("OMP_NUM_THREADS must explicitly be one positive integer")
    if os.environ.get("OMP_DYNAMIC", "").upper() != "FALSE":
        raise NativeOverlapError("OMP_DYNAMIC must explicitly be FALSE")
    count = int(raw)
    if count > np.iinfo(np.int32).max:
        raise NativeOverlapError("OMP_NUM_THREADS exceeds the ABI int32 range")
    return count


def _load(library):
    if library is None:
        raise NativeOverlapError("an explicit native library path is required; no fallback is available")
    try:
        path = Path(library).resolve(strict=True)
        metadata_path = path.with_suffix(".build.json")
        metadata = json.loads(metadata_path.read_text())
        source = Path(__file__).resolve().parents[1] / "native" / "weighted_overlap.f90"
        if metadata.get("schema") != "bass-he.c2f.native-build.v1" or metadata.get("status") != "BUILD_SUCCEEDED":
            raise NativeOverlapError("unknown or incomplete native build metadata")
        if metadata.get("abi") != 1 or metadata.get("tile_rows") != 8 or metadata.get("accumulation_profile") != "eight-lane-neumaier-v2":
            raise NativeOverlapError("unsupported native ABI or tile contract")
        if path.stat().st_size != metadata.get("library_bytes") or _digest(path) != metadata.get("library_sha256"):
            raise NativeOverlapError("native library identity mismatch")
        if _digest(source) != metadata.get("source_sha256"):
            raise NativeOverlapError("native source identity mismatch")
        flags = ["-O3" if metadata.get("mode") == "strict" else "-O0", "-std=f2008", "-fPIC", "-shared", "-fopenmp", "-cpp",
                 "-fno-fast-math", "-fno-associative-math", "-ffp-contract=off", "-fprotect-parens", "-Wall", "-Wextra"]
        if metadata.get("mode") == "debug":
            flags += ["-g", "-fcheck=all", "-fbacktrace", "-ffpe-trap=invalid,zero,overflow"]
        elif metadata.get("mode") != "strict":
            raise NativeOverlapError("unknown build mode")
        flags += ['-DBASS_OVERLAP_SOURCE_SHA="' + metadata["source_sha256"] + '"']
        if metadata.get("flags") != flags:
            raise NativeOverlapError("native build flags violate the closed arithmetic profile")
        loaded = ctypes.CDLL(str(path))
        info = (ctypes.c_int * 7)()
        embedded = ctypes.create_string_buffer(65)
        loaded.bass_overlap_contract.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_char)]
        loaded.bass_overlap_contract.restype = None
        loaded.bass_overlap_contract(info, embedded)
        if tuple(info[:4]) != (1, 64, 128, 8) or embedded.value.decode("ascii") != metadata["source_sha256"]:
            raise NativeOverlapError("compiled native ABI, precision, tile or source digest mismatch")
        loaded.bass_overlap.argtypes = [ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int,
                                       ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
        loaded.bass_overlap.restype = None
        metadata = dict(metadata)
        metadata.update(library_path=str(path), verified_library_sha256=_digest(path),
                        verified_source_sha256=embedded.value.decode("ascii"),
                        runtime_max_threads=info[4], runtime_dynamic=bool(info[5]),
                        runtime_thread_limit=info[6], backend="fortran-openmp-eight-lane-neumaier-v2",
                        environment_omp_num_threads=os.environ.get("OMP_NUM_THREADS"),
                        environment_omp_dynamic=os.environ.get("OMP_DYNAMIC"))
        return loaded, metadata
    except (OSError, ValueError, KeyError, AttributeError, UnicodeError) as exc:
        raise NativeOverlapError("native library/metadata could not be validated: " + str(exc)) from exc


def identity(library):
    """Verify source, binary, embedded ABI and closed flags; report identity."""
    _, metadata = _load(library)
    return metadata


def overlap(u, v, weights, *, library):
    """Return U† diag(weights) V with explicit native execution; no fallback."""
    threads = _threads()
    for label, frame in (("u", u), ("v", v)):
        if not isinstance(frame, np.ndarray) or frame.dtype != np.dtype(np.complex128):
            raise TypeError(label + " must be an explicit native complex128 ndarray")
        if frame.ndim != 2 or 0 in frame.shape:
            raise ValueError(label + " must have nonzero (row, column) dimensions")
        if not np.isfinite(frame).all():
            raise ValueError(label + " must contain finite values")
    if not isinstance(weights, np.ndarray) or weights.dtype != np.dtype(np.float64):
        raise TypeError("weights must be an explicit native float64 ndarray")
    if weights.ndim != 1 or weights.shape != (u.shape[0],) or v.shape[0] != u.shape[0]:
        raise ValueError("frame rows and one-dimensional weight length must agree")
    if not np.isfinite(weights).all() or not np.all(weights > 0):
        raise ValueError("weights must be finite and strictly positive")
    if u.shape[1] * v.shape[1] > np.iinfo(np.int64).max:
        raise ValueError("output element count exceeds the ABI int64 range")
    loaded, metadata = _load(library)
    if metadata["runtime_dynamic"] or threads > metadata["runtime_thread_limit"]:
        raise NativeOverlapError("OpenMP runtime cannot satisfy the explicit thread contract")
    uf = np.asfortranarray(u)
    vf = np.asfortranarray(v)
    wf = np.ascontiguousarray(weights)
    result = np.empty((u.shape[1], v.shape[1]), dtype=np.complex128, order="F")
    status = ctypes.c_int(-1)
    actual_threads = ctypes.c_int(0)
    loaded.bass_overlap(u.shape[0], u.shape[1], v.shape[1], threads,
                        uf.ctypes.data, vf.ctypes.data, wf.ctypes.data, result.ctypes.data,
                        ctypes.byref(status), ctypes.byref(actual_threads))
    if status.value == 2:
        raise FloatingPointError("native weighted products or compensated sum overflowed/nonfinite")
    if status.value or actual_threads.value != threads:
        raise NativeOverlapError(f"native kernel status={status.value}, requested_threads={threads}, actual_threads={actual_threads.value}")
    if not np.isfinite(result).all():
        raise FloatingPointError("native overlap result is nonfinite")
    return result
