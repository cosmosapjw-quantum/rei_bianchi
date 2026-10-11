"""New failure-lane migration checks only; saved arrays are never reintegrated."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from prepare_failure_transition import failure_debited_controls,assert_preserved,copy_initial_output
HERE=Path(__file__).resolve().parent
Q1B=HERE.parents[2]
PARENT=Q1B/'c12/evidence/C2_FULL001'

class Tests(unittest.TestCase):
    def test_failed_attempt_is_debited_without_breaking_cursor_counts(self):
        meta=json.loads((PARENT/'CHECKPOINTS/gen-00000039/metadata.json').read_text())
        before=copy.deepcopy(meta);new,allocation=failure_debited_controls(meta['restart_binding']['controls'],meta['adaptive_cursor'])
        self.assertEqual(new['max_attempts'],104);self.assertEqual(new['max_accepted_macros'],103)
        self.assertEqual(allocation['remaining_completed_attempts'],63)
        self.assertEqual(allocation['external_failed_attempt_debit'],1)
        self.assertEqual(meta,before)
        changed=[k for k in new if new[k]!=meta['restart_binding']['controls'][k]]
        self.assertEqual(changed,['max_attempts'])

    def test_all_saved_arrays_and_physical_metadata_preserved(self):
        p=PARENT/'CHECKPOINTS/gen-00000039'
        with np.load(p/'arrays.npz') as data:a={k:data[k].copy() for k in data.files}
        m=json.loads((p/'metadata.json').read_text());b={k:v.copy() for k,v in a.items()};n=copy.deepcopy(m)
        n['restart_binding']['controls']['max_attempts']=104;n['restart_binding_sha256']='child'
        n['production_repair_transition']={'sha256':'new'}
        self.assertTrue(assert_preserved(a,m,b,n)['all_nine_arrays_bitwise_equal'])
        b['prefix_state'][0,0]+=1e-9
        with self.assertRaisesRegex(ValueError,'ARRAY_CHANGED:prefix_state'):assert_preserved(a,m,b,n)

    def test_original_initial_output_receipt_copied_without_h0(self):
        m=json.loads((PARENT/'CHECKPOINTS/gen-00000039/metadata.json').read_text())
        with tempfile.TemporaryDirectory() as d:
            receipt=copy_initial_output(PARENT/'RUN',Path(d),m['production_output_records'])
            self.assertEqual(receipt['new_opacity_calls'],0);self.assertEqual(receipt['new_gas_calls'],0)
            for name in ('INITIAL_OUTPUT_BEGIN.json','INITIAL_OUTPUT_DONE.json','OUTPUT24/epoch-000.json'):
                self.assertEqual((PARENT/'RUN'/name).read_bytes(),(Path(d)/name).read_bytes())
            changed=copy.deepcopy(m['production_output_records']);changed[0]['fields']['xHII']+=1e-8
            with tempfile.TemporaryDirectory() as other:
                with self.assertRaisesRegex(ValueError,'INITIAL_OUTPUT_CHECKPOINT_RECORD'):
                    copy_initial_output(PARENT/'RUN',Path(other),changed)

if __name__=='__main__':unittest.main()
