#!/usr/bin/env python3
"""Preserve the closed T1 wave as manifested archives and native Dropbox copies.

Provider synchronization is deliberately a separate verification state.
This script does not evolve a history or delete/rewrite any raw result.
"""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import tarfile
import time

RESERVE = 32 * 1024**3


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(path):
    whole = hashlib.sha256()
    blocks = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            whole.update(chunk)
            blocks.update(hashlib.sha256(chunk).digest())
    return {'bytes': path.stat().st_size, 'sha256': whole.hexdigest(),
            'dropbox_content_hash': blocks.hexdigest()}


class HashingReader:
    def __init__(self, stream):
        self.stream = stream
        self.hash = hashlib.sha256()

    def read(self, size):
        data = self.stream.read(size)
        self.hash.update(data)
        return data


def build_archive(root, files, path, source_specs=None):
    manifest = {}
    temporary = path.with_suffix(path.suffix + '.partial')
    require(not path.exists() and not temporary.exists(), 'ARCHIVE_ALREADY_EXISTS')
    with temporary.open('xb') as destination:
        with gzip.GzipFile(filename='', mode='wb', fileobj=destination, mtime=0, compresslevel=1) as packed:
            with tarfile.open(mode='w|', fileobj=packed, format=tarfile.PAX_FORMAT) as archive:
                for source in sorted(set(files)):
                    require(source.is_file() and not source.is_symlink(), 'NONREGULAR_INPUT:' + str(source))
                    name = source.relative_to(root).as_posix()
                    before = source.stat()
                    item = tarfile.TarInfo(name)
                    item.size = before.st_size
                    item.mode = before.st_mode & 0o777
                    item.mtime = 0
                    with source.open('rb') as stream:
                        hashed = HashingReader(stream)
                        archive.addfile(item, hashed)
                    after = source.stat()
                    require((before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns),
                            'INPUT_CHANGED_DURING_ARCHIVE:' + name)
                    manifest[name] = {'bytes': before.st_size, 'sha256': hashed.hash.hexdigest()}
                    if source_specs and name.startswith('source/'):
                        require(manifest[name] == source_specs[name[7:]], 'SOURCE_BINDING_MISMATCH:' + name)
                encoded = (json.dumps(manifest, indent=2, sort_keys=True) + '\n').encode()
                item = tarfile.TarInfo('ARCHIVE_MANIFEST.json')
                item.size = len(encoded)
                item.mode = 0o644
                item.mtime = 0
                archive.addfile(item, io.BytesIO(encoded))
    temporary.rename(path)
    manifest_path = path.with_name(path.name + '.manifest.json')
    manifest_path.write_bytes(encoded)
    return {**identity(path), 'archive_name': path.name, 'path': str(path),
            'files': len(manifest), 'uncompressed_input_bytes': sum(x['bytes'] for x in manifest.values()),
            'manifest_sha256': hashlib.sha256(encoded).hexdigest(),
            'manifest_path': str(manifest_path)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('dropbox_copy', type=Path)
    args = parser.parse_args()
    begin, cpu = time.monotonic(), time.process_time()
    ledger_path = args.root / 'RUN_LEDGER.json'
    ledger_identity = identity(ledger_path)
    ledger = json.loads(ledger_path.read_text())
    require(ledger['status'] == 'T1_WAVE_FINISHED_WITH_RETAINED_OUTCOMES', 'WAVE_STILL_RUNNING')
    require(not args.output.exists() and not args.dropbox_copy.exists(), 'DESTINATION_ALREADY_EXISTS')
    require(args.dropbox_copy.parent.is_dir(), 'MISSING_DROPBOX_PARENT')
    args.output.mkdir()
    args.dropbox_copy.mkdir()
    results = []
    try:
        groups = []
        for case in ['ZERO', 'PLUS']:
            for segment in sorted((args.root / 'cases' / case).glob('segment_*')):
                groups.append((f'T1_{case}_{segment.name}.tar.gz',
                               [p for p in segment.rglob('*') if p.is_file()]))
        source = json.loads((args.root / 'SOURCE_BINDING.json').read_text())
        control = [args.root / 'source' / name for name in source['files']]
        for directory in ['harness', 'inputs', 'preflight', 'analysis_v1']:
            control.extend(p for p in (args.root / directory).rglob('*')
                           if p.is_file() and not p.name.endswith('.b64') and '__pycache__' not in p.parts)
        control.extend([args.root / name for name in
                        ['ALLOCATION.json', 'SOURCE_BINDING.json', 'FULL_EXECUTION_BINDING.json',
                         'PREFLIGHT_VALIDATION.json', 'PACKAGE_MANIFEST.json', 'RUN_LEDGER.json',
                         'SAMPLING_GRID.json', 'POSTPROCESS_BINDING.json',
                         'POSTPROCESS_PACKAGE_MANIFEST.json', 'POSTPROCESS_STARTED.json']])
        control.append(Path(source['binary']['path']))
        groups.append(('T1_CONTROL_SOURCE_PREFLIGHT_ANALYSIS.tar.gz', control))
        reserved_bytes = 0
        for name, files in groups:
            receipt = build_archive(args.root, files, args.output / name, source['files'])
            reserved_bytes += 2 * receipt['bytes']
            require(reserved_bytes <= RESERVE, 'BACKUP_COPY_RESERVE_EXCEEDED')
            destination = args.dropbox_copy / name
            temporary = destination.with_suffix(destination.suffix + '.partial')
            require(not destination.exists() and not temporary.exists(), 'COPY_ALREADY_EXISTS')
            shutil.copyfile(args.output / name, temporary)
            copied = identity(temporary)
            require(all(copied[key] == receipt[key] for key in copied), 'COPY_IDENTITY_FAILURE')
            temporary.rename(destination)
            receipt.update(dropbox_local_path=str(destination), local_copy_verified=True,
                           provider_sync='PENDING_PROVIDER_HASH_VERIFICATION')
            results.append(receipt)
            (args.output / 'BACKUP_PROGRESS.json').write_text(json.dumps(results, indent=2) + '\n')
            print(json.dumps({'archive': name, 'bytes': receipt['bytes'], 'sha256': receipt['sha256'],
                              'local_copy_verified': True}), flush=True)
        require(identity(ledger_path) == ledger_identity, 'RUN_LEDGER_CHANGED')
        receipt = {'status': 'NATIVE_ARCHIVES_AND_DROPBOX_LOCAL_COPIES_VERIFIED',
                   'provider_sync': 'PENDING_PROVIDER_HASH_VERIFICATION',
                   'archives': results, 'reserved_copy_bytes_used': reserved_bytes,
                   'closed_run_ledger': ledger_identity, 'CPU_s': time.process_time() - cpu,
                   'wall_s': time.monotonic() - begin, 'raw_inputs_deleted': False,
                   'script_sha256': identity(Path(__file__))['sha256'],
                   'original_DAG': '10/17', 'expansion_DAG': '28/88'}
        encoded = json.dumps(receipt, indent=2, allow_nan=False) + '\n'
        (args.output / 'BACKUP_RECEIPT.json').write_text(encoded)
        (args.dropbox_copy / 'BACKUP_RECEIPT.json').write_text(encoded)
        print(json.dumps({'status': receipt['status'], 'archives': len(results),
                          'CPU_s': receipt['CPU_s'], 'wall_s': receipt['wall_s']}))
    except BaseException as error:
        (args.output / 'BACKUP_FAILURE.json').write_text(json.dumps(
            {'error': repr(error), 'archives_completed': len(results),
             'CPU_s': time.process_time() - cpu, 'wall_s': time.monotonic() - begin,
             'no_automatic_retry': True}, indent=2) + '\n')
        raise


if __name__ == '__main__':
    main()
