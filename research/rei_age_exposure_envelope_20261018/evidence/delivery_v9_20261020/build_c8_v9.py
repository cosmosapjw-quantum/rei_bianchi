#!/usr/bin/env python3
"""Build a deterministic C8 from all frozen task Git blobs; local packaging only.

Preparation helper: syntax inspected before source freeze. Its actual build and
readback are the packaging gate after the controller freezes source identities.
"""
import argparse
import json
from pathlib import Path
import re
import zipfile

from build_c10_v9 import TASK, blob, encoded, git, read_source, sha, tree_sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repo', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    for name in ('source-commit', 'expected-parent', 'expected-task-tree'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    assert not args.out.exists(), 'Output must be absent; no existing files are overwritten.'
    for value in (args.source_commit, args.expected_parent, args.expected_task_tree):
        assert re.fullmatch('[0-9a-f]{40}', value)
    ancestry = git(args.repo, 'rev-list', '--parents', '-n', '1', args.source_commit).decode().split()
    assert ancestry == [args.source_commit, args.expected_parent]
    task_tree = git(args.repo, 'rev-parse', args.source_commit + ':' + TASK.rstrip('/')).decode().strip()
    assert task_tree == args.expected_task_tree
    root_tree = git(args.repo, 'rev-parse', args.source_commit + '^{tree}').decode().strip()
    records, data_map = read_source(args.repo, args.source_commit)
    assert tree_sha(records) == task_tree
    source = {row['path']: row for row in records}
    assert len(source) == len(records) == len(data_map)
    assert all(path.startswith(TASK) for path in data_map)
    frozen = {'schema': 'rei.v9.c8_frozen_git_plan.v1', 'source_commit': args.source_commit,
              'baseline_commit': args.expected_parent, 'repository_root_tree': root_tree,
              'source_task_tree': task_tree, 'source_files': len(records), 'files': records,
              'scientific_execution': 'NOT_RUN', 'remote_publication': 'EXTERNAL_RECEIPT_REQUIRED'}
    plan_bytes = encoded(frozen)
    receipt = {'schema': 'rei.delivery.package.v9', 'kind': 'C8', 'source_commit': args.source_commit,
               'source_parent': args.expected_parent, 'task_git_tree': task_tree,
               'source_files': len(records), 'included_source_files': len(records),
               'archive_only_files': 0, 'omitted_source_paths': [],
               'source_scope': 'ALL_FROZEN_TASK_GIT_BLOBS_WITH_MODES',
               'frozen_source_plan_sha256': sha(plan_bytes),
               'scientific_execution': 'NOT_RUN_BY_PACKAGING', 'remote_upload': 'NOT_RUN_BY_PACKAGING',
               'final_delivery_receipt': 'Post-publication/provider receipt and confirmation are external.',
               'PRODUCTION_SCIENTIFIC_ADMISSION': 'NOT_ISSUED'}
    data_map['PACKAGE_RECEIPT.json'] = encoded(receipt)
    manifest = {'schema': 'rei.package.payload_sha256.v2', 'source_commit': args.source_commit,
                'task_git_tree': task_tree,
                'files': {path: {'size': len(data), 'sha256': sha(data)}
                          for path, data in sorted(data_map.items())},
                'manifest_self_hash': 'EXCLUDED_NO_RECURSIVE_SELF_HASH'}
    manifest_bytes = encoded(manifest)
    data_map['PAYLOAD_SHA256.json'] = manifest_bytes
    assert len(data_map) == len(records) + 2
    args.out.mkdir(parents=True)
    (args.out / 'SOURCE_PLAN.json').write_bytes(plan_bytes)
    dest = args.out / 'REI_AGE_ENVELOPE_C8_CODE_20261020_v9.zip'
    with zipfile.ZipFile(dest, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path, data in sorted(data_map.items()):
            info = zipfile.ZipInfo(path, date_time=(2026, 10, 20, 0, 0, 0))
            info.create_system = 3
            mode = source[path]['mode'] if path in source else '100644'
            info.external_attr = int(mode, 8) << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    recovered = []
    with zipfile.ZipFile(dest) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        assert len(names) == len(set(names)) == len(data_map)
        assert set(names) == set(source) | {'PACKAGE_RECEIPT.json', 'PAYLOAD_SHA256.json'}
        assert not any(path.startswith('archive_only/') for path in names)
        assert archive.read('PAYLOAD_SHA256.json') == manifest_bytes
        readback_manifest = json.loads(archive.read('PAYLOAD_SHA256.json'))
        assert readback_manifest == manifest
        assert set(readback_manifest['files']) == set(names) - {'PAYLOAD_SHA256.json'}
        for path, expected in readback_manifest['files'].items():
            data = archive.read(path)
            assert len(data) == expected['size'] and sha(data) == expected['sha256']
            mode = format(archive.getinfo(path).external_attr >> 16, 'o')
            if path in source:
                identity = blob(data)
                assert identity == source[path]['blob_sha'] and mode == source[path]['mode']
                recovered.append({'path': path, 'mode': mode, 'blob_sha': identity})
            else:
                assert path == 'PACKAGE_RECEIPT.json' and mode == '100644'
        assert format(archive.getinfo('PAYLOAD_SHA256.json').external_attr >> 16, 'o') == '100644'
        assert tree_sha(recovered) == task_tree
    result = {'schema': 'rei.C8.package_build_receipt.v9', 'source_commit': args.source_commit,
              'source_parent': args.expected_parent, 'source_task_tree': task_tree,
              'archives': [{'kind': 'C8', 'path': str(dest.resolve()), 'bytes': dest.stat().st_size,
                  'sha256': sha(dest.read_bytes()), 'zip_crc': 'PASS', 'all_payload_sha256': 'PASS',
                  'source_blob_and_mode_identity': 'PASS', 'recovered_source_task_tree': tree_sha(recovered),
                  'included_source_files': len(records), 'source_task_tree': task_tree,
                  'archive_only_files': 0, 'zip_entries': len(data_map)}],
              'frozen_source_plan_sha256': sha(plan_bytes),
              'scientific_execution': 'NOT_RUN', 'remote_upload': 'NOT_RUN',
              'PRODUCTION_SCIENTIFIC_ADMISSION': 'NOT_ISSUED'}
    (args.out / 'PACKAGE_BUILD_RECEIPT_C8_20261020_v9.json').write_bytes(encoded(result))
    print(json.dumps({'status': 'PACKAGED_LOCAL_ONLY', 'archives': result['archives']}))


if __name__ == '__main__':
    main()
