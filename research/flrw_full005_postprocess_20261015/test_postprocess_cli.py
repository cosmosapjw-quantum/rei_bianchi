"""Focused CLI dispatch regression tests; no raw histories or figures are used."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import platform
import sys
import tempfile
import unittest
from unittest.mock import Mock, call, patch


SCRIPT = Path(__file__).with_name('postprocess_flrw.py')
SPEC = importlib.util.spec_from_file_location('postprocess_flrw_cli_target', SCRIPT)
postprocess = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(postprocess)


class PostprocessCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print(json.dumps({'python': platform.python_version(),
                          'executable': sys.executable,
                          'numpy': postprocess.np.__version__,
                          'matplotlib': postprocess.matplotlib.__version__}), flush=True)

    def invoke(self, *args):
        with patch.object(sys, 'argv', [str(SCRIPT), *args]):
            with contextlib.redirect_stdout(io.StringIO()):
                postprocess.main()

    def test_render_dispatches_global_run_with_path_arguments(self):
        with patch.object(postprocess, 'run') as run, \
                patch.object(postprocess, 'bind') as bind, \
                patch.object(postprocess, 'frozen_full005_guard') as guard, \
                patch.object(postprocess, 'write') as write:
            self.invoke('render', '--manifest', 'inputs/full_pair_manifest.json',
                        '--output', 'outputs/figures_and_diagnostics')
        run.assert_called_once_with(Path('inputs/full_pair_manifest.json'),
                                    Path('outputs/figures_and_diagnostics'))
        bind.assert_not_called()
        guard.assert_not_called()
        write.assert_not_called()

    def test_full_pair_bind_preserves_guard_bind_write_dispatch(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            output = base / 'full_pair_manifest.json'
            cases = ['FLRW_FULL_Q512_001', 'FLRW_FULL_Q1024_001']
            bindings = [{'case': case, 'marker': i} for i, case in enumerate(cases)]
            paths = [base / (case + '.binding.json') for case in cases]
            for path, binding in zip(paths, bindings):
                path.write_text(json.dumps(binding))
            run_dirs = [str(base / case) for case in cases]
            specs = [{'id': case, 'sentinel': i} for i, case in enumerate(cases)]
            events = Mock()
            with patch.object(postprocess, 'frozen_full005_guard') as guard, \
                    patch.object(postprocess, 'bind', side_effect=specs) as bind, \
                    patch.object(postprocess, 'write') as write, \
                    patch.object(postprocess, 'run') as run:
                events.attach_mock(guard, 'guard')
                events.attach_mock(bind, 'bind')
                events.attach_mock(write, 'write')
                argv = ['bind', '--mode', 'FULL_PAIR', '--end-zbar', '4',
                        '--output', str(output)]
                for case, run_dir, path in zip(cases, run_dirs, paths):
                    argv.extend(['--case', ','.join([case, run_dir, str(path)])])
                self.invoke(*argv)
            self.assertEqual(events.mock_calls, [
                call.guard(cases[0], bindings[0]), call.guard(cases[1], bindings[1]),
                call.bind(cases[0], run_dirs[0], str(paths[0])),
                call.bind(cases[1], run_dirs[1], str(paths[1])),
                call.write(output, {
                    'mode': 'FULL_PAIR', 'end_zbar': 4.0,
                    'source_relation': 'Identicalsourcebyteguard unlessexplicitreviewedrelation supplied',
                    'cases': specs})])
            run.assert_not_called()

    def test_short_screen_bind_dispatch(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'preview_manifest.json'
            spec = {'id': 'SHORT_SCREEN', 'sentinel': 'preview'}
            events = Mock()
            with patch.object(postprocess, 'frozen_full005_guard') as guard, \
                    patch.object(postprocess, 'bind', return_value=spec) as bind, \
                    patch.object(postprocess, 'write') as write, \
                    patch.object(postprocess, 'run') as run:
                events.attach_mock(bind, 'bind')
                events.attach_mock(write, 'write')
                self.invoke('bind', '--mode', 'SHORT_SCREEN_PREVIEW', '--end-zbar', '10',
                            '--output', str(output),
                            '--case', 'SHORT_SCREEN,inputs/short,inputs/short.binding.json')
            self.assertEqual(events.mock_calls, [
                call.bind('SHORT_SCREEN', 'inputs/short', 'inputs/short.binding.json'),
                call.write(output, {
                    'mode': 'SHORT_SCREEN_PREVIEW', 'end_zbar': 10.0,
                    'source_relation': 'Identicalsourcebyteguard unlessexplicitreviewedrelation supplied',
                    'cases': [spec]})])
            guard.assert_not_called()
            run.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
