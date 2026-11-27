"""Create a deterministic checksum-manifested overlay/dependency delivery ZIP.

The source directory is a recovered dependency snapshot, not a claim that every
file in the remote Git tree is backed up here. Existing outputs are refused.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-repo', required=True, type=Path)
    ap.add_argument('--audit-db-directory', required=True, type=Path)
    ap.add_argument('--database-v1', required=True, type=Path)
    ap.add_argument('--database-v3', required=True, type=Path)
    ap.add_argument('--database-reconstructed', required=True, type=Path)
    ap.add_argument('--publication-json', required=True, type=Path)
    ap.add_argument('--output-directory', required=True, type=Path)
    args = ap.parse_args()
    out = args.output_directory.resolve()
    if out.exists() or out.with_suffix('.zip').exists():
        raise FileExistsError('create-only package output')
    repo = args.source_repo.resolve()
    if not repo.is_dir() or out.is_relative_to(repo):
        raise ValueError('output must be outside source repo')
    out.mkdir(parents=True)
    entries = []

    def copy(src, relative, role):
        if src.is_symlink() or not src.is_file():
            raise ValueError('regular file required: ' + str(src))
        data = src.read_bytes()
        dst = out / relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        with dst.open('xb') as stream:
            stream.write(data)
        entries.append({'path': relative, 'bytes': len(data), 'sha256': sha(data), 'role': role})

    for src in sorted(repo.rglob('*')):
        rel = src.relative_to(repo)
        if any(x in {'.git', '__pycache__', '.pytest_cache'} for x in rel.parts):
            continue
        if src.is_file() and src.suffix not in {'.pyc', '.pyo'}:
            copy(src, 'repo/' + rel.as_posix(), 'SOURCE_AND_RECORDED_EVIDENCE')
    for src, name in [(args.database_v1, 'v1_acquisition.sqlite'),
                      (args.database_v3, 'v3_acquisition.sqlite'),
                      (args.database_reconstructed, 'partial_reconstruction.sqlite')]:
        copy(src, 'inspected_databases/' + name, 'READ_ONLY_RECOVERED_DATABASE')
    for name in ['current_audit.sqlite', 'current_audit.sql', 'source_map.json', 'AUDIT_DB_VERIFICATION.json']:
        copy(args.audit_db_directory / name, 'current_audit/' + name, 'NEW_EXECUTION_AUDIT_NOT_ORIGINAL_DB')
    copy(args.publication_json, 'PUBLICATION.json', 'DETACHED_GIT_PUBLICATION_EVIDENCE')
    manifest = {
        'schema': 'WU088_PRODUCTION_SOLVER_DELIVERY_MANIFEST_V1',
        'scope': 'Additive implementation, current audit and recovered dependencies; not a full remote-repository mirror or completed production certificate',
        'full_remote_repository_backed_up': False,
        'original_deep_research_database_recovered': False,
        'production_admitted': False,
        'files': entries,
        'manifest_excludes_itself': True,
    }
    (out / 'DELIVERY_MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    archive = out.with_suffix('.zip')
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for src in sorted(out.rglob('*')):
            if not src.is_file():
                continue
            info = zipfile.ZipInfo(out.name + '/' + src.relative_to(out).as_posix(), (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, src.read_bytes())
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError('ZIP CRC failure')
        for row in entries:
            data = z.read(out.name + '/' + row['path'])
            if len(data) != row['bytes'] or sha(data) != row['sha256']:
                raise ValueError('ZIP member manifest mismatch')
    print(json.dumps({'archive': str(archive), 'bytes': archive.stat().st_size,
                      'sha256': sha(archive.read_bytes()), 'payload_files': len(entries),
                      'zip_crc_and_all_member_hashes_verified': True}, indent=2))


if __name__ == '__main__':
    main()
