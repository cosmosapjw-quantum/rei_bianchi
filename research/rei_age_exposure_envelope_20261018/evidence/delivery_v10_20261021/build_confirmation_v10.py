#!/usr/bin/env python3
"""Create an immutable post-delivery UTF-8 delta; no publication or native run."""
import argparse
import datetime
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
sys.dont_write_bytecode = True
import build_c10_v10 as core


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repo', 'package-receipt', 'readback-receipt', 'upload-receipt',
                 'source-publication-receipt', 'final-publication-receipt', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    for name in ('source-commit', 'delivery-head'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    assert not args.output.resolve().is_relative_to((args.repo / core.TASK).resolve())
    for commit in (args.source_commit, args.delivery_head):
        assert re.fullmatch('[0-9a-f]{40}', commit)
    assert args.source_commit != args.delivery_head
    subprocess.run(['git', '-C', str(args.repo), 'merge-base', '--is-ancestor',
                    args.source_commit, args.delivery_head], check=True)
    before_rows, before = core.read_source(args.repo, args.source_commit)
    after_rows, after = core.read_source(args.repo, args.delivery_head)
    old = {row['path']: row for row in before_rows}
    new = {row['path']: row for row in after_rows}
    trees, roots = [], []
    for commit, rows in ((args.source_commit, before_rows), (args.delivery_head, after_rows)):
        tree = core.git(args.repo, 'rev-parse', commit + ':' + core.TASK.rstrip('/')).decode().strip()
        assert core.tree_sha(rows) == tree
        trees.append(tree)
        roots.append(core.git(args.repo, 'rev-parse', commit + '^{tree}').decode().strip())
    diff = core.git(args.repo, 'diff', '--name-status', '--no-renames', '-z',
                    args.source_commit, args.delivery_head).split(b'\0')
    assert diff.pop() == b'' and len(diff) % 2 == 0 and diff
    changed = {}
    for status, path_bytes in zip(diff[::2], diff[1::2]):
        path = path_bytes.decode('utf-8')
        assert status in (b'A', b'M') and path.startswith(core.TASK)
        assert '..' not in PurePosixPath(path).parts and path not in changed
        changed[path] = status
    # Git's binary classification supplements strict UTF-8 decoding below.
    numstat = core.git(args.repo, 'diff', '--numstat', '--no-renames', '-z',
                      args.source_commit, args.delivery_head).split(b'\0')
    for entry in filter(None, numstat):
        added, deleted, path = entry.split(b'\t', 2)
        assert added != b'-' and deleted != b'-' and path.decode('utf-8') in changed
    delta, restored, modes = [], dict(before), {p: row['mode'] for p, row in old.items()}
    for path in sorted(changed):
        row, data = new[path], after[path]
        assert row['mode'] in ('100644', '100755') and b'\0' not in data
        assert (path not in old) == (changed[path] == b'A')
        if path in old:
            assert row['mode'] == old[path]['mode'], 'Existing-file mode change: ' + path
        content = data.decode('utf-8')
        assert content.encode('utf-8') == data
        delta.append({'path': path, 'mode': row['mode'], 'type': 'blob', 'encoding': 'utf-8',
                      'bytes': len(data), 'sha256': core.sha(data), 'blob_sha': core.blob(data),
                      'content': content})
        restored[path], modes[path] = content.encode('utf-8'), row['mode']
    assert restored == after and modes == {p: row['mode'] for p, row in new.items()}
    restored_rows = [{'path': p, 'mode': modes[p], 'blob_sha': core.blob(data)}
                     for p, data in restored.items()]
    assert core.tree_sha(restored_rows) == trees[1]
    pack, readback, upload = map(load, (args.package_receipt, args.readback_receipt, args.upload_receipt))
    source_pub, final_pub = map(load, (args.source_publication_receipt, args.final_publication_receipt))
    for receipt in (pack, readback, upload, source_pub):
        assert receipt['source_commit'] == args.source_commit
        assert receipt['source_task_tree'] == trees[0]
    assert readback['status'] == 'PASS_FOUR_FULL_PROVIDER_READBACKS'
    downloads = readback['downloads']
    pairs = {(r['provider'], r['kind']) for r in downloads}
    assert len(downloads) == 4 and pairs == {(p, k) for p in ('drive', 'dropbox') for k in ('C8', 'C10')}
    archives = {row['kind']: row for row in pack['archives']}
    assert len(pack['archives']) == 2 and set(archives) == {'C8', 'C10'}
    for row in downloads:
        assert row['sha256'] == archives[row['kind']]['sha256']
        assert row['bytes'] == archives[row['kind']]['bytes']
    assert final_pub['delivery_commit'] == args.delivery_head
    assert final_pub['delivery_task_tree'] == trees[1] and final_pub['repository_root_tree'] == roots[1]
    assert final_pub['all_source_blob_modes_verified'] == len(after)
    result = {
        'schema': 'rei.age.delivery.confirmation.v10',
        'finalized_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source_snapshot': {'commit': args.source_commit, 'root_tree': roots[0],
                            'task_tree': trees[0], 'source_files': len(before)},
        'delivery_head': args.delivery_head,
        'final_delivery': {'commit': args.delivery_head, 'root_tree': roots[1],
                           'task_tree': trees[1], 'source_files': len(after)},
        'archives': pack, 'full_provider_readback': readback, 'provider_uploads': upload,
        'source_publication': source_pub, 'final_publication': final_pub,
        'restore_delta': {'schema': 'rei.task_owned_utf8_restore_delta.v1',
            'required_base_source_commit': args.source_commit, 'required_base_task_tree': trees[0],
            'allowed_repo_relative_prefix': core.TASK, 'allowed_paths_exact': sorted(changed),
            'file_count': len(delta), 'encoding_semantics': 'Encode exact UTF-8 strings without normalization.',
            'files': delta, 'expected_result_task_tree': trees[1], 'confirmation_self_included': False},
        'local_delta_validation': 'PASS_EXACT_BYTES_MODES_FILE_SET_AND_GIT_TASK_TREE',
        'source_ancestor_of_delivery': True, 'scientific_execution': 'NOT_RUN_BY_CONFIRMATION',
        'PRODUCTION_SCIENTIFIC_ADMISSION': 'NOT_ISSUED', 'status': 'SOURCE_AND_DUAL_BACKUP_COMPLETE',
        'confirmation_own_delivery': 'Own checksum and provider acknowledgements remain external; upload and verify this immutable JSON afterward.'}
    data = core.encoded(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as stream:
        stream.write(data)
    print(json.dumps({'path': str(args.output), 'bytes': len(data), 'sha256': core.sha(data),
                      'restore_delta_files': len(delta), 'final_task_tree': trees[1]}))


if __name__ == '__main__':
    main()
