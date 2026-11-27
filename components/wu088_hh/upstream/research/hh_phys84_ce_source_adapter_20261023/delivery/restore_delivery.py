#!/usr/bin/env python3
"""PHYS84 byte delivery helper, explicitly reimplemented after workspace loss.
No scientific modules are imported; no scientific computations are invoked.
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import http.client
import io
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat
import subprocess
import sys
import urllib.parse
import urllib.request
import zipfile
import zlib

UNIT = 'research/hh_phys84_ce_source_adapter_20261023'
PARENT = '6a2fc5aacb6182a916b9434c316e99e750e8273c'
SCHEMA = 'PHYS84_EXACT_GIT_UNIT_BYTE_EXPORT_V1'
GIT_SCHEMA = 'PHYS84_EXACT_GIT_UNIT_MANIFEST_V1'
MANIFEST_NAME = 'BYTE_MANIFEST.json'
PROVENANCE = {
    'status': 'REIMPLEMENTED_AFTER_WORKSPACE_LOSS',
    'pre_loss_helper_sha256': '288f753eddccf7e3f9adfb0fd3441a1d745ce321d105a123d4f48ff44ffdd9ee',
    'pre_loss_helper_hash_match': 'NOT_ASSERTED',
    'lost_original_S0_zip': {
        'filename': 'PHYS84_S0_20261023_ce14c0bfc031.zip',
        'bytes': 8496264,
        'sha256': 'b655b5bc5b6d7f2fb0032d138f3e81e5329ec0df4b15f4c4a1818e69526df255',
        'status': 'LOCAL_BYTES_LOST_NOT_UPLOADED',
        'recovery_is_same_archive_identity': False,
        'original_51_private_intake_files': 'UNAVAILABLE; ONLY_CURRENT_RECOVERED_EVIDENCE_EXPORTED',
    },
}
PARENT_PINS = {
    'PHYS83_CONT_FINAL_20261023_6a2fc5aacb61.zip': (7473461, '65f8969ec76e1971374f34638a8a9821f96bf9fcd52238a6600fb7e7c8c52d3a'),
    'PHYS83_CONT_FINAL_DELIVERY_20261023.json': (868689, '789c627dcf54fe54038ac6bc59ee7d188939981f645df7bfa7364d30fe4ae772'),
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def hexcheck(value, digits):
    require(isinstance(value, str) and re.fullmatch('[0-9a-f]{%d}' % digits, value), 'INVALID_HEXADECIMAL_ID')
    return value


def safe_name(value):
    require(isinstance(value, str) and value, 'EMPTY_OR_NONSTRING_PATH')
    require('\\' not in value and not any(ord(c) < 32 or ord(c) == 127 for c in value), 'UNSAFE_PATH_CHARACTER')
    require(not PurePosixPath(value).is_absolute() and not PureWindowsPath(value).drive, 'ABSOLUTE_OR_DRIVE_PATH')
    parts = value.split('/')
    require(all(part not in ('', '.', '..', '.git', '__pycache__') for part in parts), 'UNSAFE_PATH_COMPONENT')
    require(not value.endswith(('.pyc', '.pyo')), 'BYTECODE_PATH_FORBIDDEN')
    return value


def safe_local(path):
    path = Path(os.path.abspath(path))
    require(all(not p.is_symlink() for p in (path, *path.parents)), 'LOCAL_SYMLINK_PATH_FORBIDDEN')
    return path


def read_regular(path):
    path = safe_local(path)
    before = path.stat()
    require(stat.S_ISREG(before.st_mode), 'REGULAR_FILE_REQUIRED')
    with path.open('rb') as stream:
        data = stream.read()
    after = path.stat()
    fields = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns)
    require(fields(before) == fields(after) and len(data) == before.st_size, 'INPUT_CHANGED_OR_INCOMPLETE_READ')
    return data


def write_all(fd, data, receipt=None):
    remaining = memoryview(data)
    while remaining:
        n = os.write(fd, remaining)
        require(n > 0, 'ZERO_WRITE')
        if receipt is not None:
            receipt['bytes_written'] += n
        remaining = remaining[n:]


def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def create_file(path, data, mode=0o600):
    path = safe_local(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), mode)
    try:
        write_all(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)
    require(read_regular(path) == data, 'REOPENED_WRITE_MISMATCH')
    fsync_dir(path.parent)


def object_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'DUPLICATE_JSON_KEY')
        result[key] = value
    return result


def read_json(data):
    def reject(_):
        raise ValueError('NONFINITE_JSON_NUMBER')
    obj = json.loads(data.decode('utf-8'), object_pairs_hook=object_pairs, parse_constant=reject)
    require(isinstance(obj, dict), 'JSON_OBJECT_REQUIRED')
    return obj


def encoded_json(obj):
    return (json.dumps(obj, ensure_ascii=False, allow_nan=False, indent=2) + '\n').encode('utf-8')


def create_json(path, obj):
    create_file(path, encoded_json(obj))


def entry(name, data, kind, **kw):
    return dict(filename=safe_name(name), bytes=len(data), sha256=sha(data), kind=kind, **kw)


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.PIPE)


def git_snapshot(repo, commit):
    hexcheck(commit, 40)
    require(git(repo, 'cat-file', '-t', commit).strip() == b'commit', 'GIT_COMMIT_REQUIRED')
    # Raw object headers preserve actual parents even when this is a shallow commit.
    header = git(repo, 'cat-file', '-p', commit).split(b'\n\n', 1)[0].split(b'\n')
    trees = [x[5:].decode('ascii') for x in header if x.startswith(b'tree ')]
    parents = [hexcheck(x[7:].decode('ascii'), 40) for x in header if x.startswith(b'parent ')]
    require(len(trees) == 1, 'EXACTLY_ONE_COMMIT_TREE_REQUIRED')
    tree = hexcheck(trees[0], 40)
    rows, payload = [], {}
    listing = git(repo, 'ls-tree', '-rz', '--full-tree', commit, '--', UNIT)
    for record in listing.split(b'\0'):
        if not record:
            continue
        spec, raw_name = record.split(b'\t', 1)
        mode, kind, oid = spec.decode('ascii').split()
        name = safe_name(raw_name.decode('utf-8'))
        require(name.startswith(UNIT + '/') and name not in payload, 'GIT_UNIT_OR_DUPLICATE_PATH_ERROR')
        require(kind == 'blob' and mode in ('100644', '100755'), 'NONREGULAR_GIT_ENTRY')
        data = git(repo, 'cat-file', 'blob', hexcheck(oid, 40))
        require(blob(data) == oid, 'GIT_OBJECT_CONTENT_MISMATCH')
        rows.append(entry(name, data, 'repository', git_blob_sha1=oid, mode=mode))
        payload[name] = data
    require(rows, 'EMPTY_GIT_UNIT')
    obj = dict(schema=GIT_SCHEMA, generated_utc=now(), unit=UNIT, commit=commit, tree=tree,
               parents=parents, entries=sorted(rows, key=lambda x: x['filename']), scientific_callbacks=0)
    return obj, payload


def rows_checked(rows):
    require(isinstance(rows, list), 'ENTRIES_LIST_REQUIRED')
    result = {}
    for row in rows:
        require(isinstance(row, dict), 'ENTRY_OBJECT_REQUIRED')
        name = safe_name(row.get('filename'))
        require(name != MANIFEST_NAME and name not in result, 'DUPLICATE_OR_SELF_MANIFEST_ENTRY')
        require(type(row.get('bytes')) is int and row['bytes'] >= 0, 'INVALID_ENTRY_BYTES')
        hexcheck(row.get('sha256'), 64)
        kind = row.get('kind')
        require(kind in ('repository', 'private_evidence', 'parent_recovery'), 'INVALID_ENTRY_KIND')
        if kind == 'repository':
            require(name.startswith(UNIT + '/') and row.get('mode') in ('100644', '100755'), 'INVALID_GIT_ENTRY_SCOPE_OR_MODE')
            hexcheck(row.get('git_blob_sha1'), 40)
        else:
            require(name.startswith(kind + '/'), 'ENTRY_KIND_PREFIX_MISMATCH')
        result[name] = row
    for name in result:
        require(not any(p.as_posix() in result for p in PurePosixPath(name).parents), 'FILE_DIRECTORY_COLLISION')
    return result


def current_intake(root):
    root = safe_local(root)
    require(root.is_dir(), 'INTAKE_DIRECTORY_REQUIRED')
    payload = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        require(all(not (Path(directory) / n).is_symlink() for n in dirs + files), 'INTAKE_SYMLINK_FORBIDDEN')
        dirs[:] = sorted(n for n in dirs if n not in ('.git', '__pycache__'))
        for filename in sorted(files):
            if filename.endswith(('.pyc', '.pyo')):
                continue
            require(filename != 'wu84_recovery_requests.json', 'DOWNLOAD_REQUEST_MUST_NEVER_BE_ARCHIVED')
            path = Path(directory) / filename
            name = safe_name('private_evidence/wu84_intake/' + path.relative_to(root).as_posix())
            payload[name] = read_regular(path)
    require(payload, 'EMPTY_CURRENT_INTAKE')
    return payload


def pack(args, result):
    snapshot, payload = git_snapshot(args.repo, args.commit)
    if args.stage in ('S0', 'S0_RECOVERY'):
        require(snapshot['parents'] == [PARENT], 'S0_ACTUAL_PARENT_PIN_MISMATCH')
    rows = list(snapshot['entries'])
    private = current_intake(args.intake)
    for name, data in private.items():
        require(name not in payload, 'PAYLOAD_COLLISION')
        payload[name] = data
        rows.append(entry(name, data, 'private_evidence'))
    for filename, expected in PARENT_PINS.items():
        data = read_regular(args.parent_recovery / filename)
        require((len(data), sha(data)) == expected, 'PINNED_PARENT_BYTES_MISMATCH')
        name = 'parent_recovery/' + filename
        payload[name] = data
        rows.append(entry(name, data, 'parent_recovery'))
    rows_checked(rows)
    manifest = dict(schema=SCHEMA, created_utc=now(), stage=args.stage, unit=UNIT,
                    commit=snapshot['commit'], tree=snapshot['tree'], parents=snapshot['parents'],
                    actual_local_HEAD_at_pack=git(args.repo, 'rev-parse', '--verify', 'HEAD').decode('ascii').strip(),
                    predecessor_commit=PARENT, science_identity=args.science_identity,
                    HH_R10='OFF', production_admission='NOT_ISSUED', scientific_callbacks=0,
                    helper_provenance=PROVENANCE, entries=sorted(rows, key=lambda x: x['filename']),
                    nested_parent_policy='RAW_OUTER_HASH_ONLY; historical dual restore reused separately')
    payload[MANIFEST_NAME] = encoded_json(manifest)
    destination = safe_local(args.archive)
    with destination.open('xb', buffering=0) as stream:
        with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
            by_name = {r['filename']: r for r in rows}
            for name in sorted(payload):
                zi = zipfile.ZipInfo(name, date_time=(2026, 10, 23, 0, 0, 0))
                zi.create_system = 3
                row = by_name.get(name)
                mode = int(row['mode'], 8) & 0o777 if row and row['kind'] == 'repository' else 0o600
                zi.external_attr = (stat.S_IFREG | mode) << 16
                zi.compress_type = zipfile.ZIP_DEFLATED
                with archive.open(zi, 'w', force_zip64=True) as member:
                    view = memoryview(payload[name])
                    while view:
                        n = member.write(view)
                        require(n > 0, 'ZERO_ZIP_WRITE')
                        view = view[n:]
        stream.flush()
        os.fsync(stream.fileno())
    fsync_dir(destination.parent)
    raw = read_regular(destination)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        members = members_checked(archive)
        require(set(members) == set(payload), 'NEW_ARCHIVE_EXACT_MEMBER_COVERAGE_FAILURE')
        for name, data in payload.items():
            reread = crc_read(archive, members[name])
            require(reread == data, 'NEW_ARCHIVE_REOPENED_MEMBER_BYTES_FAILURE')
    result.update(status='PASS_EXACT_GIT_UNIT_ARCHIVE', git_identity={k: snapshot[k] for k in ('commit', 'tree', 'parents', 'unit')},
                  archive=dict(path=str(destination), bytes=len(raw), sha256=sha(raw)),
                  counts=dict(repository=len(snapshot['entries']), private_evidence=len(private), parent_recovery=len(PARENT_PINS),
                              payload=len(rows), zip_members=len(payload)), recovery_provenance=PROVENANCE)


def members_checked(archive):
    result = {}
    for item in archive.infolist():
        name = safe_name(item.filename)
        require(name == item.orig_filename and name not in result, 'NORMALIZED_OR_DUPLICATE_ZIP_PATH')
        require(not item.is_dir() and not item.flag_bits & 1, 'DIRECTORY_OR_ENCRYPTED_ZIP_ENTRY')
        require(stat.S_IFMT(item.external_attr >> 16) in (0, stat.S_IFREG), 'NONREGULAR_ZIP_ENTRY')
        result[name] = item
    for name in result:
        require(not any(p.as_posix() in result for p in PurePosixPath(name).parents), 'ZIP_FILE_DIRECTORY_COLLISION')
    return result


def crc_read(archive, item):
    data = archive.read(item)
    require(len(data) == item.file_size and zlib.crc32(data) & 0xffffffff == item.CRC, 'FULL_MEMBER_CRC_OR_SIZE_FAILURE')
    return data


PARENT_UNIT = 'research/hh_phys83_ce_completion_20261023'
PARENT_TREE = 'ea34771b32904d94e2317a09a13d630a0a28e8ca'
DEPENDENCY_PINS = {
    'results/rate_grid.csv': (46819, '64e53e02b776db2aee6d67ce03201cbc0b90404d7cdf40e52cccaaecd2fc3017', '5de4a9f8326fef6002aae8b292e4b18f433a5562'),
    'CONTRACT.json': (6315, 'd9eb980df5236e2b2ca3da313813c3ca2b21562f90486f1173d0ea509bc4dcc5', '8c60b3a31046f258d011359c25c6048d1e21458e'),
    'results/SCIENCE_IDENTITY.json': (1831, 'ca2ceebb71bff3e682dcf01761e3f5e2770d220a27bf38ac4817d8aad6622d46', '5f1c8819af003d276dc6760c2aee145c66097e7a'),
    'results/COMPLETE.json': (6250, '6a69c5552a9a311c14c55575ae1ee058d746fd377a23a21f7636ad3cc7854761', '48283d89946d7ebddbc59a014278992ba4ea0ab4'),
    'source/vendor/phys78_run_pilot.py': (28068, '76ff57ba687fd9830b84c3fcff69eb8ed0e9f6ceab4551e61c67c84d3ea65124', '249f639c6ccf8eee090ed38365b2fed2ad841885'),
}


def legacy_nested_name(name):
    # Immutable PHYS83 contains historical bytecode. Validate its metadata path
    # without extracting it or weakening the newer outer export path policy.
    require(isinstance(name, str) and name, 'EMPTY_NESTED_MEMBER_NAME')
    require('\\' not in name and not any(ord(c) < 32 or ord(c) == 127 for c in name), 'UNSAFE_NESTED_PATH_CHARACTER')
    require(not PurePosixPath(name).is_absolute() and not PureWindowsPath(name).drive, 'ABSOLUTE_NESTED_PATH')
    require(all(p not in ('', '.', '..', '.git') for p in name.split('/')), 'UNSAFE_NESTED_PATH_COMPONENT')
    return name


def restore_mandatory_parent_dependencies(extract_root, output_dir, result):
    section = dict(status='RUNNING', scope='exactly five mandatory dependency byte recoveries from downloaded nested parent ZIP; historical whole parent restoration is not repeated',
                   counts=dict(dependency_members_expected=5, nested_manifest_crc=0, selected_member_crc=0,
                               selected_pin_and_blob=0, actual_files_extracted=0, reopened_rehash=0,
                               dependency_bytes_extracted=0), entries=[], scientific_module_imports=0,
                   scientific_callbacks=0, rate_evaluations=0, ODE_executions=0)
    result['mandatory_parent_dependencies'] = section
    counts = section['counts']
    parent_name = 'PHYS83_CONT_FINAL_20261023_6a2fc5aacb61.zip'
    json_name = 'PHYS83_CONT_FINAL_DELIVERY_20261023.json'
    parent_path = extract_root / 'parent_recovery' / parent_name
    parent_json_path = extract_root / 'parent_recovery' / json_name
    raw_zip, raw_json = read_regular(parent_path), read_regular(parent_json_path)
    require((len(raw_zip), sha(raw_zip)) == PARENT_PINS[parent_name], 'DOWNLOADED_NESTED_PARENT_RAW_PIN_MISMATCH')
    require((len(raw_json), sha(raw_json)) == PARENT_PINS[json_name], 'DOWNLOADED_PARENT_JSON_RAW_PIN_MISMATCH')
    section['source_nested_zip'] = dict(path=str(parent_path), bytes=len(raw_zip), sha256=sha(raw_zip), provenance='actual outer downloaded payload extraction')
    section['parent_json_before'] = dict(bytes=len(raw_json), sha256=sha(raw_json))
    child_contract = read_json(read_regular(extract_root / UNIT / 'CONTRACT.json'))
    input_pins = {name: pin[1] for name, pin in DEPENDENCY_PINS.items() if name != 'source/vendor/phys78_run_pilot.py'}
    require(child_contract.get('input_pins') == input_pins, 'RESTORED_CHILD_FOUR_PARENT_INPUT_PINS_MISMATCH')
    selected = {}
    with zipfile.ZipFile(io.BytesIO(raw_zip)) as nested:
        members = {}
        for item in nested.infolist():
            name = legacy_nested_name(item.filename)
            require(name == item.orig_filename and name not in members, 'NESTED_NORMALIZED_OR_DUPLICATE_PATH')
            require(not item.is_dir() and not item.flag_bits & 1, 'NESTED_DIRECTORY_OR_ENCRYPTED_ENTRY')
            require(stat.S_IFMT(item.external_attr >> 16) in (0, stat.S_IFREG), 'NESTED_NONREGULAR_MEMBER')
            members[name] = item
        for name in members:
            require(not any(p.as_posix() in members for p in PurePosixPath(name).parents), 'NESTED_FILE_DIRECTORY_COLLISION')
        # This is metadata scanning, not new CRC/hash verification of all 385 payloads.
        section['nested_member_metadata_scanned'] = len(members)
        require(MANIFEST_NAME in members, 'NESTED_BYTE_MANIFEST_MISSING')
        manifest_raw = crc_read(nested, members[MANIFEST_NAME])
        counts['nested_manifest_crc'] += 1
        manifest = read_json(manifest_raw)
        require(manifest.get('schema') == 'PHYS83_CONT_BYTE_EXPORT_V1' and manifest.get('stage') == 'FINAL', 'NESTED_MANIFEST_SCHEMA_OR_STAGE_MISMATCH')
        require(manifest.get('commit') == PARENT and manifest.get('tree') == PARENT_TREE, 'NESTED_MANIFEST_COMMIT_TREE_MISMATCH')
        require(manifest.get('HH_R10') == 'OFF' and manifest.get('production_admission') == 'NOT_ISSUED', 'NESTED_MANIFEST_SCOPE_MISMATCH')
        section['nested_manifest'] = dict(bytes=len(manifest_raw), sha256=sha(manifest_raw), commit=PARENT, tree=PARENT_TREE)
        require(isinstance(manifest.get('repository_files'), list) and isinstance(manifest.get('private_evidence_files'), list), 'NESTED_MANIFEST_FILE_LISTS_REQUIRED')
        all_rows = {}
        for row in manifest['repository_files'] + manifest['private_evidence_files']:
            require(isinstance(row, dict), 'NESTED_MANIFEST_ROW_OBJECT_REQUIRED')
            name = legacy_nested_name(row.get('path'))
            require(name != MANIFEST_NAME and name not in all_rows, 'NESTED_MANIFEST_DUPLICATE_OR_SELF_PATH')
            all_rows[name] = row
        require(set(members) == set(all_rows) | {MANIFEST_NAME}, 'NESTED_MANIFEST_EXACT_PATH_COVERAGE_MISMATCH')
        repository_rows = {row['path']: row for row in manifest['repository_files']}
        for relative, (size, digest, gitblob) in DEPENDENCY_PINS.items():
            name = PARENT_UNIT + '/' + relative
            require(name in members and name in repository_rows, 'MANDATORY_NESTED_DEPENDENCY_MISSING')
            row = repository_rows[name]
            require(row.get('bytes') == size and row.get('SHA256') == digest and
                    row.get('git_blob_SHA1') == gitblob and row.get('mode') == '100644', 'MANDATORY_NESTED_MANIFEST_PIN_MISMATCH')
            data = crc_read(nested, members[name])
            counts['selected_member_crc'] += 1
            require((len(data), sha(data), blob(data)) == (size, digest, gitblob), 'MANDATORY_NESTED_DEPENDENCY_BYTES_MISMATCH')
            counts['selected_pin_and_blob'] += 1
            selected[name] = data
    dependency_root = safe_local(output_dir / 'dependency_restore')
    require(not dependency_root.exists(), 'CREATE_ONLY_DEPENDENCY_ROOT_ALREADY_EXISTS')
    dependency_root.mkdir(mode=0o700)
    section['dependency_restore_root'] = str(dependency_root)
    # Validate every selected target before beginning any extraction.
    for name in selected:
        dest = dependency_root.joinpath(*PurePosixPath(safe_name(name)).parts)
        require(safe_local(dest).is_relative_to(dependency_root) and not dest.exists(), 'UNSAFE_OR_PREEXISTING_DEPENDENCY_TARGET')
    for name, data in selected.items():
        dest = dependency_root.joinpath(*PurePosixPath(name).parts)
        dest.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        create_file(dest, data)
        os.chmod(dest, 0o644)
        require(stat.S_IMODE(dest.stat().st_mode) == 0o644, 'DEPENDENCY_RESTORED_MODE_MISMATCH')
        counts['actual_files_extracted'] += 1
        counts['dependency_bytes_extracted'] += len(data)
        reread = read_regular(dest)
        size, digest, gitblob = DEPENDENCY_PINS[name[len(PARENT_UNIT) + 1:]]
        require(reread == data and (len(reread), sha(reread), blob(reread)) == (size, digest, gitblob), 'DEPENDENCY_REOPENED_BYTE_HASH_BLOB_MISMATCH')
        counts['reopened_rehash'] += 1
        section['entries'].append(dict(filename=name, bytes=len(reread), sha256=sha(reread), git_blob_sha1=blob(reread),
                                       output_path=str(dest), mode='100644', status='PASS'))
    require(all(counts[k] == 5 for k in ('selected_member_crc', 'selected_pin_and_blob', 'actual_files_extracted', 'reopened_rehash')) and
            counts['nested_manifest_crc'] == 1 and counts['dependency_bytes_extracted'] == 89283, 'MANDATORY_DEPENDENCY_COUNT_CLOSURE_FAILURE')
    after_zip, after_json = read_regular(parent_path), read_regular(parent_json_path)
    require(after_zip == raw_zip and after_json == raw_json, 'RAW_PARENT_RECOVERY_FILES_CHANGED')
    section['parent_json_after'] = dict(bytes=len(after_json), sha256=sha(after_json), unchanged=True)
    section['nested_zip_after'] = dict(bytes=len(after_zip), sha256=sha(after_zip), unchanged=True)
    section['status'] = 'PASS_FIVE_MANDATORY_DEPENDENCY_BYTES_RESTORED'


def restore(args, result):
    raw_a, raw_b = read_regular(args.original), read_regular(args.downloaded)
    require(not os.path.samefile(args.original, args.downloaded), 'DISTINCT_ORIGINAL_DOWNLOAD_FILES_REQUIRED')
    result['complete_archive_bytes'] = dict(original=dict(bytes=len(raw_a), sha256=sha(raw_a)),
                                            downloaded=dict(bytes=len(raw_b), sha256=sha(raw_b)), byte_for_byte_equal=raw_a == raw_b)
    require(raw_a == raw_b, 'FULL_ORIGINAL_DOWNLOAD_BYTES_DIFFER')
    fresh_raw = read_regular(args.git_manifest)
    fresh = read_json(fresh_raw)
    require(fresh.get('schema') == GIT_SCHEMA and fresh.get('unit') == UNIT, 'FRESH_GIT_MANIFEST_SCHEMA_MISMATCH')
    hexcheck(fresh.get('commit'), 40); hexcheck(fresh.get('tree'), 40)
    require(isinstance(fresh.get('parents'), list), 'GIT_PARENTS_LIST_REQUIRED')
    for parent in fresh['parents']:
        hexcheck(parent, 40)
    fresh_rows = rows_checked(fresh.get('entries'))
    require(fresh_rows and all(r['kind'] == 'repository' for r in fresh_rows.values()), 'EXACT_GIT_UNIT_MANIFEST_REQUIRED')
    result['fresh_git_manifest'] = dict(path=str(args.git_manifest), bytes=len(fresh_raw), sha256=sha(fresh_raw),
                                        commit=fresh['commit'], tree=fresh['tree'])
    counts = dict(original_crc=0, downloaded_crc=0, payload_hash_size=0, repository_git_blob=0, extracted=0, extracted_rehashed=0)
    result['counts'] = counts
    with zipfile.ZipFile(io.BytesIO(raw_a)) as original, zipfile.ZipFile(io.BytesIO(raw_b)) as archive:
        om, members = members_checked(original), members_checked(archive)
        require(set(om) == set(members) and MANIFEST_NAME in members, 'EXACT_ZIP_MEMBER_SET_OR_MANIFEST_MISSING')
        manifest = read_json(crc_read(archive, members[MANIFEST_NAME]))
        require(manifest.get('schema') == SCHEMA and manifest.get('unit') == UNIT, 'ARCHIVE_SCHEMA_OR_UNIT_MISMATCH')
        require(manifest.get('HH_R10') == 'OFF' and manifest.get('production_admission') == 'NOT_ISSUED', 'ARCHIVE_SCOPE_MISMATCH')
        require(manifest.get('predecessor_commit') == PARENT, 'PREDECESSOR_COMMIT_MISMATCH')
        for key in ('commit', 'tree', 'parents', 'unit'):
            require(manifest.get(key) == fresh[key], 'FRESH_GIT_IDENTITY_MISMATCH_' + key)
        if manifest.get('stage') in ('S0', 'S0_RECOVERY'):
            require(manifest.get('parents') == [PARENT], 'S0_PARENT_PIN_MISMATCH')
        rows = rows_checked(manifest.get('entries'))
        repo_rows = {n: r for n, r in rows.items() if r['kind'] == 'repository'}
        require(repo_rows == fresh_rows, 'EXACT_REPOSITORY_PATH_MODE_BLOB_HASH_SIZE_MISMATCH')
        require(set(members) == set(rows) | {MANIFEST_NAME}, 'EXACT_PAYLOAD_MANIFEST_COVERAGE_MISMATCH')
        require({n for n, r in rows.items() if r['kind'] == 'parent_recovery'} ==
                {'parent_recovery/' + n for n in PARENT_PINS}, 'EXACT_PARENT_RECOVERY_SET_MISMATCH')
        extract_root = args.output_dir / 'extracted'
        extract_root.mkdir(mode=0o700)
        result['entry_checks'] = []
        result['archive_identity'] = {k: manifest.get(k) for k in ('stage', 'commit', 'tree', 'parents', 'science_identity')}
        for name in sorted(members):
            a, b = crc_read(original, om[name]), crc_read(archive, members[name])
            counts['original_crc'] += 1; counts['downloaded_crc'] += 1
            require(a == b, 'DECOMPRESSED_ORIGINAL_DOWNLOAD_BYTES_DIFFER')
            row = rows.get(name)
            if row:
                require((len(b), sha(b)) == (row['bytes'], row['sha256']), 'PAYLOAD_HASH_OR_SIZE_MISMATCH')
                counts['payload_hash_size'] += 1
                if row['kind'] == 'repository':
                    require(blob(b) == row['git_blob_sha1'], 'RECOMPUTED_GIT_BLOB_MISMATCH')
                    counts['repository_git_blob'] += 1
                if row['kind'] == 'parent_recovery':
                    require((len(b), sha(b)) == PARENT_PINS[PurePosixPath(name).name], 'PINNED_RAW_PARENT_BYTES_MISMATCH')
            dest = extract_root.joinpath(*PurePosixPath(name).parts)
            dest.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            require(safe_local(dest).is_relative_to(safe_local(extract_root)), 'EXTRACTION_ESCAPE')
            create_file(dest, b)
            if row and row['kind'] == 'repository':
                mode = int(row['mode'], 8) & 0o777
                os.chmod(dest, mode)
                require(stat.S_IMODE(dest.stat().st_mode) == mode, 'EXTRACTED_GIT_MODE_MISMATCH')
            counts['extracted'] += 1
            reread = read_regular(dest)
            require(reread == b and sha(reread) == sha(b), 'EXTRACTED_REHASH_MISMATCH')
            counts['extracted_rehashed'] += 1
            result['entry_checks'].append(dict(filename=name, bytes=len(b), sha256=sha(b), status='PASS'))
        require(all(counts[k] == len(members) for k in ('original_crc', 'downloaded_crc', 'extracted', 'extracted_rehashed')), 'INCOMPLETE_ZIP_ENTRY_COUNTS')
        require(counts['payload_hash_size'] == len(rows) and counts['repository_git_blob'] == len(repo_rows), 'INCOMPLETE_PAYLOAD_COUNTS')
    result['nested_parent_archive'] = dict(status='PASS_RAW_OUTER_HASH_ONLY', historical_dual_restore='REUSED_SEPARATELY')
    result['mandatory_parent_dependencies'] = dict(status='NOT_REQUESTED_NONFINAL_STAGE')
    if manifest.get('stage') == 'FINAL':
        restore_mandatory_parent_dependencies(extract_root, args.output_dir, result)
    result['scientific_freeze'] = dict(status='NOT_REQUESTED')
    if args.freeze_manifest:
        raw = read_regular(args.freeze_manifest)
        frozen_rows = rows_checked(read_json(raw).get('entries'))
        require(frozen_rows, 'NONEMPTY_FREEZE_MANIFEST_REQUIRED')
        for name, row in frozen_rows.items():
            data = read_regular(extract_root.joinpath(*PurePosixPath(name).parts))
            require((len(data), sha(data)) == (row['bytes'], row['sha256']), 'FROZEN_BYTE_MISMATCH')
            if row['kind'] == 'repository':
                require(blob(data) == row['git_blob_sha1'], 'FROZEN_GIT_BLOB_MISMATCH')
        result['scientific_freeze'] = dict(status='PASS_BYTES_ONLY', files=len(frozen_rows), manifest_sha256=sha(raw), scientific_callbacks=0)
    result['status'] = 'PASS_FULL_BYTE_RESTORATION'


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def download(args, result):
    # No private URL, request contents, response headers, or exception text enters receipts.
    request_path = safe_local(args.request)
    require(request_path.is_relative_to(Path('/tmp')), 'PRIVATE_REQUEST_MUST_BE_UNDER_TMP')
    obj = read_json(read_regular(request_path))
    require(set(obj) == {'url', 'name', 'expected_bytes', 'expected_sha256'}, 'REQUEST_KEYS_MISMATCH')
    name = safe_name(obj['name'])
    require('/' not in name, 'DOWNLOAD_FILENAME_REQUIRED')
    require(type(obj['expected_bytes']) is int and obj['expected_bytes'] >= 0, 'INVALID_EXPECTED_SIZE')
    hexcheck(obj['expected_sha256'], 64)
    parsed = urllib.parse.urlsplit(obj['url'])
    require(parsed.scheme == 'https' and parsed.hostname and not parsed.username and not parsed.password and not parsed.fragment, 'HTTPS_WITHOUT_USERINFO_REQUIRED')
    dest = safe_local(args.output_dir / name)
    result.update(name=name, expected_bytes=obj['expected_bytes'], expected_sha256=obj['expected_sha256'],
                  output_path=str(dest), get_attempts=0, automatic_retries=0, redirects_allowed=False,
                  bytes_received=0, bytes_written=0, complete_response_read=False, failure_stage='CREATE_DESTINATION')
    fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        result['failure_stage'] = 'SINGLE_FULL_GET'
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        request = urllib.request.Request(obj['url'], method='GET', headers={'Accept-Encoding': 'identity'})
        result['get_attempts'] = 1
        with opener.open(request, timeout=args.timeout) as response:
            result['http_status'] = response.status
            require(response.status == 200, 'HTTP_200_REQUIRED')
            require(response.headers.get('Content-Encoding', 'identity').lower() == 'identity', 'CONTENT_ENCODING_MUST_BE_IDENTITY')
            while True:
                try:
                    data = response.read(1024 * 1024)
                except http.client.IncompleteRead as exc:
                    if exc.partial:
                        result['bytes_received'] += len(exc.partial)
                        write_all(fd, exc.partial, result)
                    raise
                if not data:
                    result['complete_response_read'] = True
                    break
                result['bytes_received'] += len(data)
                write_all(fd, data, result)
        result['failure_stage'] = 'FSYNC_CLOSE_REOPEN_VERIFY'
    finally:
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        partial = read_regular(dest)
        result['actual_bytes'] = len(partial)
        result['actual_sha256'] = sha(partial)
        fsync_dir(dest.parent)
    require(result['complete_response_read'], 'FULL_RESPONSE_REQUIRED')
    require(result['bytes_received'] == result['bytes_written'] == result['actual_bytes'] == obj['expected_bytes'], 'DOWNLOAD_SIZE_MISMATCH')
    require(result['actual_sha256'] == obj['expected_sha256'], 'DOWNLOAD_SHA256_MISMATCH')
    result.pop('failure_stage', None)
    result['status'] = 'PASS_SINGLE_FULL_GET_REOPENED_BYTES'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('git-manifest')
    p.add_argument('--repo', type=Path, required=True); p.add_argument('--commit', required=True)
    p.add_argument('--output', type=Path, required=True)
    p = commands.add_parser('pack')
    p.add_argument('--repo', type=Path, required=True); p.add_argument('--commit', required=True)
    p.add_argument('--stage', choices=['S0', 'S0_RECOVERY', 'S1', 'S2', 'FINAL'], required=True)
    p.add_argument('--science-identity', default='NOT_SUPPLIED')
    p.add_argument('--intake', type=Path, required=True); p.add_argument('--parent-recovery', type=Path, required=True)
    p.add_argument('--archive', type=Path, required=True); p.add_argument('--receipt', type=Path, required=True)
    p = commands.add_parser('restore')
    p.add_argument('--original', type=Path, required=True); p.add_argument('--downloaded', type=Path, required=True)
    p.add_argument('--git-manifest', type=Path, required=True); p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--provider', required=True); p.add_argument('--freeze-manifest', type=Path)
    p = commands.add_parser('download')
    p.add_argument('--request', type=Path, required=True); p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--receipt', type=Path, required=True); p.add_argument('--timeout', type=float, default=120)
    args = parser.parse_args()
    result = dict(schema='PHYS84_BYTE_DELIVERY_OPERATION_V1', operation=args.command, status='RUNNING',
                  started_utc=now(), helper_sha256=sha(Path(__file__).read_bytes()), helper_provenance=PROVENANCE,
                  scientific_callbacks=0, scientific_module_imports=0, historical_science_replays=0,
                  HH_R10='OFF', production_admission='NOT_ISSUED')
    receipt_path = None
    try:
        if args.command == 'git-manifest':
            snapshot, _ = git_snapshot(args.repo, args.commit)
            snapshot['helper_provenance'] = PROVENANCE
            create_json(args.output, snapshot)
            print(json.dumps(dict(status='PASS_GIT_MANIFEST_CREATED', output=str(args.output), commit=snapshot['commit'],
                                  tree=snapshot['tree'], parents=snapshot['parents'], entries=len(snapshot['entries']))))
            return 0
        if args.command == 'restore':
            args.output_dir = safe_local(args.output_dir)
            args.output_dir.mkdir(mode=0o700, exist_ok=False)
            receipt_path = args.output_dir / 'RESULT.json'
            result['provider_label'] = args.provider
            result['scope'] = 'local complete byte comparison and actual restoration; provider origin and fresh remote Git readback are separate receipts'
        else:
            receipt_path = safe_local(args.receipt)
            require(not receipt_path.exists(), 'CREATE_ONLY_RECEIPT_ALREADY_EXISTS')
        {'pack': pack, 'restore': restore, 'download': download}[args.command](args, result)
    except Exception as exc:
        result['status'] = 'FAIL'
        result['error'] = dict(type=type(exc).__name__, code='DOWNLOAD_FAILED_SEE_STAGE_AND_COUNTS' if args.command == 'download' else str(exc))
    result['finished_utc'] = now()
    if receipt_path is not None and not receipt_path.exists():
        create_json(receipt_path, result)
    else:
        receipt_path = None
    print(json.dumps(dict(status=result['status'], receipt=str(receipt_path) if receipt_path else None,
                          counts=result.get('counts'), error=result.get('error')), ensure_ascii=False))
    return 0 if result['status'].startswith('PASS_') else 2


if __name__ == '__main__':
    sys.exit(main())
