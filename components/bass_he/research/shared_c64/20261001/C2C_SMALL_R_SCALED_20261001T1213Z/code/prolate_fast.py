"""Batched, separable prolate observables; identical operator formulas to C1.

Scalar BSplines avoid a dense basis evaluation at every two-dimensional point.
Direct Cartesian derivatives and value-only Coulomb force lanes remain separate.
Native sums have fixed point and patch order; no OpenMP floating reduction.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import os
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import BSpline


class Evaluator:
    """An immutable coefficient snapshot, not a cache of mutable states."""
    def __init__(self, state):
        if state.m not in (0, 1):
            raise ValueError('only m=0 and m=1 supported')
        self.m, self.xi_max = state.m, float(state.xi_max)
        self.normalization = float(state.normalization)
        if not np.isfinite(self.normalization) or self.normalization <= 0:
            raise ValueError('positive finite state normalization required')
        self.axes = []
        for axis, coefficients in ((state._radial, state.radial_coefficients),
                                   (state._angular, state.angular_coefficients)):
            coefficients = np.asarray(coefficients, dtype=np.float64)
            if coefficients.ndim != 1 or not np.all(np.isfinite(coefficients)):
                raise ValueError('finite coefficient vectors required')
            basis = axis.basis
            scalar = BSpline(basis.t.copy(), np.array(basis.c @ coefficients, copy=True),
                             basis.k, extrapolate=False)
            self.axes.append((scalar, scalar.derivative()))

    def _coordinates(self, xi, eta, derivatives):
        xi, eta = np.broadcast_arrays(np.asarray(xi, dtype=float), np.asarray(eta, dtype=float))
        if (not np.all(np.isfinite(xi)) or not np.all(np.isfinite(eta)) or
                np.any(xi < 1) or np.any(xi > self.xi_max) or np.any(np.abs(eta) > 1)):
            raise ValueError('point outside finite spheroidal domain')
        if derivatives and self.m and (np.any(xi == 1) or np.any(np.abs(eta) == 1)):
            raise ValueError('m=1 derivatives require open coordinate nodes')
        return xi, eta

    def evaluate(self, xi, eta, derivatives=True):
        xi, eta = self._coordinates(xi, eta, derivatives)
        # Composite tensor quadrature repeats each one-dimensional coordinate.
        # Evaluate the scalar spline only at distinct coordinates, then gather.
        ux, ix = np.unique(xi, return_inverse=True)
        uy, iy = np.unique(eta, return_inverse=True)
        sx, sy = self.axes[0][0], self.axes[1][0]
        u, v = sx(ux)[ix].reshape(xi.shape), sy(uy)[iy].reshape(eta.shape)
        n = self.normalization
        if self.m == 0:
            value = n*u*v
            if not derivatives:
                return value
            du = self.axes[0][1](ux)[ix].reshape(xi.shape)
            dv = self.axes[1][1](uy)[iy].reshape(eta.shape)
            return value, n*du*v, n*u*dv
        f, h = np.sqrt(xi*xi-1), np.sqrt(1-eta*eta)
        value = n*f*u*h*v
        if not derivatives:
            return value
        du = self.axes[0][1](ux)[ix].reshape(xi.shape)
        dv = self.axes[1][1](uy)[iy].reshape(eta.shape)
        return value, n*(xi/f*u+f*du)*h*v, n*f*u*(-eta/h*v+h*dv)

    def values(self, xi, eta):
        return self.evaluate(xi, eta, derivatives=False)


def evaluate(state, xi, eta):
    return Evaluator(state).evaluate(xi, eta)


def values(state, xi, eta):
    return Evaluator(state).values(xi, eta)


def _compatible(g, b):
    if g.m != 0 or b.m != 1 or (g.R, g.ZA, g.ZB) != (b.R, b.ZA, b.ZB):
        raise ValueError('requires matched m=0 / bright |m|=1 states')
    if g.xi_max != b.xi_max:
        raise ValueError('states must use same finite prolate domain')
    if any(not np.isfinite(x) for x in (g.R, g.ZA, g.ZB)) or g.R <= 0:
        raise ValueError('finite positive R required')
    if g.ZA < 0 or g.ZB < 0 or g.ZA+g.ZB <= 0:
        raise ValueError('nonnegative charges with positive total required')


def _patches(g, b, order, duffy):
    if isinstance(order, bool) or not isinstance(order, int) or order < 2:
        raise ValueError('quadrature order must be integer >=2')
    xe = np.unique(np.r_[g._radial.edges, b._radial.edges])
    ye = np.unique(np.r_[g._angular.edges, b._angular.edges])
    if any(not np.all(np.isfinite(e)) or np.any(np.diff(e) <= 0) for e in (xe, ye)):
        raise ValueError('finite increasing quadrature edges required')
    q, w = leggauss(order)
    t, w = (q+1)/2, w/2
    T, U = np.meshgrid(t, t, indexing='ij')
    W = w[:, None]*w[None, :]
    xx, yy, ww, counts = [], [], [], []
    for i, (xl, xh) in enumerate(zip(xe[:-1], xe[1:])):
        for j, (yl, yh) in enumerate(zip(ye[:-1], ye[1:])):
            hx, hy = xh-xl, yh-yl
            if duffy and i == 0 and j in (0, len(ye)-2):
                for a, bb in ((hx*T, hy*T*U), (hx*T*U, hy*T)):
                    xx.append((xl+a).ravel())
                    yy.append((yl+bb if j == 0 else yh-bb).ravel())
                    ww.append((hx*hy*T*W).ravel())
                    counts.append(order*order)
            else:
                xx.append((xl+hx*T).ravel())
                yy.append((yl+hy*U).ravel())
                ww.append((hx*hy*W).ravel())
                counts.append(order*order)
    if sum(counts) > np.iinfo(np.int32).max:
        raise ValueError('native ABI point count overflow')
    return tuple(np.concatenate(a) for a in (xx, yy, ww)) + (np.array(counts, dtype=np.int32),)


def _native_path():
    return Path(os.environ.get('BASS_PROLATE_LIBRARY',
                Path(__file__).resolve().parents[1]/'native/build/libbass_prolate.so')).resolve()


def native_identity():
    path = _native_path()
    manifest = path.with_suffix('.build.json')
    if not path.is_file() or not manifest.is_file():
        raise RuntimeError('native library and build manifest are required; no fallback')
    identity = json.loads(manifest.read_text())
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    expected = os.environ.get('BASS_PROLATE_EXPECTED_SHA256')
    if expected is not None and actual != expected:
        raise RuntimeError('native library differs from execution-pinned SHA256')
    source = Path(__file__).resolve().parents[1]/'native/prolate_observables.f90'
    if (identity.get('schema') != 'bass-prolate-build-v1' or identity.get('abi') != 1 or
            identity.get('library_sha256') != actual or
            identity.get('source_sha256') != hashlib.sha256(source.read_bytes()).hexdigest()):
        raise RuntimeError('native build identity mismatch')
    return {'library': str(path), 'library_sha256': actual,
            'build_manifest': str(manifest), 'build': identity}


def _native():
    identity = native_identity()
    lib = ctypes.CDLL(identity['library'])
    lib.bass_prolate_abi.restype = ctypes.c_int
    if lib.bass_prolate_abi() != 1:
        raise RuntimeError('native ABI mismatch')
    d = np.ctypeslib.ndpointer(dtype=np.float64, ndim=1, flags='C_CONTIGUOUS')
    i = np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS')
    lib.bass_direct.argtypes = [ctypes.c_int, ctypes.c_int, i]+[d]*7+[ctypes.c_double]*3+[d]
    lib.bass_direct.restype = None
    lib.bass_torque.argtypes = [ctypes.c_int, ctypes.c_int, i]+[d]*5+[ctypes.c_double, d]
    lib.bass_torque.restype = None
    return lib


def _backend(backend):
    if backend not in ('python', 'native'):
        raise ValueError('backend must be explicitly python or native')


def _finite(*arrays):
    if any(not np.all(np.isfinite(a)) for a in arrays):
        raise FloatingPointError('nonfinite observable intermediate or result')


def _direct_terms(g, xi, eta, w, G, A, Ax, Ae):
    c = g.R/2
    midpoint = (g.ZA-g.ZB)*g.R/(2*(g.ZA+g.ZB))
    p, q = xi*xi-1, 1-eta*eta
    rho, z = c*np.sqrt(p*q), c*xi*eta+midpoint
    rx, re, zx, ze = c*xi*np.sqrt(q/p), -c*eta*np.sqrt(p/q), c*eta, c*xi
    det = rx*ze-re*zx
    Ar, Az = (ze*Ax-zx*Ae)/det, (-re*Ax+rx*Ae)/det
    measure = w*g.R**3/8*(xi*xi-eta*eta)
    common, px = measure*G/np.sqrt(2), Ar+A/rho
    return [common*(z*px-rho*Az), common*((c*xi*eta-c)*px-rho*Az),
            common*px, common*rho*A, measure*G*G, measure*A*A]


def _python_sum(terms, counts):
    # Fixed patch order; np.sum may use a pairwise within-patch reduction.
    totals = np.zeros(len(terms))
    start = 0
    for size in counts:
        stop = start+int(size)
        totals += [np.sum(term[start:stop]) for term in terms]
        start = stop
    return totals


def direct(g, b, order=12, backend='native'):
    _compatible(g, b)
    _backend(backend)
    xi, eta, w, counts = _patches(g, b, order, False)
    G = Evaluator(g).values(xi, eta)
    A, Ax, Ae = Evaluator(b).evaluate(xi, eta)
    _finite(G, A, Ax, Ae)
    if backend == 'native':
        result = np.zeros(6)
        _native().bass_direct(len(xi), len(counts), counts, xi, eta, w,
                              G, A, Ax, Ae, g.R, g.ZA, g.ZB, result)
    else:
        result = _python_sum(_direct_terms(g, xi, eta, w, G, A, Ax, Ae), counts)
    _finite(result)
    return dict(zip(('L_O_bar', 'L_B_bar', 'p_x_bar', 'dipole_x', 'norm_g', 'norm_b'), map(float, result)))


def torque(g, b, order=16, backend='native'):
    _compatible(g, b)
    _backend(backend)
    delta = b.energy-g.energy
    if not np.isfinite(delta) or delta <= 0:
        raise ValueError('positive isolated bright-ground gap required')
    xi, eta, w, counts = _patches(g, b, order, True)
    G, A = Evaluator(g).values(xi, eta), Evaluator(b).values(xi, eta)
    _finite(G, A)
    if backend == 'native':
        result = np.zeros(2)
        _native().bass_torque(len(xi), len(counts), counts, xi, eta, w, G, A, g.R, result)
    else:
        rho = g.R/2*np.sqrt((xi*xi-1)*(1-eta*eta))
        ra, rb = g.R/2*(xi+eta), g.R/2*(xi-eta)
        common = w*g.R**3/8*(xi*xi-eta*eta)*rho*G*A/np.sqrt(2)
        result = _python_sum((common/ra**3, common/rb**3), counts)
    _finite(result)
    TA, TB = map(float, result)
    CR = g.ZA*g.ZB*g.R/(g.ZA+g.ZB)
    return {'T_A': TA, 'T_B': TB, 'L_O_bar': float(CR*(TB-TA)/delta),
            'L_B_bar': float(-g.ZA*g.R*TA/delta), 'gap': float(delta),
            'quadrature': 'Duffy two corner cells + composite Gauss', 'order': order}


def dark(g, b, order=16, phi_nodes=32, backend='native'):
    """Independent numerical azimuthal selection-rule diagnostic.

    Bright amplitude times sin(phi), differentiated before phi integration:
    K=z*(A_r-A/rho)-rho*A_z; phi factor sin(phi)*cos(phi)/(sqrt(2)*pi).
    No hardcoded zero is returned. This is not an additional eigenstate solve.
    """
    _compatible(g, b)
    _backend(backend)
    if isinstance(phi_nodes, bool) or not isinstance(phi_nodes, int) or phi_nodes < 4:
        raise ValueError('phi_nodes must be integer >=4')
    # The diagnostic uses vectorized NumPy for both requested backends; it does
    # not claim a native operator implementation or fall back after a failure.
    if backend == 'native':
        native_identity()
    xi, eta, w, counts = _patches(g, b, order, False)
    G = Evaluator(g).values(xi, eta)
    A, Ax, Ae = Evaluator(b).evaluate(xi, eta)
    c = g.R/2
    p, q = xi*xi-1, 1-eta*eta
    rho = c*np.sqrt(p*q)
    z = c*xi*eta+(g.ZA-g.ZB)*g.R/(2*(g.ZA+g.ZB))
    rx, re, zx, ze = c*xi*np.sqrt(q/p), -c*eta*np.sqrt(p/q), c*eta, c*xi
    det = rx*ze-re*zx
    Ar, Az = (ze*Ax-zx*Ae)/det, (-re*Ax+rx*Ae)/det
    measure = w*g.R**3/8*(xi*xi-eta*eta)
    meridional = float(_python_sum([measure*G*(z*(Ar-A/rho)-rho*Az)], counts)[0])
    phi = 2*np.pi*np.arange(phi_nodes)/phi_nodes
    weight = 2*np.pi/phi_nodes
    angular = float(weight*np.sum(np.sin(phi)*np.cos(phi))/(np.sqrt(2)*np.pi))
    result = {'L_dark_O_bar': meridional*angular, 'meridional_integral': meridional,
              'angular_sin_cos_factor': angular, 'phi_nodes': phi_nodes,
              'phi_bright_norm_factor': float(weight*np.sum(np.cos(phi)**2)/np.pi),
              'phi_dark_norm_factor': float(weight*np.sum(np.sin(phi)**2)/np.pi),
              'implementation': 'NumPy azimuthal diagnostic; numerical periodic quadrature'}
    _finite(meridional, angular, result['L_dark_O_bar'])
    return result
