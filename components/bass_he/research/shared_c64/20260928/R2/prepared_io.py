"""Standard-library delivery checks for the saved-trace research command.

Identity checks are not signatures or scientific admission. No spectral solver,
cloud process, network access, or numerical dependency is used in this module.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile


def read_trace_inputs(root: Path, manifest_path: Path) -> tuple[tuple[tuple[str, bytes], ...], dict]:
    """Verify seven pinned files and return the very bytes that were verified.

    The manifest must itself come from the caller's pinned delivery. This is a
    cooperative local-file integrity boundary, not a hostile-filesystem sandbox.
    """
    root = Path(root)
    manifest_raw = Path(manifest_path).read_bytes()
    manifest = json.loads(manifest_raw)
    if not isinstance(manifest, dict) or manifest.get('schema') != 'bass_he.fixed_trace_input.v1':
        raise ValueError('unsupported input manifest schema')
    entries = manifest.get('entries')
    if not isinstance(entries, list) or len(entries) != 7:
        raise ValueError('exactly seven manifest entries required')
    by_path = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError('invalid manifest entry')
        relative = entry.get('path')
        if not isinstance(relative, str):
            raise ValueError('invalid manifest path')
        path = PurePosixPath(relative)
        if (path.is_absolute() or str(path) != relative or len(path.parts) != 2
                or path.parts[0] != 'results' or path.suffix != '.json'
                or '..' in path.parts or '\\' in relative):
            raise ValueError('noncanonical manifest path')
        if relative in by_path:
            raise ValueError('duplicate manifest path')
        size, digest = entry.get('bytes'), entry.get('sha256')
        if (type(size) is not int or not 0 <= size <= 16 * 1024 * 1024
                or not isinstance(digest, str) or re.fullmatch('[0-9a-f]{64}', digest) is None):
            raise ValueError('invalid manifest size or digest')
        by_path[relative] = entry
    results = root / 'results'
    if root.is_symlink() or results.is_symlink():
        raise ValueError('symlink input root is not admitted')
    if not results.is_dir():
        raise ValueError('trace file set missing')
    observed = {f'results/{p.name}' for p in results.glob('*.json')}
    if observed != set(by_path):
        raise ValueError('trace file set differs from manifest')
    traces = []
    checked = []
    for relative, entry in sorted(by_path.items()):
        path = root / relative
        if path.is_symlink():
            raise ValueError('symlink trace is not admitted')
        if not path.is_file() or path.stat().st_size != entry['bytes']:
            raise ValueError(f'trace identity mismatch: {relative}')
        # Retain this buffer; the numerical caller must not reopen the path.
        payload = path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if len(payload) != entry['bytes'] or digest != entry['sha256']:
            raise ValueError(f'trace identity mismatch: {relative}')
        traces.append((relative, payload))
        checked.append({'path': relative, 'bytes': len(payload), 'sha256': digest})
    return tuple(traces), {
        'status': 'INPUT_IDENTITY_VERIFIED',
        'files_checked': len(traces),
        'manifest_sha256': hashlib.sha256(manifest_raw).hexdigest(),
        'files': checked,
        'scope': 'BYTE_IDENTITY_ONLY_NOT_SCIENTIFIC_VALIDATION',
    }


def tests_not_run() -> dict:
    """This command never executes pytest; historical logs are separate evidence."""
    return {'status': 'NOT_RUN_BY_THIS_COMMAND', 'passed': None, 'failed': None}


def require_new_output(path: Path) -> None:
    """Reject existing files and even dangling symlinks before expensive work."""
    if os.path.lexists(path):
        raise FileExistsError(f'output already exists; use a new path: {path}')


def publish_json(path: Path, document: dict) -> None:
    """Publish once via same-filesystem link after file fsync, then directory fsync.

    Existing results are never overwritten, including a racing publisher. This
    Linux/POSIX path requires hard-link support; no unsafe fallback is used.
    """
    path = Path(path)
    require_new_output(path)
    payload = (json.dumps(document, indent=2, allow_nan=False) + '\n').encode('utf-8')
    # Output parent must already be selected/prepared by the caller.
    fd, temporary_name = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)  # Atomic create-only publication; EEXIST is fatal.
        temporary.unlink()
        directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if temporary.exists():
            temporary.unlink()
