"""PHYS45 NONCERTIFYING NumPy Gauss preview and microbenchmarks of actual Yukawa 21x21.

The exact rational interval proof lives in phys45_screened_exterior.py.
Do not treat quadrature convergence or numerical eigvals as proof.
"""
from __future__ import annotations
from functools import lru_cache
from time import perf_counter
import numpy as np

@lru_cache(maxsize=3)
def _legendre_quadrature(n:int,lmax:int):
    if n<32 or n>2048 or not 0<=lmax<=20:
        raise ValueError("noncert Gauss preview budget")
    mu,w=np.polynomial.legendre.leggauss(n)
    p=np.polynomial.legendre.legvander(mu,lmax)
    alphas=np.sqrt(2*np.arange(lmax+1,dtype=np.float64)+1)
    for v in (mu,w,p,alphas):v.flags.writeable=False
    return mu,w,p,alphas


def preview_matrix(r:float=20.0,R:float=0.7,n:int=512,lmax:int=20)->dict:
    if not np.isfinite(r) or not np.isfinite(R) or r<=R or R<=0:
        raise ValueError("noncert physical finite positive exterior radius")
    mu,w,p,alpha=_legendre_quadrature(n,lmax)
    s=np.sqrt(r*r+R*R-2*r*R*mu)
    S=(1+1/s)*np.exp(-2*s)
    t=perf_counter()
    mat=(alpha[:,None]*alpha[None,:])*(p.T @ ((w*S)[:,None]*p))/2
    eig=np.linalg.eigvalsh(mat)
    return {
        "status":"NONCERTIFYING_FLOAT64_GAUSS",
        "r_a0":r,"R_a0":R,"mu_nodes":n,"lmax":lmax,
        "matrix_float64":mat.tolist(),
        "max_symmetric_deviation_float":float(np.max(np.abs(mat-mat.T))),
        "min_eigen_float":float(eig[0]),
        "max_eigen_float":float(eig[-1]),
        "kernel_wall_s":perf_counter()-t,
    }


def vectorized_vs_scalar(n:int=512,lmax:int=20,iterations:int=120)->dict:
    if not 1<=iterations<=1000:raise ValueError("bench bound")
    mu,w,p,alpha=_legendre_quadrature(n,lmax)
    s=np.sqrt(20*20+0.7**2-2*20*0.7*mu)
    S=(1+1/s)*np.exp(-2*s)
    weighted=w*S
    a=perf_counter()
    fast=None
    for _ in range(iterations):
        fast=(alpha[:,None]*alpha[None,:])*(p.T @ (weighted[:,None]*p))/2
    tf=perf_counter()-a
    b=perf_counter()
    slow=None
    for _ in range(iterations):
        slow=np.empty((lmax+1,lmax+1))
        for ell in range(lmax+1):
            for m in range(lmax+1):
                slow[ell,m]=alpha[ell]*alpha[m]*np.sum(weighted*p[:,ell]*p[:,m])/2
    ts=perf_counter()-b
    err=np.max(np.abs(fast-slow))
    return {
        "status":"NONCERTIFYING_FLOAT64_SAME_QUADRATURE",
        "repeats":iterations,"n":n,"lmax":lmax,
        "batched_numpy_matrix_mult_wall_s":tf,
        "scalar_pairwise_numpy_summations_wall_s":ts,
        "speedup_scalar_over_batched":ts/tf,
        "max_matrix_abs_difference":float(err),
        "float64_eigenvalues":np.linalg.eigvalsh(fast).tolist(),
        "scope":"same N-point Gauss kernel only; not rational interval or full scattering solver",
    }
