"""Focused synthetic packaging recovery regressions; no physics or renderer run."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

SPEC = importlib.util.spec_from_file_location('zip_recovery_wrapper', Path(__file__).with_name('postprocess_ncp.py'))
W = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(W)
FAILED = 'CONTINUATION_FAILED_NO_FULL_PLOTS_OR_ADMISSION'


class ZipRecoveryTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.old = self.base / 'old'
        self.old.mkdir()
        self.root = self.base / 'renderer'
        self.root.mkdir()
        self.campaign = self.base / 'campaign'
        self.campaign.mkdir()
        for name in ('postprocess_flrw.py', 'vendor/compare_histories.py',
                     'vendor/source_pair_guard.py', 'vendor/reconstruction_support.py',
                     'FULL005_EPOCH.json', 'FULL005_EXPECTED_BINDINGS.json',
                     'FULL005_RESOURCE_PLAN.json', 'contracts/CONTRACT.md'):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'synthetic dependency only\n')
        self.set_status(W.SUCCESS)
        (self.old / 'figures').mkdir()
        (self.old / 'figures' / 'plot.png').write_bytes(b'synthetic PNG payload\x00\xff')
        (self.old / 'render.log').write_bytes(b'synthetic render log\n')
        (self.old / 'EXTERNAL_RAW_INPUT_INDEX.json').write_text('{"files": [], "synthetic": true}\n')
        (self.old / 'REPORT_PACKAGE_RECEIPT.json').write_bytes(b'old generated receipt')
        (self.old / 'RECOVERY_RECEIPT.json').write_bytes(b'old recovery receipt')
        (self.old / W.ARCHIVE_NAME).write_bytes(b'original partial ZIP, preserve exactly')
        self.input = self.campaign / 'external.csv'
        self.input.write_bytes(b'external raw input must stay external\n')
        for tree in (self.old, self.root, self.campaign):
            for path in tree.rglob('*'):
                if path.is_file():
                    os.utime(path, ns=(0, 0))

    def set_status(self, status, **extra):
        data = {'status': status, 'solver_runs': 0,
                'scientific_admission': 'NOT_ISSUED', **extra}
        (self.old / 'FINAL_STATUS.json').write_text(json.dumps(data, indent=3) + '\n')

    def snapshot(self):
        return {str(path.relative_to(self.base)): (path.read_bytes(), path.stat().st_mtime_ns)
                for tree in (self.old, self.root, self.campaign)
                for path in tree.rglob('*') if path.is_file()}

    def recover(self, name='fresh'):
        return W.repackage(self.old, self.base / name, self.campaign, self.root)

    def test_old_timestamp_failure_and_archive_only_repair(self):
        payload = self.old / 'figures' / 'plot.png'
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'before 1980'):
            with zipfile.ZipFile(self.base / 'old_behavior.zip', 'x') as bundle:
                bundle.write(payload, 'plot.png')
        result = self.recover()
        self.assertEqual(result['packaging_status'], 'PACKAGED')
        self.assertEqual(self.snapshot(), before)
        fresh = self.base / 'fresh'
        self.assertEqual((fresh / 'FINAL_STATUS.json').read_bytes(), (self.old / 'FINAL_STATUS.json').read_bytes())
        self.assertEqual((fresh / 'figures' / 'plot.png').stat().st_mtime_ns, 0)
        with zipfile.ZipFile(result['archive']) as bundle:
            self.assertIsNone(bundle.testzip())
            self.assertEqual(bundle.getinfo('report/figures/plot.png').date_time[:3], (1980, 1, 1))
            for path in self.old.rglob('*'):
                if path.is_file() and str(path.relative_to(self.old)) not in W.PACKAGE_GENERATED:
                    self.assertEqual(bundle.read('report/' + str(path.relative_to(self.old))), path.read_bytes())
            names = bundle.namelist()
            self.assertNotIn('report/' + W.ARCHIVE_NAME, names)
            self.assertNotIn('report/REPORT_PACKAGE_RECEIPT.json', names)
            self.assertNotIn('report/RECOVERY_RECEIPT.json', names)
            self.assertFalse(any(name.endswith('external.csv') for name in names))
            self.assertEqual(bundle.read('runnable/ncp_direct_resume_20261016/postprocess_ncp.py'), Path(W.__file__).read_bytes())
            for path in self.root.rglob('*'):
                if path.is_file():
                    self.assertEqual(bundle.read('runnable/flrw_full005_postprocess_20261015/' + str(path.relative_to(self.root))), path.read_bytes())

    def test_after_deadline_zero_readiness_render_or_child_calls(self):
        before = self.snapshot()
        with mock.patch.object(W.time, 'time', return_value=W.HARD_DEADLINE + 1000), \
             mock.patch.object(W, 'inspect', side_effect=AssertionError('inspect forbidden')) as inspect, \
             mock.patch.object(W, 'render', side_effect=AssertionError('render forbidden')) as render, \
             mock.patch.object(W, 'bounded_command', side_effect=AssertionError('bind forbidden')) as bound, \
             mock.patch.object(W.subprocess, 'Popen', side_effect=AssertionError('child forbidden')) as child:
            result = self.recover()
        self.assertEqual(result['scientific_status'], W.SUCCESS)
        self.assertEqual(result['packaging_status'], 'PACKAGED')
        for operation in (inspect, render, bound, child):
            operation.assert_not_called()
        self.assertEqual(self.snapshot(), before)

    def test_failed_and_unknown_statuses_are_not_promoted(self):
        variants = [
            ('failed', {'status': FAILED, 'solver_runs': 0, 'scientific_admission': 'NOT_ISSUED', 'error': 'original render failed'}, FAILED),
            ('missing', None, 'UNKNOWN_HOLD'),
            ('malformed', '{', 'UNKNOWN_HOLD'),
            ('nonobject', [], 'UNKNOWN_HOLD'),
            ('unrecognized', {'status': 'SUCCESS'}, 'UNKNOWN_HOLD'),
            ('contradictory', {'status': W.SUCCESS, 'solver_runs': 1, 'scientific_admission': 'NOT_ISSUED'}, 'UNKNOWN_HOLD'),
            ('admitted', {'status': W.SUCCESS, 'solver_runs': 0, 'scientific_admission': 'ISSUED'}, 'UNKNOWN_HOLD'),
            ('success_error', {'status': W.SUCCESS, 'solver_runs': 0, 'scientific_admission': 'NOT_ISSUED', 'error': 'contradiction'}, 'UNKNOWN_HOLD'),
        ]
        for name, data, expected in variants:
            with self.subTest(name=name):
                path = self.old / 'FINAL_STATUS.json'
                if data is None:
                    path.unlink()
                else:
                    path.write_text(data if isinstance(data, str) else json.dumps(data))
                before = self.snapshot()
                result = self.recover(name)
                self.assertEqual(result['scientific_status'], expected)
                self.assertEqual(result['packaging_status'], 'PACKAGED')
                self.assertEqual(self.snapshot(), before)
                if expected == FAILED:
                    self.assertEqual(result['original_error'], 'original render failed')
                else:
                    self.assertIn('original_status_validation_error', result)

    def test_recovery_packaging_failure_keeps_status_and_partial_evidence(self):
        self.set_status(FAILED, error='original renderer error')
        before = self.snapshot()
        def fail(output, root):
            (output / W.ARCHIVE_NAME).write_bytes(b'new partial ZIP')
            raise OSError('synthetic archive failure')
        with mock.patch.object(W, 'build_archive', side_effect=fail):
            result = self.recover()
        self.assertEqual(result['scientific_status'], FAILED)
        self.assertEqual(result['original_error'], 'original renderer error')
        self.assertEqual(result['packaging_status'], 'PACKAGING_FAILED')
        self.assertEqual(result['packaging_error'], 'synthetic archive failure')
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(Path(result['archive']).read_bytes(), b'new partial ZIP')
        self.assertEqual(W.load(self.base / 'fresh' / 'RECOVERY_RECEIPT.json'), result)

    def test_fresh_destination_and_overlap_guards_before_mutation(self):
        existing = self.base / 'existing'
        existing.mkdir()
        for output in (existing, self.old, self.old / 'nested', self.campaign / 'nested', self.root / 'nested'):
            with self.subTest(output=output):
                before = self.snapshot()
                with self.assertRaises(ValueError):
                    W.repackage(self.old, output, self.campaign, self.root)
                self.assertEqual(self.snapshot(), before)
                if output.name == 'nested':
                    self.assertFalse(output.exists())

    def main_result(self, action, output):
        argv = ['postprocess_ncp.py', action, '--output', str(output),
                '--campaign', str(self.campaign), '--renderer-root', str(self.root)]
        if action == 'repackage':
            argv += ['--existing-output', str(self.old)]
        stdout = io.StringIO()
        with mock.patch.object(W.sys, 'argv', argv), mock.patch.object(W.resource, 'setrlimit'), contextlib.redirect_stdout(stdout):
            code = W.main()
        return code, json.loads(stdout.getvalue())

    def test_cli_repackage_exit_means_packaging_and_typed_guard_failure(self):
        self.set_status(FAILED, error='original error')
        with mock.patch.object(W.subprocess, 'Popen') as child:
            code, result = self.main_result('repackage', self.base / 'cli')
        child.assert_not_called()
        self.assertEqual(code, 0)
        self.assertEqual(result['scientific_status'], FAILED)
        self.assertEqual(result['packaging_status'], 'PACKAGED')
        self.assertIn('zero is not scientific success', result['exit_code_meaning'])
        code, result = self.main_result('repackage', self.old / 'nested')
        self.assertEqual(code, 2)
        self.assertEqual(result['scientific_status'], FAILED)
        self.assertEqual(result['packaging_status'], 'PACKAGING_FAILED')
        self.assertEqual(result['original_error'], 'original error')
        with mock.patch.object(W, 'build_archive', side_effect=OSError('injected CLI package failure')):
            code, result = self.main_result('repackage', self.base / 'cli_failure')
        self.assertEqual(code, 2)
        self.assertEqual(result['scientific_status'], FAILED)
        self.assertEqual(result['packaging_status'], 'PACKAGING_FAILED')

    def test_executable_cli_smoke_packages_failed_result(self):
        self.set_status(FAILED, error='synthetic prior render failure')
        before = self.snapshot()
        completed = subprocess.run([
            sys.executable, W.__file__, 'repackage', '--existing-output', str(self.old),
            '--output', str(self.base / 'executable_cli'), '--campaign', str(self.campaign),
            '--renderer-root', str(self.root)], capture_output=True, text=True, timeout=10)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result['scientific_status'], FAILED)
        self.assertEqual(result['packaging_status'], 'PACKAGED')
        self.assertEqual(self.snapshot(), before)

    def test_original_render_packaging_failure_keeps_success_and_failure(self):
        for successful in (True, False):
            with self.subTest(successful=successful):
                output = self.base / ('render_success' if successful else 'render_failure')
                def command(args, log, deadline):
                    if args[2] == 'render':
                        target = Path(args[args.index('--output') + 1])
                        target.mkdir()
                        (target / 'POSTPROCESS_RECEIPT.json').write_text(json.dumps({'status': 'CONDITIONAL_FULL_INTERVAL_DIAGNOSTIC_REVIEW_PENDING'}))
                    return {'returncode': 0 if successful else 1}
                status = {'status': 'READY_FOR_EXPLICIT_ONE_SHOT_DIAGNOSTIC_RENDER', 'blockers': [],
                          'solver_runs': 0, 'scientific_admission': 'NOT_ISSUED'}
                with mock.patch.object(W, 'inspect', return_value=status), \
                     mock.patch.object(W, 'bounded_command', side_effect=command), \
                     mock.patch.object(W, 'build_archive', side_effect=OSError('archive failed')), \
                     mock.patch.object(W.subprocess, 'Popen') as child:
                    code, result = self.main_result('render', output)
                child.assert_not_called()
                expected = W.SUCCESS if successful else FAILED
                self.assertEqual(code, 2)
                self.assertEqual(result['scientific_status'], expected)
                self.assertEqual(result['packaging_status'], 'PACKAGING_FAILED')
                original = W.load(output / 'FINAL_STATUS.json')
                self.assertEqual(original['status'], expected)
                self.assertNotIn('packaging_status', original)
                self.assertEqual(result['packaging_error'], 'archive failed')
                if not successful:
                    self.assertEqual(result['error'], 'COMPLETED_BINDING_INPUT_CHECK_FAILED')
                    self.assertEqual(original['error'], result['error'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
