"""Only new opacity-lane binding/debit checks; no old suite or native maps."""
import copy
import json
from pathlib import Path
import unittest
from prepare_opacity_transition import opacity_debited_controls,opacity_child_identity
HERE=Path(__file__).resolve().parent;PARENT=HERE.parents[2]/'c12/evidence/C2_FULL002/CHECKPOINTS/gen-00000059'

class Tests(unittest.TestCase):
    def test_second_failed_attempt_debit_keeps_controller_cursor(self):
        m=json.loads((PARENT/'metadata.json').read_text());before=copy.deepcopy(m)
        controls,allocation=opacity_debited_controls(m['restart_binding']['controls'],m['adaptive_cursor'])
        self.assertEqual(controls['max_attempts'],103)
        self.assertEqual(controls['max_accepted_macros'],103)
        self.assertEqual(allocation['external_failed_attempt_debit'],2)
        self.assertEqual(allocation['remaining_completed_attempts'],38)
        self.assertEqual(allocation['next_physical_attempt_ordinal'],68)
        self.assertEqual(m,before)
        self.assertEqual([k for k in controls if controls[k]!=m['restart_binding']['controls'][k]],['max_attempts'])

    def test_absorption_change_rebinds_control_but_preserves_source_identity(self):
        i=json.loads((PARENT/'identity.json').read_text());m=json.loads((PARENT/'metadata.json').read_text())
        binding=copy.deepcopy(m['restart_binding']);binding['controls']['max_attempts']=103
        binding['dependency_closure']['dependency:new_opacity_candidate.py']='1'*64
        new=opacity_child_identity(i,binding)
        self.assertEqual(new['source'],i['source'])
        self.assertEqual([k for k in new if new[k]!=i[k]],['control'])
        bad=copy.deepcopy(i);bad['source']='2'*64
        with self.assertRaisesRegex(ValueError,'UNCHANGED_SOURCE_IDENTITY'):
            opacity_child_identity(bad,binding)

if __name__=='__main__':unittest.main()
