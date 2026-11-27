#!/usr/bin/env python3
"""Bounded review of new residual/telemetry summaries; no science replay."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext
from datetime import datetime,timezone
import json
import time
import review_inputs as ri

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
BATCH=ROOT.parent/'ACTUAL_NCP_RETURN/BATCH'

def display(x):
 with localcontext() as c:
  c.prec=22
  return str(Decimal(x.numerator)/Decimal(x.denominator))
def verify_pins(base,pins,label):
 for name,pin in pins.items():
  p=base/name
  ri.check(label,p.stat().st_size==pin['bytes'] and ri.h(p)==pin['sha256'],name)

def main():
 start=time.perf_counter()
 full=ri.decode(ri.read(HERE/'INDEPENDENT_FULL_SUMS.json')['full_raw_candidate'])
 residual=ROOT/'analysis/RESIDUAL/ACTUAL'
 res=ri.read(residual/'RESIDUAL_SUMMARY.json')
 rreceipt=ri.read(residual/'RESIDUAL_EXECUTION_RECEIPT.json')
 verify_pins(residual,rreceipt['outputs'],'new_residual_output_identity')
 ri.check('residual_script_identity',ri.h(residual.parent/'analyze_saved_residual.py')==rreceipt['source_sha256'])
 ri.check('residual_no_kernel',rreceipt['scientific_kernel_calls']==0 and rreceipt['vendor_modules_loaded'] is False and res['scientific_kernel_calls']==0)
 paths=ri.read(residual/'PATH_RESIDUALS.json')['paths']
 ri.check('residual_nonzero_complete_once',[r['node'] for r in paths]==list(range(2345)) and res['tracks_consumed']==2345 and res['exact_zero_paths_retained']==95)
 cats=('midpoint_truncation','other_numerical_representation','coupling_bound','rounding_bookkeeping')
 keys=tuple(res['metrics'])
 cat_sums={q:{c:F(0) for c in cats} for q in keys}
 origins={name:{q:F(0) for q in keys} for name in res['origin_groups']}
 for r in paths:
  for q in keys:
   m=r['metrics'][q];width=F(m['width_exact']);cat={c:F(m['half_width_allocation_exact'][c]) for c in cats}
   ri.check('nonnegative_exact_halfwidth_allocation',width>=0 and all(x>=0 for x in cat.values()) and sum(cat.values())==width/2,(r['node'],q))
   origins[r['origin']][q]+=width
   for c,x in cat.items():cat_sums[q][c]+=x
 for q in keys:
  width=full['absolute'][q][1]-full['absolute'][q][0]
  ri.check('residual_full_width_is_independent_result',F(res['metrics'][q]['width_exact'])==width,q)
  ri.check('residual_positive_direct_width_sum',sum(origins[o][q] for o in origins)==width,q)
  for cat in cats:
   row=res['metrics'][q]['half_width_allocation'][cat]
   ri.check('residual_category_sum_exact',F(row['exact'])==cat_sums[q][cat],(q,cat))
   ri.check('residual_category_percent_display',row['percent']==display(200*cat_sums[q][cat]/width),(q,cat))
  for origin in origins:
   row=res['origin_groups'][origin][q]
   ri.check('residual_origin_width_and_percent',F(row['width_exact'])==origins[origin][q] and row['percent_of_full']==display(100*origins[origin][q]/width),(origin,q))
 ri.check('residual_input_candidate_bound',res['inputs']['reduction_sha256']==ri.h(ROOT/'analysis/FULL_RETURN_REDUCTION/REDUCTION.json'))
 perfroot=ROOT/'analysis/PERFORMANCE'
 perf=ri.read(perfroot/'PERFORMANCE_ANALYSIS.json');pidentity=ri.read(perfroot/'PERFORMANCE_IDENTITY.json')
 verify_pins(perfroot,pidentity['files'],'performance_output_identity')
 ri.check('performance_no_replay',pidentity['scientific_kernel_calls']==pidentity['MPI_launches']==0 and pidentity['actual_exit']==0)
 ri.check('performance_actual_work',perf['work']['rank_count']==perf['work']['computing_rank_count']==64 and perf['work']['controller_only_MPI_rank_count']==0 and perf['work']['paths']==2331 and perf['work']['new_coefficient_evaluations']==9547776 and perf['work']['automatic_retries']==0)
 raw_ranks=[]
 for row in perf['per_rank']:
  d=BATCH/f"ranks/rank_{row['rank']:04d}"
  st=ri.read(d/'START.json');rc=ri.read(d/'RECEIPT.json')
  ri.check('performance_rank_binding_actual',st['cpu_affinity']==[row['cpu_id']] and st['thread_count']==row['thread_count']==1,row['rank'])
  ri.check('performance_rank_elapsed_and_RSS_actual',rc['elapsed_seconds']==row['rank_reported_elapsed_seconds'] and rc['peak_RSS_KiB']==row['peak_RSS_KiB'],row['rank'])
  raw_ranks.append(rc)
 ri.check('performance_unique64CPUs',sorted(r['cpu_id'] for r in perf['per_rank'])==list(range(64)))
 controller=ri.read(BATCH/'EXECUTION_RECEIPT.json');launcher=ri.read(BATCH/'LAUNCH_PROCESS_RECEIPT.json')
 ri.check('performance_wall_scopes_actual',perf['wall_times']['controller_batch_seconds']==controller['elapsed_seconds'] and perf['wall_times']['MPI_launcher_seconds']==launcher['elapsed_seconds'])
 rss=sum(r['peak_RSS_KiB'] for r in raw_ranks)
 ri.check('RSS_sum_per_process_not_per_path',perf['memory']['sum_rank_individual_high_water_RSS_KiB']==rss and perf['memory']['sum_rank_individual_high_water_RSS_GiB']==rss/2**20 and perf['memory']['sum_rank_plus_controller_individual_high_water_RSS_GiB']==(rss+controller['controller_peak_RSS_KiB'])/2**20)
 for k in ('rank_lifetime_UTC','path_reservation_through_validation_UTC'):
  a=perf['task_envelope_accounting'][k]
  hist={int(i):F(str(v)) for i,v in a['seconds_by_simultaneous_envelopes'].items()}
  span=sum(hist.values());area=sum(i*t for i,t in hist.items())
  ri.check('envelope_histogram_direct_integral',F(str(a['span_seconds']))==span and F(str(a['summed_envelope_seconds']))==area,k)
  ri.check('envelope_ratio_exact_published_times',F(a['mean_simultaneous_envelopes']['exact_published_decimal_ratio'])==area/span,k)
 ri.check('performance_CPUutil_not_invented',perf['CPU_telemetry']['CPU_time_over_wall_utilization']=='NOT_MEASURED' and perf['CPU_telemetry']['measured_same_work_serial_speedup']=='NOT_ESTABLISHED' and perf['wall_times']['sum_parallel_path_time_is_measured_serial_runtime'] is False)
 ri.check('performance_memory_peak_not_invented',perf['memory']['simultaneous_global_peak_RSS']=='NOT_MEASURED')
 ri.check('performance_LPT_is_counterfactual',perf['balance']['retrospective_fixed_duration_LPT']['status']=='OFFLINE_ARITHMETIC_NOT_EXECUTED_SCHEDULE')
 report={'schema':'bass-he-e13c8-independent-analysis-scope-review-v1','status':'PASS_NEW_RESIDUAL_AND_TELEMETRY_ANALYSIS_SCOPE' if not ri.failures else 'HOLD','reviewer':'e13c8_intake','observed_utc':datetime.now(timezone.utc).isoformat(),'checks_passed':sum(v['passed'] for v in ri.checks.values()),'checks_failed':sum(v['failed'] for v in ri.checks.values()),'checks':ri.checks,'failures':ri.failures,'candidate_modules_imported':0,'scientific_kernel_calls':0,'MPI_calls':0,'saved_full_path_scientific_recheck':False,'residual_static_review':{'recurrence':'Previous P radius categories propagated through absolute gain; seam excess and total residual rounding allocated explicitly; local midpoint/numerical remainder/coupling categories nonnegative; species sums and final photon endpoint match the admitted metrics.','coupling_eta_dependence_preserved':True,'N_independent_or_physical_floor_claimed':False,'allocation_is_unique_error_cause_decomposition':False,'validated_output':'All2345 new saved attribution rows sum exactly to their positive half-width; category/origin sums reproduce the independent full widths.'},'telemetry_static_review':{'wall_mean_max_is_CPU_efficiency':False,'UTC_envelope_is_CPU_busy_fraction':False,'lifetime_high_water_sum_is_simultaneous_peak':False,'retrospective_LPT_was_executed':False,'same_work_serial_speedup_established':False},'evidence':{str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':ri.h(p)} for p in [residual/'RESIDUAL_SUMMARY.json',residual/'RESIDUAL_EXECUTION_RECEIPT.json',perfroot/'PERFORMANCE_ANALYSIS.json',perfroot/'PERFORMANCE_IDENTITY.json']},'elapsed_seconds':time.perf_counter()-start}
 with (HERE/'ANALYSIS_SCOPE_REVIEW.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps({k:report[k] for k in ('status','checks_passed','checks_failed','elapsed_seconds')}),flush=True)
 return 1 if ri.failures else 0

if __name__=='__main__':raise SystemExit(main())
