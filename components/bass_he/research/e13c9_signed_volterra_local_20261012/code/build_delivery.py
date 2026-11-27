#!/usr/bin/env python3
"""Seal an actual E13C9 package, verify archived bytes, and create 64 MiB parts.

This is an evidence-transport builder. It neither imports scientific code nor
decides scientific admission. Wait for the owner to finish reports and review
before invoking it. A sealed package and its prior attempts are never overwritten.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import time
import zipfile

from restore_transfer import (CHUNK_BYTES, DEPENDENCIES, PACKAGE_ROOT, PACKAGE_SCHEMA,
                              PART_BYTES, PRIOR_RECOVERY, TRANSFER_SCHEMA, pin,
                              safe_relative, save, validate_transfer, verify_file)


def payload_paths(root):
    paths = []
    for current, directories, filenames in os.walk(root, followlinks=False):
        directories[:] = sorted(d for d in directories if d != '__pycache__')
        for directory in directories:
            if (Path(current) / directory).is_symlink():
                raise ValueError('symlink directory in package payload')
        for name in sorted(filenames):
            if name.endswith(('.pyc', '.pyo')):
                continue
            path = Path(current) / name
            if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode):
                raise ValueError('regular package payload required: ' + str(path))
            relative = path.relative_to(root).as_posix()
            safe_relative(relative)
            paths.append(path)
    return sorted(paths)


def create_archive(root, paths, target):
    with zipfile.ZipFile(target, 'x', allowZip64=True) as zipped:
        for path in paths:
            name = root.name + '/' + path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 12, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_STORED if path.suffix.lower() == '.zip' else zipfile.ZIP_DEFLATED
            with path.open('rb') as source, zipped.open(info, 'w', force_zip64=True) as destination:
                for data in iter(lambda: source.read(CHUNK_BYTES), b''):
                    destination.write(data)


def verify_archived_payloads(archive, rootname, payload_pins, manifest_pin):
    pins = {rootname + '/' + relative: identity for relative, identity in payload_pins.items()}
    pins[rootname + '/PACKAGE_MANIFEST.json'] = manifest_pin
    with zipfile.ZipFile(archive) as zipped:
        names = zipped.namelist()
        if len(names) != len(set(names)) or set(names) != set(pins):
            raise ValueError('archived membership differs from sealed payload manifest')
        for name, expected in pins.items():
            digest = hashlib.sha256()
            count = 0
            with zipped.open(name) as source:
                for data in iter(lambda: source.read(CHUNK_BYTES), b''):
                    count += len(data)
                    digest.update(data)
            if {'bytes': count, 'sha256': digest.hexdigest()} != expected:
                raise ValueError('actual archived payload identity mismatch: ' + name)
    return len(pins)


def split_archive(archive, output):
    parts = []
    with archive.open('rb') as source:
        index = 1
        while True:
            data = source.read(PART_BYTES)
            if not data:
                break
            path = output / (archive.name + '.part%03d' % index)
            with path.open('xb') as target:
                target.write(data)
                target.flush()
                os.fsync(target.fileno())
            parts.append({'index': index, 'canonical_name': path.name, **pin(path)})
            index += 1
    return parts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    root = args.package.resolve()
    if not root.is_dir() or root.name != PACKAGE_ROOT or args.package.is_symlink():
        raise ValueError('actual regular E13C9 package root required')
    output = args.output_dir.resolve()
    if output.exists() or args.output_dir.is_symlink():
        raise FileExistsError('fresh delivery output directory required')
    if output.is_relative_to(root):
        raise ValueError('delivery output must be outside the package')
    output.mkdir(parents=True, exist_ok=False)
    stage = 'INPUT_PAYLOADS'
    try:
        manifest_path = root / 'PACKAGE_MANIFEST.json'
        if manifest_path.exists() or manifest_path.is_symlink():
            raise FileExistsError('package is already sealed; preserve prior package and attempt')
        for item in DEPENDENCIES.values():
            verify_file(root / item['relative_archive'], item)
        helper = root / 'code/restore_transfer.py'
        verify_file(helper, pin(Path(__file__).with_name('restore_transfer.py')))
        paths = payload_paths(root)
        payload_pins = {path.relative_to(root).as_posix(): pin(path) for path in paths}
        if 'code/build_delivery.py' not in payload_pins or 'code/restore_transfer.py' not in payload_pins:
            raise ValueError('package must include its actual build and restore helpers')
        manifest = {'schema': PACKAGE_SCHEMA, 'package_root': PACKAGE_ROOT, 'files': payload_pins,
                    'self_contained_E13C8_complete_and_recovery_kit': True,
                    'dependency_pins': DEPENDENCIES,
                    'scientific_admission': 'SEE_RECORDED_INDEPENDENT_DECISION_IN_PACKAGE',
                    'new_NCP_heavy_tasks': 0, 'scientific_kernel_calls_by_builder': 0,
                    'physical': 'HOLD', 'continuum': 'HOLD', 'production': 'HOLD', 'receiver': 'HOLD',
                    'generated_cache_policy': 'exclude __pycache__ directories and .pyc/.pyo files'}
        save(manifest_path, manifest)
        manifest_identity = pin(manifest_path)
        paths.append(manifest_path)
        paths.sort()
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        temporary = output / ('BASS_HE_E13C9_COMPLETE_' + stamp + '.building.zip')
        stage = 'ARCHIVE_WRITE_AND_VERIFY'
        create_archive(root, paths, temporary)
        members = verify_archived_payloads(temporary, PACKAGE_ROOT, payload_pins, manifest_identity)
        identity = pin(temporary)
        archive = output / ('BASS_HE_E13C9_COMPLETE_' + stamp + '_sha_' + identity['sha256'][:12] + '.zip')
        os.link(temporary, archive)
        temporary.unlink()
        stage = 'PARTS_AND_TRANSFER_MANIFEST'
        parts = split_archive(archive, output)
        transfer = {'schema': TRANSFER_SCHEMA, 'package_root': PACKAGE_ROOT,
                    'archive': {'canonical_name': archive.name, **identity}, 'parts': parts,
                    'package_manifest': manifest_identity, 'dependencies': DEPENDENCIES,
                    'prior_recovery': PRIOR_RECOVERY,
                    'restore_helper': {'relative_path': 'restore_transfer.py', **pin(helper)},
                    'name_policy': 'Select actual bytes/SHA regardless of download suffix; preserve source names and concatenate in manifest order.',
                    'new_NCP_heavy_tasks': 0}
        validate_transfer(transfer)
        transfer_path = output / 'BASS_HE_E13C9_TRANSFER_MANIFEST.json'
        save(transfer_path, transfer)
        transfer_identity = pin(transfer_path)
        report = {'schema': 'bass-he-e13c9-delivery-build-receipt-v1',
                  'status': 'PASS_ALL_ARCHIVED_PAYLOAD_BYTES', 'finished_utc': datetime.now(timezone.utc).isoformat(),
                  'archive_path': str(archive), 'archive': identity, 'archive_members': members,
                  'payload_files': len(payload_pins), 'payload_raw_bytes': sum(p['bytes'] for p in payload_pins.values()),
                  'package_manifest': manifest_identity,
                  'transfer_manifest': {'path': str(transfer_path), **transfer_identity},
                  'restore_helper': pin(helper), 'parts': parts, 'scientific_kernel_calls': 0,
                  'MPI_invocations': 0, 'NCP_execute_invocations': 0, 'automatic_retries': 0,
                  'elapsed_seconds': time.monotonic() - started,
                  'provenance_limit': 'byte verification does not establish provider provenance or scientific admission'}
        save(output / 'BUILD_RECEIPT.json', report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except BaseException as error:
        save(output / 'FIRST_FAILURE.json', {
            'schema': 'bass-he-e13c9-delivery-build-failure-v1', 'status': 'FAIL_PRESERVED_NO_AUTOMATIC_RETRY',
            'stage': stage, 'error_type': type(error).__name__, 'error': str(error),
            'scientific_kernel_calls': 0, 'MPI_invocations': 0, 'NCP_execute_invocations': 0,
            'automatic_retries': 0, 'elapsed_seconds': time.monotonic() - started})
        raise


if __name__ == '__main__':
    raise SystemExit(main())
