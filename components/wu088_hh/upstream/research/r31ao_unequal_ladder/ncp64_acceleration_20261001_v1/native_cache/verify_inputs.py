"""Verify immutable/candidate source and pinned backend bytes; no native run."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import shutil
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
GATE = HERE.parent.parent / 'host_synthetic_readiness_20261001_v1'
_BASE = 'research/r31ao_unequal_ladder/'
EXPECTED_PATHS = {
    _BASE+'gap_closure_20261001_g0_g6_v1/validated_callback/callback.cpp',
    _BASE+'gap_closure_20261001_g0_g6_v1/validated_callback/callback.hpp',
    _BASE+'host_synthetic_readiness_20261001_v1/provenance_gate.py',
    *(_BASE+'ncp64_acceleration_20261001_v1/native_cache/'+name for name in
      ('cached_callback.cpp', 'cached_callback.hpp', 'native_cache_synthetic.cpp',
       'build_host.sh', 'verify_inputs.py')),
}


def identity(path):
    path = Path(path).resolve(strict=True)
    if not path.is_file() or path.stat().st_size > 512*1024*1024:
        raise ValueError('bounded regular identity file required')
    digest = hashlib.sha256()
    size = 0
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            size += len(chunk)
            if size > 512*1024*1024:
                raise ValueError('identity size cap exceeded')
            digest.update(chunk)
    return {'path': str(path), 'size': size, 'sha256': digest.hexdigest()}


def verify_sources():
    lock = json.loads((HERE/'SOURCE_LOCK.json').read_text())
    if lock.get('schema') != 'WU088_NATIVE_CACHE_SOURCE_LOCK_V1':
        raise ValueError('unknown source lock schema')
    paths = [item['path'] for item in lock['files']]
    if len(paths) != len(set(paths)) or set(paths) != EXPECTED_PATHS:
        raise ValueError('source lock omits, duplicates or adds a compiled/executed dependency')
    checked = []
    for item in lock['files']:
        rel = PurePosixPath(item['path'])
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError('invalid source lock path')
        got = identity(REPO/rel)
        if not Path(got['path']).is_relative_to(REPO):
            raise ValueError('source escaped repository')
        if (got['sha256'], got['size']) != (item['sha256'], item['size']):
            raise ValueError('source identity mismatch: '+str(rel))
        checked.append(got)
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', type=Path, required=True)
    parser.add_argument('--record', type=Path, required=True)
    parser.add_argument('--binary', type=Path)
    parser.add_argument('--ldd-report', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--compiler')
    args = parser.parse_args()
    sources = verify_sources()
    sys.path.insert(0, str(GATE))
    from provenance_gate import verify_backend, verify_linkage
    record = verify_backend(args.record, args.prefix)
    result = {'scope': 'SYNTHETIC_ONLY', 'sources': sources,
              'backend_record': identity(args.record),
              'backend_byte_chain': record['verification'],
              'native_executed': False, 'native_equality_verified': False,
              'actual_HH_runs': 0, 'scientific_promotion': False}
    if args.binary is not None:
        if args.ldd_report is None or args.output is None or not args.compiler:
            raise ValueError('binary mode requires linkage report, compiler and create-only output')
        result['binary'] = identity(args.binary)
        linked = verify_linkage(args.ldd_report.read_text(),
            {name: item['binary_path'] for name, item in record['libraries'].items()})
        for name, item in linked['libraries'].items():
            if item['sha256'] != record['libraries'][name]['binary_sha256']:
                raise ValueError('linked library hash mismatch: '+name)
        result['linkage'] = linked
        result['link_report'] = identity(args.ldd_report)
        compiler_path = shutil.which(args.compiler)
        if compiler_path is None:
            raise ValueError('native compiler identity unavailable')
        result['native_compiler'] = identity(compiler_path)
        result['native_compiler_version_output'] = identity(args.binary.parent/'compiler.txt')
        result['native_flags'] = ['-std=c++17', '-O3', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
            '-fno-fast-math', '-fno-associative-math', '-fno-unsafe-math-optimizations', '-ffp-contract=off']
        with args.output.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    elif args.ldd_report is not None or args.output is not None or args.compiler is not None:
        raise ValueError('partial binary verification options refused')
    print(json.dumps({'status': 'BYTE_CHAIN_CHECKED_NATIVE_NOT_EXECUTED',
                      'source_files': len(sources), 'actual_HH_runs': 0}))


if __name__ == '__main__':
    main()
