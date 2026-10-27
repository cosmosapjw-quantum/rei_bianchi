"""Persistent manifest-only checkpoint packaging; payload is never imported."""
import resource
import signal
import sys


def cpu():
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_utime + usage.ru_stime


class BudgetStop(Exception):
    pass


def stop(signum, frame):
    raise BudgetStop('cumulative presentation process CPU exhausted')


signal.signal(signal.SIGPROF, stop)
signal.setitimer(signal.ITIMER_PROF, max(0.000001, 0.50 - cpu()))

import hashlib
import json
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path('/workspace/scratch/52cc495a5f0a/rei_bass_storage_unit')
FAILED = False


def check():
    if FAILED or cpu() >= 0.48:
        raise BudgetStop('refusing phase near cumulative process CPU limit')


def owned(value):
    if type(value) is not str:
        raise ValueError('absolute path string required')
    path = Path(value)
    if not path.is_absolute() or not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('path must remain inside new owned unit')
    return path


def archive_name(value):
    if type(value) is not str:
        raise ValueError('archive_path string required')
    path = PurePosixPath(value)
    if (path.is_absolute() or '..' in path.parts or str(path) != value
            or value in ('.', 'SOURCE_MANIFEST.json') or '\\' in value):
        raise ValueError('unsafe or reserved archive path')
    return value


def emit(value):
    value['cumulative_process_cpu_before_emission'] = cpu()
    sys.stdout.write(json.dumps(value, ensure_ascii=False) + '\n')
    sys.stdout.flush()


def entry(archive, name, data):
    info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data)


def package(command):
    manifest_path = owned(command['manifest'])
    output = owned(command['output_zip'])
    result_path = owned(command['result_json'])
    if len({p.resolve() for p in (manifest_path, output, result_path)}) != 3:
        raise ValueError('manifest, ZIP, and result must be distinct')
    if output.suffix != '.zip' or output.exists() or result_path.exists():
        raise ValueError('new exclusive ZIP and result required')
    record = {'status': 'FAIL', 'crc_passes': 0, 'archive_sha256_passes': 0,
              'execution': 'Presentation only; no payload imports/tests.',
              'unmeasured_cost': 'UNKNOWN_NOT_ZERO'}
    try:
        check()
        manifest = json.loads(manifest_path.read_bytes())
        if type(manifest) is not dict or type(manifest.get('source_pin')) is not str or not manifest['source_pin']:
            raise ValueError('explicit source_pin required')
        if type(manifest.get('files')) is not list or not manifest['files']:
            raise ValueError('nonempty explicit files list required')
        payload, metadata, seen = [], [], set()
        excluded = {manifest_path.resolve(), output.resolve(), result_path.resolve()}
        for item in manifest['files']:
            check()
            name = archive_name(item['archive_path'])
            if name in seen:
                raise ValueError('duplicate archive path')
            seen.add(name)
            source = owned(item['source'])
            if source.resolve() in excluded or source.suffix.lower() == '.zip':
                raise ValueError('self-reference or existing archive source refused')
            expected = item['expected_text']
            if type(expected) is not str:
                raise ValueError('expected_text string required')
            data = source.read_bytes()
            if data != expected.encode('utf-8'):
                raise ValueError('exact source byte mismatch: ' + name)
            blob = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
            if 'git_blob' in item and item['git_blob'] != blob:
                raise ValueError('source Git blob mismatch: ' + name)
            payload.append((name, data))
            metadata.append({'path': name, 'bytes': len(data),
                             'sha256': hashlib.sha256(data).hexdigest(), 'git_blob': blob})
        condensed = {'source_pin': manifest['source_pin'],
                     'files': sorted(metadata, key=lambda item: item['path'])}
        manifest_bytes = (json.dumps(condensed, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        check()
        with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_STORED, allowZip64=False) as archive:
            for name, data in sorted(payload):
                check()
                entry(archive, name, data)
            entry(archive, 'SOURCE_MANIFEST.json', manifest_bytes)
        check()
        with zipfile.ZipFile(output, 'r') as archive:
            bad = archive.testzip()
        record['crc_passes'] = 1
        if bad is not None:
            raise ValueError('CRC failure: ' + bad)
        check()
        data = output.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        record['archive_sha256_passes'] = 1
        check()
        record.update({'status': 'PASS', 'archive': str(output), 'bytes': len(data),
                       'sha256': digest, 'source_pin': manifest['source_pin'],
                       'payload_files': len(payload), 'zip_entries': len(payload) + 1,
                       'source_manifest_sha256': hashlib.sha256(manifest_bytes).hexdigest()})
    except BaseException as error:
        signal.setitimer(signal.ITIMER_PROF, max(0.000001, 0.60 - cpu()))
        record.update({'status': 'BUDGET_STOP' if isinstance(error, BudgetStop) else 'FAIL',
                       'error': type(error).__name__ + ': ' + str(error),
                       'partial_archive_possible': True})
    record['cumulative_process_cpu_before_result'] = cpu()
    with result_path.open('x', encoding='utf-8') as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    return record


def main():
    global FAILED
    if sys.stdin.isatty():
        import termios
        settings = termios.tcgetattr(sys.stdin.fileno())
        settings[3] &= ~(termios.ECHO | termios.ICANON)
        settings[6][termios.VMIN] = 255
        settings[6][termios.VTIME] = 1
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, settings)
    emit({'status': 'READY', 'work_cap': 0.50, 'phase_stop': 0.48,
          'tail_reserve': 0.10, 'prior_known_plus_reserved': '45.286767494'})
    exit_code = 0
    try:
        for line in sys.stdin:
            command = json.loads(line)
            if type(command) is not dict:
                raise ValueError('JSON object required')
            if command == {'quit': True}:
                break
            check()
            result = package(command)
            emit(result)
            if result['status'] != 'PASS':
                FAILED = True
                exit_code = 1
                break
    except BaseException as error:
        FAILED = True
        exit_code = 1
        signal.setitimer(signal.ITIMER_PROF, max(0.000001, 0.60 - cpu()))
        emit({'status': 'BUDGET_STOP' if isinstance(error, BudgetStop) else 'FAIL',
              'error': type(error).__name__ + ': ' + str(error),
              'partial_files_possible': True})
    finally:
        signal.setitimer(signal.ITIMER_PROF, max(0.000001, 0.60 - cpu()))
        emit({'status': 'CLOSED', 'exit_code': exit_code,
              'final_accounting': 'Outer Bash time needed for final process exit CPU; cumulative budget never resets.'})
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
