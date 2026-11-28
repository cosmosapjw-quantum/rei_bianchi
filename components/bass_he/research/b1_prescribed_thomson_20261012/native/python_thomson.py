"""Explicit source-pinned Python backend for the B1 scientific comparison.

This is an explicit backend selection, not a fallback from the Rust binding.
Every energy slice calls the original bass polarization.collide function.
No Thomson coefficients, cross section, or scattering formula is replaced.
"""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

import numpy as np

SOURCE_PATH = Path(__file__).with_name("upstream_polarization.py")
SOURCE_GIT_BLOB = "7448ea6701f236fd41d22f3c5cadfd80f482d82f"


def _load_upstream():
    raw = SOURCE_PATH.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if blob != SOURCE_GIT_BLOB:
        raise RuntimeError("Existing bass Python kernel byte identity mismatch")
    spec = importlib.util.spec_from_file_location("b1_upstream_polarization", SOURCE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


UPSTREAM = _load_upstream()


class PythonThomson:
    backend = "EXPLICIT_EXISTING_BASS_PYTHON"
    native_rust_invocations = 0

    def __init__(self, ehat, weights):
        self.ehat = np.ascontiguousarray(ehat, dtype=np.float64)
        self.weights = np.ascontiguousarray(weights, dtype=np.float64)
        if self.weights.ndim != 1 or self.ehat.shape != (len(self.weights), 3):
            raise ValueError("Grid must be ehat[M,3], weights[M]")
        if len(self.weights) == 0 or not np.isfinite(self.ehat).all():
            raise ValueError("Empty or nonfinite angular grid")
        if not np.isfinite(self.weights).all() or np.any(self.weights <= 0):
            raise ValueError("Quadrature weights must be positive and finite")
        if np.max(np.abs(np.sum(self.ehat**2, axis=1) - 1)) > 1e-12:
            raise ValueError("Angular directions must have unit norm")
        if abs(self.weights.sum() - 4*np.pi) > 1e-11:
            raise ValueError("Angular weights must integrate 4*pi")
        self.calls = 0
        self.positive_depth_calls = 0
        self.upstream_energy_slice_calls = 0
        self.depth_sum = 0.0

    def collide(self, j, x):
        arr = np.ascontiguousarray(j, dtype=np.float64)
        if arr.ndim != 3 or arr.shape[0] != len(self.weights) or arr.shape[2] != 9:
            raise ValueError("J must have shape [n_angle,n_energy,9]")
        if arr.shape[1] == 0 or not np.isfinite(x) or x < 0:
            raise ValueError("Need at least one energy and finite x>=0")
        if not np.isfinite(arr).all():
            raise ValueError("J contains nonfinite entries")
        out = np.empty_like(arr)
        for energy in range(arr.shape[1]):
            tensor = UPSTREAM.unpack9(arr[:, energy, :])
            result = UPSTREAM.collide(self.ehat, self.weights, tensor, float(x))
            out[:, energy, :] = UPSTREAM.pack9(result)
            self.upstream_energy_slice_calls += 1
        if not np.isfinite(out).all():
            raise FloatingPointError("Existing Thomson kernel returned nonfinite output")
        self.calls += 1
        self.positive_depth_calls += int(x > 0)
        self.depth_sum += float(x)
        return out

    def eigenvalues(self):
        return np.asarray(UPSTREAM.kcal_eigenvalues_numeric(self.ehat, self.weights))
