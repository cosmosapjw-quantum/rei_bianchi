"""Evaluate preregistered integration gates; never change parent evidence."""
import argparse,json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'code'))
from mpi_batch import atomic_create,json_bytes
from overlap_integral import refinement_audit
FKEYS=('T_A','T_B','L_O_bar','L_B_bar')
OKEYS=('left_domain_overlap','right_domain_overlap','normalized_overlap','self_norm_left','self_norm_right')
def delta(a,b,keys):return max(abs(a[k]-b[k]) for k in keys)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();c=json.loads((ROOT/'CONTRACT.json').read_text());criteria=c['criteria'];docs=[];inputs={}
 for batch in ('MAIN_MPI','MAIN_REMAINDER_MPI','FALLBACK_MPI','REFERENCE_FALLBACK_MPI'):
  d=ROOT/'evidence'/batch
  if not d.exists():continue
  summary_path=d/('RECOVERY_ACCEPTED_TASKS.json' if batch=='MAIN_MPI' and (d/'RECOVERY_ACCEPTED_TASKS.json').exists() else 'BATCH_SUMMARY.json')
  summary=json.loads(summary_path.read_text())
  if summary['status'] not in ('ALL_WORKER_RESULTS_PASS','PARTIAL_EXECUTION_RECOVERED_PASS'):raise RuntimeError('EXECUTION_BATCH_HAS_FAILURES')
  for task in summary['tasks']:
   folder=d/task['task_id'];r=json.loads((folder/'RESULT.json').read_text());p=folder/r['evidence_file'];raw=p.read_bytes()
   if len(raw)!=r['evidence_bytes'] or hashlib.sha256(raw).hexdigest()!=r['evidence_sha256']:raise RuntimeError('DATA_ARTIFACT_IDENTITY_MISMATCH')
   inputs[str(p.relative_to(ROOT))]=r['evidence_sha256'];doc=json.loads(raw);doc['path']=str(p.relative_to(ROOT));docs.append(doc)
 def seq(kind,states,method,sector=0):
  result=sorted([d for d in docs if d['parameters']['kind']==kind and d['parameters']['states']==states and d['parameters']['method']==method and d['parameters']['sector']==sector],key=lambda d:d['parameters']['order'])
  if len({d['parameters']['order'] for d in result})!=len(result):raise ValueError('duplicate order evidence')
  return result
 force=[];need=[]
 for name in c['force']['targets']+[c['force']['control']]:
  ds=seq('force',[name],'balanced');v=[d['value'] for d in ds];last=v[-3:]
  if len(last)<3:raise ValueError('missing force refinement sequence')
  inc=[delta(a,b,FKEYS) for a,b in zip(last,last[1:])];direct=max(max(x['direct_force_O_abs'],x['direct_force_B_abs']) for x in last)
  passed=max(inc)<=criteria['force_quadrature_abs'] and direct<=criteria['direct_force_abs']
  force.append({'state':name,'orders':[d['parameters']['order'] for d in ds],'increments_abs':inc,'max_terminal_direct_force_abs':direct,'pass':passed,'selected':v[-1],'data_paths':[d['path'] for d in ds]})
  if not passed and ds[-1]['parameters']['order']<56:need.append({'kind':'force','states':[name],'orders':[40,56],'method':'balanced','sector':0})
 overlap=[]
 for lo,hi,m in c['overlap']['failed_edges']+c['overlap']['controls']:
  states=[f'R{lo}_base',f'R{hi}_base'];ds=seq('overlap',states,'resolved',m);v=[d['value'] for d in ds];audit=refinement_audit(v,criteria['overlap_increment_abs'],criteria['overlap_magnitude_min'])
  overlap.append({'edge':[lo,hi,m],'orders':[d['parameters']['order'] for d in ds],'audit':audit,'selected':v[-1],'data_paths':[d['path'] for d in ds]})
  if not audit['transport_pass'] and ds[-1]['parameters']['order']<64:need.append({'kind':'overlap','states':states,'orders':[48,64],'method':'resolved','sector':m})
 ds=seq('force',['R16_h'],'original');v=[d['value'] for d in ds];refinc=delta(v[-2],v[-1],FKEYS);new=next(x for x in force if x['state']=='R16_h')['selected'];agreement=delta(new,v[-1],FKEYS)
 ref_force={'orders':[d['parameters']['order'] for d in ds],'increment_abs':refinc,'new_method_difference_abs':agreement,'pass':max(refinc,agreement)<=criteria['independent_force_abs'],'selected':v[-1]}
 if not ref_force['pass'] and ds[-1]['parameters']['order']<80:need.append({'kind':'force','states':['R16_h'],'orders':[80],'method':'original','sector':0})
 ds=seq('overlap',['R15_base','R16_base'],'original');v=[d['value'] for d in ds];old=json.loads((ROOT/'provenance/C2A_CONTINUATION_AUDIT.json').read_text());oldedge=next(x for x in old['rows'] if (x['R_left'],x['R_right'],x['m'])==(15,16,0));prev=v[-2] if len(v)>1 else oldedge['orders']['48'];new=next(x for x in overlap if x['edge']==[15,16,0])['selected'];inc=delta(prev,v[-1],OKEYS);agreement=delta(new,v[-1],OKEYS)
 ref_overlap={'orders':([48] if len(v)==1 else [])+[d['parameters']['order'] for d in ds],'increment_abs':inc,'new_method_difference_abs':agreement,'max_final_consistency':max(v[-1]['directional_difference_abs'],v[-1]['max_self_norm_error_abs']),'selected':v[-1]};ref_overlap['pass']=max(inc,agreement,ref_overlap['max_final_consistency'])<=criteria['overlap_independent_abs']
 if not ref_overlap['pass'] and ds[-1]['parameters']['order']<80:need.append({'kind':'overlap','states':['R15_base','R16_base'],'orders':[80],'method':'original','sector':0})
 parity=[]
 for d in docs:
  p=d['parameters']
  if p['method'].endswith('_python'):
   base=seq(p['kind'],p['states'],p['method'].replace('_python',''),p['sector']);native=next(x for x in base if x['parameters']['order']==p['order']);difference=delta(d['value'],native['value'],FKEYS if p['kind']=='force' else OKEYS);parity.append({'task_id':d['task_id'],'max_abs':difference,'pass':difference<=criteria['native_python_abs']})
 passed=all(x['pass'] for x in force) and all(x['audit']['transport_pass'] for x in overlap) and ref_force['pass'] and ref_overlap['pass'] and len(parity)==4 and all(x['pass'] for x in parity)
 result={'contract_sha256':hashlib.sha256((ROOT/'CONTRACT.json').read_bytes()).hexdigest(),'stop':'SCOPED_FROZEN_STATE_INTEGRATION_CLOSED' if passed else 'FROZEN_STATE_INTEGRATION_UNRESOLVED','all_registered_integration_gates_pass':passed,'force':force,'overlap':overlap,'independent_force':ref_force,'independent_overlap':ref_overlap,'parity':parity,'registered_fallback_needed':need,'input_data_sha256':inputs,'new_eigensolves':0,'full_C2_closed':False,'continuum_certificate':False,'gates':c['gates']}
 atomic_create(args.output,json_bytes(result));print(json.dumps({'stop':result['stop'],'force_failed':[x['state'] for x in force if not x['pass']],'overlap_failed':[x['edge'] for x in overlap if not x['audit']['transport_pass']],'reference_force_pass':ref_force['pass'],'reference_overlap_pass':ref_overlap['pass'],'fallback_tasks':need}),flush=True)
if __name__=='__main__':main()
