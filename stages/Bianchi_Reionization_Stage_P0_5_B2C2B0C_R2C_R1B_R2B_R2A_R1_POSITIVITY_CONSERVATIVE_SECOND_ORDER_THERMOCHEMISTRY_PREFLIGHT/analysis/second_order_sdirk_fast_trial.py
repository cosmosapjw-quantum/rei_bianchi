#!/usr/bin/env python3
"""MPRK22 chemistry coupled to the optimized analytic-root SDIRK2 thermal block."""
from __future__ import annotations
import importlib.util,math,sys,time
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent

def _load(name,path):
    if name in sys.modules:return sys.modules[name]
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m

base=_load('r2b_r2a_r1_trial_base_sdirk',HERE/'second_order_trial.py')
sdirk=_load('r2b_r2a_r1_fast_sdirk_thermal_trial',HERE/'thermal_fast_root.py')

class SecondOrderSDIRKFastTrial(base.SecondOrderPhysicalTrial):
    def solve(self, *, state, t0: float, t1: float, partition: int, trial_kind: str):
        started=time.perf_counter(); ledgers=base.empty_ledgers(); parent=state.mutable_copy()
        y0=np.asarray(parent.values[:5].T,dtype=np.float64)
        try:
            if not(math.isfinite(t0) and math.isfinite(t1) and t1>t0):raise ValueError('invalid interval')
            dt=float(t1-t0); tg=t0+sdirk.GAMMA*dt
            p0=self.forcing.point(interval=0,time_s=t0); pg=self.forcing.point(interval=0,time_s=tg); p1=self.forcing.point(interval=0,time_s=t1)
            step=self.forcing.step(interval=0,t0_s=t0,t1_s=t1)
            o0=self._owner(parent,p0); rhs0,f0,photo0,v0,r0=self._rhs_flux(parent,o0,p0)
            predictor_pop=base.mprk.patankar_euler(y0=y0,flux=f0,dt=dt)
            thermal_predictor=sdirk.solve_backward_euler_fast(
                populations=predictor_pop,parent_energy=parent.values[5],parent_temperature=parent.temperature_K,
                volume=v0,photoheat=photo0.heating,hubble=np.full(parent.node_count,p0.hubble_s_inv),
                dt=np.full(parent.node_count,dt))
            if not np.all(thermal_predictor.bracketed):raise FloatingPointError('THERMAL_PREDICTOR')
            pred_values=np.ascontiguousarray(np.vstack([predictor_pop.T,thermal_predictor.energy]))
            predictor_state=self.tensor.ArrayState(pred_values,np.ascontiguousarray(thermal_predictor.temperature))
            o1_pred=self._owner(predictor_state,p1); rhs1,f1,photo1_pred,v1,r1=self._rhs_flux(predictor_state,o1_pred,p1)
            corrector_pop=base.mprk.mprk22_corrector(y0=y0,predictor=predictor_pop,stage_flux=f0,final_flux=f1,dt=dt)

            gamma_pop=base.mprk.patankar_euler(y0=y0,flux=f0,dt=sdirk.GAMMA*dt)
            gamma_energy=sdirk.energy_from_temperature(gamma_pop,parent.temperature_K)
            gamma_state=self.tensor.ArrayState(np.ascontiguousarray(np.vstack([gamma_pop.T,gamma_energy])),parent.temperature_K.copy())
            og=self._owner(gamma_state,pg); photog=self.backend.photo_fields(og)
            # Owner total fractions depend on material abundances; temperature only affects
            # unresolved node distribution, whose resolved source is exact zero.
            final_provisional_energy=sdirk.energy_from_temperature(corrector_pop,thermal_predictor.temperature)
            final_provisional=self.tensor.ArrayState(
                np.ascontiguousarray(np.vstack([corrector_pop.T,final_provisional_energy])),
                thermal_predictor.temperature.copy())
            of=self._owner(final_provisional,p1); photof=self.backend.photo_fields(of)
            thermal=sdirk.solve_sdirk2_fast(
                parent_populations=y0,stage_populations=gamma_pop,final_populations=corrector_pop,
                parent_energy=parent.values[5],parent_temperature=parent.temperature_K,
                stage_volume=self.inputs.comoving_volume_cm3/(1.0+pg.z)**3,
                final_volume=self.inputs.comoving_volume_cm3/(1.0+p1.z)**3,
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
            fractions=base.condition_owner_fractions(0.5*(o0.owner_fraction+o1_pred.owner_fraction))
            exact=np.asarray(step.current)*dt; matrix=fractions*exact[None,:]
            photon=float(np.max(np.abs(np.sum(matrix,axis=0)-exact)/np.maximum(np.abs(exact),1.0)))
            counts=np.sum(matrix,axis=1,dtype=np.float64)
            energies=dt*((1.0-sdirk.GAMMA)*self._owner_energy_rates(og)+sdirk.GAMMA*self._owner_energy_rates(of))
            base.post_owner_counts(ledgers,counts,energies)
            for gi,g in enumerate(('G1','G2a','G2b','G3')):ledgers[f'photon_absorption_{g}']=float(exact[gi])
            vg=self.inputs.comoving_volume_cm3/(1.0+pg.z)**3
            vf=self.inputs.comoving_volume_cm3/(1.0+p1.z)**3
            cg,eg=self.thermal_parent.thermal_terms_numpy(np.log(thermal.stage.temperature),gamma_pop,vg,pg.hubble_s_inv)
            cf,ef=self.thermal_parent.thermal_terms_numpy(np.log(final.temperature_K),corrector_pop,vf,p1.hubble_s_inv)
            ledgers['cooling']=float(dt*np.sum((1-sdirk.GAMMA)*cg+sdirk.GAMMA*cf,dtype=np.float64))
            ledgers['expansion_work']=float(dt*np.sum((1-sdirk.GAMMA)*eg+sdirk.GAMMA*ef,dtype=np.float64))
            ledgers['resolved_thermal_delta']=float(np.sum(final.values[5]-parent.values[5],dtype=np.float64))
            unsupported=~self.inputs.owner_support.astype(bool)
            if any(np.count_nonzero(o.owner_current[unsupported]) for o in (o0,o1_pred,og,of)):
                raise FloatingPointError('STRUCTURAL_ZERO')
            return base.SecondOrderTrialResult(
                True,final,predictor_state,ledgers,hres,heres,owner_res,photon,
                float(max(np.max(thermal.stage.relative_residual),np.max(thermal.final.relative_residual))),
                max(r0,r1),float(np.min(corrector_pop)),float(time.perf_counter()-started),
                {'classification':'PASS','partition':int(partition),'trial_kind':str(trial_kind),'thermal_method':'ALEXANDER_SDIRK2','thermal_root':'ANALYTIC_NEWTON_BISECTION','thermal_stage_iterations':int(thermal.stage.iterations),'thermal_final_iterations':int(thermal.final.iterations),'thermal_predictor_root':'ANALYTIC_NEWTON_BISECTION','thermal_predictor_iterations':int(thermal_predictor.iterations)})
        except Exception as exc:
            return base.SecondOrderTrialResult(
                False,None,None,ledgers,math.inf,math.inf,math.inf,math.inf,math.inf,math.inf,0.0,
                float(time.perf_counter()-started),
                {'classification':str(exc) if isinstance(exc,FloatingPointError) else type(exc).__name__,
                 'exception':type(exc).__name__,'message':str(exc)})
