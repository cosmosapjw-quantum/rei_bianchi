#!/usr/bin/env python3
"""Restore the sealed NCP_READY ZIP from verified byte-transport parts.

Linux + Python standard library only. No network access or scientific execution.
Output must be outside the parts directory. Existing output/receipt is rejected;
incomplete output is retained after failure. Atomic publication uses Linux
renameat2(RENAME_NOREPLACE), so a concurrent existing output is never replaced.
"""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import time
import uuid

CHUNK_BYTES = 1024 * 1024


def sha_file(path):
    h = hashlib.sha256()
    n = 0
    with path.open('rb') as f:
        for b in iter(lambda: f.read(CHUNK_BYTES), b''):
            h.update(b)
            n += len(b)
    return {'bytes': n, 'sha256': h.hexdigest()}


def fresh_path(raw):
    p = Path(raw).expanduser().absolute()
    p = p.parent.resolve() / p.name
    if os.path.lexists(p):
        raise FileExistsError(f'Existing destination is preserved: {p}')
    return p


def write_all(target, data):
    view = memoryview(data)
    total = 0
    while view:
        n = target.write(view)
        if n is None or n <= 0:
            raise OSError('Output write made no progress')
        total += n
        view = view[n:]
    if total != len(data):
        raise OSError('Output write length mismatch')


def fsync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def rename_no_replace(source, destination):
    if sys.platform != 'linux':
        raise RuntimeError('This transport helper requires Linux renameat2(RENAME_NOREPLACE)')
    libc = ctypes.CDLL(None, use_errno=True)
    renameat2 = getattr(libc, 'renameat2', None)
    if renameat2 is None:
        raise RuntimeError('renameat2 is unavailable; completed partial output is preserved')
    renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    renameat2.restype = ctypes.c_int
    rc = renameat2(-100, os.fsencode(source), -100, os.fsencode(destination), 1)
    if rc != 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err), str(destination))
    fsync_directory(destination.parent)


def check_identity(actual, expected, label):
    if actual['bytes'] != expected['bytes'] or actual['sha256'] != expected['sha256']:
        raise ValueError(f'{label}: size or SHA-256 mismatch')


def validate_manifest(value):
    if value.get('schema') != 'bass-he-ncp-byte-transport-parts-v1':
        raise ValueError('Unknown transport manifest schema')
    parts = value['parts']
    order = value['part_order']
    expected = value['reassembled']
    if not isinstance(parts, list) or not parts:
        raise ValueError('No ordered part records')
    if order != list(range(1, len(parts) + 1)) or [p['index'] for p in parts] != order:
        raise ValueError('Part order is not contiguous and unambiguous')
    names = set()
    offset = 0
    for p in parts:
        name = p['file_name']
        if not isinstance(name, str) or PurePosixPath(name).name != name or name in {'.', '..'} or '\\' in name:
            raise ValueError('Part filename must be a safe basename')
        if name in names:
            raise ValueError('Duplicate part filename')
        names.add(name)
        if type(p['bytes']) is not int or p['bytes'] <= 0 or p['offset_bytes'] != offset:
            raise ValueError('Invalid part size or byte offset')
        if not isinstance(p['sha256'], str) or re.fullmatch('[0-9a-f]{64}', p['sha256']) is None:
            raise ValueError('Invalid part SHA-256')
        offset += p['bytes']
    if type(expected['bytes']) is not int or expected['bytes'] != offset:
        raise ValueError('Reassembled size differs from sum of part sizes')
    if not isinstance(expected['sha256'], str) or re.fullmatch('[0-9a-f]{64}', expected['sha256']) is None:
        raise ValueError('Invalid reassembled SHA-256')
    return parts, expected


def run(args):
    started = time.monotonic()
    parts_dir = Path(args.parts_dir).expanduser().resolve(strict=True)
    manifest_path = Path(args.manifest).expanduser().resolve(strict=True)
    if not parts_dir.is_dir() or manifest_path.stat().st_size > CHUNK_BYTES:
        raise ValueError('Invalid parts directory or oversized manifest')
    output = fresh_path(args.output)
    if output.is_relative_to(parts_dir):
        raise ValueError('Output must be outside the parts directory')
    receipt = fresh_path(args.receipt or str(output) + '.restore_receipt.json')
    if receipt == output:
        raise ValueError('Receipt and output must have different paths')
    output.parent.mkdir(parents=True, exist_ok=True)
    receipt.parent.mkdir(parents=True, exist_ok=True)
    partial = output.with_name(output.name + '.partial.' + uuid.uuid4().hex)
    report = {'schema': 'bass-he-local-byte-transport-restore-v1',
              'scope': 'LOCAL_TRANSPORT_RECONSTRUCTION_ONLY',
              'status': 'RUNNING', 'manifest': str(manifest_path),
              'manifest_identity': sha_file(manifest_path),
              'restorer_identity': sha_file(Path(__file__)),
              'parts_directory': str(parts_dir), 'output': str(output),
              'partial_output': str(partial), 'verified_parts': [],
              'network_requests': 0, 'scientific_invocations': 0,
              'actual_NCP_scientific_execution': 'NOT_RUN',
              'remote_restore': 'NOT_RUN', 'recipient_execution_ack': 'NOT_RUN',
              'output_publication': 'NOT_RUN'}
    exit_code = 0
    try:
        manifest = json.loads(manifest_path.read_text())
        parts, expected = validate_manifest(manifest)
        report['expected_reassembled'] = expected
        for p in parts:
            source = parts_dir / p['file_name']
            if source.is_symlink() or not source.is_file():
                raise FileNotFoundError(f'Missing or unsafe part: {p["file_name"]}')
            if source.stat().st_size != p['bytes']:
                raise ValueError(f'Part size mismatch: {p["file_name"]}')
        whole = hashlib.sha256()
        written_total = 0
        with partial.open('xb') as target:
            for p in parts:
                h = hashlib.sha256()
                n = 0
                fd = os.open(parts_dir / p['file_name'], os.O_RDONLY | os.O_NOFOLLOW)
                with os.fdopen(fd, 'rb') as source:
                    for b in iter(lambda: source.read(CHUNK_BYTES), b''):
                        if n + len(b) > p['bytes']:
                            raise ValueError(f'Part grew during read: {p["file_name"]}')
                        write_all(target, b)
                        n += len(b)
                        written_total += len(b)
                        h.update(b)
                        whole.update(b)
                actual = {'bytes': n, 'sha256': h.hexdigest()}
                check_identity(actual, p, p['file_name'])
                report['verified_parts'].append({'index': p['index'], 'file_name': p['file_name'], **actual})
            target.flush()
            os.fsync(target.fileno())
        check_identity({'bytes': written_total, 'sha256': whole.hexdigest()}, expected, 'Joined byte stream')
        # Verify persisted output independently of the source stream before publication.
        partial_identity = sha_file(partial)
        check_identity(partial_identity, expected, 'Persisted partial output')
        rename_no_replace(partial, output)
        report['output_publication'] = 'ATOMIC_RENAME_NOREPLACE'
        final_identity = sha_file(output)
        check_identity(final_identity, expected, 'Final published output')
        report['final_identity'] = final_identity
        report['status'] = 'PASS_LOCAL_TRANSPORT_RESTORE'
    except Exception as error:
        exit_code = 1
        report['status'] = 'FAIL_LOCAL_TRANSPORT_RESTORE'
        report['error_type'] = type(error).__name__
        report['error'] = str(error)
        report['partial_preserved'] = partial.exists()
        report['output_preserved'] = output.exists()
    report['exit_code'] = exit_code
    report['elapsed_seconds'] = time.monotonic() - started
    receipt_partial = receipt.with_name(receipt.name + '.partial.' + uuid.uuid4().hex)
    with receipt_partial.open('xb') as f:
        write_all(f, (json.dumps(report, indent=2) + '\n').encode())
        f.flush()
        os.fsync(f.fileno())
    rename_no_replace(receipt_partial, receipt)
    print(json.dumps({'status': report['status'], 'exit_code': exit_code,
                      'output': str(output), 'receipt': str(receipt),
                      'final_identity': report.get('final_identity'),
                      'error': report.get('error')}))
    return exit_code


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parts-dir', required=True)
    parser.add_argument('--manifest', default=str(Path(__file__).with_name('TRANSPORT_PARTS.json')))
    parser.add_argument('--output', required=True)
    parser.add_argument('--receipt')
    try:
        sys.exit(run(parser.parse_args()))
    except Exception as error:
        # Preflight rejects occur before output creation; an existing file is never touched.
        print(json.dumps({'status': 'FAIL_TRANSPORT_PREFLIGHT_OR_RECEIPT',
                          'error_type': type(error).__name__, 'error': str(error)}), file=sys.stderr)
        sys.exit(1)
