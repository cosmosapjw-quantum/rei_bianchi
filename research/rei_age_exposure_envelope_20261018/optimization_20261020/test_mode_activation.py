"""Targeted regressions for observed mode activation using actual run outputs."""
import json
from pathlib import Path
import unittest
from bench import mode_activation_failures

RESULTS=Path(__file__).resolve().parent/'results'


def load(label):
    return json.loads((RESULTS/(label+'_STUDY.json')).read_text())


class ActivationTests(unittest.TestCase):
    def test_baseline_cannot_satisfy_requested_optimized_modes(self):
        self.assertTrue(mode_activation_failures(load('BASELINE'),True,True,False))

    def test_feature_free_output_cannot_satisfy_reference_request(self):
        failures=mode_activation_failures(load('WRAPPER_CHECK'),True,True,True)
        self.assertTrue(any(f['mode']=='reference_exp_endpoint_checks' for f in failures))

    def test_actual_optimized_execution_activates_both_modes(self):
        self.assertEqual(mode_activation_failures(load('C8'),True,True,False),[])

    def test_actual_reference_execution_checks_every_exp(self):
        self.assertEqual(mode_activation_failures(load('B8_REFERENCE'),True,False,True),[])


if __name__=='__main__':
    unittest.main()
