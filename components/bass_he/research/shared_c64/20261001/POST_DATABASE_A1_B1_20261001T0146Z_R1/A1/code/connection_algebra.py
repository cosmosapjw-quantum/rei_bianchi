"""Auditable moving-basis matrix identities, not a BASS_HE dynamics solver.

All matrices must already be expressed in one consistent unit system.
This helper never constructs physical couplings, chooses ETF fields, projects
channels, repairs a non-Hermitian matrix, or evaluates a collision observable.
"""
import numpy as np

def dagger(a):
    return a.conj().T

def _close(a,b,tolerance):
    return np.linalg.norm(a-b,ord=np.inf)<=tolerance*max(1.0,np.linalg.norm(a,ord=np.inf),np.linalg.norm(b,ord=np.inf))

def _validated(s,h,d,sdot,hbar,tolerance,condition_limit):
    if not np.isfinite(hbar) or hbar<=0:
        raise ValueError('hbar must be finite and positive in the selected unit system')
    if not np.isfinite(tolerance) or tolerance<=0 or not np.isfinite(condition_limit) or condition_limit<1:
        raise ValueError('invalid algebra validation controls')
    mats=[np.asarray(x,dtype=complex) for x in (s,h,d,sdot)]
    shape=mats[0].shape
    if len(shape)!=2 or shape[0]!=shape[1] or shape[0]==0 or any(m.shape!=shape for m in mats):
        raise ValueError('matrices must share one nonempty square shape')
    if any(not np.all(np.isfinite(m)) for m in mats):
        raise ValueError('all matrix entries must be finite')
    s,h,d,sdot=mats
    if not _close(s,dagger(s),tolerance):
        raise ValueError('metric is not Hermitian')
    ev=np.linalg.eigvalsh(s)
    if ev[0]<=0 or ev[-1]/ev[0]>condition_limit:
        raise ValueError('metric is singular, indefinite, or beyond the declared condition limit')
    if not _close(h,dagger(h),tolerance):
        raise ValueError('Hamiltonian matrix is not Hermitian')
    if not _close(sdot,d+dagger(d),tolerance):
        raise ValueError('metric_derivative identity Sdot=D+Ddagger fails')
    return s,h,d,sdot

def metric_generator(s,h,d,sdot,hbar,*,tolerance=1e-12,condition_limit=1e8):
    """Return G for i*hbar*cdot=G*c; conserved norm is c†S c."""
    s,h,d,sdot=_validated(s,h,d,sdot,hbar,tolerance,condition_limit)
    return np.linalg.solve(s,h-1j*hbar*d)

def orthonormal_generator(s,h,d,sdot,w,wdot,hbar,*,tolerance=1e-12,condition_limit=1e8):
    """Return raw K for c=W*a, provided W†SW=I and its derivative hold."""
    s,h,d,sdot=_validated(s,h,d,sdot,hbar,tolerance,condition_limit)
    w=np.asarray(w,dtype=complex);wdot=np.asarray(wdot,dtype=complex)
    if w.shape!=s.shape or wdot.shape!=s.shape:
        raise ValueError('W and Wdot must have the metric shape')
    if not np.all(np.isfinite(w)) or not np.all(np.isfinite(wdot)):
        raise ValueError('W and Wdot must be finite')
    if not _close(dagger(w)@s@w,np.eye(s.shape[0]),tolerance):
        raise ValueError('orthonormal_metric identity fails')
    derivative=dagger(wdot)@s@w+dagger(w)@sdot@w+dagger(w)@s@wdot
    if not _close(derivative,np.zeros_like(s),tolerance):
        raise ValueError('orthonormal_metric_derivative identity fails')
    k=dagger(w)@(h-1j*hbar*d)@w-1j*hbar*dagger(w)@s@wdot
    if not _close(k,dagger(k),tolerance):
        raise ValueError('effective Hamiltonian failed Hermiticity; no symmetrization performed')
    return k
