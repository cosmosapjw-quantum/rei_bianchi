import csv,hashlib,json,math,datetime,collections
from pathlib import Path
root=Path(__file__).resolve().parent.parent;c=json.loads((root/'CONTRACT.json').read_text());controller=json.loads((root/'raw/CONTROLLER_TERMINAL.json').read_text());calls=json.loads((root/'raw/EXECUTIONS.json').read_text());compact=root/'compact';compact.mkdir(exist_ok=False);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def fields(p):return dict(line.split('=',1) for line in p.read_text().splitlines() if '=' in line)
summary={};fullmanifest=[]
for rec in calls:
 case=rec['case'];out=root/'results'/case;terminal=fields(out/'RETURN.txt') if (out/'RETURN.txt').exists() else None;tables={};historyfirst=[];historytail=collections.deque(maxlen=3);header=None
 for name in ['history.csv','abundances.csv','spectra.csv','ledgers.csv','feedback.csv']:
  path=out/name
  if not path.exists():tables[name]={'rows':None,'status':'NOT_RECORDED'};continue
  count=0;statuses={};maxima={};maxnormalized={};failures=[]
  with path.open(newline='') as f:
   reader=csv.DictReader(f)
   if name=='history.csv':header=reader.fieldnames
   for row in reader:
    count+=1
    if name=='history.csv':
     if len(historyfirst)<3:historyfirst.append(row)
     historytail.append(row)
    if name=='ledgers.csv':
     status=row['status'];statuses[status]=statuses.get(status,0)+1;v=float(row['residual'])
     if not math.isfinite(v):failures.append({'row':count,'kind':'NONFINITE_RECORDED_LEDGER'})
     if status=='PASS':
      tol=float(row['tolerance']);maxima[row['ledger_name']]=max(maxima.get(row['ledger_name'],0),abs(v));maxnormalized[row['ledger_name']]=max(maxnormalized.get(row['ledger_name'],0),abs(v)/tol if tol else 0 if v==0 else None)
      if abs(v)>tol:failures.append({'row':count,'kind':'PASS_OUTSIDE_OWN_NATIVE_TOLERANCE'})
     elif status!='VALUE':failures.append({'row':count,'kind':'NATIVE_LEDGER_'+status})
  tables[name]={'rows':count,'bytes':path.stat().st_size,'sha256':sha(path)}
  if name=='ledgers.csv':tables[name].update(status_counts=statuses,max_abs_saved_PASS_residuals=maxima,max_saved_residual_over_own_tolerance=maxnormalized,failures=failures)
 h=tables['history.csv']['rows'];countchecks={'history_equals_accepted_plus_initial':h==int(terminal['accepted'])+1 if terminal and h is not None else None,'abundances_equals_six_per_history':tables['abundances.csv']['rows']==6*h if h is not None else None,'ledgers_equals31_per_history':tables['ledgers.csv']['rows']==31*h if h is not None else None}
 if header:
  samples=historyfirst+[x for x in historytail if x not in historyfirst]
  with (compact/(case+'_history_head_tail.csv')).open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=header);w.writeheader();w.writerows(samples)
 last=historytail[-1] if historytail else None;binding={}
 if terminal and terminal.get('last_checkpoint') and Path(terminal['last_checkpoint']).exists():
  cp=Path(terminal['last_checkpoint']);text=cp.read_text();head,body=text.split('\nAXBI_CHECKPOINT_V4\n',1);prefix=head.splitlines();bl=('AXBI_CHECKPOINT_V4\n'+body).splitlines();state=list(map(float,bl[1].split()));counter=list(map(int,bl[2].split()));binding={'path':str(cp),'sha256':sha(cp),'bytes':cp.stat().st_size,'compiled_source':prefix[4],'producer_case_binding':prefix[1],'mode_schema':prefix[2],'provider_epoch':prefix[3],'config_debug_sha256':prefix[5],'run_epoch_binding':prefix[6],'run_binding_sha256':prefix[7],'body_hash_size_valid':prefix[9]==hashlib.sha256(('AXBI_CHECKPOINT_V4\n'+body).encode()).hexdigest() and int(prefix[10])==len(('AXBI_CHECKPOINT_V4\n'+body).encode()),'a':state[0],'proper_elapsed_time_s':state[1],'b':state[2],'accepted':counter[0],'attempts':counter[1],'RHS':counter[4],'comparisons':counter[5],'six_array_lengths':[len(line.split()) for line in bl[4:10]],'midpoint_or_final':'native terminal checkpoint; includes lastvalid physicalstate and allchargedcounters'}
  countchecks['checkpoint_matches_terminal_counters']=str(counter[0])==terminal['accepted'] and str(counter[1])==terminal['attempts'] and str(counter[4])==terminal['rhs_evaluations'];countchecks['checkpoint_matches_last_history_a_time']=state[0]==float(last['a']) and state[1]==float(last['time_s']) if last else None
 for p in out.rglob('*'):
  if p.is_file():fullmanifest.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
 status='NATIVE_COMPLETE_PENDING_REVIEW' if rec['exit_code']==0 and terminal and terminal['status']=='COMPLETE_REPRESENTED_INTERVAL' else 'PARTIAL_STOP_NO_COMPLETION_CLAIM'
 summary[case]={'status':status,'native_terminal':terminal,'execution':rec,'tables':tables,'count_consistency':countchecks,'coverage':{'requested_z_start':20,'requested_z_end':19.8,'actual_first_history':historyfirst[0] if historyfirst else None,'actual_last_history':last,'complete':status=='NATIVE_COMPLETE_PENDING_REVIEW'},'terminal_checkpoint_receipt':binding,'native_mode_metadata':(out/'transport_variant.txt').read_text() if (out/'transport_variant.txt').exists() else None,'runtime_compiled_source_sha256':sha(out/'source_identity.txt') if (out/'source_identity.txt').exists() else None,'feedback':'prescribed-background perturbative diagnostic only, no feedback admission'}
 if terminal:(compact/(case+'_RETURN.txt')).write_text((out/'RETURN.txt').read_text())
 write(compact/(case+'_RESULT_SUMMARY.json'),summary[case])
for item in c['case_order']:
 if item['case'] not in summary:summary[item['case']]={'status':'NOT_RUN_FIRST_CASE_FAILURE_OR_CAP','exit_code':None,'terminal':None,'reason':controller.get('reason'),'no_retry':True}
write(compact/'NATIVE_RESULT_SUMMARIES.json',summary);write(root/'FULL_RAW_MANIFEST.json',{'files':fullmanifest,'preservation':'all native CSV/checkpoints retained locally, backup by root; raw not selected forGit'})
status='BOTH_NATIVE_SHORT_HISTORIES_COMPLETE_REVIEW_PENDING' if all(v['status']=='NATIVE_COMPLETE_PENDING_REVIEW' for v in summary.values()) else 'BOUNDED_SHORT_HISTORY_PARTIAL_STOP_REVIEW_PENDING'
r={'schema':'rei.codex.return-contract/1','task_id':c['task_id'],'status':status,'written_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'execution_identity':{'requested_model':'gpt-6.1-sol/high','observed_model':'NOT_INDEPENDENTLY_OBSERVED','executor':'full005_actual_render','environment':'LOCAL native one worker, no64core utilization claim'},'source_identities':{'compiled_source_expected':c['implementation_compiled_source_sha256'],'runtime_observed':{k:v.get('runtime_compiled_source_sha256') for k,v in summary.items()},'binary_sha256':c['binary_sha256'],'HEAD_before_launch':[x['HEAD_read_immediately_before_fork'] for x in calls]},'config_identities':{'contract_sha256':sha(root/'CONTRACT.json'),'case_configs':[{'case':x['case'],'path':x['config_path'],'sha256':x['config_sha256']} for x in c['case_order']],'selected_inputs':c['scenario']},'commands':calls,'results':summary,'controller_terminal':controller,'budgets':{'actual_native_runs':len(calls),'run_cap':2,'short_history_wall_seconds':sum(x['wall_seconds'] for x in calls),'short_history_wall_cap':1200,'prior_source009_build_test_invocations':3,'prior_source009_build_test_wall_seconds':67.90825945080724,'combined_source009_wall_seconds':67.90825945080724+sum(x['wall_seconds'] for x in calls),'new_builds':0,'new_tests':0,'retries':0,'resumes':0,'all005_006_007_008_costs':'unchanged historicalrecords/epochs'},'outputs':{'full_raw_local':'results/** preserved locally, source-bound per FULL_RAW_MANIFEST.json; coordinator backs up outsideGit','compact_public':'compact/**,configs/**,actualexecutionreceipts,contract,report,rawmanifest only'},'claim':{'scientific_admission':'NOT_ISSUED','complete_history_claim':status=='BOTH_NATIVE_SHORT_HISTORIES_COMPLETE_REVIEW_PENDING','source008_mode_sensitivity':'preserved ~12.4percentGamma/~4.69percentphotonN diagnostic caveat, no equivalence claim','time_angular_fullhistory_Bianchi_admission':'HOLD','IC':'T8.098baseline differsfull005REC, conditional exploratory route','no_additional_compute_or_plot':'resultreview first'},'next_ready':[{'node':'FRESH_SOURCE009_SHORT_RESULT_REVIEW','action':'read actual native terminal/coverage/counters/ledger maxima/checkpoint bindings and stopclassification; no solver rerun/plots until separate approved packet'}],'git_mutations':0}
for name in ['RETURN_CONTRACT.json','IMPLEMENTATION_RECEIPT.json']:write(root/name,r)
lines=['# Source009 bounded short-history outcome','',status,'','| Case | Outcome | accepted | starts | RHS | actual final z | wall s |','|---|---|---:|---:|---:|---:|---:|']
for case,item in summary.items():
 t=item.get('native_terminal') or {};last=item.get('coverage',{}).get('actual_last_history') or {};lines.append('| '+case+' | '+item['status']+' | '+t.get('accepted','null')+' | '+t.get('attempts','null')+' | '+t.get('rhs_evaluations','null')+' | '+str(last.get('zbar','null'))+' | '+str(item.get('execution',{}).get('wall_seconds','null'))+' |')
lines+=['','Native CSV/checkpoint raw outputs remain local and are bound by FULL_RAW_MANIFEST.json. The compact summaries record row counts, residuals against their own native saved tolerances, source/mode/clock/sixarray checkpoint bindings and actual coverage. A capped/failed result remains partial; second case is not launched after first failure. No retry, resume, extra test/build or plot ran.','','Scientific admission is NOT_ISSUED. Source008 mode sensitivity, source007 time-convergence HOLD, conditional IC difference and prescribed-background feedback limitations remain. Fresh independent result review precedes further compute or presentation.'];(root/'REPORT.md').write_text('\n'.join(lines)+'\n')
selected=[p for p in root.rglob('*') if p.is_file() and 'results' not in p.relative_to(root).parts and p.name not in ['FILE_MANIFEST.json','PUBLIC_SELECTION.json']];write(root/'PUBLIC_SELECTION.json',{'paths':[str(p) for p in selected],'exclude_native_raw':'results/** allpreserved locally; coordinatorbackupoutsideGit'});write(root/'FILE_MANIFEST.json',{'files':[{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in selected]});print(json.dumps({'status':status,'summary':{k:{'status':v['status'],'accepted':v.get('native_terminal',{}).get('accepted'),'actual_z':v.get('coverage',{}).get('actual_last_history',{}).get('zbar')} for k,v in summary.items()},'public_files':len(selected)}))
