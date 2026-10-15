"""Portable-wrapper tests with synthetic controller files and a mock renderer.

No solver, physical histories, actual full005 rendering, or network access.
"""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock
import zipfile

SPEC = importlib.util.spec_from_file_location('postprocess_ncp', Path(__file__).with_name('postprocess_ncp.py'))
W = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(W)


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


class PortablePostprocessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'renderer'
        self.campaign = self.base / 'campaign'
        self.root.mkdir()
        self.campaign.mkdir()
        source = b'synthetic source identity, never a scientific input\n'
        source_path = self.base / 'source.txt'
        source_path.write_bytes(source)
        self.patch_source = mock.patch.object(W, 'SOURCE_SHA', W.sha(source_path))
        self.patch_source.start()
        self.addCleanup(self.patch_source.stop)
        # Tests inspect the frozen deadline semantics without depending on the
        # calendar date. Production code has no deadline override argument.
        self.patch_time = mock.patch.object(W.time, 'time', return_value=W.HARD_DEADLINE - 1000)
        self.patch_time.start()
        self.addCleanup(self.patch_time.stop)
        self.epoch = {'deadline_epoch': W.HARD_DEADLINE - 3600, 'never_reset_on_resume': True}
        self.plan = {'source_identity_sha256': W.SOURCE_SHA, 'binary_sha256': W.BINARY_SHA, 'cases': []}
        expected = {}
        for case, cells in zip(W.CASES, (512, 1024)):
            run = self.campaign / 'runs' / case
            run.mkdir(parents=True)
            (run / 'source_identity.txt').write_bytes(source)
            config = f'transport_cells={cells}\nq_ref=0\n'
            (run / 'config.cfg').write_text(config)
            name = f'full_q{cells}.cfg'
            basecfg = self.campaign / 'configs' / name
            basecfg.parent.mkdir(exist_ok=True)
            basecfg.write_text(config)
            runtime = self.campaign / 'launches' / (case + '.runtime.cfg')
            runtime.parent.mkdir(exist_ok=True)
            runtime.write_text(config)
            frozen = {'source_identity_sha256': W.SOURCE_SHA, 'binary_sha256': W.BINARY_SHA,
                      'base_config_sha256': W.sha(basecfg), 'runtime_config_sha256': W.sha(runtime)}
            expected[case] = frozen
            self.plan['cases'].append({'case': case, 'config': name, 'config_sha256': W.sha(basecfg)})
            save(self.campaign / 'launches' / (case + '.binding.json'), dict(frozen, case=case))
            native = {'status': 'COMPLETE_REPRESENTED_INTERVAL', 'result': 'Ok(())', 'a': '0.2', 'accepted': '10'}
            (run / 'RETURN.txt').write_text(''.join(f'{k}={v}\n' for k, v in native.items()))
            for name in ('history.csv', 'abundances.csv', 'ledgers.csv', 'checkpoint.txt'):
                (run / name).write_text('synthetic wrapper fixture, never physical data\n')
            save(self.campaign / 'launches' / (case + '.receipt.json'), dict(
                frozen, case=case, returncode=0, native_completion_proof=True,
                source_config_binary_bindings_match=True, source_identity_readback_equal=True,
                config_readback_equal=True, stop_reason=None, terminal_parse_error=None,
                native_return=native))
        save(self.root / 'FULL005_EXPECTED_BINDINGS.json', {'bindings': expected})
        save(self.root / 'FULL005_RESOURCE_PLAN.json', self.plan)
        save(self.root / 'FULL005_EPOCH.json', self.epoch)
        save(self.campaign / 'campaign_epoch.json', self.epoch)
        save(self.campaign / 'full_resource_plan.json', self.plan)
        save(self.campaign / 'full_campaign.receipt.json', {
            'status': 'ALL_FULL_CASES_COMPLETE_PENDING_SCIENTIFIC_POSTPROCESS',
            'source_identity_sha256': W.SOURCE_SHA, 'binary_sha256': W.BINARY_SHA,
            'source_unchanged': True, 'global_stop_reason': None, 'campaign_epoch': self.epoch})
        for name in ('compare_histories.py', 'source_pair_guard.py', 'reconstruction_support.py'):
            path = self.root / 'vendor' / name
            path.parent.mkdir(exist_ok=True)
            path.write_text('# synthetic renderer dependency\n')
        contract = self.root / 'contracts' / 'CONTRACT.md'
        contract.parent.mkdir()
        contract.write_text('synthetic packaging fixture\n')
        # This executable mock uses the real subprocess boundary and reports its
        # enforced address-space limit. It performs no scientific computation.
        (self.root / 'postprocess_flrw.py').write_text('''import json, pathlib, resource, sys
args=sys.argv[1:]
out=pathlib.Path(args[args.index('--output')+1])
if args[0]=='bind':
    out.write_text(json.dumps({'synthetic_mock':True}))
else:
    out.mkdir()
    (out/'POSTPROCESS_RECEIPT.json').write_text(json.dumps({
        'status':'CONDITIONAL_FULL_INTERVAL_DIAGNOSTIC_REVIEW_PENDING',
        'synthetic_mock':True,
        'address_space_limit_bytes':resource.getrlimit(resource.RLIMIT_AS)[0]}))
''')

    def test_incomplete_case_blocks_without_launch(self):
        path = self.campaign / 'launches' / (W.CASES[1] + '.receipt.json')
        receipt = W.load(path)
        receipt['returncode'] = 1
        save(path, receipt)
        with mock.patch.object(W.subprocess, 'Popen') as child:
            result = W.render(self.campaign, self.root, self.base / 'report')
        self.assertTrue(any('CONTROLLER_TERMINAL_INCOMPLETE' in item for item in result['blockers']))
        child.assert_not_called()
        self.assertFalse((self.base / 'report' / 'figures_and_diagnostics').exists())

    def test_missing_campaign_terminal_blocks(self):
        (self.campaign / 'full_campaign.receipt.json').unlink()
        result = W.inspect(self.campaign, self.root)
        self.assertTrue(any('CAMPAIGN_TERMINAL_UNAVAILABLE' in item for item in result['blockers']))

    def test_source_or_config_readback_mismatch_blocks(self):
        for name in ('source_identity.txt', 'config.cfg'):
            with self.subTest(name=name):
                path = self.campaign / 'runs' / W.CASES[0] / name
                original = path.read_bytes()
                path.write_bytes(original + b'changed\n')
                with mock.patch.object(W.subprocess, 'Popen') as child:
                    result = W.render(self.campaign, self.root, self.base / ('report_' + name))
                self.assertTrue(any('SOURCE_CONFIG_READBACK_MISMATCH' in item for item in result['blockers']))
                child.assert_not_called()
                path.write_bytes(original)

    def test_binary_binding_mismatch_blocks(self):
        path = self.campaign / 'launches' / (W.CASES[0] + '.binding.json')
        binding = W.load(path)
        binding['binary_sha256'] = 'wrong'
        save(path, binding)
        self.assertTrue(any('FROZEN_BINDING_MISMATCH:binary_sha256' in item
                            for item in W.inspect(self.campaign, self.root)['blockers']))

    def test_original_deadline_expired_blocks_and_is_not_reset(self):
        with mock.patch.object(W.time, 'time', return_value=W.HARD_DEADLINE + 1):
            with mock.patch.object(W.subprocess, 'Popen') as child:
                result = W.render(self.campaign, self.root, self.base / 'expired')
        self.assertIn('ORIGINAL_POSTPROCESS_DEADLINE_EXPIRED_FRESH_SCOPED_POSTPROCESS_BUDGET_REQUIRED', result['blockers'])
        self.assertEqual(result['postprocess_hard_deadline_epoch'], 1792122617.77407)
        child.assert_not_called()

    def test_successful_mock_renderer_subprocesses_are_bounded_and_packaged(self):
        output = self.base / 'success'
        result = W.render(self.campaign, self.root, output)
        self.assertEqual(result['status'], W.SUCCESS)
        self.assertEqual(result['scientific_admission'], 'NOT_ISSUED')
        for phase in ('bind', 'render'):
            self.assertEqual(result[phase]['returncode'], 0)
            self.assertGreater(result[phase]['timeout_seconds'], 0)
            self.assertLessEqual(result[phase]['timeout_seconds'], 300)
            self.assertEqual(result[phase]['address_space_limit_bytes'], 8 * 1024**3)
        self.assertLess(result['render']['timeout_seconds'], result['bind']['timeout_seconds'])
        receipt = W.load(output / 'figures_and_diagnostics' / 'POSTPROCESS_RECEIPT.json')
        self.assertTrue(receipt['synthetic_mock'])
        self.assertEqual(receipt['address_space_limit_bytes'], W.CAP_MEMORY)
        archive = output / 'POSTPROCESS_REPORT_WITH_RUNNABLE_CODE_EXTERNAL_INPUTS.zip'
        with zipfile.ZipFile(archive) as bundle:
            names = bundle.namelist()
            self.assertIsNone(bundle.testzip())
            for dependency in ('FULL005_EXPECTED_BINDINGS.json', 'FULL005_RESOURCE_PLAN.json', 'FULL005_EPOCH.json'):
                self.assertIn('runnable/flrw_full005_postprocess_20261015/' + dependency, names)
            self.assertEqual(sum('/vendor/' in name for name in names), 3)
            self.assertFalse(any(name.endswith('/history.csv') for name in names))
            self.assertTrue(any(name.endswith('.runtime.cfg') for name in names))

    def test_output_cannot_be_existing_or_inside_campaign(self):
        for output in (self.campaign, self.campaign / 'new_report'):
            with self.subTest(output=output):
                with self.assertRaises(ValueError):
                    W.render(self.campaign, self.root, output)

    def test_keyboard_interrupt_kills_renderer_group_and_reaps(self):
        child = mock.Mock(pid=12345)
        child.wait.side_effect = [KeyboardInterrupt(), 0]
        with mock.patch.object(W.subprocess, 'Popen', return_value=child):
            with mock.patch.object(W.os, 'killpg') as killpg:
                with self.assertRaises(KeyboardInterrupt):
                    W.bounded_command(['synthetic-mock-renderer'], self.base / 'interrupt.log',
                                      W.time.monotonic() + 300)
        killpg.assert_called_once_with(child.pid, W.signal.SIGKILL)
        self.assertEqual(child.wait.call_count, 2)
        self.assertIn('timeout', child.wait.call_args_list[0].kwargs)
        self.assertEqual(child.wait.call_args_list[1], mock.call())


if __name__ == '__main__':
    unittest.main(verbosity=2)
