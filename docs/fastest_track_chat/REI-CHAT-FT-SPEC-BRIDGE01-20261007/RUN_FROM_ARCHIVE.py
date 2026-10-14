#!/usr/bin/env python3
"""Verify the pinned research archive, then run its isolated reproducer."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import zipfile


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--workspace', type=Path)
    p.add_argument('--rustc', type=Path)
    p.add_argument('--verify-only', action='store_true')
    a = p.parse_args()
    spec = json.loads(Path(__file__).with_name('ARCHIVE.json').read_text())
    data = a.archive.read_bytes()
    if len(data) != spec['bytes'] or hashlib.sha256(data).hexdigest() != spec['sha256']:
        raise ValueError('ARCHIVE_IDENTITY_MISMATCH')
    root = spec['root']
    with zipfile.ZipFile(a.archive) as z:
        names = z.namelist()
        if len(set(names)) != len(names):
            raise ValueError('DUPLICATE_ARCHIVE_PATH')
        for entry in z.infolist():
            parts = PurePosixPath(entry.filename).parts
            if not parts or parts[0] != root or '..' in parts or '\\' in entry.filename or stat.S_ISLNK(entry.external_attr >> 16):
                raise ValueError('UNSAFE_ARCHIVE_PATH')
        if z.testzip() is not None:
            raise ValueError('ARCHIVE_CRC_FAILURE')
        manifest = json.loads(z.read(root + '/MANIFEST.json'))
        if set(names) != {root + '/' + n for n in manifest} | {root + '/MANIFEST.json'}:
            raise ValueError('ARCHIVE_MANIFEST_COVERAGE')
        for name, info in manifest.items():
            payload = z.read(root + '/' + name)
            if len(payload) != info['bytes'] or hashlib.sha256(payload).hexdigest() != info['sha256']:
                raise ValueError('PAYLOAD_IDENTITY_MISMATCH: ' + name)
        print(json.dumps({'archive_verified': True, 'payload_files': len(manifest), 'science_rerun': not a.verify_only}), flush=True)
        if a.verify_only:
            return 0
        if a.workspace is None or a.rustc is None:
            p.error('--workspace and --rustc are required for execution')
        compiler = a.rustc.resolve(strict=True)
        workspace = a.workspace.resolve()
        workspace.mkdir(parents=True, exist_ok=False)
        z.extractall(workspace)
    return subprocess.call([sys.executable, str(workspace / root / 'reproduce.py'), '--output', str(workspace / 'reproduction'), '--rustc', str(compiler)])


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, zipfile.BadZipFile, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
