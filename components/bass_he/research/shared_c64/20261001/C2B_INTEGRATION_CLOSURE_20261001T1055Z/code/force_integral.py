"""Geometry-balanced value-only Coulomb force quadrature on frozen states.

Subdivision changes no state or integrand. Original knot cells are retained as
unions of rectangles, with a two-triangle Duffy map at either Coulomb corner.
The native backend is the pinned C2 Fortran ABI, with no implicit fallback.
"""
from __future__ import annotations

import math

import numpy as np
from numpy.polynomial.legendre import leggauss

import prolate_fast as fast


def rectangles(xe, ye, variant='balanced'):
    """Return deterministic (xl,xh,yl,yh) cells and geometry-only metadata.

At each cell d = (xl-1) + min(yl+1, 1-yh) is its minimum distance to
either Coulomb corner in the positive (xi-1, 1 +/- eta) coordinates.
Bisect its longer direction until max(hx,hy) <= 2*(d+min(hx,hy)).
"""
    if variant not in ('balanced', 'original'):
        raise ValueError('variant must be explicitly balanced or original')
    xe, ye = np.asarray(xe, dtype=float), np.asarray(ye, dtype=float)
    if any(e.ndim != 1 or len(e) < 2 or not np.all(np.isfinite(e)) or
           np.any(np.diff(e) <= 0) for e in (xe, ye)):
        raise ValueError('finite strictly increasing edge vectors required')
    if xe[0] != 1 or ye[0] != -1 or ye[-1] != 1:
        raise ValueError('complete finite prolate domain edges required')
    original_cells = (len(xe)-1)*(len(ye)-1)
    if original_cells > 50000:
        raise RuntimeError('original geometry exceeds fixed 50000 cell cap')
    cells, splits, maximum_depth = [], 0, 0
    for xl, xh in zip(xe[:-1], xe[1:]):
        for yl, yh in zip(ye[:-1], ye[1:]):
            stack = [(float(xl), float(xh), float(yl), float(yh), 0)]
            while stack:
                a, b, c, d, depth = stack.pop()
                hx, hy = b-a, d-c
                distance = (a-1) + min(c+1, 1-d)
                both_corners = a == 1 and c == -1 and d == 1
                if variant == 'original' or (not both_corners and
                                             max(hx, hy) <= 2*(distance+min(hx, hy))):
                    cells.append((a, b, c, d))
                    maximum_depth = max(maximum_depth, depth)
                    continue
                if depth >= 32:
                    raise RuntimeError('geometry subdivision exceeded fixed depth cap')
                splits += 1
                if original_cells+splits > 50000:
                    raise RuntimeError('geometry subdivision exceeded fixed 50000 cell cap')
                if hx >= hy and not both_corners:
                    mid = a+(b-a)/2
                    if mid == a or mid == b:
                        raise FloatingPointError('radial subdivision reached float resolution')
                    stack.extend(((mid, b, c, d, depth+1), (a, mid, c, d, depth+1)))
                else:
                    mid = c+(d-c)/2
                    if mid == c or mid == d:
                        raise FloatingPointError('angular subdivision reached float resolution')
                    stack.extend(((a, b, mid, d, depth+1), (a, b, c, mid, depth+1)))
    return cells, {'variant': variant, 'original_cells': original_cells,
                   'rectangles': len(cells), 'splits': splits,
                   'maximum_depth': maximum_depth, 'geometry_ratio': 2.0}


def _patch_setup(xe, ye, order, variant):
    if isinstance(order, bool) or not isinstance(order, int) or order < 2:
        raise ValueError('quadrature order must be integer >=2')
    cells, metadata = rectangles(xe, ye, variant)
    duffy_cells = sum(xl == 1 and (yl == -1 or yh == 1) for xl,xh,yl,yh in cells)
    patches = len(cells)+duffy_cells
    if patches*order*order > np.iinfo(np.int32).max:
        raise ValueError('native ABI point count overflow')
    metadata.update({'duffy_cells': duffy_cells, 'patches': patches,
                     'points': patches*order*order, 'order': order})
    return cells, metadata


def _patch_iterator(cells, order):
    """Yield exactly the parent point order, one rectangle/triangle at a time."""
    q, w = leggauss(order)
    t, w = (q+1)/2, w/2
    T, U = np.meshgrid(t, t, indexing='ij')
    W = w[:, None]*w[None, :]
    for xl, xh, yl, yh in cells:
        hx, hy = xh-xl, yh-yl
        corner = xl == 1 and (yl == -1 or yh == 1)
        if corner:
            for a, b in ((hx*T, hy*T*U), (hx*T*U, hy*T)):
                yield (xl+a).ravel(), (yl+b if yl == -1 else yh-b).ravel(), (hx*hy*T*W).ravel()
        else:
            yield (xl+hx*T).ravel(), (yl+hy*U).ravel(), (hx*hy*W).ravel()


def _join_patches(patches):
    xi, eta, weights = (np.concatenate([p[j] for p in patches]) for j in range(3))
    if np.any(xi <= 1) or np.any(np.abs(eta) >= 1):
        raise FloatingPointError('open quadrature nodes reached coordinate endpoints')
    counts = np.array([len(p[0]) for p in patches], dtype=np.int32)
    return xi, eta, weights, counts


def patches_from_edges(xe, ye, order, variant='balanced'):
    """Full materializer for small manufactured reference tests only."""
    cells, metadata = _patch_setup(xe, ye, order, variant)
    return (*_join_patches(list(_patch_iterator(cells, order))), metadata)


def patch_batches(cells, order, batch_patches=32):
    """Bound working arrays to at most 64 patches, default 32."""
    if (isinstance(batch_patches, bool) or not isinstance(batch_patches, int)
            or not 1 <= batch_patches <= 64):
        raise ValueError('batch_patches must be integer in [1,64]')
    batch = []
    for item in _patch_iterator(cells, order):
        batch.append(item)
        if len(batch) == batch_patches:
            yield _join_patches(batch)
            batch.clear()
    if batch:
        yield _join_patches(batch)


def torque(g, b, order=12, backend='native', variant='balanced', batch_patches=32):
    """Independent, value-only TA/TB and commutator-derived LO/LB.

No gap*dipole replacement, state derivatives, eigensolves, fitting or tolerance
adaptation enters the force integrals. The positive energy gap is applied only
after integrating TA and TB, as in C2.
"""
    fast._compatible(g, b)
    fast._backend(backend)
    delta = b.energy-g.energy
    if not np.isfinite(delta) or delta <= 0:
        raise ValueError('positive isolated bright-ground gap required')
    xe = np.unique(np.r_[g._radial.edges, b._radial.edges])
    ye = np.unique(np.r_[g._angular.edges, b._angular.edges])
    cells, metadata = _patch_setup(xe, ye, order, variant)
    geval, beval = fast.Evaluator(g), fast.Evaluator(b)
    lib = fast._native() if backend == 'native' else None
    totals, batches, maximum_batch_points = [[], []], 0, 0
    for xi, eta, w, counts in patch_batches(cells, order, batch_patches):
        batches += 1
        maximum_batch_points = max(maximum_batch_points, len(xi))
        G, A = geval.values(xi, eta), beval.values(xi, eta)
        fast._finite(G, A)
        result = np.zeros(2)
        if backend == 'native':
            lib.bass_torque(len(xi), len(counts), counts, xi, eta, w, G, A, g.R, result)
        else:
            rho = g.R/2*np.sqrt((xi*xi-1)*(1-eta*eta))
            ra, rb = g.R/2*(xi+eta), g.R/2*(xi-eta)
            common = w*g.R**3/8*(xi*xi-eta*eta)*rho*G*A/np.sqrt(2)
            result = fast._python_sum((common/ra**3, common/rb**3), counts)
        fast._finite(result)
        for i in range(2):
            totals[i].append(float(result[i]))
    TA, TB = (math.fsum(v) for v in totals)
    metadata.update({'batch_patches': batch_patches, 'batches': batches,
                     'maximum_batch_points': maximum_batch_points,
                     'sum_grouping': 'original point/patch order within each batch; math.fsum over ordered batch sums',
                     'full_quadrature_materialized': False})
    CR = g.ZA*g.ZB*g.R/(g.ZA+g.ZB)
    return {'T_A': TA, 'T_B': TB, 'L_O_bar': float(CR*(TB-TA)/delta),
            'L_B_bar': float(-g.ZA*g.R*TA/delta), 'gap': float(delta),
            'quadrature': 'geometry-balanced rectangles + two-corner Duffy' if variant == 'balanced'
                          else 'original two-corner Duffy + composite Gauss',
            'backend': backend, **metadata}
