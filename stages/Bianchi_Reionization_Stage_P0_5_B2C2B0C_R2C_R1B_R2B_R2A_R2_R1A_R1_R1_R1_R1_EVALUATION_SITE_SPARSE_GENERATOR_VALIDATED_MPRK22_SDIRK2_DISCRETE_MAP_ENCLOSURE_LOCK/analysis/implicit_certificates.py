#!/usr/bin/env python3
"""Outward-oriented local implicit tangent and Krawczyk helpers.

The routines are deliberately small and batched.  They certify local H/He
linear blocks and scalar thermal roots; they do not claim to enclose the full
four-site nonlinear discrete map.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


def _batch_matrix(value: np.ndarray) -> np.ndarray:
    arr=np.asarray(value,dtype=np.float64)
    if arr.ndim==2:arr=arr[None,...]
    if arr.ndim!=3 or arr.shape[1]!=arr.shape[2]:raise ValueError('matrix must have shape [N,S,S]')
    if np.any(~np.isfinite(arr)):raise ValueError('matrix must be finite')
    return np.ascontiguousarray(arr)


def _batch_vector(value: np.ndarray,n:int,s:int) -> np.ndarray:
    arr=np.asarray(value,dtype=np.float64)
    if arr.ndim==1:arr=arr[None,...]
    if arr.shape!=(n,s):raise ValueError(f'vector must have shape {(n,s)}')
    if np.any(~np.isfinite(arr)):raise ValueError('vector must be finite')
    return np.ascontiguousarray(arr)


def implicit_linear_tangent(lhs,solution,delta_lhs,delta_rhs):
    """Differentiate ``lhs @ solution = rhs`` without finite differences."""
    A=_batch_matrix(lhs);n,s,_=A.shape
    z=_batch_vector(solution,n,s);dA=_batch_matrix(delta_lhs);db=_batch_vector(delta_rhs,n,s)
    if dA.shape!=A.shape:raise ValueError('delta_lhs shape mismatch')
    right=db-np.einsum('nij,nj->ni',dA,z,optimize=True)
    try:out=np.linalg.solve(A,right[...,None])[...,0]
    except np.linalg.LinAlgError as exc:raise FloatingPointError('implicit tangent solve failed') from exc
    if np.any(~np.isfinite(out)):raise FloatingPointError('implicit tangent is nonfinite')
    return np.ascontiguousarray(out)


@dataclass(frozen=True)
class LinearKrawczykCertificate:
    certified: np.ndarray
    row_sum_bound: np.ndarray
    center: np.ndarray
    radius: np.ndarray
    krawczyk_radius: np.ndarray


def linear_interval_krawczyk(A_lower,A_upper,b_lower,b_upper,*,inflation:float=1.0e-10):
    """Sufficient batched Krawczyk inclusion for interval linear systems.

    A common infinity-norm tube is constructed per local block.  All floating
    bounds are moved outward with ``nextafter`` before the inclusion test.
    """
    lo=_batch_matrix(A_lower);hi=_batch_matrix(A_upper)
    if lo.shape!=hi.shape or np.any(lo>hi):raise ValueError('invalid matrix interval')
    n,s,_=lo.shape
    blo=_batch_vector(b_lower,n,s);bhi=_batch_vector(b_upper,n,s)
    if np.any(blo>bhi):raise ValueError('invalid rhs interval')
    amid=0.5*(lo+hi);arad=np.nextafter(0.5*(hi-lo),np.inf)
    bmid=0.5*(blo+bhi);brad=np.nextafter(0.5*(bhi-blo),np.inf)
    try:
        center=np.linalg.solve(amid,bmid[...,None])[...,0]
        pre=np.linalg.inv(amid)
    except np.linalg.LinAlgError as exc:
        raise FloatingPointError('midpoint matrix is singular') from exc
    fcenter=np.einsum('nij,nj->ni',amid,center,optimize=True)-bmid
    frad=np.einsum('nij,nj->ni',arad,np.abs(center),optimize=True)+brad
    corr_center=-np.einsum('nij,nj->ni',pre,fcenter,optimize=True)
    corr_rad=np.einsum('nij,nj->ni',np.abs(pre),frad,optimize=True)
    eye=np.eye(s)[None,:,:]
    mmid=eye-np.einsum('nij,njk->nik',pre,amid,optimize=True)
    mrad=np.einsum('nij,njk->nik',np.abs(pre),arad,optimize=True)
    abs_m=np.nextafter(np.abs(mmid)+mrad,np.inf)
    row_sum=np.nextafter(np.max(np.sum(abs_m,axis=2),axis=1),np.inf)
    base=np.nextafter(np.abs(corr_center)+corr_rad,np.inf)
    max_base=np.max(base,axis=1)
    safe=row_sum<1.0
    scalar_radius=np.full(n,np.inf)
    scalar_radius[safe]=np.nextafter(
        max_base[safe]/np.maximum(1.0-row_sum[safe],np.finfo(float).tiny)*(1.0+inflation),np.inf)
    radius=np.repeat(scalar_radius[:,None],s,axis=1)
    krad=np.nextafter(base+np.einsum('nij,nj->ni',abs_m,radius,optimize=True),np.inf)
    certified=safe & np.all(krad<radius,axis=1)
    return LinearKrawczykCertificate(
        certified=np.ascontiguousarray(certified),row_sum_bound=np.ascontiguousarray(row_sum),
        center=np.ascontiguousarray(center),radius=np.ascontiguousarray(radius),
        krawczyk_radius=np.ascontiguousarray(krad))


@dataclass(frozen=True)
class ScalarKrawczykCertificate:
    certified: np.ndarray
    denominator_contains_zero: np.ndarray
    radius: np.ndarray
    krawczyk_radius: np.ndarray
    contraction_bound: np.ndarray


def scalar_root_krawczyk(*,center,residual,derivative_lower,derivative_upper,initial_radius,max_inflations:int=16):
    x=np.asarray(center,dtype=np.float64);f=np.asarray(residual,dtype=np.float64)
    dl=np.asarray(derivative_lower,dtype=np.float64);du=np.asarray(derivative_upper,dtype=np.float64)
    radius=np.asarray(initial_radius,dtype=np.float64).copy()
    if not (x.shape==f.shape==dl.shape==du.shape==radius.shape):raise ValueError('scalar arrays must share shape')
    if np.any(dl>du) or np.any(radius<=0):raise ValueError('invalid scalar interval')
    zero=(dl<=0)&(du>=0)
    dm=0.5*(dl+du)
    C=np.zeros_like(dm);C[~zero]=1.0/dm[~zero]
    contraction=np.maximum(np.abs(1.0-C*dl),np.abs(1.0-C*du))
    correction=np.abs(C*f)
    certified=np.zeros(x.shape,dtype=bool);krad=np.full(x.shape,np.inf)
    for _ in range(int(max_inflations)):
        krad=np.nextafter(correction+contraction*radius,np.inf)
        certified=(~zero)&(contraction<1.0)&(krad<radius)
        if np.all(certified|zero):break
        grow=(~certified)&(~zero)
        radius[grow]=np.nextafter(np.maximum(radius[grow]*2.0,correction[grow]/np.maximum(1-contraction[grow],np.finfo(float).tiny)*1.01),np.inf)
    return ScalarKrawczykCertificate(certified,zero,radius,krad,contraction)
