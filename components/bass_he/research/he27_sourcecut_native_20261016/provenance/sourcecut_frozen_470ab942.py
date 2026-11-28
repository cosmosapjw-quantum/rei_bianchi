"""Opt-in HE26 cut-source admission to HE25 fixed Killing-momentum modes.

Only newborn photons are redistributed.  The old HE25 Model, its existing
photons, native gas owner, cosmology and transport remain unchanged.  HE26's
positive child integrals are first summed in each birth direction and physical
threshold band.  A positive fixed-mode cubature then preserves all *admitted*
number, energy, species photoevent and photoheat moments in that band.  No
conditional kernel is attached as a separate gas rate.

This is a finite semi-discrete source model.  Child-local spectral shapes are
not preserved by fixed nodes; subsequent evolution is resolved by finite-m,
angle and time refinement, not certified by the source admission identities.
"""
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'he25_proper_birth_20261016' / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'he26_moving_cutoff_20261016' / 'src'))
from physics import Model, X_END, FITS, BIND_EV, shape, sigma_cm2
from portable_cut_core import geometry as donor_geometry


class SourceProjectionError(RuntimeError):
    """A positive source satisfying the donor moments was not represented."""


_CUTS = (13.6, 24.59, 54.42, 100.)
_CHILD_Z, _CHILD_W = np.polynomial.legendre.leggauss(8)


def _cut_children(panels, x, q, mu):
    """Batched HE26 children_of_cell formula, with angular weight one.

    Keep the same positive GL8 child rule and source/fit preimages.  Batching
    all children avoids recalculating GL8 nodes and Verner coefficients for
    every original panel at every proper-time birth evaluation.
    """
    g, jac = donor_geometry(x, q, mu)
    bounds = []
    for lo, hi in panels:
        left, right = max(lo, _CUTS[0] / g), min(hi, _CUTS[-1] / g)
        if right <= left:
            continue
        cut = sorted(set([left, right] + [float(t / g) for t in FITS[:, 0]
                                          if left < t / g < right]))
        bounds.extend(zip(cut[:-1], cut[1:]))
    if not bounds:
        return []
    intervals = np.array(bounds)
    mid = intervals.mean(axis=1)
    half = (intervals[:, 1] - intervals[:, 0]) / 2
    ref = mid[:, None] + half[:, None] * _CHILD_Z[None, :]
    physical = ref * g
    number = half[:, None] * jac * _CHILD_W[None, :] * shape(physical)
    sig = sigma_cm2(physical)
    n = number.sum(axis=1)
    u = np.sum(number * physical, axis=1)
    photo = np.sum(number[:, :, None] * sig, axis=1)
    heat = np.sum(number[:, :, None] * sig * (physical[:, :, None] - BIND_EV), axis=1)
    children = []
    for i, (lo, hi) in enumerate(bounds):
        low, high = lo * g, hi * g
        if not (n[i] > 0 and low - 3e-12 <= u[i] / n[i] <= high + 3e-12):
            raise SourceProjectionError('HE27_CHILD_SUPPORT')
        if np.any(photo[i] < 0) or np.any(heat[i] < 0):
            raise SourceProjectionError('HE27_NEGATIVE_CHILD_RATE')
        if any(low < t - 4e-12 and high > t + 4e-12 for t in FITS[:, 0]):
            raise SourceProjectionError('HE27_UNSPLIT_CHILD')
        children.append(dict(low_ev=low, high_ev=high, n=float(n[i]), u_ev=float(u[i]),
                             photo_cm2=photo[i].tolist(), heat_ev_cm2=heat[i].tolist()))
    return children


def _moments(n, energy, sigma):
    """Scaled, dimensionality-free rows; scale sigma before solving."""
    v = [np.ones_like(energy), energy / 25.]
    for j in range(n):
        v.append(sigma[:, j] * 1e18)
        v.append(sigma[:, j] * (energy - BIND_EV[j]) * 1e17)
    return np.array(v)


def _target(n, children):
    return np.array([
        sum(c['n'] for c in children),
        sum(c['u_ev'] for c in children) / 25.,
        *[v for j in range(n) for v in (
            sum(c['photo_cm2'][j] for c in children) * 1e18,
            sum(c['heat_ev_cm2'][j] for c in children) * 1e17,
        )],
    ])


def _positive_moment_fit(matrix, target, baseline):
    """Conservative positive correction around the original source quadrature.

    Weighted minimum-change corrections use strictly positive baseline modes as
    the metric.  Iterative active-set clamping is a real feasibility check; a
    return value is accepted only after every physical moment is re-evaluated.
    """
    if not (np.all(np.isfinite(matrix)) and np.all(np.isfinite(target)) and
            np.all(np.isfinite(baseline)) and np.all(baseline >= 0)):
        raise SourceProjectionError('HE27_SOURCE_NONFINITE_OR_NEGATIVE')
    free = baseline > 0
    if np.count_nonzero(free) < len(target):
        raise SourceProjectionError('HE27_SOURCE_INSUFFICIENT_ACTIVE_MODES')
    weights = baseline.copy()
    tol = 3e-13 * np.maximum(np.abs(target), 1e-14)
    for _ in range(matrix.shape[1] + 1):
        error = target - matrix @ weights
        if np.all(np.abs(error) <= tol):
            if np.any(weights < -1e-15 * max(weights.max(), 1.)):
                raise SourceProjectionError('HE27_SOURCE_NEGATIVE_FIT')
            return np.maximum(weights, 0.)
        if np.count_nonzero(free) < len(target):
            break
        a = matrix[:, free]
        metric = np.maximum(baseline[free], baseline[free].max() * 1e-14)
        weighted = a * np.sqrt(metric)
        correction, _, rank, _ = np.linalg.lstsq(weighted, error, rcond=1e-16)
        if rank < len(target):
            break
        delta = np.sqrt(metric) * correction
        proposed = weights[free] + delta
        if np.all(proposed >= 0):
            weights[free] = proposed
            continue
        old = weights[free]
        alpha = min(float(np.min(-old[delta < 0] / delta[delta < 0])), 1.)
        weights[free] = np.maximum(old + alpha * delta, 0.)
        free &= weights > 0
    defect = target - matrix @ weights
    raise SourceProjectionError(
        'HE27_SOURCE_MOMENT_CONE_INFEASIBLE '
        f'max_scaled_defect={float(np.max(np.abs(defect) / np.maximum(np.abs(target), 1e-14))):.9g}'
    )


class SourceCutModel(Model):
    """HE25 model with HE26 child-integrated, positive source admission."""

    def __init__(self, owner, m=4, angles=4, q=0., source_count=None):
        if source_count is None:
            super().__init__(owner, m=m, angles=angles, q=q)
        else:
            super().__init__(owner, m=m, angles=angles, q=q, source_count=source_count)
        self._groups = []
        angular_nodes, angular_weights = np.polynomial.legendre.leggauss(angles)
        e_nodes, _ = np.polynomial.legendre.leggauss(4)
        cursor = 0
        for mu, angular_weight in zip(angular_nodes, angular_weights / 2):
            end_factor = self.factor(X_END, mu)
            edges = sorted(set([*_CUTS, *[cut / end_factor for cut in _CUTS]]))
            panels = []
            for lo, hi in zip(edges[:-1], edges[1:]):
                parts = m if hi / lo > 1.01 else 1
                subedges = np.geomspace(lo, hi, parts + 1)
                for left, right in zip(subedges[:-1], subedges[1:]):
                    expected = (left + right) / 2 + (right - left) * e_nodes / 2
                    got = self.Eref[cursor:cursor + 4]
                    if len(got) != 4 or not np.array_equal(got, expected):
                        raise SourceProjectionError('HE27_HE25_GRID_IDENTITY')
                    panels.append((float(left), float(right)))
                    cursor += 4
            self._groups.append((float(mu), float(angular_weight),
                                 slice(cursor - 4 * len(panels), cursor), panels))
        if cursor != self.K:
            raise SourceProjectionError('HE27_HE25_GRID_LENGTH')
        self.last_source_moments = None

    def source_moments(self, t):
        """Raw HE26 target and actually admitted fixed-mode moments at birth."""
        x = self.x(t)
        energy, _, _ = self.geometry(t)
        sigma = sigma_cm2(energy)
        jac = np.exp(-3 * x) / self.factor(x, self.mu0) ** 2
        baseline = self.weights * shape(energy) * jac
        admitted = np.zeros(self.K)
        bands = []
        projected_groups = {}
        for mu, aw, group, panels in self._groups:
            indices = np.arange(group.start, group.stop)
            # ±mu have bitwise-identical HE25 geometry and mode ordering.
            key = abs(mu)
            if key in projected_groups:
                template, template_energy, template_sigma, template_kids = projected_groups[key]
                if (not np.array_equal(energy[group], template_energy) or
                        not np.array_equal(sigma[group], template_sigma)):
                    raise SourceProjectionError('HE27_ANGLE_PARITY_IDENTITY')
                admitted[group] = template * aw
                for band, child_count, target, actual in template_kids:
                    bands.append(dict(mu=mu, band=band, child_count=child_count,
                                      donor=(target * aw).tolist(),
                                      admitted=(actual * aw).tolist(),
                                      min_mode=float((template * aw).min())))
                continue
            kids = _cut_children(panels, x, self.q, mu)
            group_report = []
            for band in range(3):
                lo, hi = _CUTS[band:band + 2]
                child = [c for c in kids if
                         lo <= (c['low_ev'] + c['high_ev']) / 2 < hi]
                selected = indices[(energy[group] >= lo) &
                                   (energy[group] < hi if band < 2 else energy[group] <= hi)]
                if not child:
                    continue
                if not len(selected):
                    raise SourceProjectionError('HE27_SOURCE_EMPTY_THRESHOLD_BAND')
                number_species = band + 1
                target = _target(number_species, child)
                matrix = _moments(number_species, energy[selected], sigma[selected])
                try:
                    projected = _positive_moment_fit(matrix, target, baseline[selected] / aw)
                except SourceProjectionError as exc:
                    raise SourceProjectionError(f'{exc} mu={mu:.17g} band={band}') from exc
                admitted[selected] = projected * aw
                bands.append(dict(mu=mu, band=band, child_count=len(child),
                                  donor=(target * aw).tolist(),
                                  admitted=(matrix @ projected * aw).tolist(),
                                  min_mode=float((projected * aw).min())))
                group_report.append((band, len(child), target, matrix @ projected))
            projected_groups[key] = (admitted[group] / aw, energy[group].copy(),
                                     sigma[group].copy(), group_report)
        target = np.array([
            sum(b['donor'][0] for b in bands), sum(b['donor'][1] for b in bands) * 25.,
            *[sum(b['donor'][2 + 2 * j] / 1e18 for b in bands if j <= b['band'])
              for j in range(3)],
            *[sum(b['donor'][3 + 2 * j] / 1e17 for b in bands if j <= b['band'])
              for j in range(3)],
        ])
        actual = np.r_[sum(admitted), np.dot(admitted, energy),
                       (admitted[:, None] * sigma).sum(axis=0),
                       (admitted[:, None] * sigma * (energy[:, None] - BIND_EV)).sum(axis=0)]
        if np.any(admitted < 0) or np.any(actual[2:] < 0):
            raise SourceProjectionError('HE27_GLOBAL_SOURCE_POSITIVITY')
        if np.any(np.abs(actual - target) > 3e-13 * np.maximum(np.abs(target), 1e-30)):
            raise SourceProjectionError('HE27_GLOBAL_SOURCE_MOMENTS')
        self.last_source_moments = dict(
            donor_raw=target.tolist(), admitted_raw=actual.tolist(), bands=bands,
            max_relative_moment_error=float(np.max(
                np.abs(actual - target) / np.maximum(np.abs(target), 1e-30))),
            negative_mode_count=int(np.count_nonzero(admitted < 0)),
        )
        self.source_diagnostics = self.last_source_moments
        return admitted, self.last_source_moments

    def source(self, t):
        raw, report = self.source_moments(t)
        total = report['donor_raw'][0]
        if total <= 0:
            raise SourceProjectionError('HE27_SOURCE_SUPPORT_EMPTY')
        return raw / total * (self.H(t) * self.source_per_x)
