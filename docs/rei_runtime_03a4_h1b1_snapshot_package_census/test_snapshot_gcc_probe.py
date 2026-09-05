#!/usr/bin/env python3
"""Frozen tests for the read-only DEB-member extension of H1B1.

Fixtures are real ar/tar DEB envelopes with synthetic payloads. They are never
installed or executed. Ubuntu authenticity is tested separately by the live probe.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import tarfile
import unittest

SOURCE = Path(__file__).with_name('probe_snapshot_gcc.py')
MEMBER = 'usr/bin/example'
PAYLOAD = b'NOT_AN_EXECUTABLE\n'
IDENTITY = ('example', '1.0-1', 'amd64')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def tar_bytes(rows):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w') as archive:
        for name, payload, kind in rows:
            entry = tarfile.TarInfo(name)
            entry.mtime = 0
            entry.mode = 0o755
            if kind == 'symlink':
                entry.type = tarfile.SYMTYPE
                entry.linkname = 'other'
                archive.addfile(entry)
            else:
                entry.size = len(payload)
                archive.addfile(entry, io.BytesIO(payload))
    return gzip.compress(stream.getvalue(), mtime=0)


def deb_bytes(rows=None, identity=IDENTITY):
    if rows is None:
        rows = [('./' + MEMBER, PAYLOAD, 'regular')]
    control = ('Package: %s\nVersion: %s\nArchitecture: %s\nMaintainer: Test <test@example.invalid>\nDescription: fixture\n' % identity).encode()
    entries = [('debian-binary', b'2.0\n'),
               ('control.tar.gz', tar_bytes([('./control', control, 'regular')])),
               ('data.tar.gz', tar_bytes(rows))]
    result = b'!<arch>\n'
    for name, payload in entries:
        header = f'{name + "/":<16}{0:<12}{0:<6}{0:<6}{100644:<8}{len(payload):<10}`\n'.encode('ascii')
        assert len(header) == 60
        result += header + payload + (b'\n' if len(payload) % 2 else b'')
    return result


class MemberProbeTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SOURCE.is_file(), 'MISSING_H1B1_REAL_MEMBER_PROBE')
        spec = importlib.util.spec_from_file_location('rei_probe_under_test', SOURCE)
        self.mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = self.mod
        spec.loader.exec_module(self.mod)
        self.assertIsNotNone(shutil.which('dpkg-deb'), 'DPKG_DEB_RUNTIME_REQUIRED')

    def inspect(self, payload=None, **changes):
        payload = deb_bytes() if payload is None else payload
        args = dict(expected_deb_sha256=sha(payload), expected_identity=IDENTITY,
                    member_path=MEMBER, expected_member_sha256=sha(PAYLOAD),
                    dpkg_deb=Path(shutil.which('dpkg-deb')))
        args.update(changes)
        return self.mod.inspect_member(payload, **args)

    def test_regular_member_control_and_hash(self):
        report = self.inspect()
        self.assertEqual(report['status'], 'PASS_DEB_MEMBER_BYTES_ONLY')
        self.assertEqual(report['member_sha256'], sha(PAYLOAD))
        self.assertEqual(report['member_size'], len(PAYLOAD))
        self.assertEqual(tuple(report['package_identity']), IDENTITY)
        self.assertFalse(report['installed_files_verified'])
        self.assertFalse(report['payload_executed'])

    def test_wrong_deb_hash_is_rejected_before_tool(self):
        with self.assertRaisesRegex(self.mod.ProbeError, 'DEB_PIN_MISMATCH'):
            self.inspect(expected_deb_sha256='0' * 64, dpkg_deb=Path('/not/a/tool'))

    def test_control_identity_mismatch(self):
        with self.assertRaisesRegex(self.mod.ProbeError, 'CONTROL_IDENTITY_MISMATCH'):
            self.inspect(deb_bytes(identity=('other', '1.0-1', 'amd64')))

    def test_missing_member(self):
        with self.assertRaisesRegex(self.mod.ProbeError, 'MEMBER_CARDINALITY'):
            self.inspect(deb_bytes(rows=[('./usr/bin/other', PAYLOAD, 'regular')]))

    def test_wrong_member_hash(self):
        with self.assertRaisesRegex(self.mod.ProbeError, 'MEMBER_HASH_MISMATCH'):
            self.inspect(expected_member_sha256='0' * 64)

    def test_symlink_is_not_a_regular_member(self):
        with self.assertRaisesRegex(self.mod.ProbeError, 'MEMBER_NOT_REGULAR'):
            self.inspect(deb_bytes(rows=[('./' + MEMBER, b'', 'symlink')]))

    def test_duplicate_member_is_rejected(self):
        rows = [('./' + MEMBER, PAYLOAD, 'regular'), (MEMBER, PAYLOAD, 'regular')]
        with self.assertRaisesRegex(self.mod.ProbeError, 'MEMBER_CARDINALITY'):
            self.inspect(deb_bytes(rows=rows))

    def test_noncanonical_member_request(self):
        for name in ('../usr/bin/example', '/usr/bin/example', 'usr//bin/example', 'usr/./bin/example'):
            with self.subTest(name=name), self.assertRaisesRegex(self.mod.ProbeError, 'MEMBER_PATH_INVALID'):
                self.inspect(member_path=name)

    def test_decompression_output_limit(self):
        with self.assertRaisesRegex(self.mod.ProbeError, 'TAR_OUTPUT_LIMIT_OR_TOOL_FAILURE'):
            self.inspect(max_tar_bytes=512)

    def test_snapshot_url_policy(self):
        prefix = 'https://snapshot.ubuntu.com/ubuntu/20250115T120000Z/'
        self.assertEqual(self.mod.validate_url(prefix + 'dists/noble-updates/InRelease'),
                         prefix + 'dists/noble-updates/InRelease')
        for url in (prefix.replace('https:', 'http:') + 'x',
                    prefix.replace('snapshot.ubuntu.com', 'example.invalid') + 'x',
                    prefix + '../x', prefix + 'x?token=secret', prefix + 'x#fragment',
                    prefix.replace('ubuntu.com/', 'ubuntu.com:8443/') + 'x'):
            with self.subTest(url=url), self.assertRaisesRegex(self.mod.ProbeError, 'SNAPSHOT_URL_REJECTED'):
                self.mod.validate_url(url)

    def test_malformed_deb_is_not_accepted_as_member(self):
        with self.assertRaisesRegex(self.mod.ProbeError, 'TAR_OUTPUT_LIMIT_OR_TOOL_FAILURE'):
            self.inspect(b'this is not a DEB')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--expect-missing', action='store_true')
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MemberProbeTests))
    missing = (result.testsRun == 11 and len(result.failures) == 11 and not result.errors
               and not result.skipped and all('MISSING_H1B1_REAL_MEMBER_PROBE' in text for _, text in result.failures))
    record = dict(tests=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                  skipped=len(result.skipped), successful=result.wasSuccessful(),
                  expected_missing=missing, actual_ubuntu_probe=False)
    args.report.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(json.dumps(record, sort_keys=True))
    raise SystemExit(0 if (missing if args.expect_missing else result.wasSuccessful()) else 1)
