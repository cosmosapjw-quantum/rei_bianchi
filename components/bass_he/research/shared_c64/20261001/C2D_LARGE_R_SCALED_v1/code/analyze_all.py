"""Collect identity-verified C2d evidence; scalar-only, no physical evaluation."""
import argparse, copy, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from analyze_states import documents,state_ref,audit_states
from anchor_audit import evaluate_anchors,merge_observation_values
from continuation_audit import continuation_audit,parity_audit
from mpi_batch import atomic_create,json_bytes

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 c=json.loads((ROOT/'CONTRACT.json').read_bytes())
 recovery=None;recovered_original=None
 if (ROOT/'review/RECOVERY_PLAN.json').exists():
  from recovery_support import verify_recovered
  recovery=verify_recovered(ROOT,'review/RECOVERY_PLAN.json')
  recovered_original=json.loads((ROOT/'review/RECOVERY_PLAN.json').read_bytes())['partial_index']['batch']
 docs=documents();states=audit_states(docs,c)
 selected={float(k):v for k,v in states['selected_states'].items()}
 old=json.loads((ROOT/'frozen/R16_base/RESULT.json').read_bytes())
 selected_values={}
 for radius in c['new_R']:
  ref=selected.get(radius)
  if ref is None:continue
  matches=[d for d in docs if d['parameters']['kind']=='prolate' and state_ref(d)==ref]
  if len(matches)!=1:raise RuntimeError('SELECTED_STATE_BINDING')
  value=copy.deepcopy(matches[0]['value'])
  for extra in docs:
   if extra['parameters']['kind']=='operator_refinement' and extra['parameters']['state']==ref:
    for lane in ('direct','force'):value[lane].update(extra['value'][lane])
  selected_values[radius]=value
 observations={};quality={}
 for doc in docs:
  p=doc['parameters']
  if p['kind']!='sphere_observe':continue
  label=p['label'];state_docs=[]
  for ref in (p['left'],p['right']):
   found=[d for d in docs if d['parameters']['kind']=='sphere' and state_ref(d)==ref]
   if len(found)!=1:raise RuntimeError('ANCHOR_STATE_BINDING')
   state_docs.append(found[0])
  cfg={**c['spherical_anchor']['configurations'],**c['spherical_anchor']['fallback_configurations']}[label]
  if not all(d['parameters']['configuration']=={**cfg,'m':m} for m,d in enumerate(state_docs)):raise RuntimeError('ANCHOR_CONFIGURATION_BINDING')
  if len(doc['value']['states'])!=2:raise RuntimeError('ANCHOR_OBSERVATION_STATE_COUNT')
  for observed,source in zip(doc['value']['states'],state_docs):
   if observed!={'folder':str((ROOT/source['folder']).resolve()),'data_sha256':digest(ROOT/source['path']),'state_sha256':source['result']['state_sha256'],'state_bytes':source['result']['state_bytes']}:raise RuntimeError('ANCHOR_OBSERVATION_DATA_BINDING')
  quality[label]=[d['value'] for d in state_docs]
  observations[label]=merge_observation_values(observations[label],doc['value']) if label in observations else doc['value']
 anchor=evaluate_anchors(observations,selected_values.get(c['spherical_anchor']['R'],{}),c,state_values=quality)
 overlap={}
 for doc in docs:
  p=doc['parameters']
  if p['kind']!='overlap':continue
  v=doc['value']
  if not (p['left']==selected.get(v['R_left']) and p['right']==selected.get(v['R_right']) and p['sector']==v['m'] and p['order']==v['order']):raise RuntimeError('OVERLAP_SELECTED_STATE_BINDING')
  overlap[doc['task_id']]=v
 continuation=continuation_audit(overlap,c)
 actual={};references={}
 for doc in docs:
  p=doc['parameters']
  if p['kind']!='parity':continue
  index=p['index'];key=str(index);case=c['parity_cases'][index]
  if p['case']!=case or key in actual:raise RuntimeError('PARITY_CASE_BINDING')
  actual[key]=doc['value']
  if case['kind']=='overlap':
   if p['left']!=selected.get(case['edge'][0]) or p['right']!=selected.get(case['edge'][1]):raise RuntimeError('PARITY_OVERLAP_BINDING')
   found=[v for v in overlap.values() if [v['R_left'],v['R_right']]==case['edge'] and v['m']==case['sector'] and v['order']==case['order']]
   if len(found)!=1:raise RuntimeError('PARITY_REFERENCE_BINDING')
   references[key]=found[0]
  else:
   if p['state']!=selected.get(case['R']):raise RuntimeError('PARITY_STATE_BINDING')
   references[key]=(old['operators']['direct'] if case['R']==16 else selected_values[case['R']][case['kind']])[str(case['order'])]
 parity=parity_audit(actual,references,c)
 batches=[];attempts=[];attempted_kinds={};manifest_upper_kinds={}
 for receipt in sorted((ROOT/'evidence').glob('*MPI_LAUNCH.json')):
  r=json.loads(receipt.read_bytes());folder=receipt.with_name(receipt.name.removesuffix('_LAUNCH.json'))
  summary=folder/'BATCH_SUMMARY.json'
  row={'folder':str(folder.relative_to(ROOT)),'elapsed_seconds':r['elapsed_seconds'],'preflight_passed':r['preflight_passed'],'source_unchanged':r['source_unchanged'],'cleanup_complete':r['cleanup_complete'],'returncode':r['returncode'],'memory_events_delta':r['memory_events_delta'],'timed_out':r['timed_out']}
  partial=folder/'PARTIAL_BATCH_INDEX.json'
  if not summary.exists() and not partial.exists():
   row['status']='PREFLIGHT_BLOCKED_NO_SCIENCE' if not folder.exists() and not r['preflight_passed'] else 'INCOMPLETE_EXECUTION'
   attempts.append(row);continue
  if partial.exists():
   if recovery is None or str(folder.relative_to(ROOT))!=recovered_original:raise RuntimeError('PARTIAL_BATCH_WITHOUT_VERIFIED_RECOVERY')
   from recovery_support import load_partial_batch
   s=load_partial_batch(ROOT,folder)
   row['recovery_status']=recovery['status']
  else:s=json.loads(summary.read_bytes())
  manifest=json.loads((folder/'MANIFEST_INPUT.json').read_bytes())
  for t in manifest['tasks']:
   k=t['parameters']['kind'];manifest_upper_kinds[k]=manifest_upper_kinds.get(k,0)+1
   if (folder/t['task_id']).exists():attempted_kinds[k]=attempted_kinds.get(k,0)+1
  row.update(task_count=len(s['tasks']),failed_tasks=[t['task_id'] for t in s['tasks'] if t['status']!='WORKER_RESULT_PASS'],status=s['status'])
  batches.append(row)
 op=c['operational_limits'];total_wall=sum(b['elapsed_seconds'] for b in batches)
 charged_wall=total_wall+sum(b['elapsed_seconds'] for b in attempts)
 if recovery is not None:
  inv=recovery['final_attempt_inventory']
  if inv['actual_started_by_kind']!=attempted_kinds or inv['manifest_upper_bound_by_kind']!=manifest_upper_kinds or abs(inv['charged_wall_seconds']-charged_wall)>1e-9:raise RuntimeError('RECOVERY_FINAL_LEDGER_DISAGREES')
 kinds={kind:sum(d['parameters']['kind']==kind for d in docs) for kind in sorted({d['parameters']['kind'] for d in docs})}
 attempted_selected=2*(attempted_kinds.get('prolate',0)+attempted_kinds.get('bridge',0))+attempted_kinds.get('sphere',0)
 budgets={'new_selected_states':sum(d['new_eigenstates'] for d in docs),'selected_states_attempt_upper_bound':attempted_selected,'counts_by_kind':kinds,'attempted_counts_by_kind':attempted_kinds,'manifest_task_count_upper_bound_by_kind':manifest_upper_kinds,'charged_all_launch_wall_seconds':charged_wall,'active_batch_wall_seconds':total_wall,'preflight_only_wall_seconds':sum(b['elapsed_seconds'] for b in attempts if b['status']=='PREFLIGHT_BLOCKED_NO_SCIENCE'),'max_worker_rss_mib':max((d['result']['max_rss_kib']/1024 for d in docs),default=0),'spherical_requested_Ritz_roots_upper_bound':2*attempted_kinds.get('sphere',0)}
 budget_gates={'selected_states':attempted_selected<=op['new_eigenstates_total_max'],'prolate_pairs':attempted_kinds.get('prolate',0)+attempted_kinds.get('bridge',0)<=op['new_prolate_pairs_max'],'bridge_pairs':attempted_kinds.get('bridge',0)<=op['new_bridge_pairs'],'sphere_states':attempted_kinds.get('sphere',0)<=op['new_spherical_eigenstates_max'],'operator_refinements':attempted_kinds.get('operator_refinement',0)<=op['operator_refinement_tasks_max'],'overlap_evaluations':attempted_kinds.get('overlap',0)<=op['overlap_edge_orders_max'],'parity_evaluations':attempted_kinds.get('parity',0)<=op['parity_evaluations_max'],'total_wall':charged_wall<=op['total_active_science_wall_seconds'],'task_wall':all(d['result']['elapsed_seconds']<=op['task_wall_seconds'] for d in docs)}
 execution_ok=bool(batches) and all((b['returncode']==0 and not b['failed_tasks'] and b['source_unchanged'] and b['cleanup_complete'] and b['preflight_passed']) or (recovery is not None and b['folder']==recovered_original and b['returncode']==124 and b['timed_out'] and b.get('recovery_status')=='WHOLE_BATCH_TIMEOUT_RECOVERED_WITHIN_ORIGINAL_BUDGET') for b in batches) and all(b['status']=='PREFLIGHT_BLOCKED_NO_SCIENCE' and b['source_unchanged'] and b['cleanup_complete'] for b in attempts)
 gates={'state_quartets':states['all_new_R_numerical_gates_pass'],'bridge_execution_phase':states['all_bridge_gates_pass'],'anchor':anchor['accepted'],'continuation':continuation['pass'],'parity':parity['pass'],'execution':execution_ok,'budgets':all(budget_gates.values())}
 stop='SCOPED_LARGE_R_SCALED_SEQUENCE_CONVERGED' if all(gates.values()) else 'LARGE_R_EXECUTION_BLOCKED' if not execution_ok else 'LARGE_R_SCALED_NUMERICS_UNRESOLVED'
 sequence=[]
 inherited=json.loads((ROOT/'evidence/INHERITED_POINT_SCALARS.json').read_bytes())
 for row in inherited['rows']:
  sequence.append({'R':row['R'],'new_point':False,'scaled_closure_claimed':False,'L_O_bar':row['raw_selected_direct']['L_O_bar'],'L_B_bar':row['raw_selected_direct']['L_B_bar'],**row['scaled']['direct']})
 for radius,value in sorted(selected_values.items()):
  d=value['direct'][str(max(map(int,value['direct'])))];f=value['force'][str(max(map(int,value['force'])))];lo,lb=d['L_O_bar'],d['L_B_bar']
  sequence.append({'R':radius,'new_point':True,'scaled_closure_claimed':True,'L_O_bar':lo,'L_B_bar':lb,'Q_O':lo/radius,'Q_B':-radius**2*lb,'Q_O_force':f['L_O_bar']/radius,'Q_B_force':-radius**2*f['L_B_bar']})
 for row in sequence:
  for key in ('Q_O','Q_B'):
   coefficient=c['coefficients'][key]['value'];row[key+'_minus_C']=row[key]-coefficient;row[key+'_relative_difference_from_C']=row[key]/coefficient-1
 result={'node':c['node'],'stop':stop,'gates':gates,'contract_sha256':digest(ROOT/'CONTRACT.json'),'analysis_source_sha256':digest(Path(__file__)),'recovery_audit':recovery,'state_audit':states,'anchor_audit':anchor,'continuation_audit':continuation,'parity_audit':parity,'sequence':sequence,'budgets':budgets,'budget_gates':budget_gates,'batches':batches,'launch_attempts_without_summary':attempts,'input_DATA_sha256':{d['path']:digest(ROOT/d['path']) for d in docs},'coefficients':c['coefficients'],'asymptotic_remainder_bound_known':False,'new_physical_evaluations_by_analysis':0,'global_gates':c['gates']}
 if recovery is not None:atomic_create(ROOT/'evidence/RECOVERY_LEDGER.json',json_bytes(recovery))
 atomic_create(a.output,json_bytes(result));print(json.dumps({k:result[k] for k in ('stop','gates','budgets','sequence')},indent=2))

if __name__=='__main__':main()
