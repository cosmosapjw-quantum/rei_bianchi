"""Checked, explicit ctypes interface for the Fortran element kernel (ABI 1).

No implicit Python fallback or precision change is permitted. OpenMP/BLAS thread
environment variables must be set before process startup; native_info records
the loaded library identity and OpenMP maximum thread count.
"""
from __future__ import annotations

import ctypes
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path

import numpy as np

_REAL = ctypes.POINTER(ctypes.c_double)
_INT64 = ctypes.POINTER(ctypes.c_int64)
_ABI = 1


def _library_path() -> Path:
    value = os.environ.get("BASS_NATIVE_LIBRARY")
    if value:
        return Path(value).expanduser().resolve(strict=True)
    return (Path(__file__).resolve().parents[1] / "native" / "build" /
            "libbass_element.so").resolve(strict=True)


@lru_cache(maxsize=4)
def _load(path_string: str, expected: str | None):
    path = Path(path_string)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if expected is not None and sha != expected.lower():
        raise RuntimeError("native library SHA-256 differs from BASS_NATIVE_EXPECTED_SHA256")
    library = ctypes.CDLL(str(path))
    library.bass_native_abi.argtypes = []
    library.bass_native_abi.restype = ctypes.c_int
    if library.bass_native_abi() != _ABI:
        raise RuntimeError("native library ABI mismatch")
    library.bass_native_max_threads.argtypes = []
    library.bass_native_max_threads.restype = ctypes.c_int
    function = library.bass_element_blocks
    function.argtypes = [ctypes.c_int]*4 + [_REAL]*6 + [_INT64, _REAL]
    function.restype = None
    metadata = path.with_suffix(".build.json")
    build = json.loads(metadata.read_text()) if metadata.exists() else None
    if build is not None and build.get("library_sha256") != sha:
        raise RuntimeError("native build manifest does not match loaded library bytes")
    return library, {"abi": _ABI, "library_path": str(path), "library_sha256": sha,
                     "build": build,
                     "identity_scope": "library bytes measured at initial process load"}


def _backend():
    try:
        path = _library_path()
    except FileNotFoundError as exc:
        raise RuntimeError("native library absent: run python native/build.py --mode strict") from exc
    return _load(str(path), os.environ.get("BASS_NATIVE_EXPECTED_SHA256"))


def native_info() -> dict:
    library, info = _backend()
    return {**info, "openmp_max_threads": int(library.bass_native_max_threads()),
            "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"),
            "OMP_PROC_BIND": os.environ.get("OMP_PROC_BIND"),
            "OMP_PLACES": os.environ.get("OMP_PLACES")}


def library_identity() -> dict:
    """Public provenance entry point used by the optimized solver."""
    return native_info()


def _real_array(value, name, ndim):
    if not isinstance(value, np.ndarray) or value.dtype != np.dtype(np.float64):
        raise TypeError(f"{name} must be a float64 NumPy array (no implicit precision conversion)")
    if value.ndim != ndim or any(dim == 0 for dim in value.shape):
        raise ValueError(f"{name} must have {ndim} nonempty dimensions")
    if not np.isfinite(value).all():
        raise ValueError(f"{name} must contain only finite values")
    return value


def prepare_element_kernel(B, gaunt, ls):
    """Validate/copy immutable solve-wide tensors once; return a block kernel.

    Private owned read-only copies ensure a later mutation of caller inputs
    cannot invalidate validation or silently alter the prepared operator.
    """
    B = _real_array(B, "B", 2)
    gaunt = _real_array(gaunt, "gaunt", 3)
    nq, na = B.shape
    nk, nl, nl2 = gaunt.shape
    if nl != nl2:
        raise ValueError("gaunt angular dimensions must be square")
    if not isinstance(ls, np.ndarray) or ls.dtype != np.dtype(np.int64):
        raise TypeError("ls must be an int64 NumPy array")
    if (ls.shape != (nl,) or np.any(ls < 0) or
            np.any(ls[1:] <= ls[:-1])):
        raise ValueError("ls must have shape (nl,), nonnegative and strictly increasing")
    if max(nq, na, nk, nl) > np.iinfo(np.int32).max:
        raise ValueError("native ABI dimensions exceed int32")
    library, _ = _backend()
    return _PreparedElementKernel(B, gaunt, ls, library)


class _PreparedElementKernel:
    __slots__ = ("_basis", "_gaunt", "_ls", "_library", "nq", "na", "nk", "nl")

    def __init__(self, B, gaunt, ls, library):
        self._basis = np.array(B, dtype=np.float64, order="F", copy=True)
        self._gaunt = np.array(gaunt, dtype=np.float64, order="C", copy=True)
        self._ls = np.array(ls, dtype=np.int64, order="C", copy=True)
        for value in (self._basis, self._gaunt, self._ls):
            value.setflags(write=False)
        self._library = library
        self.nq, self.na = B.shape
        self.nk, self.nl, _ = gaunt.shape

    def blocks(self, vl, weights, kin, cent) -> np.ndarray:
        """Contract one element; validate only the element-varying inputs."""
        vl = _real_array(vl, "vl", 2)
        weights = _real_array(weights, "weights", 1)
        kin = _real_array(kin, "kin", 2)
        cent = _real_array(cent, "cent", 2)
        if vl.shape != (self.nq, self.nk) or weights.shape != (self.nq,):
            raise ValueError("inconsistent angular or quadrature dimensions")
        if kin.shape != (self.na, self.na) or cent.shape != (self.na, self.na):
            raise ValueError("kin and cent must both have shape (na,na)")
        inputs = [self._basis, self._gaunt, np.asfortranarray(vl),
                  np.ascontiguousarray(weights), np.asfortranarray(kin),
                  np.asfortranarray(cent)]
        result = np.empty((self.nl, self.na, self.nl, self.na), dtype=np.float64, order="C")
        self._library.bass_element_blocks(self.nq, self.na, self.nk, self.nl,
            *[value.ctypes.data_as(_REAL) for value in inputs],
            self._ls.ctypes.data_as(_INT64), result.ctypes.data_as(_REAL))
        if not np.isfinite(result).all():
            raise FloatingPointError("native element contraction produced nonfinite output")
        return result


def element_blocks(B, gaunt, vl, weights, kin, cent, ls) -> np.ndarray:
    """One-shot checked API; repeated elements should use prepare_element_kernel.

    Shapes: B=(nq,na), gaunt=(nk,nl,nl), vl=(nq,nk), weights=(nq,),
    kin=cent=(na,na), ls=(nl,). Output is C-order (nl,na,nl,na).
    Gaunt symmetry is deliberately NOT assumed.
    """
    return prepare_element_kernel(B, gaunt, ls).blocks(vl, weights, kin, cent)
