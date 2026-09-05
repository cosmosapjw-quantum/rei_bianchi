#!/usr/bin/env python3
"""Contextual Release-name regression and deterministic synthetic-key clock check.

The real signed Ubuntu failure is preserved separately. No package is installed
or executed. The deliberately earlier signing clock below tests a fixture failure,
not an override of the production signature/date policy.
"""
from __future__ import annotations
import argparse
from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import types
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('rei_chain_fixture', HERE / 'test_signed_archive_chain.py')
fixture = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = fixture
spec.loader.exec_module(fixture)
OLD_HEAD = 'edec9771c1e725484ec1a7250ba0d340eb13e21b'
OLD_BLOB = 'a530ec095cca5a9347cb419f0ef9cb5632e39ed1'
PATH = 'docs/rei_runtime_03a4_h1b1_snapshot_package_census/signed_archive_chain.py'


def extra_rows():
    return ''.join(' ' + '0' * 64 + ' 7 ' + component + '/dep11/icons-' + size + '@2.tar' + suffix + '\n'
                   for component in ('main', 'multiverse', 'restricted', 'universe')
                   for size in ('48x48', '64x64', '128x128') for suffix in ('', '.gz'))


class CompatibilityTests(fixture.SignedChainTests):
    def test_compat_all_24_hidpi_names_signed_without_filtering(self):
        signed, packed = self.bundle(extra_sha=extra_rows())
        report = self.audit(signed, packed)
        self.assertEqual(report['input_sha256']['inrelease'], fixture.digest(signed))
        plain, _ = self.mod._authenticated_release(signed, self.keyring, self.policy(), Path('/usr/bin/gpgv'))
        rows = self.mod._release_entries(self.mod._deb822(plain)[0])
        self.assertEqual(len(rows), 26)
        self.assertEqual(sum('@2' in key for key in rows), 24)
        self.assertFalse(report['full_census_complete'])

    def test_compat_duplicate_hidpi_name_is_still_rejected(self):
        row = ' ' + '0' * 64 + ' 7 main/dep11/icons-64x64@2.tar\n'
        signed, packed = self.bundle(extra_sha=row + row)
        with self.assertRaisesRegex(self.mod.ChainError, 'DUPLICATE_RELEASE_INDEX'):
            self.audit(signed, packed)

    def test_compat_noncanonical_metadata_paths_remain_rejected(self):
        for path in ('main/../icons@2.tar', '/main/icons@2.tar', 'main//icons@2.tar',
                     'main/./icons@2.tar', 'main/%2e%2e/icons@2.tar',
                     'https://x@y/icons.tar', 'main/icons@2.tar?x=1', 'main/icons@2.tar#x'):
            with self.subTest(path=path):
                signed, packed = self.bundle(extra_sha=' ' + '0' * 64 + ' 7 ' + path + '\n')
                with self.assertRaisesRegex(self.mod.ChainError, 'UNSAFE_ARCHIVE_PATH'):
                    self.audit(signed, packed)

    def test_compat_payload_grammar_did_not_gain_at_sign(self):
        signed, packed = self.bundle(plain=self.stanza(filename='pool/example@2.deb'))
        with self.assertRaisesRegex(self.mod.ChainError, 'UNSAFE_ARCHIVE_PATH'):
            self.audit(signed, packed)

    def test_compat_frozen_clock_matches_actual_key_creation(self):
        self.assertTrue(fixture.FAKE_TIME.endswith('!'))
        p = subprocess.run(self.gpg + ['--with-colons', '--list-keys'],
                           capture_output=True, text=True, check=True, timeout=10)
        epoch = next(row.split(':')[5] for row in p.stdout.splitlines() if row.startswith('pub:'))
        self.assertEqual(epoch, fixture.FAKE_TIME[:-1])
        print(json.dumps({'fixture_key_creation_epoch': epoch, 'fixture_clock': fixture.FAKE_TIME,
                          'scope': 'SYNTHETIC_KEY_ONLY'}))

    def test_compat_before_creation_clock_fails_without_policy_bypass(self):
        args = list(self.gpg)
        args[-1] = str(int(fixture.FAKE_TIME[:-1]) - 1) + '!'
        p = subprocess.run(args + ['--armor', '--digest-algo', 'SHA256', '--clearsign'],
                           input=b'SYNTHETIC_CLOCK_DIAGNOSTIC\n', capture_output=True,
                           check=False, timeout=10)
        stderr = p.stderr.decode('utf-8', errors='replace')
        print(json.dumps({'diagnostic': 'SIGN_BEFORE_SYNTHETIC_KEY_CREATION',
                          'exit_code': p.returncode, 'stderr': stderr,
                          'historical_failure_stderr_recovered': False}))
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('created', stderr)
        signed, packed = self.bundle()
        self.assertEqual(self.audit(signed, packed)['status'], 'PASS_H1B1_SIGNED_ARCHIVE_CHAIN_COMPONENT')

    def test_compat_exact_legacy_donor_rejects_identical_signed_fixture(self):
        raw = subprocess.run(['git', 'show', OLD_HEAD + ':' + PATH], cwd=HERE,
                             capture_output=True, check=True, timeout=10).stdout
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        self.assertEqual(blob, OLD_BLOB)
        old = types.ModuleType('rei_legacy_chain_proved')
        sys.modules[old.__name__] = old
        exec(compile(raw, OLD_HEAD + ':' + PATH, 'exec'), old.__dict__)
        signed, packed = self.bundle(extra_sha=extra_rows())
        with self.assertRaisesRegex(old.ChainError, 'UNSAFE_ARCHIVE_PATH'):
            old.verify_chain(inrelease=signed, index_bytes=packed,
                             debs={fixture.FILENAME: fixture.PAYLOAD}, keyring=self.keyring,
                             policy=old.ArchivePolicy(**asdict(self.policy())), gpgv=Path('/usr/bin/gpgv'))
        self.assertEqual(self.audit(signed, packed)['status'], 'PASS_H1B1_SIGNED_ARCHIVE_CHAIN_COMPONENT')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    names = sorted(name for name in CompatibilityTests.__dict__ if name.startswith('test_compat_'))
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(CompatibilityTests(name) for name in names))
    report = {'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
              'skipped': len(result.skipped), 'successful': result.wasSuccessful(),
              'scope': 'SIGNED_SYNTHETIC_METADATA_AND_FIXTURE_CLOCK_ONLY'}
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() and result.testsRun == 7 else 1)
