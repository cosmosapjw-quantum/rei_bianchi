#!/usr/bin/env python3
"""Deterministic positive production--destruction decomposition.

The source full-OTS operator conserves hydrogen nuclei in the two-state block
(HI,HII) and helium nuclei in the three-state block (HeI,HeII,HeIII).  This
module rewrites each conservative RHS as nonnegative pairwise transfer rates
`flux[dest, source]`.  No H/He cross-block transfer is introduced.
"""
from __future__ import annotations

import numpy as np

H_BLOCK=(0,1)
HE_BLOCK=(2,3,4)

class NonConservativeRHS(ValueError):
    def __init__(self, block: str, residual: float, scale: float) -> None:
        super().__init__(f"{block} RHS is not conservative: residual={residual!r}, scale={scale!r}")
        self.block=block; self.residual=float(residual); self.scale=float(scale)


def _validate(rhs: np.ndarray, relative_tolerance: float) -> np.ndarray:
    arr=np.asarray(rhs,dtype=np.float64)
    if arr.ndim!=2 or arr.shape[1]!=5:
        raise ValueError('rhs must have shape [N,5]')
    if np.any(~np.isfinite(arr)):
        raise ValueError('rhs must be finite')
    for name,idx in (('HYDROGEN',H_BLOCK),('HELIUM',HE_BLOCK)):
        block=arr[:,idx]
        residual=np.sum(block,axis=1,dtype=np.float64)
        scale=np.maximum(np.sum(np.abs(block),axis=1,dtype=np.float64),1.0)
        bad=np.abs(residual)>float(relative_tolerance)*scale
        if np.any(bad):
            i=int(np.flatnonzero(bad)[0])
            raise NonConservativeRHS(name,float(residual[i]),float(scale[i]))
    return arr


def _allocate_block(rhs: np.ndarray, indices: tuple[int,...], flux: np.ndarray) -> None:
    """Greedy deterministic transport from ascending donors to receivers."""
    block=np.asarray(rhs[:,indices],dtype=np.float64)
    supply=np.maximum(-block,0.0)
    demand=np.maximum(block,0.0)
    # Tiny source roundoff may make total supply and demand differ within the
    # accepted conservation tolerance.  Match only their common amount; the
    # remaining mismatch is exactly the source conservation residual.
    for d_local,d_global in enumerate(indices):
        for r_local,r_global in enumerate(indices):
            if d_global==r_global:
                continue
            amount=np.minimum(supply[:,d_local],demand[:,r_local])
            flux[:,r_global,d_global]=amount
            supply[:,d_local]-=amount
            demand[:,r_local]-=amount


def decompose_conservative_rhs(
    rhs: np.ndarray, *, relative_tolerance: float=1.0e-11
) -> np.ndarray:
    arr=_validate(rhs,relative_tolerance)
    flux=np.zeros((arr.shape[0],5,5),dtype=np.float64)
    _allocate_block(arr,H_BLOCK,flux)
    _allocate_block(arr,HE_BLOCK,flux)
    return flux


def flux_rhs(flux: np.ndarray) -> np.ndarray:
    arr=np.asarray(flux,dtype=np.float64)
    if arr.ndim!=3 or arr.shape[1:]!=(5,5):
        raise ValueError('flux must have shape [N,5,5]')
    if np.any(~np.isfinite(arr)) or np.any(arr<0.0):
        raise ValueError('flux must be finite and nonnegative')
    incoming=np.sum(arr,axis=2,dtype=np.float64)
    outgoing=np.sum(arr,axis=1,dtype=np.float64)
    return incoming-outgoing
