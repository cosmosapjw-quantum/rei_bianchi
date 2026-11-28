"""Check the byte chain and runtime paths; do not confer build/science authority."""
from pathlib import Path
import argparse
import hashlib
import json
import re

PINS = {
    'flint': {'version':'3.4.0', 'sha256':'108ab51a4dd33918ff3308f0c63a63616ae30a2c174d50c9188676e85011346f', 'size':8702721},
    'gmp': {'version':'6.3.0', 'sha256':'a3c2b80201b89e68616f4ad30bc66aee4927c3ce50e33929ca819d5c43538898', 'size':2094196},
    'mpfr': {'version':'4.2.2', 'sha256':'b67ba0383ef7e8a8563734e2e889ef5ec3c3b898a01d00fa0a6869ad81c6ce01', 'size':1505596},
}
MAX_FILE_BYTES = 512 * 1024 * 1024
MAX_RECORD_BYTES = 2 * 1024 * 1024


def required_digest(value):
    if not isinstance(value, str) or re.fullmatch(r'[0-9a-f]{64}', value) is None:
        raise ValueError('required SHA256 digest is absent or malformed')
    return value


def file_identity(value, expected=None, *, maximum=MAX_FILE_BYTES):
    path = Path(value)
    if not path.is_absolute():
        raise ValueError('identity requires an absolute path')
    try:
        path = path.resolve(strict=True)
        if not path.is_file() or path.stat().st_size > maximum:
            raise ValueError('not a bounded regular file: ' + str(path))
        h = hashlib.sha256()
        size = 0
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                size += len(block)
                if size > maximum:
                    raise ValueError('file grew above bound')
                h.update(block)
    except OSError as exc:
        raise ValueError('unavailable identity file: ' + str(path)) from exc
    digest = h.hexdigest()
    if expected is not None and digest != expected:
        raise ValueError('SHA256 mismatch: ' + str(path))
    return {'path': str(path), 'size': size, 'sha256': digest}


def verify_backend(record_path, prefix):
    """Return a verified copy; a caller's success flag never replaces log bytes."""
    record_path = Path(record_path)
    if record_path.stat().st_size > MAX_RECORD_BYTES:
        raise ValueError('provenance record too large')
    record = json.loads(record_path.read_text())
    prefix = Path(prefix)
    if not prefix.is_absolute() or not prefix.is_dir():
        raise ValueError('prefix must be an existing absolute directory')
    prefix = prefix.resolve(strict=True)
    if Path(record.get('prefix', '')).resolve() != prefix:
        raise ValueError('record/prefix mismatch')
    compiler = record.get('compiler', {})
    if not compiler.get('version'):
        raise ValueError('compiler version missing')
    file_identity(compiler['path'], required_digest(compiler.get('sha256')))
    libraries = record.get('libraries', {})
    if set(libraries) != set(PINS):
        raise ValueError('exactly the pinned three libraries are required')
    checked = {}
    for name, pin in PINS.items():
        item = libraries[name]
        if item.get('version') != pin['version'] or item.get('source_archive_sha256') != pin['sha256']:
            raise ValueError(name + ' source/version pin mismatch')
        source = file_identity(item['source_archive_path'], pin['sha256'], maximum=32*1024*1024)
        if source['size'] != pin['size']:
            raise ValueError(name + ' archive length mismatch')
        binary = file_identity(item['binary_path'], required_digest(item.get('binary_sha256')))
        if not Path(binary['path']).is_relative_to(prefix):
            raise ValueError(name + ' binary escaped sidecar prefix')
        with Path(binary['path']).open('rb') as stream:
            if stream.read(4) != b'\x7fELF':
                raise ValueError(name + ' binary is not ELF')
        if not item.get('compiler') or not item.get('flags') or not item.get('abi'):
            raise ValueError(name + ' compiler/flags/ABI metadata missing')
        flags = item['flags']
        tokens = flags if isinstance(flags, list) else str(flags).split()
        if any(x in ('-ffast-math', '-Ofast', '-funsafe-math-optimizations') for x in tokens):
            raise ValueError(name + ' unsafe floating flags')
        logs = item.get('build_logs', [])
        if not isinstance(logs, list) or len(logs) > 20:
            raise ValueError(name + ' invalid stage log list')
        stages = {}
        for log in logs:
            stage = log.get('stage')
            if not isinstance(stage, str) or stage in stages or type(log.get('exit_code')) is not int or log['exit_code'] != 0:
                raise ValueError(name + ' failed or duplicated stage')
            stages[stage] = file_identity(log['path'], required_digest(log.get('sha256')), maximum=64*1024*1024)
            stages[stage]['streams'] = {}
            for stream in ('stdout', 'stderr'):
                reference = log.get(stream)
                if not isinstance(reference, dict):
                    raise ValueError(name + ' missing actual ' + stream + ' log identity')
                stages[stage]['streams'][stream] = file_identity(reference['path'], required_digest(reference.get('sha256')), maximum=64*1024*1024)
        if not {'configure', 'build', 'install'} <= stages.keys():
            raise ValueError(name + ' missing executed-stage record')
        if item.get('build_log_sha256') != stages['build']['sha256']:
            raise ValueError(name + ' build log aggregate mismatch')
        checked[name] = {'source': source, 'binary': binary, 'stages': stages}
    record['verification'] = {
        'status': 'BYTE_CHAIN_VERIFIED', 'libraries': checked,
        'independent_execution_proven': False,
        'historical_abi_admitted': False, 'scientific_promotion': False,
        'limitation': 'Checks source pins and supplied compiler/log/binary bytes; a forged complete record is not an independently witnessed build. Native synthetic acceptance and reviewer admission are separate.',
    }
    return record


def verify_linkage(ldd_text, expected_library_paths):
    """Parse ldd of our newly built synthetic binary, never an arbitrary payload."""
    if not isinstance(ldd_text, str) or len(ldd_text) > 256*1024:
        raise ValueError('link report size/type')
    if set(expected_library_paths) != {'flint', 'gmp', 'mpfr'}:
        raise ValueError('expected three backend library paths')
    if any(not Path(p).is_absolute() for p in expected_library_paths.values()):
        raise ValueError('absolute backend library paths required')
    expected = {n: Path(file_identity(p)['path']) for n,p in expected_library_paths.items()}
    found = {}
    system = []
    seen_names = set()
    for raw in ldd_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(('linux-vdso.so', 'linux-gate.so')):
            continue
        if 'not found' in line or 'not a dynamic executable' in line or 'statically linked' in line:
            raise ValueError('missing or unverifiable dynamic dependency')
        m = re.fullmatch(r'(\S+)\s+=>\s+(.+?)\s+\(0x[0-9a-fA-F]+\)', line)
        if m:
            soname, path = m.groups()
        else:
            m = re.fullmatch(r'(/.+?)\s+\(0x[0-9a-fA-F]+\)', line)
            if not m:
                raise ValueError('unparsed dynamic dependency: ' + line)
            path = m.group(1)
            soname = Path(path).name
        if soname in seen_names:
            raise ValueError('duplicated dynamic dependency: ' + soname)
        seen_names.add(soname)
        backend = next((n for n in expected if re.fullmatch('lib'+n+r'\.so(?:\.\d+)*', soname)), None)
        if backend is not None:
            actual = file_identity(path)
            if backend in found or Path(actual['path']) != expected[backend]:
                raise ValueError('unexpected backend path: ' + soname)
            found[backend] = actual
        else:
            if not re.fullmatch(r'(?:lib(?:c|m|stdc\+\+|gcc_s|pthread|dl|rt)\.so(?:\.\d+)*|ld-linux[^/]*\.so(?:\.\d+)*)', soname):
                raise ValueError('unreviewed extra runtime dependency: ' + soname)
            system.append({'soname': soname, **file_identity(path)})
    if set(found) != set(expected):
        raise ValueError('backend dependency missing from link report')
    return {'status':'LINKED_BACKEND_PATHS_VERIFIED', 'libraries':found, 'system_libraries':system,
            'limitation':'Path and bytes at check time; host filesystem stability is assumed during immediate execution.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record')
    parser.add_argument('prefix')
    args = parser.parse_args()
    print(json.dumps(verify_backend(args.record, args.prefix)['verification'], indent=2))


if __name__ == '__main__':
    main()
