#!/usr/bin/env python3
"""Verify a manifest-bound E13C7 return and extract into a fresh directory."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import time
import zipfile


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def save(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--archive', type=Path, required=True)
    ap.add_argument('--package', type=Path, required=True)
    ap.add_argument('--destination', type=Path, required=True)
    ap.add_argument('--receipt', type=Path, required=True)
    a = ap.parse_args()
    started = time.monotonic()
    expected_sha = 'a7a0fd6e58a88140071a1b623897efbd35748c86c4eda6956a937171eefe6c8f'
    expected_size = 124152692
    if a.archive.stat().st_size != expected_size or sha(a.archive) != expected_sha:
        raise ValueError('actual return archive byte identity mismatch')
    if a.destination.exists() or a.receipt.exists():
        raise FileExistsError('fresh destination and receipt required; no automatic retry')
    with zipfile.ZipFile(a.archive) as z:
        infos = z.infolist()
        names = [i.filename for i in infos]
        if len(names) != len(set(names)) or len(names) > 30000:
            raise ValueError('duplicate member or unexpected member count')
        if sum(i.file_size for i in infos) > 1024**3:
            raise ValueError('unexpected expanded byte count')
        for i in infos:
            p = PurePosixPath(i.filename)
            mode = i.external_attr >> 16
            if p.is_absolute() or not p.parts or any(x in ('', '.', '..') for x in p.parts):
                raise ValueError('unsafe archive path')
            if str(p) != i.filename or '\\' in i.filename or ':' in i.filename:
                raise ValueError('noncanonical archive path')
            if i.is_dir() or stat.S_IFMT(mode) not in (0, stat.S_IFREG):
                raise ValueError('only regular archive payloads allowed')
        manifest_bytes = z.read('RETURN_MANIFEST.json')
        manifest = json.loads(manifest_bytes)
        pins = manifest['files']
        if set(names) != set(pins) | {'RETURN_MANIFEST.json'}:
            raise ValueError('manifest/member set mismatch')
        for name in ('EXECUTION_LOCK.json', 'SOURCE_LOCK.json', 'RESEARCH_CONTRACT.json', 'SCIENTIFIC_CONTRACT.md', 'inputs/WORK_PLAN.json'):
            if z.read('PINNED_EXECUTION/' + name) != (a.package / name).read_bytes():
                raise ValueError('predecessor pinned execution mismatch: ' + name)
        lock = json.loads((a.package / 'EXECUTION_LOCK.json').read_text())
        for name, pin in lock['files'].items():
            p = a.package / name
            if p.stat().st_size != pin['bytes'] or sha(p) != pin['sha256']:
                raise ValueError('predecessor execution file mismatch: ' + name)
        a.destination.mkdir(parents=True, exist_ok=False)
        extracted = 0
        for i in infos:
            dest = a.destination / i.filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            h = hashlib.sha256()
            count = 0
            with z.open(i) as src, dest.open('xb') as dst:
                while True:
                    b = src.read(1024 * 1024)
                    if not b:
                        break
                    h.update(b)
                    count += len(b)
                    dst.write(b)
            if i.filename != 'RETURN_MANIFEST.json':
                pin = pins[i.filename]
                if count != pin['bytes'] or h.hexdigest() != pin['sha256']:
                    raise ValueError('actual payload mismatch: ' + i.filename)
                extracted += 1
    attempt = json.loads((a.destination / 'ATTEMPT_COMPLETE.json').read_text())
    complete = json.loads((a.destination / 'BATCH/BATCH_COMPLETE.json').read_text())
    if attempt['new_scientific_path_calls'] != 2331 or attempt['mpi_child_exit_code'] != 0:
        raise ValueError('unexpected attempt work or exit')
    if (a.destination / 'BATCH/SOURCE_AND_INPUT_BEFORE.json').read_bytes() != (a.destination / 'BATCH/SOURCE_AND_INPUT_AFTER.json').read_bytes():
        raise ValueError('before/after source identity mismatch')
    record = {
        'schema': 'bass-he-e13c8-intake-receipt-v1',
        'status': 'PASS_ACTUAL_ARCHIVE_AND_PAYLOAD_IDENTITY',
        'archive': {'bytes': expected_size, 'sha256': expected_sha},
        'payload_files_verified': extracted,
        'archive_members': len(infos),
        'raw_bytes': sum(i.file_size for i in infos),
        'manifest_sha256': hashlib.sha256(manifest_bytes).hexdigest(),
        'predecessor_execution_files_verified': len(lock['files']),
        'source_input_before_after_identical': True,
        'attempt_status': attempt['status'],
        'batch_status': complete['status'],
        'collection_semantic_sha256': complete['collection_semantic_sha256'],
        'semantic_scientific_validation': 'PENDING_EXACT_REDUCTION_AND_INDEPENDENT_REVIEW',
        'kernel_invocations': 0,
        'elapsed_seconds': time.monotonic() - started,
        'destination': str(a.destination.resolve())
    }
    save(a.receipt, record)
    print(json.dumps(record))


if __name__ == '__main__':
    main()
