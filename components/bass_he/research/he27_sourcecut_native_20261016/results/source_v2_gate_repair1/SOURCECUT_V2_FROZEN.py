"""Event-segmented smooth source admission for the opt-in HE27 lane.

The original sourcecut.py is an immutable exact-moment C5 construction.  Its
fixed-node moment fit is ill-conditioned (HeII band ~2.7e9), causing binary64
mode jitter that stalled independent adaptive ODE solvers despite correct
instantaneous source moments.  This version tabulates *that same* positive
source on each original physical cutoff interval and linearly interpolates
only within an interval.  Tiny crossing intervals use the original direct
fit.  Every emitted source evaluation is checked against the unchanged HE26
eight-moment donor gate; this introduces a measured source-time interpolation
error, never a new source law or relaxed physical tolerance.
"""
from hashlib import sha256

import numpy as np

from sourcecut import SourceCutModel as _ExactSourceCutModel
from sourcecut import (SourceProjectionError, BIND_EV, sigma_cm2, shape,
                       _moments, _positive_moment_fit)


class SourceCutModel(_ExactSourceCutModel):
    """Positive piecewise-linear source within the original cutoff intervals."""

    def __init__(self, owner, m=4, angles=4, q=0., source_count=None,
                 source_table_nodes=512):
        if source_table_nodes not in (256, 512, 1024):
            raise ValueError('HE27_SOURCE_TABLE_SCOPE')
        super().__init__(owner, m=m, angles=angles, q=q,
                         source_count=source_count)
        self.source_table_nodes = source_table_nodes
        self._cut_bounds = np.array([0., *self.breakpoints, self.t_end])
        if np.any(np.diff(self._cut_bounds) <= 0):
            raise SourceProjectionError('HE27_BREAKPOINT_IDENTITY')
        self._source_tables = {}
        self._active_interval = None
        digest = sha256()
        digest.update(self._cut_bounds.astype('<f8').tobytes())
        digest.update(np.array([m, angles, q, self.source_count,
                                source_table_nodes], dtype='<f8').tobytes())
        for i, (left, right) in enumerate(zip(self._cut_bounds[:-1],
                                               self._cut_bounds[1:])):
            if right - left <= 1e-6 * self.t_end:
                continue
            guard = 1e-10 * (right - left)
            times = np.linspace(left + guard, right - guard,
                                source_table_nodes + 1)
            values = np.array([super(SourceCutModel, self).source_moments(t)[0]
                               for t in times])
            if not np.all(np.isfinite(values)) or np.any(values < 0):
                raise SourceProjectionError('HE27_SOURCE_TABLE_POSITIVITY')
            self._source_tables[i] = (times, values)
            digest.update(np.array([i], dtype='<i8').tobytes())
            digest.update(times.astype('<f8').tobytes())
            digest.update(values.astype('<f8').tobytes())
        self.source_table_sha256 = digest.hexdigest()
        self.source_table_diagnostics = dict(nodes_per_long_interval=source_table_nodes,
            original_breakpoints=len(self.breakpoints),
            tabulated_intervals=len(self._source_tables),
            direct_crossing_intervals=len(self._cut_bounds)-1-len(self._source_tables),
            max_interval_fraction_for_direct=1e-6,
            endpoint_guard_fraction=1e-10)
        self.max_source_moment_error = 0.
        self.last_source_moments = None
        self.source_diagnostics = None
        self._cached_source_key = None
        self._cached_source_flux = None

    def set_interval(self, left, right):
        super().set_interval(left, right)
        self._active_interval = self._locate((left + right) / 2)
        self._cached_source_key = None
        self._cached_source_flux = None

    def _locate(self, t):
        return int(np.clip(np.searchsorted(self._cut_bounds, t, side='right') - 1,
                           0, len(self._cut_bounds) - 2))

    def _one_sided_endpoint(self, t):
        """Admit the continuous donor on HE25's selected one-sided node mask."""
        _, report = super().source_moments(t)
        energy = self.geometry(t)[0]
        sigma = self.sigma(t)
        x = self.x(t)
        jac = np.exp(-3 * x) / self.factor(x, self.mu0) ** 2
        baseline = self.weights * shape(energy) * jac * self._source_mask
        admitted = np.zeros(self.K)
        targets = {(b['mu'], b['band']): np.asarray(b['donor'])
                   for b in report['bands']}
        for mu, aw, group, _ in self._groups:
            indices = np.arange(group.start, group.stop)
            active_species = np.count_nonzero(sigma[group] > 0, axis=1)
            for band in range(3):
                target = targets.get((mu, band))
                if target is None:
                    continue
                selected = indices[(active_species == band + 1) &
                                   self._source_mask[group]]
                if not len(selected):
                    raise SourceProjectionError('HE27_ONE_SIDED_EMPTY_BAND')
                matrix = _moments(band + 1, energy[selected], sigma[selected])
                admitted[selected] = _positive_moment_fit(
                    matrix, target, baseline[selected])
        return admitted

    def _raw_source(self, t):
        index = self._locate(t)
        if self._active_interval is not None:
            active = self._active_interval
            if self._cut_bounds[active] <= t <= self._cut_bounds[active + 1]:
                index = active
                if np.any(self._cut_bounds[1:-1] == t):
                    return self._one_sided_endpoint(t)
        table = self._source_tables.get(index)
        if table is None:
            return super().source_moments(t)[0]
        times, values = table
        if t <= times[0]:
            return values[0].copy()
        if t >= times[-1]:
            return values[-1].copy()
        low = min(int(np.searchsorted(times, t, side='right')) - 1,
                  len(times) - 2)
        fraction = (t - times[low]) / (times[low + 1] - times[low])
        return (1. - fraction) * values[low] + fraction * values[low + 1]

    def source_moments(self, t):
        """Check interpolated admission against fresh HE26 donor moments."""
        admitted = self._raw_source(t)
        _, direct = super().source_moments(t)
        target = np.asarray(direct['donor_raw'])
        energy = self.geometry(t)[0]
        active = self._active_interval
        if active is not None and self._cut_bounds[active] <= t <= self._cut_bounds[active + 1]:
            # HE25 owns the exact one-sided fit mask at a crossing endpoint.
            sigma = self.sigma(t)
        else:
            sigma = sigma_cm2(energy)
        actual = np.r_[sum(admitted), np.dot(admitted, energy),
                       (admitted[:, None] * sigma).sum(axis=0),
                       (admitted[:, None] * sigma *
                        (energy[:, None] - BIND_EV)).sum(axis=0)]
        relative = np.abs(actual - target) / np.maximum(np.abs(target), 1e-30)
        if (not np.all(np.isfinite(admitted)) or np.any(admitted < 0) or
                np.any(actual[2:] < 0)):
            raise SourceProjectionError('HE27_V2_SOURCE_POSITIVITY')
        if np.max(relative) > 3e-13:
            raise SourceProjectionError(
                f'HE27_V2_SOURCE_MOMENTS max_relative={np.max(relative):.9g} '
                f'interval={self._locate(t)}')
        report = dict(donor_raw=target.tolist(), admitted_raw=actual.tolist(),
                      max_relative_moment_error=float(np.max(relative)),
                      negative_mode_count=0, interval=self._locate(t),
                      source_table_sha256=self.source_table_sha256)
        self.max_source_moment_error = max(self.max_source_moment_error,
                                           report['max_relative_moment_error'])
        self.last_source_moments = report
        self.source_diagnostics = report
        return admitted, report

    def source(self, t):
        key = (self._active_interval, float(t))
        if key == self._cached_source_key:
            return self._cached_source_flux.copy()
        raw, report = self.source_moments(t)
        total = float(sum(raw))
        if total <= 0:
            raise SourceProjectionError('HE27_V2_SOURCE_SUPPORT_EMPTY')
        flux = raw / total * (self.H(t) * self.source_per_x)
        self._cached_source_key = key
        self._cached_source_flux = flux.copy()
        return flux
