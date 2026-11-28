"""Archive the recovered source snapshot and explicitly selected run evidence.

This is not a full remote repository mirror or a portable binary certification.
Symlinks inside selected roots are materialized as regular files; original link
targets are recorded. Every stored payload is rehashed through the finished ZIP.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def package(repo, extras, output):
    repo, output = Path(repo).resolve(), Path(output).resolve()
    if output.exists() or output.suffix != '.zip' or output.is_relative_to(repo):
        raise ValueError('new ZIP path outside the source repository required')
    specs = [{'source': str(repo), 'target': 'repo', 'role': 'RECOVERED_SOURCE_AND_EVIDENCE'}, *extras]
    files, names, total = [], set(), 0
    for spec in specs:
        if set(spec) != {'source', 'target', 'role'}:
            raise ValueError('exact extra source/target/role keys required')
        source = Path(spec['source']).resolve(strict=True)
        target = PurePosixPath(spec['target'])
        if target.is_absolute() or '..' in target.parts or str(target) != spec['target']:
            raise ValueError('relative canonical archive target required')
        candidates = sorted(source.rglob('*')) if source.is_dir() else [source]
        root = source if source.is_dir() else source.parent
        for path in candidates:
            relative = path.relative_to(source) if source.is_dir() else PurePosixPath()
            if any(p in {'.git', '__pycache__', '.pytest_cache'} for p in relative.parts):
                continue
            if not path.is_file() or path.suffix in {'.pyc', '.pyo'}:
                continue
            if not path.resolve().is_relative_to(root):
                raise ValueError('source link escapes selected root')
            name = str(target / relative)
            if name in names or name == 'DELIVERY_MANIFEST.json':
                raise ValueError('duplicate archive path')
            names.add(name)
            size = path.stat().st_size
            total += size
            if size > 512 * 1024**2 or total > 1024 * 1024**2 or len(names) > 20000:
                raise ValueError('archive size/file budget exceeded')
            files.append((path, name, spec['role']))
    manifest = {'schema': 'WU088_NATIVE_EXECUTION_DELIVERY_V1',
                'full_remote_repository_mirror': False,
                'portable_binary_or_production_admission': False,
                'manifest_excludes_itself': True, 'files': []}
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path, name, role in files:
            data = path.read_bytes()
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100755 if path.stat().st_mode & 0o111 else 0o100644) << 16
            archive.writestr(info, data)
            row = {'path': name, 'bytes': len(data), 'sha256': digest(data), 'role': role}
            if path.is_symlink():
                row['materialized_link_target'] = str(path.readlink())
            manifest['files'].append(row)
        archive.writestr('DELIVERY_MANIFEST.json', json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError('archive CRC failure')
        for row in manifest['files']:
            data = archive.read(row['path'])
            if len(data) != row['bytes'] or digest(data) != row['sha256']:
                raise ValueError('archived payload identity mismatch')
    return {'path': str(output), 'bytes': output.stat().st_size,
            'sha256': digest(output.read_bytes()), 'payload_files': len(files),
            'zip_crc_and_payload_hashes_verified': True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True)
    parser.add_argument('--extras-json', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(json.dumps(package(args.repo, json.loads(Path(args.extras_json).read_text()), args.output), indent=2))
