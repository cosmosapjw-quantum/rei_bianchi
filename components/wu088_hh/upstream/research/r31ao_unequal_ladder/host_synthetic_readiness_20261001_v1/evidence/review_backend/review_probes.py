"""Bounded reviewer probes; no compiler, library build or native execution."""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HERE))
import backend_runner as runner
import provenance_gate as gate


class BoundaryReview(unittest.TestCase):
    def test_br01_locked_diagnostics_and_final_marker(self):
        source = (runner.OLD/'interior_pilot/native_petras_synthetic.cpp').read_text()
        for label in ('one_dimensional_polynomial=', 'nested_polynomial='):
            self.assertIn(label, source)
        payload = {'synthetic_only': True, 'native_fixture_checks': 10, 'actual_HH_evaluations': 0}
        stdout = 'one_dimensional_polynomial=0.333333333\nnested_polynomial=0.25\n' + json.dumps(payload) + '\n'
        with self.assertRaises(json.JSONDecodeError):
            json.loads(stdout)  # The initial runner's whole-stdout parser fails.
        result = runner.parse_native_marker('petras', stdout)
        self.assertEqual(result['payload'], payload)
        self.assertEqual(len(result['diagnostic_lines']), 2)
        with self.assertRaises(runner.RunnerError):
            runner.parse_native_marker('petras', stdout + 'trailing text\n')

    def test_br02_actual_streams_bound_to_synthetic_chain(self):
        with tempfile.TemporaryDirectory(prefix='synthetic_review_') as folder:
            root = Path(folder)
            prefix = root/'prefix'
            (prefix/'lib').mkdir(parents=True)
            compiler = root/'compiler'
            compiler.write_bytes(b'synthetic identity only; never executed')
            record = {'prefix': str(prefix), 'compiler': {**runner.identity(compiler), 'version': 'synthetic'}, 'libraries': {}}
            pins = {}
            for name in ('gmp', 'mpfr', 'flint'):
                archive = root/(name+'.archive')
                archive.write_bytes(('synthetic '+name).encode())
                archive_id = runner.identity(archive)
                binary = prefix/'lib'/('lib'+name+'.so')
                binary.write_bytes(b'\x7fELFsynthetic identity only; never executed')
                logs = []
                for stage in ('configure', 'build', 'install'):
                    streams = {}
                    for stream in ('stdout', 'stderr'):
                        path = root/(name+'_'+stage+'_'+stream+'.log')
                        path.write_text('synthetic stream only')
                        streams[stream] = runner.identity(path)
                    receipt = root/(name+'_'+stage+'.json')
                    receipt.write_text(json.dumps({'exit_code': 0, **streams}))
                    logs.append({'stage': stage, **runner.identity(receipt), 'exit_code': 0, **streams})
                pins[name] = {'version': 'synthetic', 'sha256': archive_id['sha256'], 'size': archive_id['size']}
                record['libraries'][name] = {
                    'version': 'synthetic', 'source_archive_path': str(archive), 'source_archive_sha256': archive_id['sha256'],
                    'binary_path': str(binary), 'binary_sha256': runner.identity(binary)['sha256'],
                    'compiler': record['compiler'], 'flags': ['-O2', '-fno-fast-math'], 'abi': {'synthetic': True},
                    'build_logs': logs, 'build_log_sha256': logs[1]['sha256'],
                }
            record_path = root/'record.json'
            record_path.write_text(json.dumps(record))
            with patch.object(gate, 'PINS', pins):
                checked = gate.verify_backend(record_path, prefix)
                self.assertEqual(checked['verification']['status'], 'BYTE_CHAIN_VERIFIED')
                self.assertFalse(checked['verification']['independent_execution_proven'])
                target = record['libraries']['flint']['build_logs'][1]
                for stream in ('stdout', 'stderr'):
                    path = Path(target[stream]['path'])
                    original = path.read_bytes()
                    path.write_bytes(b'tampered')
                    self.assertEqual(runner.identity(target['path'])['sha256'], target['sha256'])
                    with self.assertRaises(ValueError):
                        gate.verify_backend(record_path, prefix)
                    path.write_bytes(original)

    def test_locked_dependency_bytes(self):
        result = runner.check_input_lock()
        self.assertEqual(result['status'], 'PRIOR_CODE_BYTES_VERIFIED')
        self.assertTrue(result['synthetic_fixture_source_locked'])
        self.assertFalse(result['actual_HH_input_loader_in_pipeline'])

    def test_cli_defaults_to_plan_only(self):
        with tempfile.TemporaryDirectory(prefix='plan_review_') as folder:
            output = Path(folder)/'never_created'
            stub = {'tools': {}, 'status': 'SYNTHETIC_PREFLIGHT_STUB'}
            capture = io.StringIO()
            with patch.object(sys, 'argv', ['backend_runner.py', '--source-dir', folder, '--output', str(output)]), \
                    patch.object(runner, 'preflight', return_value=stub), \
                    patch.object(runner, 'execute') as execute, contextlib.redirect_stdout(capture):
                self.assertEqual(runner.main(), 0)
            execute.assert_not_called()
            self.assertFalse(output.exists())
            result = json.loads(capture.getvalue())
            self.assertEqual(result['status'], 'PLAN_ONLY')
            self.assertEqual(result['library_builds_executed'], 0)
            self.assertEqual(result['native_runs'], 0)
            self.assertEqual(result['actual_HH_runs'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
