#!/usr/bin/env python3
"""Offline H1B1 component: OpenPGP -> Release -> Packages.xz -> package bytes.

The caller must separately admit the trust policy, gpgv executable, key ownership,
key lifecycle and archive retrieval provenance. This module does not download,
install, extract or execute packages and cannot admit a complete host epoch.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import json
import lzma
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Mapping

SNAPSHOT_ID = '20250115T120000Z'
SHA256_RE = re.compile(r'[0-9a-f]{64}\Z')
FINGERPRINT_RE = re.compile(r'(?:[0-9A-F]{40}|[0-9A-F]{64})\Z')
FIELD_RE = re.compile(r'[A-Za-z0-9][A-Za-z0-9-]*\Z')
ARCHIVE_PATH_RE = re.compile(r'[A-Za-z0-9][A-Za-z0-9+._~/-]*\Z')
# Release lists include signed DEP-11 HiDPI names such as icons-64x64@2.tar.
# This grammar is NOT used for package payload paths or requested download URLs.
RELEASE_INDEX_PATH_RE = re.compile(r'[A-Za-z0-9][A-Za-z0-9+._~@/-]*\Z')
PACKAGE_RE = re.compile(r'[a-z0-9][a-z0-9+.-]*\Z')


class ChainError(ValueError):
    """A typed rejection; no receipt is returned for an incomplete chain."""


def _require(ok: bool, code: str) -> None:
    if not ok:
        raise ChainError(code)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _archive_path(value: str) -> str:
    _require(isinstance(value, str) and bool(ARCHIVE_PATH_RE.fullmatch(value)),
             'UNSAFE_ARCHIVE_PATH')
    _require(all(part not in ('', '.', '..') for part in value.split('/')),
             'UNSAFE_ARCHIVE_PATH')
    return value


def _release_index_path(value: str) -> str:
    """Canonical literal metadata name; no normalization or row filtering."""
    _require(isinstance(value, str) and bool(RELEASE_INDEX_PATH_RE.fullmatch(value)),
             'UNSAFE_ARCHIVE_PATH')
    _require(all(part not in ('', '.', '..') for part in value.split('/')),
             'UNSAFE_ARCHIVE_PATH')
    return value


def _size(value: str) -> int:
    _require(bool(re.fullmatch(r'[0-9]{1,19}', value)), 'INVALID_SIZE_FIELD')
    size = int(value)
    _require(size <= 2**63 - 1, 'INVALID_SIZE_FIELD')
    return size


@dataclass(frozen=True)
class ArchivePolicy:
    """Declared trust inputs, not a self-issued organizational trust certificate."""
    keyring_sha256: str
    allowed_primary_fingerprints: tuple[str, ...]
    suite: str
    codename: str
    architecture: str
    index_name: str
    required: tuple[tuple[str, str, str], ...]
    snapshot: str = SNAPSHOT_ID
    max_inrelease_bytes: int = 4 * 1024 * 1024
    max_compressed_index_bytes: int = 32 * 1024 * 1024
    max_index_bytes: int = 128 * 1024 * 1024
    max_keyring_bytes: int = 8 * 1024 * 1024
    gpgv_timeout_seconds: int = 20

    def __post_init__(self) -> None:
        _require(isinstance(self.keyring_sha256, str)
                 and bool(SHA256_RE.fullmatch(self.keyring_sha256)), 'POLICY_KEYRING_HASH')
        fps = self.allowed_primary_fingerprints
        _require(type(fps) is tuple and bool(fps)
                 and all(isinstance(f, str) and FINGERPRINT_RE.fullmatch(f) for f in fps)
                 and len(fps) == len(set(fps)), 'POLICY_SIGNER_ALLOWLIST')
        _require(self.snapshot == SNAPSHOT_ID and self.codename == 'noble'
                 and self.suite in ('noble', 'noble-updates', 'noble-security')
                 and self.architecture == 'amd64', 'POLICY_ARCHIVE_DOMAIN')
        _archive_path(self.index_name)
        pieces = self.index_name.split('/')
        _require(len(pieces) == 3 and pieces[0] in ('main', 'restricted', 'universe', 'multiverse')
                 and pieces[1] == 'binary-amd64' and pieces[2] == 'Packages.xz',
                 'POLICY_INDEX_DOMAIN')
        _require(type(self.required) is tuple and bool(self.required), 'POLICY_REQUIRED_PACKAGES')
        for item in self.required:
            _require(type(item) is tuple and len(item) == 3
                     and all(type(s) is str for s in item), 'POLICY_REQUIRED_PACKAGES')
            name, version, arch = item
            _require(bool(PACKAGE_RE.fullmatch(name)) and bool(version)
                     and all(33 <= ord(c) <= 126 for c in version)
                     and arch in ('amd64', 'all'), 'POLICY_REQUIRED_PACKAGES')
        _require(len(set(self.required)) == len(self.required), 'POLICY_DUPLICATE_REQUEST')
        for value in (self.max_inrelease_bytes, self.max_compressed_index_bytes,
                      self.max_index_bytes, self.max_keyring_bytes, self.gpgv_timeout_seconds):
            _require(type(value) is int and 0 < value <= 1024 * 1024 * 1024, 'POLICY_LIMIT')


def _deb822(data: bytes) -> list[dict[str, str]]:
    """Strict field uniqueness; hashing always uses original bytes, not this view."""
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise ChainError('DEB822_INVALID_UTF8') from exc
    _require(not any(ord(c) < 32 and c not in '\n\r\t' for c in text), 'DEB822_CONTROL_BYTE')
    rows: list[dict[str, str]] = []
    fields: dict[str, str] = {}
    previous: str | None = None
    for raw in text.split('\n'):
        line = raw.removesuffix('\r')
        _require('\r' not in line, 'DEB822_BARE_CR')
        if not line:
            if fields:
                rows.append(fields)
            fields, previous = {}, None
            continue
        if line[0] in ' \t':
            _require(previous is not None, 'DEB822_ORPHAN_CONTINUATION')
            fields[previous] += '\n' + line[1:]
            continue
        key, sep, value = line.partition(':')
        _require(bool(sep) and bool(FIELD_RE.fullmatch(key)), 'DEB822_INVALID_FIELD')
        key = key.lower()
        _require(key not in fields, 'DUPLICATE_FIELD:' + key)
        fields[key], previous = value.strip(' \t'), key
    if fields:
        rows.append(fields)
    return rows


def _authenticated_release(inrelease: bytes, keyring: bytes, policy: ArchivePolicy,
                           gpgv: Path) -> tuple[bytes, dict]:
    _require(inrelease.startswith(b'-----BEGIN PGP SIGNED MESSAGE-----'), 'SIGNATURE_ENVELOPE_REQUIRED')
    _require(_sha(keyring) == policy.keyring_sha256, 'KEYRING_HASH_MISMATCH')
    try:
        executable = Path(gpgv).resolve(strict=True)
    except (OSError, TypeError) as exc:
        raise ChainError('GPGV_RUNTIME_UNAVAILABLE') from exc
    _require(executable.is_file() and os.access(executable, os.X_OK), 'GPGV_RUNTIME_UNAVAILABLE')
    executable_sha = _sha(executable.read_bytes())
    with tempfile.TemporaryDirectory(prefix='rei-h1b1-verify-') as directory:
        root = Path(directory)
        home = root / 'gnupg'
        home.mkdir(mode=0o700)
        ring = root / 'admitted-keyring.gpg'
        source = root / 'InRelease'
        output = root / 'verified-Release'
        ring.write_bytes(keyring)
        source.write_bytes(inrelease)
        command = [str(executable), '--homedir', str(home), '--keyring', str(ring),
                   '--status-fd', '1', '--output', str(output), str(source)]
        try:
            run = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, timeout=policy.gpgv_timeout_seconds,
                                 check=False, env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C',
                                                   'HOME': str(home), 'GNUPGHOME': str(home)})
        except subprocess.TimeoutExpired as exc:
            raise ChainError('GPGV_RUNTIME_TIMEOUT') from exc
        except OSError as exc:
            raise ChainError('GPGV_RUNTIME_UNAVAILABLE') from exc
        _require(run.returncode == 0, 'SIGNATURE_VERIFICATION_FAILED')
        _require(output.is_file() and output.stat().st_size <= policy.max_inrelease_bytes,
                 'SIGNATURE_AUTHENTICATED_OUTPUT_MISSING_OR_OVERSIZED')
        verified = output.read_bytes()
    status = run.stdout.decode('utf-8', errors='replace')
    signatures = []
    snapshot_epoch = int(datetime.strptime(policy.snapshot, '%Y%m%dT%H%M%SZ')
                         .replace(tzinfo=timezone.utc).timestamp())
    for line in status.splitlines():
        if not line.startswith('[GNUPG:] '):
            continue
        parts = line[len('[GNUPG:] '):].split()
        _require(bool(parts), 'SIGNATURE_STATUS_INVALID')
        _require(parts[0] not in ('BADSIG', 'ERRSIG', 'NO_PUBKEY', 'NODATA', 'FAILURE'),
                 'SIGNATURE_STATUS_REJECTED')
        if parts[0] != 'VALIDSIG':
            continue
        fields = parts[1:]
        _require(len(fields) in (9, 10), 'SIGNATURE_STATUS_INVALID')
        primary = fields[9] if len(fields) == 10 else fields[0]
        _require(bool(FINGERPRINT_RE.fullmatch(primary))
                 and primary in policy.allowed_primary_fingerprints, 'SIGNER_NOT_ALLOWED')
        _require(fields[7] in ('8', '9', '10', '11'), 'SIGNATURE_HASH_ALGORITHM_REJECTED')
        _require(fields[2].isdigit(), 'SIGNATURE_TIMESTAMP_INVALID')
        timestamp = int(fields[2])
        _require(timestamp <= snapshot_epoch, 'SIGNATURE_AFTER_SNAPSHOT')
        signatures.append({'primary_fingerprint': primary, 'signing_fingerprint': fields[0],
                           'timestamp': timestamp, 'hash_algorithm': int(fields[7])})
    _require(bool(signatures), 'SIGNATURE_VALID_STATUS_MISSING')
    return verified, {'exit_code': run.returncode, 'status_text': status,
                      'stderr': run.stderr.decode('utf-8', errors='replace'),
                      'executable': str(executable), 'executable_sha256': executable_sha,
                      'signatures': signatures}


def _release_entries(release: dict[str, str]) -> dict[str, tuple[str, int]]:
    _require('sha256' in release, 'RELEASE_SHA256_MISSING')
    entries = {}
    for line in release['sha256'].splitlines():
        if not line.strip():
            continue
        row = line.split()
        _require(len(row) == 3, 'RELEASE_SHA256_ROW_INVALID')
        checksum, count, path = row
        _release_index_path(path)
        _require(path not in entries, 'DUPLICATE_RELEASE_INDEX:' + path)
        _require(bool(SHA256_RE.fullmatch(checksum)), 'RELEASE_SHA256_INVALID')
        entries[path] = (checksum, _size(count))
    return entries


def _unpack_index(packed: bytes, limit: int) -> bytes:
    """Decode a complete XZ file, including concatenated Streams and Padding.

    XZ format sections 2/2.2 permit multiple streams and four-byte-aligned
    null padding. Every stream is decoded/checked; no trailing data is ignored.
    The output budget applies to the entire file, not independently per stream.
    Chunked input avoids repeatedly copying the whole remaining file for many
    small streams. Each decoder retains the existing 128 MiB memory limit.
    """
    _require(bool(packed), 'COMPRESSED_INDEX_TRUNCATED_OR_TRAILING')
    plain = bytearray()
    offset = 0
    try:
        while offset < len(packed):
            decoder = lzma.LZMADecompressor(format=lzma.FORMAT_XZ, memlimit=128 * 1024 * 1024)
            while not decoder.eof:
                chunk = b''
                if decoder.needs_input:
                    chunk = packed[offset:offset + 65536]
                    _require(bool(chunk), 'COMPRESSED_INDEX_TRUNCATED_OR_TRAILING')
                    offset += len(chunk)
                plain.extend(decoder.decompress(chunk, max_length=min(65536, limit - len(plain) + 1)))
                _require(len(plain) <= limit, 'DECOMPRESSED_INDEX_LIMIT')
            offset -= len(decoder.unused_data)
            padding_start = offset
            while offset < len(packed) and packed[offset] == 0:
                offset += 1
            _require((offset - padding_start) % 4 == 0, 'COMPRESSED_INDEX_TRUNCATED_OR_TRAILING')
    except lzma.LZMAError as exc:
        raise ChainError('COMPRESSED_INDEX_INVALID') from exc
    return bytes(plain)


def verify_chain(*, inrelease: bytes, index_bytes: bytes, debs: Mapping[str, bytes],
                 keyring: bytes, policy: ArchivePolicy, gpgv: Path) -> dict:
    """Verify one index and the exact requested package payload set, offline.

    A successful report is evidence relative to the supplied trust policy.
    It is not an approved Ubuntu trust root, proof of retrieval from a Snapshot
    URL, DEB-format/ELF verification, complete dependency closure or host admission.
    """
    _require(type(policy) is ArchivePolicy, 'POLICY_TYPE')
    policy.__post_init__()
    for data, limit, name in ((inrelease, policy.max_inrelease_bytes, 'INRELEASE'),
                              (keyring, policy.max_keyring_bytes, 'KEYRING'),
                              (index_bytes, policy.max_compressed_index_bytes, 'INDEX')):
        _require(type(data) is bytes and 0 < len(data) <= limit, name + '_INPUT_TYPE_OR_SIZE')
    supplied = dict(debs)
    _require(all(type(k) is str and type(v) is bytes for k, v in supplied.items()), 'PAYLOAD_TYPE')
    for path in supplied:
        _archive_path(path)
    release_bytes, signature = _authenticated_release(inrelease, keyring, policy, gpgv)
    rows = _deb822(release_bytes)
    _require(len(rows) == 1, 'RELEASE_STANZA_COUNT')
    release = rows[0]
    _require(release.get('origin') == 'Ubuntu' and release.get('label') == 'Ubuntu'
             and release.get('suite') == policy.suite and release.get('codename') == policy.codename
             and policy.architecture in release.get('architectures', '').split()
             and policy.index_name.split('/')[0] in release.get('components', '').split(),
             'RELEASE_IDENTITY_MISMATCH')
    try:
        date = parsedate_to_datetime(release['date'])
        _require(date.tzinfo is not None, 'RELEASE_DATE_TIMEZONE_REQUIRED')
    except (KeyError, ValueError, TypeError) as exc:
        raise ChainError('RELEASE_DATE_INVALID') from exc
    snapshot = datetime.strptime(policy.snapshot, '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc)
    _require(date <= snapshot, 'RELEASE_AFTER_SNAPSHOT')
    entries = _release_entries(release)
    _require(policy.index_name in entries, 'RELEASE_INDEX_UNLISTED')
    _require(entries[policy.index_name] == (_sha(index_bytes), len(index_bytes)), 'INDEX_HASH_OR_SIZE')
    plain = _unpack_index(index_bytes, policy.max_index_bytes)
    plain_name = policy.index_name[:-3]
    if plain_name in entries:
        _require(entries[plain_name] == (_sha(plain), len(plain)), 'UNCOMPRESSED_INDEX_HASH_OR_SIZE')

    providers: dict[tuple[str, str, str], dict] = {}
    filenames: set[str] = set()
    for record in _deb822(plain):
        _require(all(key in record for key in ('package', 'version', 'architecture', 'filename', 'size', 'sha256')),
                 'PACKAGE_REQUIRED_FIELD_MISSING')
        name, version, arch = record['package'], record['version'], record['architecture']
        _require(bool(PACKAGE_RE.fullmatch(name)) and bool(version)
                 and all(33 <= ord(c) <= 126 for c in version)
                 and arch in (policy.architecture, 'all'), 'PACKAGE_IDENTITY_INVALID')
        identity = (name, version, arch)
        _require(identity not in providers, 'DUPLICATE_PACKAGE:' + name)
        filename = _archive_path(record['filename'])
        _require(filename.startswith('pool/') and filename.endswith('.deb'), 'UNSAFE_ARCHIVE_PATH')
        _require(filename not in filenames, 'DUPLICATE_PACKAGE_FILENAME')
        _require(bool(SHA256_RE.fullmatch(record['sha256'])), 'PACKAGE_SHA256_INVALID')
        providers[identity] = {'package': name, 'version': version, 'architecture': arch,
                               'filename': filename, 'size': _size(record['size']),
                               'sha256': record['sha256']}
        filenames.add(filename)
    selected = []
    for identity in policy.required:
        _require(identity in providers, 'PROVIDER_UNRESOLVED:' + ':'.join(identity))
        selected.append(providers[identity])
    expected_files = {row['filename'] for row in selected}
    _require(set(supplied) == expected_files, 'PAYLOAD_SET_MISMATCH')
    for row in selected:
        payload = supplied[row['filename']]
        _require(len(payload) == row['size'] and _sha(payload) == row['sha256'],
                 'DEB_HASH_OR_SIZE:' + row['package'])
    policy_bytes = json.dumps(asdict(policy), sort_keys=True, separators=(',', ':'),
                              ensure_ascii=True, allow_nan=False).encode('utf-8')
    return {
        'schema': 'rei-h1b1-signed-archive-chain-component/v1',
        'status': 'PASS_H1B1_SIGNED_ARCHIVE_CHAIN_COMPONENT',
        'authority_effect': 'NONE', 'full_census_complete': False,
        'snapshot_retrieval_attested': False, 'installed_files_verified': False,
        'key_organizational_ownership': 'CALLER_POLICY_NOT_PROVED_BY_COMPONENT',
        'key_revocation_assessment': 'NOT_PERFORMED_BY_GPGV',
        'current_archive_freshness': 'NOT_ASSESSED_HISTORICAL_AUDIT_ONLY',
        'snapshot_selector': policy.snapshot, 'policy_sha256': _sha(policy_bytes),
        'release': {'suite': policy.suite, 'codename': policy.codename,
                    'date': date.isoformat(), 'valid_until': release.get('valid-until'),
                    'index_name': policy.index_name},
        'input_sha256': {'inrelease': _sha(inrelease), 'keyring': _sha(keyring),
                         'authenticated_release': _sha(release_bytes),
                         'compressed_index': _sha(index_bytes), 'decompressed_index': _sha(plain)},
        'signing_primary_fingerprints': sorted({s['primary_fingerprint'] for s in signature['signatures']}),
        'signature_verification': signature, 'verified_packages': selected,
        'uncompressed_index_crosscheck': plain_name in entries,
        'package_payload_format_validation': 'NOT_PERFORMED_OPAQUE_BYTES_ONLY',
        'package_install_or_execution': 'NOT_RUN', 'native_runtime': 'NOT_RUN',
        'next': 'H1B1_ACTUAL_APPROVED_TRUST_ROOT_RETRIEVAL_AND_PROVIDER_CENSUS',
    }
