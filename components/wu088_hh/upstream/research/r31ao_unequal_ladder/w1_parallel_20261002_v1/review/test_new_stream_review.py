"""Synthetic schema fixtures only, never scientific receipts or native executions."""
import copy,importlib.util,json,os,pathlib,sys,tempfile,unittest
HERE=pathlib.Path(__file__).resolve().parent
P=HERE.parent/'tile_runner/runner.py'
s=importlib.util.spec_from_file_location('review_stream_runner',P);r=importlib.util.module_from_spec(s);sys.modules[s.name]=r;s.loader.exec_module(r)
class StreamReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.ctx=r.context();cls.ctx['global_plan']=cls.ctx['d'].parse_json(r.read(r.GLOBAL));cls.grid=r.bound_grid(cls.ctx,cls.ctx['global_plan'],0,3);cls.p=cls.ctx['d'].parse_json(r.read(r.PRIOR/'plans/01.json'));cls.h=r.host_module()
 def fixture(self,path):
  q=json.loads(r.read(r.IMPORTED));q.pop('result_sha256');w=q.pop('wrapper');q['plan_sha256']=self.p['plan_sha256'];q['task_sha256']=self.p['tasks'][0]['task_sha256']
  w['physical_window']=self.p['window'];w['log2_window']=self.ctx['d'].log2_window(self.p['window']);w['command']=[str((r.BUILD/'primitive_worker').resolve()),'0',*[self.p['window'][k] for k in ('l_t','T_t','l_u','T_u')],*[str(r.LIMITS[k]) for k in ('precision_bits','radius_exp','relative_goal','max_evaluations','max_integration_calls','wall_seconds','queued_panels','degree_limit')],self.p['tasks'][0]['task_sha256'],self.p['plan_sha256']]
  stdout=r.canonical(q);stderr=b''
  host={'schema':'WU088_PROCESS_HOST_EXECUTION_V1','identity':self.h.identity(),'executor_override':'execute_bound_native_ONLY_FROZEN_RUN_TASK_VALIDATION_RETAINED','process_model':'DIRECT_EXEC_SINGLE_NATIVE_PROCESS','pdeath_signal':'SIGKILL','parent_pid_race_checked':True,'native_descendant_creation':'SECCOMP_DENY_FORK_VFORK_CLONE_CLONE3','native_process_pid':os.getpid(),'wall_cap_seconds':125,'cpu_cap_seconds':125,'memory_mib':1024,'file_bytes':r.MAX_BYTES,'native_command_sha256':r.digest(r.canonical(w['command'])),'native_wait_completed':True,'timed_out':False,'mpi_execution':False,'cgroup_containment':False,'native_execution_evidence':'SOURCE_BOUND_NATIVE_STDOUT'}
  for kind,data in [('stdout',stdout),('stderr',stderr)]:
   side=pathlib.Path(str(path)+'.'+kind);side.write_bytes(data);host[kind]={'path':str(side),'size':len(data),'sha256':r.digest(data)};w['native_'+kind+'_sha256']=r.digest(data)
  w['process_host']=host;q['wrapper']=w;return q
 def normalize(self,q,path):return r.normalize(self.ctx,self.grid,self.p,1,r.canonical(r.sealed(q,'result_sha256')),receipt_path=path)
 def test_exact_stream_fixture_then_receipt_only_reseal_tamper(self):
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td)/'SYNTHETIC_NOT_SCIENCE.json';q=self.fixture(p);self.normalize(q,p)
   q['rectangle']['real']['lower_mantissa']=str(int(q['rectangle']['real']['lower_mantissa'])+1)
   with self.assertRaisesRegex(ValueError,'differs from retained stdout'):self.normalize(q,p)
 def test_sidecar_and_host_resealed_but_receipt_mismatch_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td)/'SYNTHETIC_NOT_SCIENCE.json';q=self.fixture(p);data=json.loads(pathlib.Path(str(p)+'.stdout').read_bytes());data['rectangle']['imag']['lower_mantissa']=str(int(data['rectangle']['imag']['lower_mantissa'])+1);data=r.canonical(data);pathlib.Path(str(p)+'.stdout').write_bytes(data)
   q['wrapper']['native_stdout_sha256']=r.digest(data);q['wrapper']['process_host']['stdout'].update(sha256=r.digest(data),size=len(data))
   with self.assertRaisesRegex(ValueError,'differs from retained stdout'):self.normalize(q,p)
 def test_timeout_and_missing_native_attestation_rejected(self):
  for key,value in [('timed_out',True),('native_execution_evidence','NO_NATIVE_STDOUT_ATTESTATION')]:
   with self.subTest(key=key),tempfile.TemporaryDirectory() as td:
    p=pathlib.Path(td)/'SYNTHETIC_NOT_SCIENCE.json';q=self.fixture(p);q['wrapper']['process_host'][key]=value
    with self.assertRaisesRegex(ValueError,'source-bound stdout and no timeout'):self.normalize(q,p)
if __name__=='__main__':unittest.main(verbosity=2)
