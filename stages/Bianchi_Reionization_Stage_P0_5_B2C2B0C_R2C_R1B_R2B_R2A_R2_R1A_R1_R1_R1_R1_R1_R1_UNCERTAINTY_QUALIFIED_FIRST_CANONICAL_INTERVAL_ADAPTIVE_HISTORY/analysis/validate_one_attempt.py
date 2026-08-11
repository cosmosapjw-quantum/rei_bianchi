#!/usr/bin/env python3
"""Exact parity check for one partition-2048 three-lane endpoint."""
from __future__ import annotations
import argparse,importlib.util,json,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;STAGE=HERE.parent;REPO=STAGE.parents[1]
SEALED=REPO/'stages'/('Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_'
 'R1_R1_R1_R1_R1_CROSS_SITE_STATE_FEEDBACK_REMAINDER_AND_TABLE_EVENT_LOCK')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
policy=load('parity_policy',HERE/'adaptive_policy.py');state_io=load('parity_state_io',HERE/'state_io.py');guard=load('parity_jax_guard',HERE/'jax_import_guard.py')
def run(run_dir):
 run_dir=Path(run_dir).resolve();latest=json.loads((run_dir/'checkpoints/LATEST.json').read_text());record=json.loads((run_dir/'checkpoints'/latest['record_path']).read_text());sealed=json.loads((SEALED/'data/THREE_LANE_INTERVAL_MAP.json').read_text());sealed_rows={x['lane']:x for x in sealed['rows']};checks=[]
 def check(name,passed):checks.append({'name':name,'passed':bool(passed)})
 check('accepted_index_one',record['accepted_index']==1 and record['interval']=={'depth':0,'left_tick':0,'right_tick':64})
 guard.install_if_missing();kernel=load('parity_sealed_kernel',SEALED/'analysis/interval_discrete_map.py')
 with np.load(SEALED/'data/VALIDATED_PUBLIC_BOXES.npz') as boxes:
  for lane in policy.LANE_ORDER:
   actual=record['lanes'][lane];expected=sealed_rows[lane]
   check(f'{lane}:classification',actual['classification']==expected['classification']=='PASS')
   check(f'{lane}:widths',actual['public_widths']==expected['widths'])
   check(f'{lane}:ledgers',actual['set_ledgers']==expected['set_ledgers'])
   check(f'{lane}:local_error',actual['diagnostics']['validated_local_error_bounds']==expected['diagnostics']['validated_local_error_bounds'] and actual['diagnostics']['maximum_validated_local_error']==expected['diagnostics']['maximum_validated_local_error'])
   summary={k:actual['table_event'][k] for k in ('any_event','minimum_distance','node_count')};check(f'{lane}:table_event',summary==expected['table_event'])
   decoded=state_io.read_state(run_dir/actual['candidate_state']['path'],expected_sha256=actual['candidate_state']['sha256']);base=kernel.trial.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=REPO,lane=lane);y=np.asarray(base.inputs.state0.mutable_copy().values[:5].T);th=y[:,0]+y[:,1];the=np.sum(y[:,2:5],axis=1)
   lower=np.vstack((decoded.population_lower[:,1]/th,decoded.population_lower[:,3]/the,decoded.population_lower[:,4]/the,decoded.log_temperature_lower));upper=np.vstack((decoded.population_upper[:,1]/th,decoded.population_upper[:,3]/the,decoded.population_upper[:,4]/the,decoded.log_temperature_upper))
   check(f'{lane}:endpoint_lower_exact',np.array_equal(lower,boxes[f'{lane}__lower']))
   check(f'{lane}:endpoint_upper_exact',np.array_equal(upper,boxes[f'{lane}__upper']))
 result={'all_passed':all(x['passed'] for x in checks),'checks':checks,'classification':'ONE_ENDPOINT_EXACT_PARITY_VALIDATION','run_record_sha256':latest['record_sha256']};return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--run-dir',required=True);p.add_argument('--output');a=p.parse_args();result=run(a.run_dir);payload=json.dumps(result,indent=2,sort_keys=True)+'\n'
 if a.output:Path(a.output).write_text(payload)
 print(payload,end='');return 0 if result['all_passed'] else 2
if __name__=='__main__':raise SystemExit(main())
