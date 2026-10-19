#!/usr/bin/env python3
"""Read-only Git object delivery verification; never execute scientific code."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import stat
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
REPO = Path('/tmp/rei_run16_work/readback/git_checkout')
OLD_READBACK = REPO.parent
CANONICAL = Path('/tmp/rei_run16_repo/research/atomic_nuclear_ssot_20261017/run16')
PREFIX = 'research/atomic_nuclear_ssot_20261017/run16/'
COMMIT = 'b808f9afddf3943eb0533bf86596d8bebb911ddd'
TREE = '71fc204854692fa7d35afedf4e9dd079513c0314'
OLD = '2cc5e0862dbe9770ef83c0b2437e27627ec26524'
BASE = 'c875005e30d9de1ce7f426898e46fe912068412c'
ENV_OVERRIDES = {'GIT_OPTIONAL_LOCKS': '0', 'GIT_TERMINAL_PROMPT': '0',
                 'GIT_NO_LAZY_FETCH': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
ENV = dict(os.environ, **ENV_OVERRIDES)
COMMANDS = []
START = time.perf_counter()


def digest(b):
    return {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest(),
            'git_blob': hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()}


def write_new(path, b):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as f:
        f.write(b)


def json_bytes(x):
    return (json.dumps(x, ensure_ascii=False, indent=2) + '\n').encode()


def safe_rel(value):
    p = PurePosixPath(value)
    if (not value or p.is_absolute() or str(p) != value or '\\' in value
            or any(x in ('', '.', '..') for x in p.parts)):
        raise ValueError(f'unsafe relative path: {value!r}')
    return value


def command(stage, argv, data=None, save_stdout=True):
    t = time.perf_counter()
    r = subprocess.run(argv, cwd=REPO, env=ENV, input=data, capture_output=True)
    row = {'stage': stage, 'argv': argv, 'cwd': str(REPO),
           'environment_overrides': ENV_OVERRIDES, 'exit_code': r.returncode,
           'wall_seconds': time.perf_counter() - t,
           'stdout': digest(r.stdout), 'stderr': digest(r.stderr)}
    if data is not None:
        row['stdin'] = digest(data)
    if save_stdout:
        name = f'commands/{stage}.stdout'
        write_new(ROOT / name, r.stdout)
        row['stdout']['path'] = name
    if r.stderr:
        name = f'commands/{stage}.stderr'
        write_new(ROOT / name, r.stderr)
        row['stderr']['path'] = name
    COMMANDS.append(row)
    if r.returncode != 0:
        raise RuntimeError(f'{stage} exited {r.returncode}: {r.stderr.decode(errors="replace")[:2000]}')
    return r.stdout


def directory_inventory(root, excluded=()):
    result = []
    for folder, dirs, files in os.walk(root, followlinks=False):
        here = Path(folder)
        dirs[:] = sorted(d for d in dirs if d not in excluded)
        for name in sorted(files):
            p = here / name
            s = p.lstat()
            rel = p.relative_to(root).as_posix()
            if stat.S_ISLNK(s.st_mode):
                result.append({'path': rel, 'mode': 'symlink', 'target': os.readlink(p)})
            elif stat.S_ISREG(s.st_mode):
                result.append({'path': rel, 'mode': oct(stat.S_IMODE(s.st_mode)), **digest(p.read_bytes())})
            else:
                raise ValueError(f'nonordinary protected file: {p}')
    return sorted(result, key=lambda row: row['path'])


def protected_snapshot():
    return {
        'worktree': directory_inventory(REPO, excluded=('.git',)),
        'index': digest((REPO / '.git/index').read_bytes()),
        'HEAD_file': digest((REPO / '.git/HEAD').read_bytes()),
        'prior_receipts': directory_inventory(OLD_READBACK, excluded=('git_checkout',)),
        'canonical_run16': directory_inventory(CANONICAL),
    }


def parse_tree(data):
    out = {}
    for entry in data.split(b'\0'):
        if not entry:
            continue
        meta, rawpath = entry.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        path = rawpath.decode('utf-8')
        if not path.startswith(PREFIX):
            raise ValueError(f'out of scope tree path: {path}')
        rel = safe_rel(path[len(PREFIX):])
        if rel in out or kind != 'blob' or mode not in ('100644', '100755'):
            raise ValueError(f'nonordinary or duplicate tree entry: {entry!r}')
        out[rel] = {'git_mode': mode, 'git_blob': oid}
    return out


def parse_diff(data):
    items = data.split(b'\0')
    if items[-1] == b'':
        items.pop()
    if len(items) % 2:
        raise ValueError('unexpected raw diff record count')
    out = []
    for i in range(0, len(items), 2):
        meta, rawpath = items[i:i + 2]
        oldmode, newmode, oldoid, newoid, status = meta.decode().split()
        path = rawpath.decode('utf-8')
        if (not path.startswith(PREFIX) or oldmode != ':000000'
                or status != 'A' or oldoid != '0' * 40
                or newmode not in ('100644', '100755')):
            raise ValueError(f'non-add-only or out-of-scope change: {meta!r} {path}')
        out.append({'path': safe_rel(path[len(PREFIX):]), 'status': status,
                    'git_mode': newmode, 'git_blob': newoid})
    return out


def parse_batch(data, oids):
    pos = 0
    out = {}
    for expected in oids:
        end = data.index(b'\n', pos)
        fields = data[pos:end].decode().split()
        if len(fields) != 3 or fields[0] != expected or fields[1] != 'blob':
            raise ValueError(f'unexpected batch header: {fields}')
        count = int(fields[2])
        pos = end + 1
        value = data[pos:pos + count]
        if len(value) != count or data[pos + count:pos + count + 1] != b'\n':
            raise ValueError('truncated blob batch')
        if digest(value)['git_blob'] != expected:
            raise ValueError('Git blob content hash mismatch')
        out[expected] = value
        pos += count + 1
    if pos != len(data):
        raise ValueError('extra blob batch bytes')
    return out


def verify():
    before = protected_snapshot()
    write_new(ROOT / 'PROTECTED_BEFORE.json', json_bytes(before))
    head = command('01_preserved_head', ['git', 'rev-parse', 'HEAD']).decode().strip()
    if head != OLD:
        raise ValueError('pre-existing isolated checkout is not the verified checkpoint')
    manifest_bytes = (CANONICAL / 'SCIENCE_MANIFEST.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    entries = {}
    for row in manifest['files']:
        p = safe_rel(row['path'])
        if p in entries:
            raise ValueError('duplicate science manifest path')
        entries[p] = row
    if len(entries) != 116 or manifest['file_count_excluding_this_manifest'] != 116:
        raise ValueError('unexpected science manifest entry count')

    # Fetch only commit/tree objects first. Explicit depth includes c875 for the
    # requested complete add-only diff; no checkout, index update or FETCH_HEAD.
    command('02_fetch_final_commit', ['git', 'fetch', '--no-write-fetch-head',
            '--no-tags', '--no-recurse-submodules', '--depth=3', '--filter=blob:none',
            'origin', COMMIT])
    commit_raw = command('03_final_commit', ['git', 'cat-file', '-p', COMMIT])
    header = commit_raw.split(b'\n\n', 1)[0].decode()
    trees = [x[5:] for x in header.splitlines() if x.startswith('tree ')]
    parents = [x[7:] for x in header.splitlines() if x.startswith('parent ')]
    if trees != [TREE] or parents != [OLD]:
        raise ValueError('final commit tree/parent mismatch')
    new_tree = parse_tree(command('04_final_tree', ['git', 'ls-tree', '-r', '-z', COMMIT, '--', PREFIX.rstrip('/')]))
    old_tree = parse_tree(command('05_checkpoint_tree', ['git', 'ls-tree', '-r', '-z', OLD, '--', PREFIX.rstrip('/')]))
    if len(new_tree) != 117 or len(old_tree) != 46:
        raise ValueError('unexpected new/old tree count')
    if set(new_tree) != set(entries) | {'SCIENCE_MANIFEST.json'}:
        raise ValueError('science manifest/tree path mismatch')
    for p, row in entries.items():
        if new_tree[p] != {k: row[k] for k in ('git_mode', 'git_blob')}:
            raise ValueError(f'manifest Git identity mismatch: {p}')
    for p, row in old_tree.items():
        if new_tree.get(p) != row:
            raise ValueError(f'old verified file changed: {p}')
    new_paths = sorted(set(new_tree) - set(old_tree))
    if len(new_paths) != 71:
        raise ValueError('unexpected number of added paths')

    diff_argv = ['git', 'diff-tree', '--no-commit-id', '-r', '--raw', '-z',
                 '--no-renames', '--full-index']
    checkpoint_diff = parse_diff(command('06_diff_from_checkpoint', diff_argv + [OLD, COMMIT]))
    base_diff = parse_diff(command('07_diff_from_run15', diff_argv + [BASE, COMMIT]))
    if sorted(x['path'] for x in checkpoint_diff) != new_paths:
        raise ValueError('checkpoint diff does not exactly list 71 additions')
    if sorted(x['path'] for x in base_diff) != sorted(new_tree):
        raise ValueError('RUN15-base diff does not exactly list 117 RUN16 additions')

    # One explicit batch fetch of the newly added reachable blob objects. This
    # is the payload stage of the same delivery read; no repeated failed fetch.
    oids = sorted({new_tree[p]['git_blob'] for p in new_paths})
    object_list = ('\n'.join(oids) + '\n').encode()
    write_new(ROOT / 'NEW_BLOB_REQUEST.txt', object_list)
    command('08_fetch_new_payload_blobs', ['git', 'fetch', '--no-write-fetch-head',
            '--no-tags', '--no-recurse-submodules', '--filter=blob:none',
            'origin', '--stdin'], object_list)
    blobs = parse_batch(command('09_read_new_payload_blobs',
             ['git', 'cat-file', '--batch'], object_list, save_stdout=False), oids)

    remote_manifest = blobs[new_tree['SCIENCE_MANIFEST.json']['git_blob']]
    if remote_manifest != manifest_bytes:
        raise ValueError('remote SCIENCE_MANIFEST differs from canonical bytes')
    records = []
    for p in sorted(new_tree):
        row = new_tree[p]
        is_new = p in new_paths
        b = blobs[row['git_blob']] if is_new else (REPO / PREFIX / p).read_bytes()
        ident = digest(b)
        if ident['git_blob'] != row['git_blob']:
            raise ValueError(f'actual blob mismatch: {p}')
        if p != 'SCIENCE_MANIFEST.json':
            expected = entries[p]
            if any(ident[k] != expected[k] for k in ('bytes', 'sha256', 'git_blob')):
                raise ValueError(f'payload manifest mismatch: {p}')
        canonical = CANONICAL / p
        if canonical.read_bytes() != b:
            raise ValueError(f'canonical/raw byte mismatch: {p}')
        mode = '100755' if canonical.stat().st_mode & 0o111 else '100644'
        if mode != row['git_mode']:
            raise ValueError(f'canonical file mode mismatch: {p}')
        if is_new:
            target = ROOT / 'new_payload' / p
            write_new(target, b)
            target.chmod(0o755 if row['git_mode'] == '100755' else 0o644)
        records.append({'path': p, **ident, 'git_mode': row['git_mode'],
                        'new_at_final_science_commit': is_new,
                        'evidence': 'new Git blob bytes fetched and restored' if is_new else
                        'previously fetched Git bytes; current tree blob/mode unchanged'})

    after = protected_snapshot()
    write_new(ROOT / 'PROTECTED_AFTER.json', json_bytes(after))
    if before != after:
        raise ValueError('protected worktree/index/receipts/canonical source changed')
    actual_head = command('10_preserved_head_after', ['git', 'rev-parse', 'HEAD']).decode().strip()
    if actual_head != OLD:
        raise ValueError('checkpoint HEAD changed')
    payload_bytes = sum(x['bytes'] for x in records if x['path'] != 'SCIENCE_MANIFEST.json')
    if payload_bytes != manifest['payload_bytes_excluding_this_manifest']:
        raise ValueError('payload byte total mismatch')
    new_bytes = sum(x['bytes'] for x in records if x['new_at_final_science_commit'])
    return {
        'schema': 'rei.run16.final_science_git_readback.v1',
        'status': 'VERIFIED_ADD_ONLY_FINAL_SCIENCE_GIT_DELIVERY',
        'created_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'remote_repository': 'https://github.com/cosmosapjw-quantum/rei_bianchi',
        'remote_branch': 'research/rei-run16-gas-path-sensitivity-20261019',
        'remote_commit': COMMIT, 'remote_tree': TREE, 'remote_parent': OLD,
        'remote_commit_url': f'https://github.com/cosmosapjw-quantum/rei_bianchi/commit/{COMMIT}',
        'previous_readback_commit': OLD, 'RUN15_base': BASE,
        'scope': 'Delivery-only Git tree and byte restoration; no numerical results re-executed',
        'exact_command': [sys.executable, '-B', str(Path(__file__).resolve())],
        'script_identity': digest(Path(__file__).read_bytes()),
        'environment': {'python': platform.python_version(), 'platform': platform.platform(),
                        'executable': sys.executable},
        'source_manifest': {'canonical_path': str(CANONICAL / 'SCIENCE_MANIFEST.json'),
                            **digest(manifest_bytes), 'remote_bytes_identical': True},
        'payload': {'tree_paths': len(new_tree), 'manifest_payload_entries': len(entries),
                    'payload_bytes_excluding_manifest': payload_bytes,
                    'all_tree_modes_and_blob_ids_match_manifest': True,
                    'all_payload_hashes_sizes_and_canonical_bytes_match': True,
                    'new_paths_fetched_and_restored': len(new_paths),
                    'new_path_bytes_including_science_manifest': new_bytes,
                    'new_path_unique_git_blobs': len(oids),
                    'restored_new_payload_root': str(ROOT / 'new_payload'),
                    'old_46_tree_blob_ids_and_modes_unchanged': True,
                    'old_46_previous_verified_bytes_still_match': True,
                    'files': records},
        'diffs': {'from_checkpoint': {'only_additions': True, 'only_run16': True,
                                      'path_count': len(checkpoint_diff)},
                  'from_RUN15_base': {'only_additions': True, 'only_run16': True,
                                      'path_count': len(base_diff)}},
        'preservation': {'isolated_HEAD': actual_head, 'isolated_worktree_unchanged': True,
                         'isolated_index_unchanged': True, 'prior_receipts_unchanged': True,
                         'canonical_run16_unchanged': True,
                         'protected_before': digest((ROOT / 'PROTECTED_BEFORE.json').read_bytes()),
                         'protected_after': digest((ROOT / 'PROTECTED_AFTER.json').read_bytes()),
                         'allowed_mutation': 'Git object database and shallow metadata only'},
        'execution_counts': {'numerical_recomputations': 0, 'quadrature_runs': 0,
                             'native_RHS_calls': 0, 'native_IVP_runs': 0,
                             'test_runs': 0, 'old_archive_downloads': 0},
        'blockers': [], 'failed_attempts': 0,
        'command_log': 'COMMAND_LOG.json',
        'wall_seconds': time.perf_counter() - START,
    }


def main():
    receipt_path = ROOT / 'FINAL_SCIENCE_READBACK.json'
    if receipt_path.exists():
        raise SystemExit('Receipt already exists; this bounded verification is single-run')
    try:
        receipt = verify()
        code = 0
    except Exception as exc:
        receipt = {'schema': 'rei.run16.final_science_git_readback.v1',
                   'status': 'BLOCKED', 'remote_commit': COMMIT,
                   'error_type': type(exc).__name__, 'error': str(exc),
                   'no_retry_performed': True, 'command_log': 'COMMAND_LOG.json',
                   'execution_counts': {'numerical_recomputations': 0, 'quadrature_runs': 0,
                                        'native_RHS_calls': 0, 'native_IVP_runs': 0, 'test_runs': 0}}
        code = 1
    write_new(ROOT / 'COMMAND_LOG.json', json_bytes(COMMANDS))
    write_new(receipt_path, json_bytes(receipt))
    print(json.dumps({'status': receipt['status'], 'receipt': str(receipt_path),
                      **digest(receipt_path.read_bytes())}, ensure_ascii=False))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
