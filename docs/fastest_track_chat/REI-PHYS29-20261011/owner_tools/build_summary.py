#!/usr/bin/env python3
"""Summarize already retained PHYS29 evidence. No scientific imports or evaluations."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

ROOT=Path(__file__).resolve().parents[1]
def read(rel): return json.loads((ROOT/rel).read_bytes())
def rec(rel):
    raw=(ROOT/rel).read_bytes()
    return {'path':rel,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
def write(rel,obj):
    p=ROOT/rel; p.parent.mkdir(parents=True,exist_ok=True)
    assert not p.exists(),rel
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

raw=read('contributions/numerics/SECOND_ORDER_FIRST.json')
replay=read('portability/REPLAY_RECEIPT.json')
first=read('contributions/numerics/EXECUTION.json')
contract=read('PHYSICS_CONTRACT.json')
assert raw['summary']['all_pass'] and raw['summary']['passed']==238
assert replay['status']=='REPLAY_PASS' and replay['result_byte_equal'] and replay['result_parsed_json_equal']
assert (ROOT/'contributions/numerics/SECOND_ORDER_FIRST.json').read_bytes()==(ROOT/'portability/REPLAY_RESULT.json').read_bytes()
assert replay['preexecution_restore']['all_pass'] and replay['postexecution_restore']['all_pass']
count=raw['summary']['actual_counts']; rc=replay['actual_counts']
assert count==rc
totals={k:count[k]+rc[k] for k in count if isinstance(count[k],int) and 'energy_nodes' not in k}
assert totals['program_main_invocations_this_process']==2
assert totals['combined_kernel_derivative_joint_evaluations']==16
assert totals['new_physical_root_searches']==0
result=raw['second_order']['jet_chain']
summary={
 'task':contract['task'],'name':contract['name'],'written_utc':datetime.now(timezone.utc).isoformat(),
 'status':'CANDIDATE_RESULTS_WITH_COMPLETED_SINGLE_REPLAY; final authority independent/DECISION_REVIEW.json and state/CLOSEOUT.json',
 'coefficient_definition':'W(delta)=w+c delta+d delta^2+o(delta^2); d=W_second(0+)/2',
 'units':{'W':'eV^2','delta':'eV half-width','c':'eV','d':'dimensionless','response':'s^-4'},
 'evaluated_point':'PHYS26 serialized numerical roots; nonzero response retained; coefficients of the same response-level local curve, used as exact-root approximations without root enclosure',
 'd_star':result['upper_root']['d_dimensionless'],'d_zero':result['lower_root']['d_dimensionless'],
 'primary_second_order':result,'delta_005_comparison':raw['delta_005_comparison'],
 'maximum_scaled_kernel_expression_error':raw['maximum_scaled_kernel_expression_error'],
 'maximum_scaled_independent_envelope_error':raw['maximum_scaled_independent_envelope_error'],
 'frozen_scaled_tolerance':'1e-60',
 'first_summary':raw['summary'],
 'first_execution':first,
 'replay':{'status':replay['status'],'byte_equal':replay['result_byte_equal'],'parsed_json_equal':replay['result_parsed_json_equal'],
  'all_pass':replay['result_all_pass'],'passed':replay['result_summary']['passed'],'total_checks':replay['result_summary']['total_checks'],
  'started_utc':replay['started_utc'],'ended_utc':replay['ended_utc'],'wall_seconds':replay['wall_seconds'],
  'exit_code':replay['actual_exit_code'],'timed_out':replay['timed_out'],'stderr_bytes':replay['stderr']['bytes'],
  'receipt':rec('portability/REPLAY_RECEIPT.json'),'runtime_payloads':26,'stage_entries':27,
  'claim':'Different absolute path on the same cloud host/Python; independent physics credit0'},
 'total_execution':{'new_main':totals['program_main_invocations_this_process'],
  'joint_k_kprime_ksecond_evaluations':totals['combined_kernel_derivative_joint_evaluations'],
  'k_outputs':totals['k_component_outputs'],'k_prime_outputs':totals['k_prime_component_outputs'],'k_second_outputs':totals['k_second_component_outputs'],
  'three_component_outputs':totals['combined_k_kprime_ksecond_component_outputs'],
  'new_physical_roots':totals['new_physical_root_searches'],'all_summed_process_counters':totals,
  'unique_physical_nodes_across_both_runs':4,'metadata_display_and_review_science_main':0},
 'first_failures':{'scientific_first_failures':0,'replay_first_failures':0,'postfreeze_scientific_code_protocol_tolerance_changes':0,
  'preexecution_changes_preserved':'contributions/numerics/PREEXECUTION_CHANGES.json and preexecution_versions/',
  'display_layout_corrections':2,'display_versions_preserved':'figures/versions/',
  'intake_tooling_events_preserved':'state/TOOLING_EVENTS.json'},
 'protected':contract['protected_state'],
 'next':{'task':'PHYS30_SYMMETRIC_PROFILE_SECOND_ORDER_UNIVERSALITY','status':'PROPOSED_NOT_RUN','handoff':'next/PHYS30_NEXT_HANDOFF_KO.md',
  'question':'At fixed symmetric profile and identical center interval, are first-order coefficients unchanged and second-order profile changes determined solely by mu2?',
  'new_profile_evaluations_in_PHYS29':0},
 'claim_limits':contract['claim_limits']+[
  'Source/J/atomic physical uncertainty not enclosed; frozen source-real constants not native equivalence',
  'No exact-root enclosure or residual-to-root error bound',
  'Total d signs and single-width improvement are observed, not acceptance conditions',
  'Final reviewer is distinct NONBLIND; exact scope comes only from actual final review'],
 'identities':[rec(p) for p in [
  'PHYSICS_CONTRACT.json','SOURCE_MANIFEST.json','contributions/theory/DERIVATION_KO.md',
  'contributions/numerics/second_order_width.py','contributions/numerics/PROTOCOL.json',
  'contributions/numerics/PREEXECUTION_FROZEN.json','contributions/numerics/SECOND_ORDER_FIRST.json',
  'contributions/numerics/EXECUTION.json','portability/REPLAY_RECEIPT.json','portability/REPLAY_RESULT.json',
  'figures/PHYS29_SECOND_ORDER_DECOMPOSITION.png','figures/DISPLAY_RECEIPT.json','next/PHYS30_NEXT_HANDOFF_KO.md']],
 'publication':'Actual post-gate Git/archive evidence and later delivery ACK are detached; no future success preclaimed'
}
write('report/PHYS29_RESULTS_SUMMARY.json',summary)
claims=[
 {'id':'I29-SOURCE','status':'inherited_and_byte_verified','statement':'Frozen source, J and prior roots/derivative premises','depends_on':[],
  'evidence':['SOURCE_MANIFEST.json','evidence/INTAKE_REMOTE.json','evidence/INHERITED_INPUT_MANIFEST.json','inputs/PHYS28/independent/DECISION_REVIEW.json'],
  'limits':'Stored roots and numerical endpoint signs are not interval root enclosures; source identity is not physical validation'},
 {'id':'T29-C2','status':'direct_derivation_conditional','statement':'Physical one-sided C2 simple-root expansion and d formula','depends_on':['I29-SOURCE'],
  'evidence':['contributions/theory/DERIVATION_KO.md'],
  'limits':'Exact interior simple root and inherited regularity/sign premises; no numerical remainder bound'},
 {'id':'T29-DECOMP','status':'direct_derivation','statement':'Complete K decomposition, dV=1/3, davg=−weightedksecond/(6C), mixed and variance-curvature terms','depends_on':['T29-C2'],
  'evidence':['contributions/theory/DERIVATION_KO.md','contributions/theory/THEORY_CLAIMS.json'],
  'limits':'Fixed actual W, uniform profile and stated center family'},
 {'id':'T29-OFFROOT','status':'direct_derivation','statement':'Nonzero stored response retained with same-level numerator corrections','depends_on':['T29-C2'],
  'evidence':['contributions/theory/DERIVATION_KO.md'],
  'limits':'Not exact-root certification or root refinement'},
 {'id':'N29-COEFFICIENTS','status':'numerically_checked','statement':'dstar1.454082106621024..., dzero−.245144110608384..., full component decomposition','depends_on':['T29-DECOMP','T29-OFFROOT','I29-SOURCE'],
  'evidence':['contributions/numerics/SECOND_ORDER_FIRST.json','contributions/numerics/EXECUTION.json','contributions/numerics/PROTOCOL.json'],
  'limits':'Frozen source-real/Decimal80 model and stored numerical points; no physical uncertainty enclosure'},
 {'id':'V29-TWOALGORITHMS','status':'implementation_verified','statement':'LogJet/Bell kernel plus explicit-chain/independent-bivariate comparisons and exact rational quadratic toy;238PASS','depends_on':['N29-COEFFICIENTS'],
  'evidence':['contributions/numerics/second_order_width.py','contributions/numerics/SECOND_ORDER_FIRST.json'],
  'limits':'Shared fit/J/source/Decimal/family; independent physics credit0'},
 {'id':'N29-DELTA005','status':'single_width_diagnostic','statement':'Quadratic residuals +6.011955345e−5,+7.468738540e−6 eV2; lower sign flips; gap-reduction residual+5.265081491e−5 eV2','depends_on':['N29-COEFFICIENTS','I29-SOURCE'],
  'evidence':['contributions/numerics/SECOND_ORDER_FIRST.json'],
  'limits':'Stored PHYS27 width only; no convergence rate, validity window or Taylor remainder certificate'},
 {'id':'V29-REPLAY','status':'implementation_verified','statement':'One separate-path replay238PASS, raw byte/JSON equal, runtime26+manifest unchanged','depends_on':['V29-TWOALGORITHMS'],
  'evidence':['portability/REPLAY_RECEIPT.json','portability/PORTABILITY_PROTOCOL.json','portability/REPLAY_RESULT.json'],
  'limits':'Same host/Python/program; not independent implementation,OS or physical evidence'},
 {'id':'P30-NEXT','status':'proposed_not_run','statement':'Fixed symmetric profile second-order dependence on mu2','depends_on':['T29-DECOMP','N29-COEFFICIENTS'],
  'evidence':['next/PHYS30_NEXT_HANDOFF_KO.md'],'limits':'No PHYS30 theorem or profile computation performed in PHYS29'}
]
write('evidence/CLAIM_DAG.json',{'task':contract['task'],'claims':claims,'final_decision_authority':'independent/DECISION_REVIEW.json',
 'blind_review_claim':False,'external_source_scope':'Standard mathematical background only; no priority/novelty claim',
 'protected':contract['protected_state']})
print(json.dumps({'summary':rec('report/PHYS29_RESULTS_SUMMARY.json'),'claim_dag':rec('evidence/CLAIM_DAG.json'),'science_main':0},ensure_ascii=False))
