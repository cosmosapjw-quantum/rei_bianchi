#!/usr/bin/env python3
"""Place this one verified .part002.bin under its immutable manifest basename.

No network, ZIP restoration, scientific imports, or budget execution. Preserve
the original download; refuse a different existing canonical file. Reuse the
pinned original restorer's atomic no-replace publication primitive.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import uuid

MANIFEST_SHA = 'd20e2146447bd10748066a03573fc439be6127c5aa89627e4ff309a9f181d8a6'
RESTORER_SHA = '3b947e4537da4f24eaf3a40a7ebf9051cd560e58f813928425f6a4a69599abbb'
NAME = 'BASS_HE_E13C5_FULL_FINITE_NCP_READY_20261011_sha_5741b06b9a61.zip.part002'
EXPECTED = {'bytes': 40580022, 'sha256': '34b7b41f19c42cb19da7a001daf7ccc48ae527dbaa101b613fb90b7fa20bedbb'}
CHUNK = 1024 * 1024


def identity(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as source:
        if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
            raise ValueError('Expected a regular non-symlink file')
        digest = hashlib.sha256()
        size = 0
        for block in iter(lambda: source.read(CHUNK), b''):
            size += len(block)
            digest.update(block)
    return {'bytes': size, 'sha256': digest.hexdigest()}


def require_identity(path, expected):
    actual = identity(path)
    if actual != expected:
        raise ValueError('File bytes/SHA mismatch: ' + str(path))
    return actual


def place_alias(source, target, expected, partial, restorer):
    # This generic file operation is exercised with small byte fixtures only.
    source_identity = require_identity(source, expected)
    if os.path.lexists(target):
        require_identity(target, expected)
        return {'status': 'VERIFIED_CANONICAL_ALREADY_PRESENT', 'copied': False,
                'source_identity': source_identity, 'target_identity': expected}
    fd = os.open(source, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as src, partial.open('xb') as dst:
        if not stat.S_ISREG(os.fstat(src.fileno()).st_mode):
            raise ValueError('Source changed to a nonregular file')
        for block in iter(lambda: src.read(CHUNK), b''):
            restorer.write_all(dst, block)
        dst.flush()
        os.fsync(dst.fileno())
    require_identity(partial, expected)
    restorer.rename_no_replace(partial, target)
    final_identity = require_identity(target, expected)
    return {'status': 'VERIFIED_CANONICAL_COPY_CREATED', 'copied': True,
            'source_identity': source_identity, 'target_identity': final_identity}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kit-dir', required=True)
    parser.add_argument('--parts-dir', required=True)
    parser.add_argument('--receipt', required=True)
    args = parser.parse_args()
    receipt = Path(args.receipt).expanduser().absolute()
    receipt = receipt.parent.resolve() / receipt.name
    if os.path.lexists(receipt):
        raise FileExistsError('Existing receipt is preserved: ' + str(receipt))
    receipt.parent.mkdir(parents=True, exist_ok=True)
    report = {'schema': 'bass-he-e13c5-part002-placement-v1',
              'status': 'FAIL_PART002_PLACEMENT', 'scope': 'TRANSPORT_NAME_BINDING_ONLY',
              'budget_invocations': 0, 'physics_invocations': 0,
              'full_first2_invocations': 0, 'N512_invocations': 0,
              'archive_restore_invocations': 0, 'actual_NCP_budget_execution': 'NOT_RUN',
              'automatic_retry': False, 'original_download_preserved': True}
    partial = None
    restorer = None
    exit_code = 1
    try:
        kit = Path(args.kit_dir).expanduser().resolve(strict=True)
        parts = Path(args.parts_dir).expanduser().resolve(strict=True)
        if not kit.is_dir() or not parts.is_dir() or receipt.is_relative_to(parts):
            raise ValueError('Use existing kit/parts directories and an external fresh receipt')
        manifest_path = kit / 'TRANSPORT_PARTS.json'
        restorer_path = kit / 'restore_ncp_ready.py'
        require_identity(manifest_path, {'bytes': 1176, 'sha256': MANIFEST_SHA})
        require_identity(restorer_path, {'bytes': 9543, 'sha256': RESTORER_SHA})
        manifest = json.loads(manifest_path.read_text())
        record = manifest['parts'][1]
        if record['index'] != 2 or record['file_name'] != NAME or any(record[k] != v for k, v in EXPECTED.items()):
            raise ValueError('Pinned part002 manifest record mismatch')
        spec = importlib.util.spec_from_file_location('pinned_transport_restorer', restorer_path)
        restorer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(restorer)
        source = parts / (NAME + '.bin')
        target = parts / NAME
        partial = parts / (NAME + '.placement.partial.' + uuid.uuid4().hex)
        report.update({'source': str(source), 'target': str(target),
                       'partial': str(partial), 'expected': EXPECTED,
                       'manifest_sha256': MANIFEST_SHA, 'restorer_sha256': RESTORER_SHA})
        outcome = place_alias(source, target, EXPECTED, partial, restorer)
        require_identity(source, EXPECTED)
        require_identity(manifest_path, {'bytes': 1176, 'sha256': MANIFEST_SHA})
        require_identity(restorer_path, {'bytes': 9543, 'sha256': RESTORER_SHA})
        report.update(outcome)
        report['status'] = 'PASS_SCOPED_PART002_FILENAME_BINDING'
        report['placement_outcome'] = outcome['status']
        exit_code = 0
    except Exception as error:
        report.update({'error_type': type(error).__name__, 'error': str(error),
                       'partial_preserved': bool(partial and partial.exists())})
    report['exit_code'] = exit_code
    # Exclusive creation preserves every existing receipt and the first failure.
    with receipt.open('x') as out:
        out.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        out.flush()
        os.fsync(out.fileno())
    print(json.dumps({'status': report['status'], 'exit_code': exit_code,
                      'receipt': str(receipt), 'error': report.get('error')}))
    return exit_code


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print(json.dumps({'status': 'FAIL_PLACEMENT_PREFLIGHT_OR_RECEIPT',
                          'error_type': type(error).__name__, 'error': str(error)}), file=sys.stderr)
        sys.exit(1)
