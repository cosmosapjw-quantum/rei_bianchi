"""Opt-in HE29 algebra and exact-time reuse; the original model stays available.

The gas finite differences, reaction owner, source, masks and tolerances are
unchanged.  Only construction/storage of the same physical Jacobian changes.
Packing is gas[n,4], photon[12,K], both C contiguous, n=K+4+19.  The photon
rows are gas0..3, photon diagonal, ledger2..7, ledger10.  Native kernels must
accumulate gas columns first, then photon columns in their original order.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import sys

import numpy as np
from scipy.sparse import csr_matrix

RESEARCH = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RESEARCH / "he28_strip_refinement_20261018" / "src"))
from refined_source import RefinedSourceModel
from physics import BIND_EV, Y_HE, admissible

LEDGER_COUNT = 19
PHOTON_LEDGER_ROWS = (2, 3, 4, 5, 6, 7, 10)


def _finite_vector(value, size, label):
    a = np.asarray(value, dtype=np.float64)
    if a.shape != (size,) or not np.isfinite(a).all():
        raise ValueError("HE29_OPT_" + label)
    return a


@dataclass(frozen=True)
class PackedJacobian:
    """Owned, immutable physical coefficients; no scaled or rounded cache key."""

    gas: np.ndarray
    photon: np.ndarray

    def __post_init__(self):
        gas = np.array(self.gas, dtype=np.float64, order="C", copy=True)
        photon = np.array(self.photon, dtype=np.float64, order="C", copy=True)
        if (gas.ndim != 2 or gas.shape[1] != 4 or gas.shape[0] <= 23
                or photon.shape != (12, gas.shape[0] - 23)
                or not np.isfinite(gas).all() or not np.isfinite(photon).all()):
            raise ValueError("HE29_OPT_PACKED_SHAPE_OR_FINITE")
        gas.flags.writeable = photon.flags.writeable = False
        object.__setattr__(self, "gas", gas)
        object.__setattr__(self, "photon", photon)

    @property
    def n(self):
        return self.gas.shape[0]

    @property
    def k(self):
        return self.n - 23

    @property
    def nbytes(self):
        return self.gas.nbytes + self.photon.nbytes

    def csr(self):
        """Canonical CSR without per-photon Python sparse assignments.

        Explicit zeros are removed so column order and stored entries agree
        with the original LIL->CSR path.  No duplicate row/column pair exists.
        All returned arrays are owned by the new matrix.
        """
        n, k = self.n, self.k
        modes = np.arange(k, dtype=np.int32)
        ledger = k + 4
        rows = np.concatenate((np.repeat(np.arange(n, dtype=np.int32), 4),
            np.repeat(np.arange(4, dtype=np.int32), k), 4 + modes,
            np.repeat(ledger + np.array(PHOTON_LEDGER_ROWS, dtype=np.int32), k)))
        cols = np.concatenate((np.tile(np.arange(4, dtype=np.int32), n),
                               np.tile(4 + modes, 12)))
        data = np.concatenate((self.gas.ravel(), self.photon.ravel()))
        keep = data != 0.
        rows, cols, data = rows[keep], cols[keep], data[keep]
        order = np.lexsort((cols, rows))
        rows, cols, data = rows[order], cols[order], data[order]
        indptr = np.r_[0, np.cumsum(np.bincount(rows, minlength=n))]
        return csr_matrix((data, cols, indptr), shape=(n, n))


def prepare_jacobian(model, t, y):
    """Evaluate the exact original five RHS calls and pack analytic columns.

    The K three-term thermal dot products deliberately use the original
    np.dot call.  Replacing those by a different reduction is unnecessary
    for removing Python sparse insertion and would need separate evidence.
    """
    k = int(model.K)
    n = k + 23
    t = float(t)
    if not math.isfinite(t) or k < 1:
        raise ValueError("HE29_OPT_JACOBIAN_DOMAIN")
    y = _finite_vector(y, n, "STATE")
    scale = _finite_vector(model.scale, n, "SCALE")
    if np.any(scale <= 0):
        raise ValueError("HE29_OPT_SCALE")
    base = _finite_vector(model.rhs(t, y), n, "RHS")
    gas = np.empty((n, 4))
    for j in range(4):
        h = 1e-5 * max(abs(y[j]), scale[j])
        trial = y.copy()
        trial[j] += h
        if not admissible(trial[:4]):
            h = -h
            trial[j] = y[j] + h
        gas[:, j] = (_finite_vector(model.rhs(t, trial), n, "TRIAL_RHS") - base) / h
    _, _, energy, energy_dot, lam = model.rates(t, y[:4])
    energy = _finite_vector(energy, k, "ENERGY")
    energy_dot = _finite_vector(energy_dot, k, "ENERGY_DOT")
    lam = np.asarray(lam, dtype=np.float64)
    if lam.shape != (k, 3) or not np.isfinite(lam).all():
        raise ValueError("HE29_OPT_LAMBDA")
    photon = np.empty((12, k))
    photon[0] = lam[:, 0]
    photon[1] = (lam[:, 1] - lam[:, 2]) / Y_HE
    photon[2] = lam[:, 2] / Y_HE
    photon[3] = [np.dot(lam[j], energy[j] - BIND_EV) for j in range(k)]
    # Preserve the original sum(lam[j]) order and its finite trial domain.
    # Physical admissibility remains the original native owner's contract.
    photon[4] = -((lam[:, 0] + lam[:, 1]) + lam[:, 2])
    photon[5:8] = lam.T
    photon[8:11] = (lam * (energy[:, None] - BIND_EV)).T
    photon[11] = -energy_dot
    return PackedJacobian(gas, photon)


class OptimizedRefinedSourceModel(RefinedSourceModel):
    """Frozen HE28 grid/source, with one-entry exact-time geometry caches.

    Construction, including the full source-table byte digest, uses the parent
    path.  Caching starts only afterwards.  Every set_interval invalidates
    caches before and after selecting the parent's one-sided masks.  The
    native point evaluator and its per-call evidence policy are untouched.
    """

    def __init__(self, *args, **kwargs):
        self._opt_ready = False
        self._opt_epoch = 0
        self._opt_cache = {}
        self.optimization_counts = dict(clock_hits=0, clock_misses=0,
            hubble_hits=0, hubble_misses=0, geometry_hits=0, geometry_misses=0,
            sigma_hits=0, sigma_misses=0, packed_jacobians=0)
        super().__init__(*args, **kwargs)
        for name in ("Eref", "mu0", "weights"):
            getattr(self, name).flags.writeable = False
        self._opt_ready = True
        self._opt_cache.clear()

    def _memo(self, name, t, evaluate, *, geometry=False):
        if not self._opt_ready:
            return evaluate()
        t = float(t)
        if not math.isfinite(t):
            raise ValueError("HE29_OPT_TIME")
        key = (t.hex(), self._opt_epoch)
        if geometry:
            key += (float(self.q).hex(), id(self.Eref), id(self.mu0))
        entry = self._opt_cache.get(name)
        if entry is not None and entry[0] == key:
            self.optimization_counts[name + "_hits"] += 1
            return entry[1]
        value = evaluate()
        if isinstance(value, np.ndarray):
            value.flags.writeable = False
        elif isinstance(value, tuple):
            for item in value:
                if isinstance(item, np.ndarray):
                    item.flags.writeable = False
        self._opt_cache[name] = (key, value)
        self.optimization_counts[name + "_misses"] += 1
        return value

    def x(self, t):
        return self._memo("clock", t, lambda: super(OptimizedRefinedSourceModel, self).x(t))

    def H(self, t):
        return self._memo("hubble", t, lambda: super(OptimizedRefinedSourceModel, self).H(t))

    def geometry(self, t):
        return self._memo("geometry", t,
                         lambda: super(OptimizedRefinedSourceModel, self).geometry(t),
                         geometry=True)

    def sigma(self, t):
        return self._memo("sigma", t,
                         lambda: super(OptimizedRefinedSourceModel, self).sigma(t),
                         geometry=True)

    def set_interval(self, left, right):
        self._opt_epoch += 1
        self._opt_cache.clear()
        super().set_interval(left, right)
        self._opt_cache.clear()

    def prepare_jacobian(self, t, y):
        self.optimization_counts["packed_jacobians"] += 1
        return prepare_jacobian(self, t, y)

    def jac(self, t, y):
        return self.prepare_jacobian(t, y).csr()
