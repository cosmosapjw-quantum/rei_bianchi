"""Cheap structural regressions for the roadmap projection, not physical gates."""
import copy
import json
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from validate_igm_spine import PATH, validate  # noqa: E402


class IGMSpineStructuralTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PATH.read_text(encoding='utf-8'))

    def assert_rejected(self, mutant):
        with self.assertRaises(ValueError):
            validate(mutant)

    def test_frozen_valid_projection(self):
        result = validate(copy.deepcopy(self.payload))
        self.assertEqual((result['milestones'], result['canonical_delta']), (15, 0))

    def test_cycle_rejected(self):
        x = copy.deepcopy(self.payload)
        x['nodes'][0]['depends_on'].append('D0')
        self.assert_rejected(x)

    def test_missing_dependency_rejected(self):
        x = copy.deepcopy(self.payload)
        x['nodes'][1]['depends_on'].append('NONEXISTENT_CORE_NODE')
        self.assert_rejected(x)

    def test_auxiliary_cannot_increment_core(self):
        x = copy.deepcopy(self.payload)
        x['auxiliary_science'][0]['canonical_delta'] = 1
        self.assert_rejected(x)

    def test_falsely_promoted_roster_rejected(self):
        x = copy.deepcopy(self.payload)
        x['authority']['canonical_88_node_roster_located_in_this_snapshot'] = True
        self.assert_rejected(x)

    def test_stale_next_candidate_rejected(self):
        x = copy.deepcopy(self.payload)
        x['nodes'][2]['status'] = 'historical_scoped_complete'
        self.assert_rejected(x)

    def test_duplicate_stage_rejected(self):
        x = copy.deepcopy(self.payload)
        x['nodes'].append(copy.deepcopy(x['nodes'][0]))
        self.assert_rejected(x)

    def test_count_promotion_in_process_audit_rejected(self):
        x = copy.deepcopy(self.payload)
        x['reported_progress']['canonical_delta_this_audit'] = 1
        self.assert_rejected(x)

    def test_broken_critical_path_rejected(self):
        x = copy.deepcopy(self.payload)
        x['nodes'][3]['depends_on'] = []
        self.assert_rejected(x)


if __name__ == '__main__':
    unittest.main()
