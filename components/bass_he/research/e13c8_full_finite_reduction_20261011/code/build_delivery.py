#!/usr/bin/env python3
"""Build a complete evidence ZIP and size-bounded transfer pieces, without science."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import zipfile


def pin(path):
    with path.open('rb') as f:
        return {'bytes': path.stat().st_size, 'sha256': hashlib.file_digest(f, 'sha256').hexdigest()}


def save(path, obj):
    with path.open('x') as f:
        json.dump(obj, f, indent=2, sort_keys=True); f.write('\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package', type=Path, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    a = ap.parse_args(); root = a.package.resolve()
    if a.output_dir.exists():
        raise FileExistsError('fresh delivery output required')
    a.output_dir.mkdir(parents=True)
    paths = sorted(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    if any(p.is_symlink() for p in paths):
        raise ValueError('regular payloads only')
    if any(p.name == 'PACKAGE_MANIFEST.json' for p in paths):
        raise FileExistsError('package is already sealed')
    pins = {p.relative_to(root).as_posix(): pin(p) for p in paths}
    manifest = {'schema': 'bass-he-e13c8-complete-manifest-v1', 'package_root': root.name,
                'files': pins, 'scientific_status': 'PROMOTE_SCOPED_FULL_FINITE_CAPTURED_OFF',
                'self_contained_original_inputs_and_actual_heavy_return': True,
                'new_NCP_heavy_tasks': 0, 'physical': 'HOLD', 'continuum': 'HOLD',
                'production': 'HOLD', 'receiver': 'HOLD'}
    manifest_path = root / 'PACKAGE_MANIFEST.json'; save(manifest_path, manifest)
    paths.append(manifest_path); paths.sort()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    temp = a.output_dir / ('BASS_HE_E13C8_COMPLETE_' + stamp + '.building.zip')
    with zipfile.ZipFile(temp, 'x', allowZip64=True, compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in paths:
            name = root.name + '/' + p.relative_to(root).as_posix()
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 11, 0, 0, 0))
            info.external_attr = (0o100644 << 16)
            info.compress_type = zipfile.ZIP_STORED if p.suffix == '.zip' else zipfile.ZIP_DEFLATED
            with p.open('rb') as src, z.open(info, 'w', force_zip64=True) as dst:
                for b in iter(lambda: src.read(1024 * 1024), b''):
                    dst.write(b)
    # Verify actual archived payloads, not only the source files used for packing.
    with zipfile.ZipFile(temp) as z:
        if len(z.namelist()) != len(paths) or len(set(z.namelist())) != len(paths):
            raise ValueError('unexpected archived file set')
        for rel, expected in pins.items():
            with z.open(root.name + '/' + rel) as f:
                count = 0; h = hashlib.sha256()
                for b in iter(lambda: f.read(1024 * 1024), b''):
                    h.update(b); count += len(b)
            if count != expected['bytes'] or h.hexdigest() != expected['sha256']:
                raise ValueError('archived payload changed: ' + rel)
    identity = pin(temp)
    archive = a.output_dir / ('BASS_HE_E13C8_COMPLETE_' + stamp + '_sha_' + identity['sha256'][:12] + '.zip')
    os.link(temp, archive); temp.unlink()
    parts = []; part_bytes = 64 * 1024**2
    with archive.open('rb') as f:
        number = 1
        while True:
            data = f.read(part_bytes)
            if not data:
                break
            p = a.output_dir / (archive.name + '.part%03d' % number)
            with p.open('xb') as o:
                o.write(data)
            parts.append({'index': number, 'canonical_name': p.name, **pin(p)})
            number += 1
    dependencies = {
        'E13C7_INPUT': {'relative_archive': 'dependencies/E13C7_INPUT.zip', **pin(root / 'dependencies/E13C7_INPUT.zip'),
            'manifest_name': 'BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1/PACKAGE_MANIFEST.json',
            'member_prefix': 'BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1/',
            'package_root': 'BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1'},
        'E13C7_NCP_RETURN': {'relative_archive': 'dependencies/E13C7_NCP_RETURN.zip', **pin(root / 'dependencies/E13C7_NCP_RETURN.zip'),
            'manifest_name': 'RETURN_MANIFEST.json', 'member_prefix': '', 'package_root': '.'}
    }
    transfer = {'schema': 'bass-he-e13c8-transfer-manifest-v1', 'package_root': root.name,
                'archive': {'canonical_name': archive.name, **identity}, 'parts': parts,
                'dependencies': dependencies, 'restore_helper': {'relative_path': 'restore_transfer.py', **pin(root / 'code/restore_transfer.py')},
                'name_policy': 'Identify inputs by actual bytes/SHA, including suffixed filenames; concatenate selected parts in manifest order.',
                'new_NCP_heavy_tasks': 0}
    transfer_path = a.output_dir / 'BASS_HE_E13C8_TRANSFER_MANIFEST.json'; save(transfer_path, transfer)
    report = {'status': 'PASS_ALL_ARCHIVED_PAYLOAD_BYTES', 'archive_path': str(archive.resolve()),
              'archive': identity, 'archive_members': len(paths), 'payload_files': len(pins),
              'payload_raw_bytes': sum(x['bytes'] for x in pins.values()),
              'package_manifest': pin(manifest_path), 'transfer_manifest': pin(transfer_path),
              'parts': parts, 'scientific_kernel_calls': 0,
              'restore_controls': 'PENDING_ACTUAL_SUFFIX_AND_MISSING_PART_CONTROLS'}
    save(a.output_dir / 'BUILD_RECEIPT.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
