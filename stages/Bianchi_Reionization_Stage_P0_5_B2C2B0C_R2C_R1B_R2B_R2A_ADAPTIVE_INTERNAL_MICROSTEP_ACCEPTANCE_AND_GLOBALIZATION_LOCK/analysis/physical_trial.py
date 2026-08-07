#!/usr/bin/env python3
"""Optimized physical owner/chemistry/thermal trial for R2B-R2A.

Pandas and source tables are used only during construction.  Every Picard map
uses contiguous NumPy arrays, the source-locked JAX 5x5 event matrix compiled at
one fixed batch shape, a batched NumPy linear solve, and the independent NumPy
positive thermal root.
"""
from __future__ import annotations
from dataclasses import dataclass
import importlib.util
import math
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np
import pandas as pd

EV_ERG=1.602176634e-12
LEDGER_NAMES=(
    'resolved_HI_absorption','resolved_HeI_absorption','resolved_HeII_absorption',
    'effective_subgrid_absorption','boundary_redshift_storage',
    'resolved_photoheating','unresolved_absorbed_energy','cooling',
    'expansion_work','mass_transfer_work',
)


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class PhotoFields:
    HI: np.ndarray
    HeI: np.ndarray
    HeII: np.ndarray
    heating: np.ndarray
    unresolved_heating: np.ndarray


class ArrayChemThermalBackend:
    def __init__(self, *, repo_root: Path, inputs, thermal_backend, excess_eV: np.ndarray) -> None:
        root=Path(repo_root)
        old=root/'stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2_OWNER_CORRECT_PHOTON_CONSERVING_NONAUTONOMOUS_FIXED_POINT_HISTORY_RERUN/analysis/microphysics.py'
        self.micro=_load('r2b_r2a_source_microphysics',old)
        self.inputs=inputs
        self.thermal=thermal_backend
        self.excess_eV=np.asarray(excess_eV,dtype=float)
        if self.excess_eV.shape != (3,4):
            raise ValueError('heating moment matrix must have shape [species,group]')
        self.compile_count=0
        self.map_calls=0

    @staticmethod
    def _coordinates(state) -> np.ndarray:
        y=state.values
        nh=y[0]+y[1]; nhe=y[2]+y[3]+y[4]
        xh=np.divide(y[1],nh)
        hei=np.divide(y[2],nhe); heii=np.divide(y[3],nhe); heiii=np.divide(y[4],nhe)
        if np.any((xh<=0)|(xh>=1)) or np.any(hei<=0) or np.any(heii<=0) or np.any(heiii<=0):
            raise ValueError('chemistry coordinate requires strictly interior fractions')
        return np.ascontiguousarray(np.column_stack([
            np.log(xh)-np.log1p(-xh),
            np.log(heii)-np.log(hei),
            np.log(heiii)-np.log(hei),
            np.log(state.temperature_K),
        ]),dtype=float)

    def photo_fields(self, owner_eval) -> PhotoFields:
        node=np.asarray(owner_eval.node_current,dtype=float)
        # owner order: subgrid, HI, HeI, HeII
        hi=np.sum(node[1],axis=0,dtype=np.float64)
        hei=np.sum(node[2],axis=0,dtype=np.float64)
        heii=np.sum(node[3],axis=0,dtype=np.float64)
        heat=(
            np.sum(node[1]*self.excess_eV[0,:,None],axis=0,dtype=np.float64)
            +np.sum(node[2]*self.excess_eV[1,:,None],axis=0,dtype=np.float64)
            +np.sum(node[3]*self.excess_eV[2,:,None],axis=0,dtype=np.float64)
        )*EV_ERG
        unresolved=np.sum(node[0]*self.excess_eV[0,:,None],axis=0,dtype=np.float64)*EV_ERG
        return PhotoFields(hi,hei,heii,heat,unresolved)

    def update(self, *, parent, coefficient, owner_eval, forcing_step, tensor_module, picard_module):
        self.map_calls += 1
        y_parent=np.asarray(parent.values,dtype=float)
        y_coeff=np.asarray(coefficient.values,dtype=float)
        nh=y_parent[0]+y_parent[1]; nhe=y_parent[2]+y_parent[3]+y_parent[4]
        volume=self.inputs.comoving_volume_cm3/(1.0+forcing_step.z)**3
        photo=self.photo_fields(owner_eval)
        try:
            q=self._coordinates(coefficient)
            matrix_device=self.micro._batch_linear_matrix(
                self.micro.jnp.asarray(q),self.micro.jnp.asarray(nh),self.micro.jnp.asarray(nhe),
                self.micro.jnp.asarray(volume),self.micro.jnp.asarray(photo.HI),
                self.micro.jnp.asarray(photo.HeI),self.micro.jnp.asarray(photo.HeII),
            )
            matrices=np.asarray(matrix_device)
            self.compile_count=1
            lhs=np.eye(5,dtype=float)[None,:,:]-forcing_step.dt_s*matrices
            parent_pop=y_parent[:5].T
            pop_new=np.linalg.solve(lhs,parent_pop[...,None])[...,0]
        except (ValueError,np.linalg.LinAlgError,FloatingPointError) as exc:
            return picard_module.MapEvaluation(
                state=None,feasible=False,certificate={
                    'classification':'MATERIAL_CAPACITY','exception':type(exc).__name__,
                }
            )
        min_species=np.min(pop_new,axis=1)
        h_res=(pop_new[:,0]+pop_new[:,1])-nh
        he_res=(pop_new[:,2]+pop_new[:,3]+pop_new[:,4])-nhe
        population_ok=np.all(np.isfinite(pop_new),axis=1)&(min_species>0.0)
        if not np.all(population_ok):
            bad=int(np.flatnonzero(~population_ok)[0])
            return picard_module.MapEvaluation(
                state=None,feasible=False,
                hydrogen_residual=float(np.max(np.abs(h_res)/np.maximum(nh,1e-300))),
                helium_residual=float(np.max(np.abs(he_res)/np.maximum(nhe,1e-300))),
                certificate={'classification':'MATERIAL_CAPACITY','node_index':bad,'minimum_species':float(min_species[bad])},
            )
        thermal=self.thermal.solve(
            populations=pop_new,parent_energy=y_parent[5],
            parent_temperature=parent.temperature_K,volume=volume,
            photoheat=photo.heating,hubble=forcing_step.hubble_s_inv,
            dt=forcing_step.dt_s,
        )
        thermal_ok=(thermal.bracketed & np.isfinite(thermal.energy)&np.isfinite(thermal.temperature)
                    &(thermal.energy>0)&(thermal.temperature>0)&np.isfinite(thermal.relative_residual)
                    &(thermal.relative_residual<=1e-10))
        if not np.all(thermal_ok):
            bad=int(np.flatnonzero(~thermal_ok)[0])
            classification='THERMAL_CONE' if not bool(thermal.bracketed[bad]) else 'THERMAL_BALANCE'
            return picard_module.MapEvaluation(
                state=None,feasible=False,
                certificate={'classification':classification,'node_index':bad,
                             'thermal_residual':float(thermal.relative_residual[bad])},
            )
        values=np.ascontiguousarray(np.vstack([pop_new.T,thermal.energy]))
        state=tensor_module.ArrayState(values,np.ascontiguousarray(thermal.temperature))
        owner_res=max(owner_eval.max_kappa_residual,owner_eval.max_current_residual,owner_eval.max_node_residual)
        unsupported=~self.inputs.owner_support.astype(bool)
        structural=(np.count_nonzero(owner_eval.owner_current[unsupported])==0
                    and np.count_nonzero(owner_eval.node_current[unsupported])==0)
        return picard_module.MapEvaluation(
            state=state,feasible=True,owner_residual=float(owner_res),
            photon_residual=float(max(owner_eval.max_current_residual,owner_eval.max_node_residual)),
            hydrogen_residual=float(np.max(np.abs(h_res)/np.maximum(nh,1e-300))),
            helium_residual=float(np.max(np.abs(he_res)/np.maximum(nhe,1e-300))),
            thermal_residual=float(np.max(thermal.relative_residual)),
            unresolved_energy_residual=0.0,structural_zero_ok=bool(structural),
            certificate={'minimum_species':float(np.min(min_species))},
        )

    def ledger_delta(self, *, parent, final_state, owner_eval, forcing_step, thermal_module) -> dict[str,float]:
        photo=self.photo_fields(owner_eval)
        dt=float(forcing_step.dt_s)
        node=np.asarray(owner_eval.node_current,dtype=float)
        owner_rates=np.sum(node,axis=(1,2),dtype=np.float64)
        group_rates=np.sum(node,axis=(0,2),dtype=np.float64)
        pop=final_state.values[:5].T
        volume=self.inputs.comoving_volume_cm3/(1.0+forcing_step.z)**3
        cooling,expansion=thermal_module.thermal_terms_numpy(
            np.log(final_state.temperature_K),pop,volume,forcing_step.hubble_s_inv
        )
        ledgers={name:0.0 for name in LEDGER_NAMES}
        ledgers.update({
            'effective_subgrid_absorption':float(owner_rates[0]*dt),
            'resolved_HI_absorption':float(owner_rates[1]*dt),
            'resolved_HeI_absorption':float(owner_rates[2]*dt),
            'resolved_HeII_absorption':float(owner_rates[3]*dt),
            'resolved_photoheating':float(np.sum(photo.heating,dtype=np.float64)*dt),
            'unresolved_absorbed_energy':float(np.sum(photo.unresolved_heating,dtype=np.float64)*dt),
            'cooling':float(np.sum(cooling,dtype=np.float64)*dt),
            'expansion_work':float(np.sum(expansion,dtype=np.float64)*dt),
        })
        for gi,group in enumerate(('G1','G2a','G2b','G3')):
            ledgers[f'photon_absorption_{group}']=float(group_rates[gi]*dt)
        ledgers['resolved_thermal_delta']=float(np.sum(final_state.values[5]-parent.values[5],dtype=np.float64))
        return ledgers


class PhysicalTrialSolver:
    def __init__(self, *, repo_root: Path, lane: str, inputs, forcing, owner_kernel,
                 backend, tensor_module, picard_module, adaptive_module, thermal_module) -> None:
        self.repo_root=Path(repo_root); self.lane=str(lane); self.inputs=inputs
        self.forcing=forcing; self.owner_kernel=owner_kernel; self.backend=backend
        self.tensor=tensor_module; self.picard=picard_module; self.adaptive=adaptive_module
        self.thermal=thermal_module
        self.trial_records: list[dict[str, Any]] = []
        self.globalized=picard_module.GlobalizedPicard(
            tolerance=1e-10,owner_nuclei_tolerance=1e-11,photon_tolerance=1e-8,
            thermal_tolerance=1e-10,max_iterations=40,
        )

    @classmethod
    def from_repo(cls, *, repo_root: Path, lane: str):
        root=Path(repo_root); here=Path(__file__).resolve().parent
        tensor=_load('r2b_r2a_tensorized',here/'tensorized_inputs.py')
        owner=_load('r2b_r2a_array_owner',here/'array_owner_kernel.py')
        forcing_mod=_load('r2b_r2a_array_forcing',here/'array_forcing.py')
        thermal=_load('r2b_r2a_thermal_backends',here/'thermal_backends.py')
        picard=_load('r2b_r2a_globalized_picard',here/'globalized_picard.py')
        adaptive=_load('r2b_r2a_adaptive_controller',here/'adaptive_controller.py')
        inputs=tensor.load_tensorized_inputs(repo_root=root)
        forcing=forcing_mod.ArrayContinuousForcing.from_repo(repo_root=root,inputs=inputs)
        kernel=owner.ArrayOwnerKernel.from_repo(repo_root=root,inputs=inputs)
        r1b1=root/'stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R1_CANONICAL_TIME_RESOLVED_GROUP_BOUNDARY_FLUX_DYNAMIC_OPACITY_AND_HEATING_MOMENT_EXTRACTION_LOCK_RERUN_V2'
        frame=pd.read_csv(r1b1/'data/heating_lock/bdf_heating_moment_calibration.csv')
        excess=np.zeros((3,4),dtype=float)
        for si,species in enumerate(('HI','HeI','HeII')):
            for gi,group in enumerate(('G1','G2a','G2b','G3')):
                row=frame[(frame.species==species)&(frame.group==group)]
                if len(row)!=1:
                    raise ValueError(f'missing heating moment {species}/{group}')
                excess[si,gi]=float(row.iloc[0].canonical_excess_eV)
        backend=ArrayChemThermalBackend(
            repo_root=root,inputs=inputs,thermal_backend=thermal.NumpyThermalBackend(),
            excess_eV=excess,
        )
        return cls(repo_root=root,lane=lane,inputs=inputs,forcing=forcing,
                   owner_kernel=kernel,backend=backend,tensor_module=tensor,
                   picard_module=picard,adaptive_module=adaptive,thermal_module=thermal)

    def owner_evaluation(self, *, state, step):
        return self.owner_kernel.evaluate_values(
            kappa_total=step.kappa,current_total=step.current,
            external_subgrid=step.external_subgrid,z=step.z,gamma_hi=step.gamma_hi,
            state=state,lane=self.lane,
        )

    def solve_trial(self, parent, t0: float, t1: float, partition: int, trial_kind: str):
        started=time.perf_counter()
        step=self.forcing.step(interval=0,t0_s=t0,t1_s=t1)
        def map_state(iterate):
            owner_eval=self.owner_evaluation(state=iterate,step=step)
            return self.backend.update(
                parent=parent,coefficient=iterate,owner_eval=owner_eval,
                forcing_step=step,tensor_module=self.tensor,picard_module=self.picard,
            )
        result=self.globalized.solve(parent=parent,map_state=map_state)
        if result.converged:
            owner_eval=self.owner_evaluation(state=result.state,step=step)
            delta=self.backend.ledger_delta(
                parent=parent,final_state=result.state,owner_eval=owner_eval,
                forcing_step=step,thermal_module=self.thermal,
            )
        else:
            delta={name:0.0 for name in LEDGER_NAMES}
        self.trial_records.append({
            'trial_kind':str(trial_kind),
            'partition':int(partition),
            't0_s':float(t0),
            't1_s':float(t1),
            'dt_s':float(t1-t0),
            'elapsed_s':float(time.perf_counter()-started),
            'converged':bool(result.converged),
            'iterations':int(result.iterations),
            'map_calls':int(result.map_calls),
            'residual':float(result.residual),
            'minimum_species':float(result.minimum_species),
            'max_hydrogen_residual':float(result.max_hydrogen_residual),
            'max_helium_residual':float(result.max_helium_residual),
            'max_owner_residual':float(result.max_owner_residual),
            'max_photon_residual':float(result.max_photon_residual),
            'max_thermal_residual':float(result.max_thermal_residual),
            'damping_trace':[float(v) for v in result.damping_trace],
            'certificate':dict(result.certificate),
        })
        return self.adaptive.MicroTrial(result=result,ledger_delta=delta)
