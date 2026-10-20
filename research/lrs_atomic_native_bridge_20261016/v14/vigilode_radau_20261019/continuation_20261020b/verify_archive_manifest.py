#!/usr/bin/env python3
"""Verify the embedded optimization payload manifest without extracting files.

Exit 0 means exact regular-file set and payload hashes/sizes agree with MANIFEST.
Exit 1 means an observed verification failure; exit 2 is an invocation error.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import tarfile
import time

SCHEMA = 'optimization-archive-verification-v1'
CHUNK = 1024 * 1024

def digest_file(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(CHUNK), b''):
            result.update(block)
    return result.hexdigest()

def member_parts(name):
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise ValueError('invalid archive member path: ' + repr(name))
    return path.parts

def verify(archive):
    start = time.monotonic()
    report = {
        'schema': SCHEMA,
        'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'archive': str(archive.resolve()),
        'archive_bytes': archive.stat().st_size,
        'archive_sha256': digest_file(archive),
        'status': 'FAIL',
        'errors': [],
        'extraction_performed': False,
    }
    errors = report['errors']
    try:
        # A streaming first pass finds the sole top-level manifest. No payload is extracted.
        candidates = []
        with tarfile.open(archive, 'r|*') as stream:
            for member in stream:
                parts = member_parts(member.name)
                if len(parts) == 2 and parts[1] == 'MANIFEST.json':
                    if not member.isfile():
                        raise ValueError('manifest is not a regular file')
                    if member.size > 16 * 1024 * 1024:
                        raise ValueError('manifest exceeds bounded 16 MiB reader limit')
                    candidates.append((parts[0], stream.extractfile(member).read()))
        if len(candidates) != 1:
            raise ValueError('expected exactly one top-level MANIFEST.json; observed ' + str(len(candidates)))
        root, manifest_bytes = candidates[0]
        manifest = json.loads(manifest_bytes)
        report['archive_root'] = root
        report['manifest_sha256'] = hashlib.sha256(manifest_bytes).hexdigest()
        report['manifest_bytes'] = len(manifest_bytes)
        if manifest.get('schema') != 'optimization-final-payload-v1':
            raise ValueError('unsupported embedded manifest schema')
        if manifest.get('manifest_self_excluded') is not True:
            raise ValueError('manifest must explicitly exclude itself')
        expected = manifest['files']
        if not isinstance(expected, dict):
            raise ValueError('manifest files is not a mapping')
        for name, metadata in expected.items():
            member_parts(name)
            if name == 'MANIFEST.json':
                raise ValueError('manifest unexpectedly lists itself')
            if type(metadata.get('bytes')) is not int or metadata['bytes'] < 0:
                raise ValueError('invalid byte count for ' + name)
            if not re.fullmatch('[0-9a-f]{64}', metadata.get('sha256', '')):
                raise ValueError('invalid SHA256 for ' + name)
        expected_bytes = sum(item['bytes'] for item in expected.values())
        if manifest.get('file_count') != len(expected):
            errors.append({'kind': 'manifest_file_count_mismatch'})
        if manifest.get('payload_bytes') != expected_bytes:
            errors.append({'kind': 'manifest_payload_bytes_mismatch'})
        seen_names = set()
        observed_payload = set()
        regular_count = 0
        payload_bytes = 0
        directories = 0
        verified = 0
        with tarfile.open(archive, 'r|*') as stream:
            for member in stream:
                parts = member_parts(member.name)
                if member.name in seen_names:
                    errors.append({'kind': 'duplicate_member', 'path': member.name})
                seen_names.add(member.name)
                if parts[0] != root:
                    errors.append({'kind': 'unexpected_archive_root', 'path': member.name})
                    continue
                if member.isdir():
                    directories += 1
                    continue
                if not member.isfile():
                    errors.append({'kind': 'unsupported_nonregular_member', 'path': member.name})
                    continue
                regular_count += 1
                relative = str(PurePosixPath(*parts[1:]))
                reader = stream.extractfile(member)
                digest = hashlib.sha256()
                size = 0
                for block in iter(lambda: reader.read(CHUNK), b''):
                    size += len(block)
                    digest.update(block)
                actual_hash = digest.hexdigest()
                if relative == 'MANIFEST.json':
                    if actual_hash != report['manifest_sha256'] or size != len(manifest_bytes):
                        errors.append({'kind': 'manifest_readback_mismatch'})
                    continue
                observed_payload.add(relative)
                payload_bytes += size
                metadata = expected.get(relative)
                if metadata is None:
                    errors.append({'kind': 'unexpected_regular_file', 'path': relative})
                    continue
                if size != metadata['bytes'] or actual_hash != metadata['sha256']:
                    errors.append({'kind': 'payload_mismatch', 'path': relative,
                                   'expected_bytes': metadata['bytes'], 'actual_bytes': size,
                                   'expected_sha256': metadata['sha256'], 'actual_sha256': actual_hash})
                else:
                    verified += 1
        for name in sorted(set(expected) - observed_payload):
            errors.append({'kind': 'missing_regular_file', 'path': name})
        report.update(expected_payload_files=len(expected), observed_payload_files=len(observed_payload),
                      verified_payload_files=verified, regular_files_including_manifest=regular_count,
                      directory_members=directories, expected_payload_bytes=expected_bytes,
                      observed_payload_bytes=payload_bytes)
        if regular_count != len(expected) + 1:
            errors.append({'kind': 'regular_file_count_mismatch',
                           'expected': len(expected) + 1, 'actual': regular_count})
        if payload_bytes != expected_bytes:
            errors.append({'kind': 'payload_byte_total_mismatch'})
    except (OSError, ValueError, KeyError, TypeError, tarfile.TarError) as exc:
        errors.append({'kind': 'verification_exception', 'message': str(exc)})
    report['wall_s'] = time.monotonic() - start
    report['status'] = 'PASS' if not errors else 'FAIL'
    return report

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        report = verify(args.archive)
    except OSError as exc:
        report = {'schema': SCHEMA, 'status': 'FAIL', 'archive': str(args.archive),
                  'errors': [{'kind': 'archive_read_error', 'message': str(exc)}],
                  'extraction_performed': False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
