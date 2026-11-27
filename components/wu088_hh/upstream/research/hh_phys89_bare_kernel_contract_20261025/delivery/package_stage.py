"""Mechanical published-commit package and complete extraction verifier.

Only native Git blobs in the owned prefix and three explicit parent artifacts
are admitted. No dirty/untracked traversal and no nested parent ZIP extraction.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import subprocess
import zipfile

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
PREFIX = 'research/hh_phys89_bare_kernel_contract_20261025/'
PARENT_FILES = {
    'parent/PHYS88_FINAL_20261024_92dec7cdc1cf.zip': Path('/tmp/hh89_recovery/PHYS88_FINAL_20261024_92dec7cdc1cf.zip'),
    'parent/PHYS88_FINAL_DELIVERY_20261024.json': Path('/tmp/hh89_recovery/PHYS88_FINAL_DELIVERY_20261024.json'),
    'parent/PHYS88_FINAL_DELIVERY_TERMINAL_20261024.json': Path('/tmp/hh89_recovery/PHYS88_FINAL_DELIVERY_TERMINAL_20261024.json')}
MANIFEST = 'PACKAGE_MANIFEST.json'


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blobid(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def pack(commit, output, receipt):
    actual = git('rev-parse', '--verify', commit+'^{commit}').decode().strip()
    if commit != actual:
        raise ValueError('FULL_PUBLISHED_COMMIT_ID_REQUIRED')
    tree = git('rev-parse', actual+'^{tree}').decode().strip()
    records = git('ls-tree', '-r', '-z', actual, '--', PREFIX).split(b'\0')
    payloads, blob_ids = {}, {}
    for record in records:
        if not record:
            continue
        metadata, name = record.split(b'\t', 1)
        mode, kind, oid = metadata.decode().split()
        name = name.decode()
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise ValueError('REGULAR_COMMITTED_BLOB_REQUIRED')
        if '_links' in Path(name).name or not name.startswith(PREFIX):
            raise ValueError('PRIVATE_LINK_FILE_OR_UNOWNED_PATH')
        raw = git('show', actual+':'+name)
        if blobid(raw) != oid:
            raise ValueError('NATIVE_GIT_BLOB_MISMATCH')
        payloads[name] = raw
        blob_ids[name] = oid
    if not payloads or PREFIX+'CONTRACT.json' not in payloads:
        raise ValueError('NO_COMPLETE_PUBLISHED_UNIT')
    for name, path in PARENT_FILES.items():
        payloads[name] = path.read_bytes()
    manifest = {'schema': 'PHYS89_PUBLISHED_COMMIT_PACKAGE_V1', 'commit': actual, 'tree': tree,
                'owned_prefix': PREFIX, 'payload_sha256': {p: sha(v) for p, v in payloads.items()},
                'payload_bytes': {p: len(v) for p, v in payloads.items()},
                'actual_commit_blob_ids': blob_ids, 'manifest_self_excluded': True,
                'parent_zip_copies': 1, 'nested_parent_extraction': False,
                'stagewholeGET': 0}
    if output.exists() or receipt.exists():
        raise FileExistsError('CREATE_ONLY_PACKAGE_OR_RECEIPT_EXISTS')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name, raw in payloads.items():
            z.writestr(name, raw)
        z.writestr(MANIFEST, canonical(manifest))
    raw = output.read_bytes()
    summary = {'schema': 'PHYS89_PACKAGE_WHOLE_IDENTITY_V1', 'archive': output.name,
               'bytes': len(raw), 'whole_sha256': sha(raw), 'published_commit': actual,
               'published_tree': tree, 'payload_members': len(payloads), 'stagewholeGET': 0}
    with receipt.open('xb') as stream:
        stream.write(canonical(summary))
    print(json.dumps(summary))


def restore_verify(archive, receipt, destination):
    rec = json.loads(receipt.read_text())
    raw = archive.read_bytes()
    if len(raw) != rec['bytes'] or sha(raw) != rec['whole_sha256']:
        raise ValueError('WHOLE_SHA_OR_SIZE_MISMATCH')
    if destination.exists():
        raise FileExistsError('CREATE_ONLY_RESTORE_DIRECTORY_EXISTS')
    with zipfile.ZipFile(archive) as z:
        infos = z.infolist()
        names = [i.filename for i in infos]
        if len(names) != len(set(names)) or z.testzip() is not None:
            raise ValueError('DUPLICATE_MEMBER_OR_CRC_FAILURE')
        manifest = json.loads(z.read(MANIFEST))
        payloads = manifest['payload_sha256']
        if set(names) != set(payloads)|{MANIFEST}:
            raise ValueError('PAYLOAD_MEMBER_SET_MISMATCH')
        actual = manifest['commit']
        if actual != rec['published_commit'] or manifest['tree'] != rec['published_tree']:
            raise ValueError('RECEIPT_COMMIT_TREE_MISMATCH')
        # Bind against actual native Git tree, not a claim inside the ZIP.
        if git('rev-parse', actual+'^{tree}').decode().strip() != manifest['tree']:
            raise ValueError('ACTUAL_GIT_TREE_MISMATCH')
        expected = {}
        for row in git('ls-tree', '-r', '-z', actual, '--', PREFIX).split(b'\0'):
            if row:
                meta, name = row.split(b'\t', 1)
                expected[name.decode()] = meta.decode().split()[2]
        if expected != manifest['actual_commit_blob_ids']:
            raise ValueError('ACTUAL_COMMIT_BLOB_MANIFEST_MISMATCH')
        if set(payloads) != set(expected)|set(PARENT_FILES):
            raise ValueError('NONCOMMIT_OR_EXTRA_PAYLOAD')
        for name, digest in payloads.items():
            path = PurePosixPath(name)
            if path.is_absolute() or '..' in path.parts:
                raise ValueError('INVALID_MEMBER_PATH')
            member = z.read(name)
            if sha(member) != digest or len(member) != manifest['payload_bytes'][name]:
                raise ValueError('PAYLOAD_SHA_OR_SIZE_MISMATCH')
            if name in expected and blobid(member) != expected[name]:
                raise ValueError('ACTUAL_MEMBER_GIT_BLOB_MISMATCH')
        destination.mkdir(parents=True)
        for name in names:
            target = destination/name
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                stream.write(z.read(name))
        for name, digest in payloads.items():
            if sha((destination/name).read_bytes()) != digest:
                raise ValueError('EXTRACTED_PAYLOAD_REHASH_MISMATCH')
        if sha((destination/MANIFEST).read_bytes()) != sha(z.read(MANIFEST)):
            raise ValueError('EXTRACTED_MANIFEST_REHASH_MISMATCH')
    print(json.dumps({'status': 'PASS_WHOLE_SHA_CRC_ALL_PAYLOAD_ACTUAL_GIT_ALL_EXTRACTION_REHASH',
                      'members_extracted': len(names), 'nested_parent_extraction': 0,
                      'commit': actual, 'tree': manifest['tree']}))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='operation', required=True)
    create = sub.add_parser('pack')
    create.add_argument('--commit', required=True)
    create.add_argument('--output', type=Path, required=True)
    create.add_argument('--receipt', type=Path, required=True)
    verify = sub.add_parser('restore-verify')
    verify.add_argument('--archive', type=Path, required=True)
    verify.add_argument('--receipt', type=Path, required=True)
    verify.add_argument('--destination', type=Path, required=True)
    args = p.parse_args()
    if args.operation == 'pack':
        pack(args.commit, args.output, args.receipt)
    else:
        restore_verify(args.archive, args.receipt, args.destination)


if __name__ == '__main__':
    main()
