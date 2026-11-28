"""Verify saved E13C2 evidence, or explicitly recompute only the new E13C2 work.

Always writes to a new directory outside this immutable package. No native
receiver, gas advance, old campaign, network call, or dependency install exists
in this entry point. The default performs hash checks and the saved-result
verifier, including one constant-coefficient limit and domain rejections.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_manifest(root):
    manifest = json.loads((root / 'FILE_MANIFEST.json').read_text())
    for item in manifest['files']:
        path = root / item['path']
        if not path.is_file() or path.stat().st_size != item['bytes'] or sha(path) != item['sha256']:
            raise ValueError('immutable package identity mismatch: ' + item['path'])
    return len(manifest['files'])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--output', type=Path, required=True, help='new directory outside package')
    p.add_argument('--recompute', action='store_true', help='explicitly repeat only new E13C2 fixed-path/Decimal/algebra calculations')
    args = p.parse_args()
    root = args.root.resolve()
    out = args.output.resolve()
    if out.is_relative_to(root):
        p.error('--output must be outside the immutable package')
    if out.exists():
        p.error('--output already exists; refusing overwrite')
    count = verify_manifest(root)
    out.mkdir(parents=True)
    history = []
    env = dict(os.environ)
    env['OPENBLAS_NUM_THREADS'] = '1'

    def command(label, script, tail):
        argv = [sys.executable, '-B', '-W', 'error', str(root / 'code' / script), *map(str, tail)]
        started = time.perf_counter()
        with (out / (label + '.stdout')).open('w') as stdout, (out / (label + '.stderr')).open('w') as stderr:
            result = subprocess.run(argv, cwd=root, env=env, stdout=stdout, stderr=stderr, check=False)
        history.append({'label': label, 'argv': argv, 'exit_code': result.returncode,
                        'elapsed_seconds': time.perf_counter() - started})
        if result.returncode:
            (out / 'FIRST_FAILURE.json').write_text(json.dumps({'commands': history, 'classification': 'REPRODUCTION_FAILURE_UNCLASSIFIED'}, indent=2) + '\n')
            raise RuntimeError(label + ' failed; original evidence unchanged; inspect FIRST_FAILURE and stderr')

    if args.recompute:
        work = out / 'recomputed'
        (work / 'evidence').mkdir(parents=True)
        # Read-only usage of immutable package inputs; all outputs are external.
        (work / 'inputs').symlink_to(root / 'inputs', target_is_directory=True)
        command('primary_coarse', 'continuous_defect.py', ['--root', work, '--output', work / 'evidence/defect_rtol_2e9', '--rtol', '2e-9'])
        command('primary_fine', 'continuous_defect.py', ['--root', work, '--output', work / 'evidence/defect_rtol_2e11', '--rtol', '2e-11'])
        command('decimal', 'decimal_collocation.py', ['--source', root / 'inputs/upstream_e13c1', '--output', work / 'evidence/ORACLE_RESULTS.json'])
        command('algebra', 'e13c2_symbolic_check.py', [work / 'evidence/SYMBOLIC_VERIFICATION.json'])
        command('verify_recomputed', 'verify_research.py', ['--root', work, '--output', out / 'VERIFICATION.json'])
    else:
        command('verify_saved', 'verify_research.py', ['--root', root, '--output', out / 'VERIFICATION.json'])
    receipt = {'package_files_verified': count, 'mode': 'new_E13C2_recompute' if args.recompute else 'saved_evidence_verification',
               'commands': history, 'old_campaign_replays': 0, 'native_runs': 0, 'new_gas_steps': 0,
               'verdict': 'PASS_SCOPED', 'physical': 'HOLD', 'production': 'HOLD'}
    (out / 'REPRODUCTION_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'verdict': receipt['verdict'], 'mode': receipt['mode'], 'output': str(out)}))


if __name__ == '__main__':
    main()
