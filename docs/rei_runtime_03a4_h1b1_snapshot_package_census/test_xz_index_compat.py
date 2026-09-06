#!/usr/bin/env python3
"""XZ file compatibility: frozen public synthetic fixture, no network or install.

--create-fixture creates public bytes once in a new directory. Normal runs reuse
them; --only X01 observes an actual public-consumer missing-feature RED.
"""
import argparse
from dataclasses import asdict
import hashlib
import importlib.util
import json
import lzma
from pathlib import Path
import random
import sys
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
FIXTURE_DIR = None


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha(data):
    return hashlib.sha256(data).hexdigest()


def create_fixture(directory):
    helper = load('rei_xz_public_fixture_helpers', 'test_deb_member_census.py')
    cls = helper.FIXTURE.SignedChainTests
    cls.setUpClass()
    try:
        fixture = cls('test_valid_real_signature_and_hash_chain')
        payload = helper.deb_bytes()
        filename = helper.FIXTURE.FILENAME
        plain = (f'Package: {helper.FIXTURE.PACKAGE}\nVersion: {helper.FIXTURE.VERSION}\n'
                 f'Architecture: amd64\nFilename: {filename}\nSize: {len(payload)}\n'
                 f'SHA256: {sha(payload)}\n\n').encode()
        packed = lzma.compress(plain) + lzma.compress(b'')
        with mock.patch.object(helper.FIXTURE.lzma, 'compress', return_value=packed):
            signed, _ = fixture.bundle(plain=plain)
            bad_plain_signed, _ = fixture.bundle(plain=plain + b'\n')
        files = {'InRelease': signed, 'bad-plain.InRelease': bad_plain_signed,
                 'Packages.xz': packed, 'package.deb': payload,
                 'public-keyring.gpg': fixture.keyring}
        directory.mkdir(parents=True, exist_ok=False)
        for name, data in files.items():
            (directory / name).write_bytes(data)
        record = {'scope': 'SYNTHETIC_PUBLIC_INPUTS_NOT_UBUNTU', 'policy': asdict(fixture.policy()),
                  'filename': filename, 'member': helper.MEMBER, 'member_sha256': sha(helper.CONTENT),
                  'files': {name: {'sha256': sha(data), 'size': len(data)} for name, data in files.items()},
                  'private_keys_included': False}
        (directory / 'FIXTURE.json').write_text(json.dumps(record, indent=2) + '\n')
    finally:
        cls.tearDownClass()


class XZTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.consumer = load('rei_xz_current_consumer', 'deb_member_census.py')
        cls.donor = cls.consumer.DONOR
        cls.fixture = json.loads((FIXTURE_DIR / 'FIXTURE.json').read_text())
        for name, row in cls.fixture['files'].items():
            data = (FIXTURE_DIR / name).read_bytes()
            assert (sha(data), len(data)) == (row['sha256'], row['size'])

    def inputs(self):
        fields = dict(self.fixture['policy'])
        fields['allowed_primary_fingerprints'] = tuple(fields['allowed_primary_fingerprints'])
        fields['required'] = tuple(map(tuple, fields['required']))
        policy = self.consumer.ArchivePolicy(**fields)
        self.assertIs(type(policy), self.donor.ArchivePolicy)
        return dict(inrelease=(FIXTURE_DIR / 'InRelease').read_bytes(),
                    index_bytes=(FIXTURE_DIR / 'Packages.xz').read_bytes(),
                    debs={self.fixture['filename']: (FIXTURE_DIR / 'package.deb').read_bytes()},
                    keyring=(FIXTURE_DIR / 'public-keyring.gpg').read_bytes(), policy=policy,
                    gpgv=Path('/usr/bin/gpgv'),
                    required_members=((self.fixture['filename'], self.fixture['member'],
                                       self.fixture['member_sha256']),))

    def reject(self, packed, code='COMPRESSED_INDEX'):
        with self.assertRaisesRegex(self.donor.ChainError, code):
            self.donor._unpack_index(packed, 1024)

    def test_X01_public_consumer_accepts_data_and_empty_stream(self):
        with mock.patch.object(self.donor, 'verify_chain', wraps=self.donor.verify_chain) as called:
            try:
                actual = self.consumer.verify_member_census(**self.inputs())
            except self.donor.ChainError as error:
                if str(error) == 'COMPRESSED_INDEX_TRUNCATED_OR_TRAILING':
                    self.fail('MISSING_XZ_MULTI_STREAM:' + str(error))
                raise
        self.assertEqual(called.call_count, 1)
        self.assertEqual(actual['status'], 'PASS_H1B1_AUTHENTICATED_DEB_MEMBERS')
        self.assertEqual(actual['verified_members'][0]['sha256'], self.fixture['member_sha256'])
        self.assertEqual(actual['authority_effect'], 'NONE')
        self.assertIs(actual['installed_files_verified'], False)
        self.assertIs(actual['full_census_complete'], False)

    def test_X02_nonempty_streams_contribute_in_order(self):
        self.assertEqual(self.donor._unpack_index(lzma.compress(b'abc') + lzma.compress(b'def'), 6), b'abcdef')

    def test_X03_legal_interstream_and_final_padding(self):
        packed = lzma.compress(b'a') + b'\0' * 4 + lzma.compress(b'b') + b'\0' * 8
        self.assertEqual(self.donor._unpack_index(packed, 2), b'ab')

    def test_X04_misaligned_padding_rejected(self):
        for count in (1, 2, 3, 5, 6, 7):
            for suffix in (b'', lzma.compress(b'b')):
                with self.subTest(id=f'padding-{count}-followed-{bool(suffix)}'):
                    self.reject(lzma.compress(b'a') + b'\0' * count + suffix)

    def test_X05_truncated_first_stream_rejected(self):
        self.reject(lzma.compress(b'a')[:-1])

    def test_X06_truncated_later_stream_rejected(self):
        self.reject(lzma.compress(b'a') + lzma.compress(b'b')[:-4])

    def test_X07_corrupt_later_stream_rejected(self):
        later = bytearray(lzma.compress(b'b'))
        later[-12] ^= 1
        self.reject(lzma.compress(b'a') + later)

    def test_X08_arbitrary_trailing_bytes_rejected(self):
        for suffix in (b'garbage', b'\0' * 4 + b'junk', b'\0\0\0X'):
            with self.subTest(id=suffix.hex()):
                self.reject(lzma.compress(b'a') + suffix)

    def test_X09_limit_applies_to_all_streams(self):
        with self.assertRaisesRegex(self.donor.ChainError, 'DECOMPRESSED_INDEX_LIMIT'):
            self.donor._unpack_index(lzma.compress(b'abc') + lzma.compress(b'def'), 5)

    def test_X10_exact_limit_allows_empty_later_stream(self):
        self.assertEqual(self.donor._unpack_index(lzma.compress(b'abc') + lzma.compress(b''), 3), b'abc')

    def test_X11_empty_or_padding_only_file_rejected(self):
        for packed in (b'', b'\0' * 4):
            with self.subTest(id=packed.hex() or 'empty'):
                self.reject(packed)

    def test_X12_compressed_chunk_boundary_and_total_output(self):
        plain = random.Random(71).randbytes(200000)
        packed = lzma.compress(plain) + lzma.compress(b'end')
        self.assertEqual(self.donor._unpack_index(packed, len(plain) + 3), plain + b'end')

    def test_X13_compressed_pin_still_precedes_unpack(self):
        args = self.inputs()
        args['index_bytes'] += lzma.compress(b'')
        with mock.patch.object(self.donor, '_unpack_index', wraps=self.donor._unpack_index) as unpack:
            with self.assertRaisesRegex(self.donor.ChainError, 'INDEX_HASH_OR_SIZE'):
                self.consumer.verify_member_census(**args)
        self.assertEqual(unpack.call_count, 0)

    def test_X14_signature_still_precedes_unpack(self):
        args = self.inputs()
        args['inrelease'] = args['inrelease'].replace(b'Origin: Ubuntu', b'Origin: Ubuntx', 1)
        with mock.patch.object(self.donor, '_unpack_index', wraps=self.donor._unpack_index) as unpack:
            with self.assertRaisesRegex(self.donor.ChainError, 'SIGNATURE'):
                self.consumer.verify_member_census(**args)
        self.assertEqual(unpack.call_count, 0)

    def test_X15_plain_index_pin_checks_complete_decoded_file(self):
        args = self.inputs()
        args['inrelease'] = (FIXTURE_DIR / 'bad-plain.InRelease').read_bytes()
        with self.assertRaisesRegex(self.donor.ChainError, 'UNCOMPRESSED_INDEX_HASH_OR_SIZE'):
            self.consumer.verify_member_census(**args)

    def test_X16_non_xz_format_rejected(self):
        self.reject(lzma.compress(b'a', format=lzma.FORMAT_ALONE))


class RecordedResult(unittest.TextTestResult):
    def startTest(self, test):
        self.test_ids.append(test.id())
        super().startTest(test)

    def addSubTest(self, test, subtest, err):
        self.subcases.append({'id': str(subtest), 'status': 'PASS' if err is None else 'FAIL'})
        super().addSubTest(test, subtest, err)

    def __init__(self, *args):
        super().__init__(*args)
        self.test_ids, self.subcases = [], []


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--fixture-dir', required=True, type=Path)
    parser.add_argument('--create-fixture', action='store_true')
    parser.add_argument('--report', type=Path)
    parser.add_argument('--only')
    args = parser.parse_args()
    if args.create_fixture:
        create_fixture(args.fixture_dir)
        raise SystemExit(0)
    if args.report is None:
        parser.error('--report is required for tests')
    FIXTURE_DIR = args.fixture_dir
    names = sorted(name for name in XZTests.__dict__ if name.startswith('test_'))
    selected = [name for name in names if args.only is None or name.startswith('test_' + args.only + '_')]
    if not selected:
        parser.error('unknown --only test ID')
    result = unittest.TextTestRunner(verbosity=2, resultclass=RecordedResult).run(
        unittest.TestSuite(XZTests(name) for name in selected))
    record = {'tests': result.testsRun, 'test_ids': result.test_ids,
              'failures': len(result.failures), 'errors': len(result.errors), 'skipped': len(result.skipped),
              'not_run': len(names) - len(selected), 'successful': result.wasSuccessful(),
              'subcases': result.subcases, 'subcase_count': len(result.subcases),
              'test_source_sha256': sha(Path(__file__).read_bytes()),
              'fixture_manifest_sha256': sha((FIXTURE_DIR / 'FIXTURE.json').read_bytes()),
              'scope': 'XZ_FORMAT_AND_SYNTHETIC_PUBLIC_CHAIN_NOT_REAL_UBUNTU'}
    args.report.write_text(json.dumps(record, indent=2) + '\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
