#!/usr/bin/env python3
"""Build only a local C10 from a frozen Git commit; no native run or publication.

Preparation helper. It was syntax inspected, not executed against a final source
snapshot. Caller must finish source publication and independent readback first.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile
import tomllib
import zipfile

TASK = 'research/rei_age_exposure_envelope_20261018/'
V9_SHA = '5eef15a565636fa1e7c160aa30f3b2bb294dfa00364e504ee774f867c6ca4995'
NATIVE = '35d9747a0bbedcafdb568467ce7c1e7a25f965b6'
B1_SHA = '89c646db1de80c6e85fe34f7c3eaae2f10904810a8a6c3acc3426a7e7c1dd7a4'
RAW_NAME = 'REI_AGE32_BLOCKMAX_DIAGNOSTICS_NCP_20261020T112800Z.tar.gz'
RAW_PATH = 'archive_only/native_age32/' + RAW_NAME
RAW_SHA = '8c4579811faefbf3738c2dcd3c5105300a9aedec0b08c930bee032e094ef0cde'
RAW_SIZE = 1181985


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def tree_sha(rows):
    root = {}
    for row in rows:
        path = row['path']
        assert path.startswith(TASK)
        parts = path[len(TASK):].split('/')
        node = root
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        assert parts[-1] not in node
        node[parts[-1]] = (row['mode'], row['blob_sha'])

    def digest(node):
        records = []
        for name, value in node.items():
            if isinstance(value, dict):
                mode, identity, key = '40000', digest(value), name.encode() + b'/'
            else:
                mode, identity = value
                key = name.encode()
            records.append((key, mode.encode() + b' ' + name.encode() + b'\0' + bytes.fromhex(identity)))
        data = b''.join(record[1] for record in sorted(records))
        return hashlib.sha1(b'tree ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    return digest(root)


def read_source(repo, commit):
    listing = git(repo, 'ls-tree', '-r', '-z', commit, '--', TASK)
    records = []
    for item in listing.split(b'\0'):
        if not item:
            continue
        meta, raw_path = item.split(b'\t', 1)
        mode, kind, identity = meta.decode().split()
        path = raw_path.decode()
        assert kind == 'blob' and mode in ('100644', '100755')
        assert path.startswith(TASK) and '..' not in PurePosixPath(path).parts
        records.append({'path': path, 'mode': mode, 'blob_sha': identity})
    assert records
    request = ''.join(row['blob_sha'] + '\n' for row in records).encode()
    result = subprocess.run(['git', '-C', str(repo), 'cat-file', '--batch'], input=request,
                            stdout=subprocess.PIPE, check=True)
    stream = io.BytesIO(result.stdout)
    data_map = {}
    for row in records:
        identity, kind, size = stream.readline().decode().rstrip('\n').split()
        assert identity == row['blob_sha'] and kind == 'blob'
        data = stream.read(int(size))
        assert stream.read(1) == b'\n' and blob(data) == identity
        row.update(bytes=len(data), sha256=sha(data))
        data_map[row['path']] = data
    assert stream.read() == b''
    return records, data_map



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repo', 'prior-c10', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    for name in ('source-commit', 'expected-parent', 'expected-task-tree'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    assert not args.out.exists(), 'Output must be new; no existing files are overwritten.'
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
    old_bytes = args.prior_c10.read_bytes()
    assert sha(old_bytes) == V9_SHA
    with zipfile.ZipFile(io.BytesIO(old_bytes)) as prior:
        old = {path: prior.read(path) for path in prior.namelist() if path.startswith('archive_only/')}
        old_modes = {path: format(prior.getinfo(path).external_attr >> 16, 'o') for path in old}
    assert len(old) == 157
    raw_bytes = old[RAW_PATH]
    assert len(raw_bytes) == RAW_SIZE and sha(raw_bytes) == RAW_SHA
    assert not any(row['sha256'] == RAW_SHA for row in records), 'Do not duplicate raw tar in Git.'
    with tarfile.open(fileobj=io.BytesIO(raw_bytes), mode='r:gz') as archive:
        members = archive.getmembers()
        assert len(members) == 98 and sum(row.isfile() for row in members) == 94
        assert len({row.name for row in members}) == len(members)
        assert all((row.isfile() or row.isdir()) and not PurePosixPath(row.name).is_absolute()
                   and '..' not in PurePosixPath(row.name).parts for row in members)
    native = json.loads(data_map[TASK + 'contracts/NATIVE_INPUTS.json'])
    assert native['native_sha'] == NATIVE and len(native['files']) == 153
    for path, identity in native['files'].items():
        data = old['archive_only/runtime_base/native_original_35d9747/' + path]
        assert len(data) == identity['size'] and sha(data) == identity['sha256']
    assert sha(old['archive_only/runtime_base/blockmax_B1/positive_native.bin']) == B1_SHA
    mapping = json.loads(old['archive_only/B1_RESTORATION_MAP.json'])
    assert mapping['binary_sha256'] == B1_SHA and len(mapping['deduplicated_source_files']) == 161
    for row in mapping['deduplicated_source_files']:
        assert sha(data_map[row['source_archive_path']]) == row['sha256']
    vendor = TASK + 'vigilode_age_transport_20261019/rust/'
    lock = tomllib.loads(data_map[vendor + 'Cargo.lock'].decode())
    packages = [p for p in lock['package'] if p.get('source', '').startswith('registry+')]
    assert len(packages) == 22
    vendor_files = 0
    for package in packages:
        directory = vendor + 'vendor/' + package['name'] + '/'
        checks = json.loads(data_map[directory + '.cargo-checksum.json'])
        assert checks['package'] == package['checksum']
        for path, identity in checks['files'].items():
            assert sha(data_map[directory + path]) == identity
            vendor_files += 1
    assert vendor_files == 865
    layout = 'archive_only/RESTORATION_LAYOUT.md'
    text, changed = re.subn(r'\d+ task files committed in source commit [0-9a-f]{40}',
                           f'{len(records)} task files committed in source commit {args.source_commit}',
                           old[layout].decode())
    assert changed == 1
    # Only the source-binding layout changes among the 157 prior extra paths.
    data_map.update(old)
    data_map[layout] = text.encode()
    frozen = {'schema': 'rei.v10.c10_frozen_git_plan.v1', 'source_commit': args.source_commit,
              'baseline_commit': args.expected_parent, 'repository_root_tree': root_tree,
              'source_task_tree': task_tree, 'source_files': len(records), 'files': records,
              'prior_c10': str(args.prior_c10.resolve()), 'prior_c10_sha256': V9_SHA,
              'native32_archive_path': RAW_PATH, 'native32_sha256': RAW_SHA,
              'scientific_execution': 'NOT_RUN', 'remote_publication': 'EXTERNAL_RECEIPT_REQUIRED'}
    plan_bytes = encoded(frozen)
    receipt = {'schema': 'rei.delivery.package.v10', 'kind': 'C10', 'source_commit': args.source_commit,
               'source_parent': args.expected_parent, 'task_git_tree': task_tree,
               'source_files': len(records), 'included_source_files': len(records),
               'archive_only_files': len(old), 'omitted_source_paths': [],
               'vigilode_vendor_copies_in_archive': 1, 'frozen_source_plan_sha256': sha(plan_bytes),
               'restoration': layout, 'native32_archive_path': RAW_PATH, 'native32_sha256': RAW_SHA,
               'scientific_execution': 'NOT_RUN_BY_PACKAGING', 'remote_upload': 'NOT_RUN_BY_PACKAGING',
               'final_delivery_receipt': 'Post-publication/provider receipt and confirmation are external.',
               'PRODUCTION_SCIENTIFIC_ADMISSION': 'NOT_ISSUED'}
    data_map['PACKAGE_RECEIPT.json'] = encoded(receipt)
    manifest = {'schema': 'rei.package.payload_sha256.v2', 'source_commit': args.source_commit,
                'task_git_tree': task_tree,
                'files': {p: {'size': len(data), 'sha256': sha(data)} for p, data in sorted(data_map.items())},
                'manifest_self_hash': 'EXCLUDED_NO_RECURSIVE_SELF_HASH'}
    data_map['PAYLOAD_SHA256.json'] = encoded(manifest)
    args.out.mkdir(parents=True)
    (args.out / 'SOURCE_PLAN.json').write_bytes(plan_bytes)
    dest = args.out / 'REI_AGE_ENVELOPE_EXECUTION_READY_20261021_v10.zip'
    with zipfile.ZipFile(dest, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path, data in sorted(data_map.items()):
            info = zipfile.ZipInfo(path, date_time=(2026, 10, 21, 0, 0, 0))
            info.create_system = 3
            mode = source[path]['mode'] if path in source else old_modes[path] if path in old_modes else '100644'
            info.external_attr = int(mode, 8) << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(dest) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(data_map) and set(archive.namelist()) == set(data_map)
        for path, expected in manifest['files'].items():
            data = archive.read(path)
            assert len(data) == expected['size'] and sha(data) == expected['sha256']
            if path in source:
                assert blob(data) == source[path]['blob_sha']
                assert format(archive.getinfo(path).external_attr >> 16, 'o') == source[path]['mode']
        for path, data in old.items():
            if path != layout:
                assert archive.read(path) == data
            assert format(archive.getinfo(path).external_attr >> 16, 'o') == old_modes[path]
    result = {'schema': 'rei.C10.package_build_receipt.v10', 'source_commit': args.source_commit,
              'source_task_tree': task_tree, 'archives': [{'kind': 'C10', 'path': str(dest.resolve()),
                  'bytes': dest.stat().st_size, 'sha256': sha(dest.read_bytes()), 'zip_crc': 'PASS',
                  'all_payload_sha256': 'PASS', 'source_blob_and_mode_identity': 'PASS',
                  'included_source_files': len(records), 'source_task_tree': task_tree,
                  'archive_only_files': len(old), 'zip_entries': len(data_map)}],
              'baseline_native_inputs_preserved': 153, 'B1_binary_sha256': B1_SHA,
              'deduplicated_B1_source_files': 161, 'locked_vendor_packages': 22,
              'vendor_files_rehashed': 865, 'native32_original_archive_sha256': RAW_SHA,
              'native_runtime_reused_from_verified_v9': True,
              'scientific_execution': 'NOT_RUN', 'remote_upload': 'NOT_RUN',
              'PRODUCTION_SCIENTIFIC_ADMISSION': 'NOT_ISSUED'}
    (args.out / 'PACKAGE_BUILD_RECEIPT_20261021_v10.json').write_bytes(encoded(result))
    print(json.dumps({'status': 'PACKAGED_LOCAL_ONLY', 'archives': result['archives']}))


if __name__ == '__main__':
    main()
