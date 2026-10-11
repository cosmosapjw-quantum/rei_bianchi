"""Fail-closed source-only audit of every proposed public commit, without network I/O.

Scope is the new range after the declared public base, not retroactive privacy
certification of already-public history. A private denylist may supplement the
generic detectors; its values are never printed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

HPC = 'research/accel02_20261011/q1b/hpc/'
C13 = 'research/accel02_20261011/q1b/c13/allocation/'
LEGACY = {C13 + name for name in ('prepare_runtime_allocation.py', 'run_full_history_chunk_v5.py')}
ALLOWED_SUFFIXES = {'.py', '.md', '.json', '.sh', '.sbatch', '.txt'}
PATTERNS = {
    'host_session_path': re.compile(r'/workspace/scratch/[0-9a-f]{8,}'),
    'private_home_path': re.compile(r'/home/[A-Za-z0-9_-]+/|/roo[t]/'),
    'drive_object_url': re.compile(r'https://drive\.google\.com/(?:file/d/|drive/folders/)[A-Za-z0-9_-]+'),
    'dropbox_object_id': re.compile(r'id:BSp[A-Za-z0-9_-]{12,}'),
    'dropbox_namespace': re.compile(r'ns:[0-9]{5,}'),
    'private_backup_folder': re.compile(r'BASS_DERIVATION_DOSSIERS_[0-9]{8}'),
    'token': re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})\b'),
    'private_key': re.compile(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----'),
}


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def permitted(path):
    if path == '.gitignore' or path in LEGACY:
        return True
    if not path.startswith(HPC):
        return False
    rel = Path(path.removeprefix(HPC))
    return (rel.suffix in ALLOWED_SUFFIXES and
            not set(rel.parts) & {'local_results', 'private', 'evidence', 'receipts', '__pycache__'})


def inspect(repo, base, head, *, forbidden_commits=(), deny_values=(), allowed_paths=None):
    if subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor', base, head],
                      capture_output=True).returncode:
        raise ValueError('PUBLIC_BASE_NOT_ANCESTOR')
    commits = git(repo, 'rev-list', '--reverse', f'{base}..{head}').decode().splitlines()
    if not commits:
        raise ValueError('EMPTY_PUBLIC_RANGE')
    findings, blobs = [], {}
    for forbidden in forbidden_commits:
        check = subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor', forbidden, head],
                               capture_output=True)
        if check.returncode == 0:
            findings.append({'kind': 'private_commit_ancestor', 'commit': forbidden})
        elif check.returncode != 1:
            raise ValueError('UNKNOWN_FORBIDDEN_COMMIT')
    def scan(text, location):
        for label, regex in PATTERNS.items():
            if regex.search(text):
                findings.append({'kind': label, 'location': location})
        if any(value and value in text for value in deny_values):
            findings.append({'kind': 'private_denylist_match', 'location': location})
    for commit in commits:
        parents = git(repo, 'rev-list', '--parents', '-n', '1', commit).decode().split()[1:]
        if len(parents) != 1:
            findings.append({'kind': 'unexpected_merge', 'commit': commit})
        scan(git(repo, 'show', '-s', '--format=%B', commit).decode(), commit + ':message')
        paths = git(repo, 'diff-tree', '--no-commit-id', '--name-only', '-r', '-z', commit).decode().split('\0')
        for path in filter(None, paths):
            sensitive_path = any(v and v in path for v in deny_values) or any(r.search(path) for r in PATTERNS.values())
            display_path = ('REDACTED_PATH_SHA256_' + hashlib.sha256(path.encode()).hexdigest()
                            if sensitive_path else path)
            location = commit + ':' + display_path
            scan(path, location)
            if sensitive_path:
                continue
            if not permitted(path) or (allowed_paths is not None and path not in allowed_paths):
                findings.append({'kind': 'path_not_allowlisted', 'location': location})
                continue
            entry = git(repo, 'ls-tree', commit, '--', path).decode().strip()
            if not entry:  # deletion: prior changed blobs are checked at their own commit
                continue
            mode, objtype, rest = entry.split(' ', 2)
            oid = rest.split('\t', 1)[0]
            if mode not in ('100644', '100755') or objtype != 'blob':
                findings.append({'kind': 'not_regular_source', 'location': location})
                continue
            data = git(repo, 'cat-file', 'blob', oid)
            if len(data) > 512 * 1024 or b'\x00' in data:
                findings.append({'kind': 'binary_or_oversized_source', 'location': location})
                continue
            try:
                content = data.decode('utf-8')
            except UnicodeDecodeError:
                findings.append({'kind': 'not_utf8', 'location': location})
                continue
            scan(content, location)
            blobs[oid] = {'path': path, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    return {'schema': 'rei.hpc.publication_audit.v1', 'base': base, 'head': head,
            'commits_checked': len(commits), 'unique_blobs_checked': len(blobs),
            'status': 'PASS_SOURCE_ONLY_NEW_HISTORY' if not findings else 'FAIL',
            'findings': findings, 'blobs': blobs,
            'exact_path_allowlist_checked': allowed_paths is not None,
            'existing_public_history_privacy_certified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--base', required=True)
    parser.add_argument('--head', default='HEAD')
    parser.add_argument('--forbid-commit', action='append', default=[])
    parser.add_argument('--private-denylist', type=Path)
    parser.add_argument('--allowlist', type=Path, help='JSON array of exact reviewed source paths')
    args = parser.parse_args()
    values = json.loads(args.private_denylist.read_text()) if args.private_denylist else []
    result = inspect(args.repo, args.base, args.head,
                     forbidden_commits=args.forbid_commit, deny_values=values,
                     allowed_paths=set(json.loads(args.allowlist.read_text())) if args.allowlist else None)
    print(json.dumps(result, indent=2))
    return 0 if not result['findings'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
