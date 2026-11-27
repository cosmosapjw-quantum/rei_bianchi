#!/usr/bin/env python3
"""Independent full saved-return review. No candidate/kernel import or evaluation."""
from pathlib import Path
from fractions import Fraction as F
from datetime import datetime, timezone
import hashlib
import json
import time
import traceback
import review_inputs as ri
import review_saved_outputs_e13c8 as rs

HERE=Path(__file__).resolve().parent
ROOT7=Path('/workspace/scratch/7fd51143e473/e13c7_research_20261011/BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1')
RETURN=Path('/workspace/scratch/7fd51143e473/e13c8_research_20261011/ACTUAL_NCP_RETURN')
BATCH=RETURN/'BATCH'
ri.ROOT=rs.ROOT=ROOT7
ri.HERE=rs.HERE=HERE
EXEC='c04cfde1838563d95389e499de9bcbe505a7d67f6bda1fff4476af953c8cc4f4'
SOURCE='386d0abd02a33b15a015166369cec981b00fd05987dbd146f2badcb9f604688f'

def save(path,obj):
 raw=(json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
 with path.open('xb') as f:f.write(raw)
 return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}

def encode(x):
 return {k:{q:{'lo':str(v[0]),'hi':str(v[1])} for q,v in m.items()} for k,m in x.items()}

def main():
 start=time.perf_counter();summaries=[];aggregate={'old':{},'new':{}}
 ri.check('actual_original_source_lock',ri.h(ROOT7/'SOURCE_LOCK.json')==SOURCE)
 ri.check('actual_original_execution_lock',ri.h(ROOT7/'EXECUTION_LOCK.json')==EXEC)
 index=ri.read(ROOT7/'inputs/INPUT_INDEX.json')['records']
 plan=ri.read(ROOT7/'inputs/WORK_PLAN.json')
 c=ri.read(BATCH/'BATCH_COMPLETE.json')
 nodes=plan['ncp_nodes']
 ri.check('exact_scope_work',c['work']=={'N':1024,'mode':'OFF','precision':60,'scope':'ncp','nodes':nodes})
 ri.check('unique_sorted_2331_nodes',nodes==sorted(set(nodes)) and len(nodes)==2331)
 ri.check('original_runtime_work_closure',c['execution_lock_sha256']==EXEC and plan['primary_N']==1024 and plan['precision']==60)
 ri.check('batch_completion_status',c['status']=='COMPLETE_PATHS_AWAIT_EXACT_REDUCTION_AND_INDEPENDENT_REVIEW')
 ri.check('new_counts_no_reused',c['new_validated_path_calls']==2331 and c['reused_completed_paths']==0 and c['new_coefficient_evaluations']==9547776)
 ri.check('batch_forbidden_zero',all(v==0 for v in c['forbidden_invocations'].values()))
 ri.check('complete_ordered_coverage',[e['node'] for e in c['ordered_paths']]==nodes)
 expected_dirs={str((BATCH/e['relative_directory']).resolve()) for e in c['ordered_paths']}
 actual_dirs={str(p.parent.resolve()) for p in (BATCH/'paths').rglob('COMPLETE.json')}
 ri.check('all_saved_completions_indexed_once',actual_dirs==expected_dirs and len(actual_dirs)==2331)
 ri.check('no_returned_path_failures',not any((BATCH/'paths').rglob('*FAILURE*.json')))
 collection={'work':c['work'],'execution_lock_sha256':EXEC,'paths':[{'node':e['node'],'semantic_sha256':e['summary']['semantic_sha256']} for e in c['ordered_paths']]}
 collection_sha=hashlib.sha256(b'bass-he-e13c7-ordered-path-collection-v1\n'+ri.canon(collection)).hexdigest()
 ri.check('ordered_collection_semantic',collection_sha==c['collection_semantic_sha256'])
 original_old=ri.metrics;original_new=rs.new_metrics
 def collect_old(x):
  v=original_old(x);aggregate['old']=ri.combine([aggregate['old'],v]);return v
 def collect_new(track,w):
  v=original_new(track,w);aggregate['new']=ri.combine([aggregate['new'],v]);return v
 ri.metrics=collect_old;rs.new_metrics=collect_new
 for counter,e in enumerate(c['ordered_paths'],1):
  path=(BATCH/e['relative_directory']).resolve()
  ri.check('safe_relative_returned_path',path.is_relative_to(BATCH) and not path.is_symlink(),e['node'])
  ri.check('complete_three_files_exact',set(e['files'])=={'RESULT.json','ADMISSION.json','COMPLETE.json'},e['node'])
  for name,pin in e['files'].items():
   f=path/name
   ri.check('collection_actual_file_bytes',f.stat().st_size==pin['bytes'] and ri.h(f)==pin['sha256'],(e['node'],name))
  row=rs.review(path,index,'primary')
  ri.check('prespecified_N1024_P60_each',(row['node'],row['N'],row['precision'])==(e['node'],1024,60),e['node'])
  ri.check('entry_semantic_and_sha_correspond',all(row[k]==e['summary'][k] for k in ('node','N','precision','semantic_sha256','result_sha256','admission_sha256')),e['node'])
  ri.check('entry_not_reused',e['reused'] is False,e['node'])
  summaries.append(row)
  if counter%250==0 or counter==2331:
   print(json.dumps({'reviewed_paths':counter,'checks_failed':sum(x['failed'] for x in ri.checks.values()),'elapsed_seconds':time.perf_counter()-start}),flush=True)
 ri.check('all_fresh_counts_sum',sum(x['coefficient_evaluations'] for x in summaries)==9547776 and sum(x['local_enclosures'] for x in summaries)==4662)
 pred=ri.read(ROOT7/'inputs/PREDECESSOR_BUDGET.json')
 local=ri.read(ROOT7/'analysis/LOCAL/LOCAL_ADMITTED_CANDIDATE.json')
 retained=ri.combine([ri.decode(pred['prior_six']),ri.decode(local['new_local_eight'])])
 before=ri.decode(local['current_full_OFF'])
 candidate=ri.combine([retained,aggregate['new']])
 expected_old=ri.decode(pred['old_ncp_2331'])
 reconstructed_before=ri.combine([retained,aggregate['old']])
 comparisons=[]
 for kind in sorted(candidate):
  for q in sorted(candidate[kind]):
   ri.check('direct_old_group_bridge',aggregate['old'][kind][q]==expected_old[kind][q],(kind,q))
   ri.check('direct_full_predecessor_bridge',reconstructed_before[kind][q]==before[kind][q],(kind,q))
   row=rs.comparison(before[kind][q],candidate[kind][q],kind,q)
   ri.check('all_34_full_raw_nested_nonincreasing',row['nested'] and row['width_nonincreasing'],(kind,q))
   comparisons.append(row)
 sums={'schema':'bass-he-e13c8-independent-direct-sums-v1','source_lock_sha256':SOURCE,'execution_lock_sha256':EXEC,'collection_semantic_sha256':collection_sha,'paths':2331,'old_group':encode(aggregate['old']),'new_raw_group':encode(aggregate['new']),'retained_direct_sum':encode(retained),'full_before':encode(before),'full_raw_candidate':encode(candidate),'full_comparison':comparisons,'intersection_used':False,'old_fallback_used':False,'candidate_or_kernel_imports':0,'scientific_kernel_calls':0}
 sum_pin=save(HERE/'INDEPENDENT_FULL_SUMS.json',sums)
 report={'schema':'bass-he-e13c8-independent-heavy-saved-review-v1','reviewer':'e13c8_intake','observed_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS_ALL2331_SAVED_RELATIONS_AND_DIRECT_SUM' if not ri.failures else 'HOLD','source_lock_sha256':SOURCE,'execution_lock_sha256':EXEC,'collection_semantic_sha256':collection_sha,'candidate_modules_imported':0,'scientific_kernel_invocations':0,'checks_passed':sum(v['passed'] for v in ri.checks.values()),'checks_failed':sum(v['failed'] for v in ri.checks.values()),'checks':ri.checks,'failures':ri.failures,'paths':summaries,'direct_sum_file':{'path':'INDEPENDENT_FULL_SUMS.json',**sum_pin},'elapsed_seconds':time.perf_counter()-start,'physical':'HOLD','continuum':'HOLD','production':'HOLD','receiver':'HOLD','claim_ceiling':'Exact saved input/output relations and independent direct sums for the same finite captured target; no new coefficient computation and no extension of inherited interval proof.'}
 save(HERE/'FULL_SAVED_RETURN_REVIEW.json',report)
 print(json.dumps({k:report[k] for k in ('status','checks_passed','checks_failed','elapsed_seconds')}),flush=True)
 return 1 if ri.failures else 0

if __name__=='__main__':
 try:raise SystemExit(main())
 except BaseException as e:
  if isinstance(e,SystemExit):raise
  save(HERE/'REVIEW_FIRST_EXCEPTION.json',{'error':str(e),'type':type(e).__name__,'traceback':traceback.format_exc(),'failures':ri.failures,'scientific_kernel_invocations':0})
  raise
