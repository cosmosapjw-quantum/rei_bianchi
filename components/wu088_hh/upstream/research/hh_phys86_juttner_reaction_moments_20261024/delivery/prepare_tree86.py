#!/usr/bin/env python3
"""Prepare byte-preserving remote Git tree arguments from the existing Git index.

Read-only with respect to Git and remote services. Root stages and freezes first.
Binary blobs require separate create_blob responses before tree args can be sent.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess

PREFIX = 'research/hh_phys86_juttner_reaction_moments_20261024'


def git(repo, *args):
    return subprocess.check_output(['git', '-C', repo, *args])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', required=True)
    p.add_argument('--base-tree', required=True)
    p.add_argument('--output', required=True)
    args = p.parse_args()
    assert re.fullmatch('[0-9a-f]{40}', args.base_tree), 'explicit base tree required'
    assert git(args.repo, 'rev-parse', args.base_tree + '^{tree}').decode().strip() == args.base_tree
    out = Path(args.output)
    assert not out.exists(), 'create-only output already exists'
    tree, blobs, records = [], [], []
    for item in git(args.repo, 'ls-files', '--stage', '-z', '--', PREFIX).split(b'\0'):
        if not item:
            continue
        meta, path_bytes = item.split(b'\t', 1)
        mode, oid, stage = meta.decode('ascii').split()
        assert stage == '0' and mode in ('100644', '100755'), 'unmerged or nonregular index entry'
        path = path_bytes.decode('utf-8')
        assert path.startswith(PREFIX + '/')
        raw = git(args.repo, 'cat-file', 'blob', oid)
        assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == oid
        entry = {'path': path, 'mode': mode, 'type': 'blob'}
        try:
            content = raw.decode('utf-8')
            assert content.encode('utf-8') == raw
            if '\0' in content:
                raise UnicodeError('binary NUL')
            entry['content'] = content
        except UnicodeError:
            blobs.append({'repo_path': path, 'expected_git_blob_sha1': oid,
                          'create_blob_args': {'content': base64.b64encode(raw).decode('ascii'), 'encoding': 'base64'}})
            entry['sha'] = oid
        tree.append(entry)
        records.append({'path': path, 'git_mode': mode, 'git_blob_sha1': oid,
                        'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    assert tree, 'no indexed owned files'
    # Explicit deletion of an existing owned path would need a controller decision.
    base_paths = {r.split(b'\t', 1)[1].decode('utf-8') for r in
                  git(args.repo, 'ls-tree', '-r', '-z', args.base_tree, '--', PREFIX).split(b'\0') if r}
    current = {r['path'] for r in records}
    assert not base_paths - current, 'owned deletion requires explicit controller handling'
    result = {'schema': 'PHYS86_PREPARED_REMOTE_TREE_V1',
              'status': 'PREPARED_BINARY_BLOBS_REQUIRE_ACK' if blobs else 'PREPARED_NO_REMOTE_MUTATION',
              'base_tree': args.base_tree, 'owned_prefix': PREFIX,
              'create_tree_args': {'base_tree': args.base_tree, 'tree': tree},
              'required_create_blob_requests': blobs, 'indexed_payload': records,
              'newline_conversion': False, 'git_mutations': 0, 'remote_mutations': 0,
              'execution_note': 'For binary requests, root must first create each base64 blob and verify returned SHA before sending tree args.'}
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=True, indent=2)
        f.write('\n')
    print(json.dumps({'status': result['status'], 'output': str(out), 'owned_entries': len(tree),
                      'binary_blob_requests': len(blobs), 'git_mutations': 0, 'remote_mutations': 0}))


if __name__ == '__main__':
    main()
