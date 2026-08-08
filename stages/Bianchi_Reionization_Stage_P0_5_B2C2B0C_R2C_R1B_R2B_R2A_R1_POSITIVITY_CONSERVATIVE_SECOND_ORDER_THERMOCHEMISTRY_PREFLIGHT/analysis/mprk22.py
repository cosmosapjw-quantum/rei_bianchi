#!/usr/bin/env python3
"""Nonautonomous MPRK22(1) Patankar--Heun kernel.

For alpha=1 the second-stage denominator is y^n and the final Patankar weight
denominator is sigma=y^(2).  The pairwise production array is stored as
`flux[dest, source] >= 0`.  Both linear systems have M-matrix form, preserve
strict positivity, and conserve every linear invariant respected by the flux
blocks.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
import math
import numpy as np

FluxFunction=Callable[[float,np.ndarray],np.ndarray]

@dataclass(frozen=True)
class MPRK22Result:
    predictor: np.ndarray
    corrector: np.ndarray
    stage_flux: np.ndarray
    final_flux: np.ndarray
    predictor_minimum: float
    corrector_minimum: float
    conservation_residual: float


def _state(y: np.ndarray) -> np.ndarray:
    arr=np.asarray(y,dtype=np.float64)
    if arr.ndim!=2 or arr.shape[1]<2:
        raise ValueError('state must have shape [N,S], S>=2')
    if np.any(~np.isfinite(arr)) or np.any(arr<=0.0):
        raise ValueError('MPRK state must be finite and strictly positive')
    return np.ascontiguousarray(arr)


def _flux(flux: np.ndarray, shape: tuple[int,int]) -> np.ndarray:
    arr=np.asarray(flux,dtype=np.float64)
    n,s=shape
    if arr.shape!=(n,s,s):
        raise ValueError(f'flux must have shape {(n,s,s)}')
    if np.any(~np.isfinite(arr)) or np.any(arr<0.0):
        raise ValueError('flux must be finite and nonnegative')
    if np.any(np.diagonal(arr,axis1=1,axis2=2)!=0.0):
        raise ValueError('self-transfer flux must be exactly zero')
    return np.ascontiguousarray(arr)


def _generator(flux: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    den=_state(denominator)
    n,s=den.shape
    p=_flux(flux,(n,s))
    with np.errstate(over='raise',divide='raise',invalid='raise'):
        generator=np.divide(p,den[:,None,:])
        outgoing=np.sum(p,axis=1,dtype=np.float64)/den
    idx=np.arange(s)
    generator[:,idx,idx]=-outgoing
    if np.any(~np.isfinite(generator)):
        raise FloatingPointError('Patankar generator is nonfinite')
    return generator


def _solve(y0: np.ndarray, flux: np.ndarray, denominator: np.ndarray, dt: float) -> np.ndarray:
    parent=_state(y0); step=float(dt)
    if not math.isfinite(step) or step<0.0:
        raise ValueError('dt must be finite and nonnegative')
    if step==0.0:
        return parent.copy()
    generator=_generator(flux,denominator)
    s=parent.shape[1]
    lhs=np.eye(s,dtype=np.float64)[None,:,:]-step*generator
    try:
        result=np.linalg.solve(lhs,parent[...,None])[...,0]
    except np.linalg.LinAlgError as exc:
        raise FloatingPointError('Patankar linear solve failed') from exc
    if np.any(~np.isfinite(result)) or np.any(result<=0.0):
        raise FloatingPointError('Patankar solve left the strict positive cone')
    return np.ascontiguousarray(result)


def patankar_euler(*, y0: np.ndarray, flux: np.ndarray, dt: float) -> np.ndarray:
    parent=_state(y0)
    return _solve(parent,flux,parent,dt)


def mprk22_step(*, y0: np.ndarray, t0: float, dt: float, flux_function: FluxFunction) -> MPRK22Result:
    parent=_state(y0); start=float(t0); step=float(dt)
    if not math.isfinite(start) or not math.isfinite(step) or step<0.0:
        raise ValueError('invalid time or timestep')
    flux0=_flux(flux_function(start,parent),(parent.shape[0],parent.shape[1]))
    predictor=patankar_euler(y0=parent,flux=flux0,dt=step)
    flux1=_flux(flux_function(start+step,predictor),(parent.shape[0],parent.shape[1]))
    # MPRK22(alpha=1): b1=b2=1/2 and sigma_i=y_i^(2).
    average_flux=0.5*(flux0+flux1)
    corrector=_solve(parent,average_flux,predictor,step)
    total0=np.sum(parent,axis=1,dtype=np.float64)
    total1=np.sum(corrector,axis=1,dtype=np.float64)
    scale=np.maximum(np.abs(total0),1.0)
    residual=float(np.max(np.abs(total1-total0)/scale))
    return MPRK22Result(
        predictor=predictor,corrector=corrector,
        stage_flux=flux0,final_flux=flux1,
        predictor_minimum=float(np.min(predictor)),
        corrector_minimum=float(np.min(corrector)),
        conservation_residual=residual,
    )
