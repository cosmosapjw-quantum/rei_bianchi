#!/usr/bin/env python3
"""Integrated nonautonomous MPRK22 + positive trapezoidal thermal trial."""
from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import math
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np

HERE=Path(__file__).resolve().parent
STAGE=HERE.parent
REPO=STAGE.parents[1]
R2A=REPO/'stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_ADAPTIVE_INTERNAL_MICROSTEP_ACCEPTANCE_AND_GLOBALIZATION_LOCK'


def _load(name: str, path: Path):
    if name in sys.modules: return sys.modules[name]
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise ImportError(path)
    m=importlib.util.module_from_spec(spec); sys.modules[name]=m; spec.loader.exec_module(m); return m

pds=_load('r2b_r2a_r1_pds_trial',HERE/'pds_decomposition.py')
mprk=_load('r2b_r2a_r1_mprk_trial',HERE/'mprk22.py')
thermal2=_load('r2b_r2a_r1_thermal_trial',HERE/'thermal_trapezoid.py')
physical=_load('r2b_r2a_r1_parent_physical',R2A/'analysis/physical_trial.py')
owner_mod=_load('r2b_r2a_r1_parent_owner',R2A/'analysis/array_owner_kernel.py')

LANES=owner_mod.LANES
LEDGER_NAMES=(
    'resolved_HI_absorption','resolved_HeI_absorption','resolved_HeII_absorption',
    'effective_subgrid_absorption','boundary_redshift_storage',
    'resolved_photoheating','unresolved_absorbed_energy','cooling',
    'expansion_work','mass_transfer_work','photon_absorption_G1',
    'photon_absorption_G2a','photon_absorption_G2b','photon_absorption_G3',
    'resolved_thermal_delta',
)


def empty_ledgers() -> dict[str,float]: return {name:0.0 for name in LEDGER_NAMES}


def condition_owner_fractions(raw: np.ndarray) -> np.ndarray:
    values=np.asarray(raw,dtype=np.float64)
    if values.ndim!=2 or values.shape[0]!=4 or np.any(~np.isfinite(values)) or np.any(values<0.0):
        raise ValueError('owner fractions must be nonnegative [4,G]')
    out=np.zeros_like(values)
    for g in range(values.shape[1]):
        support=float(np.sum(values[:,g],dtype=np.float64))
        if support==0.0: continue
        out[:,g]=values[:,g]/support
        target=int(np.argmax(values[:,g]))
        out[target,g]+=1.0-float(np.sum(out[:,g],dtype=np.float64))
    return out


def post_owner_counts(ledger: dict[str,float], counts: np.ndarray, energy: np.ndarray) -> None:
    c=np.asarray(counts,dtype=np.float64); e=np.asarray(energy,dtype=np.float64)
    if c.shape!=(4,) or e.shape!=(4,) or np.any(c<0.0) or np.any(e<0.0):
        raise ValueError('owner counts/energy must be nonnegative length four')
    ledger['effective_subgrid_absorption']+=float(c[0])
    ledger['resolved_HI_absorption']+=float(c[1])
    ledger['resolved_HeI_absorption']+=float(c[2])
    ledger['resolved_HeII_absorption']+=float(c[3])
    ledger['unresolved_absorbed_energy']+=float(e[0])
    ledger['resolved_photoheating']+=float(np.sum(e[1:],dtype=np.float64))


@dataclass(frozen=True)
class SecondOrderTrialResult:
    converged: bool
    state: Any | None
    predictor_state: Any | None
    ledger_delta: dict[str,float]
    hydrogen_residual: float
    helium_residual: float
    owner_residual: float
    photon_residual: float
    thermal_residual: float
    pds_reconstruction_residual: float
    minimum_species: float
    elapsed_s: float
    certificate: dict[str,Any]


class SecondOrderPhysicalTrial:
    def __init__(self, *, base, lane: str) -> None:
        if lane not in LANES: raise KeyError(lane)
        self.base=base; self.lane=lane
        self.inputs=base.inputs; self.forcing=base.forcing
        self.owner_kernel=base.owner_kernel; self.backend=base.backend
        self.tensor=base.tensor; self.thermal_parent=base.thermal
        self.source_rhs_calls=0

    @classmethod
    def from_repo(cls, *, repo_root: Path, lane: str):
        if lane not in LANES: raise KeyError(lane)
        return cls(base=physical.PhysicalTrialSolver.from_repo(repo_root=Path(repo_root),lane=lane),lane=lane)

    def _owner(self,state,point):
        return self.owner_kernel.evaluate_values(
            kappa_total=point.kappa,current_total=point.current,
            external_subgrid=point.external_subgrid,z=point.z,gamma_hi=point.gamma_hi,
            state=state,lane=self.lane,
        )

    def _rhs_flux(self,state,owner,point):
        self.source_rhs_calls+=1
        y=np.asarray(state.values,dtype=np.float64)
        nh=y[0]+y[1]; nhe=y[2]+y[3]+y[4]
        volume=self.inputs.comoving_volume_cm3/(1.0+point.z)**3
        photo=self.backend.photo_fields(owner)
        q=self.backend._coordinates(state)
        rhs=np.asarray(self.backend.micro._batch_rhs(
            self.backend.micro.jnp.asarray(q),self.backend.micro.jnp.asarray(nh),
            self.backend.micro.jnp.asarray(nhe),self.backend.micro.jnp.asarray(volume),
            self.backend.micro.jnp.asarray(photo.HI),self.backend.micro.jnp.asarray(photo.HeI),
            self.backend.micro.jnp.asarray(photo.HeII),
        ),dtype=np.float64)
        flux=pds.decompose_conservative_rhs(rhs,relative_tolerance=1.0e-11)
        reconstructed=pds.flux_rhs(flux)
        scale=np.maximum(np.max(np.abs(rhs),axis=1),1.0)
        residual=float(np.max(np.max(np.abs(reconstructed-rhs),axis=1)/scale))
        return rhs,flux,photo,volume,residual

    def _owner_energy_rates(self,owner) -> np.ndarray:
        node=np.asarray(owner.node_current,dtype=np.float64)
        excess=self.backend.excess_eV
        rates=np.zeros(4,dtype=np.float64)
        rates[0]=float(np.sum(node[0]*excess[0,:,None],dtype=np.float64))*physical.EV_ERG
        rates[1]=float(np.sum(node[1]*excess[0,:,None],dtype=np.float64))*physical.EV_ERG
        rates[2]=float(np.sum(node[2]*excess[1,:,None],dtype=np.float64))*physical.EV_ERG
        rates[3]=float(np.sum(node[3]*excess[2,:,None],dtype=np.float64))*physical.EV_ERG
        return rates

    def solve(self, *, state, t0: float, t1: float, partition: int, trial_kind: str) -> SecondOrderTrialResult:
        started=time.perf_counter(); ledgers=empty_ledgers()
        parent=state.mutable_copy(); y0=np.asarray(parent.values[:5].T,dtype=np.float64)
        try:
            if not (math.isfinite(t0) and math.isfinite(t1) and t1>t0): raise ValueError('invalid interval')
            dt=float(t1-t0); point0=self.forcing.point(interval=0,time_s=t0); point1=self.forcing.point(interval=0,time_s=t1)
            step=self.forcing.step(interval=0,t0_s=t0,t1_s=t1)
            owner0=self._owner(parent,point0)
            rhs0,flux0,photo0,volume0,pds0=self._rhs_flux(parent,owner0,point0)
            predictor_pop=mprk.patankar_euler(y0=y0,flux=flux0,dt=dt)
            thermal_pred=thermal2.solve_backward_euler(
                populations=predictor_pop,parent_energy=parent.values[5],
                parent_temperature=parent.temperature_K,volume=volume0,
                photoheat=photo0.heating,hubble=np.full(parent.node_count,point0.hubble_s_inv),
                dt=np.full(parent.node_count,dt),rhs_function=self.thermal_parent._thermal_rhs_numpy,
            )
            if not np.all(thermal_pred.bracketed) or np.max(thermal_pred.relative_residual)>1.0e-10:
                raise FloatingPointError('THERMAL_PREDICTOR')
            predictor_values=np.ascontiguousarray(np.vstack([predictor_pop.T,thermal_pred.energy]))
            predictor_state=self.tensor.ArrayState(predictor_values,np.ascontiguousarray(thermal_pred.temperature))
            owner1=self._owner(predictor_state,point1)
            rhs1,flux1,photo1,volume1,pds1=self._rhs_flux(predictor_state,owner1,point1)
            corrector_pop=mprk.mprk22_corrector(
                y0=y0,predictor=predictor_pop,stage_flux=flux0,final_flux=flux1,dt=dt,
            )
            thermal_final=thermal2.solve_trapezoid_corrector(
                parent_populations=y0,final_populations=corrector_pop,
                parent_energy=parent.values[5],parent_temperature=parent.temperature_K,
                volume0=volume0,volume1=volume1,photoheat0=photo0.heating,photoheat1=photo1.heating,
                hubble0=np.full(parent.node_count,point0.hubble_s_inv),
                hubble1=np.full(parent.node_count,point1.hubble_s_inv),dt=np.full(parent.node_count,dt),
                rhs_function=self.thermal_parent._thermal_rhs_numpy,
            )
            if not np.all(thermal_final.bracketed) or np.max(thermal_final.relative_residual)>1.0e-10:
                raise FloatingPointError('THERMAL_CORRECTOR')
            values=np.ascontiguousarray(np.vstack([corrector_pop.T,thermal_final.energy]))
            final=self.tensor.ArrayState(values,np.ascontiguousarray(thermal_final.temperature))
            nh0=y0[:,0]+y0[:,1]; nhe0=np.sum(y0[:,2:5],axis=1,dtype=np.float64)
            hres=float(np.max(np.abs(corrector_pop[:,0]+corrector_pop[:,1]-nh0)/np.maximum(nh0,1e-300)))
            heres=float(np.max(np.abs(np.sum(corrector_pop[:,2:5],axis=1)-nhe0)/np.maximum(nhe0,1e-300)))
            owner_res=float(max(owner0.max_kappa_residual,owner0.max_current_residual,owner0.max_node_residual,
                                owner1.max_kappa_residual,owner1.max_current_residual,owner1.max_node_residual))
            fractions=condition_owner_fractions(0.5*(owner0.owner_fraction+owner1.owner_fraction))
            exact_group_counts=np.asarray(step.current,dtype=np.float64)*dt
            count_matrix=fractions*exact_group_counts[None,:]
            photon_res=float(np.max(np.abs(np.sum(count_matrix,axis=0)-exact_group_counts)/np.maximum(np.abs(exact_group_counts),1.0)))
            counts=np.sum(count_matrix,axis=1,dtype=np.float64)
            energies=0.5*dt*(self._owner_energy_rates(owner0)+self._owner_energy_rates(owner1))
            post_owner_counts(ledgers,counts,energies)
            for gi,g in enumerate(('G1','G2a','G2b','G3')):
                ledgers[f'photon_absorption_{g}']=float(exact_group_counts[gi])
            cool0,exp0=self.thermal_parent.thermal_terms_numpy(np.log(parent.temperature_K),y0,volume0,point0.hubble_s_inv)
            cool1,exp1=self.thermal_parent.thermal_terms_numpy(np.log(final.temperature_K),corrector_pop,volume1,point1.hubble_s_inv)
            ledgers['cooling']=float(0.5*dt*np.sum(cool0+cool1,dtype=np.float64))
            ledgers['expansion_work']=float(0.5*dt*np.sum(exp0+exp1,dtype=np.float64))
            ledgers['resolved_thermal_delta']=float(np.sum(final.values[5]-parent.values[5],dtype=np.float64))
            unsupported=~self.inputs.owner_support.astype(bool)
            structural=(np.count_nonzero(owner0.owner_current[unsupported])==0 and np.count_nonzero(owner1.owner_current[unsupported])==0)
            if not structural: raise FloatingPointError('STRUCTURAL_ZERO')
            return SecondOrderTrialResult(
                converged=True,state=final,predictor_state=predictor_state,ledger_delta=ledgers,
                hydrogen_residual=hres,helium_residual=heres,owner_residual=owner_res,
                photon_residual=photon_res,thermal_residual=float(np.max(thermal_final.relative_residual)),
                pds_reconstruction_residual=max(pds0,pds1),minimum_species=float(np.min(corrector_pop)),
                elapsed_s=float(time.perf_counter()-started),certificate={
                    'classification':'PASS','partition':int(partition),'trial_kind':str(trial_kind),
                    'source_rhs_calls':self.source_rhs_calls,
                },
            )
        except Exception as exc:
            classification=str(exc) if isinstance(exc,FloatingPointError) else type(exc).__name__
            return SecondOrderTrialResult(
                converged=False,state=None,predictor_state=None,ledger_delta=ledgers,
                hydrogen_residual=math.inf,helium_residual=math.inf,owner_residual=math.inf,
                photon_residual=math.inf,thermal_residual=math.inf,pds_reconstruction_residual=math.inf,
                minimum_species=0.0,elapsed_s=float(time.perf_counter()-started),
                certificate={'classification':classification,'exception':type(exc).__name__,'message':str(exc)},
            )
