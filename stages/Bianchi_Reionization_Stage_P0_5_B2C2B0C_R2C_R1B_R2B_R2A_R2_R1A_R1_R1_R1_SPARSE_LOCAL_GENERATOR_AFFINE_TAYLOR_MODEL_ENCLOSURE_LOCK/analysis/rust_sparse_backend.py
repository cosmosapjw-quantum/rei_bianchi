"""Optional Rust hot-loop backend for sparse bilinear bounds."""
from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import subprocess

import numpy as np


def _rustc() -> str:
    explicit = Path("/mnt/data/rust-1.94.1-prefix/bin/rustc")
    if explicit.is_file():
        return str(explicit)
    return os.environ.get("RUSTC", "rustc")


def build_rust_backend(*, stage_dir: Path, output_dir: Path) -> Path:
    stage = Path(stage_dir).resolve()
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    source = stage / "rust/sparse_bounds.rs"
    library = output / "libsparse_local_bounds.so"
    command = [
        _rustc(),
        "--edition=2021",
        "--crate-type=cdylib",
        "-C",
        "opt-level=3",
        "-C",
        "panic=abort",
        str(source),
        "-o",
        str(library),
    ]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(f"rustc failed ({result.returncode}):\n{result.stdout}{result.stderr}")
    return library


def _contiguous(array: np.ndarray, *, shape, name: str) -> np.ndarray:
    result = np.ascontiguousarray(np.asarray(array, dtype=np.float64))
    if result.shape != shape:
        raise ValueError(f"{name} shape mismatch: {result.shape} != {shape}")
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} contains nonfinite values")
    return result


def _load_function(library: Path):
    dll = ctypes.CDLL(str(Path(library).resolve()))
    function = dll.sparse_local_bounds
    pointer = ctypes.POINTER(ctypes.c_double)
    function.argtypes = [
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.c_size_t,
        pointer,
        pointer,
        pointer,
        pointer,
        pointer,
        pointer,
        pointer,
        pointer,
        pointer,
    ]
    function.restype = ctypes.c_int
    return function


def rust_bounds(model, *, library: Path) -> tuple[np.ndarray, np.ndarray]:
    shape = model.center.shape
    n_coordinate, n_node = shape
    center = _contiguous(model.center, shape=shape, name="center")
    local_v = _contiguous(model.local_linear[0], shape=shape, name="local_v")
    local_f = _contiguous(model.local_linear[1], shape=shape, name="local_f")
    mixed = _contiguous(model.local_mixed, shape=shape, name="mixed")
    global_modes = np.ascontiguousarray(np.asarray(model.global_generators, dtype=np.float64))
    if global_modes.shape != (model.global_rank,) + shape:
        raise ValueError("global generator shape mismatch")
    rem_lo = _contiguous(model.remainder_lo, shape=shape, name="remainder_lo")
    rem_hi = _contiguous(model.remainder_hi, shape=shape, name="remainder_hi")
    lower = np.empty(shape, dtype=np.float64)
    upper = np.empty(shape, dtype=np.float64)
    pointer = ctypes.POINTER(ctypes.c_double)
    null = ctypes.cast(0, pointer)
    global_pointer = global_modes.ctypes.data_as(pointer) if model.global_rank else null
    code = _load_function(library)(
        n_coordinate,
        n_node,
        model.global_rank,
        center.ctypes.data_as(pointer),
        local_v.ctypes.data_as(pointer),
        local_f.ctypes.data_as(pointer),
        mixed.ctypes.data_as(pointer),
        global_pointer,
        rem_lo.ctypes.data_as(pointer),
        rem_hi.ctypes.data_as(pointer),
        lower.ctypes.data_as(pointer),
        upper.ctypes.data_as(pointer),
    )
    if code:
        raise RuntimeError(f"Rust sparse_local_bounds returned error code {code}")
    return lower, upper


def _ordered_bits(values: np.ndarray) -> np.ndarray:
    bits = np.asarray(values, dtype=np.float64).view(np.uint64)
    sign = bits >> np.uint64(63)
    return np.where(sign != 0, ~bits, bits | np.uint64(0x8000000000000000))


def maximum_ulp_distance(left: np.ndarray, right: np.ndarray) -> int:
    a = _ordered_bits(np.asarray(left, dtype=np.float64)).ravel()
    b = _ordered_bits(np.asarray(right, dtype=np.float64)).ravel()
    larger = np.maximum(a, b)
    smaller = np.minimum(a, b)
    return int(np.max(larger - smaller, initial=np.uint64(0)))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


__all__ = ["build_rust_backend", "file_sha256", "maximum_ulp_distance", "rust_bounds"]
