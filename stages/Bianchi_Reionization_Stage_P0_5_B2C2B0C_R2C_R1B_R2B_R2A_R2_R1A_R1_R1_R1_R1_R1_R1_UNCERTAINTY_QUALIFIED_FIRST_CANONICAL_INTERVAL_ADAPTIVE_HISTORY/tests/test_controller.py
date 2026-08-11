import json,tempfile,unittest
from pathlib import Path
from unittest import mock
from helpers import load
m=load('test_controller_module','analysis/run_adaptive_history.py');FAKE=Path(__file__).with_name('fake_attempt_worker.py')
class Tests(unittest.TestCase):
 def c(self,path,mode='PASS',resume=False,timeout=5):return m.Coordinator(run_dir=Path(path),workers=3,worker_timeout=timeout,worker_script=FAKE,worker_environment={'FAKE_WORKER_MODE':mode,'OPENBLAS_NUM_THREADS':'99'},resume=resume,runtime_contract_value={'sha256':'d'*64},_test_mode=True)
 def test_nonproduction_worker_requires_explicit_test_mode(self):
  with tempfile.TemporaryDirectory() as r:
   with self.assertRaisesRegex(ValueError,'production|test'):
    m.Coordinator(run_dir=Path(r),worker_script=FAKE,runtime_contract_value={'sha256':'d'*64})
 def test_production_run_requires_matching_preflight(self):
  runtime={'files':{'analysis/attempt_worker.py':m.sha_file(m.DEFAULT_WORKER)},'sha256':'a'*64}
  with tempfile.TemporaryDirectory() as r,mock.patch.object(m.runtime_contract,'build',return_value=runtime):
   with self.assertRaisesRegex(ValueError,'preflight'):
    m.Coordinator(run_dir=Path(r))
 def test_run_directory_has_one_exclusive_coordinator(self):
  with tempfile.TemporaryDirectory() as r:
   first=self.c(r)
   try:
    self.assertTrue(Path(r,'.RUN.lock').is_file())
    with self.assertRaisesRegex(RuntimeError,'active|lock'):
     self.c(r,resume=True)
   finally:
    if hasattr(first,'close'):first.close()
   self.assertTrue(Path(r,'.RUN.lock').is_file())
 def test_replaced_run_lock_cannot_split_the_owned_lock_domain(self):
  with tempfile.TemporaryDirectory() as r:
   first=self.c(r);replacement=None;lock=Path(r,'.RUN.lock');lock.unlink();lock.write_text('replacement')
   try:
    with self.assertRaisesRegex((RuntimeError,ValueError),'lock|ownership'):
     replacement=self.c(r,resume=True)
   finally:
    if replacement is not None:replacement.close()
    first.close()
 def test_common_commit_and_bisection(self):
  with tempfile.TemporaryDirectory() as r:
   s=self.c(r).run(max_accepted=1);self.assertEqual((s['status'],s['accepted_tick']),('PAUSED_LIMIT',64));self.assertEqual(s['schema'],1);self.assertTrue(Path(r,'checkpoints/LATEST.json').is_file())
  with tempfile.TemporaryDirectory() as r:
   s=self.c(r,'REJECT_BASE_ZERO').run(max_accepted=1);self.assertEqual((s['accepted_tick'],s['rejected_attempts']),(32,1))
 def test_event_crash_preserve_parent(self):
  for mode,status in [('EVENT','BLOCKED_TABLE_EVENT'),('CRASH','BLOCKED_TRANSPORT')]:
   with tempfile.TemporaryDirectory() as r:
    s=self.c(r,mode).run(max_accepted=1);self.assertEqual(s['status'],status);self.assertEqual(s['accepted_endpoints'],0);latest=json.loads(Path(r,'checkpoints/LATEST.json').read_text());self.assertIsNone(latest['latest_generation'])
 def test_resume_determinism_and_explicit(self):
  with tempfile.TemporaryDirectory() as one,tempfile.TemporaryDirectory() as split:
   whole=self.c(one).run(max_accepted=2);self.c(split).run(max_accepted=1)
   with self.assertRaisesRegex(FileExistsError,'resume'):self.c(split)
   resumed=self.c(split,resume=True).run(max_accepted=1);self.assertEqual(resumed['latest_record_sha256'],whole['latest_record_sha256']);self.assertEqual(resumed['final_state_sha256'],whole['final_state_sha256'])
 def test_resume_rejects_cursor_tamper(self):
  with tempfile.TemporaryDirectory() as r:
   self.c(r).run(max_accepted=1);control=Path(r,'CONTROL.json');row=json.loads(control.read_text());row['cursor']['current']={'depth':0,'left_tick':128,'right_tick':192};control.write_text(json.dumps(row))
   with self.assertRaises((ValueError,RuntimeError)):self.c(r,resume=True)
 def test_resume_replays_rejection_cursor_journal(self):
  with tempfile.TemporaryDirectory() as r:
   coordinator=self.c(r,'REJECT_BASE_ZERO');coordinator.run(max_accepted=1);coordinator.close()
   control=Path(r,'CONTROL.json');latest=Path(r,'checkpoints/LATEST.json');c=json.loads(control.read_text())
   c['cursor']['current']={'depth':2,'left_tick':32,'right_tick':48};c['cursor']['pending']=[{'depth':2,'left_tick':48,'right_tick':64}]
   control.write_text(json.dumps(c));l=json.loads(latest.read_text());l['control_state']=c;latest.write_text(json.dumps(l))
   with self.assertRaisesRegex((ValueError,RuntimeError),'journal|transition|cursor'):
    self.c(r,'REJECT_BASE_ZERO',resume=True)
 def test_resume_requires_journal_bound_attempt_receipts(self):
  with tempfile.TemporaryDirectory() as r:
   coordinator=self.c(r);coordinator.run(max_accepted=1);coordinator.close()
   next(Path(r,'receipts').glob('attempt_*.json')).unlink()
   with self.assertRaisesRegex((ValueError,FileNotFoundError),'receipt|evidence|journal'):
    self.c(r,resume=True)
 def test_resume_discards_one_authenticated_prejournal_attempt(self):
  with tempfile.TemporaryDirectory() as interrupted,tempfile.TemporaryDirectory() as reference:
   expected=self.c(reference).run(max_accepted=1);coordinator=self.c(interrupted);original=coordinator._persist
   def crash(status,*,initial=False,action,evidence=None):
    if action=='ACCEPT':raise RuntimeError('simulated pre-journal crash')
    return original(status,initial=initial,action=action,evidence=evidence)
   coordinator._persist=crash
   with self.assertRaisesRegex(RuntimeError,'pre-journal'):coordinator.run(max_accepted=1)
   coordinator.close();self.assertTrue(next(Path(interrupted,'receipts').glob('attempt_*.json')).is_file());self.assertTrue(Path(interrupted,'history/accepted_00000001.json').is_file())
   resumed=self.c(interrupted,resume=True);self.assertEqual((resumed.cursor.accepted_index,resumed.attempts,resumed.transition),(0,0,0));observed=resumed.run(max_accepted=1);resumed.close()
   self.assertEqual(observed['latest_record_sha256'],expected['latest_record_sha256']);self.assertEqual(observed['final_state_sha256'],expected['final_state_sha256'])
 def test_preflight_nested_failure_is_not_hidden_by_top_level_pass(self):
  names=('git_head_readable','tracked_worktree_clean','integration_commit_is_ancestor','predecessor_sha256sums','predecessor_payloads_verify','current_stage_payloads_verify','predecessor_bundle_sha256','predecessor_bundle_size','predecessor_bundle_crc','runtime_dependencies','jax_absent_import_guard_required','memory_for_three_workers','runtime_contract_closed')
  with tempfile.TemporaryDirectory() as r:
   coordinator=m.Coordinator.__new__(m.Coordinator);coordinator.run_dir=Path(r);coordinator.test_mode=False;coordinator.runtime_sha='d'*64
   checks=[{'name':name,'passed':name!='current_stage_payloads_verify','observed':0,'expected':0} for name in names];Path(r,'preflight.json').write_text(json.dumps({'all_passed':True,'calculation_started':False,'checks':checks,'classification':'PREFLIGHT_ONLY_NO_SCIENCE_RESULT','environment':{'machine':'x86_64','platform':'test','python':'3.12.13'},'runtime_contract_sha256':'d'*64,'stage_id':m.policy.STAGE_ID}))
   with self.assertRaisesRegex(ValueError,'preflight|check'):
    coordinator._validate_preflight()
 def test_history_parent_state_chain_is_replayed(self):
  with tempfile.TemporaryDirectory() as r:
   coordinator=self.c(r);coordinator.run(max_accepted=2)
   path=Path(r,'history/accepted_00000002.json');record=json.loads(path.read_text());task=m._task_load(record['interval']);bad='f'*64
   for lane in m.policy.LANE_ORDER:
    envelope=record['lanes'][lane];envelope['parent_state_sha256']=bad;envelope['job_key']=m.policy.job_key(lane=lane,task=task,accepted_index=2,parent_state_sha256=bad,input_lock_sha256=coordinator.input_sha,predecessor_kernel_sha256=coordinator.kernel_sha,runtime_contract_sha256=coordinator.runtime_sha)
   path.write_bytes(m.canonical(record)+b'\n')
   with self.assertRaisesRegex(ValueError,'parent|state chain'):
    coordinator._validate_history_chain(2)
   coordinator.close()
 def test_transition_receipt_jobs_bind_the_accepted_record(self):
  with tempfile.TemporaryDirectory() as r:
   coordinator=self.c(r);coordinator.run(max_accepted=1)
   initial=m.read_json(Path(r,'history/transitions/transition_00000000.json'));accepted=m.read_json(Path(r,'history/transitions/transition_00000001.json'));evidence=dict(accepted['evidence']);receipt_path=Path(r,evidence['attempt_receipt_path']);receipt=m.read_json(receipt_path);receipt['jobs'][m.policy.LANE_ORDER[0]]='f'*64;receipt_path.write_bytes(m.canonical(receipt)+b'\n');evidence['attempt_receipt_sha256']=m.sha_file(receipt_path)
   with self.assertRaisesRegex(ValueError,'job|receipt|record'):
    coordinator._validate_transition_evidence(initial['control_state'],accepted['control_state'],'ACCEPT',evidence)
   coordinator.close()
 def test_resume_requires_canonical_run_metadata(self):
  with tempfile.TemporaryDirectory() as r:
   coordinator=self.c(r);coordinator.run(max_accepted=1);coordinator.close();metadata=Path(r,'RUN_METADATA.json');row=json.loads(metadata.read_text());row['workers']=999;metadata.write_text(json.dumps(row))
   with self.assertRaisesRegex(ValueError,'metadata'):
    self.c(r,resume=True)
 def test_resume_rejects_impossible_control_latest_order(self):
  with tempfile.TemporaryDirectory() as r:
   coordinator=self.c(r);coordinator.run(max_accepted=1);coordinator.close()
   prior_path=Path(r,'history/transitions/transition_00000001.json');prior=json.loads(prior_path.read_text())['control_state'];prior['latest_transition_sha256']=m.sha_file(prior_path)
   latest=m.Coordinator.__new__(m.Coordinator)._latest_for_control(prior);Path(r,'checkpoints/LATEST.json').write_text(json.dumps(latest))
   with self.assertRaisesRegex(ValueError,'order|pair|LATEST|CONTROL'):
    self.c(r,resume=True)
 def test_resume_removes_only_owned_transition_temporary(self):
  with tempfile.TemporaryDirectory() as r:
   coordinator=self.c(r);coordinator.run(max_accepted=1);coordinator.close()
   temporary=Path(r,'history/transitions/.transition_00000003.json.tmp-owned');temporary.write_text('partial')
   resumed=self.c(r,resume=True);self.assertFalse(temporary.exists());resumed.close()
 def test_resume_completes_owned_initialization_crash(self):
  for remove_metadata in (False,True):
   with tempfile.TemporaryDirectory() as r:
    coordinator=self.c(r);coordinator.close();Path(r,'CONTROL.json').unlink();Path(r,'checkpoints/LATEST.json').unlink();Path(r,'history/transitions/transition_00000000.json').unlink()
    if remove_metadata:Path(r,'RUN_METADATA.json').unlink()
    resumed=self.c(r,resume=True);self.assertEqual(resumed.status,'READY');self.assertTrue(Path(r,'RUN_METADATA.json').is_file());resumed.close()
  with tempfile.TemporaryDirectory() as r:
   self.c(r).run(max_accepted=1);control=Path(r,'CONTROL.json');latest=Path(r,'checkpoints/LATEST.json');c=json.loads(control.read_text());c['cursor']['current']=None;control.write_text(json.dumps(c));l=json.loads(latest.read_text());l['control_state']=c;latest.write_text(json.dumps(l))
   with self.assertRaises((ValueError,RuntimeError)):self.c(r,resume=True)
 def test_foreign_run_directory_is_refused(self):
  with tempfile.TemporaryDirectory() as r:
   Path(r,'foreign.txt').write_text('do not touch')
   with self.assertRaisesRegex((FileExistsError,ValueError),'foreign|empty|owned'):self.c(r)
   self.assertEqual(Path(r,'foreign.txt').read_text(),'do not touch')
 def test_timeout_partial_output_is_durable_and_caps_are_reserved(self):
  with tempfile.TemporaryDirectory() as r:
   self.assertEqual(self.c(r,'TIMEOUT',timeout=.1).run(max_accepted=1)['status'],'BLOCKED_TRANSPORT');receipt=next(Path(r,'receipts').glob('*.json'));self.assertIn('partial timeout output',receipt.read_text())
   coordinator=self.c(r,resume=True);self.assertEqual(coordinator._env()['OPENBLAS_NUM_THREADS'],'1')
 def test_malformed_state_and_envelope_never_commit(self):
  for mode in ('MALFORMED_STATE','MALFORMED_ENVELOPE'):
   with tempfile.TemporaryDirectory() as r:
    summary=self.c(r,mode).run(max_accepted=1);self.assertEqual(summary['status'],'BLOCKED_PROTOCOL');self.assertEqual(summary['accepted_endpoints'],0)
 def test_history_foreign_generation_and_runtime_changes_fail_resume(self):
  with tempfile.TemporaryDirectory() as r:
   self.c(r).run(max_accepted=2);history=Path(r,'history/accepted_00000001.json');history.write_text(history.read_text()+' ')
   with self.assertRaises((ValueError,RuntimeError)):self.c(r,resume=True)
  with tempfile.TemporaryDirectory() as r:
   self.c(r).run(max_accepted=1);Path(r,'checkpoints/generations/g-foreign').mkdir()
   with self.assertRaises((ValueError,FileNotFoundError)):self.c(r,resume=True)
  with tempfile.TemporaryDirectory() as r:
   self.c(r).run(max_accepted=1)
   with self.assertRaisesRegex(ValueError,'runtime|ownership'):m.Coordinator(run_dir=Path(r),workers=1,worker_script=FAKE,resume=True,runtime_contract_value={'sha256':'e'*64},_test_mode=True)
 def test_cleanup_is_limited_to_direct_child(self):
  with tempfile.TemporaryDirectory() as raw:
   root=Path(raw)/'generations';root.mkdir();child=root/'g-1';child.mkdir();m._safe_rmtree(child,root);self.assertFalse(child.exists())
   with self.assertRaisesRegex(ValueError,'unsafe cleanup'):m._safe_rmtree(root,root)
   outside=Path(raw)/'outside';outside.mkdir()
   with self.assertRaisesRegex(ValueError,'unsafe cleanup'):m._safe_rmtree(outside,root)
if __name__=='__main__':unittest.main()
