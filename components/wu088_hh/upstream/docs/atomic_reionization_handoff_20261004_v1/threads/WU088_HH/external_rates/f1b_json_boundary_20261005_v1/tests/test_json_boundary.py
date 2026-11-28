"""Public CLI input checks; fixtures describe algebra only, not physical domains."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(os.environ.get('WU088_F1B_SCRIPT', ROOT / 'src/hh_f03_binding.py'))
ORIGINAL = ROOT / 'input/WU088_HH_FAST_F1B_20261004_v1/src/hh_f03_binding.py'
if not ORIGINAL.exists():
    ORIGINAL = ROOT.parent / 'f1b_20261004_v1/src/hh_f03_binding.py'
MODEL = {'n_h_cm3': '1', 'n_he_cm3': '1', 'kb_erg_k': '1', 'chi_erg': '10'}
# P=2.7 and u=3*P*2000/2; this is an inherited manufactured CLI fixture.
STATE = ['0.2', '0.3', '0.1', '8100', '1', '2', '3']


class JsonBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if hashlib.sha256(ORIGINAL.read_bytes()).hexdigest() != 'eb006d8ee3cf6b3b7365991c9442890a985f9eba011def37390f4dd92a54fa2f':
            raise AssertionError('Original F1B source identity changed')
        if hashlib.sha256((ORIGINAL.parent / 'hh_external.py').read_bytes()).hexdigest() != '8c02df302adc895be1327cb2e55bae03ebed8ec06ee7496ff4eeda20fdcdc197':
            raise AssertionError('Original provider identity changed')

    def call(self, text, script=SCRIPT, existing=None):
        with tempfile.TemporaryDirectory() as temp:
            inp, out = Path(temp) / 'input.json', Path(temp) / 'output.json'
            inp.write_text(text)
            if existing is not None:
                out.write_bytes(existing)
            argv = [sys.executable, '-B', str(script), '--input', str(inp), '--output', str(out)]
            r = subprocess.run(argv, capture_output=True, text=True)
            content = out.read_bytes() if out.exists() else None
            log = os.environ.get('WU088_CLI_CALL_LOG')
            if log:
                with Path(log).open('a') as f:
                    f.write(json.dumps({'script': str(script), 'input_sha256': hashlib.sha256(text.encode()).hexdigest(),
                                        'exit_code': r.returncode, 'output_present': content is not None,
                                        'stderr': r.stderr, 'preexisting_output': existing is not None}) + '\n')
            return r, content

    def reject(self, text, message):
        r, content = self.call(text)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIsNone(content)
        self.assertIn(message, r.stderr)
        self.assertNotIn('Traceback', r.stderr)

    def test_duplicate_provider_cannot_silently_select_another_fit(self):
        body = json.dumps({'model': MODEL, 'state': STATE})[:-1]
        for second_key in ('"provider"', '"provi\\u0064er"'):
            with self.subTest(second_key=second_key):
                self.reject(body + ',"provider":"LCS91",' + second_key + ':"KS92_corrected_Glover15"}',
                            'DUPLICATE_JSON_FIELD:provider')

    def test_duplicate_model_constant_rejected_before_output(self):
        model = json.dumps(MODEL)[:-1] + ',"chi_erg":"20"}'
        text = '{"model":' + model + ',"state":' + json.dumps(STATE) + ',"provider":"LCS91"}'
        self.reject(text, 'DUPLICATE_JSON_FIELD:chi_erg')

    def test_non_object_root_has_controlled_refusal(self):
        for text in ('null', '[]', '"provider"', '0', 'true'):
            with self.subTest(text=text):
                self.reject(text, 'JSON_OBJECT_INPUT_REQUIRED')

    def test_valid_inputs_retain_original_bytes_and_output_fence(self):
        for provider in ('LCS91', 'KS92_corrected_Glover15'):
            data = {'model': MODEL, 'state': STATE, 'provider': provider,
                    'direction': ['0.1', '0.2', '-0.1', '3', '0', '0', '0'], 'dt_s': '7',
                    'label': 'algebra_fixture_not_physical_domain'}
            text = json.dumps(data)
            with self.subTest(provider=provider):
                old, expected = self.call(text, ORIGINAL)
                new, actual = self.call(text)
                self.assertEqual(old.returncode, 0, old.stderr)
                self.assertEqual(new.returncode, 0, new.stderr)
                self.assertEqual(actual, expected)
                payload = json.loads(actual)
                self.assertFalse(payload['consumer_admission'])
                self.assertFalse(payload['state_box_enclosed'])
                self.assertFalse(payload['direction']['full_BE_invertibility_claim'])
                refusal, preserved = self.call(text, existing=actual)
                self.assertEqual(refusal.returncode, 2)
                self.assertEqual(preserved, actual)


if __name__ == '__main__':
    unittest.main()
