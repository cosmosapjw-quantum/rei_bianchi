"""Analytic donor-moment validation for the unchanged HE27 v3 source flux.

For fixed birth direction nu, E=P*G and J=d(E,mu)/d(P,nu).  Hence
J dP=(J/G)dE.  The isotropic physical birth spectrum has one fixed set of
eight moments, integrated once in E across the H/He fit thresholds.  Only
the positive angular factor J/G changes with proper time and signed q.

The v3 source vector, cutoff intervals, one-sided endpoint rule, photon
transport and native chemistry are inherited unchanged.  This module
replaces only the expensive repeated donor-validation calculation; it retains
the exact original 3e-13 eight-moment admission gate.
"""
import numpy as np

from sourcecut_v3 import SourceCutModel as _V3SourceCutModel
from sourcecut import SourceProjectionError, BIND_EV, sigma_cm2, shape
from portable_cut_core import geometry as donor_geometry


_SOURCE_EDGES = (13.6, 24.59, 54.42, 100.)


def _physical_birth_moments(order):
    """Raw N,U,three sigma and three physical heating moments at birth."""
    z, w = np.polynomial.legendre.leggauss(order)
    result = np.zeros((3, 8))
    for band, (lo, hi) in enumerate(zip(_SOURCE_EDGES[:-1], _SOURCE_EDGES[1:])):
        half = (hi - lo) / 2
        energy = (lo + hi) / 2 + half * z
        photons = half * w * shape(energy)
        sigma = sigma_cm2(energy)
        result[band, :2] = [sum(photons), np.dot(photons, energy)]
        result[band, 2:5] = (photons[:, None] * sigma).sum(axis=0)
        result[band, 5:8] = (photons[:, None] * sigma *
                             (energy[:, None] - BIND_EV)).sum(axis=0)
    return result


class SourceCutModel(_V3SourceCutModel):
    """The v3 source operator with a factored, independently checked donor."""

    def __init__(self, owner, m=4, angles=4, q=0., source_count=None,
                 source_table_nodes=512):
        super().__init__(owner, m=m, angles=angles, q=q,
                         source_count=source_count,
                         source_table_nodes=source_table_nodes)
        physical64 = _physical_birth_moments(64)
        physical128 = _physical_birth_moments(128)
        difference = (np.abs(physical128 - physical64) /
                      np.maximum(np.abs(physical128), 1e-30))
        if np.max(difference) > 5e-14:
            raise SourceProjectionError('HE27_PHYSICAL_BIRTH_QUADRATURE')
        self._physical_birth_band_moments = physical128
        self._physical_birth_moments = physical128.sum(axis=0)
        self.physical_birth_quadrature_relative = float(np.max(difference))
        self._mode_angular_index = np.empty(self.K, dtype=np.intp)
        for angle_index, (_, _, group, _) in enumerate(self._groups):
            self._mode_angular_index[group] = angle_index

    def source_moments(self, t):
        """Validate exactly the inherited raw source against factored HE26 N/U."""
        admitted = self._raw_source(t)
        x = self.x(t)
        factors = np.empty(self.angles)
        energy = self.geometry(t)[0]
        active = self._active_interval
        if (active is not None and
                self._cut_bounds[active] <= t <= self._cut_bounds[active + 1]):
            sigma = self.sigma(t)
            support = self._source_mask
        else:
            sigma = sigma_cm2(energy)
            support = (energy >= 13.6) & (energy <= 100.)
        for i, (mu, angular_weight, _, _) in enumerate(self._groups):
            g, jac = donor_geometry(x, self.q, mu)
            factors[i] = angular_weight * jac / g
        target = self._physical_birth_moments * sum(factors)
        band_index = np.count_nonzero(sigma > 0, axis=1) - 1
        valid = support & (band_index >= 0)
        code = 3 * self._mode_angular_index[valid] + band_index[valid]
        photons = admitted[valid]
        e = energy[valid]
        s = sigma[valid]
        def grouped(weights):
            return np.bincount(code, weights=weights,
                               minlength=3 * self.angles).reshape(self.angles, 3)
        local = np.stack((grouped(photons), grouped(photons * e),
                          *(grouped(photons * s[:, j]) for j in range(3)),
                          *(grouped(photons * s[:, j] * (e - BIND_EV[j]))
                            for j in range(3))), axis=-1)
        expected = factors[:, None, None] * self._physical_birth_band_moments[None, :, :]
        max_local = float(np.max(np.abs(local - expected) /
                                 np.maximum(np.abs(expected), 1e-30)))
        actual = np.r_[sum(admitted), np.dot(admitted, energy),
                       (admitted[:, None] * sigma).sum(axis=0),
                       (admitted[:, None] * sigma *
                        (energy[:, None] - BIND_EV)).sum(axis=0)]
        relative = np.abs(actual - target) / np.maximum(np.abs(target), 1e-30)
        if (not np.all(np.isfinite(admitted)) or np.any(admitted < 0) or
                np.any(actual[2:] < 0)):
            raise SourceProjectionError('HE27_FAST_SOURCE_POSITIVITY')
        if np.max(relative) > 3e-13 or max_local > 3e-13:
            raise SourceProjectionError(
                f'HE27_FAST_SOURCE_MOMENTS max_relative={np.max(relative):.9g} '
                f'max_angle_band_relative={max_local:.9g} '
                f'interval={self._locate(t)}')
        report = dict(donor_raw=target.tolist(), admitted_raw=actual.tolist(),
                      max_relative_moment_error=float(np.max(relative)),
                      max_angle_band_relative_error=max_local,
                      negative_mode_count=0, interval=self._locate(t),
                      source_table_sha256=self.source_table_sha256)
        self.max_source_moment_error = max(self.max_source_moment_error,
                                           report['max_relative_moment_error'])
        self.last_source_moments = report
        self.source_diagnostics = report
        return admitted, report
