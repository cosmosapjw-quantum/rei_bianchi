#!/usr/bin/env python3
"""Bounded H1B1 real-provider probe; no package install or payload execution.

Reuses the signature/index verifier with a narrowly amended Release-name grammar.
A provider/member result is not an installed-filesystem or runtime certificate.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import resource
import subprocess
import sys
import tarfile
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

DONOR_BLOB = 'dfed33dd8428cd3293a8292088c21ba23f6b2f43'
BASE = 'https://snapshot.ubuntu.com/ubuntu/20250115T120000Z/'
IDENTITY = ('gcc-13-x86-64-linux-gnu', '13.3.0-6ubuntu2~24.04', 'amd64')
DEB_SHA = '7cd398670e8306eabc9e77202f356a3206c440bd9f3dc764680a19be01784776'
MEMBER = 'usr/bin/x86_64-linux-gnu-gcc-13'
MEMBER_SHA = '6117c52522997d2aaccb2b52b3c6bf42c0a6c5edb1d718431fed6b2fc5fec234'
SIGNER = 'F6ECB3762474EDA9D21B7022871920D1991BC93C'
SAVED_INRELEASE_SHA = '26b3656730b29965e984a5d2319b6870c456ad1bb5362267987bb5b015905372'
MAX_DEB = 64 * 1024 * 1024


class ProbeError(ValueError):
    """Typed failure of the bounded provider/member probe."""


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ProbeError(code)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_donor():
    path = Path(__file__).with_name('signed_archive_chain.py')
    data = path.read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
    require(blob == DONOR_BLOB, 'DONOR_BLOB_MISMATCH')
    name = '_rei_h1b1_signed_chain_pinned'
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


chain = _load_donor()


def _member_path(name: str) -> str:
    require(type(name) is str and bool(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9+._~/-]*', name)),
            'MEMBER_PATH_INVALID')
    require(all(part not in ('', '.', '..') for part in name.split('/')), 'MEMBER_PATH_INVALID')
    return name


def validate_url(url: str) -> str:
    try:
        parts = urlsplit(url)
        valid = (parts.scheme == 'https' and parts.netloc == 'snapshot.ubuntu.com'
                 and not parts.query and not parts.fragment and url.startswith(BASE))
        require(valid, 'SNAPSHOT_URL_REJECTED')
        _member_path(url[len(BASE):])
    except (ValueError, TypeError) as exc:
        raise ProbeError('SNAPSHOT_URL_REJECTED') from exc
    return url


class _SnapshotRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        validate_url(newurl)
        return super().redirect_request(request, fp, code, message, headers, newurl)


def _tar_from_deb(tool: Path, deb: Path, output: Path, option: str, limit: int) -> dict:
    def limits():
        resource.setrlimit(resource.RLIMIT_FSIZE, (limit, limit))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    try:
        with output.open('xb') as stream:
            run = subprocess.run([str(tool), option, str(deb)], stdin=subprocess.DEVNULL,
                                 stdout=stream, stderr=subprocess.PIPE, timeout=30,
                                 check=False, preexec_fn=limits,
                                 env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C',
                                      'DPKG_DEB_THREADS_MAX': '1'})
        require(run.returncode == 0 and 0 < output.stat().st_size <= limit,
                'TAR_OUTPUT_LIMIT_OR_TOOL_FAILURE')
    except (OSError, subprocess.SubprocessError) as exc:
        raise ProbeError('TAR_OUTPUT_LIMIT_OR_TOOL_FAILURE') from exc
    return {'option': option, 'exit_code': run.returncode,
            'stderr': run.stderr.decode('utf-8', errors='replace'),
            'tar_size': output.stat().st_size, 'tar_sha256': sha(output.read_bytes())}


def _read_unique_regular(archive_path: Path, requested: str, limit: int) -> tuple[bytes, int]:
    try:
        with tarfile.open(archive_path, 'r:') as archive:
            matches = []
            for count, info in enumerate(archive, 1):
                require(count <= 100000, 'TAR_ENTRY_LIMIT')
                normalized = info.name[2:] if info.name.startswith('./') else info.name
                if normalized == requested:
                    matches.append(info)
            require(len(matches) == 1, 'MEMBER_CARDINALITY:' + requested)
            info = matches[0]
            require(info.isreg() and not info.issparse(), 'MEMBER_NOT_REGULAR:' + requested)
            require(0 <= info.size <= limit, 'MEMBER_SIZE_LIMIT')
            stream = archive.extractfile(info)
            require(stream is not None, 'MEMBER_READ_FAILED')
            with stream:
                payload = stream.read(limit + 1)
            require(len(payload) == info.size, 'MEMBER_SIZE_MISMATCH')
            return payload, info.mode
    except (tarfile.TarError, OSError, EOFError) as exc:
        raise ProbeError('TAR_OUTPUT_LIMIT_OR_TOOL_FAILURE') from exc


def inspect_member(payload: bytes, *, expected_deb_sha256: str,
                   expected_identity: tuple[str, str, str], member_path: str,
                   expected_member_sha256: str, dpkg_deb: Path,
                   max_tar_bytes: int = 256 * 1024 * 1024) -> dict:
    """Read control/data tar streams; never extract a filesystem or run a member."""
    require(type(payload) is bytes and 0 < len(payload) <= MAX_DEB, 'DEB_INPUT_LIMIT')
    require(sha(payload) == expected_deb_sha256, 'DEB_PIN_MISMATCH')
    _member_path(member_path)
    require(type(expected_identity) is tuple and len(expected_identity) == 3
            and all(type(x) is str and x for x in expected_identity), 'IDENTITY_INPUT_INVALID')
    require(type(max_tar_bytes) is int and 0 < max_tar_bytes <= 512 * 1024 * 1024,
            'TAR_LIMIT_INVALID')
    try:
        tool = Path(dpkg_deb).resolve(strict=True)
        require(tool.is_file() and os.access(tool, os.X_OK), 'DPKG_DEB_UNAVAILABLE')
        tool_hash = sha(tool.read_bytes())
    except OSError as exc:
        raise ProbeError('DPKG_DEB_UNAVAILABLE') from exc
    with tempfile.TemporaryDirectory(prefix='rei-deb-member-') as directory:
        root = Path(directory)
        deb = root / 'input.deb'
        deb.write_bytes(payload)
        control_tar, data_tar = root / 'control.tar', root / 'data.tar'
        control_tool = _tar_from_deb(tool, deb, control_tar, '--ctrl-tarfile',
                                     min(max_tar_bytes, 8 * 1024 * 1024))
        control, _ = _read_unique_regular(control_tar, 'control', 1024 * 1024)
        records = chain._deb822(control)
        require(len(records) == 1, 'CONTROL_STANZA_COUNT')
        identity = tuple(records[0].get(k) for k in ('package', 'version', 'architecture'))
        require(identity == expected_identity, 'CONTROL_IDENTITY_MISMATCH')
        data_tool = _tar_from_deb(tool, deb, data_tar, '--fsys-tarfile', max_tar_bytes)
        member, mode = _read_unique_regular(data_tar, member_path, MAX_DEB)
        require(sha(member) == expected_member_sha256, 'MEMBER_HASH_MISMATCH')
    require(sha(tool.read_bytes()) == tool_hash, 'DPKG_DEB_IDENTITY_CHANGED')
    return {'schema': 'rei-h1b1-deb-member/v1', 'status': 'PASS_DEB_MEMBER_BYTES_ONLY',
            'package_identity': list(identity), 'deb_sha256': sha(payload),
            'control_sha256': sha(control), 'member_path': member_path,
            'member_sha256': sha(member), 'member_size': len(member), 'member_mode': mode,
            'dpkg_deb': {'path': str(tool), 'sha256': tool_hash,
                         'control': control_tool, 'data': data_tool},
            'filesystem_extracted': False, 'installed_files_verified': False,
            'payload_executed': False, 'authority_effect': 'NONE'}


def _write(path: Path, data: bytes) -> None:
    with path.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def _json(path: Path, value: dict) -> None:
    _write(path, (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode())


def _download(url: str, limit: int, target: Path, events: list) -> bytes:
    validate_url(url)
    event = {'requested_url': url, 'started_utc': utc(), 'retry_count': 0}
    events.append(event)
    opener = build_opener(ProxyHandler({}), _SnapshotRedirects())
    try:
        request = Request(url, headers={'User-Agent': 'REI-H1B1-public-archive-probe/1',
                                        'Accept-Encoding': 'identity'})
        with opener.open(request, timeout=45) as response:
            validate_url(response.geturl())
            event.update(final_url=response.geturl(), http_status=response.status)
            require(response.status == 200, 'SNAPSHOT_HTTP_STATUS')
            data = response.read(limit + 1)
            require(0 < len(data) <= limit, 'SNAPSHOT_DOWNLOAD_LIMIT')
            event['headers'] = {k: response.headers.get(k) for k in
                                ('Date', 'ETag', 'Last-Modified', 'Content-Length')}
        _write(target, data)
        event.update(completed_utc=utc(), size=len(data), sha256=sha(data))
        return data
    except (OSError, URLError, HTTPError, ValueError) as exc:
        event.update(completed_utc=utc(), error_type=type(exc).__name__, error=str(exc))
        raise ProbeError('SNAPSHOT_RETRIEVAL_FAILED:' + type(exc).__name__ + ':' + str(exc)) from exc


def run_probe(output: Path, keyring_path: Path, gpgv: Path, dpkg_deb: Path,
              saved_inrelease: Path | None = None) -> int:
    require(output.is_absolute(), 'OUTPUT_MUST_BE_ABSOLUTE')
    repo = Path(__file__).resolve().parents[2]
    output = output.resolve()
    require(not output.is_relative_to(repo), 'OUTPUT_MUST_BE_OUTSIDE_REPOSITORY')
    output.mkdir(mode=0o700, parents=False, exist_ok=False)
    events: list[dict] = []
    state = {'schema': 'rei-h1b1-real-gcc-probe/v1', 'status': 'RUNNING',
             'started_utc': utc(), 'authority_effect': 'NONE',
             'full_census_complete': False, 'installed_files_verified': False,
             'h1a_workstation_readmission': 'NOT_PERFORMED',
             'historical_retrieval_time_proved': False,
             'key_lifecycle_admitted': False, 'native_runtime': 'NOT_RUN',
             'package_install_or_execution': 'NOT_RUN'}
    stage = 'KEYRING'
    try:
        ring_path = keyring_path.resolve(strict=True)
        require(ring_path.is_file() and 0 < ring_path.stat().st_size <= 8 * 1024 * 1024,
                'KEYRING_INPUT_LIMIT')
        ring = ring_path.read_bytes()
        policy = chain.ArchivePolicy(keyring_sha256=sha(ring),
                                     allowed_primary_fingerprints=(SIGNER,), suite='noble-updates',
                                     codename='noble', architecture='amd64',
                                     index_name='main/binary-amd64/Packages.xz', required=(IDENTITY,))
        _write(output / 'public-keyring.gpg', ring)
        _json(output / 'POLICY.json', asdict(policy))
        _json(output / 'SOURCE_INPUTS.json', {
            'donor_git_blob': DONOR_BLOB,
            'donor_sha256': sha(Path(__file__).with_name('signed_archive_chain.py').read_bytes()),
            'probe_sha256': sha(Path(__file__).read_bytes()),
            'keyring_source_path': str(ring_path), 'keyring_sha256': sha(ring),
            'keyring_admission': 'DECLARED_PUBLIC_RING_POLICY_ONLY_NOT_ORGANIZATIONAL_ADMISSION',
            'signer_reference': 'https://wiki.ubuntu.com/SecurityTeam/FAQ',
            'run_id': os.environ.get('GITHUB_RUN_ID'), 'executed_git_sha': os.environ.get('REI_EXECUTED_HEAD')})
        stage = 'AUTHENTICATE_RELEASE'
        release_url = BASE + 'dists/noble-updates/InRelease'
        if saved_inrelease is None:
            inrelease = _download(release_url, policy.max_inrelease_bytes, output / 'InRelease', events)
        else:
            saved = saved_inrelease.resolve(strict=True)
            require(saved.is_file() and 0 < saved.stat().st_size <= policy.max_inrelease_bytes,
                    'SAVED_INRELEASE_INPUT_LIMIT')
            inrelease = saved.read_bytes()
            require(sha(inrelease) == SAVED_INRELEASE_SHA, 'SAVED_INRELEASE_PIN_MISMATCH')
            _write(output / 'InRelease', inrelease)
            events.append({'kind': 'PINNED_SAVED_INRELEASE_REUSED', 'sha256': sha(inrelease),
                           'original_run': 33954698424, 'original_artifact': 9965968444,
                           'new_snapshot_request': False})
        release_bytes, signature = chain._authenticated_release(inrelease, ring, policy, gpgv)
        _write(output / 'authenticated-Release', release_bytes)
        _json(output / 'SIGNATURE.json', signature)
        release_rows = chain._deb822(release_bytes)
        require(len(release_rows) == 1, 'RELEASE_STANZA_COUNT')
        release = release_rows[0]
        require(release.get('origin') == 'Ubuntu' and release.get('label') == 'Ubuntu'
                and release.get('suite') == policy.suite and release.get('codename') == 'noble',
                'RELEASE_IDENTITY_MISMATCH')
        entries = chain._release_entries(release)
        require(policy.index_name in entries, 'RELEASE_INDEX_UNLISTED')
        _json(output / 'RELEASE_ENTRIES.json', {'total': len(entries),
              'literal_at_sign_names': [key for key in entries if '@' in key],
              'index': policy.index_name, 'expected_index_sha256': entries[policy.index_name][0],
              'rows_filtered_or_normalized': False})
        stage = 'AUTHENTICATE_INDEX'
        index = _download(BASE + 'dists/noble-updates/' + policy.index_name,
                          policy.max_compressed_index_bytes, output / 'Packages.xz', events)
        require(entries[policy.index_name] == (sha(index), len(index)), 'INDEX_HASH_OR_SIZE')
        plain = chain._unpack_index(index, policy.max_index_bytes)
        providers = [r for r in chain._deb822(plain) if
                     tuple(r.get(k) for k in ('package', 'version', 'architecture')) == IDENTITY]
        require(len(providers) == 1, 'EXACT_GCC_PROVIDER_CARDINALITY')
        record = providers[0]
        filename = chain._archive_path(record['filename'])
        require(filename.startswith('pool/') and filename.endswith('.deb'), 'DEB_ARCHIVE_PATH')
        require(record.get('sha256') == DEB_SHA and chain._size(record['size']) <= MAX_DEB,
                'EXPECTED_GCC_METADATA_MISMATCH')
        _json(output / 'SELECTED_PROVIDER.json', record)
        stage = 'AUTHENTICATE_PAYLOAD'
        payload = _download(BASE + filename, MAX_DEB, output / 'gcc-provider.deb', events)
        report = chain.verify_chain(inrelease=inrelease, index_bytes=index,
                                    debs={filename: payload}, keyring=ring, policy=policy, gpgv=gpgv)
        _json(output / 'SIGNED_CHAIN.json', report)
        stage = 'VERIFY_CONTROL_AND_MEMBER'
        member = inspect_member(payload, expected_deb_sha256=DEB_SHA, expected_identity=IDENTITY,
                                member_path=MEMBER, expected_member_sha256=MEMBER_SHA,
                                dpkg_deb=dpkg_deb)
        _json(output / 'DEB_MEMBER.json', member)
        state.update(status='PASS_H1B1_REAL_GCC_SIGNED_MEMBER_PROBE',
                     verified_packages=1, expected_deb_sha256=DEB_SHA,
                     member_path=MEMBER, member_sha256=member['member_sha256'],
                     signing_fingerprints=report['signing_primary_fingerprints'],
                     scope='ONE_REAL_PROVIDER_AND_REGULAR_ARCHIVE_MEMBER_ONLY')
        exit_code = 0
    except Exception as exc:
        state.update(status='STOP_H1B1_REAL_GCC_PROBE', first_blocker=type(exc).__name__ + ':' + str(exc),
                     first_blocker_stage=stage)
        exit_code = 65
    state.update(completed_utc=utc(), exit_code=exit_code)
    _json(output / 'RETRIEVAL.json', {'events': events,
          'provenance_kind': 'CLIENT_OBSERVATIONS_AND_PINNED_PRIOR_INPUT_NOT_SERVER_ATTESTATION'})
    _json(output / 'PROBE_RESULT.json', state)
    manifest = ''.join(sha(p.read_bytes()) + '  ' + p.name + '\n'
                       for p in sorted(output.iterdir()) if p.is_file())
    _write(output / 'SHA256SUMS', manifest.encode())
    print(json.dumps(state, sort_keys=True))
    return exit_code


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--keyring', type=Path, default=Path('/usr/share/keyrings/ubuntu-archive-keyring.gpg'))
    parser.add_argument('--gpgv', type=Path, default=Path('/usr/bin/gpgv'))
    parser.add_argument('--dpkg-deb', type=Path, default=Path('/usr/bin/dpkg-deb'))
    parser.add_argument('--saved-inrelease', type=Path)
    arguments = parser.parse_args()
    raise SystemExit(run_probe(arguments.output, arguments.keyring, arguments.gpgv,
                               arguments.dpkg_deb, arguments.saved_inrelease))
