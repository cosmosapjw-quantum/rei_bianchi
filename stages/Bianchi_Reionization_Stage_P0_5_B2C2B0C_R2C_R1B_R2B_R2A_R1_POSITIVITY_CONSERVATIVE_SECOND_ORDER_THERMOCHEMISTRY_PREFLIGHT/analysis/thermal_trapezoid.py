#!/usr/bin/env python3
"""Positive implicit first-stage and trapezoidal thermal corrector.

Temperature is solved in log coordinates.  No clipping is applied: if the
implicit balance has no positive bracket the corresponding node is marked
unbracketed and the caller must reject the trial.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
import numpy as np

KB_ERG=1.380649e-16
RHSFunction=Callable[[np.ndarray,np.ndarray,np.ndarray,np.ndarray,np.ndarray],np.ndarray]

@dataclass(frozen=True)
class ThermalResult:
    energy: np.ndarray
    temperature: np.ndarray
    rhs: np.ndarray
    relative_residual: np.ndarray
    bracketed: np.ndarray


def _pop(populations: np.ndarray) -> np.ndarray:
    pop=np.asarray(populations,dtype=np.float64)
    if pop.ndim!=2 or pop.shape[1]!=5:
        raise ValueError('populations must have shape [N,5]')
    if np.any(~np.isfinite(pop)) or np.any(pop<=0.0):
        raise ValueError('populations must be finite and strictly positive')
    return pop


def _vec(value, n: int, name: str, *, positive: bool=False) -> np.ndarray:
    arr=np.broadcast_to(np.asarray(value,dtype=np.float64),(n,)).copy()
    if np.any(~np.isfinite(arr)) or (positive and np.any(arr<=0.0)):
        qualifier='positive ' if positive else ''
        raise ValueError(f'{name} must be finite {qualifier}with shape [N]')
    return arr


def particles(populations: np.ndarray) -> np.ndarray:
    pop=_pop(populations)
    nhi,nhii,nhei,nheii,nheiii=pop.T
    return (nhi+nhii)+(nhei+nheii+nheiii)+nhii+nheii+2.0*nheiii


def energy_from_temperature(populations: np.ndarray, temperature: np.ndarray) -> np.ndarray:
    pop=_pop(populations); T=_vec(temperature,pop.shape[0],'temperature',positive=True)
    return 1.5*KB_ERG*particles(pop)*T


def _root(
    *, balance: Callable[[np.ndarray],np.ndarray], populations: np.ndarray,
    parent_energy: np.ndarray, parent_temperature: np.ndarray,
    rhs_final: Callable[[np.ndarray],np.ndarray],
) -> ThermalResult:
    pop=_pop(populations); n=pop.shape[0]
    U0=_vec(parent_energy,n,'parent_energy',positive=True)
    T0=_vec(parent_temperature,n,'parent_temperature',positive=True)
    log_lo=np.log(np.maximum(T0*1.0e-12,1.0e-12))
    log_hi=np.log(np.maximum(T0*10.0,1.0e8))
    f_lo=np.asarray(balance(log_lo),dtype=np.float64)
    f_hi=np.asarray(balance(log_hi),dtype=np.float64)
    for _ in range(28):
        need=~(np.isfinite(f_hi)&(f_hi>=0.0))
        if not np.any(need): break
        log_hi=np.where(need,log_hi+np.log(10.0),log_hi)
        f_hi=np.asarray(balance(log_hi),dtype=np.float64)
    bracketed=np.isfinite(f_lo)&np.isfinite(f_hi)&(f_lo<=0.0)&(f_hi>=0.0)
    lo=log_lo.copy(); hi=log_hi.copy()
    for _ in range(80):
        mid=0.5*(lo+hi); f_mid=np.asarray(balance(mid),dtype=np.float64)
        move=np.isfinite(f_mid)&(f_mid<=0.0)
        lo=np.where(bracketed&move,mid,lo)
        hi=np.where(bracketed&~move,mid,hi)
    log_root=0.5*(lo+hi)
    T=np.where(bracketed,np.exp(log_root),T0)
    energy=np.where(bracketed,energy_from_temperature(pop,T),U0)
    residual=np.asarray(balance(np.log(T)),dtype=np.float64)
    rhs=np.asarray(rhs_final(np.log(T)),dtype=np.float64)
    scale=np.maximum.reduce([np.abs(energy),np.abs(U0),np.abs(residual),np.full(n,1e-300)])
    relative=np.where(bracketed,np.abs(residual)/scale,np.inf)
    return ThermalResult(energy,T,rhs,relative,bracketed)


def solve_backward_euler(
    *, populations: np.ndarray, parent_energy, parent_temperature, volume,
    photoheat, hubble, dt, rhs_function: RHSFunction,
) -> ThermalResult:
    pop=_pop(populations); n=pop.shape[0]
    U0=_vec(parent_energy,n,'parent_energy',positive=True)
    T0=_vec(parent_temperature,n,'parent_temperature',positive=True)
    vol=_vec(volume,n,'volume',positive=True); heat=_vec(photoheat,n,'photoheat')
    H=_vec(hubble,n,'hubble'); step=_vec(dt,n,'dt',positive=True)
    def rhs(logt): return np.asarray(rhs_function(logt,pop,vol,heat,H),dtype=np.float64)
    def balance(logt): return energy_from_temperature(pop,np.exp(logt))-U0-step*rhs(logt)
    return _root(balance=balance,populations=pop,parent_energy=U0,parent_temperature=T0,rhs_final=rhs)


def solve_trapezoid_corrector(
    *, parent_populations: np.ndarray, final_populations: np.ndarray,
    parent_energy, parent_temperature, volume0, volume1,
    photoheat0, photoheat1, hubble0, hubble1, dt,
    rhs_function: RHSFunction,
) -> ThermalResult:
    p0=_pop(parent_populations); p1=_pop(final_populations)
    if p0.shape!=p1.shape: raise ValueError('parent/final population shape mismatch')
    n=p0.shape[0]
    U0=_vec(parent_energy,n,'parent_energy',positive=True)
    T0=_vec(parent_temperature,n,'parent_temperature',positive=True)
    v0=_vec(volume0,n,'volume0',positive=True); v1=_vec(volume1,n,'volume1',positive=True)
    h0=_vec(photoheat0,n,'photoheat0'); h1=_vec(photoheat1,n,'photoheat1')
    H0=_vec(hubble0,n,'hubble0'); H1=_vec(hubble1,n,'hubble1')
    step=_vec(dt,n,'dt',positive=True)
    rhs0=np.asarray(rhs_function(np.log(T0),p0,v0,h0,H0),dtype=np.float64)
    def rhs1(logt): return np.asarray(rhs_function(logt,p1,v1,h1,H1),dtype=np.float64)
    def balance(logt):
        return energy_from_temperature(p1,np.exp(logt))-U0-0.5*step*(rhs0+rhs1(logt))
    return _root(balance=balance,populations=p1,parent_energy=U0,parent_temperature=T0,rhs_final=rhs1)
