"""Adapter to the unchanged, pinned INTAKE01 cumulative resource wrapper."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / 'scripts/legacy_bounded_runner.py'
EXPECTED = 'b0f36cb3ee2f79d4fc29fa6596be37b829d299694f3fd167bf40460a3b976e8f'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repair-reason')
    parser.add_argument('--test-name', action='append', default=[])
    args = parser.parse_args()
    if hashlib.sha256(RUNNER.read_bytes()).hexdigest() != EXPECTED:
        raise RuntimeError('pinned unchanged resource wrapper differs')
    spec = importlib.util.spec_from_file_location('aperture07_resource_wrapper', RUNNER)
    runner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = runner
    spec.loader.exec_module(runner)
    runner.ROOT = ROOT
    runner.OUT = ROOT / 'evidence/validation'
    ledger = runner.OUT / 'RESOURCE_LEDGER.json'
    count = len(json.loads(ledger.read_text())['attempts']) + 1 if ledger.exists() else 1
    files = [ROOT / 'VALIDATION_CONTRACT.json']
    for directory in ('src', 'scripts', 'tests', 'sources'):
        files.extend(p for p in (ROOT / directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    # Root-authored theory/model are bound when installed at the admitted unit.
    files.extend(p for name in ('THEORY_KO.md', 'MODEL_CONTRACT.json') if (p := ROOT / name).exists())
    manifest = {
        'schema': 'HE_APERTURE07_TESTED_DEPENDENCIES_V1',
        'files': [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size,
                   'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(files))],
        'preparation_cost': 'UNKNOWN_NOT_ZERO; outside test measurement',
    }
    destination = ROOT / 'evidence' / f'TESTED_DEPENDENCIES_{count:02d}.json'
    if destination.exists() and json.loads(destination.read_text()) != manifest:
        raise RuntimeError('different existing dependency binding')
    runner.save(destination, manifest)
    return runner.run('tests', args.repair_reason, tuple(args.test_name))


if __name__ == '__main__':
    raise SystemExit(main())
