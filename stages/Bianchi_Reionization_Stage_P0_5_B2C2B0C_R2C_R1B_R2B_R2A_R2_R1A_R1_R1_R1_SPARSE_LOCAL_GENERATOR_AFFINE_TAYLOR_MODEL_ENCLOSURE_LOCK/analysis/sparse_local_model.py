"""Block-sparse affine/Taylor model with exact local bilinear ranges.

The model retains one pair of independent node-local coordinates and their
local product per node.  Global coupling generators are stored separately.
Remainders are explicit outward-rounded componentwise intervals.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


def _array(value, *, shape=None, name: str) -> np.ndarray:
    result = np.ascontiguousarray(np.asarray(value, dtype=np.float64))
    if shape is not None and result.shape != shape:
        raise ValueError(f"{name} shape {result.shape} != {shape}")
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} contains nonfinite values")
    result.setflags(write=False)
    return result


def _down(value: np.ndarray) -> np.ndarray:
    return np.nextafter(np.asarray(value, dtype=np.float64), -np.inf)


def _up(value: np.ndarray) -> np.ndarray:
    return np.nextafter(np.asarray(value, dtype=np.float64), np.inf)


@dataclass(frozen=True)
class SparseLocalTaylorModel:
    """Second-degree local branch model plus low-rank global generators.

    ``local_linear[0]`` multiplies ``theta_v[i]`` and ``local_linear[1]``
    multiplies ``theta_f[i]``.  ``local_mixed`` multiplies their product at the
    same node.  No cross-node local polynomial is materialized.
    """

    center: np.ndarray
    local_linear: np.ndarray
    local_mixed: np.ndarray
    global_generators: np.ndarray
    remainder_lo: np.ndarray
    remainder_hi: np.ndarray
    coordinate_names: tuple[str, ...]
    local_rank_hint: int | None = None
    global_generator_names: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        center = _array(self.center, name="center")
        if center.ndim != 2:
            raise ValueError("center must have shape (coordinate,node)")
        ncoord, nnode = center.shape
        local = _array(self.local_linear, shape=(2, ncoord, nnode), name="local_linear")
        mixed = _array(self.local_mixed, shape=(ncoord, nnode), name="local_mixed")
        global_modes = np.asarray(self.global_generators, dtype=np.float64)
        if global_modes.size == 0:
            global_modes = np.empty((0, ncoord, nnode), dtype=np.float64)
        global_modes = _array(global_modes, name="global_generators")
        if global_modes.ndim != 3 or global_modes.shape[1:] != center.shape:
            raise ValueError("global_generators must have shape (rank,coordinate,node)")
        rem_lo = _array(self.remainder_lo, shape=center.shape, name="remainder_lo")
        rem_hi = _array(self.remainder_hi, shape=center.shape, name="remainder_hi")
        if np.any(rem_lo > rem_hi):
            raise ValueError("remainder lower bound exceeds upper bound")
        names = tuple(str(item) for item in self.coordinate_names)
        if len(names) != ncoord or len(set(names)) != ncoord:
            raise ValueError("coordinate_names must be unique and match coordinate axis")
        global_names = tuple(str(item) for item in self.global_generator_names)
        if global_names and len(global_names) != len(global_modes):
            raise ValueError("global_generator_names length mismatch")
        if not global_names:
            global_names = tuple(f"global_{index}" for index in range(len(global_modes)))
        if self.local_rank_hint is not None and int(self.local_rank_hint) < 0:
            raise ValueError("local_rank_hint must be nonnegative")
        for name, value in (
            ("center", center),
            ("local_linear", local),
            ("local_mixed", mixed),
            ("global_generators", global_modes),
            ("remainder_lo", rem_lo),
            ("remainder_hi", rem_hi),
            ("coordinate_names", names),
            ("global_generator_names", global_names),
        ):
            object.__setattr__(self, name, value)

    @classmethod
    def point(cls, center: np.ndarray, *, coordinate_names: Iterable[str]) -> "SparseLocalTaylorModel":
        values = np.asarray(center, dtype=np.float64)
        if values.ndim != 2:
            raise ValueError("point center must be two-dimensional")
        return cls(
            center=values,
            local_linear=np.zeros((2,) + values.shape),
            local_mixed=np.zeros_like(values),
            global_generators=np.empty((0,) + values.shape),
            remainder_lo=np.zeros_like(values),
            remainder_hi=np.zeros_like(values),
            coordinate_names=tuple(coordinate_names),
            local_rank_hint=0,
        )

    @property
    def n_coordinate(self) -> int:
        return int(self.center.shape[0])

    @property
    def n_node(self) -> int:
        return int(self.center.shape[1])

    @property
    def global_rank(self) -> int:
        return int(self.global_generators.shape[0])

    @property
    def active_local_rank(self) -> int:
        if self.local_rank_hint is not None:
            return int(self.local_rank_hint)
        total = 0
        for node in range(self.n_node):
            block = self.local_linear[:, :, node].T
            scale = max(float(np.linalg.norm(block, ord=2)), np.finfo(float).tiny)
            total += int(np.linalg.matrix_rank(block, tol=1.0e-12 * scale))
        return total

    @property
    def storage_bytes(self) -> int:
        return int(
            self.center.nbytes
            + self.local_linear.nbytes
            + self.local_mixed.nbytes
            + self.global_generators.nbytes
            + self.remainder_lo.nbytes
            + self.remainder_hi.nbytes
        )

    def evaluate(
        self,
        *,
        theta_v: np.ndarray,
        theta_f: np.ndarray,
        eta: np.ndarray | None = None,
    ) -> np.ndarray:
        tv = np.asarray(theta_v, dtype=np.float64)
        tf = np.asarray(theta_f, dtype=np.float64)
        if tv.shape != (self.n_node,) or tf.shape != (self.n_node,):
            raise ValueError("local coordinate shape mismatch")
        if np.any(np.abs(tv) > 1.0) or np.any(np.abs(tf) > 1.0):
            raise ValueError("local coordinates leave [-1,1]")
        result = np.array(self.center, copy=True)
        result += self.local_linear[0] * tv[None, :]
        result += self.local_linear[1] * tf[None, :]
        result += self.local_mixed * (tv * tf)[None, :]
        if self.global_rank:
            if eta is None:
                global_coordinates = np.zeros(self.global_rank, dtype=np.float64)
            else:
                global_coordinates = np.asarray(eta, dtype=np.float64)
            if global_coordinates.shape != (self.global_rank,):
                raise ValueError("global coordinate shape mismatch")
            if np.any(np.abs(global_coordinates) > 1.0):
                raise ValueError("global coordinates leave [-1,1]")
            result += np.tensordot(global_coordinates, self.global_generators, axes=(0, 0))
        elif eta is not None and np.asarray(eta).size:
            raise ValueError("model has no global generators")
        return np.ascontiguousarray(result)

    def local_bilinear_bounds(self) -> tuple[np.ndarray, np.ndarray]:
        av, af = self.local_linear
        values = np.stack(
            [
                self.center - av - af + self.local_mixed,
                self.center - av + af - self.local_mixed,
                self.center + av - af - self.local_mixed,
                self.center + av + af + self.local_mixed,
            ],
            axis=0,
        )
        return np.min(values, axis=0), np.max(values, axis=0)

    def bounds(self) -> tuple[np.ndarray, np.ndarray]:
        lower, upper = self.local_bilinear_bounds()
        if self.global_rank:
            radius = np.sum(np.abs(self.global_generators), axis=0, dtype=np.float64)
            lower = lower - radius
            upper = upper + radius
        lower = lower + self.remainder_lo
        upper = upper + self.remainder_hi
        return np.ascontiguousarray(_down(lower)), np.ascontiguousarray(_up(upper))

    def with_remainder(self, lower: np.ndarray, upper: np.ndarray) -> "SparseLocalTaylorModel":
        return SparseLocalTaylorModel(
            center=self.center,
            local_linear=self.local_linear,
            local_mixed=self.local_mixed,
            global_generators=self.global_generators,
            remainder_lo=lower,
            remainder_hi=upper,
            coordinate_names=self.coordinate_names,
            local_rank_hint=self.local_rank_hint,
            global_generator_names=self.global_generator_names,
        )

    def scaled_and_shifted(self, *, scale: float, shift: np.ndarray) -> "SparseLocalTaylorModel":
        factor = float(scale)
        offset = np.asarray(shift, dtype=np.float64)
        if offset.shape != self.center.shape:
            raise ValueError("shift shape mismatch")
        if factor < 0.0 or not np.isfinite(factor):
            raise ValueError("scale must be finite and nonnegative")
        return SparseLocalTaylorModel(
            center=offset + factor * self.center,
            local_linear=factor * self.local_linear,
            local_mixed=factor * self.local_mixed,
            global_generators=factor * self.global_generators,
            remainder_lo=factor * self.remainder_lo,
            remainder_hi=factor * self.remainder_hi,
            coordinate_names=self.coordinate_names,
            local_rank_hint=self.local_rank_hint,
            global_generator_names=self.global_generator_names,
        )


__all__ = ["SparseLocalTaylorModel"]
