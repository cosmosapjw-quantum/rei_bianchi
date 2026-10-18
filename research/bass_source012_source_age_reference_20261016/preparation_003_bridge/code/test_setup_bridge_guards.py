"""Supplemental guard-only regressions: all process and clock boundaries mocked."""
import json,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock,patch
import setup_bridge as bridge

ROOT=Path(__file__).resolve().parents[1]/'guard_repair_001/raw'
class Clock:
    def __init__(self):self.now=0.
    def __call__(self):return self.now

class BridgeGuardTests(unittest.TestCase):
    def setUp(self):
        self.root=ROOT/self._testMethodName;self.root.mkdir(parents=True,exist_ok=False)
        self.private=self.root/'private';self.public=self.root/'public'
        self.private.mkdir();self.public.mkdir()
        self.usage=SimpleNamespace(ru_utime=.01,ru_stime=.02,ru_maxrss=100)

    def test_expired_unit_before_case_does_not_collect_or_popen(self):
        with patch.object(bridge.time,'monotonic',side_effect=[0.,31.,31.]),patch.object(bridge,'collect') as collect,patch.object(bridge.subprocess,'Popen') as popen:
            with self.assertRaisesRegex(bridge.BridgeFailure,'UNIT_DEADLINE_BEFORE_NEXT_CASE'):
                bridge._collect_cases(self.private,self.public)
            collect.assert_not_called();popen.assert_not_called()
        self.assertEqual(json.loads((self.public/'UNIT_FAILURE_DISPOSITION.json').read_text())['completed_cases'],0)

    def test_expired_immediate_pre_popen_starts_zero_children(self):
        with patch.object(bridge.time,'monotonic',side_effect=[0.,0.,11.,11.]),patch.object(bridge.subprocess,'Popen') as popen:
            with self.assertRaisesRegex(bridge.BridgeFailure,'IMMEDIATE_PREPOPEN_ZERO_NEW_CHILDREN'):
                bridge.collect(['MOCK_NEVER_EXECUTED'],self.private/'birth8',8,public_receipt_dir=self.public/'birth8')
            popen.assert_not_called()
        self.assertTrue((self.public/'birth8/FAILURE_DISPOSITION.json').exists())

    def test_after_reap_deadline_retains_measured_process_cost(self):
        clock=Clock();child=MagicMock(pid=12345)
        def reap(*args):clock.now=11.;return 12345,0,self.usage
        with patch.object(bridge.time,'monotonic',clock),patch.object(bridge.subprocess,'Popen',return_value=child),patch.object(bridge.os,'wait4',side_effect=reap),patch.object(bridge,'parse_stdout') as parse:
            with self.assertRaisesRegex(bridge.BridgeFailure,'DEADLINE_AFTER_REAP_COST_RETAINED'):
                bridge.collect(['MOCK_ONLY'],self.private/'birth8',8,public_receipt_dir=self.public/'birth8')
            parse.assert_not_called()
        receipt=json.loads((self.public/'birth8/PROCESS_RECEIPT.json').read_text())
        self.assertEqual(receipt['wall_seconds'],11.) # mocked clock, not actual work
        self.assertEqual(receipt['user_seconds'],.01)
        self.assertTrue((self.public/'birth8/FAILURE_DISPOSITION.json').exists())

    def test_validation_crossing_deadline_prevents_next_case(self):
        clock=Clock();child=MagicMock(pid=12345)
        def parse(*args):clock.now=31.;return {},{'status':'MOCK_VALIDATION_ONLY'}
        with patch.object(bridge.time,'monotonic',clock),patch.object(bridge.subprocess,'Popen',return_value=child) as popen,patch.object(bridge.os,'wait4',return_value=(12345,0,self.usage)),patch.object(bridge,'parse_stdout',side_effect=parse):
            with self.assertRaisesRegex(bridge.BridgeFailure,'DEADLINE_AFTER_VALIDATION_COST_RETAINED'):
                bridge._collect_cases(self.private,self.public)
            self.assertEqual(popen.call_count,1) # mock call only, zero actual process
        self.assertTrue((self.public/'birth_8/PROCESS_RECEIPT.json').exists())
        self.assertTrue((self.public/'birth_8/VALIDATION.json').exists())
        self.assertFalse((self.private/'birth_16').exists())
        self.assertEqual(json.loads((self.public/'UNIT_FAILURE_DISPOSITION.json').read_text())['completed_cases'],0)

    def test_final_validation_metadata_counts_toward_combined_case_cap(self):
        clock=Clock();child=MagicMock(pid=12345)
        with patch.object(bridge.time,'monotonic',clock),patch.object(bridge.subprocess,'Popen',return_value=child),patch.object(bridge.os,'wait4',return_value=(12345,0,self.usage)),patch.object(bridge,'parse_stdout',return_value=({}, {'large_mock_validation':'X'*4096})):
            with self.assertRaisesRegex(bridge.BridgeFailure,'AGGREGATE_OUTPUT_AFTER_VALIDATION_METADATA'):
                bridge.collect(['MOCK_ONLY'],self.private/'birth8',8,public_receipt_dir=self.public/'birth8',output_cap=2048)
        self.assertTrue((self.public/'birth8/PROCESS_RECEIPT.json').exists())
        self.assertTrue((self.public/'birth8/VALIDATION.json').exists())

    def test_last_case_cannot_bypass_unit_output_cap(self):
        with patch.object(bridge.time,'monotonic',return_value=0.),patch.object(bridge,'collect',return_value=({}, {}, {})) as collect,patch.object(bridge,'output_size',side_effect=[0,0,0,0,0,16777217]),patch.object(bridge.subprocess,'Popen') as popen:
            with self.assertRaisesRegex(bridge.BridgeFailure,'UNIT_AGGREGATE_OUTPUT_AFTER_CASE_METADATA'):
                bridge._collect_cases(self.private,self.public)
            self.assertEqual(collect.call_count,3);popen.assert_not_called()
        self.assertEqual(json.loads((self.public/'UNIT_FAILURE_DISPOSITION.json').read_text())['completed_cases'],3)

if __name__=='__main__':unittest.main(verbosity=2)
