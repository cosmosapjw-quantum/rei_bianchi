import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import backup_ncp as B


class BackupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.stage = self.root / 'stage'
        self.stage.mkdir()
        self.campaign = self.stage / 'full_campaign001'
        self.case = B.CASES[0]
        self.out = self.campaign / 'runs' / self.case
        self.out.mkdir(parents=True)
        (self.campaign / 'full_resource_plan.json').write_text('{"fixture_plan": true}\n')
        launch = self.campaign / 'launches'
        launch.mkdir()
        (launch / (self.case + '.receipt.json')).write_text(json.dumps({'returncode': 1, 'terminal_utc': 'now'}))
        for name, data in {'checkpoint.txt': 'AXBI_CHECKPOINT_V4\nfixture\n',
                           'config.cfg': 'frozen=1\n', 'source_identity.txt': 'identity\n',
                           'RETURN.txt': 'status=STOPPED\n', 'history.csv': 't,x\n0,1\n'}.items():
            (self.out / name).write_text(data)
        (self.stage / 'full_control.py').write_text('# frozen controller\n')
        self.proc = self.root / 'proc'
        self.proc.mkdir()
        self.disk = patch.object(B.shutil, 'disk_usage', return_value=type('Disk', (), {'free': 40 * B.GIB})())
        self.disk.start()

    def tearDown(self):
        self.disk.stop()
        self.tmp.cleanup()

    def run_backup(self, mode, **kw):
        return B.backup(mode, self.stage, self.root / (mode + '.tar.gz'),
                        case=self.case, evidence_roots=(), proc_root=self.proc, **kw)

    def make_live(self):
        p = self.proc / '123'
        p.mkdir()
        argv = [str(self.stage / 'target/release/examples/axbi_reionization'),
                '--output', str(self.out), '--case', self.case]
        (p / 'cmdline').write_bytes(b'\0'.join(s.encode() for s in argv))
        (p / 'stat').write_text('123 (solver) S 0 0')

    def test_compact_live_labeled_and_originals_unchanged(self):
        before = {p: p.read_bytes() for p in self.stage.rglob('*') if p.is_file()}
        self.make_live()
        (self.out / 'environment.txt').write_text('not for archive')
        r = self.run_backup('compact')
        self.assertEqual(r['status'], 'ARCHIVE_CREATED')
        self.assertEqual(r['snapshot_kind'], 'LIVE_SNAPSHOT_NOT_FULL_HISTORY')
        self.assertTrue(all(p.read_bytes() == b for p, b in before.items()))
        with tarfile.open(r['archive']) as tar:
            names = tar.getnames()
            self.assertFalse(any('history.csv' in n or 'environment' in n for n in names))
            manifest = json.load(tar.extractfile('BACKUP_MANIFEST.json'))
            self.assertEqual(manifest['snapshot_kind'], 'LIVE_SNAPSHOT_NOT_FULL_HISTORY')
            self.assertIn(str(self.stage / 'ncp_helpers.py'), manifest['missing'])

    def test_full_rejects_active_even_with_terminal_receipt(self):
        self.make_live()
        r = self.run_backup('full')
        self.assertEqual(r['status'], 'REJECTED_ACTIVE_SCIENCE')
        self.assertFalse(Path(r['archive']).exists())
        self.assertFalse(r['partial_retained'])

    def test_full_all_exact_members_and_extraction_matches(self):
        (self.out / 'spectra').mkdir()
        (self.out / 'spectra' / '0001.csv').write_text('a,b\n2,3\n')
        r = self.run_backup('full')
        self.assertEqual(r['status'], 'ARCHIVE_CREATED')
        expected = {'stage005/full_campaign001/runs/' + self.case + '/' + str(p.relative_to(self.out)): p.read_bytes()
                    for p in self.out.rglob('*') if p.is_file()}
        expected['stage005/full_campaign001/full_resource_plan.json'] = (self.campaign / 'full_resource_plan.json').read_bytes()
        expected['stage005/full_control.py'] = (self.stage / 'full_control.py').read_bytes()
        name = 'stage005/full_campaign001/launches/' + self.case + '.receipt.json'
        expected[name] = (self.campaign / 'launches' / (self.case + '.receipt.json')).read_bytes()
        with tarfile.open(r['archive']) as tar:
            self.assertEqual(set(tar.getnames()), set(expected) | {'BACKUP_MANIFEST.json'})
            for name, data in expected.items():
                self.assertEqual(tar.extractfile(name).read(), data)
        self.assertEqual(json.loads(Path(r['archive'] + '.status.json').read_text())['status'], 'ARCHIVE_CREATED')

    def test_partial_limit_retained_and_not_success(self):
        r = self.run_backup('full', max_archive_bytes=20)
        self.assertEqual(r['status'], 'PARTIAL_ARCHIVE_BUDGET')
        self.assertTrue(r['partial_retained'])
        self.assertFalse(Path(r['archive']).exists())
        self.assertTrue(Path(r['partial']).exists())

    def test_live_disk_floor_checked_during_stream(self):
        with patch.object(B.shutil, 'disk_usage', side_effect=[type('Disk', (), {'free': 40 * B.GIB})(),
                                                             type('Disk', (), {'free': 7 * B.GIB})()]):
            r = self.run_backup('full')
        self.assertEqual(r['status'], 'PARTIAL_DISK_FLOOR')
        self.assertTrue(r['partial_retained'])

    def test_missing_terminal_rejected_and_input_archive_never_replaced(self):
        (self.campaign / 'launches' / (self.case + '.receipt.json')).unlink()
        self.assertEqual(self.run_backup('full')['status'], 'REJECTED_TERMINAL_EVIDENCE_MISSING')
        with self.assertRaises(ValueError):
            B.backup('compact', self.stage, self.stage / 'danger.tar.gz')


if __name__ == '__main__':
    unittest.main()
