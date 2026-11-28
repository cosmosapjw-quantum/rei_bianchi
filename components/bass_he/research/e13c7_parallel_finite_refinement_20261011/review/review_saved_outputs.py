#!/usr/bin/env python3
"""Independent exact review of saved E13C7 outputs. Never imports a project module."""
from pathlib import Path
from fractions import Fraction as F
import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
import review_inputs as ri

ROOT=ri.ROOT
HERE=ri.HERE
SOURCE='386d0abd02a33b15a015166369cec981b00fd05987dbd146f2badcb9f604688f'
KEYS=('schema','work','path_input_sha256','source_lock_sha256','input_checks','new_local_enclosures','new_coefficient_evaluations','rounding_operation_counts','forbidden_invocations')
check=ri.check
pair=ri.pair
cap=ri.cap
def add(a,b):return a[0]+b[0],a[1]+b[1]
def sub(a,b):return a[0]-b[1],a[1]-b[0]
def mul(a,b):
 v=[x*y for x in a for y in b]
 return min(v),max(v)
def point(x):return F(x),F(x)
def contains(a,b):return a[0]<=b[0]<=b[1]<=a[1]
def enclosing(actual,expected,label,detail):check(label,contains(pair(actual),expected),detail)
def summation(seq):
 out=point(0)
 for x in seq:out=add(out,x)
 return out
def all_boxes(x,where=''):
 if isinstance(x,dict):
  if set(x)=={'lo','hi'}:
   pair(x);check('all_saved_intervals_finite_ordered',True)
  else:
   for k,v in x.items():all_boxes(v,where+'/'+k)
 elif isinstance(x,list):
  for k,v in enumerate(x):all_boxes(v,where+'/'+str(k))
def new_metrics(track,w):
 values={'absolute':{k:tuple(v*w for v in pair(track['true_moment_enclosures'][k])) for k in ri.MOM},
         'correction':{k:tuple(v*w for v in pair(track['cumulative_moment_corrections'][k]['interval'])) for k in ri.MOM}}
 values['absolute']['P_final']=tuple(v*w for v in pair(track['final_photon']['true_absolute_interval']))
 values['absolute']['anchor']=tuple(v*w for v in pair(track['summed_true_anchor_eV']))
 values['correction']['P_final']=tuple(v*w for v in pair(track['final_photon']['true_minus_captured_interval']))
 values['correction']['energy_eV']=tuple(v*w for v in pair(track['final_energy_stock_eV']['true_minus_captured_interval']))
 for kind in values:
  for prefix in ('A','B','H'):
   suffix='_eV' if prefix!='A' else ''
   values[kind][prefix+'_total'+suffix]=tuple(sum(values[kind][prefix+'_'+s+suffix][i] for s in ri.SP) for i in (0,1))
 return values
def enc(a):return {'lo':str(a[0]),'hi':str(a[1])}
def comparison(a,b,kind,q):
 wa,wb=a[1]-a[0],b[1]-b[0]
 return {'kind':kind,'quantity':q,'old':enc(a),'new_raw':enc(b),'overlap':max(a[0],b[0])<=min(a[1],b[1]),'nested':a[0]<=b[0]<=b[1]<=a[1],'width_nonincreasing':wb<=wa,'old_width':str(wa),'new_width':str(wb),'gain_fraction':str((wa-wb)/wa) if wa else None}

def review(directory,index,lane):
 result=ri.read(directory/'RESULT.json');complete=ri.read(directory/'COMPLETE.json');admission=ri.read(directory/'ADMISSION.json')
 work=result['work'];node=work['node'];n=work['N'];prec=work['precision'];tag=(node,n,prec)
 check('no_preserved_failure_in_complete_path',not (directory/'FAILURE.json').exists() and not (directory/'RAW_COMPARISON_FAILURE.json').exists(),tag)
 check('work_mode_OFF',work['mode']=='OFF',tag)
 check('work_identity_consistent',admission['work']==work and all(complete[k]==work[k] for k in ('node','N','precision')),tag)
 check('source_input_binding',all(x['source_lock_sha256']==SOURCE and x['path_input_sha256']==index[str(node)]['path_input_sha256'] for x in (result,complete,admission)),tag)
 check('complete_status',complete['status']=='COMPLETE' and result['status']=='PASS_MECHANICAL_PENDING_INDEPENDENT_ADMISSION',tag)
 check('result_actual_sha',ri.h(directory/'RESULT.json')==complete['result_sha256'],tag)
 check('admission_actual_sha',ri.h(directory/'ADMISSION.json')==complete['admission_sha256'],tag)
 projection={k:result[k] for k in KEYS};projection['track']={k:v for k,v in result['track'].items() if k!='elapsed_seconds'}
 digest=hashlib.sha256(b'bass-he-e13c7-path-numerical-v1\n'+ri.canon(projection)).hexdigest()
 check('numerical_semantic_recomputed',digest==complete['semantic_sha256'],tag)
 rec=index[str(node)]
 with (ROOT/'inputs/OFF_OLD_PATHS.jsonl').open('rb') as stream:
  stream.seek(rec['offset']);raw=stream.read(rec['bytes'])
 check('old_selected_path_actual_bytes',hashlib.sha256(raw).hexdigest()==rec['old_line_sha256'],tag)
 old=json.loads(raw)
 track=result['track'];segments=track['segments'];seams=track['seams']
 check('ordered_path_controls',track['track']=={'mode':'OFF','node':node} and [s['key'] for s in segments]==rec['keys'],tag)
 check('fresh_enclosure_counts',len(segments)==rec['segments']==result['new_local_enclosures']==complete['new_local_enclosures'],tag)
 check('fresh_coefficient_counts',result['new_coefficient_evaluations']==complete['new_coefficient_evaluations']==2*n*len(segments),tag)
 check('all_input_checks_pass',bool(result['input_checks']) and all(x['pass'] for x in result['input_checks']),tag)
 check('no_forbidden_science',result['forbidden_invocations']=={k:0 for k in ('ODE_solves','native_runs','gas_advances','full_first2_reruns','old_budget_reruns','reused_local_enclosures')},tag)
 check('first_incoming_zero',F(segments[0]['incoming']['center'])==F(segments[0]['incoming']['radius'])==0 and pair(segments[0]['incoming']['interval'])==point(0),tag)
 check('seam_count',len(seams)==len(segments)-1,tag)
 all_boxes(track)
 for i,s in enumerate(segments):
  info=(node,n,prec,i)
  check('per_segment_fresh_count',s['local']['new_coefficient_evaluations']==2*n,info)
  check('per_segment_ledger_zero',all(pair(v)[0]<=0<=pair(v)[1] for v in s['ledger_enclosures'].values()),info)
  for k,o in s['outputs'].items():
   a=F(o['candidate']);radius=F(o['radius']);numeric=F(o['numerical_and_representation_radius'])
   check('radii_nonnegative',radius>=0 and numeric>=0,(info,k))
   enclosing(o['true_minus_captured_interval'],(a-radius,a+radius),'correction_encloses_center_radius',(info,k))
   enclosing(o['true_absolute_interval'],add(pair(s['captured'][k]),pair(o['true_minus_captured_interval'])),'absolute_encloses_capture_plus_correction',(info,k))
   check('numeric_radius_encloses_centered_interval',contains((a-numeric,a+numeric),pair(o['centered_firstvariation_plus_representation_interval'])),(info,k))
   enclosing(o['centered_firstvariation_plus_representation_interval'],add(pair(s['firstvariation_with_candidate_incoming'][k]),pair(s['representation_exactfrozen_minus_captured'][k])),'firstvariation_representation_added_once',(info,k))
   incoming=F(s['remainder']['incoming_upper'][k]);coupling=F(s['remainder']['nonlinear_upper'][k]);pre=F(s['remainder']['total_before_numerical_upper'][k])
   check('complete_radius_budget',incoming>=0 and coupling>=0 and pre>=incoming+coupling and radius>=numeric+pre,(info,k))
  for k,accum in s['cumulative_moment_corrections'].items():
   previous={'candidate':'0','radius':'0'} if i==0 else segments[i-1]['cumulative_moment_corrections'][k]
   outgoing=s['outputs'][k]
   ca,ra=F(previous['candidate']),F(previous['radius'])
   cb,rb=F(outgoing['candidate']),F(outgoing['radius'])
   cc,rc=F(accum['candidate']),F(accum['radius'])
   check('undamped_moment_radius_recentring',rc>=ra+rb+abs(cc-ca-cb),(info,k))
   enclosing(accum['interval'],(ca+cb-ra-rb,ca+cb+ra+rb),'undamped_moment_accumulation',(info,k))
   before=point(0) if i==0 else pair(segments[i-1]['cumulative_captured_moments'][k])
   enclosing(s['cumulative_captured_moments'][k],add(before,pair(s['captured'][k])),'captured_moment_accumulation',(info,k))
  if i:
   join=seams[i-1]
   check('incoming_seam_exact_object',s['incoming']==join['next_incoming'],info)
   left=segments[i-1]
   check('seam_keys',join['left']==left['key'] and join['right']==s['key'],info)
   enclosing(join['DeltaE_eV'],sub(pair(s['initial_energy_eV']),pair(left['endpoint_energy_eV'])),'signed_energy_jump_same_definition',info)
   check('outgoing_correction_carried_once',join['incoming_correction_to_anchor']==left['outputs']['P1']['true_minus_captured_interval'],info)
   enclosing(join['next_incoming']['interval'],add(pair(left['outputs']['P1']['true_minus_captured_interval']),pair(join['captured_photon_stitch_residual'])),'incoming_encloses_outgoing_plus_stitch',info)
   enclosing(join['true_anchor_eV'],mul(pair(join['DeltaE_eV']),add(pair(left['captured']['P1']),pair(left['outputs']['P1']['true_minus_captured_interval']))),'signed_seam_anchor_product',info)
 check('final_stock_is_last_endpoint',track['final_photon']==segments[-1]['outputs']['P1'] and track['final_energy_stock_eV']==segments[-1]['outputs']['P1_energy_eV'],tag)
 check('final_cumulative_fields',track['cumulative_moment_corrections']==segments[-1]['cumulative_moment_corrections'] and track['cumulative_captured_moments']==segments[-1]['cumulative_captured_moments'],tag)
 enclosing(track['summed_true_anchor_eV'],summation(pair(s['true_anchor_eV']) for s in seams),'anchor_sum_encloses_signed_seams',tag)
 for k,v in track['true_moment_enclosures'].items():
  enclosing(v,add(pair(track['cumulative_captured_moments'][k]),pair(track['cumulative_moment_corrections'][k]['interval'])),'true_moment_same_capture_plus_correction',(tag,k))
 check('global_ledger_contains_zero',all(pair(v)[0]<=0<=pair(v)[1] for v in track['global_ledger_enclosures'].values()),tag)
 # All branch/primary paths have a proven zero initial photon. Energy ledger
 # must include subtraction of the signed seam even on unanchored joins.
 energy=add(add(pair(track['final_energy_stock_eV']['true_absolute_interval']),pair(track['true_moment_enclosures']['B_total_eV'])),pair(track['true_moment_enclosures']['Z_eV']))
 energy=sub(sub(energy,pair(track['true_moment_enclosures']['QE_eV'])),pair(track['summed_true_anchor_eV']))
 enclosing(track['global_ledger_enclosures']['energy_eV_with_anchor_subtracted'],energy,'global_energy_ledger_signed_seams_subtracted',tag)
 oldm=ri.metrics(old);newm=new_metrics(track,pair(old['weight'])[0])
 check('old_metric_definition_exact',ri.decode(admission['old_weighted'])==oldm,tag)
 check('new_metric_definition_exact',ri.decode(admission['new_raw_weighted'])==newm,tag)
 rows=[]
 for kind in sorted(oldm):
  for q in sorted(oldm[kind]):rows.append(comparison(oldm[kind][q],newm[kind][q],kind,q))
 check('all_34_comparisons_recomputed',len(rows)==34 and rows==admission['comparisons'],tag)
 check('all_raw_comparisons_overlap',all(x['overlap'] for x in rows),tag)
 eligible=all(x['nested'] and x['width_nonincreasing'] for x in rows)
 check('mechanical_admission_boolean',eligible==admission['mechanically_admissible']==complete['mechanically_admissible'] and admission['intersection_used'] is False,tag)
 check('comparison_counts',admission['count']==34 and admission['overlap_count']==sum(x['overlap'] for x in rows) and admission['nested_count']==sum(x['nested'] for x in rows) and admission['nonincreasing_count']==sum(x['width_nonincreasing'] for x in rows),tag)
 if lane=='primary':check('primary_all34_admissible',eligible,tag)
 return {'node':node,'N':n,'precision':prec,'relative_directory':str(directory.relative_to(ROOT)),'result_sha256':ri.h(directory/'RESULT.json'),'admission_sha256':ri.h(directory/'ADMISSION.json'),'semantic_sha256':digest,'coefficient_evaluations':result['new_coefficient_evaluations'],'local_enclosures':result['new_local_enclosures'],'elapsed_seconds':result['elapsed_seconds'],'peak_RSS_KiB':result['peak_RSS_KiB'],'overlap_count':sum(x['overlap'] for x in rows),'nested_count':sum(x['nested'] for x in rows),'nonincreasing_count':sum(x['width_nonincreasing'] for x in rows),'mechanically_admissible':eligible}

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--lane',choices=['branch','primary','resolution'],required=True)
 parser.add_argument('--run-dir',type=Path,required=True)
 parser.add_argument('--report-name',required=True)
 args=parser.parse_args();start=time.perf_counter()
 check('sealed_source_lock',ri.h(ROOT/'SOURCE_LOCK.json')==SOURCE)
 index=ri.read(ROOT/'inputs/INPUT_INDEX.json')['records']
 complete=sorted(args.run_dir.rglob('COMPLETE.json'))
 summaries=[review(p.parent,index,args.lane) for p in complete]
 actual={(x['node'],x['N'],x['precision']) for x in summaries}
 contract=ri.read(ROOT/'RESEARCH_CONTRACT.json')
 if args.lane=='branch':expected={(node,n,p) for node in contract['local_branch_control_nodes'] for n,p in ((32,60),(32,80),(128,60))}
 elif args.lane=='primary':expected={(node,512,60) for node in contract['local_primary_nodes']}
 else:expected={(node,1024,60) for node in contract['local_resolution_diagnostic_nodes']}
 check('declared_work_units_complete_once',actual==expected and len(summaries)==len(expected))
 result={'schema':'bass-he-e13c7-independent-saved-output-review-v1','lane':args.lane,'reviewer':'e13c7_intake','observed_utc':datetime.now(timezone.utc).isoformat(),'source_lock_sha256':SOURCE,'candidate_modules_imported':0,'scientific_kernel_invocations':0,'checks_passed':sum(x['passed'] for x in ri.checks.values()),'checks_failed':sum(x['failed'] for x in ri.checks.values()),'checks':ri.checks,'failures':ri.failures,'paths':summaries,'elapsed_seconds':time.perf_counter()-start,'status':'PASS_SAVED_OUTPUT_RELATIONS' if not ri.failures else 'HOLD','claim_ceiling':'Independent source-bound saved relation review; reuses inherited mathematical interval proof, not an independent new coefficient computation.'}
 (HERE/args.report_name).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({k:result[k] for k in ('lane','status','checks_passed','checks_failed','elapsed_seconds')}))
 if ri.failures:print(json.dumps(ri.failures)[:15000])
 return 1 if ri.failures else 0

if __name__=='__main__':raise SystemExit(main())
