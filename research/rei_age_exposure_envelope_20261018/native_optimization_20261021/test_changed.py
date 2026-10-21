import json,sys,tempfile,unittest,subprocess,os
import verify
from pathlib import Path
from fractions import Fraction as F
import campaign as c
import analyze as a

class ChangedRiskTests(unittest.TestCase):
 def test_c9_timeout_preserves_output_and_debits_both_budgets(self):
  for build in [False,True]:
   with tempfile.TemporaryDirectory() as t:
    out=Path(t);cmd=[sys.executable,'-c','import sys,time;print("prefix",flush=True);print("errorprefix",file=sys.stderr,flush=True);time.sleep(2)']
    with self.assertRaises(RuntimeError):verify.execute(cmd,out,'fake_timeout',.1,build=build)
    records=json.loads((out/('BUILD_COMMANDS.json' if build else 'COMMANDS.json')).read_text());r=records[-1]
    self.assertTrue(r['timed_out']);self.assertEqual(r['exit_code'],124);self.assertGreaterEqual(r['wall_seconds'],.1)
    self.assertIn('prefix',Path(r['stdout']).read_text());self.assertIn('errorprefix',Path(r['stderr']).read_text())
 def test_c9_live_orphan_refusal_then_confirmed_exit_debit(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);data=root/'old/data';data.mkdir(parents=True);(data/'prefix').write_text('preserve')
   sidecar=root/'CHILD_IDENTITY.json'
   child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(5)'],start_new_session=True,preexec_fn=lambda:c.save(sidecar,c._proc_identity(Path('/proc/self'))))
   row=dict(case='time8',attempt='time8_attempt001',status='RUNNING',cap_seconds=1.,data=str(data),child_identity=json.loads(sidecar.read_text()),identity={})
   c.save(root/'CAMPAIGN.json',dict(attempts=[row],elapsed_used=0.))
   try:
    with self.assertRaisesRegex(RuntimeError,'LIVE_OWN_ORPHAN'):c.run_scheduler(Path('/unused'),root,{},dict(jobs=1,workers=1,case_memory_bytes=c.GIB),case_wall=1,total_wall=3,elapsed_cap=5,command_factory=lambda n,d:(_ for _ in ()).throw(AssertionError('NO_NEW_LAUNCH')))
    self.assertIsNone(child.poll())
   finally:child.terminate();child.wait()
   r=c.run_scheduler(Path('/unused'),root,{},dict(jobs=1,workers=1,case_memory_bytes=c.GIB),case_wall=1,total_wall=3,elapsed_cap=5,command_factory=lambda n,d:[sys.executable,'-c','print("ok")'])
   self.assertEqual(r['attempts'][0]['status'],'INCOMPLETE');self.assertGreaterEqual(r['elapsed_used'],1.);self.assertEqual((data/'prefix').read_text(),'preserve')
 def test_c9_analysis_rejects_wrong_identity_hash_and_reference_cache(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);data=root/'data';data.mkdir();(data/'payload').write_text('original')
   row=dict(case='time8',attempt='time8_attempt001',status='COMPLETE',identity=dict(v=1),data=str(data),outputs=c.hashes(data))
   self.assertEqual(a.eligibility(row,dict(v=1)),'ELIGIBLE');self.assertEqual(a.eligibility(row,dict(v=2)),'CURRENT_IDENTITY_MISMATCH')
   (data/'payload').write_text('changed');self.assertEqual(a.eligibility(row,dict(v=1)),'OUTPUT_HASH_MISMATCH')
   result=a.postprocess(root,dict(attempts=[row],current_identity=dict(v=1)))
   self.assertEqual(result['pairs']['time8_vs_time16']['status'],'MISSING_PAIR')
   c.save(root/'RAW_INPUTS.json',dict(age32_data=str(data),archive_sha256='8c4579811faefbf3738c2dcd3c5105300a9aedec0b08c930bee032e094ef0cde',outputs={'data/payload':'wrong'}))
   with self.assertRaisesRegex(ValueError,'CACHED_REFERENCE'):c.restore_reference(Path('/unused'),root)
 def test_c9_launch_exception_preserves_failed_attempts(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);r=c.run_scheduler(Path('/unused'),root,{},dict(jobs=1,workers=1,case_memory_bytes=c.GIB),case_wall=1,total_wall=3,elapsed_cap=4,command_factory=lambda n,d:['/definitely_missing_v10_fake_executable'])
   self.assertEqual(len(r['attempts']),3)
   self.assertTrue(all(x['status']=='FAILED' and 'LAUNCH_EXCEPTION' in x['failure'] for x in r['attempts']))
   self.assertTrue(all((Path(x['data']).parent/'stdout.log').is_file() for x in r['attempts']))
 def test_c9_original_b1_is_separate_reference(self):
  r=c.baseline_reference_identity();self.assertEqual(r['binary_sha256'],'89c646db1de80c6e85fe34f7c3eaae2f10904810a8a6c3acc3426a7e7c1dd7a4')
  self.assertIn('DISTINCT',r['relation'])
 def test_host64_default_and_small_budget(self):
  r=c.allocation(dict(cpus=64,memory_bytes=128*c.GIB));self.assertEqual((r['jobs'],r['workers'],r['total_slots']),(3,20,63));self.assertLessEqual(r['case_memory_bytes'],24*c.GIB);self.assertGreaterEqual(r['reserve_bytes'],16*c.GIB)
  r=c.allocation(dict(cpus=8,memory_bytes=8*c.GIB));self.assertLessEqual(r['total_slots'],8);self.assertLessEqual(r['jobs']*r['case_memory_bytes']+r['reserve_bytes'],8*c.GIB)
 def test_failure_preserved_independent_complete_and_resume(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t)
   def cmd(name,data):return [sys.executable,'-c','import pathlib,sys;pathlib.Path(sys.argv[1]).write_text("ok");sys.exit(int(sys.argv[2]))',str(data/'payload'),str(7 if name=='time8' else 0)]
   alloc=dict(jobs=2,workers=1,case_memory_bytes=c.GIB)
   r=c.run_scheduler(Path('/unused'),root,dict(test=1),alloc,case_wall=2,total_wall=6,elapsed_cap=4,command_factory=cmd)
   self.assertEqual([r['status'] for r in r['attempts']],['FAILED','COMPLETE','COMPLETE'])
   r2=c.run_scheduler(Path('/unused'),root,dict(test=1),alloc,case_wall=2,total_wall=6,elapsed_cap=4,command_factory=cmd)
   self.assertEqual(len(r2['attempts']),3)
   (Path(r2['attempts'][1]['data'])/'payload').write_text('corrupt')
   r3=c.run_scheduler(Path('/unused'),root,dict(test=1),alloc,case_wall=2,total_wall=6,elapsed_cap=4,command_factory=cmd)
   self.assertEqual(len(r3['attempts']),3);self.assertIn('time16',r3['missing_cases'])
 def test_persistent_aggregate_budget(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);root.mkdir(exist_ok=True);c.save(root/'CAMPAIGN.json',dict(elapsed_used=0.,attempts=[dict(case='time8',status='FAILED',wall_seconds=6)]))
   r=c.run_scheduler(Path('/unused'),root,{},dict(jobs=1,workers=1,case_memory_bytes=c.GIB),case_wall=2,total_wall=6,elapsed_cap=4,command_factory=lambda n,d: (_ for _ in ()).throw(AssertionError('MUST_NOT_LAUNCH')))
   self.assertEqual(len(r['attempts']),1)
 def test_endpoint_setup_enrichment_and_missing_channel(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);left=root/'left';right=root/'right';left.mkdir();right.mkdir()
   endpoint=dict(N=1.,U=20.,temperature_K=8000.,proper_time_s=2.,flat=[.01,.01,.001,1.],ledgers=[1.]*14,Gamma_s=[1.,2.,3.],heat_erg_per_absorber_s=[1.,2.,3.],cohorts=[[1.,20.]],quadrupole_U_mu2_minus_third=0.)
   for dest in [left,right]:
    (dest/'endpoint.json').write_text(json.dumps(endpoint));(dest/'setup.json').write_text(json.dumps(dict(birth_times_s=[1.])));(dest/'observations.json').write_text('[]')
   self.assertEqual(a.finite_pair(left,right)['status'],'AVAILABLE')
   endpoint.pop('Gamma_s');(right/'endpoint.json').write_text(json.dumps(endpoint))
   self.assertEqual(a.finite_pair(left,right)['status'],'INVALID_PAIR')
 def test_exact_stored_denominators_zero_and_threshold(self):
  for lo,hi in [(1.,1.),(1.,2.),(1.5,3.)]:
   r=dict(dt=1.,before_N=2.,Q=2.,after_N=2./hi,nodes=2,lambda_min=lo-1,lambda_max=hi-1,d_min=lo,d_max=hi,Q_lo=2.,Q_hi=2.,S_lo=2./hi-.0001,S_hi=2./lo+.0001,cohort=0,birth_bits='0',a_bits='0',kernel='STORED_DENOMINATOR_DISCRETE_BE')
   o=a.analyze_row(r);low=o['exact_stored_kernel_enclosure'][0];self.assertEqual(F(int(low['numerator']),int(low['denominator'])),F(2)/F.from_float(hi))
  r.update(Q=0.,before_N=0.,after_N=0.,nodes=0,d_min=1.,d_max=1.,Q_lo=0.,Q_hi=0.,S_lo=0.,S_hi=0.,lambda_min=0.,lambda_max=0.)
  self.assertTrue(a.analyze_row(r)['zero_nodes'])
  self.assertEqual(a.finite_pair(None,None)['status'],'MISSING_PAIR')

if __name__=='__main__':unittest.main()
