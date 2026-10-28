"""Static final-packager preparation; cap47 execution approval is still pending.

Reuses the successful finite-history manifest packaging design. This module is
import-safe: the process CPU timer and packaging begin only inside main().
No payload module is imported or executed.
"""
import resource
import signal
import sys
import hashlib
import json
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path('/workspace/scratch/52cc495a5f0a/rei_bass_storage_unit')
PRIOR = '46.331767494'
PROPOSED_CAP = '47'
RESERVATION = '0.65'


class BudgetStop(Exception):
    pass


def cpu():
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_utime + usage.ru_stime


def stop(signum, frame):
    raise BudgetStop('absolute presentation process CPU deadline reached')


def check():
    if cpu() >= 0.48:
        raise BudgetStop('refusing next packaging phase near work cap')


def owned(value):
    if type(value) is not str:
        raise ValueError('absolute path string required')
    path = Path(value)
    if not path.is_absolute() or not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('path must remain under the BASS unit root')
    return path


def name(value):
    if type(value) is not str:
        raise ValueError('archive_path string required')
    path = PurePosixPath(value)
    if (path.is_absolute() or '..' in path.parts or str(path) != value
            or '\x00' in value
            or value in ('.', 'SOURCE_MANIFEST.json') or '\\' in value):
        raise ValueError('unsafe, noncanonical, or reserved archive path')
    return value


def entry(archive, archive_path, data):
    info = zipfile.ZipInfo(archive_path, (1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data)


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    # This flag is supplied only after explicit user approval. It is a guard
    # against accidental launch, not a substitute for that approval.
    if len(args) != 5 or args[:2] != ['--approved-reservation', RESERVATION]:
        sys.stderr.write('REFUSED: explicit approved --approved-reservation 0.65 plus MANIFEST ZIP RESULT required; cap47 remains pending until user approval.\n')
        return 2
    result_path = None
    result = {'status': 'FAIL', 'prior_presentation_cpu': PRIOR,
              'approved_cap_requested': PROPOSED_CAP, 'approved_reservation_argument': RESERVATION,
              'work_cap': '0.50', 'absolute_final_deadline': '0.60',
              'outer_report_allowance': '0.05', 'unmeasured_cost': 'UNKNOWN_NOT_ZERO',
              'execution': 'Presentation only; no scientific imports, tests, or payload execution.',
              'crc_passes': 0, 'archive_sha256_passes': 0}
    signal.signal(signal.SIGPROF, stop)
    signal.setitimer(signal.ITIMER_PROF, max(0.000001, 0.50 - cpu()))
    try:
        check()
        manifest_path, output, candidate_result = map(owned, args[2:])
        identities = {path.resolve() for path in (manifest_path, output, candidate_result)}
        if len(identities) != 3 or output.suffix != '.zip':
            raise ValueError('distinct manifest, ZIP, result paths required')
        if output.exists() or candidate_result.exists():
            raise ValueError('existing ZIP/result refused; no automatic retry')
        result_path = candidate_result
        manifest = json.loads(manifest_path.read_bytes())
        if (type(manifest) is not dict or type(manifest.get('source_pin')) is not str
                or not manifest['source_pin'] or type(manifest.get('files')) is not list
                or not manifest['files']):
            raise ValueError('explicit source_pin and nonempty files list required')
        payload, metadata, seen = [], [], set()
        for item in manifest['files']:
            check()
            archive_path = name(item['archive_path'])
            if archive_path in seen:
                raise ValueError('duplicate archive path')
            seen.add(archive_path)
            source = owned(item['source'])
            if source.resolve() in identities or source.suffix.lower() == '.zip':
                raise ValueError('self-reference or existing ZIP source refused')
            expected = item['expected_text']
            if type(expected) is not str:
                raise ValueError('expected_text string required')
            data = source.read_bytes()
            if data != expected.encode('utf-8'):
                raise ValueError('source exact UTF8 bytes mismatch: ' + archive_path)
            blob = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
            if 'git_blob' in item and item['git_blob'] != blob:
                raise ValueError('source Git blob mismatch: ' + archive_path)
            payload.append((archive_path, data))
            metadata.append({'path': archive_path, 'bytes': len(data),
                             'sha256': hashlib.sha256(data).hexdigest(), 'git_blob': blob})
        condensed = {'source_pin': manifest['source_pin'],
                     'files': sorted(metadata, key=lambda item: item['path'])}
        condensed_bytes = (json.dumps(condensed, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        check()
        with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_STORED, allowZip64=False) as archive:
            for archive_path, data in sorted(payload):
                check()
                entry(archive, archive_path, data)
            entry(archive, 'SOURCE_MANIFEST.json', condensed_bytes)
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
        check()
        result.update({'status': 'PASS', 'archive': str(output), 'bytes': len(archive_bytes),
                       'sha256': digest, 'source_pin': manifest['source_pin'],
                       'input_manifest': str(manifest_path), 'source_manifest': 'SOURCE_MANIFEST.json (inside archive)',
                       'source_manifest_sha256': hashlib.sha256(condensed_bytes).hexdigest(),
                       'payload_files': len(payload), 'zip_entries': len(payload) + 1})
    except BaseException as error:
        result.update({'status': 'BUDGET_STOP' if isinstance(error, BudgetStop) else 'FAIL',
                       'error': type(error).__name__ + ': ' + str(error),
                       'partial_archive_possible': True})
    finally:
        # Absolute deadline includes startup; repeated tail renewal is forbidden.
        signal.setitimer(signal.ITIMER_PROF, max(0.000001, 0.60 - cpu()))
        result['process_cpu_before_final_serialization'] = cpu()
        result['final_accounting'] = 'Outer Bash receipt must include final exit; retain display uncertainty and prior actual. No budget reset.'
        if result_path is not None:
            with result_path.open('x', encoding='utf-8') as stream:
                json.dump(result, stream, ensure_ascii=False, indent=2)
                stream.write('\n')
        sys.stdout.write(json.dumps(result, ensure_ascii=False) + '\n')
        sys.stdout.flush()
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
