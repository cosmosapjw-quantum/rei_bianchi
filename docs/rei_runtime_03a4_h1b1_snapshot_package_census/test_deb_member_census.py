#!/usr/bin/env python3
"""Frozen behavioral tests; real GnuPG, synthetic trust root, no installation.

CLI: no arguments runs GREEN-only unittest accounting and prints JSON.
--report PATH additionally saves that JSON; --evidence-dir NEW_PATH preserves
public signed fixtures and actual consumer/error reports, never private keys.
The default exit is nonzero for any failure/error/skip; there is no RED mode.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
MISSING = 'MISSING_H1B1_DEB_MEMBER_IMPLEMENTATION'
MEMBER = 'usr/bin/witness'
CONTENT = b'REI authenticated member fixture; never executed\n'
EVIDENCE = None
CASES = []


def load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


DONOR = load('rei_h1b1_deb_member_donor', HERE / 'signed_archive_chain.py')
FIXTURE = load('rei_h1b1_deb_member_fixture', HERE / 'test_signed_archive_chain.py')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def tar_bytes(entries):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w', format=tarfile.USTAR_FORMAT) as archive:
        for name, kind, data in entries:
            info = tarfile.TarInfo(name)
            info.type = kind
            if kind == tarfile.REGTYPE:
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
            else:
                info.linkname = 'usr/bin/witness' if kind in (tarfile.SYMTYPE, tarfile.LNKTYPE) else ''
                archive.addfile(info)
    return stream.getvalue()


def ar_bytes(entries):
    """Test-fixture serializer only; the consumer must use dpkg-deb for DEBs."""
    result = bytearray(b'!<arch>\n')
    for name, data in entries:
        header = f'{name:<16}{0:<12}{0:<6}{0:<6}{100644:<8}{len(data):<10}`\n'.encode('ascii')
        assert len(header) == 60
        result.extend(header + data + (b'\n' if len(data) % 2 else b''))
    return bytes(result)


def control_bytes(**changes):
    fields = dict(Package=FIXTURE.PACKAGE, Version=FIXTURE.VERSION, Architecture='amd64',
                  Maintainer='Fixture <fixture@example.invalid>', Description='synthetic DEB')
    fields.update(changes)
    return ''.join(f'{k}: {v}\n' for k, v in fields.items()).encode()


def deb_bytes(entries=None, control=None, data_name='data.tar.gz'):
    entries = entries if entries is not None else [('./' + MEMBER, tarfile.REGTYPE, CONTENT)]
    ctl = tar_bytes([('./control', tarfile.REGTYPE, control or control_bytes())])
    return ar_bytes([('debian-binary', b'2.0\n'), ('control.tar.gz', gzip.compress(ctl, mtime=0)),
                     (data_name, gzip.compress(tar_bytes(entries), mtime=0))])


class MemberTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        FIXTURE.SignedChainTests.setUpClass()
        cls.fixture = FIXTURE.SignedChainTests('test_valid_real_signature_and_hash_chain')
        cls.consumer = (load('rei_h1b1_deb_member_tested', HERE / 'deb_member_census.py')
                        if (HERE / 'deb_member_census.py').is_file() else None)

    @classmethod
    def tearDownClass(cls):
        FIXTURE.SignedChainTests.tearDownClass()

    def implementation(self):
        self.assertIsNotNone(self.consumer, MISSING)
        return self.consumer

    def inputs(self, deb):
        stanza = (f'Package: {FIXTURE.PACKAGE}\nVersion: {FIXTURE.VERSION}\nArchitecture: amd64\n'
                  f'Filename: {FIXTURE.FILENAME}\nSize: {len(deb)}\nSHA256: {sha(deb)}\n\n').encode()
        signed, packed = self.fixture.bundle(plain=stanza)
        # The fixture deliberately loads a different donor module identity.
        policy = DONOR.ArchivePolicy(**asdict(self.fixture.policy()))
        return dict(inrelease=signed, index_bytes=packed, keyring=self.fixture.keyring,
                    policy=policy, gpgv=Path(shutil.which('gpgv')), debs={FIXTURE.FILENAME: deb})

    def audit(self, deb, *, required=None, **changes):
        consumer = self.implementation()
        inputs = self.inputs(deb)
        inputs.update(changes)
        required = required if required is not None else ((FIXTURE.FILENAME, MEMBER, sha(CONTENT)),)
        record = {'test_id': self.id(), 'subcase': len(CASES) + 1,
                  'fixture': 'SYNTHETIC_REAL_GPG_NOT_UBUNTU_ARCHIVE',
                  'input_sha256': {k: sha(inputs[k]) for k in ('inrelease', 'index_bytes', 'keyring')},
                  'deb_sha256': sha(deb), 'required_members': required}
        CASES.append(record)
        case_path = None
        if EVIDENCE is not None:
            case_path = EVIDENCE / f'case-{len(CASES):03d}'
            case_path.mkdir()
            for key, name in [('inrelease', 'InRelease'), ('index_bytes', 'Packages.xz'),
                              ('keyring', 'public-keyring.gpg')]:
                (case_path / name).write_bytes(inputs[key])
            (case_path / 'package.deb').write_bytes(deb)
            (case_path / 'policy.json').write_text(json.dumps(asdict(inputs['policy']), indent=2) + '\n')
        try:
            report = consumer.verify_member_census(**inputs, required_members=required)
            record.update(outcome='PASS', result=report)
            return report
        except (consumer.MemberError, DONOR.ChainError) as error:
            record.update(outcome='REJECTED', error_type=type(error).__name__,
                          error=str(error), evidence=getattr(error, 'evidence', {}))
            raise
        finally:
            if case_path is not None:
                (case_path / 'result.json').write_text(json.dumps(record, indent=2, allow_nan=False) + '\n')

    def test_D01_valid_signed_regular_member(self):
        consumer = self.implementation()
        self.assertIs(consumer.ArchivePolicy, DONOR.ArchivePolicy)
        entries = [('./', tarfile.DIRTYPE, b''), ('./' + MEMBER, tarfile.REGTYPE, CONTENT),
                   ('./usr/bin/unrelated-link', tarfile.SYMTYPE, b'')]
        with mock.patch.object(consumer.DONOR, 'verify_chain', wraps=DONOR.verify_chain) as verify:
            result = self.audit(deb_bytes(entries))
        self.assertEqual(verify.call_count, 1)
        self.assertEqual(result['status'], 'PASS_H1B1_AUTHENTICATED_DEB_MEMBERS')
        self.assertEqual(result['signed_chain']['status'], 'PASS_H1B1_SIGNED_ARCHIVE_CHAIN_COMPONENT')
        self.assertEqual(result['authority_effect'], 'NONE')
        self.assertIs(result['installed_files_verified'], False)
        self.assertIs(result['full_census_complete'], False)
        row, = result['verified_members']
        self.assertEqual((row['archive_filename'], row['member_path'], row['sha256'], row['size']),
                         (FIXTURE.FILENAME, MEMBER, sha(CONTENT), len(CONTENT)))
        self.assertTrue(result['tool_runs'])
        for command in result['tool_runs']:
            self.assertEqual(command['exit_code'], 0)
            self.assertIs(command['timed_out'], False)
        self.assertEqual(len(result['tools']['dpkg_deb']['sha256']), 64)
        json.dumps(result, allow_nan=False)

    def test_D02_signed_non_deb_rejected(self):
        consumer = self.implementation()
        with self.assertRaisesRegex(consumer.MemberError, 'DEB_TOOL_FAILED'):
            self.audit(b'validly signed bytes but not a Debian archive\n')

    def test_D03_control_identity_mismatch(self):
        consumer = self.implementation()
        for changes in ({'Package': 'other'}, {'Version': '0.1'}, {'Architecture': 'all'}):
            with self.subTest(changes=changes):
                with self.assertRaisesRegex(consumer.MemberError, 'CONTROL_IDENTITY_MISMATCH'):
                    self.audit(deb_bytes(control=control_bytes(**changes)))

    def test_D04_member_hash_mismatch(self):
        consumer = self.implementation()
        with self.assertRaisesRegex(consumer.MemberError, 'MEMBER_HASH_MISMATCH'):
            self.audit(deb_bytes(), required=((FIXTURE.FILENAME, MEMBER, '0' * 64),))

    def test_D05_selected_nonregular_types(self):
        consumer = self.implementation()
        for kind in (tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.DIRTYPE, tarfile.FIFOTYPE):
            with self.subTest(kind=kind):
                with self.assertRaisesRegex(consumer.MemberError, 'MEMBER_NOT_REGULAR'):
                    self.audit(deb_bytes([(MEMBER, kind, b'')]))

    def test_D06_normalized_duplicate_selected_member(self):
        consumer = self.implementation()
        for second in (MEMBER, './' + MEMBER, '././' + MEMBER):
            with self.subTest(second=second):
                with self.assertRaisesRegex(consumer.MemberError, 'DUPLICATE_MEMBER'):
                    self.audit(deb_bytes([(MEMBER, tarfile.REGTYPE, CONTENT),
                                         (second, tarfile.REGTYPE, CONTENT)]))

    def test_D07_signature_tamper_stops_before_archive_tools(self):
        consumer = self.implementation()
        inputs = self.inputs(deb_bytes())
        inputs['inrelease'] = inputs['inrelease'].replace(b'Origin: Ubuntu', b'Origin: Ubuntx', 1)
        with mock.patch.object(consumer, '_run_tool', side_effect=AssertionError('ARCHIVE_BEFORE_AUTH')):
            with self.assertRaisesRegex(DONOR.ChainError, 'SIGNATURE'):
                self.audit(deb_bytes(), **inputs)

    def test_I01_fixture_module_policy_identity(self):
        inputs = self.inputs(deb_bytes())
        self.assertIsNot(type(self.fixture.policy()), DONOR.ArchivePolicy)
        self.assertIs(type(inputs['policy']), DONOR.ArchivePolicy)
        report = DONOR.verify_chain(**inputs)
        self.assertEqual(report['status'], 'PASS_H1B1_SIGNED_ARCHIVE_CHAIN_COMPONENT')
        with self.assertRaisesRegex(DONOR.ChainError, 'POLICY_TYPE'):
            DONOR.verify_chain(**dict(inputs, policy=self.fixture.policy()))

    def test_E01_path_rejections_and_leading_dot_acceptance(self):
        consumer = self.implementation()
        for path in ('/usr/bin/witness', '../witness', 'usr/../witness',
                     'usr//bin/witness', 'usr/./bin/witness', 'usr\\bin\\witness'):
            with self.subTest(path=path):
                with self.assertRaisesRegex(consumer.MemberError, 'UNSAFE_MEMBER_PATH'):
                    self.audit(deb_bytes([(path, tarfile.REGTYPE, CONTENT)]))
        result = self.audit(deb_bytes([('././' + MEMBER, tarfile.REGTYPE, CONTENT)]))
        self.assertEqual(result['verified_members'][0]['member_path'], MEMBER)

    def test_E02_missing_member_and_invalid_requests(self):
        consumer = self.implementation()
        with self.assertRaisesRegex(consumer.MemberError, 'MEMBER_MISSING'):
            self.audit(deb_bytes([('usr/bin/other', tarfile.REGTYPE, CONTENT)]))
        for request in ((), ((FIXTURE.FILENAME, './' + MEMBER, sha(CONTENT)),),
                        ((FIXTURE.FILENAME, MEMBER, 'bad'),),
                        ((FIXTURE.FILENAME, MEMBER, sha(CONTENT)),) * 2,
                        (('pool/absent.deb', MEMBER, sha(CONTENT)),)):
            with self.subTest(request=request):
                with self.assertRaisesRegex(consumer.MemberError, 'REQUIRED_MEMBER'):
                    self.audit(deb_bytes(), required=request)

    def test_E03_duplicate_or_missing_control(self):
        consumer = self.implementation()
        for entries in ([], [('control', tarfile.REGTYPE, control_bytes()),
                             ('./control', tarfile.REGTYPE, control_bytes())]):
            with self.subTest(count=len(entries)):
                archive = ar_bytes([('debian-binary', b'2.0\n'),
                                    ('control.tar.gz', gzip.compress(tar_bytes(entries), mtime=0)),
                                    ('data.tar.gz', gzip.compress(tar_bytes([(MEMBER, tarfile.REGTYPE, CONTENT)]), mtime=0))])
                with self.assertRaisesRegex(consumer.MemberError, 'MEMBER_MISSING|DUPLICATE_MEMBER'):
                    self.audit(archive)

    def test_E04_real_tool_compression_formats_and_unsupported(self):
        consumer = self.implementation()
        with tempfile.TemporaryDirectory(prefix='rei-deb-format-fixture-') as temporary:
            root = Path(temporary) / 'pkg'
            (root / 'DEBIAN').mkdir(parents=True)
            (root / 'DEBIAN/control').write_bytes(control_bytes())
            (root / 'usr/bin').mkdir(parents=True)
            (root / MEMBER).write_bytes(CONTENT)
            for kind in ('none', 'gzip', 'xz', 'zstd'):
                with self.subTest(compression=kind):
                    target = Path(temporary) / (kind + '.deb')
                    argv = [shutil.which('dpkg-deb'), '--root-owner-group', '-Z' + kind,
                            '--build', str(root), str(target)]
                    start = time.monotonic()
                    built = subprocess.run(argv, capture_output=True, timeout=20)
                    self.assertEqual(built.returncode, 0, built.stderr)
                    report = self.audit(target.read_bytes())
                    CASES[-1]['format_build'] = {'argv': argv, 'exit_code': built.returncode,
                                               'timed_out': False, 'elapsed_seconds': time.monotonic() - start,
                                               'stdout': built.stdout.decode(), 'stderr': built.stderr.decode(),
                                               'compression': kind}
                    self.assertEqual(report['verified_members'][0]['sha256'], sha(CONTENT))
        with self.assertRaisesRegex(consumer.MemberError, 'DEB_TOOL_FAILED'):
            self.audit(deb_bytes(data_name='data.tar.zzz'))

    def test_R01_decompressed_tar_output_limit(self):
        consumer = self.implementation()
        with self.assertRaisesRegex(consumer.MemberError, 'TOOL_STDOUT_LIMIT'):
            self.audit(deb_bytes(), limits=consumer.MemberLimits(max_tar_bytes=1024))

    def test_R02_member_size_and_count_limits(self):
        consumer = self.implementation()
        with self.assertRaisesRegex(consumer.MemberError, 'MEMBER_SIZE_LIMIT'):
            self.audit(deb_bytes([(MEMBER, tarfile.REGTYPE, b'x' * 8192)]),
                       limits=consumer.MemberLimits(max_member_bytes=4096))
        entries = [(MEMBER, tarfile.REGTYPE, CONTENT), ('usr/share/one', tarfile.REGTYPE, b'1')]
        with self.assertRaisesRegex(consumer.MemberError, 'MEMBER_COUNT_LIMIT'):
            self.audit(deb_bytes(entries), limits=consumer.MemberLimits(max_members=1))

    def test_R03_real_subprocess_output_and_timeout_limits(self):
        consumer = self.implementation()
        for code, expected, seconds in [("import sys;sys.stderr.write('x'*65536)", 'TOOL_STDERR_LIMIT', 2.0),
                                        ("import time;time.sleep(2)", 'TOOL_TIMEOUT', 0.1)]:
            with self.subTest(expected=expected):
                runs = []
                with self.assertRaisesRegex(consumer.MemberError, expected):
                    consumer._run_tool([sys.executable, '-c', code], max_stdout=4096,
                                       max_stderr=1024, timeout=seconds, runs=runs)
                self.assertEqual(len(runs), 1)
                self.assertEqual(runs[0]['timed_out'], expected == 'TOOL_TIMEOUT')


class Accounting(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rows = []
        self.subcases = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.rows.append({'id': test.id(), 'outcome': 'PASS'})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.rows.append({'id': test.id(), 'outcome': 'FAIL', 'detail': str(err[1])})

    def addError(self, test, err):
        super().addError(test, err)
        self.rows.append({'id': test.id(), 'outcome': 'ERROR', 'detail': str(err[1])})

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        self.subcases.append({'id': subtest.id(), 'outcome': 'PASS' if err is None else 'FAIL',
                              'detail': None if err is None else str(err[1])})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--evidence-dir', type=Path)
    args = parser.parse_args()
    if args.evidence_dir:
        EVIDENCE = args.evidence_dir.resolve()
        EVIDENCE.mkdir(parents=True, exist_ok=False)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(MemberTests)
    planned = [test.id() for test in suite]
    result = unittest.TextTestRunner(verbosity=2, resultclass=Accounting).run(suite)
    missing = sum(MISSING in text for _, text in result.failures)
    record = {'work_unit': 'REI_H1B1_AUTHENTICATED_DEB_MEMBERS', 'tests': result.testsRun,
              'planned_ids': planned, 'test_results': result.rows, 'subcases': result.subcases,
              'subcase_count': len(result.subcases), 'failures': len(result.failures),
              'errors': len(result.errors), 'skipped': len(result.skipped),
              'not_run': len(planned) - result.testsRun,
              'passed': sum(r['outcome'] == 'PASS' for r in result.rows),
              'implementation_absent_assertions': missing,
              'expected_implementation_absent_red': (result.testsRun == 15 and missing == 14
                  and len(result.failures) == 14 and not result.errors and not result.skipped
                  and sum(r['outcome'] == 'PASS' for r in result.rows) == 1),
              'successful': result.wasSuccessful() and not result.skipped,
              'donor_suite_tests_counted_here': 0,
              'fixture': 'SYNTHETIC_REAL_GPG_NOT_UBUNTU_ARCHIVE', 'cases': CASES}
    text = json.dumps(record, indent=2, allow_nan=False) + '\n'
    if args.report:
        with args.report.open('x') as stream:
            stream.write(text)
    print(text)
    raise SystemExit(0 if record['successful'] else 1)
