"""Restore an externally supplied private seed into a checkout, missing files only.

The archive SHA comes from a private upload receipt. No locator, credential,
physical data or provider object ID is embedded in this public program.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import re
import uuid
import zipfile

PREFIX = 'repos/rei_bianchi/'
MANIFEST = 'NCP_SEED_MANIFEST.json'


def file_sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def safe_target(repo, name):
    rel = PurePosixPath(name)
    if (not name.startswith(PREFIX) or rel.is_absolute() or '..' in rel.parts or
            '\\' in name or rel.as_posix() != name):
        raise ValueError('UNSAFE_ARCHIVE_PATH')
    parts = PurePosixPath(name[len(PREFIX):]).parts
    if not parts or '.git' in parts:
        raise ValueError('GIT_OR_EMPTY_ARCHIVE_PATH')
    target = repo.joinpath(*parts)
    for part in (target, *target.parents):
        if part == repo:
            break
        if part.is_symlink():
            raise ValueError('SYMLINK_RESTORE_PATH')
    if not target.resolve().is_relative_to(repo):
        raise ValueError('RESTORE_PATH_OUTSIDE_REPO')
    return target


def restore(archive, repo, expected_sha256, *, max_bytes=4 * 1024 ** 3):
    repo = Path(repo).resolve(strict=True)
    archive = Path(archive)
    if file_sha(archive) != expected_sha256:
        raise ValueError('SEED_ARCHIVE_SHA256')
    prepared, unchanged = [], 0
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        if len(names) != len(set(names)):
            raise ValueError('DUPLICATE_ARCHIVE_MEMBER')
        if sum(info.file_size for info in z.infolist()) > max_bytes:
            raise ValueError('SEED_UNCOMPRESSED_LIMIT')
        manifest = json.loads(z.read(MANIFEST))
        rows = manifest['files']
        listed = [row['path'] for row in rows]
        if len(listed) != len(set(listed)):
            raise ValueError('DUPLICATE_MANIFEST_MEMBER')
        if set(names) != set(listed) | {MANIFEST}:
            raise ValueError('UNLISTED_ARCHIVE_MEMBER')
        seed = safe_target(repo, manifest['seed_relative_path'])
        checkpoint = safe_target(repo, manifest['checkpoint_relative_path'])
        expected = manifest['checkpoint_manifest_sha256']
        if not re.fullmatch(r'[0-9a-f]{64}', expected) or not checkpoint.is_relative_to(seed):
            raise ValueError('SEED_CHECKPOINT_REFERENCE')
        by_name = {row['path']: row for row in rows}
        checkpoint_member = manifest['checkpoint_relative_path']+'/manifest.json'
        if checkpoint_member not in by_name or by_name[checkpoint_member]['sha256'] != expected:
            raise ValueError('SEED_CHECKPOINT_PIN_NOT_LISTED')
        # Preflight every member and existing destination before any writes.
        for row in rows:
            target = None if row['path'] == 'README.md' else safe_target(repo, row['path'])
            info = z.getinfo(row['path'])
            archived_mode = info.external_attr >> 16
            if stat.S_ISLNK(archived_mode) or info.is_dir():
                raise ValueError('SEED_NOT_REGULAR_FILE')
            mode = row['mode']
            if type(mode) is not int or mode < 0 or mode & 0o7000:
                raise ValueError('SEED_UNSAFE_FILE_MODE')
            payload = z.read(info)
            if len(payload) != row['bytes'] or hashlib.sha256(payload).hexdigest() != row['sha256']:
                raise ValueError('SEED_MEMBER_IDENTITY:' + row['path'])
            if target is None:
                continue
            if target.exists():
                if not target.is_file() or file_sha(target) != row['sha256']:
                    raise ValueError('EXISTING_FILE_DIFFERS:' + row['path'])
                if mode & 0o111 and not os.access(target, os.X_OK):
                    raise ValueError('EXISTING_EXECUTABLE_MODE_DIFFERS:' + row['path'])
                unchanged += 1
            else:
                prepared.append((row, target))
        for row, target in prepared:
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name + '.ncp-restore-' + uuid.uuid4().hex)
            try:
                with temporary.open('xb') as f:
                    f.write(z.read(row['path'])); f.flush(); os.fsync(f.fileno())
                os.chmod(temporary, 0o755 if row['mode'] & 0o111 else 0o644)
                os.link(temporary, target)  # refuse a concurrent overwrite
                fsync_dir(target.parent)
            finally:
                temporary.unlink(missing_ok=True)
                fsync_dir(target.parent)
    if file_sha(checkpoint/'manifest.json') != expected:
        raise ValueError('LATEST_CHECKPOINT_MANIFEST_MISMATCH')
    return {'schema': 'rei.hpc.seed_restore_receipt.v1', 'status': 'RESTORED_MEMBER_IDENTITIES',
            'archive_sha256': expected_sha256, 'created_files': len(prepared),
            'preserved_existing_files': unchanged, 'seed_root': str(seed),
            'checkpoint_path': str(checkpoint), 'checkpoint_manifest_sha256': expected,
            'scientific_validation': 'NOT_RUN', 'native_calls': 0}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive', required=True, type=Path)
    p.add_argument('--repo', required=True, type=Path)
    p.add_argument('--sha256', required=True)
    args = p.parse_args()
    print(json.dumps(restore(args.archive, args.repo, args.sha256), indent=2))


if __name__ == '__main__':
    main()
