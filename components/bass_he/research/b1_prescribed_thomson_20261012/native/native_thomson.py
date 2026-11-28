"""C ABI binding to the unmodified bass polarized Thomson Rust operator.

Array convention: J[angle, energy, component], float64, C contiguous.
Components: S11,S22,S33,S12,S13,S23,A23,A31,A12.
The collision depth x is dimensionless c*sigma_T*ne_eff*proper_dt.
This module contains no replacement Thomson implementation.
"""
from __future__ import annotations

import ctypes as ct
from pathlib import Path

import numpy as np

DPTR = ct.POINTER(ct.c_double)


class NativeThomson:
    def __init__(self, ehat, weights, library_path=None):
        self.ehat = np.ascontiguousarray(ehat, dtype=np.float64)
        self.weights = np.ascontiguousarray(weights, dtype=np.float64)
        if self.ehat.shape != (len(self.weights), 3) or self.weights.ndim != 1:
            raise ValueError("Grid must be ehat[M,3], weights[M]")
        if len(self.weights) == 0 or not np.isfinite(self.ehat).all():
            raise ValueError("Empty or nonfinite angular grid")
        if not np.isfinite(self.weights).all() or np.any(self.weights <= 0):
            raise ValueError("Quadrature weights must be positive and finite")
        if np.max(np.abs(np.sum(self.ehat**2, axis=1) - 1)) > 1e-12:
            raise ValueError("Angular directions must have unit norm")
        if abs(self.weights.sum() - 4*np.pi) > 1e-11:
            raise ValueError("Angular weights must integrate 4*pi")
        path = Path(library_path) if library_path else Path(__file__).with_name("libb1_thomson.so")
        self.lib = ct.CDLL(str(path.resolve()))
        self.lib.b1_kernel_abi.restype = ct.c_uint64
        if self.lib.b1_kernel_abi() != 1:
            raise RuntimeError("Unexpected B1 kernel ABI")
        self.lib.b1_collide_modeb.argtypes = [DPTR, DPTR, DPTR, ct.c_size_t,
                                            ct.c_size_t, ct.c_double, DPTR]
        self.lib.b1_collide_modeb.restype = ct.c_int
        self.lib.b1_kcal_eigenvalues.argtypes = [DPTR, DPTR, ct.c_size_t, DPTR]
        self.lib.b1_kcal_eigenvalues.restype = ct.c_int
        self.calls = 0
        self.positive_depth_calls = 0
        self.depth_sum = 0.0

    @staticmethod
    def _ptr(array):
        return array.ctypes.data_as(DPTR)

    def collide(self, j, x):
        arr = np.ascontiguousarray(j, dtype=np.float64)
        if arr.ndim != 3 or arr.shape[0] != len(self.weights) or arr.shape[2] != 9:
            raise ValueError("J must have shape [n_angle,n_energy,9]")
        if arr.shape[1] == 0 or not np.isfinite(x) or x < 0:
            raise ValueError("Need at least one energy and finite x>=0")
        out = np.empty_like(arr)
        code = self.lib.b1_collide_modeb(self._ptr(self.ehat), self._ptr(self.weights),
                                        self._ptr(arr), len(self.weights), arr.shape[1],
                                        float(x), self._ptr(out))
        if code:
            raise RuntimeError(f"Native Thomson boundary rejected call, code={code}")
        self.calls += 1
        self.positive_depth_calls += int(x > 0)
        self.depth_sum += float(x)
        return out

    def eigenvalues(self):
        out = np.empty(3, dtype=np.float64)
        code = self.lib.b1_kcal_eigenvalues(self._ptr(self.ehat), self._ptr(self.weights),
                                          len(self.weights), self._ptr(out))
        if code:
            raise RuntimeError(f"Native grid eigenvalue call failed, code={code}")
        return out
