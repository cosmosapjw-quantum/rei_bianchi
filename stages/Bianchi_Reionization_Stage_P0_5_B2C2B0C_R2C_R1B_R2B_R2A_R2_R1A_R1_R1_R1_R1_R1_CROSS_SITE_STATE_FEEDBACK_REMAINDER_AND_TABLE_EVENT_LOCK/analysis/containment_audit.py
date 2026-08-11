#!/usr/bin/env python3
"""Direct containment audit of inherited and adversarial endpoint evidence."""
from __future__ import annotations
import importlib.util,json,sys,time
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;STAGE=HERE.parent;REPO=STAGE.parents[1]
LANES=('LOCAL_NEUTRAL_HAZARD_PRIMARY','RECOMBINATION_WEIGHTED_AUDITOR','SCRIPT_SELF_SHIELDING_AUDITOR')
COORDS=('x_HII','x_HeII','x_HeIII','log_T')

def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
idm=load('containment_idm_direct',HERE/'interval_discrete_map.py')
AFF=next(REPO.glob('stages/*AFFINE_SET_PARAMETERIZED_TAYLOR_MODEL_CONTINUOUS_BRANCH_ENCLOSURE_LOCK'))
R1A=next(REPO.glob('stages/*R2_R1A_FOUR_CORNER*'))
EVAL=next(REPO.glob('stages/*EVALUATION_SITE_SPARSE_GENERATOR_VALIDATED_MPRK22_SDIRK2*'))
trial=idm.trial

def observable_box(result,base):
 pop=result.population_box;nh=base.inputs.state0.values[0]+base.inputs.state0.values[1];nhe=base.inputs.state0.values[2]+base.inputs.state0.values[3]+base.inputs.state0.values[4]
 return np.vstack([pop.lower[:,1]/nh,pop.lower[:,3]/nhe,pop.lower[:,4]/nhe,result.log_temperature_box.lo]),np.vstack([pop.upper[:,1]/nh,pop.upper[:,3]/nhe,pop.upper[:,4]/nhe,result.log_temperature_box.hi])

def outside(lo,hi,value):
 d=np.maximum(lo-value,value-hi);p=np.maximum(d,0.0)
 tol=128*np.finfo(float).eps*np.maximum(np.maximum(np.abs(lo),np.abs(hi)),np.finfo(float).tiny)
 return {'maximum_raw_outside':float(np.max(p)),'maximum_tolerance':float(np.max(tol)),'outside_count':int(np.count_nonzero(p>tol))}

def margins(lo,hi,value):
 return {'minimum_lower_margin':float(np.min(value-lo)),'minimum_upper_margin':float(np.min(hi-value))}

def run():
 start=time.perf_counter();rows=[];boxes={}
 with np.load(R1A/'data/strict_corner_envelopes.npz',allow_pickle=False) as d:static={k:np.array(d[k]) for k in d.files}
 witness=json.loads((EVAL/'data/STAGEWISE_WITNESS_REPLAY.json').read_text());wrows={r['lane']:r for r in witness['rows']}
 with np.load(AFF/'data/coherent_primary_endpoint_evidence.npz',allow_pickle=False) as d:interior={k:np.array(d[k]) for k in d.files}
 direct_rows=[]
 for lane in LANES:
  r=idm.run_lane(REPO,lane=lane,partition=2048);base=trial.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=REPO,lane=lane)
  blo,bhi=observable_box(r,base);boxes[f'{lane}__lower']=blo;boxes[f'{lane}__upper']=bhi;token=lane.lower()
  slo=np.vstack([static[f'{token}__{c}_lower'] for c in COORDS]);shi=np.vstack([static[f'{token}__{c}_upper'] for c in COORDS])
  static_lo=outside(blo,bhi,slo);static_hi=outside(blo,bhi,shi)
  with np.load(STAGE/f'data/STAGEWISE_ENDPOINT_{lane}.npz',allow_pickle=False) as d:stagewise=np.asarray(d['observables'])
  direct={**outside(blo,bhi,stagewise),**margins(blo,bhi,stagewise)};direct_rows.append({'lane':lane,**direct})
  ia=[]
  if lane==LANES[0]:
   for name,value in interior.items():ia.append({'name':name,**outside(blo,bhi,value)})
  all_contained=bool(static_lo['outside_count']==0 and static_hi['outside_count']==0 and direct['outside_count']==0 and all(x['outside_count']==0 for x in ia))
  wr=wrows[lane]
  rows.append({'lane':lane,'certified_map':r.certified,'widths':r.public_widths,'static_lower':static_lo,'static_upper':static_hi,
   'direct_stagewise_endpoint':direct,'inherited_stagewise_escape_by_coordinate':dict(zip(COORDS,map(float,wr['maximum_outside_by_coordinate']))),
   'primary_interior':ia,'all_contained':all_contained})
 np.savez_compressed(STAGE/'data/VALIDATED_PUBLIC_BOXES.npz',**boxes)
 direct_result={'classification':'DIRECT_STAGEWISE_ENDPOINT_CONTAINMENT','rows':direct_rows,'all_contained':all(x['outside_count']==0 for x in direct_rows)}
 (STAGE/'data/STAGEWISE_ENDPOINT_CONTAINMENT.json').write_text(json.dumps(direct_result,indent=2,sort_keys=True)+'\n')
 result={'classification':'DIRECT_ENDPOINT_AND_STORED_INTERIOR_CONTAINMENT_AUDIT','rows':rows,'all_contained':all(r['all_contained'] for r in rows),'elapsed_s':time.perf_counter()-start,'supersedes':'state/ATTEMPT_1_MARGIN_ONLY_CONTAINMENT.json'}
 (STAGE/'data/CONTAINMENT_AUDIT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 return result
if __name__=='__main__':
 result=run();print(json.dumps(result,indent=2,sort_keys=True));raise SystemExit(0 if result['all_contained'] else 1)
