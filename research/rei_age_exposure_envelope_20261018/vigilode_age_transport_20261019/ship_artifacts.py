"""Prepare reviewable Git API payloads and streamed v6 archives; never publish.

All frozen plans and API payloads must be written outside the repository tree.
The caller supplies exact existing-path ownership and the fetched PR199 tree.
"""
from pathlib import Path, PurePosixPath
import argparse
import base64
import hashlib
import json
import zipfile

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
REPO = TASK.parents[1]
TASK_PREFIX = 'research/rei_age_exposure_envelope_20261018/'
NEW_PREFIX = TASK_PREFIX + HERE.name + '/'
BASELINE_COMMIT = '0ae749e9fdb179729c018706dbd59c4f61732b6a'
BASELINE_ROOT = 'e199be9e2fd2e5c311e08e71a7ed173100935753'
BASELINE_TASK = '74c29763d58f324cfd657ef41e306d3ff289bfe1'
NATIVE = '35d9747a0bbedcafdb568467ce7c1e7a25f965b6'
PRIOR_C8_SHA = '2a2b61fea8a08d2ba28968e2c964f7124ba38802be89b860fc743394e09d64fc'
PRIOR_C10_SHA = 'fbf323e7e78b495a3c282a567897c0b87c02f6a4d2972adfe3b5f895f1064da5'
B1_SHA = '89c646db1de80c6e85fe34f7c3eaae2f10904810a8a6c3acc3426a7e7c1dd7a4'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob_sha(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode()


def write_json(path, value):
    path.write_bytes(encoded(value))


def load(path):
    return json.loads(path.read_text())


def safe_owned(path):
    pure = PurePosixPath(path)
    if pure.is_absolute() or '..' in pure.parts or not path.startswith(TASK_PREFIX):
        raise ValueError('Owned path outside task scope: ' + path)
    if any(part in {'target', '__pycache__', '.git', 'deliverables'} for part in pure.parts):
        raise ValueError('Runtime or recursive delivery path: ' + path)
    return path


def external_output(path):
    path = path.resolve()
    if path == REPO or REPO in path.parents:
        raise ValueError('Write plans/payloads outside the repository to prevent recursive snapshots')
    path.mkdir(parents=True, exist_ok=True)
    return path


def default_archive(kind):
    name = ('REI_AGE_ENVELOPE_C8_CODE_20261019_v5.zip' if kind == 'C8' else
            'REI_AGE_ENVELOPE_EXECUTION_READY_20261019_v5.zip')
    return TASK/'deliverables'/name


def baseline_records(path):
    obj = load(path)
    assert obj['commit'] == BASELINE_COMMIT
    assert obj['root_tree'] == BASELINE_ROOT
    assert obj['task_prefix'] == TASK_PREFIX
    tree = obj['task_tree']
    assert tree['sha'] == BASELINE_TASK and not tree.get('truncated', False)
    records = {TASK_PREFIX + row['path']: row for row in tree['tree'] if row['type'] == 'blob'}
    assert len(records) == 814
    return records


def source_bytes(record, prior):
    if record['origin'] == 'local':
        data = (REPO/record['path']).read_bytes()
    else:
        data = prior.read(record['path'])
    assert sha(data) == record['sha256'], 'Changed after plan: ' + record['path']
    assert blob_sha(data) == record['blob_sha']
    return data


def tree_sha(records):
    root = {}
    for row in records:
        assert row['path'].startswith(TASK_PREFIX)
        node = root
        parts = PurePosixPath(row['path'][len(TASK_PREFIX):]).parts
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = row

    def recurse(node):
        entries = []
        for name, value in node.items():
            directory = 'blob_sha' not in value
            digest = recurse(value) if directory else bytes.fromhex(value['blob_sha'])
            mode = b'40000' if directory else value['mode'].encode()
            entries.append(((name + ('/' if directory else '')).encode(),
                            mode + b' ' + name.encode() + b'\0' + digest))
        data = b''.join(value for _, value in sorted(entries))
        return hashlib.sha1(b'tree ' + str(len(data)).encode() + b'\0' + data).digest()
    return recurse(root).hex()


def make_plan(args):
    baseline = baseline_records(args.baseline_tree)
    owned = set(load(args.owned_paths)) if args.owned_paths else set()
    owned = {safe_owned(path) for path in owned}
    for path in HERE.rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:
            owned.add(safe_owned(path.relative_to(REPO).as_posix()))
    prior_path = args.prior_c10.resolve()
    assert sha(prior_path.read_bytes()) == PRIOR_C10_SHA
    assert sha(args.prior_c8.read_bytes()) == PRIOR_C8_SHA
    records, unresolved, unowned_drift = [], [], []
    with zipfile.ZipFile(prior_path) as prior:
        prior_names = set(prior.namelist())
        for path in sorted(set(baseline) | owned):
            before = baseline.get(path)
            local = REPO/path
            data, origin = None, None
            if local.is_file():
                candidate = local.read_bytes()
                if path in owned or (before and blob_sha(candidate) == before['sha']):
                    data, origin = candidate, 'local'
                else:
                    unowned_drift.append(path)
            if data is None and before and path in prior_names:
                candidate = prior.read(path)
                if blob_sha(candidate) == before['sha']:
                    data, origin = candidate, 'prior_c10'
            if data is None:
                unresolved.append(path)
                continue
            try:
                data.decode('utf-8')
                encoding = 'utf-8'
            except UnicodeDecodeError:
                encoding = 'base64'
            digest = blob_sha(data)
            records.append({'path': path, 'mode': before['mode'] if before else '100644',
                            'bytes': len(data), 'sha256': sha(data), 'blob_sha': digest,
                            'origin': origin, 'encoding': encoding,
                            'changed': before is None or before['sha'] != digest,
                            'owned': path in owned})
    if unresolved:
        raise RuntimeError('Cannot reconstruct exact baseline or owned inputs: ' + json.dumps(unresolved))
    changed = [row for row in records if row['changed']]
    assert all(row['owned'] for row in changed)
    plan = {'schema': 'rei.v6.shipping_plan.v1', 'baseline_commit': BASELINE_COMMIT,
            'baseline_root_tree': BASELINE_ROOT, 'baseline_task_tree': BASELINE_TASK,
            'source_task_tree': tree_sha(records), 'prior_c10': str(prior_path),
            'prior_c10_sha256': sha(prior_path.read_bytes()),
            'prior_c8': str(args.prior_c8.resolve()), 'prior_c8_sha256': PRIOR_C8_SHA,
            'files': records, 'changed_files': len(changed),
            'source_files': len(records), 'changed_bytes': sum(row['bytes'] for row in changed),
            'unowned_local_drift_excluded': unowned_drift,
            'scientific_execution': 'NOT_RUN', 'publication': 'NOT_RUN'}
    out = external_output(args.out)
    write_json(out/'SOURCE_PLAN.json', plan)
    print(json.dumps({'plan': str(out/'SOURCE_PLAN.json'), 'source_files': len(records),
                      'changed_files': len(changed), 'changed_bytes': plan['changed_bytes'],
                      'source_task_tree': plan['source_task_tree'],
                      'binary_changed_files': [row['path'] for row in changed if row['encoding'] == 'base64'],
                      'largest_changed_files': sorted(changed, key=lambda row: row['bytes'], reverse=True)[:5],
                      'unowned_local_drift_excluded': unowned_drift}))


def split_blob(data, encoding, output, stem, limit):
    content = data.decode('utf-8') if encoding == 'utf-8' else base64.b64encode(data).decode()
    result = []
    offset = 0
    while offset < len(content) or not result:
        low, high, best = offset + 1, len(content), offset
        if not content:
            best = 0
        while low <= high:
            end = (low + high)//2
            row = {'part_index': 999999, 'content': content[offset:end]}
            if len(encoded(row)) <= limit:
                best = end
                low = end + 1
            else:
                high = end - 1
        if content and best == offset:
            raise ValueError('Chunk limit too small')
        if encoding == 'base64' and best < len(content):
            best -= (best-offset) % 4
        path = output/f'{stem}_part_{len(result):04d}.json'
        write_json(path, {'part_index': len(result), 'content': content[offset:best]})
        assert path.stat().st_size <= limit
        result.append({'path': str(path), 'part_index': len(result),
                       'bytes': path.stat().st_size, 'sha256': sha(path.read_bytes())})
        offset = best
        if not content:
            break
    return result


def make_payload(args):
    plan = load(args.plan)
    output = external_output(args.out)
    limit = args.chunk_bytes
    assert 1024 <= limit <= 409600
    trees, current, blobs = [], [], []

    def flush():
        nonlocal current
        if not current:
            return
        body = {'base_tree': BASELINE_ROOT if not trees else 'REPLACE_WITH_PREVIOUS_TREE_SHA',
                'tree': current}
        path = output/f'CREATE_TREE_{len(trees):04d}.json'
        write_json(path, body)
        assert path.stat().st_size <= limit
        trees.append({'path': str(path), 'entries': len(current), 'bytes': path.stat().st_size,
                      'sha256': sha(path.read_bytes())})
        current = []

    with zipfile.ZipFile(plan['prior_c10']) as prior:
        for record in plan['files']:
            if not record['changed']:
                continue
            data = source_bytes(record, prior)
            entry = {'path': record['path'], 'mode': record['mode'], 'type': 'blob'}
            text = data.decode('utf-8') if record['encoding'] == 'utf-8' else None
            candidate = dict(entry, content=text) if text is not None else None
            if candidate is not None and len(encoded({'base_tree': BASELINE_ROOT, 'tree': [candidate]})) <= limit:
                entry = candidate
            else:
                encoding = 'utf-8' if text is not None else 'base64'
                parts = split_blob(data, encoding, output, f'BLOB_{len(blobs):04d}', limit)
                blobs.append({'path': record['path'], 'expected_blob_sha': record['blob_sha'],
                              'sha256': record['sha256'], 'file_bytes': len(data),
                              'api_encoding': encoding, 'parts': parts,
                              'instruction': 'Join part content in order; call create_blob, verify returned SHA before any tree request.'})
                entry['sha'] = record['blob_sha']
            prospective = {'base_tree': BASELINE_ROOT, 'tree': current + [entry]}
            # Reserve room for the longer later-batch placeholder string.
            if current and len(encoded(prospective)) + 32 > limit:
                flush()
            current.append(entry)
        flush()
    index = {'schema': 'rei.v6.git_api_payload.v1', 'baseline_commit': BASELINE_COMMIT,
             'initial_base_tree': BASELINE_ROOT, 'expected_final_task_tree': plan['source_task_tree'],
             'changed_files': plan['changed_files'], 'source_plan': str(args.plan.resolve()),
             'source_plan_sha256': sha(args.plan.read_bytes()), 'blob_requests_first': blobs,
             'tree_requests_in_order': trees, 'maximum_json_chunk_bytes': limit,
             'instructions': ['Create all listed large/binary blobs first and verify deterministic SHA.',
                              'Execute tree batches sequentially, setting base_tree to the previous response SHA.',
                              'No commit/ref update is performed by this helper. Commit only after final complete tree verification.'],
             'changed_blob_manifest': [{key: row[key] for key in ['path','mode','bytes','blob_sha','sha256']}
                                       for row in plan['files'] if row['changed']],
             'publication': 'NOT_RUN'}
    write_json(output/'GIT_API_PAYLOAD_INDEX.json', index)
    print(json.dumps({'index': str(output/'GIT_API_PAYLOAD_INDEX.json'),
                      'large_or_binary_blob_requests': len(blobs), 'tree_requests': len(trees),
                      'changed_files': plan['changed_files'], 'source_task_tree': plan['source_task_tree'],
                      'largest_payload_bytes': max([row['bytes'] for row in trees] +
                                                  [part['bytes'] for row in blobs for part in row['parts']])}))


def package(args):
    plan = load(args.plan)
    assert args.published_task_tree == plan['source_task_tree'], 'Published task tree must match frozen plan'
    assert len(args.source_commit) == 40 and all(ch in '0123456789abcdef' for ch in args.source_commit)
    source = {row['path']: row for row in plan['files']}
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=True)
    records = []
    with zipfile.ZipFile(plan['prior_c8']) as old_code, zipfile.ZipFile(plan['prior_c10']) as prior:
        assert sha(Path(plan['prior_c10']).read_bytes()) == plan['prior_c10_sha256'] == PRIOR_C10_SHA
        assert sha(Path(plan['prior_c8']).read_bytes()) == plan['prior_c8_sha256'] == PRIOR_C8_SHA
        old_code_paths = {name for name in old_code.namelist() if name.startswith(TASK_PREFIX)}
        for kind in ['C8','C10']:
            selected = set(source) if kind == 'C10' else {
                path for path in source if path in old_code_paths or
                (source[path]['changed'] and not path.startswith(NEW_PREFIX)) or
                (path.startswith(NEW_PREFIX) and
                 not path[len(NEW_PREFIX):].startswith(('inputs/','results/')))}
            archive_only = [name for name in prior.namelist() if name.startswith('archive_only/')] if kind == 'C10' else []
            payload = {path: {'bytes': source[path]['bytes'], 'sha256': source[path]['sha256']}
                       for path in selected}
            archive_data = {}
            for path in archive_only:
                data = prior.read(path)
                if path == 'archive_only/RESTORATION_LAYOUT.md':
                    text = data.decode()
                    text = text.replace('811 task files committed in source commit 9f85ea1a08063d27f1148b386b5e4fb0d4c16c28',
                                        f"{len(source)} task files committed in source commit {args.source_commit}")
                    data = text.encode()
                archive_data[path] = data
                payload[path] = {'bytes': len(data), 'sha256': sha(data)}
            if kind == 'C10':
                native = [path for path in archive_only if path.startswith('archive_only/runtime_base/native_original_35d9747/')]
                assert len(native) == 153
                native_manifest = json.loads(source_bytes(source[TASK_PREFIX+'contracts/NATIVE_INPUTS.json'], prior))
                assert native_manifest['native_sha'] == NATIVE and len(native_manifest['files']) == 153
                for name, identity in native_manifest['files'].items():
                    original = archive_data['archive_only/runtime_base/native_original_35d9747/'+name]
                    assert len(original) == identity['size'] and sha(original) == identity['sha256']
                restoration_map = json.loads(archive_data['archive_only/B1_RESTORATION_MAP.json'])
                for mapping in restoration_map['deduplicated_source_files']:
                    assert source[mapping['source_archive_path']]['sha256'] == mapping['sha256']
                assert sha(archive_data['archive_only/runtime_base/blockmax_B1/positive_native.bin']) == B1_SHA
            receipt = {'schema': 'rei.delivery.package.v6', 'kind': kind,
                       'source_commit': args.source_commit, 'source_parent': BASELINE_COMMIT,
                       'task_git_tree': plan['source_task_tree'], 'source_files': len(source),
                       'included_source_files': len(selected), 'archive_only_files': len(archive_only),
                       'omitted_source_paths': sorted(set(source)-selected),
                       'vigilode_vendor_copies_in_archive': 1,
                       'frozen_source_plan_sha256': sha(args.plan.read_bytes()),
                       'restoration': 'archive_only/RESTORATION_LAYOUT.md' if kind == 'C10' else 'Use C10 for inputs/results/native153/B1 restoration.',
                       'scientific_execution': 'NOT_RUN_BY_PACKAGING',
                       'remote_upload': 'NOT_RUN_BY_PACKAGING',
                       'final_delivery_receipt': 'Created after publication/upload/readback, outside immutable archive bytes.',
                       'PRODUCTION_SCIENTIFIC_ADMISSION': 'NOT_ISSUED'}
            receipt_data = encoded(receipt)
            payload['PACKAGE_RECEIPT.json'] = {'bytes': len(receipt_data), 'sha256': sha(receipt_data)}
            manifest_data = encoded({'schema': 'rei.package.payload_sha256.v2',
                                     'source_commit': args.source_commit, 'task_git_tree': plan['source_task_tree'],
                                     'files': {path: {'size': row['bytes'], 'sha256': row['sha256']}
                                               for path,row in sorted(payload.items())},
                                     'manifest_self_hash': 'EXCLUDED_NO_RECURSIVE_SELF_HASH'})
            name = ('REI_AGE_ENVELOPE_C8_CODE_20261019_v6.zip' if kind == 'C8' else
                    'REI_AGE_ENVELOPE_EXECUTION_READY_20261019_v6.zip')
            path = output/name
            with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
                for entry in sorted(set(payload) | {'PAYLOAD_SHA256.json'}):
                    if entry == 'PACKAGE_RECEIPT.json': data = receipt_data
                    elif entry == 'PAYLOAD_SHA256.json': data = manifest_data
                    elif entry in archive_data: data = archive_data[entry]
                    else: data = source_bytes(source[entry], prior)
                    info = zipfile.ZipInfo(entry, date_time=(2026,10,19,0,0,0))
                    info.create_system = 3
                    mode = source[entry]['mode'] if entry in source else ('100755' if entry.endswith('positive_native.bin') else '100644')
                    info.external_attr = int(mode,8) << 16
                    info.compress_type = zipfile.ZIP_DEFLATED
                    archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
            with zipfile.ZipFile(path) as archive:
                assert archive.testzip() is None
                assert set(archive.namelist()) == set(payload) | {'PAYLOAD_SHA256.json'}
                for entry,identity in payload.items():
                    data = archive.read(entry)
                    assert len(data) == identity['bytes'] and sha(data) == identity['sha256']
            records.append({'kind': kind, 'path': str(path), 'bytes': path.stat().st_size,
                            'sha256': sha(path.read_bytes()), 'zip_crc': 'PASS', 'all_payload_sha256': 'PASS',
                            'included_source_files': len(selected), 'source_task_tree': plan['source_task_tree'],
                            'archive_only_files': len(archive_only), 'zip_entries': len(payload)+1})
    write_json(output/'PACKAGE_BUILD_RECEIPT_20261019_v6.json', {
        'schema': 'rei.C8_C10.package_build_receipt.v6', 'source_commit': args.source_commit,
        'source_task_tree': plan['source_task_tree'], 'archives': records,
        'baseline_native_inputs_preserved': 153, 'B1_binary_sha256': B1_SHA,
        'native_inputs_binary_and_B1_restoration_map_copied_from_verified_v5': True,
        'scientific_execution': 'NOT_RUN', 'remote_upload': 'NOT_RUN'})
    print(json.dumps({'status': 'PACKAGED_LOCAL_ONLY', 'archives': records}))


def emit(args):
    # For hosts that need a small, resumable read of a generated JSON file.
    data = args.file.read_bytes()
    assert 0 <= args.offset <= len(data) and 1 <= args.length <= 294912
    part = data[args.offset:args.offset+args.length]
    print(json.dumps({'file_bytes': len(data), 'offset': args.offset,
                      'next_offset': args.offset+len(part),
                      'base64': base64.b64encode(part).decode()}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    plan = commands.add_parser('plan')
    plan.add_argument('--baseline-tree', type=Path, required=True)
    plan.add_argument('--owned-paths', type=Path)
    plan.add_argument('--prior-c8', type=Path, default=default_archive('C8'))
    plan.add_argument('--prior-c10', type=Path, default=default_archive('C10'))
    plan.add_argument('--out', type=Path, required=True)
    payload = commands.add_parser('git-payload')
    payload.add_argument('--plan', type=Path, required=True)
    payload.add_argument('--out', type=Path, required=True)
    payload.add_argument('--chunk-bytes', type=int, default=393216)
    pack = commands.add_parser('package')
    pack.add_argument('--plan', type=Path, required=True)
    pack.add_argument('--source-commit', required=True)
    pack.add_argument('--published-task-tree', required=True)
    pack.add_argument('--out', type=Path, required=True)
    reader = commands.add_parser('emit')
    reader.add_argument('--file', type=Path, required=True)
    reader.add_argument('--offset', type=int, default=0)
    reader.add_argument('--length', type=int, default=196608)
    args = parser.parse_args()
    {'plan': make_plan, 'git-payload': make_payload, 'package': package, 'emit': emit}[args.command](args)


if __name__ == '__main__':
    main()
