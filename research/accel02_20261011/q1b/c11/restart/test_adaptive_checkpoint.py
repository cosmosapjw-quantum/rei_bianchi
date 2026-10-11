"""Changed adaptive adapter cases; saved C10 states are fixture bytes only."""
import copy,json
from pathlib import Path
import sys,unittest
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'c10'))
from entry_checkpoint import unpack_entry_state
from adaptive_checkpoint import make_adaptive_snapshot,validate_adaptive_snapshot

class AdaptiveTests(unittest.TestCase):
    def setUp(self):
        p=HERE.parents[1]/'c10/evidence/NATIVE_ENTRY_C2_T1E11_N4_HEAT_CHECKPOINTS/gen-00000002'
        m=json.loads((p/'metadata.json').read_text())
        with np.load(p/'arrays.npz',allow_pickle=False) as a:
            self.scales=a['scales'].copy();self.states=[]
            for i,(t,y) in enumerate(zip(a['prefix_clock'],a['prefix_state'])):
                s=unpack_entry_state(y,m['cell_count']);s.update(t_s=float(t),nH_ref=m['nH_ref'],nHe_ref=m['nHe_ref'],
                    R=np.array(m['prefix_R'][i]),support=np.array(m['prefix_support'][i]))
                self.states.append(s)
        self.controls=dict(schema='rei.q1b.c11.adaptive_controls.v1',method_order=1,physical_state_floor=False,
            scientific_normalization_changed=False,local_defect_target=1e-7,safety=.8,min_shrink=.2,max_growth=2.,
            min_step_s=1.,max_step_s=1e12,initial_step_s=1e11,max_attempts=10,max_accepted_macros=5,
            observable_scales={'xHII':1.},distribution_scales={})
        self.cursor=dict(schema='rei.q1b.c11.adaptive_cursor.v1',next_step_s=1e11,attempts=1,
            accepted_macros=1,rejected_macros=0,accepted_boundaries=2,accepted_clock_s=5e10)
    def snap(self):return make_adaptive_snapshot(states=self.states,controls=self.controls,cursor=self.cursor,
        end_time_s=1e12,hard_events=[7e11],scales=self.scales,dependency_closure={})
    def test_macro_endpoint_retains_every_half_boundary(self):
        a,m=self.snap();result=validate_adaptive_snapshot(a,m)
        self.assertTrue(result['controller_checked']);self.assertEqual(a['prefix_clock'].tolist(),[0,2.5e10,5e10])
        self.assertEqual(m['adaptive_cursor']['accepted_boundaries'],2)
    def test_cursor_count_drift_rejected(self):
        a,m=self.snap();m['adaptive_cursor']['accepted_boundaries']=1
        with self.assertRaisesRegex(ValueError,'CURSOR'):validate_adaptive_snapshot(a,m)
    def test_control_binding_drift_rejected(self):
        a,m=self.snap();m['restart_binding']['controls']['local_defect_target']*=2
        with self.assertRaisesRegex(ValueError,'BINDING'):validate_adaptive_snapshot(a,m)
    def test_incomplete_half_history_rejected(self):
        self.states=self.states[::2]
        with self.assertRaisesRegex(ValueError,'CURSOR'):self.snap()
    def test_pending_midpoint_restart_rejected(self):
        a,m=self.snap();m['pending_halfstep']={'t_s':6e10}
        with self.assertRaisesRegex(ValueError,'PENDING'):validate_adaptive_snapshot(a,m)
if __name__=='__main__':unittest.main()
