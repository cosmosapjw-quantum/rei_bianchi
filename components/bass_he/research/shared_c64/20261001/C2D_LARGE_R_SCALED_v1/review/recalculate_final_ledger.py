"""Independent artifact/ledger review; stdlib only, no scientific execution."""
from pathlib import Path
from collections import Counter
import hashlib,json,math,os,zipfile,datetime
R=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}
def verify(m):
 p=R/m['path'];assert bind(p)==m;return p
def canonical(x):return (json.dumps(x,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def h(x):return hashlib.sha256(canonical(x)).hexdigest()
a=load(R/'evidence/FINAL_AUDIT.json');ledger=load(R/'evidence/RECOVERY_LEDGER.json');plan=load(R/'review/RECOVERY_PLAN.json');c=load(R/'CONTRACT.json');ix=load(R/'evidence/FOLLOWUP_MPI/PARTIAL_BATCH_INDEX.json')
ind=load(R/'review/C2D_FOLLOWUP_INDEPENDENT_RECALCULATION.json');main=load(R/'review/C2D_MAIN_INDEPENDENT_RECALCULATION.json');anchor=load(R/'review/ANCHOR_INITIAL_DIAGNOSTIC.json');classified=load(R/'review/TIMEOUT_TASK_CLASSIFICATION.json')
assert ind['pass'] and main['pass'] and a['recovery_audit']==ledger and a['contract_sha256']==sha(R/'CONTRACT.json')
for meta in classified['bindings'].values():
 if not Path(meta['path']).is_absolute():verify(meta)
assert ix==plan['partial_index'] and not (R/'evidence/FOLLOWUP_MPI/BATCH_SUMMARY.json').exists()
assert Counter(t['classification'] for t in ix['tasks'])=={'COMPLETED_VALIDATED':124,'FINAL_EXECUTION_FAILED_REQUIRES_CLASSIFICATION':4,'INTERRUPTED_WITHOUT_RESULT':3,'NOT_STARTED':19}
for row in ix['tasks']:
 for meta in row['artifacts'].values():verify(meta)
orig=load(R/'evidence/FOLLOWUP_MPI/MANIFEST_INPUT.json');rec=load(R/'evidence/RECOVERY_MPI/MANIFEST_INPUT.json');origt={t['task_id']:t for t in orig['tasks']};rect={t['task_id']:t for t in rec['tasks']};uncompleted=[row for row in ix['tasks'] if row['classification']!='COMPLETED_VALIDATED']
expected_mapping=[{'original_task_id':row['task_id'],'recovery_task_id':'rec_'+row['task_id'],'original_classification':row['classification'],'parameters_sha256':h(origt[row['task_id']]['parameters'])} for row in uncompleted]
assert plan['task_mapping']==expected_mapping and len(rect)==26
assert rec['limits']==orig['limits']
assert rec['tasks']==[{'task_id':'rec_'+row['task_id'],'parameters':origt[row['task_id']]['parameters']} for row in uncompleted]
assert not set(rect)&{'rec_'+row['task_id'] for row in ix['tasks'] if row['classification']=='COMPLETED_VALIDATED'}
assert ledger['completed_task_replays']==plan['validated_completed_replays']==0 and ledger['new_eigenstates_requested']==plan['new_eigenstates_requested']==0
verify(ledger['plan']);verify(ledger['recovery_launch']);verify(plan['timeout_kill_classification'])
launches=[];actual=Counter();upper=Counter();completed=Counter();started=[];semantic=set();all_results=[]
for lp in sorted((R/'evidence').glob('*MPI_LAUNCH.json')):
 launch=load(lp);batch=lp.with_name(lp.name.removesuffix('_LAUNCH.json'));launches.append({'binding':bind(lp),'elapsed_seconds':launch['elapsed_seconds']})
 assert launch['source_unchanged'] and launch['cleanup_complete'] and all(v==0 for v in launch['memory_events_delta'].values())
 if not batch.exists():
  assert not launch['preflight_passed'] and launch['returncode']!=0;continue
 run=load(batch/'RUN_IDENTITY.json');manifest=load(batch/'MANIFEST_INPUT.json')
 assert launch['source_identity_before']==run['code'] and h(run['code']['files'])==run['code']['sha256']
 assert launch['manifest_sha256']==run['manifest_sha256']==sha(batch/'MANIFEST_INPUT.json')
 assert launch['preflight_passed']
 if batch.name=='FOLLOWUP_MPI':assert launch['returncode']==124 and launch['timed_out'] and launch['wall_cap_seconds']==1800
 else:assert launch['returncode']==0 and not launch['timed_out']
 for t in manifest['tasks']:
  kind=t['parameters']['kind'];upper[kind]+=1;folder=batch/t['task_id']
  if folder.exists():actual[kind]+=1;started.append({'batch':str(batch.relative_to(R)),'kind':kind,'task_id':t['task_id']})
  ep=folder/'TASK_EXECUTION.json'
  if not ep.exists():continue
  e=load(ep)
  if e['status']!='WORKER_RESULT_PASS':
   assert batch.name=='FOLLOWUP_MPI' and t['task_id'] in {x['task_id'] for x in classified['tasks']};continue
  result=load(folder/'RESULT.json');d=load(folder/'DATA.json')
  assert e['returncode']==0 and e['task_id']==t['task_id'] and e['code_sha256']==run['code']['sha256']
  assert result['status']=='PASS' and result['parameters']==d['parameters']==t['parameters']
  assert e['worker_result_sha256']==sha(folder/'RESULT.json') and result['evidence_sha256']==sha(folder/'DATA.json')
  assert e['task_sha256']==sha(folder/'TASK_INPUT.json')==result['input_sha256'] and load(folder/'TASK_INPUT.json')==t
  for name,meta in e['artifacts'].items():assert meta=={'bytes':(folder/name).stat().st_size,'sha256':sha(folder/name)}
  assert result['elapsed_seconds']<=c['operational_limits']['task_wall_seconds'] and e['wall_seconds']<=c['operational_limits']['task_wall_seconds']
  assert a['input_DATA_sha256'][str((folder/'DATA.json').relative_to(R))]==sha(folder/'DATA.json')
  key=h(t['parameters']);assert key not in semantic;semantic.add(key);completed[kind]+=1;all_results.append(result)
assert ledger['final_attempt_inventory']['launches']==launches
assert ledger['final_attempt_inventory']['started_tasks']==started
assert actual==ledger['final_attempt_inventory']['actual_started_by_kind']==a['budgets']['attempted_counts_by_kind']
assert upper==ledger['final_attempt_inventory']['manifest_upper_bound_by_kind']==a['budgets']['manifest_task_count_upper_bound_by_kind']
assert completed==a['budgets']['counts_by_kind'] and len(semantic)==184 and sum(actual.values())==191
wall=sum(x['elapsed_seconds'] for x in launches)
assert wall==ledger['final_attempt_inventory']['charged_wall_seconds']==a['budgets']['charged_all_launch_wall_seconds']
prior=[x for x in launches if x['binding']['path']!='evidence/RECOVERY_MPI_LAUNCH.json'];priorwall=sum(x['elapsed_seconds'] for x in prior)
assert prior==plan['prior_attempt_inventory']['launches'] and priorwall==plan['wall_budget']['charged_prior_seconds']
assert plan['wall_budget']['original_total_seconds']==c['operational_limits']['total_active_science_wall_seconds']==3600
assert plan['wall_budget']['recovery_wall_cap_seconds']==min(1800,math.floor(3600-priorwall-plan['wall_budget']['cleanup_margin_seconds']))==1470
rec_launch=load(R/'evidence/RECOVERY_MPI_LAUNCH.json');assert rec_launch['wall_cap_seconds']==1470 and rec_launch['elapsed_seconds']<1470 and wall<3600
assert actual['overlap']==151<=c['operational_limits']['overlap_edge_orders_max'] and actual['parity']==4<=c['operational_limits']['parity_evaluations_max']
assert sum(x['new_eigenstates'] for x in all_results)==a['budgets']['new_selected_states']==64
assert max(x['max_rss_kib']/1024 for x in all_results)==a['budgets']['max_worker_rss_mib']
oldrun=load(R/'evidence/FOLLOWUP_MPI/RUN_IDENTITY.json');newrun=load(R/'evidence/RECOVERY_MPI/RUN_IDENTITY.json')
assert newrun['code']==plan['source_identity_for_recovery'] and oldrun['selected_backend']==newrun['selected_backend']
changed=[k for k,v in oldrun['code']['files'].items() if newrun['code']['files'].get(k)!=v]
assert sorted(changed)==sorted(plan['allowed_analysis_changes'])
assert sorted(set(newrun['code']['files'])-set(oldrun['code']['files']))==sorted(plan['new_helper_files'])
for key in ['code/task_worker.py','code/run_bounded.py']:assert oldrun['code']['files'][key]==newrun['code']['files'][key]==sha(R/key)
with zipfile.ZipFile(R/'provenance/RECOVERY_CODE_SNAPSHOT.zip') as z:
 for name,digest in newrun['code']['files'].items():
  matches=[n for n in z.namelist() if n==name or n.endswith('/'+name)];assert len(matches)==1 and hashlib.sha256(z.read(matches[0])).hexdigest()==digest
assert newrun['rank_count']==4 and newrun['worker_count']==3 and rec_launch['binding']=='none'
aff=load(R/'review/RECOVERY_BOUND_AFFINITY.json');assert aff['run_identity_sha256']==sha(R/'evidence/RECOVERY_MPI/RUN_IDENTITY.json')
for w in aff['workers']:
 p=R/'evidence/RECOVERY_MPI'/w['task_id']/'OWNED_PROCESS.json';owned=load(p);assert sha(p)==w['registry_sha256'];leader=owned['leader']
 assert w['procfs_pid']==leader['procfs_pid'] and w['namespace_pid']==leader['pid'] and w['start_time_ticks']==leader['start_time_ticks']
 assert w['cpus_allowed_list']=='0-8' and w['threads']==1 and owned['batch_owner_token']==rec_launch['batch_owner_token']
assert len(aff['workers'])==2
# Compare independently recalculated overlap and parity values to final author audit.
aedges={(x['R_left'],x['R_right'],x['m']):x for x in a['continuation_audit']['rows']}
for x in ind['edge_rows']:
 y=aedges[(*x['edge'],x['m'])];assert y['selected']['normalized_overlap']==x['signed_normalized_overlap']
 assert y['quadrature_increments_abs']==x['increments'] and y['directional_difference_max_abs']==x['max_direction'] and y['self_norm_error_max_abs']==x['max_selfnorm']
for key,rows in ind['phase_chains'].items():assert rows==[{k:x[k] for k in ['R','phase']} for x in a['continuation_audit']['phase_chains'][key]]
# Bind the independent anchor expert's accepted record and recompute printed comparisons.
assert anchor['contract_file_sha256']==sha(R/'CONTRACT.json') and anchor['audit']==a['anchor_audit'] and anchor['status']=='PASS' and a['anchor_audit']['accepted']
for item in anchor['input_bindings']:
 folder=R/item['folder'];assert sha(folder/'DATA.json')==item['data_sha256'] and sha(folder/'RESULT.json')==item['result_sha256']
 if 'state_sha256' in item:assert sha(folder/'STATE.npz')==item['state_sha256'] and (folder/'STATE.npz').stat().st_size==item['state_bytes']
s72=load(R/'evidence/FOLLOWUP_MPI/observe_l72/DATA.json')['value'];s96=load(R/'evidence/FOLLOWUP_MPI/observe_l96/DATA.json')['value'];p32=load(R/'evidence/MAIN3_MPI/R32_base/DATA.json')['value']['direct']['32'];anchor_print={}
for key,raw,factor in [('Q_O','L_O_bar',1/32),('Q_B','L_B_bar',1024)]:
 agreement=abs(s96['direct']['30'][raw]-p32[raw])*factor
 increment=abs(s96['direct']['30'][raw]-s72['direct']['30'][raw])*factor
 gates={g['name']:g for x in a['anchor_audit']['comparisons'] if x['label']=='l96' for g in x['gates']}
 assert agreement==gates[key+'_agreement']['value'] and agreement<=c['scaled_criteria'][key+'_spherical_agreement_abs']
 assert increment<=c['scaled_criteria'][key+'_spherical_increment_abs']
 anchor_print[key]={'agreement':agreement,'angular_increment':increment}
expected_metrics={}
for q in ['Q_O','Q_B']:
 expected_metrics[q]={'spatial':max(v[k] for block in main['quartet_metrics'].values() for v in block.values() for k in ['direct_'+q,'force_'+q]),'direct_force':max(v['direct_force_'+q] for v in main['pair_metrics'].values()),'origin':max(v['origin_'+q] for v in main['pair_metrics'].values()),'momentum':max(v['momentum_'+q] for v in main['pair_metrics'].values())}
for row in a['sequence']:
 assert row['Q_O']==row['L_O_bar']/row['R'] and row['Q_B']==-row['L_B_bar']*row['R']**2
 for q in ['Q_O','Q_B']:assert row[q+'_relative_difference_from_C']==row[q]/c['coefficients'][q]['value']-1
 if row['new_point']:
  for q in ['Q_O','Q_B']:assert row[q]==main['pair_metrics'][f"R{row['R']}_base"][q]
assert a['stop']=='SCOPED_LARGE_R_SCALED_SEQUENCE_CONVERGED' and all(a['gates'].values()) and all(a['budget_gates'].values())
assert a['global_gates']==c['gates'] and c['gates']['full_C2_closed'] is False and c['gates']['scientific_PROMOTE']=='HOLD' and c['gates']['Eq55']=='NOT_RUN'
report={'schema':'bass-c2d-independent-final-ledger-review-v1','pass':True,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Independent stdlib calculations over immutable artifacts; no author audit imports and no physics/tests rerun.','stop':a['stop'],'bindings':{n:bind(R/n) for n in ['CONTRACT.json','evidence/FINAL_AUDIT.json','evidence/RECOVERY_LEDGER.json','review/RECOVERY_PLAN.json','review/TIMEOUT_TASK_CLASSIFICATION.json','review/TIMEOUT_KILL_CLASSIFICATION.json','review/C2D_MAIN_INDEPENDENT_RECALCULATION.json','review/C2D_FOLLOWUP_INDEPENDENT_RECALCULATION.json','review/ANCHOR_INITIAL_DIAGNOSTIC.json','review/RECOVERY_BOUND_AFFINITY.json','provenance/RECOVERY_CODE_SNAPSHOT.zip']},'unique_completed_tasks':184,'actual_started_attempts':191,'original_failed_records_preserved':4,'original_additional_interrupted_attempts_preserved':3,'completed_task_replays':0,'recovery_tasks':26,'recovery_new_eigenstates':0,'counts_by_kind':dict(completed),'actual_started_by_kind':dict(actual),'manifest_upper_bound_by_kind':dict(upper),'charged_wall_seconds':wall,'registered_wall_seconds':3600,'recovery_wall_seconds':rec_launch['elapsed_seconds'],'recovery_wall_cap_seconds':1470,'worker_native_unchanged':True,'changed_prior_source_files':changed,'owned_worker_affinity_observations':aff,'affinity_scope_note':'Two observed owned workers retained 0-8 masks and one thread; observer could not directly read namespace inodes, as retained in evidence. No speedup/NCP64 claim.','anchor_accepted':True,'anchor_independent_evidence':'review/ANCHOR_INITIAL_DIAGNOSTIC.json','anchor_comparison_independent_recalculation':anchor_print,'report_expected_metrics':expected_metrics,'report_expected_minimum_overlap':ind['minimum_absolute_normalized_overlap'],'report_expected_max_worker_rss_mib':a['budgets']['max_worker_rss_mib'],'report_expected_sequence':a['sequence'],'global_gates':c['gates'],'numerical_scope':'Empirical fixed-m large-R endpoint convergence and local overlaps only; no continuum, spectral cluster, all-collision-domain or asymptotic-radius certificate.','new_physical_evaluations':0,'concrete_blockers':[]}
out=R/'review/C2D_FINAL_INDEPENDENT_REVIEW.json'
with out.open('x') as f:json.dump(report,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'output':str(out),'sha256':sha(out),'pass':True,'wall':wall,'counts':dict(actual),'anchor':anchor_print,'metrics':expected_metrics},indent=2))
