#!/usr/bin/env python3
"""Branch-policy MPRK22 + SDIRK2 microstep with event-resolved OTS ledgers."""
from __future__ import annotations

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
R1=REPO/'stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R1_POSITIVITY_CONSERVATIVE_SECOND_ORDER_THERMOCHEMISTRY_PREFLIGHT/analysis'
R2A=REPO/'stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_ADAPTIVE_INTERNAL_MICROSTEP_ACCEPTANCE_AND_GLOBALIZATION_LOCK/analysis'


def _load(name: str,path: Path):
    if name in sys.modules:return sys.modules[name]
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise ImportError(path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module


fast=_load('r2b_r2a_r1a_parent_fast_trial',R1/'second_order_sdirk_fast_trial.py')
policy_mod=_load('r2b_r2a_r1a_uncertainty_policy',HERE/'uncertainty_policy.py')
event_mod=_load('r2b_r2a_r1a_event_operator',HERE/'event_uncertainty_operator.py')

EXTRA_LEDGER_NAMES=(
    'ots_resolved_heating','ots_unresolved_energy','ots_escaped_energy',
    'ots_chemical_energy','ots_augmented_energy_residual',
)


class UncertaintySecondOrderTrial(fast.SecondOrderSDIRKFastTrial):
    """One fixed branch policy evaluated without the legacy summed-RHS path."""

    def __init__(self, *, base, lane: str, v_policy: str, f_value: float) -> None:
        super().__init__(base=base,lane=lane)
        if v_policy not in policy_mod.V_POLICIES:raise KeyError(v_policy)
        if float(f_value) not in policy_mod.F_ENDPOINTS:raise ValueError('unsupported f endpoint')
        self.v_policy=str(v_policy);self.f_value=float(f_value)
        self.legacy_rhs_calls=0

    @classmethod
    def from_repo(cls, *, repo_root: Path, lane: str, v_policy: str, f_value: float):
        base_solver=fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=Path(repo_root),lane=lane)
        return cls(base=base_solver,lane=lane,v_policy=v_policy,f_value=f_value)

    def _event_evaluation(self,state,owner,point):
        y=np.asarray(state.values,dtype=np.float64)
        volume=self.inputs.comoving_volume_cm3/(1.0+point.z)**3
        photo=self.backend.photo_fields(owner)
        v=policy_mod.build_v_field_from_temperature(self.v_policy,state.temperature_K)
        f=policy_mod.build_f_field(self.f_value,state.node_count)
        event=event_mod.evaluate_event_flux(
            populations=y[:5].T,
            temperature_K=state.temperature_K,
            proper_volume_cm3=volume,
            photo_hi=photo.HI,
            photo_hei=photo.HeI,
            photo_heii=photo.HeII,
            v=v,
            f=f,
        )
        adjusted=fast.base.physical.PhotoFields(
            HI=photo.HI,
            HeI=photo.HeI,
            HeII=photo.HeII,
            heating=np.ascontiguousarray(photo.heating+event.resolved_ots_heating_erg_s),
            unresolved_heating=np.ascontiguousarray(photo.unresolved_heating+event.unresolved_ots_energy_erg_s),
        )
        return event,adjusted,volume

    def _rhs_flux(self,state,owner,point):
        self.source_rhs_calls+=1
        event,photo,volume=self._event_evaluation(state,owner,point)
        return event.population_rhs,event.pds_flux,photo,volume,event.pds_reconstruction_residual,event

    @staticmethod
    def _integrated_event_ledgers(*,dt: float,stage,final) -> dict[str,float]:
        gamma=fast.sdirk.GAMMA
        def integrate(name: str)->float:
            a=np.asarray(getattr(stage,name),dtype=np.float64)
            b=np.asarray(getattr(final,name),dtype=np.float64)
            return float(dt*np.sum((1.0-gamma)*a+gamma*b,dtype=np.float64))
        rows={
            'ots_resolved_heating':integrate('resolved_ots_heating_erg_s'),
            'ots_unresolved_energy':integrate('unresolved_ots_energy_erg_s'),
            'ots_escaped_energy':integrate('escaped_ots_energy_erg_s'),
            'ots_chemical_energy':integrate('chemical_ots_energy_rate_erg_s'),
        }
        rows['ots_augmented_energy_residual']=math.fsum((
            rows['ots_resolved_heating'],rows['ots_unresolved_energy'],
            rows['ots_escaped_energy'],rows['ots_chemical_energy'],
        ))
        return rows

    def solve(self, *, state, t0: float, t1: float, partition: int, trial_kind: str):
        started=time.perf_counter();ledgers=fast.base.empty_ledgers();parent=state.mutable_copy()
        ledgers.update({name:0.0 for name in EXTRA_LEDGER_NAMES})
        y0=np.asarray(parent.values[:5].T,dtype=np.float64)
        try:
            if not(math.isfinite(t0) and math.isfinite(t1) and t1>t0):raise ValueError('invalid interval')
            dt=float(t1-t0);tg=t0+fast.sdirk.GAMMA*dt
            p0=self.forcing.point(interval=0,time_s=t0)
            pg=self.forcing.point(interval=0,time_s=tg)
            p1=self.forcing.point(interval=0,time_s=t1)
            step=self.forcing.step(interval=0,t0_s=t0,t1_s=t1)

            o0=self._owner(parent,p0)
            rhs0,f0,photo0,v0,r0,e0=self._rhs_flux(parent,o0,p0)
            predictor_pop=fast.base.mprk.patankar_euler(y0=y0,flux=f0,dt=dt)
            thermal_predictor=fast.sdirk.solve_backward_euler_fast(
                populations=predictor_pop,parent_energy=parent.values[5],parent_temperature=parent.temperature_K,
                volume=v0,photoheat=photo0.heating,hubble=np.full(parent.node_count,p0.hubble_s_inv),
                dt=np.full(parent.node_count,dt))
            if not np.all(thermal_predictor.bracketed):raise FloatingPointError('THERMAL_PREDICTOR')
            pred_values=np.ascontiguousarray(np.vstack([predictor_pop.T,thermal_predictor.energy]))
            predictor_state=self.tensor.ArrayState(pred_values,np.ascontiguousarray(thermal_predictor.temperature))

            o1_pred=self._owner(predictor_state,p1)
            rhs1,f1,photo1_pred,v1,r1,e1=self._rhs_flux(predictor_state,o1_pred,p1)
            corrector_pop=fast.base.mprk.mprk22_corrector(
                y0=y0,predictor=predictor_pop,stage_flux=f0,final_flux=f1,dt=dt)

            gamma_pop=fast.base.mprk.patankar_euler(y0=y0,flux=f0,dt=fast.sdirk.GAMMA*dt)
            gamma_energy=fast.sdirk.energy_from_temperature(gamma_pop,parent.temperature_K)
            gamma_state=self.tensor.ArrayState(
                np.ascontiguousarray(np.vstack([gamma_pop.T,gamma_energy])),parent.temperature_K.copy())
            og=self._owner(gamma_state,pg)
            eg,photog,vg=self._event_evaluation(gamma_state,og,pg)

            final_provisional_energy=fast.sdirk.energy_from_temperature(corrector_pop,thermal_predictor.temperature)
            final_provisional=self.tensor.ArrayState(
                np.ascontiguousarray(np.vstack([corrector_pop.T,final_provisional_energy])),
                thermal_predictor.temperature.copy())
            of=self._owner(final_provisional,p1)
            ef,photof,vf=self._event_evaluation(final_provisional,of,p1)

            thermal=fast.sdirk.solve_sdirk2_fast(
                parent_populations=y0,stage_populations=gamma_pop,final_populations=corrector_pop,
                parent_energy=parent.values[5],parent_temperature=parent.temperature_K,
                stage_volume=vg,final_volume=vf,
                stage_photoheat=photog.heating,final_photoheat=photof.heating,
                stage_hubble=np.full(parent.node_count,pg.hubble_s_inv),
                final_hubble=np.full(parent.node_count,p1.hubble_s_inv),
                dt=np.full(parent.node_count,dt))
            if (not np.all(thermal.stage.bracketed) or not np.all(thermal.final.bracketed)
                or np.max(thermal.stage.relative_residual)>1e-10 or np.max(thermal.final.relative_residual)>1e-10):
                raise FloatingPointError('THERMAL_SDIRK2')
            final=self.tensor.ArrayState(
                np.ascontiguousarray(np.vstack([corrector_pop.T,thermal.final.energy])),
                np.ascontiguousarray(thermal.final.temperature))

            nh0=y0[:,0]+y0[:,1];nhe0=np.sum(y0[:,2:5],axis=1,dtype=np.float64)
            hres=float(np.max(np.abs(corrector_pop[:,0]+corrector_pop[:,1]-nh0)/np.maximum(nh0,1e-300)))
            heres=float(np.max(np.abs(np.sum(corrector_pop[:,2:5],axis=1)-nhe0)/np.maximum(nhe0,1e-300)))
            owner_res=float(max(o0.max_kappa_residual,o0.max_current_residual,o0.max_node_residual,
                                o1_pred.max_kappa_residual,o1_pred.max_current_residual,o1_pred.max_node_residual,
                                og.max_kappa_residual,of.max_kappa_residual))
            fractions=fast.base.condition_owner_fractions(0.5*(o0.owner_fraction+o1_pred.owner_fraction))
            exact=np.asarray(step.current)*dt;matrix=fractions*exact[None,:]
            photon=float(np.max(np.abs(np.sum(matrix,axis=0)-exact)/np.maximum(np.abs(exact),1.0)))
            counts=np.sum(matrix,axis=1,dtype=np.float64)
            energies=dt*((1.0-fast.sdirk.GAMMA)*self._owner_energy_rates(og)+fast.sdirk.GAMMA*self._owner_energy_rates(of))
            fast.base.post_owner_counts(ledgers,counts,energies)
            for gi,g in enumerate(('G1','G2a','G2b','G3')):ledgers[f'photon_absorption_{g}']=float(exact[gi])
            for name,value in self._integrated_event_ledgers(dt=dt,stage=eg,final=ef).items():
                ledgers[name]=value
            # The exact OTS Ly-alpha heat is included in the thermal solve and
            # therefore belongs to the resolved-photoheating ledger exactly once.
            ledgers['resolved_photoheating']+=ledgers['ots_resolved_heating']

            cg,exp_g=self.thermal_parent.thermal_terms_numpy(np.log(thermal.stage.temperature),gamma_pop,vg,pg.hubble_s_inv)
            cf,exp_f=self.thermal_parent.thermal_terms_numpy(np.log(final.temperature_K),corrector_pop,vf,p1.hubble_s_inv)
            ledgers['cooling']=float(dt*np.sum((1-fast.sdirk.GAMMA)*cg+fast.sdirk.GAMMA*cf,dtype=np.float64))
            ledgers['expansion_work']=float(dt*np.sum((1-fast.sdirk.GAMMA)*exp_g+fast.sdirk.GAMMA*exp_f,dtype=np.float64))
            ledgers['resolved_thermal_delta']=float(np.sum(final.values[5]-parent.values[5],dtype=np.float64))

            unsupported=~self.inputs.owner_support.astype(bool)
            if any(np.count_nonzero(o.owner_current[unsupported]) for o in (o0,o1_pred,og,of)):
                raise FloatingPointError('STRUCTURAL_ZERO')
            events=(e0,e1,eg,ef)
            branch_fail=max(e.branch_domain_failure_count for e in events)
            energy_res=max(e.max_augmented_energy_residual for e in events)
            photon_branch=max(e.max_photon_count_identity_residual for e in events)
            if branch_fail:raise FloatingPointError('BRANCH_DOMAIN')
            if energy_res>1e-10:raise FloatingPointError('OTS_ENERGY_LEDGER')
            if photon_branch>1e-12:raise FloatingPointError('OTS_PHOTON_IDENTITY')
            return fast.base.SecondOrderTrialResult(
                True,final,predictor_state,ledgers,hres,heres,owner_res,photon,
                float(max(np.max(thermal.stage.relative_residual),np.max(thermal.final.relative_residual))),
                max(r0,r1,eg.pds_reconstruction_residual,ef.pds_reconstruction_residual),
                float(np.min(corrector_pop)),float(time.perf_counter()-started),
                {'classification':'PASS','partition':int(partition),'trial_kind':str(trial_kind),
                 'v_policy':self.v_policy,'f_value':self.f_value,
                 'max_augmented_energy_residual':float(energy_res),
                 'max_photon_branch_identity_residual':float(photon_branch),
                 'branch_domain_failure_count':int(branch_fail),'legacy_rhs_calls':int(self.legacy_rhs_calls),
                 'source_rhs_calls':int(self.source_rhs_calls),'thermal_method':'ALEXANDER_SDIRK2'})
        except Exception as exc:
            return fast.base.SecondOrderTrialResult(
                False,None,None,ledgers,math.inf,math.inf,math.inf,math.inf,math.inf,math.inf,0.0,
                float(time.perf_counter()-started),
                {'classification':str(exc) if isinstance(exc,FloatingPointError) else type(exc).__name__,
                 'exception':type(exc).__name__,'message':str(exc),'v_policy':self.v_policy,'f_value':self.f_value,
                 'legacy_rhs_calls':int(self.legacy_rhs_calls)})
