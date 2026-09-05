#!/usr/bin/env python3
"""Real-GnuPG tests of the offline H1B1 trust-chain component; no Ubuntu admission."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import lzma
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
IMPLEMENTATION = HERE / 'signed_archive_chain.py'
MISSING = 'MISSING_H1B1_SIGNED_CHAIN_IMPLEMENTATION'
# GnuPG's trailing ! freezes the clock; without it, key generation can advance
# beyond the time of the next signing process. This affects fixtures only.
FAKE_TIME = str(int(datetime(2025, 1, 14, 12, tzinfo=timezone.utc).timestamp())) + '!'
PACKAGE = 'gcc-13-x86-64-linux-gnu'
VERSION = '13.3.0-6ubuntu2~24.04'
FILENAME = 'pool/main/g/gcc-13/gcc-13-x86-64-linux-gnu_13.3.0-6ubuntu2~24.04_amd64.deb'
PAYLOAD = b'H1B1 synthetic opaque package bytes; not an installed executable\n'


def digest(data):
    return hashlib.sha256(data).hexdigest()


class SignedChainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not IMPLEMENTATION.is_file():
            return
        spec = importlib.util.spec_from_file_location('rei_h1b1_signed_chain_tested', IMPLEMENTATION)
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.mod
        spec.loader.exec_module(cls.mod)
        if not shutil.which('gpg') or not shutil.which('gpgv'):
            raise RuntimeError('TEST_ENVIRONMENT_REQUIRES_REAL_GPG_AND_GPGV')
        cls.tmp = tempfile.TemporaryDirectory(prefix='rei-h1b1-gpg-fixture-')
        cls.home = Path(cls.tmp.name) / 'gnupg'
        cls.home.mkdir(mode=0o700)
        cls.gpg = ['gpg', '--batch', '--no-options', '--homedir', str(cls.home),
                   '--pinentry-mode', 'loopback', '--passphrase', '',
                   '--faked-system-time', FAKE_TIME]
        subprocess.run(cls.gpg + ['--quick-generate-key', 'REI H1B1 synthetic fixture <fixture@example.invalid>',
                                 'rsa2048', 'sign', '0'], check=True, capture_output=True, timeout=45)
        listing = subprocess.run(cls.gpg + ['--with-colons', '--list-keys'],
                                 check=True, capture_output=True, text=True, timeout=10).stdout
        cls.fingerprint = next(row.split(':')[9] for row in listing.splitlines() if row.startswith('fpr:'))
        cls.keyring = subprocess.run(cls.gpg + ['--export', cls.fingerprint],
                                    check=True, capture_output=True, timeout=10).stdout

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'tmp'):
            if shutil.which('gpgconf'):
                subprocess.run(['gpgconf', '--homedir', str(cls.home), '--kill', 'gpg-agent'],
                               capture_output=True, timeout=10, check=False)
            cls.tmp.cleanup()

    def setUp(self):
        self.assertTrue(IMPLEMENTATION.is_file(), MISSING)

    def policy(self, **changes):
        args = dict(keyring_sha256=digest(self.keyring),
                    allowed_primary_fingerprints=(self.fingerprint,),
                    suite='noble-updates', codename='noble', architecture='amd64',
                    index_name='main/binary-amd64/Packages.xz',
                    required=((PACKAGE, VERSION, 'amd64'),))
        args.update(changes)
        return self.mod.ArchivePolicy(**args)

    def stanza(self, *, filename=FILENAME, suffix='', architecture='amd64', version=VERSION):
        return (f'Package: {PACKAGE}\nVersion: {version}\nArchitecture: {architecture}\n'
                f'Filename: {filename}\nSize: {len(PAYLOAD)}\nSHA256: {digest(PAYLOAD)}\n'
                f'Description: synthetic trust-chain fixture\n continuation text\n{suffix}\n').encode()

    def bundle(self, *, plain=None, suite='noble-updates', origin='Ubuntu', date='Tue, 14 Jan 2025 12:00:00 UTC',
               extra_sha='', extra_release='', signing_time=None):
        plain = self.stanza() if plain is None else plain
        packed = lzma.compress(plain)
        release = (f'Origin: {origin}\nLabel: Ubuntu\nSuite: {suite}\nCodename: noble\n'
                   f'Date: {date}\nArchitectures: amd64 all\nComponents: main\n'
                   f'SHA256:\n {digest(packed)} {len(packed)} main/binary-amd64/Packages.xz\n'
                   f' {digest(plain)} {len(plain)} main/binary-amd64/Packages\n'
                   f'{extra_sha}{extra_release}').encode()
        args = list(self.gpg)
        if signing_time is not None:
            args[-1] = signing_time
        run = subprocess.run(args + ['--armor', '--digest-algo', 'SHA256', '--clearsign'],
                             input=release, check=False, capture_output=True, timeout=10)
        if run.returncode:
            raise RuntimeError('GPG_FIXTURE_SIGNING_FAILED: ' + run.stderr.decode('utf-8', errors='replace'))
        return run.stdout, packed

    def audit(self, signed, packed, **changes):
        args = dict(inrelease=signed, index_bytes=packed, debs={FILENAME: PAYLOAD},
                    keyring=self.keyring, policy=self.policy(), gpgv=Path(shutil.which('gpgv')))
        args.update(changes)
        return self.mod.verify_chain(**args)

    def test_valid_real_signature_and_hash_chain(self):
        signed, packed = self.bundle()
        report = self.audit(signed, packed)
        self.assertEqual(report['status'], 'PASS_H1B1_SIGNED_ARCHIVE_CHAIN_COMPONENT')
        self.assertEqual(report['authority_effect'], 'NONE')
        self.assertEqual(report['verified_packages'][0]['sha256'], digest(PAYLOAD))
        self.assertEqual(report['signing_primary_fingerprints'], [self.fingerprint])
        self.assertFalse(report['full_census_complete'])
        self.assertFalse(report['snapshot_retrieval_attested'])
        self.assertFalse(report['installed_files_verified'])
        self.assertEqual(report['key_revocation_assessment'], 'NOT_PERFORMED_BY_GPGV')
        self.assertEqual(report['input_sha256']['inrelease'], digest(signed))
        json.dumps(report, allow_nan=False)

    def test_signed_text_tamper_is_rejected(self):
        signed, packed = self.bundle()
        signed = signed.replace(b'Origin: Ubuntu', b'Origin: Ubuntx', 1)
        with self.assertRaisesRegex(self.mod.ChainError, 'SIGNATURE'):
            self.audit(signed, packed)

    def test_unsigned_release_is_rejected(self):
        _, packed = self.bundle()
        with self.assertRaisesRegex(self.mod.ChainError, 'SIGNATURE'):
            self.audit(b'Origin: Ubuntu\n', packed)

    def test_keyring_byte_pin_is_enforced(self):
        signed, packed = self.bundle()
        with self.assertRaisesRegex(self.mod.ChainError, 'KEYRING_HASH'):
            self.audit(signed, packed, policy=self.policy(keyring_sha256='0' * 64))

    def test_signer_identity_is_not_inferred_from_exit_zero(self):
        signed, packed = self.bundle()
        with self.assertRaisesRegex(self.mod.ChainError, 'SIGNER'):
            self.audit(signed, packed, policy=self.policy(allowed_primary_fingerprints=('0' * 40,)))

    def test_origin_and_suite_are_authenticated_and_checked(self):
        for changes in ({'origin': 'OtherArchive'}, {'suite': 'noble-security'}):
            with self.subTest(changes=changes):
                signed, packed = self.bundle(**changes)
                with self.assertRaisesRegex(self.mod.ChainError, 'RELEASE_IDENTITY'):
                    self.audit(signed, packed)

    def test_release_after_snapshot_is_rejected(self):
        signed, packed = self.bundle(date='Thu, 16 Jan 2025 12:00:00 UTC')
        with self.assertRaisesRegex(self.mod.ChainError, 'RELEASE_AFTER_SNAPSHOT'):
            self.audit(signed, packed)

    def test_signature_after_snapshot_is_rejected(self):
        future = str(int(datetime(2025, 1, 16, 12, tzinfo=timezone.utc).timestamp()))
        signed, packed = self.bundle(signing_time=future)
        with self.assertRaisesRegex(self.mod.ChainError, 'SIGNATURE_AFTER_SNAPSHOT'):
            self.audit(signed, packed)

    def test_index_byte_tamper_is_rejected_before_parsing(self):
        signed, packed = self.bundle()
        with self.assertRaisesRegex(self.mod.ChainError, 'INDEX_HASH_OR_SIZE'):
            self.audit(signed, packed + b'x')

    def test_duplicate_release_index_is_rejected(self):
        signed, packed = self.bundle(extra_sha=' ' + '0' * 64 + ' 7 main/binary-amd64/Packages.xz\n')
        with self.assertRaisesRegex(self.mod.ChainError, 'DUPLICATE_RELEASE_INDEX'):
            self.audit(signed, packed)

    def test_duplicate_deb822_field_is_rejected(self):
        signed, packed = self.bundle(plain=self.stanza(suffix='sHa256: ' + digest(PAYLOAD)))
        with self.assertRaisesRegex(self.mod.ChainError, 'DUPLICATE_FIELD'):
            self.audit(signed, packed)

    def test_duplicate_package_provider_is_rejected(self):
        signed, packed = self.bundle(plain=self.stanza() + self.stanza())
        with self.assertRaisesRegex(self.mod.ChainError, 'DUPLICATE_PACKAGE'):
            self.audit(signed, packed)

    def test_exact_package_version_is_required(self):
        signed, packed = self.bundle(plain=self.stanza(version=VERSION + '.1'))
        with self.assertRaisesRegex(self.mod.ChainError, 'PROVIDER_UNRESOLVED'):
            self.audit(signed, packed)

    def test_package_payload_hash_and_size_are_enforced(self):
        signed, packed = self.bundle()
        for bad in (PAYLOAD + b'x', b'X' + PAYLOAD[1:]):
            with self.subTest(size=len(bad)):
                with self.assertRaisesRegex(self.mod.ChainError, 'DEB_HASH_OR_SIZE'):
                    self.audit(signed, packed, debs={FILENAME: bad})

    def test_noncanonical_package_path_is_rejected(self):
        for path in ('../package.deb', '/pool/package.deb', 'pool/a/../package.deb', 'pool/%2e%2e/package.deb'):
            with self.subTest(path=path):
                signed, packed = self.bundle(plain=self.stanza(filename=path))
                with self.assertRaisesRegex(self.mod.ChainError, 'UNSAFE_ARCHIVE_PATH'):
                    self.audit(signed, packed)

    def test_missing_or_extra_payload_is_rejected(self):
        signed, packed = self.bundle()
        for debs in ({}, {FILENAME: PAYLOAD, 'pool/extra.deb': b'x'}):
            with self.subTest(paths=sorted(debs)):
                with self.assertRaisesRegex(self.mod.ChainError, 'PAYLOAD_SET'):
                    self.audit(signed, packed, debs=debs)

    def test_authenticated_decompression_is_bounded(self):
        signed, packed = self.bundle(plain=self.stanza(suffix='X-Padding: ' + 'a' * 4096))
        with self.assertRaisesRegex(self.mod.ChainError, 'DECOMPRESSED_INDEX_LIMIT'):
            self.audit(signed, packed, policy=self.policy(max_index_bytes=1024))

    def test_release_field_duplicate_is_rejected(self):
        signed, packed = self.bundle(extra_release='Origin: Ubuntu\n')
        with self.assertRaisesRegex(self.mod.ChainError, 'DUPLICATE_FIELD'):
            self.audit(signed, packed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--expect-red', action='store_true')
    parser.add_argument('--report', required=True)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SignedChainTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    is_red = (result.testsRun == 18 and len(result.failures) == 18 and not result.errors
              and not result.skipped and all(MISSING in text for _, text in result.failures))
    record = dict(tests=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                  skipped=len(result.skipped), expected_implementation_absent_red=is_red,
                  successful=result.wasSuccessful(), fixture='SYNTHETIC_REAL_GPG_NOT_UBUNTU_ARCHIVE',
                  ubuntu_archive_admitted=False, native_runtime='NOT_RUN')
    Path(args.report).write_text(json.dumps(record, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    raise SystemExit(0 if (is_red if args.expect_red else result.wasSuccessful()) else 1)
