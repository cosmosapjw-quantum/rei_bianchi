"""Bounded-memory tensor quadrature for the unchanged prolate observables.

The complete point sequence is identical to prolate_fast._patches(..., False).
Only storage and inter-batch summation change; bitwise agreement is not claimed.
"""
from __future__ import annotations

import math

import numpy as np
from numpy.polynomial.legendre import leggauss

import prolate_fast as fast


DIRECT_KEYS = ('L_O_bar', 'L_B_bar', 'p_x_bar', 'dipole_x', 'norm_g', 'norm_b')


def _positive_integer(value, name, minimum, maximum=None):
    if (isinstance(value, bool) or not isinstance(value, int) or value < minimum
            or (maximum is not None and value > maximum)):
        raise ValueError(f'{name} must be integer in [{minimum}, {maximum or "unbounded"}]')


def _geometry(g, b, order, batch_patches):
    fast._compatible(g, b)
    _positive_integer(order, 'quadrature order', 2)
    _positive_integer(batch_patches, 'batch_patches', 1, 64)
    edges = []
    for attr, lo, hi in (('_radial', 1., g.xi_max), ('_angular', -1., 1.)):
        for state in (g, b):
            e = np.asarray(getattr(state, attr).edges, dtype=np.float64)
            if (e.ndim != 1 or len(e) < 2 or not np.all(np.isfinite(e))
                    or np.any(np.diff(e) <= 0) or e[0] != lo or e[-1] != hi):
                raise ValueError('finite increasing edges covering the state domain required')
        edges.append(np.unique(np.r_[getattr(g, attr).edges, getattr(b, attr).edges]))
    patches = (len(edges[0])-1)*(len(edges[1])-1)
    points = patches*order*order
    if points > np.iinfo(np.int32).max:
        raise ValueError('native ABI point count overflow')
    return edges[0], edges[1], {
        'quadrature': 'unchanged composite tensor Gauss, streamed in original patch order',
        'order': order, 'patches': patches, 'points': points,
        'batch_patches': batch_patches,
        'batches': math.ceil(patches/batch_patches),
        'maximum_batch_points': min(patches, batch_patches)*order*order,
        'full_quadrature_materialized': patches <= batch_patches,
        'unbounded_domain_materialization': False,
        'batch_total_combination': 'math.fsum in fixed batch order per observable',
        'bitwise_parent_identity_claimed': False,
    }


def _tensor_batches(xe, ye, order, batch_patches):
    # Match every floating operation, mesh index, and ravel order in _patches.
    q, w = leggauss(order)
    t, w = (q+1)/2, w/2
    T, U = np.meshgrid(t, t, indexing='ij')
    W = w[:, None]*w[None, :]
    xx, yy, ww = [], [], []
    for xl, xh in zip(xe[:-1], xe[1:]):
        for yl, yh in zip(ye[:-1], ye[1:]):
            hx, hy = xh-xl, yh-yl
            xx.append((xl+hx*T).ravel())
            yy.append((yl+hy*U).ravel())
            ww.append((hx*hy*W).ravel())
            if len(xx) == batch_patches:
                yield (np.concatenate(xx), np.concatenate(yy), np.concatenate(ww),
                       np.full(len(xx), order*order, dtype=np.int32))
                xx, yy, ww = [], [], []
    if xx:
        yield (np.concatenate(xx), np.concatenate(yy), np.concatenate(ww),
               np.full(len(xx), order*order, dtype=np.int32))


def patch_batches(g, b, order=12, batch_patches=32):
    """Yield original tensor quadrature in bounded batches; no full point arrays."""
    xe, ye, _ = _geometry(g, b, order, batch_patches)
    yield from _tensor_batches(xe, ye, order, batch_patches)


def direct(g, b, order=12, backend='native', batch_patches=32):
    fast._backend(backend)
    xe, ye, metadata = _geometry(g, b, order, batch_patches)
    eg, eb = fast.Evaluator(g), fast.Evaluator(b)
    lib = fast._native() if backend == 'native' else None
    totals = [[] for _ in DIRECT_KEYS]
    for xi, eta, w, counts in _tensor_batches(xe, ye, order, batch_patches):
        G = eg.values(xi, eta)
        A, Ax, Ae = eb.evaluate(xi, eta)
        fast._finite(G, A, Ax, Ae)
        if lib is not None:
            values = np.zeros(6)
            lib.bass_direct(len(xi), len(counts), counts, xi, eta, w,
                            G, A, Ax, Ae, g.R, g.ZA, g.ZB, values)
        else:
            values = fast._python_sum(
                fast._direct_terms(g, xi, eta, w, G, A, Ax, Ae), counts)
        fast._finite(values)
        for bucket, value in zip(totals, values):
            bucket.append(float(value))
    values = [math.fsum(bucket) for bucket in totals]
    fast._finite(values)
    metadata['backend'] = backend
    metadata['implementation'] = ('unchanged Fortran bass_direct ABI 1, fixed patch sums'
                                  if lib is not None else 'unchanged NumPy direct terms and patch sums')
    return dict(zip(DIRECT_KEYS, values)) | {'streaming': metadata}


def dark(g, b, order=16, phi_nodes=32, backend='native', batch_patches=32):
    """Numerical selection-rule diagnostic; unchanged NumPy meridional/phi formula.

    Like the parent, backend='native' checks the native identity but this diagnostic
    performs its operator arithmetic with NumPy. It does not claim native speed.
    """
    fast._backend(backend)
    _positive_integer(phi_nodes, 'phi_nodes', 4)
    xe, ye, metadata = _geometry(g, b, order, batch_patches)
    if backend == 'native':
        fast.native_identity()
    eg, eb = fast.Evaluator(g), fast.Evaluator(b)
    c = g.R/2
    totals = []
    for xi, eta, w, counts in _tensor_batches(xe, ye, order, batch_patches):
        G = eg.values(xi, eta)
        A, Ax, Ae = eb.evaluate(xi, eta)
        fast._finite(G, A, Ax, Ae)
        p, q = xi*xi-1, 1-eta*eta
        rho = c*np.sqrt(p*q)
        z = c*xi*eta+(g.ZA-g.ZB)*g.R/(2*(g.ZA+g.ZB))
        rx, re, zx, ze = c*xi*np.sqrt(q/p), -c*eta*np.sqrt(p/q), c*eta, c*xi
        det = rx*ze-re*zx
        Ar, Az = (ze*Ax-zx*Ae)/det, (-re*Ax+rx*Ae)/det
        measure = w*g.R**3/8*(xi*xi-eta*eta)
        value = float(fast._python_sum([measure*G*(z*(Ar-A/rho)-rho*Az)], counts)[0])
        fast._finite(value)
        totals.append(value)
    meridional = math.fsum(totals)
    phi = 2*np.pi*np.arange(phi_nodes)/phi_nodes
    weight = 2*np.pi/phi_nodes
    angular = float(weight*np.sum(np.sin(phi)*np.cos(phi))/(np.sqrt(2)*np.pi))
    result = {
        'L_dark_O_bar': meridional*angular,
        'meridional_integral': meridional,
        'angular_sin_cos_factor': angular, 'phi_nodes': phi_nodes,
        'phi_bright_norm_factor': float(weight*np.sum(np.cos(phi)**2)/np.pi),
        'phi_dark_norm_factor': float(weight*np.sum(np.sin(phi)**2)/np.pi),
        'implementation': 'NumPy azimuthal diagnostic; numerical periodic quadrature',
    }
    fast._finite(meridional, angular, result['L_dark_O_bar'])
    metadata['requested_backend'] = backend
    metadata['actual_operator_backend'] = 'numpy'
    result['streaming'] = metadata
    return result
