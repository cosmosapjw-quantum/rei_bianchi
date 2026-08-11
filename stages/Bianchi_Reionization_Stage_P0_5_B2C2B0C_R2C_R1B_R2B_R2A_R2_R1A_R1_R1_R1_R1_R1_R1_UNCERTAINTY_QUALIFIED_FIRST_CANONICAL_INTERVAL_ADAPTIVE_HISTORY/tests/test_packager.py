import hashlib,json,tempfile,unittest
from pathlib import Path
from helpers import load
m=load('test_packager_module','analysis/package_local_results.py')
FAKE=Path(__file__).with_name('fake_attempt_worker.py')
class Tests(unittest.TestCase):
 def inventory(self,root):
  rows={}
  for path in sorted(Path(root).rglob('*')):
   relative=path.relative_to(root).as_posix()
   if path.is_symlink():rows[relative]=('symlink',path.readlink().as_posix())
   elif path.is_file():rows[relative]=('file',hashlib.sha256(path.read_bytes()).hexdigest())
   elif path.is_dir():rows[relative]=('directory',None)
  return rows
 def test_bundle_selection_includes_transition_journal_and_snapshots(self):
  with tempfile.TemporaryDirectory() as raw:
   run=Path(raw);(run/'data').mkdir();(run/'history/transitions').mkdir(parents=True);(run/'receipts').mkdir();(run/'checkpoints/snapshots/g-1').mkdir(parents=True)
   for relative in ('CONTROL.json','RUN_OWNER.json','RUN_METADATA.json','data/results.json'):Path(run,relative).write_text('{}\n')
   (run/'checkpoints/LATEST.json').write_text('{"latest_generation":null}\n');transition=run/'history/transitions/transition_00000000.json';transition.write_text('{}\n');snapshot=run/'checkpoints/snapshots/g-1/lane.state';snapshot.write_bytes(b'state')
   selected=m.select(run);self.assertIn(transition.resolve(),selected);self.assertIn(snapshot.resolve(),selected)
 def test_packager_shares_the_nonblocking_run_lock(self):
  with tempfile.TemporaryDirectory() as raw:
   root=Path(raw);run=root/'run';coordinator=m.supervisor.Coordinator(run_dir=run,worker_script=FAKE,worker_environment={'FAKE_WORKER_MODE':'PASS'},runtime_contract_value={'sha256':'d'*64},_test_mode=True)
   try:
    with self.assertRaisesRegex(RuntimeError,'active|lock'):m.package(run,root/'candidate.tar.gz')
    self.assertFalse((root/'candidate.tar.gz').exists())
   finally:coordinator.close()
 def test_source_run_and_existing_outputs_are_never_clobbered(self):
  with tempfile.TemporaryDirectory() as raw:
   root=Path(raw);run=root/'run';run.mkdir();control=run/'CONTROL.json';control.write_text('preserve')
   with self.assertRaisesRegex(ValueError,'outside'):m.package(run,control)
   self.assertEqual(control.read_text(),'preserve')
   output=root/'candidate.tar.gz';output.write_text('preserve')
   with self.assertRaisesRegex(FileExistsError,'exists'):m.package(run,output)
   self.assertEqual(output.read_text(),'preserve')
 def test_validate_only_packaging_never_repairs_or_deletes_source(self):
  for fault in ('missing-control','temporary-snapshot'):
   with self.subTest(fault=fault),tempfile.TemporaryDirectory() as raw:
    root=Path(raw);run=root/'run';coordinator=m.supervisor.Coordinator(run_dir=run,worker_script=FAKE,worker_environment={'FAKE_WORKER_MODE':'PASS'},runtime_contract_value={'sha256':'d'*64},_test_mode=True);coordinator.run(max_accepted=1)
    if fault=='missing-control':(run/'CONTROL.json').unlink()
    else:
     name='g-00000002-tick-000128';temporary=run/'checkpoints/snapshots'/f'.{name}.tmp-probe';temporary.mkdir();(temporary/'TEMPORARY_OWNER.json').write_text(json.dumps(coordinator._temporary_owner(name)))
    coordinator.close();before=self.inventory(run)
    with m.supervisor.RunLock(run) as held_lock:
     with self.assertRaises((ValueError,FileNotFoundError)):
      m.supervisor.Coordinator(run_dir=run,worker_script=FAKE,worker_environment={'FAKE_WORKER_MODE':'PASS'},resume=True,runtime_contract_value={'sha256':'d'*64},_test_mode=True,_repair=False,_held_run_lock=held_lock)
    self.assertEqual(self.inventory(run),before)
    self.assertFalse((root/'candidate.tar.gz').exists())
 def test_validate_only_preserves_a_prejournal_attempt(self):
  with tempfile.TemporaryDirectory() as raw:
   root=Path(raw);run=root/'run';coordinator=m.supervisor.Coordinator(run_dir=run,worker_script=FAKE,worker_environment={'FAKE_WORKER_MODE':'PASS'},runtime_contract_value={'sha256':'d'*64},_test_mode=True);original=coordinator._persist
   def crash(status,*,initial=False,action,evidence=None):
    if action=='ACCEPT':raise RuntimeError('simulated pre-journal crash')
    return original(status,initial=initial,action=action,evidence=evidence)
   coordinator._persist=crash
   with self.assertRaisesRegex(RuntimeError,'pre-journal'):coordinator.run(max_accepted=1)
   coordinator.close();before=self.inventory(run)
   with m.supervisor.RunLock(run) as held_lock:
    with self.assertRaisesRegex(ValueError,'repair'):
     m.supervisor.Coordinator(run_dir=run,worker_script=FAKE,worker_environment={'FAKE_WORKER_MODE':'PASS'},resume=True,runtime_contract_value={'sha256':'d'*64},_test_mode=True,_repair=False,_held_run_lock=held_lock)
   self.assertEqual(self.inventory(run),before)
if __name__=='__main__':unittest.main()
