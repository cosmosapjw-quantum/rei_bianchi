import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import provenance_gate as gate


class ProvenanceGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.prefix = self.root / 'prefix'
        (self.prefix / 'lib').mkdir(parents=True)
        self.compiler = self.root / 'compiler'
        self.compiler.write_bytes(b'synthetic compiler identity only')
        self.record = {'prefix': str(self.prefix), 'verified_build_provenance': True,
                       'compiler': {'path': str(self.compiler), 'sha256': self.hash(self.compiler), 'version': 'fixture'},
                       'libraries': {}}
        self.pins = {}
        for name in ('gmp', 'mpfr', 'flint'):
            archive = self.root / (name + '.tar')
            archive.write_bytes(name.encode())
            binary = self.prefix / 'lib' / ('lib' + name + '.so.1')
            binary.write_bytes(b'\x7fELF' + name.encode())
            logs = []
            for stage in ('configure', 'build', 'install'):
                log = self.root / (name + '-' + stage + '.log')
                log.write_text('synthetic evidence, not an executed build')
                streams = {}
                for stream in ('stdout', 'stderr'):
                    stream_path = self.root / (name + '-' + stage + '-' + stream + '.log')
                    stream_path.write_text('fixture output')
                    streams[stream] = {'path':str(stream_path), 'sha256':self.hash(stream_path)}
                logs.append({'stage': stage, 'path': str(log), 'sha256': self.hash(log), 'exit_code': 0, **streams})
            self.pins[name] = {'version': 'fixture-1', 'sha256': self.hash(archive), 'size': archive.stat().st_size}
            self.record['libraries'][name] = {'version': 'fixture-1', 'source_archive_path': str(archive),
                'source_archive_sha256': self.hash(archive), 'binary_path': str(binary), 'binary_sha256': self.hash(binary),
                'compiler': str(self.compiler), 'flags': ['-O2','-fno-fast-math'], 'abi': 'fixture',
                'build_log_sha256': logs[1]['sha256'], 'build_logs': logs}
        self.record_path = self.root / 'record.json'

    @staticmethod
    def hash(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def verify(self):
        self.record_path.write_text(json.dumps(self.record))
        with patch.object(gate, 'PINS', self.pins):
            return gate.verify_backend(self.record_path, self.prefix)

    def linkage(self):
        expected = {n: x['binary_path'] for n, x in self.record['libraries'].items()}
        text = '\n'.join('lib'+n+'.so.1 => '+p+' (0x1234)' for n,p in expected.items())
        return text, expected

    def test_intact_chain_has_limited_claim(self):
        result = self.verify()
        self.assertEqual(result['verification']['status'], 'BYTE_CHAIN_VERIFIED')
        self.assertFalse(result['verification']['independent_execution_proven'])
        self.assertFalse(result['verification']['historical_abi_admitted'])

    def test_boolean_does_not_admit_missing_log(self):
        Path(self.record['libraries']['gmp']['build_logs'][1]['path']).unlink()
        with self.assertRaises(ValueError): self.verify()

    def test_modified_log_rejected(self):
        Path(self.record['libraries']['mpfr']['build_logs'][0]['path']).write_text('modified')
        with self.assertRaises(ValueError): self.verify()

    def test_actual_stream_tamper_is_rejected_even_with_unchanged_receipt(self):
        log = self.record['libraries']['flint']['build_logs'][1]
        Path(log['stdout']['path']).write_text('altered actual build output')
        self.assertEqual(self.hash(Path(log['path'])), log['sha256'])
        with self.assertRaises(ValueError): self.verify()

    def test_failed_or_missing_stage_rejected(self):
        for mode in ('failed', 'missing'):
            with self.subTest(mode=mode):
                original = copy.deepcopy(self.record)
                if mode == 'failed': self.record['libraries']['flint']['build_logs'][1]['exit_code'] = 2
                else: self.record['libraries']['flint']['build_logs'].pop()
                with self.assertRaises(ValueError): self.verify()
                self.record = original

    def test_source_or_compiler_tamper_rejected(self):
        self.compiler.write_bytes(b'changed')
        with self.assertRaises(ValueError): self.verify()

    def test_binary_symlink_escape_rejected(self):
        binary = Path(self.record['libraries']['gmp']['binary_path'])
        outside = self.root / 'outside.so'
        outside.write_bytes(binary.read_bytes())
        binary.unlink(); binary.symlink_to(outside)
        with self.assertRaises(ValueError): self.verify()

    def test_missing_or_duplicated_dependency_rejected(self):
        text, expected = self.linkage()
        for bad in (text.replace('libgmp.so.1 => '+expected['gmp']+' (0x1234)', 'libgmp.so.1 => not found'), text+'\n'+text.splitlines()[0]):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError): gate.verify_linkage(bad, expected)

    def test_different_linked_library_rejected(self):
        text, expected = self.linkage()
        with self.assertRaises(ValueError): gate.verify_linkage(text.replace(expected['gmp'], '/usr/lib/libgmp.so.1'), expected)

    def test_linkage_returns_actual_hashes(self):
        text, expected = self.linkage()
        result = gate.verify_linkage(text, expected)
        self.assertEqual(result['status'], 'LINKED_BACKEND_PATHS_VERIFIED')
        for name, path in expected.items(): self.assertEqual(result['libraries'][name]['sha256'], self.hash(Path(path)))

    def test_unknown_dependency_cannot_hide(self):
        text, expected = self.linkage()
        with self.assertRaises(ValueError): gate.verify_linkage(text+'\nlibsurprise.so => /tmp/other.so (0x4321)', expected)

    def test_missing_null_or_malformed_identity_is_not_admitted(self):
        for location in ('compiler', 'binary', 'log'):
            for invalid in (None, '', 'abc', 123):
                with self.subTest(location=location, invalid=invalid):
                    original = copy.deepcopy(self.record)
                    if location == 'compiler': self.record['compiler']['sha256'] = invalid
                    elif location == 'binary': self.record['libraries']['gmp']['binary_sha256'] = invalid
                    else: self.record['libraries']['gmp']['build_logs'][0]['sha256'] = invalid
                    with self.assertRaises(ValueError): self.verify()
                    self.record = original


if __name__ == '__main__':
    unittest.main()
