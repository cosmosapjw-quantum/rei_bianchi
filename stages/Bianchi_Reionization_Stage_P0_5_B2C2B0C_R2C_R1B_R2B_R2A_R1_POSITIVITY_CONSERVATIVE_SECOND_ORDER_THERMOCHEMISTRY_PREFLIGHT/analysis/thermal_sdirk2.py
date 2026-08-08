#!/usr/bin/env python3
"""L-stable two-stage SDIRK2 thermal solve in positive log-temperature coordinates."""
from __future__ import annotations
from dataclasses import dataclass
import importlib.util,sys
from pathlib import Path
from typing import Callable
import numpy as np

HERE=Path(__file__).resolve().parent

def _load():
    name='r2b_r2a_r1_thermal_base_for_sdirk'
    if name in sys.modules: return sys.modules[name]
    spec=importlib.util.spec_from_file_location(name,HERE/'thermal_trapezoid.py')
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

base=_load()
KB_ERG=base.KB_ERG
GAMMA=1.0-1.0/np.sqrt(2.0)

@dataclass(frozen=True)
class SDIRK2ThermalResult:
    stage: base.ThermalResult
    final: base.ThermalResult

energy_from_temperature=base.energy_from_temperature


def solve_sdirk2(
    *, parent_populations: np.ndarray, stage_populations: np.ndarray,
    final_populations: np.ndarray, parent_energy, parent_temperature,
    stage_volume, final_volume, stage_photoheat, final_photoheat,
    stage_hubble, final_hubble, dt,
    rhs_function: Callable,
) -> SDIRK2ThermalResult:
    p0=base._pop(parent_populations); ps=base._pop(stage_populations); pf=base._pop(final_populations)
    if p0.shape!=ps.shape or p0.shape!=pf.shape: raise ValueError('population shape mismatch')
    n=p0.shape[0]
    U0=base._vec(parent_energy,n,'parent_energy',positive=True)
    T0=base._vec(parent_temperature,n,'parent_temperature',positive=True)
    step=base._vec(dt,n,'dt',positive=True)
    vs=base._vec(stage_volume,n,'stage_volume',positive=True)
    vf=base._vec(final_volume,n,'final_volume',positive=True)
    hs=base._vec(stage_photoheat,n,'stage_photoheat')
    hf=base._vec(final_photoheat,n,'final_photoheat')
    Hs=base._vec(stage_hubble,n,'stage_hubble')
    Hf=base._vec(final_hubble,n,'final_hubble')
    stage=base.solve_backward_euler(
        populations=ps,parent_energy=U0,parent_temperature=T0,volume=vs,
        photoheat=hs,hubble=Hs,dt=GAMMA*step,rhs_function=rhs_function,
    )
    rhs_stage=stage.rhs
    def rhs_final(logt):
        return np.asarray(rhs_function(logt,pf,vf,hf,Hf),dtype=np.float64)
    def balance(logt):
        return (base.energy_from_temperature(pf,np.exp(logt))-U0
                -step*((1.0-GAMMA)*rhs_stage+GAMMA*rhs_final(logt)))
    final=base._root(
        balance=balance,populations=pf,parent_energy=U0,
        parent_temperature=T0,rhs_final=rhs_final,
    )
    # A failed stage is load-bearing even if the final equation happened to bracket.
    final=base.ThermalResult(
        final.energy,final.temperature,final.rhs,final.relative_residual,
        final.bracketed & stage.bracketed,
    )
    return SDIRK2ThermalResult(stage=stage,final=final)
