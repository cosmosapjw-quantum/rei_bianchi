"""Pure new benchmark-contract tests: no actor or native execution."""
from pathlib import Path
import sys
import tempfile
import hashlib
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from benchmark_workers import check_code_pins,recommend,inspect_baseline,SAMPLE_CHECKS


class WorkerBenchmarkContracts(unittest.TestCase):
    def test_changed_or_missing_code_pin_is_refused(self):
        check_code_pins({'a.py':'abc'},{'a.py':'abc'})
        with self.assertRaisesRegex(ValueError,'BASELINE_CODE_PIN_MISMATCH'):
            check_code_pins({'a.py':'abc'},{'a.py':'def'})
        with self.assertRaisesRegex(ValueError,'BASELINE_CODE_PIN_MISMATCH'):
            check_code_pins({}, {'a.py':'abc'})

    def test_only_positive_finite_exact_pass_samples_compete(self):
        sample=lambda w,t,status='PASS_EXACT_PARITY',checks=None:dict(workers=w,phase_wall_s=t,
            status=status,exact_checks={name:True for name in SAMPLE_CHECKS} if checks is None else checks)
        selection=recommend([sample(8,4.),sample(16,3.),sample(32,.1,status='FAILED_PARITY'),
                             sample(48,.2,checks={'all':False}),sample(24,float('nan'))])
        self.assertEqual(selection['workers'],16)
        self.assertFalse(selection['guarantee'])
        self.assertEqual(selection['warmup_maps'],0)

    def test_no_eligible_sample_or_tie(self):
        self.assertIsNone(recommend([dict(workers=8,status='SKIPPED_RESOURCE_BUDGET')]))
        rows=[dict(workers=w,status='PASS_EXACT_PARITY',exact_checks={name:True for name in SAMPLE_CHECKS},phase_wall_s=2.) for w in (16,8)]
        self.assertEqual(recommend(rows)['workers'],8)

    def test_external_baseline_hash_mismatch_fails_before_content_trust(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp);(path/'RESULT.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'BASELINE_EXTERNAL_RESULT_HASH_MISMATCH'):
                inspect_baseline(path,'0'*64,'0'*64)

    def test_result_pin_does_not_authorize_changed_launch_pins(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)
            result=b'{}';(path/'RESULT.json').write_bytes(result)
            (path/'LAUNCH.json').write_text('{"code_pins":{"attacker.py":"changed"}}')
            with self.assertRaisesRegex(ValueError,'BASELINE_EXTERNAL_LAUNCH_HASH_MISMATCH'):
                inspect_baseline(path,hashlib.sha256(result).hexdigest(),'0'*64)


if __name__=='__main__':unittest.main()
