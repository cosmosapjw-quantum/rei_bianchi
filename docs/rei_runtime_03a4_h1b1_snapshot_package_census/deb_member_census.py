#!/usr/bin/env python3
"""Authenticated DEB/member consumer; no installation or installed-file claim.

Reuse the pinned sibling donor before parsing the same immutable DEB bytes.
dpkg-deb emits uncompressed tar streams; tarfile reads selected regular files
in memory and never extracts paths to the host. Tool paths refer to host tools,
not archive members. No maintainer script or packaged program is executed.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import tarfile
import tempfile
import time
from typing import Mapping

HERE = Path(__file__).resolve().parent
DONOR_NAME = 'rei_h1b1_deb_member_donor'
if DONOR_NAME not in sys.modules:
    _spec = importlib.util.spec_from_file_location(DONOR_NAME, HERE / 'signed_archive_chain.py')
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[DONOR_NAME] = _module
    _spec.loader.exec_module(_module)
DONOR = sys.modules[DONOR_NAME]
ArchivePolicy = DONOR.ArchivePolicy


class MemberError(ValueError):
    """Typed incomplete-result rejection; bounded command evidence is retained."""

    def __init__(self, code: str, evidence: dict | None = None):
        super().__init__(code)
        self.code = code
        self.evidence = evidence if evidence is not None else {}


def _require(condition, code):
    if not condition:
        raise MemberError(code)


def _sha(data):
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class MemberLimits:
    max_total_deb_bytes: int = 512 * 1024 * 1024
    max_debs: int = 32
    max_requests: int = 256
    max_control_tar_bytes: int = 4 * 1024 * 1024
    max_tar_bytes: int = 256 * 1024 * 1024
    max_total_tar_bytes: int = 512 * 1024 * 1024
    max_member_bytes: int = 128 * 1024 * 1024
    max_members: int = 100000
    max_stderr_bytes: int = 65536
    tool_timeout_seconds: float = 30
    total_timeout_seconds: float = 120

    def __post_init__(self):
        for name, value in asdict(self).items():
            if name.endswith('_seconds'):
                _require(type(value) in (int, float) and 0 < value <= 3600, 'LIMIT_INVALID:' + name)
            else:
                _require(type(value) is int and 0 < value <= 1024 * 1024 * 1024, 'LIMIT_INVALID:' + name)


def _run_tool(argv, *, max_stdout, max_stderr, timeout, runs):
    """Bound both pipes while draining them, and reap only this owned group."""
    start = time.monotonic()
    buffers = {'stdout': bytearray(), 'stderr': bytearray()}
    caps = {'stdout': max_stdout, 'stderr': max_stderr}
    code = None
    process = None
    try:
        process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True,
                                   env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C',
                                        'DPKG_DEB_THREADS_MAX': '1'})
        with selectors.DefaultSelector() as selector:
            for name in buffers:
                pipe = getattr(process, name)
                os.set_blocking(pipe.fileno(), False)
                selector.register(pipe, selectors.EVENT_READ, name)
            while selector.get_map():
                remaining = timeout - (time.monotonic() - start)
                if remaining <= 0:
                    code = 'TOOL_TIMEOUT'
                    break
                for key, _ in selector.select(min(remaining, 0.1)):
                    name = key.data
                    data = os.read(key.fd, min(65536, caps[name] - len(buffers[name]) + 1))
                    if not data:
                        selector.unregister(key.fileobj)
                        continue
                    available = caps[name] - len(buffers[name])
                    buffers[name].extend(data[:available])
                    if len(data) > available:
                        code = 'TOOL_' + name.upper() + '_LIMIT'
                        break
                if code:
                    break
        if not code:
            try:
                process.wait(timeout=max(0.001, timeout - (time.monotonic() - start)))
            except subprocess.TimeoutExpired:
                code = 'TOOL_TIMEOUT'
    except OSError as error:
        code = 'TOOL_RUNTIME_UNAVAILABLE'
        buffers['stderr'] = bytearray(str(error).encode()[:max_stderr])
    finally:
        if process is not None:
            if code or process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            process.wait()
            process.stdout.close()
            process.stderr.close()
        record = {'argv': list(map(str, argv)), 'exit_code': None if process is None else process.returncode,
                  'timed_out': code == 'TOOL_TIMEOUT', 'timeout_seconds': timeout,
                  'elapsed_seconds': round(time.monotonic() - start, 6),
                  'stdout_bytes': len(buffers['stdout']), 'stderr_bytes': len(buffers['stderr']),
                  'stdout_sha256': _sha(buffers['stdout']), 'stderr_sha256': _sha(buffers['stderr']),
                  'stderr': buffers['stderr'].decode('utf-8', errors='replace'),
                  'output_limits': caps, 'output_truncated': code in ('TOOL_STDOUT_LIMIT', 'TOOL_STDERR_LIMIT'),
                  'failure': code}
        runs.append(record)
    if code:
        raise MemberError(code, {'tool_runs': list(runs)})
    if process.returncode != 0:
        raise MemberError('DEB_TOOL_FAILED', {'tool_runs': list(runs)})
    return bytes(buffers['stdout'])


def _member_path(name, *, directory=False):
    _require(type(name) is str and bool(name), 'UNSAFE_MEMBER_PATH')
    _require(not name.startswith('/') and '\\' not in name
             and not any(ord(c) < 32 or ord(c) == 127 for c in name), 'UNSAFE_MEMBER_PATH')
    while name.startswith('./'):
        name = name[2:]
    if directory and name in ('', '.'):
        return '.'
    if directory and name.endswith('/'):
        name = name[:-1]
    _require(bool(name) and all(part not in ('', '.', '..') for part in name.split('/')),
             'UNSAFE_MEMBER_PATH')
    return name


def _remaining(deadline, limits):
    value = deadline - time.monotonic()
    _require(value > 0, 'CENSUS_TIMEOUT')
    return min(limits.tool_timeout_seconds, value)


def _read_tar(data, wanted, *, limits, deadline, keep_bytes=False):
    """Read the complete logical member sequence so later duplicates cannot hide."""
    found = {}
    count = 0
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:') as archive:
            for member in archive:
                _remaining(deadline, limits)
                count += 1
                _require(count <= limits.max_members, 'MEMBER_COUNT_LIMIT')
                name = _member_path(member.name, directory=member.isdir())
                _require(0 <= member.size <= limits.max_member_bytes, 'MEMBER_SIZE_LIMIT')
                if name not in wanted:
                    continue
                _require(name not in found, 'DUPLICATE_MEMBER:' + name)
                _require(member.type in (tarfile.REGTYPE, tarfile.AREGTYPE) and member.sparse is None,
                         'MEMBER_NOT_REGULAR:' + name)
                source = archive.extractfile(member)
                _require(source is not None, 'MEMBER_DATA_MISSING:' + name)
                digest = hashlib.sha256()
                size = 0
                content = bytearray()
                with source:
                    while True:
                        _remaining(deadline, limits)
                        chunk = source.read(65536)
                        if not chunk:
                            break
                        size += len(chunk)
                        _require(size <= limits.max_member_bytes and size <= member.size,
                                 'MEMBER_SIZE_LIMIT')
                        digest.update(chunk)
                        if keep_bytes:
                            content.extend(chunk)
                _require(size == member.size, 'MEMBER_SIZE_MISMATCH:' + name)
                found[name] = {'member_path': name, 'sha256': digest.hexdigest(), 'size': size}
                if keep_bytes:
                    found[name]['bytes'] = bytes(content)
    except (tarfile.TarError, EOFError, OSError, ValueError) as error:
        if isinstance(error, MemberError):
            raise
        raise MemberError('DEB_TAR_INVALID:' + str(error)) from error
    _require(set(found) == set(wanted), 'MEMBER_MISSING:' + ','.join(sorted(set(wanted) - set(found))))
    return found, count


def _tool_identity(path):
    try:
        executable = Path(path).resolve(strict=True)
        _require(executable.is_file() and os.access(executable, os.X_OK), 'TOOL_RUNTIME_UNAVAILABLE')
        return {'path': str(executable), 'sha256': _sha(executable.read_bytes())}
    except (OSError, TypeError) as error:
        raise MemberError('TOOL_RUNTIME_UNAVAILABLE') from error


def _read_deb(payload, record, requests, *, tool, limits, runs, deadline, total):
    """Private format/member readback; it does not authenticate an archive."""
    with tempfile.TemporaryDirectory(prefix='rei-deb-member-read-') as temporary:
        path = Path(temporary) / 'input.deb'
        path.write_bytes(payload)
        control_tar = _run_tool([tool, '--ctrl-tarfile', str(path)],
                                max_stdout=min(limits.max_control_tar_bytes, limits.max_tar_bytes,
                                               limits.max_total_tar_bytes - total[0]),
                                max_stderr=limits.max_stderr_bytes,
                                timeout=_remaining(deadline, limits), runs=runs)
        total[0] += len(control_tar)
        control_rows, control_count = _read_tar(control_tar, {'control'}, limits=limits,
                                                deadline=deadline, keep_bytes=True)
        try:
            fields = DONOR._deb822(control_rows['control']['bytes'])
        except DONOR.ChainError as error:
            raise MemberError('CONTROL_FIELDS_INVALID:' + str(error)) from error
        _require(len(fields) == 1, 'CONTROL_RECORD_COUNT')
        identity = {key: fields[0].get(key) for key in ('package', 'version', 'architecture')}
        _require(identity == {key: record[key] for key in identity}, 'CONTROL_IDENTITY_MISMATCH')
        data_tar = _run_tool([tool, '--fsys-tarfile', str(path)],
                            max_stdout=min(limits.max_tar_bytes, limits.max_total_tar_bytes - total[0]),
                            max_stderr=limits.max_stderr_bytes,
                            timeout=_remaining(deadline, limits), runs=runs)
        total[0] += len(data_tar)
        members, data_count = _read_tar(data_tar, requests, limits=limits, deadline=deadline)
        for name, expected in requests.items():
            _require(members[name]['sha256'] == expected, 'MEMBER_HASH_MISMATCH:' + name)
        return {'control_identity': identity, 'control_sha256': control_rows['control']['sha256'],
                'control_size': control_rows['control']['size'], 'members': members,
                'control_member_count': control_count, 'data_member_count': data_count}


def verify_member_census(*, inrelease: bytes, index_bytes: bytes, debs: Mapping[str, bytes],
                         keyring: bytes, policy: ArchivePolicy, gpgv: Path, required_members,
                         dpkg_deb: Path = Path('/usr/bin/dpkg-deb'),
                         limits: MemberLimits | None = None) -> dict:
    """Verify exact archive/member bytes relative to the donor's caller policy.

    required_members is a finite list/tuple of (authenticated archive filename,
    normalized regular member path, lowercase SHA-256). No receipt/PASS input is
    accepted. Limits bound added archive processing; the unchanged donor retains
    its existing metadata/decompression/time limits and subprocess implementation.
    """
    start = time.monotonic()
    limits = MemberLimits() if limits is None else limits
    _require(type(limits) is MemberLimits, 'LIMIT_TYPE')
    limits.__post_init__()
    deadline = start + limits.total_timeout_seconds
    supplied = dict(debs)  # One immutable-byte snapshot used by both stages.
    _require(len(supplied) <= limits.max_debs and all(type(v) is bytes for v in supplied.values()),
             'DEB_INPUT_LIMIT')
    _require(sum(map(len, supplied.values())) <= limits.max_total_deb_bytes, 'DEB_INPUT_LIMIT')
    signed = DONOR.verify_chain(inrelease=inrelease, index_bytes=index_bytes, debs=supplied,
                               keyring=keyring, policy=policy, gpgv=gpgv)
    _remaining(deadline, limits)
    # These are readback caps; the donor itself performs buffered capture.
    signature = signed['signature_verification']
    _require(len(signature['status_text'].encode()) <= limits.max_stderr_bytes
             and len(signature['stderr'].encode()) <= limits.max_stderr_bytes, 'SIGNATURE_OUTPUT_LIMIT')
    _require(type(required_members) in (tuple, list) and 0 < len(required_members) <= limits.max_requests,
             'REQUIRED_MEMBER_REQUEST')
    grouped = {}
    ordered = []
    for item in required_members:
        _require(type(item) in (tuple, list) and len(item) == 3
                 and all(type(value) is str for value in item), 'REQUIRED_MEMBER_REQUEST')
        filename, name, digest = item
        try:
            normalized = _member_path(name)
        except MemberError as error:
            raise MemberError('REQUIRED_MEMBER_PATH') from error
        _require(normalized == name and filename in supplied, 'REQUIRED_MEMBER_PATH_OR_ARCHIVE')
        _require(bool(DONOR.SHA256_RE.fullmatch(digest)), 'REQUIRED_MEMBER_SHA256')
        _require(name not in grouped.setdefault(filename, {}), 'REQUIRED_MEMBER_DUPLICATE')
        grouped[filename][name] = digest
        ordered.append((filename, name, digest))
    runs = []
    try:
        tool = _tool_identity(dpkg_deb)
        tool['version'] = _run_tool([tool['path'], '--version'], max_stdout=65536,
                                    max_stderr=limits.max_stderr_bytes,
                                    timeout=_remaining(deadline, limits), runs=runs).decode().splitlines()[0]
        gpg_tool = _tool_identity(signature['executable'])
        _require(gpg_tool['sha256'] == signature['executable_sha256'], 'TOOL_IDENTITY_CHANGED')
        gpg_tool['version'] = _run_tool([gpg_tool['path'], '--version'], max_stdout=65536,
                                       max_stderr=limits.max_stderr_bytes,
                                       timeout=_remaining(deadline, limits), runs=runs).decode().splitlines()[0]
        packages = {}
        total = [0]
        # Validate each authenticated DEB's structure/control, even if no member is requested from it.
        for record in signed['verified_packages']:
            filename = record['filename']
            packages[filename] = _read_deb(supplied[filename], record, grouped.get(filename, {}),
                                           tool=tool['path'], limits=limits, runs=runs,
                                           deadline=deadline, total=total)
        verified = []
        for filename, name, expected in ordered:
            row = packages[filename]['members'][name]
            verified.append(dict(row, archive_filename=filename, archive_sha256=_sha(supplied[filename]),
                                 expected_sha256=expected,
                                 control_identity=packages[filename]['control_identity']))
        _require(_tool_identity(tool['path']) == {k: tool[k] for k in ('path', 'sha256')},
                 'TOOL_IDENTITY_CHANGED')
        _remaining(deadline, limits)
        identity_paths = {'consumer': Path(__file__).resolve(), 'donor': Path(DONOR.__file__).resolve(),
                          'python': Path(sys.executable).resolve()}
        source_identity = {name: {'path': str(path), 'sha256': _sha(path.read_bytes())}
                           for name, path in identity_paths.items()}
        return {'schema': 'rei-h1b1-authenticated-deb-members/v1',
                'status': 'PASS_H1B1_AUTHENTICATED_DEB_MEMBERS', 'signed_chain': signed,
                'verified_members': verified, 'authority_effect': 'NONE',
                'installed_files_verified': False, 'full_census_complete': False,
                'tools': {'dpkg_deb': tool, 'gpgv': gpg_tool}, 'tool_runs': runs,
                'gpgv_signature_timed_out': False, 'gpgv_signature_timeout_seconds': policy.gpgv_timeout_seconds,
                'signature_output_limit_scope': 'POST_RETURN_READBACK; inherited donor uses buffered subprocess.run',
                'source_identity': source_identity, 'limits': asdict(limits),
                'total_uncompressed_tar_bytes': total[0],
                'package_readback': {name: {k: v for k, v in data.items() if k != 'members'}
                                     for name, data in packages.items()},
                'required_members_sha256': _sha(json.dumps(ordered, separators=(',', ':')).encode()),
                'verified_members_sha256': _sha(json.dumps(verified, sort_keys=True, separators=(',', ':')).encode()),
                'elapsed_seconds': round(time.monotonic() - start, 6),
                'claim_scope': 'CALLER_POLICY_AUTHENTICATED_ARCHIVE_MEMBERS_NOT_INSTALLED_FILES_OR_HOST'}
    except MemberError as error:
        error.evidence.setdefault('tool_runs', runs)
        error.evidence.setdefault('signed_chain', signed)
        raise
