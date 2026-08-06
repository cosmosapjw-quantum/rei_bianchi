#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
import pandas as pd
import numpy as np

STAGE=Path(__file__).resolve().parents[1]
DATA=STAGE/'data'

def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()

def require(x:bool,msg:str)->None:
 if not x: raise AssertionError(msg)

s=json.loads((DATA/'summary.json').read_text())
seg=json.loads((DATA/'convex_endpoint_segment_summary.json').read_text())
exact=json.loads((DATA/'exact_symbolic_fallback_report.json').read_text())
macro=pd.read_csv(DATA/'node_local_physics_macro_audit.csv')
case=pd.read_csv(DATA/'node_local_physics_case_audit.csv')
cov=pd.read_csv(DATA/'capacity_refinement_covariance.csv')
mass=pd.read_csv(DATA/'mass_farkas_endpoint_segment_audit.csv')

require(s['state_row_count']==1382400,'state row count')
require(s['group_row_count']==2764800,'group row count')
require(s['macro_case_count']==540 and s['case_count']==30,'case counts')
require(s['endpoint_state_cone_failure_count']==0,'endpoint state cone')
require(s['mass_nonpositive_count']==0 and s['neutral_negative_count']==0,'state signs')
require(s['x_outside_unit_interval_count']==0 and s['temperature_nonpositive_count']==0,'intensive signs')
require(s['nonfinite_direct_rate_count']==0,'direct rate finiteness')
require(s['negative_group_current_count']==0 and s['negative_group_opacity_count']==0,'RT signs')
require(s['maximum_locked_moment_relative_residual']<=5e-11,'locked moments')
require(s['maximum_current_Gamma_relative_residual']<=5e-11,'current-Gamma')
require(s['farkas_case_count']==497 and s['radiative_farkas_case_count']==491 and s['mass_farkas_case_count']==6,'Farkas partition')
require(s['mass_farkas_both_endpoints_within_cap_count']==6,'mass Farkas endpoint caps')
require(seg['pass'] and seg['convex_state_segment_failure_count']==0,'convex state segments')
require(len(macro)==540 and len(case)==30,'audit table lengths')
require(bool(macro.endpoint_state_cone_pass.all()),'macro state cone')
require(bool(mass.convex_segment_within_cap.all()),'six mass segments')
q2=cov[cov.q_refinement==2]
require(len(q2)==10 and bool((q2.C_change_relative_to_original>0).all()),'capacity refinement noninvariance')
require(s['old_capacity_local_budget_mismatch_macro_count']==540,'old/local budget mismatch evidence')
require(s['local_budget_pointwise_violation_node_count']>0,'mass-proportional capacity is not local budget')
require(exact['pass'],'symbolic fallback')

checks={
 'all_node_endpoint_state_cone':True,
 'all_direct_rates_finite':True,
 'all_RT_endpoint_signs':True,
 'locked_moments_close':True,
 'current_Gamma_closes':True,
 '497_Farkas_partition_replayed':True,
 'six_mass_Farkas_pairs_have_convex_cap_path':True,
 'C_is_not_refinement_invariant':True,
 'old_mass_proportional_C_is_not_node_local_budget':True,
 'exact_symbolic_fallback':True,
}
report={
 'classification':'R2C_R1A_INDEPENDENT_VALIDATION',
 'checks':checks,
 'pass':all(checks.values()),
 'artifact_hashes':{p.name:sha(p) for p in [DATA/'summary.json',DATA/'node_local_physics_macro_audit.csv',DATA/'node_local_physics_case_audit.csv',DATA/'capacity_refinement_covariance.csv',DATA/'mass_farkas_endpoint_segment_audit.csv',DATA/'convex_endpoint_segment_audit.csv',DATA/'exact_symbolic_fallback_report.json']},
 'reviewer_verdict':'The inherited Farkas certificates reject the common-equilibrium state surrogate. They do not prove physical-history infeasibility once C is restored to an interval budget and J_g to an algebraic reaction flux.',
}
(DATA/'independent_validation_report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps(report,indent=2,sort_keys=True))
