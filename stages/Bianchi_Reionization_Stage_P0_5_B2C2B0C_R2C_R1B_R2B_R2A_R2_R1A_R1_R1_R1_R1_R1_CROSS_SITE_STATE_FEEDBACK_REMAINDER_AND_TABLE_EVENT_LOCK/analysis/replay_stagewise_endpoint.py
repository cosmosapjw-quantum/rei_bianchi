#!/usr/bin/env python3
from __future__ import annotations
import argparse,importlib.util,sys,json
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;STAGE=HERE.parent;REPO=STAGE.parents[1]

def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
AFF=next(REPO.glob('stages/*AFFINE_SET_PARAMETERIZED_TAYLOR_MODEL_CONTINUOUS_BRANCH_ENCLOSURE_LOCK'))
field=load('stagewise_replay_field',AFF/'analysis/field_trial.py')

def run(lane):
 trial_mod,policy_mod,_=field.load_parent_modules(REPO);klass=field.make_trial_class(REPO)
 base=trial_mod.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=REPO,lane=lane);full=float(base.forcing.duration_seconds(0)/2048);mid=.5*full
 class Stage(klass):
  def __init__(self):super().__init__(base=base,lane=lane,alpha=0,beta=0)
  def _event_evaluation(self,state,owner,point):
   y=np.asarray(state.values);volume=self.inputs.comoving_volume_cm3/(1+point.z)**3;photo=self.backend.photo_fields(owner)
   lo=policy_mod.build_v_field_from_temperature('CELL_LOWER_STRICT',state.temperature_K);hi=policy_mod.build_v_field_from_temperature('CELL_UPPER_STRICT',state.temperature_K)
   early=bool(point.time_s<=mid*(1+1e-12));v=hi if early else lo;f=np.full(state.node_count,1.0 if early else .1)
   ev=trial_mod.event_mod.evaluate_event_flux(populations=y[:5].T,temperature_K=state.temperature_K,proper_volume_cm3=volume,photo_hi=photo.HI,photo_hei=photo.HeI,photo_heii=photo.HeII,v=v,f=f)
   ph=trial_mod.fast.base.physical.PhotoFields(HI=photo.HI,HeI=photo.HeI,HeII=photo.HeII,heating=np.ascontiguousarray(photo.heating+ev.resolved_ots_heating_erg_s),unresolved_heating=np.ascontiguousarray(photo.unresolved_heating+ev.unresolved_ots_energy_erg_s))
   return ev,ph,volume
 solver=Stage();parent=base.inputs.state0.mutable_copy();a=solver.solve(state=parent,t0=0,t1=mid,partition=4096,trial_kind='FIRST_HALF');b=solver.solve(state=a.state.mutable_copy(),t0=mid,t1=full,partition=4096,trial_kind='SECOND_HALF')
 if not(a.converged and b.converged):raise RuntimeError
 obs=field.state_observables(b.state);np.savez_compressed(STAGE/f'data/STAGEWISE_ENDPOINT_{lane}.npz',observables=obs)
 return {'lane':lane,'endpoint_sha256':field.state_sha256(b.state),'hard_gates_pass':field.gate_trial(a) and field.gate_trial(b)}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--lane',required=True);a=p.parse_args();print(json.dumps(run(a.lane),indent=2))
