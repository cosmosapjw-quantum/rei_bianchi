#!/usr/bin/env python3
"""Restore the E13C9 complete backup; this program performs no scientific run.

Supply the externally published transfer-manifest SHA-256. File names, including
an appended .bin suffix, do not establish byte identity. --hydrate invokes only
the byte-pinned E13C8 restoration helper, once, to restore its saved dependencies.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import time
import zipfile


PACKAGE_ROOT = 'BASS_HE_E13C9_SIGNED_VOLTERRA_LOCAL_20261012_v1'
TRANSFER_SCHEMA = 'bass-he-e13c9-transfer-manifest-v1'
PACKAGE_SCHEMA = 'bass-he-e13c9-complete-manifest-v1'
PART_BYTES = 64 * 1024 ** 2
CHUNK_BYTES = 1024 ** 2
MAX_MEMBERS = 50000
MAX_EXPANDED_BYTES = 2 * 1024 ** 3
DEPENDENCIES = {
    'E13C8_COMPLETE': {
        'relative_archive': 'dependencies/E13C8_COMPLETE.zip',
        'bytes': 170991376,
        'sha256': 'ba4b1ace541f52bae5dd096d3da75ca9f0bf2d1894d0c3cba40375e40b1eca80',
    },
    'E13C8_RECOVERY_KIT': {
        'relative_archive': 'dependencies/E13C8_RECOVERY_KIT.zip',
        'bytes': 10727,
        'sha256': 'cf25ae33079f21189472cafc40403f066651883b7803c44a6d9e56c6f2f73ed3',
    },
}
PRIOR_RECOVERY = {
    'helper': {
        'relative_path': 'restore_transfer.py',
        'bytes': 9177,
        'sha256': 'd061629aa3c689b0f7fd0d70cd14c01946ec688bc0ed8e91c48eaaffee6f1343',
    },
    'transfer_manifest': {
        'relative_path': 'BASS_HE_E13C8_TRANSFER_MANIFEST.json',
        'bytes': 2170,
        'sha256': 'dd62793a79f35aa4b8358cece38ac02517e75db4b32c45f26b890210b19594b1',
    },
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def pin(path):
    path = Path(path)
    if not path.is_file() or path.is_symlink():
        raise ValueError('regular file required: ' + str(path))
    return {'bytes': path.stat().st_size, 'sha256': sha(path)}


def valid_pin(value):
    if not isinstance(value, dict) or type(value.get('bytes')) is not int or value['bytes'] < 0:
        raise ValueError('nonnegative integer byte count required')
    digest = value.get('sha256')
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
        raise ValueError('canonical lowercase SHA-256 required')
    return {'bytes': value['bytes'], 'sha256': digest}


def verify_file(path, expected):
    expected = valid_pin(expected)
    actual = pin(path)
    if actual != expected:
        raise ValueError('file byte identity mismatch: ' + str(path))
    return actual


def save(path, obj):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(obj, stream, indent=2, sort_keys=True, ensure_ascii=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + str(key))
        result[key] = value
    return result


def load_json(raw):
    return json.loads(raw, object_pairs_hook=unique_object)


def safe_relative(name, single=False):
    if not isinstance(name, str) or not name or '\\' in name or ':' in name or any(ord(c) < 32 for c in name):
        raise ValueError('unsafe relative path')
    value = PurePosixPath(name)
    if value.is_absolute() or value.as_posix() != name or any(p in ('', '.', '..') for p in value.parts):
        raise ValueError('noncanonical relative path')
    if single and len(value.parts) != 1:
        raise ValueError('single path component required')
    return name


def validate_transfer(manifest):
    if manifest.get('schema') != TRANSFER_SCHEMA or manifest.get('package_root') != PACKAGE_ROOT:
        raise ValueError('unexpected E13C9 transfer schema or package root')
    if manifest.get('dependencies') != DEPENDENCIES or manifest.get('prior_recovery') != PRIOR_RECOVERY:
        raise ValueError('previous complete backup or recovery pins changed')
    if manifest.get('new_NCP_heavy_tasks') != 0:
        raise ValueError('this restore protocol does not authorize a new NCP task')
    archive = manifest['archive']
    valid_pin(archive)
    safe_relative(archive['canonical_name'], single=True)
    helper = manifest['restore_helper']
    valid_pin(helper)
    if helper.get('relative_path') != 'restore_transfer.py':
        raise ValueError('unexpected recovery-helper location')
    valid_pin(manifest['package_manifest'])
    parts = manifest['parts']
    if not isinstance(parts, list) or not parts:
        raise ValueError('nonempty transfer part list required')
    names = set()
    for index, item in enumerate(parts, start=1):
        valid_pin(item)
        expected_name = archive['canonical_name'] + '.part%03d' % index
        if item.get('index') != index or item.get('canonical_name') != expected_name:
            raise ValueError('part order or canonical name does not match manifest index')
        safe_relative(item['canonical_name'], single=True)
        if item['canonical_name'] in names:
            raise ValueError('duplicate canonical part name')
        names.add(item['canonical_name'])
        if item['bytes'] <= 0 or item['bytes'] > PART_BYTES:
            raise ValueError('invalid transfer part size')
        if index < len(parts) and item['bytes'] != PART_BYTES:
            raise ValueError('nonterminal transfer piece must be 64 MiB')
    if sum(item['bytes'] for item in parts) != archive['bytes']:
        raise ValueError('part sizes do not sum to complete archive size')


def select_parts(parts_dir, parts):
    """Find actual bytes, preserving all downloaded file names and duplicates."""
    directory = Path(parts_dir)
    if not directory.is_dir() or directory.is_symlink():
        raise ValueError('regular transfer-parts directory required')
    needed_sizes = {valid_pin(item)['bytes'] for item in parts}
    identities = {}
    for candidate in sorted(directory.iterdir(), key=lambda p: str(p)):
        if candidate.is_file() and not candidate.is_symlink() and candidate.stat().st_size in needed_sizes:
            actual = pin(candidate)
            identities.setdefault((actual['bytes'], actual['sha256']), []).append(candidate)
    selected = []
    for item in parts:
        actual_pin = valid_pin(item)
        matches = identities.get((actual_pin['bytes'], actual_pin['sha256']), [])
        if not matches:
            raise FileNotFoundError('no actual-byte match for part ' + item['canonical_name'])
        # Identical content may serve repeated logical pieces; the final complete
        # archive hash independently checks ordered reconstruction in every case.
        chosen = matches[0]
        selected.append({'index': item['index'], 'canonical_name': item['canonical_name'],
                         'actual_path': str(chosen.resolve()), 'matching_downloads': len(matches), **actual_pin})
    return selected


def reassemble(selected, destination, expected):
    digest = hashlib.sha256()
    count = 0
    with Path(destination).open('xb') as target:
        for item in selected:
            part_digest = hashlib.sha256()
            part_count = 0
            with Path(item['actual_path']).open('rb') as source:
                for data in iter(lambda: source.read(CHUNK_BYTES), b''):
                    target.write(data)
                    digest.update(data)
                    count += len(data)
                    part_digest.update(data)
                    part_count += len(data)
            if {'bytes': part_count, 'sha256': part_digest.hexdigest()} != valid_pin(item):
                raise ValueError('selected transfer part changed while reading')
        target.flush()
        os.fsync(target.fileno())
    actual = {'bytes': count, 'sha256': digest.hexdigest()}
    if actual != valid_pin(expected):
        raise ValueError('reassembled complete ZIP byte identity mismatch')
    return actual


def extract_verified(archive, destination, manifest_name, prefix, schema,
                     required_payload_pins=None, expected_manifest_pin=None):
    """Safely extract a previously archive-hash-verified ZIP, checking all bytes."""
    destination = Path(destination)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError('fresh extraction directory required')
    safe_relative(manifest_name)
    with zipfile.ZipFile(archive) as zipped:
        infos = zipped.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or len(names) > MAX_MEMBERS:
            raise ValueError('duplicate or excessive ZIP members')
        if sum(info.file_size for info in infos) > MAX_EXPANDED_BYTES:
            raise ValueError('unexpected ZIP expansion')
        for info in infos:
            safe_relative(info.filename)
            if info.is_dir() or info.flag_bits & 1:
                raise ValueError('directory or encrypted ZIP member is not supported')
            if stat.S_IFMT(info.external_attr >> 16) not in (0, stat.S_IFREG):
                raise ValueError('nonregular ZIP member')
            if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                raise ValueError('unexpected ZIP compression method')
        manifest_info = zipped.getinfo(manifest_name)
        if manifest_info.file_size > 16 * 1024 ** 2:
            raise ValueError('unexpectedly large package manifest')
        manifest_bytes = zipped.read(manifest_name)
        manifest_identity = {'bytes': len(manifest_bytes), 'sha256': hashlib.sha256(manifest_bytes).hexdigest()}
        if expected_manifest_pin is not None and manifest_identity != valid_pin(expected_manifest_pin):
            raise ValueError('embedded package manifest identity mismatch')
        manifest = load_json(manifest_bytes)
        if manifest.get('schema') != schema or not isinstance(manifest.get('files'), dict):
            raise ValueError('unexpected embedded manifest schema')
        pins = {}
        for relative, identity in manifest['files'].items():
            safe_relative(relative)
            full_name = prefix + relative
            safe_relative(full_name)
            pins[full_name] = valid_pin(identity)
        if set(names) != set(pins) | {manifest_name} or manifest_name in pins:
            raise ValueError('ZIP member set differs from embedded payload manifest')
        for relative, expected in (required_payload_pins or {}).items():
            if pins.get(prefix + relative) != valid_pin(expected):
                raise ValueError('required embedded payload pin missing or changed: ' + relative)
        destination.mkdir(parents=True, exist_ok=False)
        for info in infos:
            target = destination / info.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            count = 0
            digest = hashlib.sha256()
            with zipped.open(info) as source, target.open('xb') as output:
                for data in iter(lambda: source.read(CHUNK_BYTES), b''):
                    count += len(data)
                    digest.update(data)
                    output.write(data)
            identity = {'bytes': count, 'sha256': digest.hexdigest()}
            expected = manifest_identity if info.filename == manifest_name else pins[info.filename]
            if identity != expected:
                raise ValueError('actual extracted payload identity mismatch: ' + info.filename)
        return {'members': len(infos), 'payload_files_verified': len(pins),
                'raw_bytes': sum(info.file_size for info in infos),
                'manifest': manifest_identity, 'manifest_schema': schema}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--manifest-sha256', required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--archive', type=Path)
    source.add_argument('--parts-dir', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--hydrate', action='store_true', help='restore the byte-pinned E13C8 backup and its original inputs/completed return')
    args = parser.parse_args()
    started = time.monotonic()
    output = args.output_dir
    if output.exists() or output.is_symlink():
        raise FileExistsError('fresh output directory required; preserve previous attempts')
    output.mkdir(parents=True, exist_ok=False)
    selected = []
    stage = 'EXTERNAL_MANIFEST'
    prior_invocations = 0
    try:
        valid_pin({'bytes': 0, 'sha256': args.manifest_sha256})
        if not args.manifest.is_file() or args.manifest.is_symlink() or sha(args.manifest) != args.manifest_sha256:
            raise ValueError('external transfer manifest identity mismatch')
        manifest = load_json(args.manifest.read_bytes())
        validate_transfer(manifest)
        verify_file(Path(__file__), manifest['restore_helper'])
        stage = 'COMPLETE_ARCHIVE'
        if args.archive is not None:
            verify_file(args.archive, manifest['archive'])
            archive = args.archive.resolve()
        else:
            selected = select_parts(args.parts_dir, manifest['parts'])
            archive = output / 'REASSEMBLED_COMPLETE.zip'
            reassemble(selected, archive, manifest['archive'])
        stage = 'OUTER_PAYLOADS'
        required = {item['relative_archive']: item for item in DEPENDENCIES.values()}
        required['code/restore_transfer.py'] = manifest['restore_helper']
        outer = extract_verified(archive, output / 'package', PACKAGE_ROOT + '/PACKAGE_MANIFEST.json',
                                 PACKAGE_ROOT + '/', PACKAGE_SCHEMA, required, manifest['package_manifest'])
        package = output / 'package' / PACKAGE_ROOT
        hydrated = {}
        if args.hydrate:
            stage = 'E13C8_DEPENDENCY_BYTES'
            actual_dependencies = {name: verify_file(package / item['relative_archive'], item)
                                   for name, item in DEPENDENCIES.items()}
            kit_archive = package / DEPENDENCIES['E13C8_RECOVERY_KIT']['relative_archive']
            kit_root = output / 'runtime' / 'E13C8_RECOVERY_KIT'
            kit_required = {item['relative_path']: item for item in PRIOR_RECOVERY.values()}
            kit_extraction = extract_verified(kit_archive, kit_root, 'KIT_MANIFEST.json', '',
                                             'bass-he-e13c8-recovery-kit-manifest-v1', kit_required)
            helper = kit_root / PRIOR_RECOVERY['helper']['relative_path']
            old_manifest = kit_root / PRIOR_RECOVERY['transfer_manifest']['relative_path']
            verify_file(helper, PRIOR_RECOVERY['helper'])
            verify_file(old_manifest, PRIOR_RECOVERY['transfer_manifest'])
            prior_output = output / 'runtime' / 'E13C8'
            command = [sys.executable, '-B', str(helper.resolve()), '--manifest', str(old_manifest.resolve()),
                       '--manifest-sha256', PRIOR_RECOVERY['transfer_manifest']['sha256'], '--archive',
                       str((package / DEPENDENCIES['E13C8_COMPLETE']['relative_archive']).resolve()),
                       '--output-dir', str(prior_output.resolve()), '--hydrate']
            stdout_path = output / 'E13C8_HYDRATE.stdout'
            stderr_path = output / 'E13C8_HYDRATE.stderr'
            stage = 'PINNED_E13C8_RESTORE'
            prior_started = time.monotonic()
            with stdout_path.open('xb') as stdout, stderr_path.open('xb') as stderr:
                prior_invocations += 1
                process = subprocess.run(command, stdout=stdout, stderr=stderr, check=False)
            if process.returncode != 0:
                raise RuntimeError('pinned E13C8 restore failed with exit ' + str(process.returncode))
            prior_receipt_path = prior_output / 'RESTORE_RECEIPT.json'
            prior_receipt = load_json(prior_receipt_path.read_bytes())
            if (prior_receipt.get('schema') != 'bass-he-e13c8-restore-receipt-v1'
                    or prior_receipt.get('status') != 'PASS_COMPLETE_RESTORE'
                    or prior_receipt.get('scientific_kernel_calls') != 0
                    or prior_receipt.get('MPI_invocations') != 0
                    or prior_receipt.get('automatic_retries') != 0):
                raise ValueError('unexpected pinned E13C8 restore receipt')
            expected_prior_package = (prior_output / 'package' / 'BASS_HE_E13C8_FULL_FINITE_REDUCTION_20261011_v1').resolve()
            if Path(prior_receipt['package_directory']).resolve() != expected_prior_package or not expected_prior_package.is_dir():
                raise ValueError('unexpected restored E13C8 package directory')
            hydrated = {'dependency_bytes': actual_dependencies, 'kit': kit_extraction,
                        'command': command, 'returncode': process.returncode,
                        'elapsed_seconds': time.monotonic() - prior_started,
                        'receipt': {'path': str(prior_receipt_path.resolve()), **pin(prior_receipt_path)},
                        'stdout': {'path': str(stdout_path.resolve()), **pin(stdout_path)},
                        'stderr': {'path': str(stderr_path.resolve()), **pin(stderr_path)},
                        'package_directory': str(expected_prior_package),
                        'prior_hydrated_dependencies': prior_receipt['hydrated_dependencies']}
        stage = 'RECEIPT'
        receipt = {'schema': 'bass-he-e13c9-restore-receipt-v1', 'status': 'PASS_COMPLETE_RESTORE',
                   'finished_utc': utc_now(), 'archive': manifest['archive'], 'selected_parts': selected,
                   'external_transfer_manifest_sha256': args.manifest_sha256, 'outer': outer,
                   'hydrated_E13C8': hydrated, 'package_directory': str(package.resolve()),
                   'scientific_kernel_calls': 0, 'MPI_invocations': 0, 'NCP_execute_invocations': 0,
                   'prior_restore_helper_invocations': prior_invocations, 'automatic_retries': 0,
                   'elapsed_seconds': time.monotonic() - started}
        save(output / 'RESTORE_RECEIPT.json', receipt)
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0
    except BaseException as error:
        save(output / 'FIRST_FAILURE.json', {
            'schema': 'bass-he-e13c9-restore-failure-v1', 'status': 'FAIL_PRESERVED_NO_AUTOMATIC_RETRY',
            'failed_utc': utc_now(), 'stage': stage, 'error_type': type(error).__name__, 'error': str(error),
            'selected_parts': selected, 'scientific_kernel_calls': 0, 'MPI_invocations': 0,
            'NCP_execute_invocations': 0, 'prior_restore_helper_invocations': prior_invocations,
            'automatic_retries': 0, 'elapsed_seconds': time.monotonic() - started})
        raise


if __name__ == '__main__':
    raise SystemExit(main())
