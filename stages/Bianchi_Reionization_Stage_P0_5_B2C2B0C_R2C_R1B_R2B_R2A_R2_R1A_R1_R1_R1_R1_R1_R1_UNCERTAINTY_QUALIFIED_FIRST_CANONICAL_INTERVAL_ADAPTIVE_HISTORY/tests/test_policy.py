import copy,unittest
from helpers import load
m=load('test_policy_module','analysis/adaptive_policy.py')
class Tests(unittest.TestCase):
 def setUp(self):self.task=m.IntervalTask(0,64,0)
 def row(self,lane,accepted=True,classification='PASS',event=False,task=None):
  task=task or self.task;runtime='d'*64;key=m.job_key(lane=lane,task=task,accepted_index=1,parent_state_sha256='INITIAL',input_lock_sha256='b'*64,predecessor_kernel_sha256='c'*64,runtime_contract_sha256=runtime);duration=1.
  widths={'x_HII':1e-6,'x_HeII':1e-6,'x_HeIII':1e-6,'log_T':1e-6};local={k:1e-7 for k in widths};ledgers={k:[-1e-12,1e-12] for k in m.EXPECTED_LEDGER_KEYS}
  if classification=='PUBLIC_WIDTH_GATE_FAILURE':widths['log_T']=.002
  if not accepted and classification not in {'PUBLIC_WIDTH_GATE_FAILURE','VALIDATED_LOCAL_ERROR_GATE_FAILURE','SET_LEDGER_EXCLUDES_ZERO'}:widths={};local={};ledgers={}
  table={'any_event':event,'events':[{'any_event':True,'knot_indices':[],'minimum_distance':0.,'node_indices':[]}] if event else [],'minimum_distance':0. if event else .25,'node_count':0}
  candidate={'format':'REIADP1-deterministic-float64','node_count':m.STATE_NODE_COUNT,'path':'/tmp/candidate','sha256':'a'*64,'size_bytes':123} if accepted else None
  diagnostics={'map_enclosed':True,'maximum_validated_local_error':max(local.values()),'validated_local_error_bounds':local} if local else {'failed_phase':'full_step'}
  return {'accepted_index':1,'candidate_state':candidate,'classification':classification,'diagnostics':diagnostics,'duration_seconds_hex':duration.hex(),'input_lock_sha256':'b'*64,'interval':task.as_dict(),'job_key':key,'lane':lane,'parent_state_sha256':'INITIAL','predecessor_kernel_sha256':'c'*64,'public_widths':widths,'runtime_contract_sha256':runtime,'scientific_accept':accepted,'set_ledgers':ledgers,'stage_id':m.STAGE_ID,'table_event':table,'time':{'t0_hex':(duration*task.left_tick/m.TOTAL_TICKS).hex(),'t1_hex':(duration*task.right_tick/m.TOTAL_TICKS).hex()},'transport_status':'OK','worker_envelope_schema':1}
 def decide(self,rows,task=None):return m.validate_and_decide(task=task or self.task,accepted_index=1,parent_state_sha256='INITIAL',input_lock_sha256='b'*64,predecessor_kernel_sha256='c'*64,runtime_contract_sha256='d'*64,envelopes=rows)
 def test_common_and_missing(self):
  rows=[self.row(l) for l in m.LANE_ORDER];self.assertEqual(self.decide(rows).action,'ACCEPT')
  with self.assertRaisesRegex(ValueError,'missing'):self.decide(rows[:-1])
 def test_cross_lane_duration_mismatch_is_rejected(self):
  rows=[self.row(l) for l in m.LANE_ORDER];duration=2.;rows[1]['duration_seconds_hex']=duration.hex();rows[1]['time']={'t0_hex':0.0.hex(),'t1_hex':(duration*self.task.right_tick/m.TOTAL_TICKS).hex()}
  with self.assertRaisesRegex(ValueError,'cross-lane duration'):self.decide(rows)
 def test_table_event_precedes_cross_lane_duration_mismatch(self):
  rows=[self.row(l) for l in m.LANE_ORDER];duration=2.;rows[1]['duration_seconds_hex']=duration.hex();rows[1]['time']={'t0_hex':0.0.hex(),'t1_hex':(duration*self.task.right_tick/m.TOTAL_TICKS).hex()};rows[2]=self.row(m.LANE_ORDER[2],False,'TABLE_EVENT_REQUIRES_RESTART',True)
  self.assertEqual(self.decide(rows).action,'STOP_TABLE_EVENT')
 def test_reject_bisects_and_event_stops(self):
  rows=[self.row(l) for l in m.LANE_ORDER];rows[1]=self.row(m.LANE_ORDER[1],False,'PUBLIC_WIDTH_GATE_FAILURE');d=self.decide(rows);self.assertEqual(d.left_child,m.IntervalTask(0,32,1))
  rows[2]=self.row(m.LANE_ORDER[2],False,'TABLE_EVENT_REQUIRES_RESTART',True);self.assertEqual(self.decide(rows).action,'STOP_TABLE_EVENT')
 def test_minimum_stop_and_cursor(self):
  t=m.IntervalTask(17,18,6);rows=[self.row(l,False,'LOCAL_POPULATION_CERTIFICATE_FAILURE',task=t) for l in m.LANE_ORDER];self.assertEqual(self.decide(rows,t).action,'STOP_MINIMUM_STEP')
  c=m.Cursor(0,0,m.IntervalTask(0,32,1),(m.IntervalTask(32,64,1),));self.assertEqual(m.advance_after_accept(c).current,m.IntervalTask(32,64,1))
 def test_malformed_pass_and_cursor_are_rejected(self):
  rows=[self.row(l) for l in m.LANE_ORDER];bad=copy.deepcopy(rows);bad[0]['interval']={'depth':0,'left_tick':0,'right_tick':128}
  with self.assertRaisesRegex(ValueError,'interval'):self.decide(bad)
  bad=copy.deepcopy(rows);bad[1]['public_widths']['log_T']=float('nan')
  with self.assertRaisesRegex(ValueError,'width'):self.decide(bad)
  bad=copy.deepcopy(rows);bad[2]['set_ledgers']['H_nuclei']=[1.,2.]
  with self.assertRaisesRegex(ValueError,'ledger|gate'):self.decide(bad)
  with self.assertRaises(ValueError):m.validate_cursor(m.Cursor(1,64,m.IntervalTask(128,192,0),()))
 def test_boolean_grid_fields_are_not_integers(self):
  with self.assertRaises((TypeError,ValueError)):m.IntervalTask(0,64,False)
  with self.assertRaises((TypeError,ValueError)):m.validate_cursor(m.Cursor(False,0,m.IntervalTask(0,64,0),()))
if __name__=='__main__':unittest.main()
