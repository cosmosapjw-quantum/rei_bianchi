"""Targeted local fixtures only: no physics run, cargo, network, or NCP access."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import contextlib
import io

SPEC = importlib.util.spec_from_file_location('ncp_resume', Path(__file__).with_name('ncp_resume.py'))
N = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(N)


class ResumeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def profile(self, count=1):
        p = self.root / 'attempt003'
        (p / 'src').mkdir(parents=True)
        (p / 'src/hpc_profile.rs').write_bytes(b'fn main() { previous();' + N.BAD_NEWLINE * count + b'\n}\n')
        (p / 'Cargo.toml').write_text('[package]\nname="diagnostic"\nversion="0.1.0"\n')
        (p / 'Cargo.lock').write_text('# preserved fixture\nversion=3\n')
        (p / 'build_failure.log').write_text('original compiler failure\n')
        (p / 'failure.receipt.json').write_text('{"run":"NOT_EXECUTED"}\n')
        (p / 'caller.py').write_text('# existing caller; no invented command\n')
        (p / 'target').mkdir()
        (p / 'target/old_cache').write_text('must not copy\n')
        return p

    def test_zero_or_multiple_literal_rejected_before_destination_creation(self):
        for count in (0, 2):
            with self.subTest(count=count):
                p = self.root / 'attempt003'
                if p.exists():
                    import shutil
                    shutil.rmtree(p)
                source = self.profile(count)
                dest = self.root / ('repair' + str(count))
                before = (source / 'src/hpc_profile.rs').read_bytes()
                with self.assertRaisesRegex(ValueError, 'exactly one'):
                    N.repair_profile(source, dest)
                self.assertFalse(dest.exists())
                self.assertEqual(before, (source / 'src/hpc_profile.rs').read_bytes())

    def test_preparation_preserves_original_failures_and_copies_no_target(self):
        source = self.profile()
        original = {str(p.relative_to(source)): p.read_bytes() for p in source.rglob('*') if p.is_file()}
        dest = self.root / 'repair004'
        receipt = N.repair_profile(source, dest)
        self.assertEqual(receipt['status'], 'PREPARED_NOT_EXECUTED')
        self.assertFalse(receipt['profile_executed'])
        self.assertEqual(receipt['build']['status'], 'NOT_REQUESTED')
        self.assertFalse((dest / 'target').exists())
        self.assertNotIn(N.BAD_NEWLINE, (dest / 'src/hpc_profile.rs').read_bytes())
        self.assertEqual((dest / 'preserved_attempt003/build_failure.log').read_bytes(), original['build_failure.log'])
        self.assertEqual((dest / 'preserved_attempt003/hpc_profile.rs.original').read_bytes(), original['src/hpc_profile.rs'])
        self.assertEqual(original, {str(p.relative_to(source)): p.read_bytes() for p in source.rglob('*') if p.is_file()})
        with self.assertRaisesRegex(ValueError, 'fresh'):
            N.repair_profile(source, dest)

    def test_interrupted_campaign_is_incomplete_and_epoch_never_reset(self):
        stage = self.root / 'science005'
        campaign = stage / 'full_campaign001'
        campaign.mkdir(parents=True)
        epoch = campaign / 'campaign_epoch.json'
        epoch.write_text(json.dumps({'first_full_launch_epoch': N.EPOCH, 'deadline_epoch': N.DEADLINE}))
        before = epoch.read_bytes()
        proc = self.root / 'proc'
        proc.mkdir()
        result = N.status(stage, proc)
        self.assertEqual(result['status'], 'OBSERVED_INCOMPLETE_OR_UNAVAILABLE')
        self.assertTrue(result['epoch_matches_frozen'])
        self.assertFalse(result['epoch_modified'])
        self.assertEqual(epoch.read_bytes(), before)
        self.assertFalse(result['solver_launched_or_restarted'])

    def test_actual_native_argv_match_required_and_live_never_complete(self):
        stage = self.root / 'science005'
        campaign = stage / 'full_campaign001'
        campaign.mkdir(parents=True)
        case = N.CASES[0]
        argv = [str(stage / 'target/release/examples/axbi_reionization'), '--config',
                str(campaign / 'launches' / (case + '.runtime.cfg')), '--output',
                str(campaign / 'runs' / case), '--case', case]
        self.assertEqual(N.process_role(argv, stage, campaign), case)
        wrong = list(argv)
        wrong[wrong.index('--output') + 1] = '/other/job/output'
        self.assertIsNone(N.process_role(wrong, stage, campaign))
        proc = self.root / 'proc'
        process = proc / '239575'
        process.mkdir(parents=True)
        (process / 'cmdline').write_bytes(b'\0'.join(x.encode() for x in argv) + b'\0')
        values = ['0'] * 22
        values[0], values[17], values[19], values[21] = 'R', '8', '12345', '10'
        (process / 'stat').write_text('239575 (axbi test) ' + ' '.join(values))
        (process / 'status').write_text('Cpus_allowed_list:\t0-7\n')
        result = N.status(stage, proc)
        self.assertEqual(result['status'], 'OBSERVED_LIVE_INCOMPLETE')
        self.assertEqual(result['processes']['matched'][0]['start_ticks'], 12345)
        self.assertFalse(result['cases'][0]['observed_terminal_completion_evidence'])

    def test_default_cli_observes_missing_stage_and_refuses_overwrite(self):
        output = self.root / 'observation.json'
        self.assertEqual(N.main(['--stage', str(self.root / 'absent005'), '--output', str(output)]), 0)
        data = json.loads(output.read_text())
        self.assertFalse(data['stage_exists'])
        self.assertEqual(data['scientific_admission'], 'NOT_ISSUED')
        before = output.read_bytes()
        with self.assertRaises(SystemExit):
            N.main(['--stage', str(self.root / 'absent005'), '--output', str(output)])
        self.assertEqual(output.read_bytes(), before)

    def test_cli_repair_rejects_consumed_allowance_before_mutation(self):
        source = self.profile()
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        dest, output = self.root / 'forbidden_repair004', self.root / 'forbidden_output.json'
        for execute in (False, True):
            with self.subTest(execute=execute), mock.patch.object(N, 'repair_profile', side_effect=AssertionError('repair called')), mock.patch.object(N.subprocess, 'Popen', side_effect=AssertionError('build called')):
                stdout = io.StringIO()
                args = ['repair-profile', '--source', str(source), '--destination', str(dest), '--output', str(output)]
                if execute:
                    args.append('--execute')
                with contextlib.redirect_stdout(stdout):
                    code = N.main(args)
                result = json.loads(stdout.getvalue())
                self.assertEqual(code, 3)
                self.assertEqual(result['status'], 'ALREADY_COMPLETED')
                self.assertEqual(result['reason'], 'ALLOWANCE_EXHAUSTED')
                self.assertEqual((result['remaining_builds'], result['remaining_runs']), (0, 0))
                self.assertFalse(result['output_written'])
                self.assertFalse(dest.exists())
                self.assertFalse(output.exists())
                self.assertEqual(before, {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})


if __name__ == '__main__':
    unittest.main()
