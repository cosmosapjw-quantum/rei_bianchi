"""One manifest-driven presentation pass; never imports payload source."""
import resource
import signal
import sys


def cpu():
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_utime + usage.ru_stime


class BudgetStop(Exception):
    pass


def stop(signum, frame):
    raise BudgetStop('presentation process CPU cap reached')


signal.signal(signal.SIGPROF, stop)
signal.setitimer(signal.ITIMER_PROF, max(0.000001, 0.65 - cpu()))

import hashlib
import json
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path('/workspace/scratch/52cc495a5f0a/rei_finite_history_unit')


def check():
    if cpu() >= 0.60:
        raise BudgetStop('refusing next packaging phase near CPU limit')


def entry_name(name):
    if type(name) is not str:
        raise ValueError('archive_path string required')
    path = PurePosixPath(name)
    if (path.is_absolute() or '..' in path.parts or str(path) != name
            or name in ('.', 'SOURCE_MANIFEST.json') or '\\' in name):
        raise ValueError('unsafe, noncanonical, or reserved archive path')
    return name


def write_entry(archive, name, data):
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data)


def main():
    result = {'status': 'FAIL', 'execution': 'Presentation only; no payload imports or tests.',
              'prior_presentation_cpu': '44.990767494', 'approved_absolute_cap': '46',
              'reservation': 0.80, 'process_work_cap': 0.65, 'tail_reserve': 0.10,
              'unmeasured_cost': 'UNKNOWN_NOT_ZERO', 'crc_passes': 0,
              'archive_sha256_passes': 0}
    result_path = None
    try:
        if len(sys.argv) != 4:
            raise ValueError('usage: package_whole_unit.py MANIFEST OUTPUT_ZIP RESULT_JSON')
        manifest_path, output, result_path = map(Path, sys.argv[1:])
        for path in (manifest_path, output, result_path):
            if not path.is_absolute() or not path.resolve().is_relative_to(ROOT.resolve()):
                raise ValueError('all arguments must be absolute paths under existing unit')
        if output.suffix != '.zip' or output.exists() or result_path.exists():
            raise ValueError('exclusive new ZIP/result paths required')
        if len({manifest_path.resolve(), output.resolve(), result_path.resolve()}) != 3:
            raise ValueError('manifest, archive, and result must be distinct')
        check()
        manifest_bytes = manifest_path.read_bytes()
        manifest = json.loads(manifest_bytes)
        if type(manifest) is not dict or not isinstance(manifest.get('files'), list) or not manifest['files']:
            raise ValueError('manifest object with nonempty files list required')
        if type(manifest.get('source_pin')) is not str or not manifest['source_pin']:
            raise ValueError('explicit source_pin required')
        payload = []
        source_metadata = []
        seen = set()
        for item in manifest['files']:
            check()
            name = entry_name(item['archive_path'])
            if name in seen:
                raise ValueError('duplicate archive path')
            seen.add(name)
            source = Path(item['source'])
            if (not source.is_absolute() or not source.resolve().is_relative_to(ROOT.resolve())
                    or source.resolve() in {output.resolve(), result_path.resolve(), manifest_path.resolve()}):
                raise ValueError('invalid or self-referential source path')
            if source.suffix.lower() == '.zip':
                raise ValueError('existing archives are not payload sources')
            data = source.read_bytes()
            if 'expected_text' in item:
                if type(item['expected_text']) is not str or data != item['expected_text'].encode('utf-8'):
                    raise ValueError('source exact UTF8 text mismatch: ' + name)
            else:
                if type(item['bytes']) is not int or item['bytes'] != len(data):
                    raise ValueError('source byte count mismatch: ' + name)
                if hashlib.sha256(data).hexdigest() != item['sha256']:
                    raise ValueError('source SHA256 mismatch: ' + name)
            actual = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
            if 'git_blob' in item and actual != item['git_blob']:
                raise ValueError('source Git blob mismatch: ' + name)
            source_metadata.append({'path': name, 'bytes': len(data),
                                    'sha256': hashlib.sha256(data).hexdigest(), 'git_blob': actual})
            payload.append((name, data))
        condensed = {'source_pin': manifest['source_pin'],
                     'files': sorted(source_metadata, key=lambda item: item['path'])}
        condensed_bytes = (json.dumps(condensed, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        check()
        with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_STORED, allowZip64=False) as archive:
            for name, data in sorted(payload):
                check()
                write_entry(archive, name, data)
            write_entry(archive, 'SOURCE_MANIFEST.json', condensed_bytes)
        check()
        with zipfile.ZipFile(output, 'r') as archive:
            bad = archive.testzip()
        result['crc_passes'] = 1
        if bad is not None:
            raise ValueError('archive CRC failure: ' + bad)
        check()
        archive_bytes = output.read_bytes()
        digest = hashlib.sha256(archive_bytes).hexdigest()
        result['archive_sha256_passes'] = 1
        result.update({'status': 'PASS', 'archive': str(output), 'bytes': len(archive_bytes),
                       'sha256': digest, 'source_pin': manifest['source_pin'],
                       'input_manifest': str(manifest_path),
                       'source_manifest': 'SOURCE_MANIFEST.json (inside archive)',
                       'source_manifest_sha256': hashlib.sha256(condensed_bytes).hexdigest(),
                       'payload_files': len(payload), 'zip_entries': len(payload) + 1})
        check()
    except BaseException as error:
        result['status'] = 'BUDGET_STOP' if isinstance(error, BudgetStop) else 'FAIL'
        result['error'] = type(error).__name__ + ': ' + str(error)
        result['partial_archive_possible'] = True
    finally:
        signal.setitimer(signal.ITIMER_PROF, 0.10)
        result['process_cpu_before_final_serialization'] = cpu()
        result['final_accounting'] = 'Outer Bash time includes process exit; retain display uncertainty separately. No budget reset.'
        if result_path is not None and result_path.is_absolute() and result_path.resolve().is_relative_to(ROOT.resolve()):
            with result_path.open('x', encoding='utf-8') as stream:
                json.dump(result, stream, indent=2)
                stream.write('\n')
        sys.stdout.write(json.dumps(result) + '\n')
        sys.stdout.flush()
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
