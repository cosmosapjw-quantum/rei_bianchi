"""Independent small analytic/direct-matrix oracles; not the B1 author driver.

Imports no candidate transport or native collision code. The 2N collision
matrix follows direct axisymmetric moment quadrature, not the native
rank-nine exponential coefficients. Shared physical kernel is explicit.
"""
from __future__ import annotations

from typing import Callable
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.linalg import expm


def backward_lrs(mu_target, beta_increment):
    """Return source mu and source/target comoving energy ratio."""
    mu = np.asarray(mu_target, dtype=float)
    if not np.all(np.isfinite(mu)) or np.any(np.abs(mu) > 1):
        raise ValueError("MU_DOMAIN")
    b = float(beta_increment)
    if not np.isfinite(b):
        raise ValueError("BETA_DOMAIN")
    g = np.sqrt((1-mu*mu)*np.exp(-2*b)+mu*mu*np.exp(4*b))
    return mu*np.exp(2*b)/g, g


def collisionless_quadrupole(occupation: Callable, energy, beta_increment, nmu=256):
    """Exact one-shot LRS pullback with GL angular integration.

    energy is any fixed comoving-energy coordinate with initial F(energy).
    It is not automatically a physical frequency or observed CMB energy.
    """
    en = np.atleast_1d(np.asarray(energy, dtype=float))
    if np.any(en <= 0) or not np.all(np.isfinite(en)):
        raise ValueError("ENERGY_DOMAIN")
    mu, wt = leggauss(nmu)
    _, g = backward_lrs(mu, beta_increment)
    f = np.asarray(occupation(en[:, None]*g[None, :]), dtype=float)
    if f.shape != (len(en), nmu) or not np.all(np.isfinite(f)) or np.any(f < 0):
        raise ValueError("OCCUPATION_DOMAIN")
    monopole = f @ wt
    numerator = f @ (wt*(3*mu*mu-1)/2)
    valid = monopole > 0
    q2 = np.full_like(monopole, np.nan)
    q2[valid] = numerator[valid]/monopole[valid]
    return {"comoving_energy":en, "q2":q2, "monopole_mu_integral":monopole,
            "defined":valid}


def direct_axisym_collision_matrix(mu, weights):
    """Generator on [f_theta(mu),f_phi(mu)], integrated dmu weights."""
    mu, wt = np.asarray(mu, float), np.asarray(weights, float)
    if mu.ndim != 1 or wt.shape != mu.shape or len(mu) < 3:
        raise ValueError("QUADRATURE_SHAPE")
    if np.any(wt <= 0) or np.any(abs(mu) > 1) or not np.all(np.isfinite(mu+wt)):
        raise ValueError("QUADRATURE_DOMAIN")
    n = len(mu)
    p = np.r_[np.pi*wt*mu*mu, np.pi*wt]
    z = np.r_[2*np.pi*wt*(1-mu*mu), np.zeros(n)]
    k = np.empty((2*n, 2*n))
    k[:n] = (3/(8*np.pi))*(mu[:, None]**2*p+(1-mu[:, None]**2)*z)
    k[n:] = np.broadcast_to((3/(8*np.pi))*p, (n, 2*n))
    return k-np.eye(2*n)


def direct_axisym_collide(mu, weights, f_theta, f_phi, depth):
    tau = float(depth)
    if not np.isfinite(tau) or tau < 0:
        raise ValueError("COLLISION_DEPTH_DOMAIN")
    mu = np.asarray(mu)
    ft, fp = np.asarray(f_theta, float), np.asarray(f_phi, float)
    if ft.shape != mu.shape or fp.shape != mu.shape:
        raise ValueError("STATE_SHAPE")
    if not np.all(np.isfinite(ft+fp)):
        raise ValueError("STATE_NONFINITE")
    state = np.r_[ft, fp]
    answer = expm(tau*direct_axisym_collision_matrix(mu, weights))@state
    return answer[:len(mu)], answer[len(mu):]


LINEAR_QUADRUPOLE_MATRIX = np.array([[-0.9, -0.4], [-0.15, -0.4]])


def linear_shear_cells(beta_increments, collision_depths, logarithmic_slope=1.0):
    """Exact constant-coefficient cell solution of the FIRST-ORDER shear ODE.

    The returned columns are i2/F0 and q/F0; q2=i2/(5F0) to first order.
    Beta and tau per cell are independent inputs; no history ODE is rerun.
    """
    db, tau = np.asarray(beta_increments,float), np.asarray(collision_depths,float)
    if db.ndim != 1 or db.shape != tau.shape or np.any(tau < 0):
        raise ValueError("LINEAR_CELL_SHAPE_OR_DEPTH")
    if not np.all(np.isfinite(db+tau)):
        raise ValueError("LINEAR_CELL_NONFINITE")
    pm1 = -(LINEAR_QUADRUPOLE_MATRIX+0.3*np.eye(2))/0.7
    pm03 = (LINEAR_QUADRUPOLE_MATRIX+np.eye(2))/0.7
    history = np.zeros((len(db)+1,2))
    for i, (stepb, steptau) in enumerate(zip(db,tau)):
        if steptau == 0:
            e1=e03=1.0
            phi1=phi03=1.0
        else:
            e1=np.exp(-steptau); e03=np.exp(-0.3*steptau)
            phi1=-np.expm1(-steptau)/steptau
            phi03=-np.expm1(-0.3*steptau)/(0.3*steptau)
        propagator=e1*pm1+e03*pm03
        integral=phi1*pm1+phi03*pm03
        history[i+1]=propagator@history[i]+2*stepb*logarithmic_slope*integral[:,0]
    return history


def planck_occupation(y):
    """Dimensionless Planck occupation; only an oracle unless IC is pinned."""
    y=np.asarray(y, float)
    if np.any(y <= 0) or not np.all(np.isfinite(y)):
        raise ValueError("PLANCK_DOMAIN")
    return np.exp(-y)/(-np.expm1(-y))


def planck_logarithmic_slope(y):
    y=np.asarray(y, float)
    return -y/(-np.expm1(-y))
