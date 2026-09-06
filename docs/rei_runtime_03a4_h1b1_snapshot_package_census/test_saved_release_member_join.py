#!/usr/bin/env python3
"""Offline public-consumer integration using one saved synthetic signed fixture.

--create-fixture writes only public input bytes to a new --fixture-dir and exits.
Normal invocation reads those exact bytes; --only J01 selects the discriminator
for an actual old-donor RED. No expected-RED success or unittest skip is used.
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
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
PARENT = 'c03ff27615cce53a5057d8facbf141b83c89913b'
DONOR_PATH = 'docs/rei_runtime_03a4_h1b1_snapshot_package_census/signed_archive_chain.py'
OLD_BLOB = 'a530ec095cca5a9347cb419f0ef9cb5632e39ed1'
FIXTURE_DIR = None
OBSERVATIONS = []


def load(name, path):
    assert name not in sys.modules, 'FRESH_MODULE_NAME_REQUIRED:' + name
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha(data):
    return hashlib.sha256(data).hexdigest()


def create_fixture(directory):
    member = load('rei_saved_join_fixture_helpers', HERE / 'test_deb_member_census.py')
    compat = load('rei_saved_join_compat_helpers', HERE / 'test_release_path_compat.py')
    fixture_class = member.FIXTURE.SignedChainTests
    fixture_class.setUpClass()
    try:
        fixture = fixture_class('test_valid_real_signature_and_hash_chain')
        payload = member.deb_bytes()
        directory.mkdir(parents=True, exist_ok=False)
        files = {'package.deb': payload, 'public-keyring.gpg': fixture.keyring}
        filenames = {'normal': member.FIXTURE.FILENAME, 'unsafe': 'pool/example@2.deb'}
        for label, filename in filenames.items():
            stanza = (f'Package: {member.FIXTURE.PACKAGE}\nVersion: {member.FIXTURE.VERSION}\n'
                      f'Architecture: amd64\nFilename: {filename}\nSize: {len(payload)}\n'
                      f'SHA256: {sha(payload)}\n\n').encode()
            signed, packed = fixture.bundle(plain=stanza, extra_sha=compat.extra_rows())
            files[label + '.InRelease'] = signed
            files[label + '.Packages.xz'] = packed
        for name, data in files.items():
            (directory / name).write_bytes(data)
        record = {'scope': 'SYNTHETIC_REAL_GPG_NOT_UBUNTU_ARCHIVE',
                  'policy': asdict(fixture.policy()), 'filenames': filenames,
                  'member': member.MEMBER, 'member_sha256': sha(member.CONTENT),
                  'signed_hidpi_rows': 24, 'total_signed_sha256_rows': 26,
                  'files': {name: {'size': len(data), 'sha256': sha(data)} for name, data in files.items()},
                  'private_keys_included': False}
        (directory / 'FIXTURE.json').write_text(json.dumps(record, indent=2) + '\n')
        return record
    finally:
        fixture_class.tearDownClass()


class JoinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.consumer = load('rei_saved_join_current_consumer', HERE / 'deb_member_census.py')
        cls.fixture = json.loads((FIXTURE_DIR / 'FIXTURE.json').read_text())
        for name, identity in cls.fixture['files'].items():
            data = (FIXTURE_DIR / name).read_bytes()
            assert len(data) == identity['size'] and sha(data) == identity['sha256'], name
        assert cls.consumer.DONOR is sys.modules[cls.consumer.DONOR_NAME]
        assert cls.consumer.ArchivePolicy is cls.consumer.DONOR.ArchivePolicy

    def inputs(self, consumer=None, label='normal'):
        consumer = self.consumer if consumer is None else consumer
        filename = self.fixture['filenames'][label]
        fields = dict(self.fixture['policy'])
        fields['allowed_primary_fingerprints'] = tuple(fields['allowed_primary_fingerprints'])
        fields['required'] = tuple(map(tuple, fields['required']))
        policy = consumer.DONOR.ArchivePolicy(**fields)
        self.assertIs(type(policy), consumer.DONOR.ArchivePolicy)
        return dict(inrelease=(FIXTURE_DIR / (label + '.InRelease')).read_bytes(),
                    index_bytes=(FIXTURE_DIR / (label + '.Packages.xz')).read_bytes(),
                    keyring=(FIXTURE_DIR / 'public-keyring.gpg').read_bytes(), policy=policy,
                    debs={filename: (FIXTURE_DIR / 'package.deb').read_bytes()}, gpgv=Path('/usr/bin/gpgv'),
                    required_members=((filename, self.fixture['member'], self.fixture['member_sha256']),))

    def test_J01_public_consumer_accepts_signed_hidpi_fixture(self):
        inputs = self.inputs()
        donor = self.consumer.DONOR
        with mock.patch.object(donor, 'verify_chain', wraps=donor.verify_chain) as called:
            try:
                report = self.consumer.verify_member_census(**inputs)
            except donor.ChainError as error:
                OBSERVATIONS.append({'id': self.id(), 'stage': 'ACTUAL_PUBLIC_CONSUMER',
                                     'error': str(error), 'donor_calls': called.call_count,
                                     'inrelease_sha256': sha(inputs['inrelease']),
                                     'policy_identity_verified': type(inputs['policy']) is donor.ArchivePolicy})
                if str(error) == 'UNSAFE_ARCHIVE_PATH':
                    self.fail('MISSING_RELEASE_MEMBER_JOIN:' + str(error))
                raise
        self.assertEqual(called.call_count, 1)
        self.assertEqual(report['status'], 'PASS_H1B1_AUTHENTICATED_DEB_MEMBERS')
        self.assertEqual(report['signed_chain']['input_sha256']['inrelease'], sha(inputs['inrelease']))
        self.assertEqual(report['verified_members'][0]['sha256'], self.fixture['member_sha256'])
        self.assertEqual(report['authority_effect'], 'NONE')
        self.assertIs(report['installed_files_verified'], False)
        self.assertIs(report['full_census_complete'], False)
        OBSERVATIONS.append({'id': self.id(), 'donor_calls': called.call_count, 'result': report})

    def test_J02_exact_old_public_consumer_rejects_same_bytes(self):
        raw = subprocess.run(['git', 'show', PARENT + ':' + DONOR_PATH], cwd=HERE,
                             capture_output=True, check=True, timeout=10).stdout
        self.assertEqual(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest(), OLD_BLOB)
        with tempfile.TemporaryDirectory(prefix='rei-join-old-donor-') as temporary:
            source = Path(temporary) / 'signed_archive_chain.py'
            source.write_bytes(raw)
            old = load('rei_saved_join_exact_old_donor', source)
            with mock.patch.dict(sys.modules, {self.consumer.DONOR_NAME: old}):
                old_consumer = load('rei_saved_join_exact_old_consumer', HERE / 'deb_member_census.py')
            self.assertIs(old_consumer.DONOR, old)
            self.assertIsNot(old, self.consumer.DONOR)
            self.assertIsNot(old.ArchivePolicy, self.consumer.ArchivePolicy)
            inputs = self.inputs(old_consumer)
            with self.assertRaisesRegex(old.ChainError, '^UNSAFE_ARCHIVE_PATH$'):
                old_consumer.verify_member_census(**inputs)
            OBSERVATIONS.append({'id': self.id(), 'old_blob': OLD_BLOB,
                                 'inrelease_sha256': sha(inputs['inrelease']),
                                 'expected_rejection': 'UNSAFE_ARCHIVE_PATH',
                                 'distinct_module_and_policy_identities_verified': True})

    def reject_before_archive(self, inputs, expected):
        with mock.patch.object(self.consumer, '_run_tool', side_effect=AssertionError('ARCHIVE_BEFORE_AUTH')):
            with self.assertRaisesRegex(self.consumer.DONOR.ChainError, expected) as caught:
                self.consumer.verify_member_census(**inputs)
        OBSERVATIONS.append({'id': self.id(), 'actual_rejection': str(caught.exception),
                             'inrelease_sha256': sha(inputs['inrelease']), 'archive_tools_called': False})

    def test_J03_corrupt_signature_rejected_by_public_consumer(self):
        inputs = self.inputs()
        changed = inputs['inrelease'].replace(b'Origin: Ubuntu', b'Origin: Ubuntx', 1)
        self.assertNotEqual(changed, inputs['inrelease'])
        inputs['inrelease'] = changed
        self.reject_before_archive(inputs, 'SIGNATURE')

    def test_J04_corrupt_payload_rejected_by_public_consumer(self):
        inputs = self.inputs()
        filename, = inputs['debs']
        original = inputs['debs'][filename]
        inputs['debs'][filename] = original[:-1] + bytes([original[-1] ^ 1])
        self.reject_before_archive(inputs, 'DEB_HASH_OR_SIZE')

    def test_J05_unsafe_package_filename_rejected_by_public_consumer(self):
        self.reject_before_archive(self.inputs(label='unsafe'), '^UNSAFE_ARCHIVE_PATH$')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture-dir', type=Path, required=True)
    parser.add_argument('--create-fixture', action='store_true')
    parser.add_argument('--only', choices=['J01'])
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    FIXTURE_DIR = args.fixture_dir.resolve()
    if args.create_fixture:
        print(json.dumps(create_fixture(FIXTURE_DIR), indent=2))
        raise SystemExit(0)
    names = sorted(name for name in JoinTests.__dict__ if name.startswith('test_J'))
    selected = [name for name in names if not args.only or name.startswith('test_' + args.only + '_')]
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(JoinTests(name) for name in selected))
    failures = [{'id': test.id(), 'traceback': text} for test, text in result.failures]
    errors = [{'id': test.id(), 'traceback': text} for test, text in result.errors]
    unsuccessful = {row['id'] for row in failures + errors} | {test.id() for test, _ in result.skipped}
    record = {'work_unit': 'REI_H1B1_SAVED_RELEASE_MEMBER_JOIN', 'scope': 'SYNTHETIC_REAL_GPG_NOT_UBUNTU_ARCHIVE',
              'tests': result.testsRun, 'selected_ids': ['__main__.JoinTests.' + name for name in selected],
              'all_methods': 5, 'unselected_methods': len(names) - len(selected),
              'passed': result.testsRun - len(unsuccessful), 'failures': len(failures), 'errors': len(errors),
              'skipped': len(result.skipped), 'not_run': len(selected) - result.testsRun,
              'successful': result.wasSuccessful() and not result.skipped and result.testsRun == len(selected),
              'failure_rows': failures, 'error_rows': errors, 'observations': OBSERVATIONS,
              'fixture_manifest_sha256': sha((FIXTURE_DIR / 'FIXTURE.json').read_bytes()),
              'old_member_and_donor_suites_counted_here': 0}
    text = json.dumps(record, indent=2) + '\n'
    if args.report:
        with args.report.open('x') as stream:
            stream.write(text)
    print(text)
    raise SystemExit(0 if record['successful'] else 1)
