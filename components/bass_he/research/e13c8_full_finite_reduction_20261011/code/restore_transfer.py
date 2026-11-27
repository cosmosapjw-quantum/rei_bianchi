#!/usr/bin/env python3
"""Restore the complete E13C8 evidence from a ZIP or SHA-selected transfer parts.

The externally supplied manifest SHA is required. Downloaded filenames, including
an added .bin suffix, never establish identity. This program does no science.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import time
import zipfile


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def verify_file(path, pin):
    if not path.is_file() or path.is_symlink():
        raise ValueError('regular input file required: ' + str(path))
    actual = {'bytes': path.stat().st_size, 'sha256': sha(path)}
    if actual != {'bytes': pin['bytes'], 'sha256': pin['sha256']}:
        raise ValueError('file byte identity mismatch: ' + str(path))
    return actual


def save(path, obj):
    with path.open('x') as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write('\n'); f.flush(); os.fsync(f.fileno())


def extract(archive, destination, manifest_name, prefix):
    """Extract an already hash-verified ZIP while checking every manifest pin."""
    if destination.exists():
        raise FileExistsError('fresh extraction directory required')
    with zipfile.ZipFile(archive) as z:
        infos = z.infolist(); names = [x.filename for x in infos]
        if len(names) != len(set(names)) or len(names) > 50000:
            raise ValueError('duplicate or excessive archive members')
        if sum(x.file_size for x in infos) > 2 * 1024**3:
            raise ValueError('unexpected archive expansion')
        for i in infos:
            p = PurePosixPath(i.filename)
            if p.is_absolute() or str(p) != i.filename or any(x in ('', '.', '..') for x in p.parts):
                raise ValueError('noncanonical archive path')
            if '\\' in i.filename or ':' in i.filename or i.is_dir():
                raise ValueError('unsafe archive path')
            if stat.S_IFMT(i.external_attr >> 16) not in (0, stat.S_IFREG):
                raise ValueError('nonregular archive member')
        manifest_bytes = z.read(manifest_name)
        manifest = json.loads(manifest_bytes)
        pins = {prefix + k: v for k, v in manifest['files'].items()}
        if set(names) != set(pins) | {manifest_name}:
            raise ValueError('manifest/member set mismatch')
        destination.mkdir(parents=True, exist_ok=False)
        for i in infos:
            dest = destination / i.filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            h = hashlib.sha256(); count = 0
            with z.open(i) as src, dest.open('xb') as dst:
                for b in iter(lambda: src.read(1024 * 1024), b''):
                    h.update(b); count += len(b); dst.write(b)
            if i.filename != manifest_name:
                pin = pins[i.filename]
                if count != pin['bytes'] or h.hexdigest() != pin['sha256']:
                    raise ValueError('manifest payload mismatch: ' + i.filename)
        return {'members': len(infos), 'payload_files_verified': len(pins),
                'raw_bytes': sum(x.file_size for x in infos),
                'manifest_sha256': hashlib.sha256(manifest_bytes).hexdigest()}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--manifest-sha256', required=True)
    source = ap.add_mutually_exclusive_group(required=True)
    source.add_argument('--archive', type=Path)
    source.add_argument('--parts-dir', type=Path)
    ap.add_argument('--output-dir', type=Path, required=True)
    ap.add_argument('--hydrate', action='store_true', help='also restore original source/input and the completed heavy return')
    a = ap.parse_args(); start = time.monotonic()
    if a.output_dir.exists():
        raise FileExistsError('fresh output directory required; preserve previous attempts')
    a.output_dir.mkdir(parents=True, exist_ok=False)
    try:
        if sha(a.manifest) != a.manifest_sha256:
            raise ValueError('external transfer manifest identity mismatch')
        manifest = json.loads(a.manifest.read_bytes())
        if manifest['schema'] != 'bass-he-e13c8-transfer-manifest-v1':
            raise ValueError('unexpected transfer manifest schema')
        rootname = manifest['package_root']
        if not rootname or PurePosixPath(rootname).parts != (rootname,) or rootname in ('.', '..') or ':' in rootname or '\\' in rootname:
            raise ValueError('single safe package root required')
        for name, pin in manifest['dependencies'].items():
            if not name or PurePosixPath(name).parts != (name,) or name in ('.', '..') or ':' in name or '\\' in name:
                raise ValueError('single safe dependency key required')
            for field in ('relative_archive', 'manifest_name'):
                value = pin[field]; p = PurePosixPath(value)
                if not value or p.is_absolute() or str(p) != value or '..' in p.parts or ':' in value or '\\' in value:
                    raise ValueError('safe relative dependency path required')
            p = PurePosixPath(pin['package_root'])
            if p.is_absolute() or '..' in p.parts:
                raise ValueError('safe relative restored dependency root required')
        selected = []
        if a.archive:
            verify_file(a.archive, manifest['archive'])
            archive = a.archive.resolve()
        else:
            candidates = [p for p in a.parts_dir.iterdir() if p.is_file() and not p.is_symlink()]
            needed_sizes = {p['bytes'] for p in manifest['parts']}
            identities = {}
            for p in candidates:
                if p.stat().st_size in needed_sizes:
                    identities.setdefault((p.stat().st_size, sha(p)), []).append(p)
            for pin in manifest['parts']:
                matches = identities.get((pin['bytes'], pin['sha256']), [])
                if not matches:
                    raise FileNotFoundError('no actual-byte match for part ' + pin['canonical_name'])
                # Same-hash duplicate downloads have the same content. Pick a stable
                # path, preserve every source filename, and record the chosen file.
                chosen = sorted(matches, key=lambda p: str(p))[0]
                selected.append({'canonical_name': pin['canonical_name'],
                                 'actual_path': str(chosen.resolve()), **{k: pin[k] for k in ('bytes', 'sha256')}})
            if len({x['sha256'] for x in selected}) != len(selected):
                raise ValueError('ambiguous repeated part identity')
            archive = a.output_dir / 'REASSEMBLED_COMPLETE.zip'
        if a.parts_dir:
            h = hashlib.sha256(); count = 0
            with archive.open('xb') as out:
                for item in selected:
                    with Path(item['actual_path']).open('rb') as src:
                        for b in iter(lambda: src.read(1024 * 1024), b''):
                            out.write(b); h.update(b); count += len(b)
                out.flush(); os.fsync(out.fileno())
            if count != manifest['archive']['bytes'] or h.hexdigest() != manifest['archive']['sha256']:
                raise ValueError('reassembled ZIP byte identity mismatch')
        outer = extract(archive, a.output_dir / 'package', rootname + '/PACKAGE_MANIFEST.json', rootname + '/')
        root = a.output_dir / 'package' / rootname
        hydrated = {}
        if a.hydrate:
            for name, pin in manifest['dependencies'].items():
                dependency = root / pin['relative_archive']
                verify_file(dependency, pin)
                target = a.output_dir / 'runtime' / name
                hydrated[name] = extract(dependency, target, pin['manifest_name'], pin['member_prefix'])
                restored_root = (target / pin['package_root']).resolve()
                if not restored_root.is_relative_to(target.resolve()) or not restored_root.is_dir():
                    raise ValueError('restored dependency root is missing or outside its destination')
                hydrated[name]['directory'] = str(restored_root)
        receipt = {'schema': 'bass-he-e13c8-restore-receipt-v1', 'status': 'PASS_COMPLETE_RESTORE',
                   'archive': manifest['archive'], 'selected_parts': selected,
                   'manifest_sha256': a.manifest_sha256, 'outer': outer,
                   'hydrated_dependencies': hydrated, 'package_directory': str(root.resolve()),
                   'scientific_kernel_calls': 0, 'MPI_invocations': 0,
                   'automatic_retries': 0, 'elapsed_seconds': time.monotonic() - start}
        save(a.output_dir / 'RESTORE_RECEIPT.json', receipt)
        print(json.dumps(receipt, indent=2))
    except BaseException as exc:
        save(a.output_dir / 'FIRST_FAILURE.json', {'status': 'FAIL_PRESERVED_NO_AUTOMATIC_RETRY',
             'error_type': type(exc).__name__, 'error': str(exc), 'elapsed_seconds': time.monotonic() - start})
        raise


if __name__ == '__main__':
    main()
