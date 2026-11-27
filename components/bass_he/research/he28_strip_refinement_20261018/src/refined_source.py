"""HE28 opt-in refinement of HE27's previously fixed cutoff strips.

The source law, native chemistry, moment constraints and time integrators are
inherited unchanged. ``strips`` changes the semi-discrete photon model, so old
native acceptance does not transfer. No remapping of existing photons occurs.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
from pathlib import Path
import json
import math
import sys
import time

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

RESEARCH = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RESEARCH / 'he27_sourcecut_native_20261016' / 'src'))
from sourcecut import SourceCutModel as ExactSource, SourceProjectionError
from sourcecut_fast import SourceCutModel as FastSource, _physical_birth_moments
from physics import Model, X_END, A_BIRTH, SOURCE_N_PER_H, Hubble, shape

CUTS = (13.6, 24.59, 54.42, 100.)


@dataclass(frozen=True)
class GridSpec:
    m: int = 4
    angles: int = 4
    q: float = 0.
    strips: int = 2

    def __post_init__(self):
        for field, allowed in (('m', (4, 8, 16)),
                               ('angles', (4, 8, 16, 32)),
                               ('strips', (1, 2, 4, 8, 16))):
            value = getattr(self, field)
            if type(value) is not int or value not in allowed:
                raise ValueError('HE28_GRID_' + field.upper())
        if not math.isfinite(self.q) or self.q not in (-.005, 0., .005):
            raise ValueError('HE28_GRID_Q')


@dataclass(frozen=True)
class Grid:
    energy: np.ndarray
    mu: np.ndarray
    weight: np.ndarray
    groups: tuple


def factor(x, mu, q):
    mu = np.asarray(mu)
    return np.sqrt((1 - mu**2) * np.exp(-2 * (1 + q) * x)
                   + mu**2 * np.exp(-2 * (1 - 2 * q) * x))


def build_grid(spec: GridSpec) -> Grid:
    """HE25/27 arithmetic exactly at strips=1, only narrow panels subdivided."""
    az, aw = np.polynomial.legendre.leggauss(spec.angles)
    ez, ew = np.polynomial.legendre.leggauss(4)
    energy, mus, weights, groups = [], [], [], []
    for mu, angular_weight in zip(az, aw / 2):
        g = factor(X_END, mu, spec.q)
        boundaries = sorted(set([*CUTS, *[c / g for c in CUTS]]))
        panels = []
        start = len(energy)
        for lo, hi in zip(boundaries[:-1], boundaries[1:]):
            narrow = hi / lo <= 1.01
            parts = spec.strips if narrow else spec.m
            edges = np.geomspace(lo, hi, parts + 1)
            for left, right in zip(edges[:-1], edges[1:]):
                ee = (left + right) / 2 + (right - left) * ez / 2
                energy.extend(ee)
                mus.extend([mu] * len(ee))
                weights.extend(ew * (right - left) / 2 * angular_weight)
                panels.append((float(left), float(right), narrow))
        groups.append((float(mu), float(angular_weight),
                       slice(start, len(energy)), tuple(panels)))
    arrays = tuple(np.asarray(v) for v in (energy, mus, weights))
    if not all(np.isfinite(v).all() for v in arrays) or np.any(arrays[2] <= 0):
        raise ValueError('HE28_NONPOSITIVE_GRID')
    return Grid(*arrays, tuple(groups))


class RefinedSourceModel(FastSource):
    """Same HE27 source algorithm on a genuinely strip-refined fixed grid.

    tabulate=False is for source-only checks. Actual adaptive native transport
    requires tabulate=True, to retain the parent's control of source jitter.
    Table memory and wall budgets fail explicitly, never shrink a resolution.
    """

    def __init__(self, owner, spec: GridSpec | None = None, source_count=None,
                 tabulate=True, source_table_nodes=512,
                 max_table_bytes=2 * 1024**3, max_table_wall_s=600.):
        self.spec = spec or GridSpec()
        spec = self.spec
        if type(tabulate) is not bool:
            raise ValueError('HE28_TABULATE_BOOL')
        if type(source_table_nodes) is not int or source_table_nodes not in (256, 512, 1024):
            raise ValueError('HE28_SOURCE_TABLE_SCOPE')
        if type(max_table_bytes) is not int or max_table_bytes < 1:
            raise ValueError('HE28_TABLE_MEMORY_DOMAIN')
        if not math.isfinite(max_table_wall_s) or max_table_wall_s <= 0:
            raise ValueError('HE28_TABLE_WALL_DOMAIN')
        source_count = SOURCE_N_PER_H if source_count is None else source_count
        if not math.isfinite(source_count) or source_count < 0:
            raise ValueError('HE28_SOURCE_COUNT_DOMAIN')
        # Base clock, state and physics are reused, no old source tables built.
        Model.__init__(self, owner, m=spec.m, angles=spec.angles,
                       q=spec.q, source_count=source_count)
        grid = build_grid(spec)
        self.Eref, self.mu0, self.weights = grid.energy, grid.mu, grid.weight
        self.K = len(self.Eref)
        self._groups = [(mu, aw, sl, [(a, b) for a, b, _ in panels])
                        for mu, aw, sl, panels in grid.groups]
        self.k_perp = A_BIRTH * self.Eref * np.sqrt(1 - self.mu0**2)
        self.k_parallel = A_BIRTH * self.Eref * self.mu0
        times = []
        for e, mu in zip(self.Eref, self.mu0):
            for cut in CUTS:
                if e > cut and e * self.factor(X_END, mu) < cut:
                    root = brentq(lambda x: e * self.factor(x, mu) - cut,
                                  0, X_END, xtol=1e-19, rtol=1e-14)
                    times.append(quad(lambda x: 1 / Hubble(x), 0, root,
                                      epsabs=.0001, epsrel=3e-14)[0])
        self.breakpoints = sorted(set(times))
        ps = source_count * self.weights * shape(self.Eref)
        if ps.sum() > 0:
            ps = ps / ps.sum() * max(source_count, 1e-12)
        else:
            ps = self.weights / self.weights.sum() * 1e-12
        self.scale = np.r_[1e-5, 1e-5, 1e-12, self.g0[3], np.maximum(ps, 1e-18),
                           [max(source_count, 1e-12), max(source_count*25, 1e-11)],
                           np.full(3, max(source_count, 1e-12)),
                           np.full(3, max(source_count*10, 1e-11)),
                           [1e-9, 1e-9, 1e-10, 1e-6], np.full(3, 1e-10),
                           np.full(3, 1e-10), 1e-10]
        self.source_table_nodes = source_table_nodes
        self._cut_bounds = np.array([0., *self.breakpoints, self.t_end])
        if np.any(np.diff(self._cut_bounds) <= 0):
            raise SourceProjectionError('HE28_BREAKPOINT_ORDER')
        long_intervals = np.diff(self._cut_bounds) > 1e-6 * self.t_end
        # Includes table values, time vectors, and one temporary interval copy.
        self.table_estimate_bytes = int((int(sum(long_intervals)) + 1)
                                       * (source_table_nodes + 1) * (self.K + 1) * 8)
        if tabulate and self.table_estimate_bytes > max_table_bytes:
            raise MemoryError(f'HE28_TABLE_BUDGET {self.table_estimate_bytes}>{max_table_bytes}')
        self._source_tables = {}
        self._active_interval = None
        self._cached_source_key = self._cached_source_flux = None
        self.max_source_moment_error = 0.
        self.last_source_moments = self.source_diagnostics = None
        self._source_mask = self._sigma_mask = None
        p64, p128 = _physical_birth_moments(64), _physical_birth_moments(128)
        error = np.max(np.abs(p64 - p128) / np.maximum(abs(p128), 1e-30))
        if error > 5e-14:
            raise SourceProjectionError('HE28_BIRTH_REFERENCE_FAILURE')
        self._physical_birth_band_moments = p128
        self._physical_birth_moments = p128.sum(axis=0)
        self.physical_birth_quadrature_relative = float(error)
        self._mode_angular_index = np.empty(self.K, dtype=np.intp)
        for i, (_, _, sl, _) in enumerate(self._groups):
            self._mode_angular_index[sl] = i
        digest = sha256(json.dumps(asdict(spec), sort_keys=True).encode())
        digest.update(self._cut_bounds.astype('<f8').tobytes())
        digest.update(np.array([self.source_count, source_table_nodes], dtype='<f8').tobytes())
        self.tabulated = tabulate
        start = time.monotonic()
        if tabulate:
            for i, (left, right) in enumerate(zip(self._cut_bounds[:-1], self._cut_bounds[1:])):
                if not long_intervals[i]:
                    continue
                guard = 1e-10 * (right - left)
                ts = np.linspace(left + guard, right - guard, source_table_nodes + 1)
                values = np.empty((len(ts), self.K))
                for j, t in enumerate(ts):
                    if time.monotonic() - start > max_table_wall_s:
                        raise TimeoutError('HE28_TABLE_WALL_BUDGET')
                    values[j] = ExactSource.source_moments(self, float(t))[0]
                if not np.isfinite(values).all() or np.any(values < 0):
                    raise SourceProjectionError('HE28_TABLE_POSITIVITY')
                self._source_tables[i] = (ts, values)
                digest.update(np.array([i], dtype='<i8').tobytes())
                digest.update(ts.astype('<f8').tobytes())
                digest.update(values.astype('<f8').tobytes())
        digest.update(bytes([tabulate]))
        self.source_table_sha256 = digest.hexdigest()
        self.source_table_diagnostics = dict(
            spec=asdict(spec), nodes_per_long_interval=source_table_nodes,
            original_breakpoints=len(self.breakpoints),
            tabulated_intervals=len(self._source_tables),
            direct_crossing_intervals=len(self._cut_bounds)-1-len(self._source_tables),
            estimated_bytes=self.table_estimate_bytes,
            build_wall_s=time.monotonic()-start,
            scope='new semi-discrete model, native validation separate')
