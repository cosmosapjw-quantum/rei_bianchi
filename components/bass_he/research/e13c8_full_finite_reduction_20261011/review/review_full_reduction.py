#!/usr/bin/env python3
"""Compare independent actual path sums to the untouched candidate reducer outputs."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext
from datetime import datetime,timezone
import csv
import io
import hashlib
import json
import time
import review_inputs as ri

HERE=Path(__file__).resolve().parent
ROOT8=HERE.parent
ROOT7=Path('/workspace/scratch/7fd51143e473/e13c7_research_20261011/BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1')
INTAKE=ROOT8.parent/'intake'
ACTUAL=ROOT8.parent/'ACTUAL_NCP_RETURN'

def pin(p):return {'bytes':p.stat().st_size,'sha256':ri.h(p)}
def write(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False);f.write('\n')
def display(v):
 with localcontext() as c:
  c.prec=22
  return str(Decimal(v.numerator)/Decimal(v.denominator))

def main():
 start=time.perf_counter()
 independent=ri.read(HERE/'INDEPENDENT_FULL_SUMS.json')
 saved=ri.read(HERE/'FULL_SAVED_RETURN_REVIEW.json')
 target=ROOT8/'analysis/FULL_RETURN_REDUCTION'
 candidate=ri.read(target/'REDUCTION.json');identity=ri.read(target/'REDUCTION_IDENTITY.json')
 intake=ri.read(INTAKE/'ACTUAL_INTAKE_RECEIPT.json')
 previous=ri.read(ROOT7/'review/INDEPENDENT_DECISION.json')
 local_path=ROOT7/'analysis/LOCAL/LOCAL_ADMITTED_CANDIDATE.json'
 local=ri.read(local_path)
 pred=ri.read(ROOT7/'inputs/PREDECESSOR_BUDGET.json')
 ri.check('full_saved_review_passed',saved['status']=='PASS_ALL2331_SAVED_RELATIONS_AND_DIRECT_SUM' and saved['checks_failed']==0 and len(saved['paths'])==2331)
 ri.check('saved_review_direct_sums_actual_bytes',pin(HERE/'INDEPENDENT_FULL_SUMS.json')=={k:saved['direct_sum_file'][k] for k in ('bytes','sha256')})
 ri.check('previous_scoped_local_admission',previous['decision']=='PROMOTE_SCOPED_LOCAL_FINITE_REFINEMENT_AND_READY_HEAVY_HANDOFF')
 ri.check('previous_actual_candidate_identity',ri.h(local_path)==previous['local_admission']['candidate_sha256'])
 ri.check('independent_retained_local_eight_direct_sum',ri.combine(ri.decode(p['new_raw_weighted']) for p in local['paths'])==ri.decode(local['new_local_eight']))
 ri.check('retained_prior_six_exact_same',ri.decode(local['retained_prior_six'])==ri.decode(pred['prior_six']))
 ri.check('current_intake_archive_identity',intake['status']=='PASS_ACTUAL_ARCHIVE_AND_PAYLOAD_IDENTITY' and intake['archive']=={'bytes':124152692,'sha256':'a7a0fd6e58a88140071a1b623897efbd35748c86c4eda6956a937171eefe6c8f'})
 ri.check('intake_payload_and_original_execution_closure',intake['archive_members']==18800 and intake['payload_files_verified']==18799 and intake['predecessor_execution_files_verified']==60 and intake['source_input_before_after_identical'] is True)
 ri.check('actual_return_manifest_identity',ri.h(ACTUAL/'RETURN_MANIFEST.json')==intake['manifest_sha256']=='189a7aa1b4e93c489716fd431d7164c1333ecd2dea20bc7703274bff1bcca555')
 ri.check('candidate_status_and_scope',candidate['status']=='PASS_MECHANICAL_PENDING_INDEPENDENT_REVIEW' and candidate['mode']=='ncp-return' and candidate['paths_consumed']==2331 and candidate['not_admissible_nodes']==[])
 for k in ('source_lock_sha256','execution_lock_sha256'):
  ri.check('candidate_same_locked_work',candidate[k]==independent[k],k)
 ri.check('candidate_same_collection',candidate['ordered_collection_semantic_sha256']==independent['collection_semantic_sha256']==intake['collection_semantic_sha256'])
 for k in ('old_group','new_raw_group','retained_direct_sum','full_before','full_raw_candidate'):
  a=ri.decode(independent[k]);b=ri.decode(candidate[k])
  ri.check('direct_sum_quantity_coverage',set(a)==set(b) and all(set(a[t])==set(b[t]) for t in a),k)
  for kind in a:
   for q,v in a[kind].items():ri.check('candidate_exact_endpoint_matches_independent_sum',v==b[kind][q],(k,kind,q))
 ri.check('candidate_all34_comparisons_exact',candidate['full_comparison']==independent['full_comparison'] and len(candidate['full_comparison'])==34)
 ri.check('no_intersection_or_fallback',candidate['intersection_used'] is False and candidate['old_fallback_used'] is False and candidate['all_34_direct_predecessor_bridges'] is True)
 ri.check('no_reducer_kernel',candidate['kernel_invocations_in_reduction']==0)
 for k in ('physical','continuum','production','receiver'):ri.check('claim_ceiling_preserved',candidate[k]=='HOLD',k)
 ordered=[{'node':p['node'],'semantic_sha256':p['semantic_sha256'],'mechanically_admissible':p['mechanically_admissible']} for p in saved['paths']]
 ri.check('all_candidate_path_semantics_independently_verified',candidate['path_evidence']==ordered)
 semantic=hashlib.sha256(b'bass-he-e13c7-return-reduction-v1\n'+ri.canon(candidate)).hexdigest()
 ri.check('actual_candidate_semantic',semantic==identity['semantic_sha256']=='d647ba154b84baf22a3f85f9b7dca19f029b97f466838c036a9d3321f4c315d1')
 ri.check('actual_candidate_result_sha',ri.h(target/'REDUCTION.json')==identity['result_sha256'])
 buf=io.StringIO(newline='');writer=csv.writer(buf)
 writer.writerow(['kind','quantity','old_width_exact','new_raw_width_exact','gain_percent','nested','width_nonincreasing'])
 for r in independent['full_comparison']:
  writer.writerow([r['kind'],r['quantity'],r['old_width'],r['new_width'],display(100*F(r['gain_fraction'])) if r['gain_fraction'] is not None else 'EXACT_ZERO',r['nested'],r['width_nonincreasing']])
 csv_bytes=buf.getvalue().encode()
 ri.check('full_CSV_actual_bytes_independent',csv_bytes==(target/'FULL_WIDTHS.csv').read_bytes())
 ri.check('full_CSV_actual_sha',hashlib.sha256(csv_bytes).hexdigest()==identity['csv_sha256'])
 widths={r['quantity']:{'old_width_exact':r['old_width'],'new_width_exact':r['new_width'],'old_width_display':display(F(r['old_width'])),'new_width_display':display(F(r['new_width'])),'gain_percent_display':display(100*F(r['gain_fraction'])) if r['gain_fraction'] is not None else 'EXACT_ZERO'} for r in independent['full_comparison'] if r['kind']=='absolute'}
 report={'schema':'bass-he-e13c8-independent-full-reduction-review-v1','reviewer':'e13c8_intake','status':'PASS_INDEPENDENT_EXACT_FULL_REDUCTION' if not ri.failures else 'HOLD','observed_utc':datetime.now(timezone.utc).isoformat(),'checks_passed':sum(v['passed'] for v in ri.checks.values()),'checks_failed':sum(v['failed'] for v in ri.checks.values()),'checks':ri.checks,'failures':ri.failures,'candidate_modules_imported':0,'scientific_kernel_invocations':0,'candidate_semantic_sha256':semantic,'candidate_identity':identity,'full_absolute_widths':widths,'evidence':{str(p.relative_to(ROOT8)) if p.is_relative_to(ROOT8) else str(p):pin(p) for p in [HERE/'FULL_SAVED_RETURN_REVIEW.json',HERE/'INDEPENDENT_FULL_SUMS.json',target/'REDUCTION.json',target/'FULL_WIDTHS.csv',target/'REDUCTION_IDENTITY.json',INTAKE/'ACTUAL_INTAKE_RECEIPT.json',ROOT7/'review/INDEPENDENT_DECISION.json']},'elapsed_seconds':time.perf_counter()-start,'scope':'2440 captured OFF paths:2331 returned N1024/P60,8 locally admitted mixed-N paths,6 previously admitted paths,95 exact-zero paths. No cross-mode sum.','limitations':['Reuses inherited directed-interval proof and same captured source/mask model.','No independent new coefficient evaluation or continuum/physical assertion.','Root actual archive/payload intake reused by identity; independent review separately checks every critical saved result/admission/completion file and all path semantics.']}
 write(HERE/'FULL_REDUCTION_REVIEW.json',report)
 print(json.dumps({k:report[k] for k in ('status','checks_passed','checks_failed','candidate_semantic_sha256','elapsed_seconds')}),flush=True)
 return 1 if ri.failures else 0

if __name__=='__main__':raise SystemExit(main())
