"""Collect verified C2c evidence; scalar-only, no numerical solves/integrals."""
import argparse,copy,hashlib,json,sys
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
 contract=json.loads((ROOT/'CONTRACT.json').read_bytes());docs=documents();states=audit_states(docs,contract)
 selected={float(k):v for k,v in states['selected_states'].items()}
 folder=ROOT/'frozen/R0p25_base';old=json.loads((folder/'RESULT.json').read_bytes())
 assert digest(folder/'STATE.npz')==old['state_sha256']
 selected[.25]={'folder':str(folder.relative_to(ROOT)),'state_sha256':old['state_sha256'],'result_sha256':digest(folder/'RESULT.json')}
 selected_values={}
 for radius,ref in selected.items():
  if radius==.25:continue
  matches=[d for d in docs if d['parameters']['kind']=='prolate' and state_ref(d)==ref]
  assert len(matches)==1
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
   matches=[d for d in docs if d['parameters']['kind']=='sphere' and state_ref(d)==ref]
   assert len(matches)==1
   state_docs.append(matches[0])
  cfg={**contract['spherical_anchor']['configurations'],**contract['spherical_anchor']['fallback_configurations']}[label]
  assert all(d['parameters']['configuration']=={**cfg,'m':m} for m,d in enumerate(state_docs))
  quality[label]=[d['value'] for d in state_docs]
  observations[label]=merge_observation_values(observations[label],doc['value']) if label in observations else doc['value']
 anchor=evaluate_anchors(observations,selected_values.get(.125,{}),contract,state_values=quality)
 overlap={}
 for doc in docs:
  p=doc['parameters']
  if p['kind']!='overlap':continue
  v=doc['value'];assert p['left']==selected[v['R_left']] and p['right']==selected[v['R_right']]
  assert p['sector']==v['m'] and p['order']==v['order']
  overlap[doc['task_id']]=v
 continuation=continuation_audit(overlap,contract)
 actual={};references={}
 for doc in docs:
  p=doc['parameters']
  if p['kind']!='parity':continue
  index=p['index'];key=str(index);case=contract['parity_cases'][index]
  assert p['case']==case and key not in actual
  actual[key]=doc['value']
  if case['kind']=='overlap':
   assert p['left']==selected[case['edge'][0]] and p['right']==selected[case['edge'][1]]
   found=[v for v in overlap.values() if [v['R_left'],v['R_right']]==case['edge'] and v['m']==case['sector'] and v['order']==case['order']]
   assert len(found)==1;references[key]=found[0]
  else:
   assert p['state']==selected[case['R']]
   references[key]=(old['operators']['direct'] if case['R']==.25 else selected_values[case['R']][case['kind']])[str(case['order'])]
 parity=parity_audit(actual,references,contract)
 batches=[]
 for folder in sorted((ROOT/'evidence').glob('*MPI')):
  summary=folder/'BATCH_SUMMARY.json';receipt=folder.with_name(folder.name+'_LAUNCH.json')
  if summary.exists():
   s=json.loads(summary.read_bytes());r=json.loads(receipt.read_bytes())
   batches.append({'folder':str(folder.relative_to(ROOT)),'task_count':len(s['tasks']),'failed_tasks':[t['task_id'] for t in s['tasks'] if t['status']!='WORKER_RESULT_PASS'],
    'elapsed_seconds':r['elapsed_seconds'],'preflight_passed':r['preflight_passed'],'source_unchanged':r['source_unchanged'],
    'cleanup_complete':r['cleanup_complete'],'returncode':r['returncode'],'memory_events_delta':r['memory_events_delta']})
 kinds={kind:sum(d['parameters']['kind']==kind for d in docs) for kind in sorted({d['parameters']['kind'] for d in docs})}
 operational=contract['operational_limits'];total_wall=sum(b['elapsed_seconds'] for b in batches)
 budgets={'new_selected_states':sum(d['new_eigenstates'] for d in docs),'counts_by_kind':kinds,'active_batch_wall_seconds':total_wall,
  'max_worker_rss_mib':max(d['result']['max_rss_kib']/1024 for d in docs),'spherical_requested_Ritz_roots':2*kinds.get('sphere',0)}
 budget_gates={'selected_states':budgets['new_selected_states']<=operational['new_eigenstates_total_max'],
  'prolate_pairs':kinds.get('prolate',0)<=operational['new_prolate_pairs_max'],'sphere_states':kinds.get('sphere',0)<=operational['new_spherical_eigenstates_max'],
  'operator_refinements':kinds.get('operator_refinement',0)<=operational['operator_refinement_tasks_max'],
  'overlap_evaluations':kinds.get('overlap',0)<=operational['overlap_edge_orders_max'],
  'parity_evaluations':kinds.get('parity',0)<=operational['parity_evaluations_max'],
  'total_wall':total_wall<=operational['total_active_science_wall_seconds'],
  'task_wall':all(d['result']['elapsed_seconds']<=operational['task_wall_seconds'] for d in docs)}
 execution_ok=all(b['returncode']==0 and not b['failed_tasks'] and b['source_unchanged'] and b['cleanup_complete'] and b['preflight_passed'] for b in batches)
 gates={'state_quartets':states['all_new_R_numerical_gates_pass'],'anchor':anchor['accepted'],'continuation':continuation['pass'],'parity':parity['pass'],'execution':execution_ok,'budgets':all(budget_gates.values())}
 stop='SCOPED_SMALL_R_SCALED_SEQUENCE_CONVERGED' if all(gates.values()) else 'SMALL_R_EXECUTION_BLOCKED' if not execution_ok else 'SMALL_R_SCALED_NUMERICS_UNRESOLVED'
 coefficient=contract['coefficient']['value'];sequence=[]
 inherited=json.loads((ROOT/'evidence/INHERITED_POINT_SCALARS.json').read_bytes())['profiles']['base']
 for radius in sorted(selected):
  value=selected_values.get(radius)
  lo=value['direct'][str(max(map(int,value['direct'])))]['L_O_bar'] if value else inherited['L_O_bar']
  scaled=lo/radius**3
  sequence.append({'R':radius,'L_O_bar':lo,'S':scaled,'S_minus_C':scaled-coefficient,'relative_difference_from_C':scaled/coefficient-1,'new_point':radius!=.25})
 result={'node':contract['node'],'stop':stop,'gates':gates,'contract_sha256':digest(ROOT/'CONTRACT.json'),
  'state_audit':states,'anchor_audit':anchor,'continuation_audit':continuation,'parity_audit':parity,'sequence':sequence,
  'budgets':budgets,'budget_gates':budget_gates,'batches':batches,'input_DATA_sha256':{d['path']:digest(ROOT/d['path']) for d in docs},
  'coefficient':coefficient,'asymptotic_remainder_bound_known':False,'new_physical_evaluations_by_analysis':0,'global_gates':contract['gates']}
 atomic_create(a.output,json_bytes(result));print(json.dumps({'stop':stop,'gates':gates,'budgets':budgets,'sequence':sequence,'anchor_failures':anchor['failures'],'anchor_unknown':anchor['unknown'],'continuation_failed':continuation['failed'],'parity_failed':parity.get('failed_case_indices')},indent=2))

if __name__=='__main__':main()
