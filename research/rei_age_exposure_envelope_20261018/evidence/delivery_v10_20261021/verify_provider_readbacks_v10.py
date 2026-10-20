#!/usr/bin/env python3
"""Verify whole remotely downloaded v10 archives without any scientific execution.

Mechanically adapted from the retained v9 verifier. Current source and package
identities are supplied by the current plans and receipts.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile
import tomllib
import zipfile

SOURCE = None
TREE = None
TASK = 'research/rei_age_exposure_envelope_20261018/'
EXPECTED = {}

def configure(plan, package):
    global SOURCE, TREE, EXPECTED
    SOURCE, TREE = plan['source_commit'], plan['source_task_tree']
    assert package['source_commit'] == SOURCE and package['source_task_tree'] == TREE
    archives = package['archives']
    assert len(archives) == 2 and {row['kind'] for row in archives} == {'C8', 'C10'}
    EXPECTED = {row['kind']: (row['bytes'], row['sha256']) for row in archives}
    assert plan['source_files'] == len(plan['files'])

B1 = '89c646db1de80c6e85fe34f7c3eaae2f10904810a8a6c3acc3426a7e7c1dd7a4'
NATIVE32 = '8c4579811faefbf3738c2dcd3c5105300a9aedec0b08c930bee032e094ef0cde'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def tree_identity(rows):
    root = {}
    for row in rows:
        assert row['path'].startswith(TASK)
        parts = row['path'][len(TASK):].split('/')
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
        data = b''.join(value for _, value in sorted(records))
        return hashlib.sha1(b'tree ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    return digest(root)


def verify(row, plan):
    kind = row['kind']
    data = Path(row['local_path']).read_bytes()
    expected_bytes, expected_hash = EXPECTED[kind]
    assert len(data) == expected_bytes
    assert sha(data) == expected_hash
    result = {k: v for k, v in row.items() if k not in ('download_url', 'file_uri')}
    result.update(bytes=len(data), sha256=sha(data), status='PASS_FULL_READBACK')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = z.namelist()
        assert len(names) == len(set(names))
        assert all(not PurePosixPath(p).is_absolute() and '..' not in PurePosixPath(p).parts for p in names)
        assert z.testzip() is None
        payload = json.loads(z.read('PAYLOAD_SHA256.json'))
        assert payload['source_commit'] == SOURCE and payload['task_git_tree'] == TREE
        assert set(payload['files']) == set(names) - {'PAYLOAD_SHA256.json'}
        for path, identity in payload['files'].items():
            member = z.read(path)
            assert len(member) == identity['size'] and sha(member) == identity['sha256'], path
        receipt = json.loads(z.read('PACKAGE_RECEIPT.json'))
        assert receipt['source_commit'] == SOURCE and receipt['task_git_tree'] == TREE
        assert receipt['kind'] == kind
        assert receipt['included_source_files'] == receipt['source_files'] == len(plan['files'])
        assert set(p for p in names if p.startswith(TASK)) == set(r['path'] for r in plan['files'])
        actual_rows = []
        for source in plan['files']:
            member = z.read(source['path'])
            assert len(member) == source['bytes'] and sha(member) == source['sha256']
            assert blob(member) == source['blob_sha']
            assert z.getinfo(source['path']).external_attr >> 16 == int(source['mode'], 8)
            actual_rows.append({'path': source['path'], 'mode': source['mode'], 'blob_sha': blob(member)})
        assert len(actual_rows) == len(plan['files']) and tree_identity(actual_rows) == TREE
        checks = {'whole_bytes_and_sha256': 'PASS', 'zip_crc': 'PASS', 'unique_safe_members': 'PASS',
                  'zip_entries': len(names), 'all_manifest_payloads': 'PASS',
                  'manifest_payload_count': len(payload['files']), 'source_blob_mode_count': len(actual_rows),
                  'source_blob_modes': 'PASS', 'source_task_tree': TREE, 'task_tree_reconstructed': 'PASS'}
        if kind == 'C10':
            native = json.loads(z.read(TASK + 'contracts/NATIVE_INPUTS.json'))
            assert native['native_sha'] == '35d9747a0bbedcafdb568467ce7c1e7a25f965b6'
            assert len(native['files']) == 153
            for path, identity in native['files'].items():
                member = z.read('archive_only/runtime_base/native_original_35d9747/' + path)
                assert len(member) == identity['size'] and sha(member) == identity['sha256']
            assert sha(z.read('archive_only/runtime_base/blockmax_B1/positive_native.bin')) == B1
            mapping = json.loads(z.read('archive_only/B1_RESTORATION_MAP.json'))
            assert mapping['binary_sha256'] == B1
            assert len(mapping['deduplicated_source_files']) == 161
            for source in mapping['deduplicated_source_files']:
                assert sha(z.read(source['source_archive_path'])) == source['sha256']
            vendor = TASK + 'vigilode_age_transport_20261019/rust/'
            lock = tomllib.loads(z.read(vendor + 'Cargo.lock').decode())
            packages = [p for p in lock['package'] if p.get('source', '').startswith('registry+')]
            assert len(packages) == 22
            content_files = 0
            for package in packages:
                directory = vendor + 'vendor/' + package['name'] + '/'
                checksum = json.loads(z.read(directory + '.cargo-checksum.json'))
                assert checksum['package'] == package['checksum']
                for path, identity in checksum['files'].items():
                    assert sha(z.read(directory + path)) == identity
                    content_files += 1
            assert content_files == 865
            raw_path = 'archive_only/native_age32/REI_AGE32_BLOCKMAX_DIAGNOSTICS_NCP_20261020T112800Z.tar.gz'
            raw = z.read(raw_path)
            assert len(raw) == 1181985 and sha(raw) == NATIVE32
            with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as tar:
                members = tar.getmembers()
                assert len(members) == 98 and sum(m.isfile() for m in members) == 94
                assert len({m.name for m in members}) == 98
                assert all((m.isfile() or m.isdir()) and not PurePosixPath(m.name).is_absolute()
                           and '..' not in PurePosixPath(m.name).parts for m in members)
            checks.update(native_original153='PASS', B1_binary_sha256=B1, B1_binary='PASS',
                          deduplicated_source161='PASS', vendor_packages=22, vendor_content_files=865,
                          vendor_lock_checksums='PASS', native32_bytes=len(raw), native32_sha256=NATIVE32,
                          native32_archive='PASS', native32_tar_members=98, native32_tar_regular_files=94)
        result['checks'] = checks
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download-receipt', type=Path, required=True)
    parser.add_argument('--source-plan', type=Path, required=True)
    parser.add_argument('--package-receipt', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    assert not args.out.exists()
    downloads = json.loads(args.download_receipt.read_text())
    plan = json.loads(args.source_plan.read_text())
    configure(plan, json.loads(args.package_receipt.read_text()))
    assert plan['source_commit'] == SOURCE and plan['source_task_tree'] == TREE
    assert downloads['source_commit'] == SOURCE and downloads['source_task_tree'] == TREE
    assert len(downloads['downloads']) == 4
    assert {(r['provider'], r['kind']) for r in downloads['downloads']} == {
        ('drive', 'C8'), ('drive', 'C10'), ('dropbox', 'C8'), ('dropbox', 'C10')}
    report = {'schema': 'rei.age.remote_full_readback.v10', 'source_commit': SOURCE, 'source_task_tree': TREE,
              'status': 'IN_PROGRESS', 'downloads': [], 'scientific_execution': 'NOT_RUN',
              'PRODUCTION_SCIENTIFIC_ADMISSION': 'NOT_ISSUED'}
    try:
        for row in downloads['downloads']:
            result = verify(row, plan)
            report['downloads'].append(result)
            print(json.dumps({'provider': row['provider'], 'kind': row['kind'], 'status': result['status']}, sort_keys=True), flush=True)
        report['status'] = 'PASS_FOUR_FULL_PROVIDER_READBACKS'
    except Exception as error:
        report['status'] = 'FAIL_PRESERVED'
        report['error'] = repr(error)
        raise
    finally:
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
