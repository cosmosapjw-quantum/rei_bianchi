"""Read-only actual W1 campaign review. Never launches a scientific worker."""
from pathlib import Path
from fractions import Fraction
import hashlib,importlib.util,json,sys
HERE=Path(__file__).resolve().parent
NEW=HERE.parent
ROOT=NEW/'runtime/W1_CAMPAIGN'
PREPARED_SHA='e85c2fa451d00a32f7d129d55e82f45ffee71342af0fd39d1b9ac81b4d84a4a9'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def canonical(o):return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()
def sealcheck(o,key):assert o[key]==hashlib.sha256(canonical({k:v for k,v in o.items() if k!=key})).hexdigest()
def main():
 gate=read(HERE/'PRE_EXECUTION_REVIEW.json')
 for rel,expected in gate['source_sha256'].items():assert sha(NEW/rel)==expected,rel
 spec=importlib.util.spec_from_file_location('independent_actual_w1_runner',NEW/'tile_runner/runner.py');r=importlib.util.module_from_spec(spec);sys.modules[spec.name]=r;spec.loader.exec_module(r)
 ctx,m,plans=r.load_prepared(ROOT,PREPARED_SHA)
 accepted,rejected,attempted=r.load_state(ROOT,ctx,m,plans)
 quarantine=NEW/'runtime/W1_CLAIMS_QUARANTINE_20261002_v1'
 qr=read(quarantine/'RECEIPT.json');sealcheck(qr,'receipt_sha256')
 qp=read(quarantine/'PLAN.json');sealcheck(qp,'plan_sha256')
 qgate=read(HERE/'CLAIM_RECONCILIATION_REVIEW.json')
 assert qr['plan_sha256']==qp['plan_sha256']==qgate['reviewed_plan_sha256']
 assert qr['reconciler_source_sha256']==qgate['reconciler_source_sha256']==sha(NEW/'tile_runner/reconcile_claims.py')
 assert qr['archived_claim_count']==6 and qr['immutable_campaign_snapshot_unchanged'] is True
 assert qr['numerical_files_modified'] is False and qr['actual_native_executions']==0
 assert qr['root_cause']=='UNDETERMINED' and qr['root_cause_closed'] is False
 for entry in qr['claims']:
  destination=Path(entry['destination']);source=Path(entry['source'])
  assert sha(destination)==entry['sha256'] and destination.read_bytes()==entry['data'].encode()
  assert destination.stat().st_mtime_ns==entry['mtime_ns'] and not source.exists()
 for rel,identity in qp['immutable_campaign_snapshot'].items():
  assert sha(ROOT/rel)==identity['sha256'] and (ROOT/rel).stat().st_size==identity['size']
 reconciliation={'status':'PASS_EXACT_SIX_TERMINAL_CLAIMS_ARCHIVED_AND_STRICT_RESUME_READBACK','archive_receipt_file_sha256':sha(quarantine/'RECEIPT.json'),'archive_receipt_sha256':qr['receipt_sha256'],'independent_gate_sha256':sha(HERE/'CLAIM_RECONCILIATION_REVIEW.json'),'claims_preserved':6,'campaign_nonclaim_snapshot_unchanged':True,'root_cause':'UNDETERMINED','root_cause_closed':False,'new_HH_executions':0}
 assert not (ROOT/'RUN.claim').exists(),'campaign still has claim'
 sessions=sorted((ROOT/'sessions').glob('*/RESULT.json'));assert sessions,'terminal session result required'
 terminal=read(sessions[-1]);sealcheck(terminal,'result_sha256')
 assert terminal['prepared_sha256']==PREPARED_SHA and terminal['accepted_tile_ids']==sorted(accepted)
 assert terminal['total_native_dispatch_count']==len(attempted)
 assert len(attempted)<=15 and terminal['total_native_cap_charged']==len(attempted)*200000
 evidence={'PRE_EXECUTION_REVIEW.json':sha(HERE/'PRE_EXECUTION_REVIEW.json'),'PREPARED.json':sha(ROOT/'PREPARED.json'),'session_result':sha(sessions[-1])}
 rows=[];attested=0;total_evals=0;total_calls=0;accepted_new=0
 for i in attempted:
  raw=ROOT/'raw'/('%02d.json'%i);ret=read(ROOT/'attempts'/('%02d'%i)/'RETURN.json');sealcheck(ret,'return_sha256')
  row={'tile_id':i,'accepted':i in accepted,'dispatch_counted':True,'native_execution_attested':False,'return_status':ret['status']}
  if raw.is_file():
   q=read(raw);sealcheck(q,'result_sha256');assert ret['raw_receipt_sha256']==sha(raw)
   w=q['wrapper'];task=plans[i]['tasks'][0]
   for k,v in {'build_manifest_sha256':r.BUILD_SHA,'binary_sha256':ctx['manifest']['binary_sha256'],'build_source':ctx['manifest']['source'],'archive_sha256':r.INPUT_SHA,'input_record_sha256':ctx['manifest']['input_record_sha256'],'native_limits':r.LIMITS,'physical_window':plans[i]['window'],'endpoint_plan_module_sha256':sha(ctx['d'].PLAN_MODULE)}.items():assert w[k]==v,(i,k)
   command=[str((r.BUILD/'primitive_worker').resolve()),'0',*[plans[i]['window'][k] for k in ('l_t','T_t','l_u','T_u')],*[str(r.LIMITS[k]) for k in ('precision_bits','radius_exp','relative_goal','max_evaluations','max_integration_calls','wall_seconds','queued_panels','degree_limit')],task['task_sha256'],plans[i]['plan_sha256']]
   assert w['command']==command
   r.host_module().validate_receipt(w['process_host'],command=command,limits=r.LIMITS,output_path=raw)
   stdout=Path(str(raw)+'.stdout').read_bytes();stderr=Path(str(raw)+'.stderr').read_bytes()
   assert hashlib.sha256(stdout).hexdigest()==w['native_stdout_sha256'] and hashlib.sha256(stderr).hexdigest()==w['native_stderr_sha256']
   if q.get('schema')=='WU088_LOG2_NATIVE_INTERIOR_REJECTION_V1':assert q['native_stdout']==stdout.decode('utf-8','replace') and q['native_stderr']==stderr.decode('utf-8','replace')
   native=json.loads(stdout) if stdout else None
   if isinstance(native,dict) and native.get('schema')=='WU088_LOG2_RANGE_INTERIOR_RESULT_V1':
    expected={'index':0,'task_sha256':task['task_sha256'],'plan_sha256':plans[i]['plan_sha256'],'archive_sha256':r.INPUT_SHA,'input_record_sha256':ctx['manifest']['input_record_sha256'],'build_source_sha256':r.SOURCE_SHA,'precision_bits':128,'accepted_component_radius_exp':-52,'coordinate_map':'LOG2_EXACT_POWER_ENDPOINTS_V1','endpoint_included':False,'normalization_applied':False,'full_domain_integral':False,'scientific_admission':False,'production_admission':False}
    for key,value in expected.items():assert type(native[key]) is type(value) and native[key]==value,(i,key)
    assert w['process_host']['native_execution_evidence']=='SOURCE_BOUND_NATIVE_STDOUT' and w['native_execution_observed'] is True
    assert 0<=native['dispatched_evaluations']<=200000 and 0<=native['integration_calls']<=1024
    attested+=1;total_evals+=native['dispatched_evaluations'];total_calls+=native['integration_calls']
    row.update(native_execution_attested=True,native_status=native['status'],evaluations=native['dispatched_evaluations'],integration_calls=native['integration_calls'],native_elapsed_wall_ns=w['elapsed_wall_ns'],native_returncode=w['returncode'])
    if i in accepted:
     assert native['accepted'] is True and native['status']=='RADIUS_MET' and w['returncode']==0
     assert canonical({k:v for k,v in q.items() if k not in ('wrapper','result_sha256')})==canonical(native)
     independent={}
     for part in ('real','imag'):
      v=native['rectangle'][part];lo=int(v['lower_mantissa'])*Fraction(2)**int(v['exponent2']);hi=int(v['upper_mantissa'])*Fraction(2)**int(v['exponent2']);rad=(hi-lo)/2
      assert 0<=rad<=Fraction(2)**-52
      assert accepted[i]['rectangle'][part]=={'lower':str(lo),'upper':str(hi)}
      independent[part]={'lower':str(lo),'upper':str(hi),'radius':str(rad)}
     row['independent_exact_intervals']=independent;accepted_new+=1
    else:assert native['accepted'] is False
   row['raw_receipt_sha256']=sha(raw);evidence['raw/%02d.json'%i]=sha(raw)
  rows.append(row)
 collected=ROOT/'COLLECTED.json';independent_sum=None
 if len(accepted)==16:
  assert collected.is_file();c=read(collected);sealcheck(c,'result_sha256');independent_sum={}
  for part in ('real','imag'):
   lo=sum(Fraction(accepted[i]['rectangle'][part]['lower']) for i in range(16));hi=sum(Fraction(accepted[i]['rectangle'][part]['upper']) for i in range(16));rad=(hi-lo)/2
   assert rad<=Fraction(2)**-48 and c['rectangle'][part]=={'lower':str(lo),'upper':str(hi)} and c['component_radius'][part]==str(rad)
   independent_sum[part]={'lower':str(lo),'upper':str(hi),'radius':str(rad)}
  assert terminal['status']=='COMPLETE_COMPACT_INTERIOR_RADIUS_MET'
 else:assert not collected.exists(),'partial campaign must not emit collection'
 result={'schema':'WU088_W1_ACTUAL_CAMPAIGN_INDEPENDENT_REVIEW_V1','status':'PASS_ACTUAL_RECEIPT_INTEGRITY_AND_EXACT_SCOPE_REVIEW','campaign_status':terminal['status'],'prepared_sha256':PREPARED_SHA,'evidence_sha256':evidence,'reused_accepted_tile_ids':[0],'new_dispatch_count':len(attempted),'new_native_invocations_attested':attested,'new_native_invocations_unattested':len(attempted)-attested,'new_accepted_count':accepted_new,'new_rejected_count':len(rejected),'accepted_tile_ids':sorted(accepted),'rejected_tile_ids':rejected,'new_total_evaluations':total_evals,'new_total_integration_calls':total_calls,'new_rows':rows,'independent_exact_global_sum':independent_sum,'full_W1_complete':len(accepted)==16,'old_tile0_not_rerun':0 not in attempted,'reviewer_new_HH_executions':0,'operational_claim_reconciliation':reconciliation,'raw_success_stdout_verified_for_new_receipts':True,'source_bound_interval_execution_not_independent_HH_oracle':True,'endpoint_included':False,'normalization_applied':False,'full_domain_integral':False,'scientific_admission':False,'production_admission':False,'NCP64_benchmark':False,'MPI_execution':False,'review_script_sha256':sha(__file__)}
 out=HERE/'ACTUAL_CAMPAIGN_REVIEW.json'
 with out.open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps({k:result[k] for k in ('status','campaign_status','new_dispatch_count','new_native_invocations_attested','new_accepted_count','new_rejected_count','full_W1_complete')},sort_keys=True))
if __name__=='__main__':main()
