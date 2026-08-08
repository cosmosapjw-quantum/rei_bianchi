#!/usr/bin/env python3
"""Continuous PCHIP forcing adapter over immutable tensorized BDF nodes."""
from __future__ import annotations
from dataclasses import dataclass
import math
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator

GROUPS=("G1","G2a","G2b","G3")
MPC_CM=3.085677581491367e24
H0=67.4*1.0e5/MPC_CM
OMEGA_M=0.315
OMEGA_L=0.685


def hubble_s_inv(z: float) -> float:
    redshift=float(z)
    return H0*math.sqrt(OMEGA_M*(1.0+redshift)**3+OMEGA_L)


@dataclass(frozen=True)
class ForcingPoint:
    interval: int
    time_s: float
    z: float
    gamma_hi: float
    kappa: np.ndarray
    current: np.ndarray
    external_subgrid: np.ndarray
    hubble_s_inv: float


@dataclass(frozen=True)
class ForcingStep:
    interval: int
    t0_s: float
    t1_s: float
    dt_s: float
    midpoint_s: float
    z: float
    gamma_hi: float
    kappa: np.ndarray
    current: np.ndarray
    external_subgrid: np.ndarray
    hubble_s_inv: float


class ArrayContinuousForcing:
    def __init__(self, *, inputs) -> None:
        self.inputs=inputs
        self._models=[]
        for interval in range(5):
            times=np.asarray(inputs.time_s[interval],dtype=float)
            if times.shape!=(17,) or not np.all(np.diff(times)>0.0):
                raise ValueError('forcing interval must have 17 increasing nodes')
            self._models.append({
                'times':times,
                'kappa':[PchipInterpolator(times,inputs.kappa[interval,:,g],extrapolate=False) for g in range(4)],
                'current':[PchipInterpolator(times,inputs.absorption[interval,:,g],extrapolate=False) for g in range(4)],
                'external':[PchipInterpolator(times,inputs.external_subgrid[interval,:,g],extrapolate=False) for g in range(4)],
                'z':PchipInterpolator(times,inputs.z_mid[interval],extrapolate=False),
                'gamma':PchipInterpolator(times,inputs.gamma_hi[interval],extrapolate=False),
            })

    @classmethod
    def from_repo(cls, *, repo_root: Path, inputs):
        del repo_root
        return cls(inputs=inputs)

    def _model(self,interval:int):
        if not 0<=int(interval)<5:
            raise IndexError('forcing interval out of range')
        return self._models[int(interval)]

    def duration_seconds(self, interval: int) -> float:
        t=self._model(interval)['times']
        return float(t[-1]-t[0])

    def point(self, *, interval: int, time_s: float) -> ForcingPoint:
        m=self._model(interval); t=float(time_s)
        if t<m['times'][0] or t>m['times'][-1] or not math.isfinite(t):
            raise ValueError('forcing point outside interval')
        kappa=np.array([float(f(t)) for f in m['kappa']],dtype=float)
        current=np.array([float(f(t)) for f in m['current']],dtype=float)
        external=np.array([float(f(t)) for f in m['external']],dtype=float)
        z=float(m['z'](t)); gamma=float(m['gamma'](t))
        return ForcingPoint(int(interval),t,z,gamma,kappa,current,external,hubble_s_inv(z))

    def step(self, *, interval: int, t0_s: float, t1_s: float) -> ForcingStep:
        m=self._model(interval); t0=float(t0_s); t1=float(t1_s); dt=t1-t0
        if not (math.isfinite(t0) and math.isfinite(t1) and dt>0.0):
            raise ValueError('adaptive forcing step requires positive duration')
        if t0<m['times'][0] or t1>m['times'][-1]:
            raise ValueError('adaptive forcing step outside interval')
        midpoint=0.5*(t0+t1)
        kappa=np.array([float(f.integrate(t0,t1))/dt for f in m['kappa']],dtype=float)
        current=np.array([float(f.integrate(t0,t1))/dt for f in m['current']],dtype=float)
        external=np.array([float(f.integrate(t0,t1))/dt for f in m['external']],dtype=float)
        z=float(m['z'](midpoint)); gamma=float(m['gamma'](midpoint))
        if any(np.any(~np.isfinite(x)) or np.any(x<0.0) for x in (kappa,current,external)):
            raise ValueError('interpolated forcing left the nonnegative cone')
        return ForcingStep(int(interval),t0,t1,dt,midpoint,z,gamma,kappa,current,external,hubble_s_inv(z))
