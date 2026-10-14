"""Transport/receipt regressions only. No Rust or scientific reference is run.

Child results and modules below are explicit test doubles. Their values are
not Rust observations and must not be reported as function parity evidence.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[4]
CHECKER = ROOT / 'scripts/check_rust_forward_parity.py'


def load_checker():
    spec = importlib.util.spec_from_file_location('receipt_test_checker', CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextlib.contextmanager
def fake_reference_environment():
    modules = {}
    for name in ('jax', 'jax.numpy', 'numpy', 'scipy'):
        module = types.ModuleType(name)
        module.__version__ = 'SIMULATED_NO_REFERENCE_EXECUTED'
        modules[name] = module
    modules['jax'].numpy = modules['jax.numpy']
    modules['jax'].config = types.SimpleNamespace(read=lambda name: True)
    modules['jax'].default_backend = lambda: 'SIMULATED_NO_BACKEND'
    with mock.patch.dict(sys.modules, modules):
        yield


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.m = load_checker()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / 'receipt.json'
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()

    def invoke(self, check_contract=False):
        args = ['checker', '--output', str(self.output)]
        if check_contract:
            args.append('--check-contract')
        with mock.patch.object(sys, 'argv', args), contextlib.redirect_stdout(self.stdout), contextlib.redirect_stderr(self.stderr):
            return self.m.main()

    def receipt(self):
        self.assertTrue(self.output.exists(), 'requested failure receipt was not created')
        return json.loads(self.output.read_text())

    def run_transport(self, effects, fixture=None):
        fixture = fixture or {'cases': [], 'raw_protocol_cases': [], 'python_shape_cases': []}
        with fake_reference_environment(), mock.patch.object(self.m, 'check_contract', return_value=(fixture, {'grade':'SIMULATED_CONTRACT'})), mock.patch.object(self.m, 'load_reference', return_value=object()), mock.patch.object(self.m.subprocess, 'run', side_effect=effects) as child:
            code = self.invoke()
        return code, child

    def test_contract_failure_receipt_is_saved(self):
        with mock.patch.object(self.m, 'check_contract', side_effect=ValueError('INPUT_HASH_MISMATCH')), mock.patch.object(self.m, 'execute') as execution:
            code = self.invoke()
        self.assertEqual(code, 2)
        execution.assert_not_called()
        r = self.receipt()
        self.assertFalse(r['passed'])
        self.assertIn('INPUT_HASH_MISMATCH', r['error'])
        self.assertFalse(r['fallback_used'])

    def test_existing_receipt_aborts_before_validation_or_child(self):
        self.output.write_text('immutable evidence\n')
        with mock.patch.object(self.m, 'check_contract') as check, mock.patch.object(self.m, 'execute') as execution:
            code = self.invoke()
        self.assertEqual(code, 2)
        self.assertEqual(self.output.read_text(), 'immutable evidence\n')
        check.assert_not_called()
        execution.assert_not_called()

    def test_missing_reference_writes_failure_without_child(self):
        with mock.patch.object(self.m, 'check_contract', return_value=({}, {})), mock.patch.object(self.m, 'load_reference', side_effect=ModuleNotFoundError('SIMULATED_MISSING_JAX')), mock.patch.object(self.m.subprocess, 'run') as child:
            code = self.invoke()
        self.assertEqual(code, 2)
        child.assert_not_called()
        self.assertIn('SIMULATED_MISSING_JAX', self.receipt()['error'])

    def test_timeout_preserves_partial_binary_streams(self):
        error = subprocess.TimeoutExpired(['SIMULATED_CARGO'], 180,
                    output=b'partial-output\xff\n', stderr=b'partial-error\xfe\n')
        code, child = self.run_transport([error])
        self.assertEqual(code, 2)
        self.assertEqual(child.call_count, 1)
        r = self.receipt()
        self.assertFalse(r['passed'])
        run = r['child_runs'][0]
        self.assertEqual(run['status'], 'TIMEOUT')
        self.assertIsNone(run['returncode'])
        import base64
        self.assertEqual(base64.b64decode(run['stdout_base64']), error.output)
        self.assertEqual(base64.b64decode(run['stderr_base64']), error.stderr)
        self.assertIn('partial-output', self.stdout.getvalue())
        self.assertIn('partial-error', self.stdout.getvalue())

    def test_nonzero_child_keeps_exit_and_logs(self):
        proc = subprocess.CompletedProcess(['SIMULATED_CARGO'], 101, 'compiler stdout\n', 'compiler stderr\n')
        code, child = self.run_transport([proc])
        self.assertEqual(code, 2)
        self.assertEqual(child.call_count, 1)
        run = self.receipt()['child_runs'][0]
        self.assertEqual(run['returncode'], 101)
        self.assertEqual(run['status'], 'NONZERO_EXIT')
        self.assertEqual(run['stdout'], proc.stdout)
        self.assertEqual(run['stderr'], proc.stderr)

    def test_second_batch_timeout_keeps_first_batch(self):
        first = subprocess.CompletedProcess(['SIMULATED_CARGO'], 0, '', 'first batch log\n')
        second = subprocess.TimeoutExpired(['SIMULATED_CARGO'], 180, output='second partial\n', stderr='second error\n')
        code, child = self.run_transport([first, second])
        self.assertEqual(code, 2)
        self.assertEqual(child.call_count, 2)
        runs = self.receipt()['child_runs']
        self.assertEqual(len(runs), 2)
        self.assertEqual(runs[0]['status'], 'COMPLETED')
        self.assertEqual(runs[0]['stderr'], 'first batch log\n')
        self.assertEqual(runs[1]['status'], 'TIMEOUT')
        self.assertEqual(runs[1]['stdout'], 'second partial\n')

    def test_malformed_reply_keeps_success_exit_raw_evidence(self):
        proc = subprocess.CompletedProcess(['SIMULATED_CARGO'], 0, 'unexpected OK 1 7\n', '')
        code, child = self.run_transport([proc])
        self.assertEqual(code, 2)
        self.assertEqual(child.call_count, 1)
        r = self.receipt()
        self.assertIn('REPLY_COUNT_MISMATCH', r['error'])
        self.assertEqual(r['child_runs'][0]['stdout'], proc.stdout)
        self.assertEqual(r['child_runs'][0]['returncode'], 0)
        self.assertFalse(r['passed'])

    def test_launch_failure_records_no_child_exit(self):
        code, child = self.run_transport([FileNotFoundError('SIMULATED_MISSING_CARGO')])
        self.assertEqual(code, 2)
        self.assertEqual(child.call_count, 1)
        run = self.receipt()['child_runs'][0]
        self.assertEqual(run['status'], 'LAUNCH_ERROR')
        self.assertIsNone(run['returncode'])

    def test_mismatch_retains_reference_and_both_child_runs(self):
        fixture = {'cases':[{'id':'m','op':'mass','total':8,'prior':[1,3]}], 'raw_protocol_cases':[], 'python_shape_cases':[]}
        reply = subprocess.CompletedProcess(['SIMULATED_CARGO'], 0, 'm OK 2 2 7\n', '')
        with mock.patch.object(self.m, 'reference_case', return_value={'values':[2.,6.]}), mock.patch.object(self.m, 'scales', return_value=[2.,6.]), mock.patch.object(self.m, 'invariants', return_value=[]):
            code, child = self.run_transport([reply, reply], fixture)
        self.assertEqual(code, 1)
        self.assertEqual(child.call_count, 2)
        r = self.receipt()
        self.assertFalse(r['passed'])
        self.assertEqual(r['failures'][0]['reference']['values'], [2.,6.])
        self.assertEqual(r['failures'][0]['rust']['values'], [2.,7.])
        self.assertEqual(len(r['child_runs']), 2)

    def test_contract_success_does_not_execute_reference_or_rust(self):
        report = {'grade':'CONTRACT_ONLY_NOT_RUST_PARITY', 'cases':84}
        with mock.patch.object(self.m, 'check_contract', return_value=({}, report)), mock.patch.object(self.m, 'execute') as execute:
            code = self.invoke(check_contract=True)
        self.assertEqual(code, 0)
        execute.assert_not_called()
        self.assertEqual(self.receipt(), report)


if __name__ == '__main__':
    unittest.main(verbosity=2)
