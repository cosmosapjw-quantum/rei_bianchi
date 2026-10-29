"""BASS-native 21-state electron-feedback algebra; no IVP or owner-source imports.

Source identity: rei_bianchi PR265 9b0b97aa, BASS_ATOMIC_NETWORK.py blob
 e3a0603176304f64b953c0b2faf898d6b75eceb. This module implements a
matrix-only check of that source's displayed evaluate() equations.

Y is per baryon; nb is m^-3; G0/D s^-1; Gne m^3/s.
The optional x-time chemical block is scaled by H (s^-1), and requires an
externally supplied *positive* H and source-selected diagonal state scales.
It does not reconstruct donor atomic coefficients or physical trajectories.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

# Exact native index semantics from original source, no approximate isotope lift.
A = np.array([1,1,1,2,2,3,3,3,3,3,4,4,4,6,6,6,6,7,7,7,7], dtype=float)
Q = np.array([0,0,1,0,1,0,1,0,1,2,0,1,2,0,1,2,3,0,1,2,3], dtype=float)
GROUPS = ((0,), (1,2), (3,4), (5,6), (7,8,9), (10,11,12),
          (13,14,15,16), (17,18,19,20))


def validate(Y, G0, Gne, D, nb):
    y = np.asarray(Y, dtype=float)
    g = np.asarray(G0, dtype=float); r = np.asarray(Gne, dtype=float)
    d = np.asarray(D, dtype=float)
    if y.shape != (21,) or any(t.shape != (21,21) for t in (g,r,d)):
        raise ValueError('BASS full21 expected; no silent 17/reduced30 lift')
    if np.any(~np.isfinite(y)) or any(np.any(~np.isfinite(t)) for t in (g,r,d)):
        raise ValueError('nonfinite input')
    if not np.isfinite(nb) or nb < 0:
        raise ValueError('nb must be finite nonnegative m^-3')
    return y,g,r,d


def physical_rhs_jac(Y, G0, Gne, D, nb):
    """Exact pointwise source equation, Jacobian and rank-one factors.

    F=(G0+D+nb*(q.Y)*Gne)Y
    J=(G0+D+nb*(q.Y)*Gne)+nb*(Gne.Y) outer q.
    Does not assume the supplied matrices are physical donor coefficients.
    """
    y,g,r,d = validate(Y,G0,Gne,D,nb)
    ne = nb * float(Q@y)
    frozen = g+d+ne*r
    u = nb * (r@y)
    rhs = frozen@y
    jac = frozen + np.outer(u,Q)
    return dict(rhs=rhs,jac=jac,frozen=frozen,u=u,q=Q.copy(),ne=ne)


@dataclass(frozen=True)
class RankOneResult:
    solution: np.ndarray
    denominator: float
    relative_residual: float
    residual_identity_defect: float
    # No speedup or conditioning certificate is implied by this result.


def rank_one_solve(M, u, q, h, b, *, denominator_safety=64.0):
    """Solve (M-h*u*q^T)x=b by two base solves and Sherman-Morrison.

    Returns an observed full-matrix residual and an observed exact-in-arithmetic
    residual-identity defect. The O(n) correction is not a native speed benchmark.
    When |1-q^T M^-1(h*u)| is within a roundoff-scale danger window, HOLD.
    """
    M=np.asarray(M,dtype=float);u=np.asarray(u,dtype=float)
    q=np.asarray(q,dtype=float);b=np.asarray(b,dtype=float)
    n=b.size
    if M.shape!=(n,n) or u.shape!=(n,) or q.shape!=(n,):
        raise ValueError('matrix/vector shape mismatch')
    if n==0 or not np.isfinite(M).all() or not np.isfinite(u).all() or not np.isfinite(q).all() or not np.isfinite(b).all() or not np.isfinite(h):
        raise ValueError('nonfinite or empty input')
    if h<0:
        raise ValueError('only nonnegative implicit step parameter')
    # Two right-hand sides share one base factorization in LAPACK.
    zw=np.linalg.solve(M,np.column_stack((b,h*u)))
    z,w=zw[:,0],zw[:,1]
    qw=float(q@w); s=float(1.-qw)
    roundoff=np.finfo(float).eps*denominator_safety*(1+float(np.dot(np.abs(q),np.abs(w))))
    if abs(s)<=roundoff:
        raise np.linalg.LinAlgError('rank-one Schur denominator unresolved')
    alpha=float(q@z)/s
    x=z+alpha*w
    rhs_full=M@x-h*u*float(q@x)
    residual=b-rhs_full
    r_z=b-M@z
    r_w=h*u-M@w
    # Algebraic residual identity for INEXACT base solves:
    # b-(M-h u q^T)(z+alpha*w) = r_z+alpha*r_w.
    identity_resid=r_z+alpha*r_w
    rel=float(np.linalg.norm(residual,np.inf)/(1+np.linalg.norm(b,np.inf)+np.linalg.norm(M@x,np.inf)+np.linalg.norm(h*u*float(q@x),np.inf)))
    defect=float(np.linalg.norm(residual-identity_resid,np.inf))
    return RankOneResult(x,s,rel,defect)


def solve_physical_step(Y,G0,Gne,D,nb,dt,b):
    if not np.isfinite(dt) or dt<0: raise ValueError('nonnegative proper dt required')
    c=physical_rhs_jac(Y,G0,Gne,D,nb)
    M=np.eye(21)-dt*c['frozen']
    return rank_one_solve(M,c['u'],Q,dt,b)


def log_clock_scaled_block(Y,G0,Gne,D,nb,H,scales):
    """The source-consistent 21x21 *chemical subblock*, not full62 Jacobian.
    Native BASS x=ln a, z=D_s^-1 Y, so Jx=D_s^-1 Jphys D_s/H.
    """
    if not np.isfinite(H) or H<=0: raise ValueError('H must be finite positive s^-1')
    s=np.asarray(scales,dtype=float)
    if s.shape!=(21,) or not np.isfinite(s).all() or np.any(s<=0):
        raise ValueError('positive source-defined full21 scales required')
    c=physical_rhs_jac(Y,G0,Gne,D,nb)
    frozen=c['frozen']*s[None,:]/s[:,None]/H
    u=c['u']/s/H
    q=Q*s
    return dict(frozen=frozen,u=u,q=q,jac=frozen+np.outer(u,q))
