"""Record fresh focused synthetic evidence in a new directory only."""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import unittest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir', type=Path, required=True)
    args = parser.parse_args()
    args.outdir = args.outdir.resolve()
    args.outdir.mkdir(parents=True, exist_ok=False)
    sys.dont_write_bytecode = True
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    import adapter
    import test_composition
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromModule(test_composition))
    (args.outdir / 'TEST_LOG.txt').write_text(stream.getvalue())
    fixture = args.outdir / 'SYNTHETIC_INPUT.json'
    fixture.write_bytes(adapter.canonical_bytes(test_composition.request()) + b'\n')
    output = args.outdir / 'SYNTHETIC_RESULT.json'
    command = [sys.executable, str(Path(__file__).with_name('adapter.py')),
               '--input', str(fixture), '--output', str(output)]
    smoke = subprocess.run(command, capture_output=True)
    (args.outdir / 'CLI_STDERR.txt').write_bytes(smoke.stderr)
    synthetic = json.loads(output.read_bytes()) if smoke.returncode == 0 else None
    files = [Path(__file__).with_name(name) for name in
             ('adapter.py', 'test_composition.py', 'verify_component.py', 'README_KO.md')]
    files += sorted(path for path in args.outdir.iterdir() if path.is_file())
    evidence = {
        'schema': 'WU088_T5_COMPONENT_VERIFICATION_V1',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS' if result.wasSuccessful() and smoke.returncode == 0 else 'FAIL',
        'scope': 'New composition component; analytic synthetic fixed-shape matrices only',
        'python': platform.python_version(),
        'command': [sys.executable, str(Path(__file__)), '--outdir', str(args.outdir)],
        'tests_run': result.testsRun, 'failures': len(result.failures),
        'errors': len(result.errors), 'skipped': len(result.skipped),
        'test_count_semantics': 'unique unittest methods; parameter subcases not counted again',
        'cli_command': command, 'cli_exit_code': smoke.returncode,
        'sample_arithmetic_operations': synthetic['arithmetic']['operations_used'] if synthetic else None,
        'sample_epsilon': synthetic['epsilon'] if synthetic else None,
        'observed_red': {'test': 'test_sharp_identity_counterexample', 'exit_code': 1,
                         'reason': "ModuleNotFoundError: No module named 'adapter'",
                         'stage': 'Test executed before the adapter existed; not a mathematical failure'},
        'grammar_source_sha256': adapter.GRAM_SHA256,
        'file_identities': {str(path.resolve().relative_to(Path(__file__).resolve().parent)): {
            'size': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in files},
        'actual_HH_runs': 0, 'native_backend_runs': 0, 'archived_HH_array_reads': 0,
        'historical_test_suites_rerun': False, 'rigorous': False,
        'production_admitted': False, 'independent_decision_review_admitted': False,
    }
    (args.outdir / 'VERIFICATION.json').write_text(json.dumps(evidence, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': evidence['status'], 'tests_run': evidence['tests_run'],
                      'failures': evidence['failures'], 'errors': evidence['errors'],
                      'cli_exit_code': smoke.returncode, 'actual_HH_runs': 0,
                      'evidence': str(args.outdir / 'VERIFICATION.json')}, sort_keys=True))
    return 0 if evidence['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
