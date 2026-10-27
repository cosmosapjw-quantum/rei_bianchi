"""Prepared only: cached-source ZIP worker. Approval and execution are NOT_RUN.

Run through measure_final_once_20261028.py after separate explicit approval.
Flags are accident-prevention guards; supplying them does not confer approval.
No scientific imports, restoration, payload execution, or recursive discovery.
"""
import argparse
import hashlib
import json
import resource
import signal
import sys
import time
import zipfile
from pathlib import Path, PurePosixPath

CACHE = Path('/workspace/scratch/52cc495a5f0a/rei_bass_storage_unit')
MANIFEST = CACHE / 'delivery/PENDING_SOURCE_ZIP_INPUT.json'
MANIFEST_BYTES = 4699240
MANIFEST_SHA256 = 'd77ea863ad2730f6ef0be27a3f3a93c8b5c864f3d863b4b1b5950fd61a6ef63e'
MANIFEST_BLOB = '713ac1d7c89b53028f6d63b3051c774f5a621546'
SOURCE_PIN = 'd9a1c4c4252f1b7b4c868fb2cb817a879f503cd5'
PRIOR_LOWER = 48.263016494
WORK_STOP = 5.5
FINAL_DEADLINE = 6.0


class BudgetStop(Exception):
    pass


def usage():
    r = resource.getrusage(resource.RUSAGE_SELF)
    return {'user': r.ru_utime, 'system': r.ru_stime,
            'total': r.ru_utime + r.ru_stime}


def stop(signum, frame):
    raise BudgetStop('fixed worker CPU deadline reached')


def check():
    if usage()['total'] >= WORK_STOP:
        raise BudgetStop('worker work allowance exhausted; receipt allowance retained')


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def archive_name(value):
    if type(value) is not str:
        raise ValueError('archive_path must be a string')
    p = PurePosixPath(value)
    if (not value or p.is_absolute() or '..' in p.parts or str(p) != value
            or value in ('.', 'SOURCE_MANIFEST.json') or '\x00' in value
            or '\\' in value or p.suffix.lower() == '.zip'):
        raise ValueError('noncanonical, reserved, or nested ZIP archive path')
    return value


def entry(archive, name, data):
    info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data)


def arguments(argv):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--explicit-approved-launch', action='store_true', required=True)
    p.add_argument('--approved-absolute-cap', type=float, required=True)
    p.add_argument('--approved-reservation', type=float, required=True)
    p.add_argument('--output-root', type=Path, required=True)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('archive', type=Path)
    p.add_argument('result', type=Path)
    a = p.parse_args(argv)
    if (a.approved_absolute_cap != 60 or a.approved_reservation != 8
            or PRIOR_LOWER + a.approved_reservation > a.approved_absolute_cap):
        p.error('only separately approved absolute cap 60 / reservation 8 accepted')
    return a


def output_path(value, root):
    if not value.is_absolute() or value.resolve().parent != root:
        raise ValueError('output must be an absolute direct child of explicit output root')
    if value.exists() or value.is_symlink():
        raise ValueError('existing output refused: ' + str(value))
    return value


def main(argv=None):
    started_wall = time.monotonic()
    snapshots = []
    result_path = None
    result = {'status': 'FAIL', 'claim_admission': 'NOT_RUN',
              'historical_cpu_lower_bound': PRIOR_LOWER,
              'historical_unmeasured_cpu': 'UNKNOWN_NOT_ZERO',
              'proposed_absolute_cap': 60, 'reservation_argument': 8,
              'worker_work_stop_cpu': WORK_STOP,
              'worker_fixed_report_deadline_cpu': FINAL_DEADLINE,
              'worker_cpu_hard_limit_seconds': 6,
              'approval_flag_is_authorization': False,
              'crc_invocations': 0, 'crc_passes': 0,
              'archive_sha256_passes': 0, 'phase_snapshots': snapshots}

    def snapshot(phase):
        absolute = usage()
        prior = snapshots[-1]['absolute'] if snapshots else dict.fromkeys(absolute, 0.0)
        snapshots.append({'phase': phase, 'absolute': absolute,
                          'delta': {k: absolute[k] - prior[k] for k in absolute},
                          'wall_since_main': time.monotonic() - started_wall})

    # Absolute RUSAGE_SELF includes interpreter startup before this function.
    # Interrupt work at 5.5; the sole phase transition below can arm only the
    # remainder to the already fixed 6.0 receipt deadline, never a fresh budget.
    signal.signal(signal.SIGPROF, stop)
    remaining = WORK_STOP - usage()['total']
    if remaining > 0:
        signal.setitimer(signal.ITIMER_PROF, remaining)
    try:
        snapshot('startup')
        a = arguments(sys.argv[1:] if argv is None else argv)
        root = a.output_root.resolve()
        if (not a.output_root.is_absolute() or not root.is_dir()
                or root.is_relative_to(CACHE.resolve())):
            raise ValueError('existing writable output root outside cached source required')
        # Retain a valid result destination even when the first work check fails.
        result_path = output_path(a.result, root)
        output = output_path(a.archive, root)
        if output.resolve() == result_path.resolve() or output.suffix.lower() != '.zip':
            raise ValueError('distinct ZIP and result paths required')
        if not a.manifest.is_absolute() or a.manifest.resolve() != MANIFEST.resolve():
            raise ValueError('only the frozen cached input manifest is accepted')
        resource.setrlimit(resource.RLIMIT_CPU, (6, 6))
        check()
        if remaining <= 0:
            raise BudgetStop('worker entered after fixed CPU deadline')
        if MANIFEST.stat().st_size != MANIFEST_BYTES:
            raise ValueError('input manifest byte count mismatch')
        raw = MANIFEST.read_bytes()
        if (len(raw) != MANIFEST_BYTES or hashlib.sha256(raw).hexdigest() != MANIFEST_SHA256
                or git_blob(raw) != MANIFEST_BLOB):
            raise ValueError('input manifest byte identity mismatch')
        manifest = json.loads(raw)
        if (type(manifest) is not dict or manifest.get('source_pin') != SOURCE_PIN
                or type(manifest.get('files')) is not list or len(manifest['files']) != 116):
            raise ValueError('frozen source_pin / 116 payload count mismatch')
        snapshot('manifest_validation')
        payload, metadata, seen, sources = [], [], set(), set()
        for item in manifest['files']:
            check()
            name = archive_name(item['archive_path'])
            if name in seen:
                raise ValueError('duplicate archive path')
            seen.add(name)
            source_value = item['source']
            if type(source_value) is not str:
                raise ValueError('source path must be a string')
            source = Path(source_value)
            resolved = source.resolve()
            if (not source.is_absolute() or not resolved.is_relative_to(CACHE.resolve())
                    or resolved == MANIFEST.resolve() or resolved in sources
                    or source.suffix.lower() == '.zip' or resolved.suffix.lower() == '.zip'):
                raise ValueError('source outside cache, duplicate, manifest, or ZIP refused')
            sources.add(resolved)
            expected = item['expected_text']
            if type(expected) is not str:
                raise ValueError('expected_text must be a string')
            data = source.read_bytes()
            if data != expected.encode('utf-8'):
                raise ValueError('source exact UTF8 bytes mismatch: ' + name)
            blob = git_blob(data)
            if 'git_blob' in item and item['git_blob'] != blob:
                raise ValueError('source Git blob mismatch: ' + name)
            payload.append((name, data))
            metadata.append({'path': name, 'bytes': len(data),
                             'sha256': hashlib.sha256(data).hexdigest(), 'git_blob': blob})
        condensed = {'source_pin': SOURCE_PIN,
                     'files': sorted(metadata, key=lambda item: item['path'])}
        condensed_bytes = (json.dumps(condensed, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        snapshot('source_validation')
        check()
        with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_STORED, allowZip64=False) as archive:
            for name, data in sorted(payload):
                check()
                entry(archive, name, data)
            check()
            entry(archive, 'SOURCE_MANIFEST.json', condensed_bytes)
        snapshot('zip_write')
        check()
        with zipfile.ZipFile(output, 'r') as archive:
            if len(archive.infolist()) != 117:
                raise ValueError('ZIP entry count mismatch')
            result['crc_invocations'] = 1
            bad = archive.testzip()
        if bad is not None:
            raise ValueError('archive CRC failure: ' + bad)
        result['crc_passes'] = 1
        snapshot('crc')
        check()
        archive_bytes = output.read_bytes()
        digest = hashlib.sha256(archive_bytes).hexdigest()
        result['archive_sha256_passes'] = 1
        snapshot('archive_sha256')
        check()
        result.update({'status': 'PASS', 'archive': str(output), 'bytes': len(archive_bytes),
                       'sha256': digest, 'source_pin': SOURCE_PIN,
                       'input_manifest': str(MANIFEST),
                       'input_manifest_sha256': MANIFEST_SHA256,
                       'source_manifest': 'SOURCE_MANIFEST.json (inside archive)',
                       'payload_files': 116, 'zip_entries': 117})
    except SystemExit as error:
        result['error'] = 'argument refusal: ' + str(error)
    except BaseException as error:
        result.update({'status': 'BUDGET_STOP' if isinstance(error, BudgetStop) else 'FAIL',
                       'error': type(error).__name__ + ': ' + str(error),
                       'partial_archive_possible': True})
    try:
        receipt_remaining = FINAL_DEADLINE - usage()['total']
        if receipt_remaining <= 0:
            raise BudgetStop('fixed worker receipt deadline already exhausted')
        signal.setitimer(signal.ITIMER_PROF, receipt_remaining)
        snapshot('receipt')
        result['process_cpu_before_final_serialization'] = usage()['total']
        result['worker_exit_tail'] = 'Measured only by supervisor wait4 after exit'
        serialized = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        if result_path is not None:
            with result_path.open('x', encoding='utf-8') as stream:
                stream.write(serialized)
        sys.stdout.write(serialized)
        sys.stdout.flush()
    except BaseException as error:
        # No deadline expansion or archive cleanup/retry. Hard limit remains.
        try:
            sys.stderr.write('FAIL receipt: ' + type(error).__name__ + ': ' + str(error) + '\n')
        except BaseException:
            pass
        return 1
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
