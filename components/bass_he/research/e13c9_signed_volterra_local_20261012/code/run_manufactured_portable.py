#!/usr/bin/env python3
"""Bind portable paths around the unchanged, byte-pinned E13C9 control script."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


PINS = {
    'oracle': '15806e4758038a788312dfe075f10a364682e3655a0ca35ed0ca602166ea091f',
    'candidate': '5f20e1b5b0f4936f7bd443d19c7181fd2c7de9de762fe2fa3e9be98f8963cfc5',
    'contract': '6e19a3f37520f30309ef18db1353f61c1affd8711a2797f42452dae4a2ecbc83',
    'original_source_lock': '386d0abd02a33b15a015166369cec981b00fd05987dbd146f2badcb9f604688f',
    'original_execution_lock': 'c04cfde1838563d95389e499de9bcbe505a7d67f6bda1fff4476af953c8cc4f4',
}
SOURCE_RELATIVE = 'runtime/E13C7_INPUT/BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1'


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def pinned(path, expected):
    actual = sha(path)
    if actual != expected:
        raise ValueError('byte pin mismatch: ' + str(path))
    return {'path': str(path), 'bytes': path.stat().st_size,
            'expected_sha256': expected, 'actual_sha256': actual, 'pass': True}


def inside(root, relative):
    path = (root / relative).resolve(strict=True)
    if not path.is_relative_to(root):
        raise ValueError('bound path leaves its declared root: ' + relative)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True, help='Restored E13C9 package root.')
    parser.add_argument('--restored-e13c8', type=Path, required=True, help='Hydrated E13C8 restoration root containing runtime/E13C7_INPUT.')
    parser.add_argument('--output-dir', type=Path, required=True, help='A fresh output directory for an explicitly requested control execution.')
    parser.add_argument('--describe-only', action='store_true', help='Read and validate bindings and pins, print JSON, and do not import or execute the control script.')
    args = parser.parse_args()
    package = args.package.resolve(strict=True)
    restored = args.restored_e13c8.resolve(strict=True)
    output = args.output_dir.resolve()
    if not package.is_dir() or not restored.is_dir():
        raise ValueError('package and restored-e13c8 must be directories')
    if output.exists():
        raise FileExistsError('a fresh output directory is required: ' + str(output))
    source = inside(restored, SOURCE_RELATIVE)
    if output.is_relative_to(restored):
        raise ValueError('output must preserve the restored E13C8 source tree')
    oracle = inside(package, 'tests/MANUFACTURED/run_manufactured_controls.py')
    candidate = inside(package, 'code/signed_volterra.py')
    contract = inside(package, 'SCIENTIFIC_CONTRACT.md')
    source_lock = inside(source, 'SOURCE_LOCK.json')
    execution_lock = inside(source, 'EXECUTION_LOCK.json')
    files = {'oracle': oracle, 'candidate': candidate, 'contract': contract,
             'original_source_lock': source_lock, 'original_execution_lock': execution_lock}
    checks = {name: pinned(path, PINS[name]) for name, path in files.items()}
    original_lock = json.loads(source_lock.read_bytes())
    members = []
    for relative, expected in sorted(original_lock['files'].items()):
        member = inside(source, relative)
        if member.stat().st_size != expected['bytes']:
            raise ValueError('source member size mismatch: ' + relative)
        members.append(pinned(member, expected['sha256']))
    execution = json.loads(execution_lock.read_bytes())
    plan_relative = 'inputs/WORK_PLAN.json'
    plan = inside(source, plan_relative)
    expected_plan = execution['files'][plan_relative]
    if plan.stat().st_size != expected_plan['bytes']:
        raise ValueError('original work-plan size mismatch')
    checks['original_work_plan'] = pinned(plan, expected_plan['sha256'])
    description = {
        'schema': 'bass-he-e13c9-portable-manufactured-bindings-v1',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS_PATH_BINDINGS_ONLY_NO_CONTROL_EXECUTION',
        'package': str(package), 'restored_e13c8': str(restored),
        'path_bindings': {'SOURCE': str(source), 'CANDIDATE': str(candidate), 'CONTRACT': str(contract)},
        'oracle_module_file': str(oracle), 'fresh_output_dir': str(output),
        'pin_checks': checks, 'original_source_members_checked': members,
        'wrapper_sha256': sha(Path(__file__).resolve()),
        'oracle_code_modified': False, 'output_directory_created': False,
        'original_controls_imported': False, 'control_executions': 0,
        'manufactured_coefficient_evaluations': 0, 'captured_coefficient_evaluations': 0,
        'NCP_launches': 0,
    }
    if args.describe_only:
        print(json.dumps(description, ensure_ascii=False, sort_keys=True, indent=2))
        return
    # The tested source bytes and __file__ remain unchanged. Only these three
    # explicit path constants are rebound before its original main is invoked.
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('bass_he_e13c9_preserved_manufactured_controls', oracle)
    if spec is None or spec.loader is None:
        raise ImportError('unable to load the pinned manufactured-control module')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.SOURCE, module.CANDIDATE, module.CONTRACT = source, candidate, contract
    previous_argv = sys.argv
    sys.argv = [str(oracle), '--output-dir', str(output)]
    try:
        module.main()
    finally:
        sys.argv = previous_argv


if __name__ == '__main__':
    main()
