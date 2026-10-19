"""Process-plumbing regressions only; no native solver/history is executed."""
import importlib.util,json,os,pathlib,shutil,subprocess,sys,tempfile,unittest
MODULE=pathlib.Path(__file__).resolve().parents[1]/'prepare_and_run.py'
spec=importlib.util.spec_from_file_location('portable_prepare',MODULE)
prepare=importlib.util.module_from_spec(spec);spec.loader.exec_module(prepare)
STUB='''import json,pathlib,sys,time
raw,mode,method,n=sys.argv[1:]
if mode=='slow':time.sleep(2)
failed=mode=='fail'
pathlib.Path(raw).write_text(json.dumps({'completed':not failed,'wall_s':0.01,'native_rhs_attempts_including_fd_replay':7,'kind':'PROCESS_TEST_STUB'}))
raise SystemExit(1 if failed else 0)
'''
class ProcessRunnerTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.temp.name);self.stub=self.root/'stub.py';self.stub.write_text(STUB)
 def tearDown(self):
  if os.environ.get('PREPARE_RUNNER_TEST_EVIDENCE'):
   target=pathlib.Path(os.environ['PREPARE_RUNNER_TEST_EVIDENCE'])/self._testMethodName
   target.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(self.root,target)
  self.temp.cleanup()
 def test_failure_exit_and_family_block_preserve_independent_success(self):
  evidence=self.root/'evidence'
  driver=self.root/'driver.py'
  driver.write_text(f"import importlib.util,pathlib,sys\nspec=importlib.util.spec_from_file_location('p',{str(MODULE)!r});p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)\nraise SystemExit(p.run_cases(pathlib.Path({str(evidence)!r}),[sys.executable,{str(self.stub)!r}],[('fail','radau','2'),('fail','radau','4'),('good','ssprk','8')]))\n")
  result=subprocess.run([sys.executable,driver],capture_output=True,text=True)
  self.assertEqual(result.returncode,1,result.stderr)
  receipt=json.loads((evidence/'MATRIX_RECEIPT.json').read_text())
  self.assertEqual([x['status'] for x in receipt['cases']],['FAILED_OR_TRUNCATED','NOT_RUN_FAMILY_BLOCKED','COMPLETED'])
  self.assertEqual(receipt['overall_exit_code'],1)
  self.assertEqual(receipt['cases'][0]['native_rhs'],7)
  self.assertTrue((evidence/'fail_radau_n2/raw.json').is_file())
  self.assertFalse((evidence/'fail_radau_n4').exists())
 def test_remaining_budget_caps_process_and_unrun_is_nonzero(self):
  evidence=self.root/'budget'
  code=prepare.run_cases(evidence,[sys.executable,self.stub],[('slow','radau','2'),('good','ssprk','8')],total_budget_s=0.05)
  self.assertEqual(code,1)
  receipt=json.loads((evidence/'MATRIX_RECEIPT.json').read_text())
  first=receipt['cases'][0]
  self.assertLessEqual(first['external_timeout_s'],0.05)
  self.assertGreaterEqual(first['charged_wall_s'],0.05)
  self.assertEqual(receipt['cases'][1]['status'],'NOT_RUN_TOTAL_BUDGET')
  self.assertTrue(json.loads((evidence/'slow_radau_n2/outcome.json').read_text())['truncated'])
  self.assertFalse((evidence/'good_ssprk_n8').exists())
 def test_success_returns_zero_and_archive_mapping_is_explicit(self):
  evidence=self.root/'success';source=self.root/'source';source.mkdir();(source/'one.txt').write_text('one')
  code=prepare.run_cases(evidence,[sys.executable,self.stub],[('good','radau','2')],sources=(source,),total_budget_s=10)
  self.assertEqual(code,0)
  inputs=json.loads((evidence/'good_radau_n2/inputs.json').read_text())
  self.assertEqual(inputs['source_archive_member_paths'],{'source_0000/one.txt':str(source/'one.txt')})
  self.assertEqual(json.loads((evidence/'MATRIX_RECEIPT.json').read_text())['overall_status'],'COMPLETED')
 def test_multicall_symlink_preserves_cargo_and_rustc_dispatch(self):
  dispatcher=self.root/'multicall_dispatcher'
  dispatcher.write_text('#!'+sys.executable+'\nimport pathlib,sys\nname=pathlib.Path(sys.argv[0]).name\nif name not in ("cargo","rustc"):raise SystemExit(77)\nprint("PROCESS_TEST_STUB dispatch="+name+" args="+" ".join(sys.argv[1:]))\n')
  dispatcher.chmod(0o755)
  cargo=self.root/'cargo';rustc=self.root/'rustc'
  cargo.symlink_to(dispatcher);rustc.symlink_to(dispatcher)
  invocation=prepare.invocation_path(cargo)
  self.assertEqual(invocation,cargo.absolute())
  self.assertNotEqual(invocation,dispatcher.resolve())
  env=os.environ.copy();env['RUSTC']=str(rustc)
  evidence=self.root/'toolchain'
  prepare.record_toolchain(evidence,invocation,env)
  metadata=json.loads((evidence/'HOST_TOOLCHAIN_METADATA.json').read_text())
  self.assertIn('dispatch=cargo',metadata['cargo_vv'])
  self.assertIn('dispatch=rustc',metadata['rustc_vv'])
  self.assertEqual(metadata['cargo_path'],str(cargo.absolute()))
  self.assertEqual(metadata['rustc_path'],str(rustc.absolute()))
  self.assertEqual(metadata['cargo_sha256'],prepare.sha(dispatcher))
  self.assertEqual(metadata['rustc_sha256'],prepare.sha(dispatcher))
if __name__=='__main__':unittest.main()
