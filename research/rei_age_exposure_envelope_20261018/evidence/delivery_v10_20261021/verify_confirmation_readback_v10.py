#!/usr/bin/env python3
"""Independently validate a whole v10 confirmation and its exact UTF-8 restore delta.

Read-only with respect to Git, source archives, and providers. No science runs.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import zipfile

import verify_provider_readbacks_v10 as base

FINAL_TREE = None
FINAL_ROOT = None
SOURCE_ROOT = None

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ('confirmation', 'source-c10', 'source-plan', 'package-receipt', 'final-publication-receipt', 'repo', 'out'):
        parser.add_argument('--' + option, type=Path, required=True)
    for option in ('provider', 'file-id', 'final-head', 'sha256'):
        parser.add_argument('--' + option, required=True)
    parser.add_argument('--bytes', type=int, required=True)
    args = parser.parse_args()
    global FINAL_TREE, FINAL_ROOT, SOURCE_ROOT
    plan = json.loads(args.source_plan.read_text())
    package = json.loads(args.package_receipt.read_text())
    publication = json.loads(args.final_publication_receipt.read_text())
    base.configure(plan, package)
    SOURCE_ROOT = plan['repository_root_tree']
    FINAL_TREE, FINAL_ROOT = publication['delivery_task_tree'], publication['repository_root_tree']
    assert publication['delivery_commit'] == args.final_head
    source_count, final_count = len(plan['files']), publication['all_source_blob_modes_verified']
    assert not args.out.exists()
    assert args.provider in ('drive', 'dropbox')
    report = {'schema': 'rei.age.confirmation_full_readback.v10', 'provider': args.provider,
              'file_id': args.file_id, 'source_commit': base.SOURCE, 'source_task_tree': base.TREE,
              'delivery_head': args.final_head, 'final_task_tree': FINAL_TREE,
              'local_path': str(args.confirmation), 'status': 'IN_PROGRESS',
              'scientific_execution': 'NOT_RUN', 'PRODUCTION_SCIENTIFIC_ADMISSION': 'NOT_ISSUED'}
    try:
        raw = args.confirmation.read_bytes()
        assert len(raw) == args.bytes and base.sha(raw) == args.sha256
        report.update(bytes=len(raw), sha256=base.sha(raw))
        value = json.loads(raw.decode('utf-8'))
        assert value['schema'] == 'rei.age.delivery.confirmation.v10'
        assert value['source_snapshot'] == {'commit': base.SOURCE, 'root_tree': SOURCE_ROOT,
                                           'task_tree': base.TREE, 'source_files': source_count}
        assert value['delivery_head'] == args.final_head
        assert value['final_delivery'] == {'commit': args.final_head, 'root_tree': FINAL_ROOT,
                                          'task_tree': FINAL_TREE, 'source_files': final_count}
        assert value['PRODUCTION_SCIENTIFIC_ADMISSION'] == 'NOT_ISSUED'
        assert value['source_ancestor_of_delivery'] is True
        assert git(args.repo, 'rev-list', '--parents', '-n', '1', args.final_head).decode().split() == [args.final_head, base.SOURCE]
        assert git(args.repo, 'rev-parse', args.final_head + '^{tree}').decode().strip() == FINAL_ROOT
        assert git(args.repo, 'rev-parse', args.final_head + ':' + base.TASK.rstrip('/')).decode().strip() == FINAL_TREE

        archive_records = {row['kind']: row for row in value['archives']['archives']}
        assert len(value['archives']['archives']) == 2 and set(archive_records) == {'C8', 'C10'}
        readback = value['full_provider_readback']
        assert readback['status'] == 'PASS_FOUR_FULL_PROVIDER_READBACKS'
        assert len(readback['downloads']) == 4
        assert {(r['provider'], r['kind']) for r in readback['downloads']} == {(p, k) for p in ('drive', 'dropbox') for k in ('C8', 'C10')}
        uploads = {(r['provider'], r['kind']): r for r in value['provider_uploads']['uploads']}
        assert len(value['provider_uploads']['uploads']) == 4
        for receipt in (value['archives'], readback, value['provider_uploads'], value['source_publication']):
            assert receipt['source_commit'] == base.SOURCE and receipt['source_task_tree'] == base.TREE
        for row in readback['downloads']:
            package = archive_records[row['kind']]
            uploaded = uploads[row['provider'], row['kind']]
            assert (row['bytes'], row['sha256']) == base.EXPECTED[row['kind']]
            assert row['bytes'] == package['bytes'] == uploaded['bytes']
            assert row['sha256'] == package['sha256'] == uploaded['sha256']
            assert row['file_id'] == uploaded['provider_file_id']
        final_publication = value['final_publication']
        assert final_publication['delivery_commit'] == args.final_head
        assert final_publication['delivery_task_tree'] == FINAL_TREE
        assert final_publication['repository_root_tree'] == FINAL_ROOT
        assert final_publication['all_source_blob_modes_verified'] == final_count

        plan = json.loads(args.source_plan.read_text())
        assert plan['source_commit'] == base.SOURCE and plan['source_task_tree'] == base.TREE
        assert len(plan['files']) == source_count
        c10 = args.source_c10.read_bytes()
        assert (len(c10), base.sha(c10)) == base.EXPECTED['C10']
        restored, modes = {}, {}
        with zipfile.ZipFile(args.source_c10) as z:
            for row in plan['files']:
                data = z.read(row['path'])
                assert len(data) == row['bytes'] and base.sha(data) == row['sha256']
                assert base.blob(data) == row['blob_sha']
                assert z.getinfo(row['path']).external_attr >> 16 == int(row['mode'], 8)
                restored[row['path']], modes[row['path']] = data, row['mode']
        assert base.tree_identity([{'path': path, 'mode': modes[path], 'blob_sha': base.blob(data)}
                                   for path, data in restored.items()]) == base.TREE

        delta = value['restore_delta']
        assert delta['required_base_source_commit'] == base.SOURCE
        assert delta['required_base_task_tree'] == base.TREE
        assert delta['allowed_repo_relative_prefix'] == base.TASK
        assert delta['expected_result_task_tree'] == FINAL_TREE
        assert delta['confirmation_self_included'] is False
        assert delta['file_count'] == len(delta['files'])
        changed = {}
        diff = git(args.repo, 'diff', '--name-status', '--no-renames', '-z', base.SOURCE, args.final_head).split(b'\0')
        assert diff.pop() == b'' and len(diff) == 2 * len(delta['files'])
        for status, path_raw in zip(diff[::2], diff[1::2]):
            path = path_raw.decode('utf-8')
            assert status in (b'A', b'M') and path.startswith(base.TASK)
            assert path not in changed
            changed[path] = status.decode()
        assert sorted(changed) == delta['allowed_paths_exact']
        assert sorted(row['path'] for row in delta['files']) == sorted(changed)
        checks = []
        for row in delta['files']:
            path = row['path']
            assert not PurePosixPath(path).is_absolute() and '..' not in PurePosixPath(path).parts
            assert path.startswith(base.TASK) and row['encoding'] == 'utf-8' and row['type'] == 'blob'
            assert row['mode'] in ('100644', '100755')
            assert (path not in restored) == (changed[path] == 'A')
            if path in modes:
                assert row['mode'] == modes[path]
            data = row['content'].encode('utf-8')
            assert data.decode('utf-8') == row['content'] and b'\0' not in data
            assert len(data) == row['bytes'] and base.sha(data) == row['sha256']
            assert base.blob(data) == row['blob_sha']
            assert git(args.repo, 'show', args.final_head + ':' + path) == data
            restored[path], modes[path] = data, row['mode']
            checks.append({k: row[k] for k in ('path', 'mode', 'bytes', 'sha256', 'blob_sha')})
        assert len(restored) == final_count
        actual_rows = []
        for entry in git(args.repo, 'ls-tree', '-r', '-z', args.final_head, '--', base.TASK).split(b'\0'):
            if not entry:
                continue
            meta, path = entry.split(b'\t', 1)
            mode, kind, identity = meta.decode().split()
            path = path.decode('utf-8')
            assert kind == 'blob' and path in restored
            assert mode == modes[path] and identity == base.blob(restored[path])
            actual_rows.append({'path': path, 'mode': mode, 'blob_sha': identity})
        assert len(actual_rows) == final_count and {r['path'] for r in actual_rows} == set(restored)
        assert base.tree_identity(actual_rows) == FINAL_TREE
        report.update(status='PASS_WHOLE_CONFIRMATION_AND_EXACT_UTF8_RESTORE',
                      checks={'whole_bytes_and_sha256': 'PASS', 'utf8_json': 'PASS',
                              'source_and_final_git_bindings': 'PASS', 'four_archive_readback_bindings': 'PASS',
                              'exact_global_git_delta_paths': 'PASS', 'delta_file_count': len(delta['files']),
                              'delta_files_added': sum(v == 'A' for v in changed.values()),
                              'delta_files_modified': sum(v == 'M' for v in changed.values()),
                              'delta_bytes_modes_and_blobs': 'PASS', 'delta_matches_final_git_bytes': 'PASS',
                              'restoration_method': 'IN_MEMORY_EXACT_BYTES_MODES_AND_FILE_SET',
                              'base_source_files': source_count, 'restored_final_files': final_count,
                              'all_final_git_blobs_modes_and_paths': 'PASS', 'restored_task_tree': FINAL_TREE,
                              'confirmation_self_excluded': 'PASS'}, delta_files=checks)
    except Exception as error:
        report['status'] = 'FAIL_PRESERVED'
        report['error'] = repr(error)
        raise
    finally:
        args.out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'provider': args.provider, 'status': report['status'], 'bytes': report['bytes'],
                      'sha256': report['sha256'], 'delta_files': len(delta['files']), 'final_task_tree': FINAL_TREE}))


if __name__ == '__main__':
    main()
