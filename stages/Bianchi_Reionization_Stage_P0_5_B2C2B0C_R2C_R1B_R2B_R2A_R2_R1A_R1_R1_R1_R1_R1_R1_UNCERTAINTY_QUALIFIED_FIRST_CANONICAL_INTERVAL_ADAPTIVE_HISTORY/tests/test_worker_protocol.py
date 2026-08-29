import unittest
import copy
import numpy as np
from helpers import load
p=load('worker_test_policy','analysis/adaptive_policy.py');w=load('worker_test_module','analysis/attempt_worker.py')
class Event:
 def __init__(self,e,n,k,d):self.any_event=e;self.node_indices=np.array(n);self.knot_indices=np.array(k);self.minimum_distance=d
class Tests(unittest.TestCase):
 def job(self):
  t=p.IntervalTask(64,128,0);j={'accepted_index':2,'input_lock_sha256':'b'*64,'interval':t.as_dict(),'lane':p.LANE_ORDER[0],'parent':{'kind':'STATE','path':'/tmp/p','sha256':'a'*64},'predecessor_kernel_sha256':'c'*64,'runtime_contract_sha256':'d'*64,'stage_id':p.STAGE_ID,'worker_job_schema':1};j['job_key']=p.job_key(lane=j['lane'],task=t,accepted_index=2,parent_state_sha256='a'*64,input_lock_sha256='b'*64,predecessor_kernel_sha256='c'*64,runtime_contract_sha256='d'*64);return j
 def test_identity_and_events(self):
  self.assertEqual(w.validate_job(self.job()).task.as_dict(),{'depth':0,'left_tick':64,'right_tick':128});j=self.job();j['job_key']='0'*64
  with self.assertRaisesRegex(ValueError,'job key'):w.validate_job(j)
  s=w.summarize_events((Event(False,[],[],.25),Event(True,[7,2],[3,1],.125)));self.assertTrue(s['any_event']);self.assertEqual(s['node_count'],2)
 def test_job_schema_rejects_boolean_and_integral_float_fields(self):
  variants=[]
  for field,value in (('accepted_index',True),):
   job=copy.deepcopy(self.job());job[field]=value;variants.append(job)
  for field,value in (('left_tick',64.0),('right_tick',128.0),('depth',False)):
   job=copy.deepcopy(self.job());job['interval'][field]=value;variants.append(job)
  job=copy.deepcopy(self.job());job['unexpected']=1;variants.append(job)
  for job in variants:
   with self.subTest(job=job):
    with self.assertRaisesRegex(ValueError,'schema|integer|index|interval|unsupported'):w.validate_job(job)
 def test_rejection_no_state(self):
  e=w.make_envelope(job=self.job(),classification='PUBLIC_WIDTH_GATE_FAILURE',scientific_accept=False,widths={},table_event={'any_event':False,'events':[],'minimum_distance':1.,'node_count':0},set_ledgers={},diagnostics={},candidate_state=None,duration_seconds=1,t0=0,t1=.5,elapsed_s=.1,jax_guard_installed=False);self.assertIsNone(e['candidate_state'])
 def test_scientific_exception_mapping(self):
  self.assertEqual(w.classify_scientific_exception(FloatingPointError('POPULATION_CONE')),('POPULATION_CONE_FAILURE',False))
  self.assertEqual(w.classify_scientific_exception(ValueError('ABOVE_TABLE')),('TABLE_EVENT_ABOVE_TABLE_REQUIRES_RESTART',True))
  self.assertIsNone(w.classify_scientific_exception(ValueError('programming bug')))
if __name__=='__main__':unittest.main()
