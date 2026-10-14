"""Evidence-only terminal and persisted successor regression; no processes."""
import importlib.util,json,pathlib,copy,tempfile,sys
sys.dont_write_bytecode=True
HERE=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('exit_epoch',HERE/'post_cap_epoch_recovery.py'); E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
PLUS=E.load(HERE/'post_plus_epoch_dispatch.py','exit_plus_fixture')
original,cases=E.validate(require_review=False)
source=cases['SHEAR_MINUS']['output'];source_raw=source.parent/'SHEAR_MINUS_raw'
# Inspect the actual preserved evidence once; no output edits or process scan.
before={str(p):E.digest(p) for p in [source/'RETURN.txt',source/'checkpoint.txt',source_raw/'execution_receipt.json',source_raw/'stderr.log']}
actual_minus=E.terminal(cases['SHEAR_MINUS'],original,{})
assert actual_minus['exit_code']==1 and actual_minus['actual_launcher_status']=='FAILED_EXIT_1' and actual_minus['typed_stop']=='ACCEPTED_STEP_CAP'
assert before=={p:E.digest(p) for p in before}
print('Actual MINUS1 exact terminal accepted; original FAILED_EXIT_1/RETURN/checkpoint/stderr unchanged')
def refused(call):
 try:call()
 except (RuntimeError,ValueError,KeyError,IndexError):return
 raise AssertionError('unsafe classification accepted')
with tempfile.TemporaryDirectory(dir=pathlib.Path(__file__).parent,prefix='fixture_') as directory:
 root=pathlib.Path(directory);records=[]
 for name in ['ZERO','SHEAR_PLUS','SHEAR_MINUS','SHEAR_HALF_PLUS','SHEAR_HALF_MINUS']:
  out=root/name;out.mkdir();raw=root/(name+'_raw');raw.mkdir();case=dict(cases[name],output=out)
  for file in ['RETURN.txt','checkpoint.txt','source_identity.txt']:(out/file).write_bytes((source/file).read_bytes())
  (out/'config.cfg').write_bytes(case['config'].read_bytes());(out/'case_id.txt').write_text(name);(out/'ledgers.csv').write_text('kind,value,status\nenergy,0,PASS\n')
  code=101 if name in ['ZERO','SHEAR_PLUS'] else 1
  start=json.loads((source_raw/'execution_start.json').read_text());start.update(case=name,config_sha256=E.digest(case['config']),observed_process_pid=999999,argv=[str(case['binary']),'--config',str(case['config']),'--output',str(out),'--case',name]);(raw/'execution_start.json').write_text(json.dumps(start));(raw/'time.log').write_text('Exit status: '+str(code)+'\n');(raw/'stdout.log').write_text('');(raw/'stderr.log').write_text('InvalidInput("AXBI_RUNTIME_CAP")\n')
  launcher=dict(case=name,exit_code=code,status='FAILED_EXIT_'+str(code),driver_terminal_record=(out/'RETURN.txt').read_text());(raw/'execution_receipt.json').write_text(json.dumps(launcher))
  record=E.terminal(case,original,{});assert record['exit_code']==code and E.original_cap_exit(record);records.append(record)
  if name!='SHEAR_MINUS':continue
  def mutate(path,content):
   old=path.read_bytes();path.write_text(content)
   try:refused(lambda:E.terminal(case,original,{}))
   finally:path.write_bytes(old)
  for invalid in [99,124,137,101,-9]:mutate(raw/'time.log','Exit status: '+str(invalid)+'\n')
  mutate(out/'RETURN.txt',(out/'RETURN.txt').read_text().replace('AXBI_RUNTIME_CAP','AXBI_SCIENCE_FAILURE'))
  mutate(raw/'stderr.log','InvalidInput("DIFFERENT_FIRST_ERROR")\n')
  mutate(out/'checkpoint.txt',(out/'checkpoint.txt').read_text().replace('200000 600054','199999 600054'))
  mutate(out/'config.cfg','wrong config');mutate(out/'source_identity.txt','wrong epoch')
  badstart=dict(start,binary_sha256='0'*64);mutate(raw/'execution_start.json',json.dumps(badstart))
  refused(lambda:E.terminal(case,original,{999999:[{'pid':999999}]}))
  mutate(out/'ledgers.csv','kind,value,status\nenergy,1,FAIL\n')
 # Persist a classified signed1 receipt through ACTUAL PLUS fresh_handoff.
 pe=PLUS.EPOCH;pe.RECEIPT=root/'recovered.json';pe.validate=lambda:({},{});pe.RECOVER.process_groups=lambda:{}
 receipt=dict(status='COMPLETED_EPOCH_RECOVERY',remaining_signed_queue=[],original_actual_starts=5,continuation_actual_starts=1,total_full_starts=6,prior_pilot_starts=3,prior_and_current_starts=9,original_results=records,zero_result=dict(status='SUCCESS',exit_code=0),source_mapping=E.MAPPING,preserved_stale_receipt_sha256=E.digest(E.OLD_RECEIPT))
 pe.reconcile=lambda *args,**kwargs:receipt
 pe.RECEIPT.write_text(json.dumps(receipt));carried,_=PLUS.fresh_handoff();assert carried['total_full_starts']==6 and carried['all_history_starts']==9
 receipt['original_results'][2]['exit_code']=101;pe.RECEIPT.write_text(json.dumps(receipt));refused(lambda:PLUS.fresh_handoff())
print('EXIT_CLASSIFICATION_EVIDENCE_FIXTURE_PASS; actual predicate and persisted PLUS; signed1 only, historical ZERO/PLUS101 retained; unknown/timeout/signal/signed101/result/first-error/checkpoint/config/source/start/live/ledger rejected; full6/history9; no process starts')
