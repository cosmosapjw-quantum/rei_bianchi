"""New zero-map binding tests. No source scan/native trajectory is executed."""
from pathlib import Path
import copy,json,sys,tempfile,unittest
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from production_control import production_controls,assert_runtime_only_controls
from prepare_production_transition import prepare_transition,verify_parent_before_import,assert_prefix_preserved,verify_parent_payload
REPO=HERE.parents[5]
C11=HERE.parents[1]

class TransitionTests(unittest.TestCase):
    def setUp(self):
        self.controls=json.loads((C11/'controller/CONTROL_V1.json').read_text())
        self.parent=json.loads((C11/'HANDOFF.json').read_text())['parent']
    def test_runtime_caps_preserve_scales_and_counters(self):
        c=production_controls(self.controls,self.parent['cursor'])
        self.assertEqual((c['max_attempts'],c['max_accepted_macros']),(105,103))
        self.assertEqual(c['observable_scales'],self.controls['observable_scales'])
        self.assertEqual(c['bounded_run_request']['start_s'],self.parent['resume_t_s'])
        self.assertEqual(c['bounded_run_request']['end_s'],4.011926941800233e16)
        assert_runtime_only_controls(self.controls,c,self.parent['cursor'])
    def test_forbidden_numerical_and_physics_changes(self):
        for change in ('local_defect_target','physical_state_floor','observable_scales','method_order'):
            c=production_controls(self.controls,self.parent['cursor'])
            if change=='observable_scales':c[change]['T_K']*=2
            elif change=='physical_state_floor':c[change]=True
            else:c[change]*=2
            with self.subTest(change=change),self.assertRaisesRegex(ValueError,'FORBIDDEN_CONTROL_CHANGE'):
                assert_runtime_only_controls(self.controls,c,self.parent['cursor'])
    def test_manifest_payload_rejected_before_import(self):
        parent=REPO/self.parent['checkpoint']
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)
            for file in parent.iterdir():
                if file.is_file():(dest/file.name).write_bytes(file.read_bytes())
            with (dest/'metadata.json').open('ab') as f:f.write(b' ')
            with self.assertRaisesRegex(ValueError,'PARENT_MEMBER'):
                verify_parent_payload(dest,self.parent['manifest_sha256'])
    def test_actual_gen3_zero_map_transition_and_preservation(self):
        epochs=json.loads((C11/'integration/production_design/OUTPUT_EPOCHS.json').read_text())
        schedule={'target_time_s':epochs['time_s'][-1],'end_time_s':epochs['time_s'][-1],
                  'hard_events_s':epochs['time_s'][1:],'output_epochs_s':epochs['time_s'],
                  'shared65_indices':epochs['shared65_indices'],'scope':'TEST_OUTPUT_SCHEDULE_ONLY_NO_PHYSICAL_EVENTS_NO_LAUNCH'}
        base=REPO/'research/accel02_20261011/q1b/c12/transition/evidence'
        with tempfile.TemporaryDirectory(prefix='TEST_CHILD_',dir=base) as temp:
            out=Path(temp)/'child'
            result=prepare_transition(REPO,out,schedule)
            self.assertEqual(result['native_map_calls'],0)
            self.assertEqual(result['cursor'],self.parent['cursor'])
            self.assertEqual(result['generation'],3)
            self.assertEqual(result['preservation']['physical_arrays_bitwise'],True)
            self.assertEqual(result['preservation']['metadata_preserved'],True)
            self.assertEqual(result['parent_dependency_count'],41)
            self.assertEqual(result['controls']['max_attempts'],105)
            self.assertEqual(result['old_completed_replays'],0)
            with self.assertRaises(FileExistsError):prepare_transition(REPO,out,schedule)
            from adaptive_checkpoint import load_adaptive_checkpoint
            child=load_adaptive_checkpoint(result['checkpoint_directory'],3,result['identity'],expected_manifest_sha256=result['manifest_sha256'])
            self.assertEqual(child['metadata']['adaptive_cursor'],self.parent['cursor'])
            with np.load(REPO/self.parent['checkpoint']/'arrays.npz') as h:
                parentarrays={k:h[k] for k in h.files}
            bad={k:v.copy() for k,v in child['arrays'].items()}
            bad['scales'][0]*=2
            with self.assertRaisesRegex(ValueError,'PHYSICAL_ARRAY_CHANGED:scales'):
                assert_prefix_preserved(parentarrays,child['metadata'],bad,child['metadata'])

if __name__=='__main__':unittest.main(verbosity=2)
