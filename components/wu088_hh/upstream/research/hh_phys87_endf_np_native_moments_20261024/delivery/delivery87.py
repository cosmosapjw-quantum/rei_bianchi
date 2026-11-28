#!/usr/bin/env python3
"""Create-only PHYS87 scoped packages and verify/extract downloaded provider ZIPs."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import zipfile

BASE = 'f4a6d5505c845a046e3b81d33a2992a239ab4c8b'
PREFIXES = ('research/hh_phys87_endf_np_native_moments_20261024',)
DEPENDENCIES = {
    'PHYS86_FINAL_20261024_f4a6d5505c84.zip':
        (11759665, 'd41454b0900ca9afbd127632ac0c84c3561288a24587af8d53cee04f09fccb42'),
}
CHUNK = 1024 * 1024
SCHEMA = 'phys87-scoped-delivery-v1'


def require(value, message):
    if not value:
        raise ValueError(message)


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def identity(repo, head):
    require(re.fullmatch(r'[0-9a-f]{40}', head), '--head must be the explicit full 40-character commit SHA1')
    require(git(repo, 'rev-parse', '--show-object-format').strip() == b'sha1', 'SHA1 Git repository required')
    require(git(repo, 'rev-parse', head + '^{commit}').decode().strip() == head, 'commit identity mismatch')
    subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor', BASE, head], check=True)
    entries = {}
    raw = git(repo, 'ls-tree', '-r', '-z', head, '--', *PREFIXES)
    for record in raw.split(b'\0'):
        if not record:
            continue
        meta, name = record.split(b'\t', 1)
        mode, kind, oid = meta.decode('ascii').split()
        path = name.decode('utf-8')
        require(any(path.startswith(p + '/') for p in PREFIXES), 'unexpected Git path')
        require(kind == 'blob' and mode in ('100644', '100755'), 'regular Git blobs only: ' + path)
        entries[path] = {'git_blob_sha1': oid, 'git_mode': mode}
    for prefix in PREFIXES:
        require(any(p.startswith(prefix + '/') for p in entries), 'commit lacks required public prefix: ' + prefix)
    return {'commit': head, 'tree': git(repo, 'rev-parse', head + '^{tree}').decode().strip(),
            'base': BASE, 'public_prefixes': list(PREFIXES)}, entries


def file_hash(path):
    digest = hashlib.sha256()
    count = 0
    with open(path, 'rb') as src:
        while data := src.read(CHUNK):
            count += len(data)
            digest.update(data)
    return count, digest.hexdigest()


def regular(path):
    require(stat.S_ISREG(path.lstat().st_mode), 'regular non-symlink file required: ' + str(path))


def stable_file(path):
    s = path.stat()
    return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns)


def safe_name(name):
    require(isinstance(name, str) and name and '\\' not in name and '\0' not in name,
            'unsafe ZIP member name')
    p = PurePosixPath(name)
    require(not p.is_absolute() and p.as_posix() == name and all(x not in ('', '.', '..') for x in p.parts),
            'unsafe ZIP member: ' + name)
    return p


def is_tmp_url(path):
    # Exclude temporary-URL transport files by name, not ordinary provenance URLs in JSON.
    name = path.name.lower().replace('-', '').replace('_', '')
    return ('url' in name and any(tag in name for tag in ('tmp', 'temporary', 'signed'))) or name.endswith('downloadrequest.json')


def is_transport_file(path):
    if is_tmp_url(path):
        return True
    # Private downloader requests can have arbitrary filenames. Exclude those by
    # their actual JSON shape, and exclude responses carrying live signed links.
    if path.suffix.lower() != '.json':
        return False
    try:
        obj = json.loads(path.read_bytes())
    except (ValueError, UnicodeError):
        return False
    if isinstance(obj, dict) and 'url' in obj and {'expected_bytes', 'expected_sha256'} <= set(obj):
        return True
    raw = path.read_bytes().lower()
    return any(mark in raw for mark in (b'x-amz-signature=', b'x-goog-signature=', b'"temporary_link"', b'"download_url"', b'&sig=', b'?sig='))


def stream_member(archive, name, source, blob_size=None, compress=zipfile.ZIP_DEFLATED):
    safe_name(name)
    info = zipfile.ZipInfo(name, date_time=(2026, 10, 24, 0, 0, 0))
    info.compress_type = compress
    info.external_attr = 0o100644 << 16
    sha256 = hashlib.sha256()
    sha1 = hashlib.sha1()
    if blob_size is not None:
        sha1.update(('blob ' + str(blob_size) + '\0').encode('ascii'))
    count = 0
    with archive.open(info, 'w', force_zip64=True) as dest:
        while data := source.read(CHUNK):
            count += len(data)
            sha256.update(data)
            sha1.update(data)
            dest.write(data)
    if blob_size is not None:
        require(count == blob_size, 'Git blob length changed')
    result = {'path': name, 'bytes': count, 'sha256': sha256.hexdigest()}
    if blob_size is not None:
        result['git_blob_sha1'] = sha1.hexdigest()
    return result


def core_pack(args):
    repo = Path(args.repo).resolve()
    ident, entries = identity(repo, args.head)
    private = Path(args.private_root).resolve()
    deps = Path(args.dependencies_root).resolve()
    require(private.is_dir(), 'private-root must be the intake directory')
    require(deps.is_dir(), 'dependencies-root directory missing')
    private_files, excluded = [], []
    for folder, dirs, files in os.walk(private, followlinks=False):
        for name in dirs:
            require(not (Path(folder) / name).is_symlink(), 'private symlink directory forbidden')
        for name in sorted(files):
            source = Path(folder) / name
            regular(source)
            if is_transport_file(source):
                excluded.append(source.relative_to(private).as_posix())
            else:
                private_files.append(source)
    require(private_files, 'private intake is empty')
    for name, expected in DEPENDENCIES.items():
        source = deps / name
        regular(source)
        require(file_hash(source) == expected, 'pinned dependency mismatch: ' + name)
    output = Path(args.output).absolute()
    require(not output.exists(), 'create-only output already exists: ' + str(output))
    require(not output.is_relative_to(private), 'output may not be inside private-root')
    payload = []
    with open(output, 'xb') as raw_output:
        with zipfile.ZipFile(raw_output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
            for path, entry in sorted(entries.items()):
                oid = entry['git_blob_sha1']
                size = int(git(repo, 'cat-file', '-s', oid))
                process = subprocess.Popen(['git', '-C', str(repo), 'cat-file', 'blob', oid], stdout=subprocess.PIPE)
                try:
                    record = stream_member(archive, 'repo/' + path, process.stdout, blob_size=size)
                finally:
                    process.stdout.close()
                    code = process.wait()
                require(code == 0, 'git cat-file failed: ' + path)
                require(record['git_blob_sha1'] == oid, 'streamed Git blob hash mismatch: ' + path)
                record.update({'kind': 'repository', 'repo_path': path, 'git_mode': entry['git_mode']})
                payload.append(record)
            for source in sorted(private_files):
                before = stable_file(source)
                with open(source, 'rb') as src:
                    record = stream_member(archive, 'private/intake/' + source.relative_to(private).as_posix(), src)
                require(stable_file(source) == before, 'private file changed while packing: ' + str(source))
                record['kind'] = 'private_intake'
                payload.append(record)
            for name, expected in sorted(DEPENDENCIES.items()):
                source = deps / name
                with open(source, 'rb') as src:
                    record = stream_member(archive, 'dependencies/' + name, src,
                                           compress=zipfile.ZIP_STORED if name.endswith('.zip') else zipfile.ZIP_DEFLATED)
                require((record['bytes'], record['sha256']) == expected, 'dependency changed while packing: ' + name)
                record['kind'] = 'historical_dependency'
                payload.append(record)
            manifest = {'schema': SCHEMA, 'created_utc': utc(), 'stage': args.stage, **ident,
                        'payload': sorted(payload, key=lambda r: r['path']),
                        'frozen_input_manifest_sha256': args.freeze_sha,
                        'excluded_temporary_url_files': sorted(excluded),
                        'historical_parent_restore': {'status': 'REUSED_PRIOR_RESTORE_EVIDENCE',
                            'new_nested_restore_executions': 0,
                            'scope': 'Pinned dependency whole-byte validation only; no parent science replay or nested historical extraction.'}}
            encoded = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')
            archive.writestr('MANIFEST.json', encoded)
    size, sha256 = file_hash(output)
    return {'status': 'PACK_CREATED', 'operation': 'pack', 'created_utc': utc(), 'stage': args.stage,
            **ident, 'archive': output.name, 'archive_bytes': size, 'archive_sha256': sha256,
            'manifest_sha256': hashlib.sha256(encoded).hexdigest(),
            'counts': {'zip_created': 1, 'payload_members': len(payload),
                       'repository_blobs': len(entries), 'private_intake_files': len(private_files),
                       'historical_dependencies': len(DEPENDENCIES), 'members_including_manifest': len(payload) + 1,
                       'excluded_temporary_url_files': len(excluded)},
            'historical_parent_restore': manifest['historical_parent_restore'],
            'provider_backup_status': 'NOT_ESTABLISHED_BY_LOCAL_PACK'}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result


def restore(args):
    require(re.fullmatch(r'[0-9a-f]{64}', args.expected_sha256), 'expected whole-archive SHA256 required')
    archive_path = Path(args.archive).resolve()
    regular(archive_path)
    whole_size, whole_sha = file_hash(archive_path)
    require(whole_sha == args.expected_sha256, 'downloaded archive whole-byte SHA256 mismatch')
    ident, git_entries = identity(Path(args.repo).resolve(), args.head)
    output = Path(args.output).absolute()
    require(not output.exists(), 'create-only restore directory already exists: ' + str(output))
    with zipfile.ZipFile(archive_path, 'r') as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        require(len(names) == len(set(names)), 'duplicate ZIP member')
        for item in infos:
            safe_name(item.filename)
            require(not item.is_dir(), 'unexpected directory member')
            require(not stat.S_ISLNK(item.external_attr >> 16), 'ZIP symlink forbidden')
            require(not item.flag_bits & 1, 'encrypted member forbidden')
        require('MANIFEST.json' in names, 'manifest missing')
        manifest_bytes = archive.read('MANIFEST.json')  # Exhaustion checks its CRC.
        manifest = json.loads(manifest_bytes, object_pairs_hook=unique_object)
        require(manifest.get('schema') == SCHEMA, 'unknown manifest schema')
        for key, value in ident.items():
            require(manifest.get(key) == value, 'manifest Git identity mismatch: ' + key)
        require(manifest.get('stage') == args.stage, 'manifest stage mismatch')
        records = manifest.get('payload')
        require(isinstance(records, list), 'payload must be a list')
        by_name = {}
        for record in records:
            name = record['path']
            safe_name(name)
            require(name not in by_name and name != 'MANIFEST.json', 'duplicate/invalid payload record')
            require(type(record['bytes']) is int and record['bytes'] >= 0, 'invalid payload length')
            require(re.fullmatch(r'[0-9a-f]{64}', record['sha256']), 'invalid payload SHA256')
            by_name[name] = record
        require(set(names) == set(by_name) | {'MANIFEST.json'}, 'ZIP member list differs from manifest')
        repo_records = {r.get('repo_path'): r for r in records if r.get('kind') == 'repository'}
        require(len(repo_records) == sum(r.get('kind') == 'repository' for r in records), 'duplicate repository record')
        require(set(repo_records) == set(git_entries), 'repository manifest differs from fresh git ls-tree')
        for path, expected in git_entries.items():
            record = repo_records[path]
            require(record['path'] == 'repo/' + path, 'repository namespace mismatch')
            for key, value in expected.items():
                require(record.get(key) == value, 'repository blob identity mismatch: ' + path)
        dep_records = {r['path'].removeprefix('dependencies/'): r for r in records if r.get('kind') == 'historical_dependency'}
        require(set(dep_records) == set(DEPENDENCIES), 'dependency list mismatch')
        require(len(dep_records) == sum(r.get('kind') == 'historical_dependency' for r in records), 'duplicate dependency')
        for name, expected in DEPENDENCIES.items():
            r = dep_records[name]
            require(r['path'] == 'dependencies/' + name and (r['bytes'], r['sha256']) == expected,
                    'dependency pin mismatch: ' + name)
        for r in records:
            require(r.get('kind') in ('repository', 'historical_dependency', 'private_intake'), 'unknown payload kind')
            if r['kind'] == 'private_intake':
                require(r['path'].startswith('private/intake/') and len(PurePosixPath(r['path']).parts) > 2,
                        'private intake namespace mismatch')
                require(not is_tmp_url(PurePosixPath(r['path'])), 'temporary URL payload forbidden')
        # Exhaust every ZIP member before extracting: zipfile verifies every member CRC.
        payload_checked = git_checked = 0
        for name, record in sorted(by_name.items()):
            sha256 = hashlib.sha256()
            sha1 = hashlib.sha1(('blob ' + str(record['bytes']) + '\0').encode('ascii'))
            count = 0
            with archive.open(name, 'r') as src:
                while data := src.read(CHUNK):
                    count += len(data)
                    sha256.update(data)
                    sha1.update(data)
            require((count, sha256.hexdigest()) == (record['bytes'], record['sha256']), 'payload mismatch: ' + name)
            payload_checked += 1
            if record['kind'] == 'repository':
                require(sha1.hexdigest() == record['git_blob_sha1'], 'actual Git blob mismatch: ' + name)
                git_checked += 1
        # All archive/member/Git checks passed; create a fresh extraction directory now.
        output.mkdir(parents=False, exist_ok=False)
        extracted = 0
        for item in infos:
            target = output.joinpath(*PurePosixPath(item.filename).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(item.filename, 'r') as src, open(target, 'xb') as dest:
                while data := src.read(CHUNK):
                    dest.write(data)
            if item.filename == 'MANIFEST.json':
                expected = (len(manifest_bytes), hashlib.sha256(manifest_bytes).hexdigest())
            else:
                record = by_name[item.filename]
                expected = (record['bytes'], record['sha256'])
                if record.get('git_mode') == '100755':
                    target.chmod(0o755)
            require(file_hash(target) == expected, 'extracted-file mismatch: ' + item.filename)
            extracted += 1
    return {'status': 'RESTORE_VERIFIED', 'operation': 'restore', 'created_utc': utc(), 'stage': args.stage,
            **ident, 'archive': archive_path.name, 'archive_bytes': whole_size, 'archive_sha256': whole_sha,
            'extracted_directory': output.name,
            'counts': {'whole_zip_sha256_checked': 1, 'member_crc_checked': len(infos),
                       'payload_sha256_checked': payload_checked, 'git_blob_sha1_checked': git_checked,
                       'extracted_members_rehashed': extracted, 'historical_dependency_whole_bytes_checked': len(DEPENDENCIES),
                       'nested_historical_restore_executions': 0},
            'historical_parent_restore': manifest['historical_parent_restore'],
            'provider_backup_status': 'ONE_DOWNLOADED_ARCHIVE_VERIFIED;_PROVIDER_IDENTITY_REQUIRES_ROOT_RECEIPT'}



def source_paths(args):
    repo = Path(args.repo).resolve()
    ident, entries = identity(repo, args.head)
    private, deps = Path(args.private_root).resolve(), Path(args.dependencies_root).resolve()
    require(private.is_dir() and deps.is_dir(), 'input root missing')
    sources, excluded = {}, []
    for path, entry in sorted(entries.items()):
        source = repo / path
        regular(source)
        sources['repo/' + path] = (source, entry['git_blob_sha1'])
    for folder, dirs, files in os.walk(private, followlinks=False):
        require(all(not (Path(folder) / n).is_symlink() for n in dirs), 'private symlink directory forbidden')
        for name in sorted(files):
            source = Path(folder) / name
            regular(source)
            rel = source.relative_to(private).as_posix()
            if is_transport_file(source):
                excluded.append(rel)
            else:
                sources['private/intake/' + rel] = (source, None)
    for name in DEPENDENCIES:
        source = deps / name
        regular(source)
        sources['dependencies/' + name] = (source, None)
    return ident, sources, sorted(excluded)


def snapshot(args):
    ident, sources, excluded = source_paths(args)
    before = {name: stable_file(p) for name, (p, _) in sources.items()}
    records = {}
    for name, (p, expected_blob) in sorted(sources.items()):
        size, digest = file_hash(p)
        record = {'bytes': size, 'sha256': digest, 'stat_before': list(before[name])}
        if expected_blob:
            # Native Git computes expected blob identity over exact raw bytes, without
            # checkout filters, newline conversion, or writing a Git object.
            with p.open('rb') as src:
                actual_blob = subprocess.check_output(['git', '-C', args.repo, 'hash-object', '--no-filters', '--stdin'], stdin=src).decode().strip()
            require(actual_blob == expected_blob, 'working bytes differ from committed Git blob: ' + name)
            record['git_blob_sha1'] = actual_blob
        if name.startswith('dependencies/'):
            require((size, digest) == DEPENDENCIES[p.name], 'parent dependency identity mismatch')
        records[name] = record
    for name, (p, _) in sources.items():
        require(stable_file(p) == before[name], 'input stats changed during freeze: ' + name)
        records[name]['stat_after'] = list(stable_file(p))
    return {'schema': 'PHYS87_ROOT_INPUT_FREEZE_V1', 'stage': args.stage, **ident,
            'files': records, 'excluded_transport_files': excluded}


def freeze(args):
    output = Path(args.output).absolute()
    private = Path(args.private_root).resolve()
    require(not output.is_relative_to(private), 'freeze output must be outside private intake')
    require(not output.exists(), 'create-only freeze output exists')
    doc = snapshot(args)
    raw = (json.dumps(doc, sort_keys=True, indent=2) + '\n').encode('utf-8')
    with output.open('xb') as dest:
        dest.write(raw)
    return {'status': 'INPUT_FREEZE_PREPARED_REQUIRES_ROOT_ADOPTION', 'operation': 'freeze',
            'stage': args.stage, 'head': args.head, 'manifest': output.name,
            'manifest_bytes': len(raw), 'manifest_sha256': hashlib.sha256(raw).hexdigest(),
            'input_files': len(doc['files']), 'scientific_executions': 0}


def pack(args):
    require(re.fullmatch('[0-9a-f]{64}', args.freeze_sha), 'explicit root-adopted freeze SHA256 required')
    p = Path(args.freeze_manifest)
    regular(p)
    raw = p.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == args.freeze_sha, 'root freeze manifest bytes mismatch')
    expected = json.loads(raw, object_pairs_hook=unique_object)
    require(snapshot(args) == expected, 'current inputs differ from root-adopted frozen manifest')
    result = core_pack(args)
    require(snapshot(args) == expected, 'inputs changed during archive creation; preserve new archive, do not upload')
    result['frozen_input_manifest_sha256'] = args.freeze_sha
    result['all_input_stats_and_bytes_before_after'] = 'MATCH_ROOT_ADOPTED_FREEZE'
    return result


def verify_upload(args):
    require(re.fullmatch('[0-9a-f]{64}', args.expected_sha256), 'expected archive SHA256 required')
    p = Path(args.archive)
    regular(p)
    before = stable_file(p)
    actual = file_hash(p)
    require(actual == (args.expected_bytes, args.expected_sha256), 'archive bytes changed before upload')
    require(stable_file(p) == before, 'archive stats changed during upload preflight')
    return {'status': 'EXACT_BYTES_READY_FOR_ONE_UPLOAD', 'operation': 'verify-upload',
            'archive': p.name, 'bytes': actual[0], 'sha256': actual[1],
            'stat_before': list(before), 'stat_after': list(stable_file(p)),
            'provider_ACK': 'NOT_ESTABLISHED_BY_LOCAL_CHECK', 'scientific_executions': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    for name in ('freeze', 'pack', 'restore'):
        p = sub.add_parser(name)
        for key in ('repo', 'head', 'stage', 'output'):
            p.add_argument('--' + key, required=True)
        p.add_argument('--receipt')
        if name in ('freeze', 'pack'):
            p.add_argument('--private-root', required=True)
            p.add_argument('--dependencies-root', required=True)
        if name == 'pack':
            p.add_argument('--freeze-manifest', required=True)
            p.add_argument('--freeze-sha', required=True)
        if name == 'restore':
            p.add_argument('--archive', required=True)
            p.add_argument('--expected-sha256', required=True)
    p = sub.add_parser('verify-upload')
    p.add_argument('--archive', required=True)
    p.add_argument('--expected-bytes', required=True, type=int)
    p.add_argument('--expected-sha256', required=True)
    p.add_argument('--receipt')
    args = parser.parse_args()
    try:
        if args.receipt:
            require(not Path(args.receipt).exists(), 'create-only receipt exists')
        result = {'freeze': freeze, 'pack': pack, 'restore': restore, 'verify-upload': verify_upload}[args.operation](args)
        encoded = json.dumps(result, sort_keys=True, indent=2) + '\n'
        if args.receipt:
            with Path(args.receipt).open('x') as dest:
                dest.write(encoded)
        print(encoded, end='')
        return 0
    except Exception as exc:
        # Do not serialize arbitrary exception text or local absolute input paths.
        error = {'status': 'FAILED', 'operation': args.operation, 'error_type': type(exc).__name__,
                 'reason': 'Inspect frozen relative input identities and preserved new output; no overwrite or automatic retry.',
                 'existing_outputs_overwritten': False, 'scientific_executions': 0}
        if args.receipt and not Path(args.receipt).exists():
            with Path(args.receipt).open('x') as dest:
                json.dump(error, dest, indent=2)
                dest.write('\n')
        print(json.dumps(error, indent=2))
        return 1


if __name__ == '__main__':
    sys.exit(main())
