"""Only new third-failure budget/binding delta; no old test replay."""
import copy
import json
from pathlib import Path
import unittest
from prepare_opacity_transition_v4 import opacity_debited_controls
HERE=Path(__file__).resolve().parent
PARENT=HERE.parents[2]/'c12/evidence/C2_FULL003/CHECKPOINTS/gen-00000060'

class Tests(unittest.TestCase):
    def test_third_failure_debit_retains_actual_accepted_cursor(self):
        m=json.loads((PARENT/'metadata.json').read_text());before=copy.deepcopy(m)
        control,allocation=opacity_debited_controls(m['restart_binding']['controls'],m['adaptive_cursor'])
        self.assertEqual(control['max_attempts'],102);self.assertEqual(control['max_accepted_macros'],103)
        self.assertEqual(allocation['external_failed_attempt_debit'],3)
        self.assertEqual(allocation['remaining_completed_attempts'],36)
        self.assertEqual(allocation['next_child_attempt_number'],67)
        self.assertEqual(allocation['next_physical_attempt_ordinal'],70)
        self.assertEqual([k for k in control if control[k]!=m['restart_binding']['controls'][k]],['max_attempts'])
        self.assertEqual(m,before)

if __name__=='__main__':unittest.main()
