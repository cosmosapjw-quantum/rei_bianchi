"""Analytic end-to-end fixtures, independent of the molecular solver."""
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from manufactured_cases import run_case


class Workflow(unittest.TestCase):
    def test_registered_analytic_reference_cases(self):
        manifest=json.loads((ROOT/'contract/MANUFACTURED_TASKS.json').read_text())
        for case in manifest['cases']:
            with self.subTest(case=case['case_id']):
                result=run_case(case,backend='reference',native_library=None)
                self.assertLess(result['max_error'],2e-11)
                self.assertEqual(result['physical_evaluations'],0)
                self.assertFalse(result['continuum_certificate'])
                self.assertAlmostEqual(result['observed_guard_gap'],.7)


if __name__=='__main__':
    unittest.main()
