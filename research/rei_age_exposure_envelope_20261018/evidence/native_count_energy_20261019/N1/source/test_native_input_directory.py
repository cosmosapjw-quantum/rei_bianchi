"""Mocked input-contract tests, not physics or frozen 153-file validation.

Use a two-file temporary manifest and real included overlay donors. The external
153-to-156 preparation receipt independently checks the actual frozen inputs.
"""
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import hashlib
import io
import json
import sys
import tempfile
import unittest

import prepare_native as m

ROOT = Path(__file__).resolve().parents[1]
TRANSPORT = 'rust/rei_microphysics/src/axbi_covariant_transport.rs'
CARGO = 'rust/rei_microphysics/Cargo.toml'
NATIVE_SHA = '35d9747a0bbedcafdb568467ce7c1e7a25f965b6'


class NativeInputDirectoryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.tmp = Path(temporary.name)
        self.inputs = self.tmp / 'mock_inputs'
        self.payloads = {TRANSPORT: b'// Mock native transport input; no physics.\n',
                         CARGO: b'# Mock Cargo input; never compiled.\n'}
        for name, data in self.payloads.items():
            path = self.inputs / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        self.manifest = dict(native_sha=NATIVE_SHA, archive_sha256='MOCK_UNUSED',
            files={name: dict(sha256=hashlib.sha256(data).hexdigest(), size=len(data))
                   for name, data in self.payloads.items()})
        mocked = patch.object(m, 'load_manifest', return_value=self.manifest)
        mocked.start()
        self.addCleanup(mocked.stop)

    def test_exact_directory_success_preserves_inputs(self):
        dest = self.tmp / 'prepared'
        identity = m.prepare(ROOT, dest, native_input_dir=self.inputs)
        self.assertEqual(identity['native_sha'], NATIVE_SHA)
        self.assertEqual(identity['original_input_count'], 2)
        self.assertEqual(len(identity['outputs']), 5)
        self.assertEqual(identity['native_compile'], 'NOT_RUN_BY_PREPARER')
        self.assertTrue((dest / TRANSPORT).read_bytes().startswith(self.payloads[TRANSPORT]))
        self.assertEqual((dest / CARGO).read_bytes(), self.payloads[CARGO])
        for name, data in self.payloads.items():
            self.assertEqual((self.inputs / name).read_bytes(), data)
        for name, digest in identity['outputs'].items():
            self.assertEqual(m.sha(dest / name), digest)

    def test_missing_mismatch_and_ambiguous_inputs_rejected_before_output(self):
        (self.inputs / CARGO).unlink()
        with patch.object(m.urllib.request, 'urlopen', side_effect=AssertionError('NO_FETCH')):
            with self.assertRaisesRegex(FileNotFoundError, 'FROZEN_GIT_INPUT_MISSING'):
                m.prepare(ROOT, self.tmp / 'missing', native_input_dir=self.inputs,
                          fetch_missing=True)
        self.assertFalse((self.tmp / 'missing').exists())
        (self.inputs / CARGO).write_bytes(self.payloads[CARGO] + b'changed')
        with self.assertRaisesRegex(ValueError, 'FROZEN_INPUT_SHA_MISMATCH'):
            m.prepare(ROOT, self.tmp / 'mismatch', native_input_dir=self.inputs)
        self.assertFalse((self.tmp / 'mismatch').exists())
        for other in ({'archive': self.tmp / 'absent.zip'}, {'repo': self.tmp / 'repo'}):
            with self.assertRaisesRegex(ValueError, 'NATIVE_INPUT_DIR_SOURCE_CONFLICT'):
                m.prepare(ROOT, self.tmp / 'conflict', native_input_dir=self.inputs, **other)
            self.assertFalse((self.tmp / 'conflict').exists())

    def test_default_generation_unchanged_and_cli_plumbing(self):
        def frozen_git_show(argv, **kwargs):
            self.assertEqual(argv[:4], ['git', '-C', str(self.tmp / 'repo'), 'show'])
            native_sha, name = argv[4].split(':', 1)
            self.assertEqual(native_sha, NATIVE_SHA)
            return SimpleNamespace(returncode=0, stdout=self.payloads[name])
        with patch.object(m.subprocess, 'run', frozen_git_show):
            default = m.prepare(ROOT, self.tmp / 'default', repo=self.tmp / 'repo')
        directory = m.prepare(ROOT, self.tmp / 'directory', native_input_dir=self.inputs)
        self.assertEqual(default, directory)
        for name in default['outputs']:
            self.assertEqual((self.tmp / 'default' / name).read_bytes(),
                             (self.tmp / 'directory' / name).read_bytes())
        output = io.StringIO()
        with patch.object(sys, 'argv', ['prepare_native.py', '--native-input-dir',
                str(self.inputs), '--dest', str(self.tmp / 'cli')]), redirect_stdout(output):
            m.main()
        self.assertEqual(json.loads(output.getvalue()), dict(status='PREPARED_NOT_COMPILED',
                         native_sha=NATIVE_SHA, files=5))
        self.assertEqual(m.read_json(self.tmp / 'cli/PREPARED_IDENTITY.json'), default)


if __name__ == '__main__':
    unittest.main()
