"""Local, offline verification of actual downloaded final ZIP or JSON bytes."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import tempfile
import zipfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def load(path):
    return json.loads(Path(path).read_bytes())


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def keypath(value, keys):
    for key in keys:
        value = value[key]
    return value


def check_fields(value, checks):
    # Missing keys fail; an explicitly expected null remains null.
    for item in checks:
        require(keypath(value, item['keys']) == item['value'], str(item['keys']))


def raw(path, expected):
    data = Path(path).read_bytes()
    require(len(data) == expected['bytes'], 'raw byte count')
    require(sha(data) == expected['sha256'], 'raw SHA256')
    return data


def verify_zip(download, expectation):
    e = load(expectation)
    data = raw(download, e)
    c = load(e['original_config'])
    inherited = load(e['reuse_bindings'])
    authoritative = load(e['authoritative_tree'])
    # Root supplies the tree map, head/tree identity and raw-source metadata.
    require(authoritative['head'] == c['head'], 'authoritative head')
    require(authoritative['tree'] == c['tree'], 'authoritative tree')
    require(bool(authoritative['source_metadata']), 'authoritative source metadata')
    frozen = load(e['frozen_manifest'])['files']
    with zipfile.ZipFile(download) as z:
        infos = z.infolist()
        names = [i.filename for i in infos]
        require(len(names) == len(set(names)), 'duplicate ZIP path')
        for i in infos:
            p = PurePosixPath(i.filename)
            require(not p.is_absolute() and '..' not in p.parts and '\\' not in i.filename,
                    'unsafe ZIP path: ' + i.filename)
            require(not i.is_dir() and not stat.S_ISLNK(i.external_attr >> 16),
                    'non-file ZIP member: ' + i.filename)
        require(z.testzip() is None, 'ZIP CRC')
        payload = {n: z.read(n) for n in names}
    manifest = json.loads(payload['ARCHIVE_MANIFEST.json'])
    records = manifest['files']
    require(set(payload) == set(records) | {'ARCHIVE_MANIFEST.json'}, 'ZIP path set')
    require(manifest['head'] == c['head'] and manifest['tree'] == c['tree'], 'manifest Git identity')
    for key in ('expected_parent', 'PR', 'caps', 'scoped_roles_snapshot', 'total_roles'):
        require(manifest[key] == c[key], 'manifest config: ' + key)
    require(manifest['scientific_identity'] == c.get('scientific_identity'), 'scientific identity')
    check_fields(manifest, e.get('manifest_checks', []))
    remote = authoritative['files']
    inherited_map = {r['path']: r for r in inherited['files']}
    git_count = 0
    for name, r in records.items():
        b = payload[name]
        require(len(b) == r['bytes'] and sha(b) == r['sha256'], 'payload: ' + name)
        if 'git_blob' in r:
            pinned = remote.get(name)
            if pinned is None:
                require(name in inherited_map, 'no authoritative Git binding: ' + name)
                pinned = inherited_map[name]['git_blob']
            require(blob(b) == r['git_blob'] == pinned, 'Git blob: ' + name)
            git_count += 1
    # All unit tree blobs must be represented, including any omitted from the manifest.
    unit_prefix = c['unit'].rstrip('/') + '/'
    unit_files = {n for n in remote if n.startswith(unit_prefix)}
    require(unit_files == {n for n, r in records.items() if r['role'] == 'git_owned'},
            'authoritative unit path set')
    for name, r in inherited_map.items():
        b = payload[name]
        require(len(b) == r['bytes'] and sha(b) == r['sha256'] and blob(b) == r['git_blob'],
                'inherited identity: ' + name)
    for name, digest in frozen.items():
        full = name if name.startswith(unit_prefix) else unit_prefix + name
        require(sha(payload[full]) == digest, 'frozen identity: ' + full)
    require(len(frozen) == 8, 'frozen eight')
    contract_name = c.get('contract_path', unit_prefix + 'CONTRACT.json')
    inputs = json.loads(payload[contract_name])['inputs']
    require(len(inputs) == 3, 'three contract inputs')
    for r in inputs:
        b = payload[r['path']]
        require(len(b) == r['bytes'] and sha(b) == r['sha256'], 'input identity: ' + r['path'])
        if r.get('git_blob') is not None:
            require(blob(b) == r['git_blob'], 'input Git identity: ' + r['path'])
    parents = [n for n, r in records.items() if r['role'] == 'whole_parent_archive']
    require(len(parents) == manifest['parent_whole_archives'] == 1, 'whole parent archive')
    require(manifest['parent_nested_restore'] == 0, 'nested parent restore')
    for r in inherited['parent_files']:
        name = 'parent/' + Path(r['path']).name
        b = payload[name]
        require(len(b) == r['bytes'] and sha(b) == r['sha256'], 'parent identity: ' + name)
    # Create a unique directory only after all byte and identity checks pass.
    destination = Path(tempfile.mkdtemp(prefix='PHYS91_actual_restore_', dir=e['extract_parent']))
    for name, b in payload.items():
        out = destination.joinpath(*PurePosixPath(name).parts)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open('xb') as f:
            f.write(b)
        require(sha(out.read_bytes()) == sha(b), 'extracted SHA256: ' + name)
    require({p.relative_to(destination).as_posix() for p in destination.rglob('*') if p.is_file()}
            == set(payload), 'extracted path set')
    return dict(status='PASS', downloaded_path=str(download), bytes=len(data), sha256=sha(data),
                members=len(payload), payloads=len(records), git_blobs=git_count,
                frozen=len(frozen), contract_inputs=len(inputs), every_zip_crc='PASS',
                every_payload_sha256='PASS', authoritative_git_identity='PASS',
                actual_extraction=str(destination), every_extracted_sha256='PASS',
                parent_whole_archives=len(parents), parent_nested_restore=0,
                source_metadata=e.get('source_metadata'),
                authoritative_source_metadata=authoritative['source_metadata'],
                scientific_identity=manifest['scientific_identity'])


def verify_json(download, expectation):
    e = load(expectation)
    data = raw(download, e)
    value = json.loads(data)
    check_fields(value, e['checks'])
    return dict(status='PASS', downloaded_path=str(download), bytes=len(data), sha256=sha(data),
                parsed_identity_checks=e['checks'], source_metadata=e.get('source_metadata'))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['zip', 'json'])
    p.add_argument('downloaded_path')
    p.add_argument('expectation')
    p.add_argument('receipt', help='create-only output receipt')
    a = p.parse_args()
    require(not Path(a.receipt).exists(), 'receipt already exists')
    result = (verify_zip if a.mode == 'zip' else verify_json)(a.downloaded_path, a.expectation)
    with Path(a.receipt).open('x') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write('\n')
