#!/usr/bin/env python3
"""Explicit four-site control wrapper with a primal-parity audit.

This wrapper changes only branch-policy dispatch.  With identical controls at
all sites it must reproduce the inherited trial exactly; this is the first
load-bearing gate before tangent or enclosure arithmetic is connected.
"""
from __future__ import annotations
import importlib.util,sys
from pathlib import Path
import numpy as np

SITES=('population_t0','population_t1_predictor','thermal_tgamma','thermal_t1_final')

def _load(name,path):
    if name in sys.modules:return sys.modules[name]
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise ImportError(path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

def _parent(repo:Path):
    r1a=next(repo.glob('stages/*R2_R1A_FOUR_CORNER*'))
    trial=_load('evalsite_parent_uncertainty_trial',r1a/'analysis/uncertainty_trial.py')
    policy=_load('evalsite_parent_uncertainty_policy',r1a/'analysis/uncertainty_policy.py')
    return trial,policy

def make_trial_class(repo_root:Path):
    repo=Path(repo_root).resolve();trial,policy=_parent(repo)
    class EvaluationSiteTrial(trial.UncertaintySecondOrderTrial):
        def __init__(self,*,base,lane,controls):
            super().__init__(base=base,lane=lane,v_policy='CELL_LOWER_STRICT',f_value=0.1)
            if set(controls)!=set(SITES):raise ValueError('controls must name exactly four evaluation sites')
            self.controls={k:(str(v[0]),float(v[1])) for k,v in controls.items()}
            self.site_trace=[];self._evaluation_count=0
        def _site(self):
            n=self._evaluation_count;self._evaluation_count+=1
            if n==0:site=SITES[0]
            elif n==1:site=SITES[1]
            else:site=SITES[2+(n-2)%2]
            self.site_trace.append(site);return site
        def _event_evaluation(self,state,owner,point):
            site=self._site();v_policy,f_value=self.controls[site]
            y=np.asarray(state.values,dtype=np.float64)
            volume=self.inputs.comoving_volume_cm3/(1.0+point.z)**3
            photo=self.backend.photo_fields(owner)
            v=policy.build_v_field_from_temperature(v_policy,state.temperature_K)
            f=policy.build_f_field(f_value,state.node_count)
            event=trial.event_mod.evaluate_event_flux(
                populations=y[:5].T,temperature_K=state.temperature_K,
                proper_volume_cm3=volume,photo_hi=photo.HI,photo_hei=photo.HeI,
                photo_heii=photo.HeII,v=v,f=f)
            adjusted=trial.fast.base.physical.PhotoFields(
                HI=photo.HI,HeI=photo.HeI,HeII=photo.HeII,
                heating=np.ascontiguousarray(photo.heating+event.resolved_ots_heating_erg_s),
                unresolved_heating=np.ascontiguousarray(photo.unresolved_heating+event.unresolved_ots_energy_erg_s))
            return event,adjusted,volume
        def solve(self,**kwargs):
            self.site_trace=[];self._evaluation_count=0
            return super().solve(**kwargs)
    return EvaluationSiteTrial

def _relative(a,b):
    a=np.asarray(a,dtype=np.float64);b=np.asarray(b,dtype=np.float64)
    return float(np.max(np.abs(a-b)/np.maximum(np.maximum(np.abs(a),np.abs(b)),np.finfo(float).tiny)))

def primal_parity_audit(repo_root:Path,*,lane:str,partition:int=2048):
    repo=Path(repo_root).resolve();trial,_=_parent(repo)
    base=trial.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=repo,lane=lane)
    parent=base.inputs.state0.mutable_copy();dt=base.forcing.duration_seconds(0)/int(partition)
    reference=trial.UncertaintySecondOrderTrial(base=base,lane=lane,v_policy='CELL_LOWER_STRICT',f_value=0.1)
    controls={site:('CELL_LOWER_STRICT',0.1) for site in SITES}
    candidate=make_trial_class(repo)(base=base,lane=lane,controls=controls)
    ref=reference.solve(state=parent.mutable_copy(),t0=0.0,t1=dt,partition=partition,trial_kind='REFERENCE')
    got=candidate.solve(state=parent.mutable_copy(),t0=0.0,t1=dt,partition=partition,trial_kind='EVALSITE_PARITY')
    if not(ref.converged and got.converged):
        return {'parity_pass':False,'reference_certificate':ref.certificate,'candidate_certificate':got.certificate,'site_trace':candidate.site_trace}
    sr=_relative(ref.state.values,got.state.values);tr=_relative(ref.state.temperature_K,got.state.temperature_K)
    keys=set(ref.ledger_delta)|set(got.ledger_delta)
    ledger_differences={k:float(got.ledger_delta.get(k,0.0)-ref.ledger_delta.get(k,0.0)) for k in sorted(keys)}
    ledger_equal=all(v==0.0 for v in ledger_differences.values())
    return {'parity_pass':bool(sr==0.0 and tr==0.0 and ledger_equal),
        'max_state_relative_difference':sr,'max_temperature_relative_difference':tr,
        'ledger_equal':ledger_equal,'ledger_differences':ledger_differences,
        'site_trace':candidate.site_trace,'reference_certificate':ref.certificate,
        'candidate_certificate':got.certificate}
