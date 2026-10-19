"""Verify four caller-supplied provider downloads without network or source writes.

Reuse frozen shipping utilities and the exact published source plan. This is
archive/readback verification only: no test, solver, native export or build runs.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import importlib.util
import json
import sys
import time
import tomllib
import zipfile

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parent
WORKSPACE = BASE.parents[2]
TASK = WORKSPACE/'rei_bianchi/research/rei_age_exposure_envelope_20261018'
HELPER = TASK/'vigilode_age_transport_20261019/ship_artifacts.py'
SPEC = importlib.util.spec_from_file_location('frozen_ship_artifacts', HELPER)
SHIP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SHIP)
PLAN_PATH = BASE/'SOURCE_PLAN.json'
PLAN = SHIP.load(PLAN_PATH)
SOURCE = {row['path']: row for row in PLAN['files']}
PUBLISHED_COMMIT = '50bc41f6b6aea05f67c03ab3ad23bb118d574622'
PUBLISHED_ROOT = '6c54f5d176845ef8122357b6090964decde0da20'
PUBLISHED_TASK = '411b11eb8c939fdbe974a383725472b7cbf00360'
EXPECTED = {
    'C8': {'bytes': 3482883,
           'sha256': 'a2a634f819deb9cc047466274fc655985f9c09a54abc350d7259e402368f24e4',
           'entries': 1225, 'source_files': 1223, 'archive_only': 0,
           'local': TASK/'deliverables/REI_AGE_ENVELOPE_C8_CODE_20261019_v6.zip'},
    'C10': {'bytes': 20837116,
            'sha256': '40910062112b341b10c16e632f821b8e1dac5210299b15c585b39f1cc3b29559',
            'entries': 2002, 'source_files': 1844, 'archive_only': 156,
            'local': TASK/'deliverables/REI_AGE_ENVELOPE_EXECUTION_READY_20261019_v6.zip'},
}


def file_sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            digest.update(block)
    return digest.hexdigest()


def exact_files_equal(first, second):
    with first.open('rb') as a, second.open('rb') as b:
        while True:
            x, y = a.read(1024*1024), b.read(1024*1024)
            if x != y:
                return False
            if not x:
                return True


def expected_source_set(kind):
    if kind == 'C10':
        return set(SOURCE)
    with zipfile.ZipFile(PLAN['prior_c8']) as old:
        old_paths = {name for name in old.namelist() if name.startswith(SHIP.TASK_PREFIX)}
    return {path for path,row in SOURCE.items() if path in old_paths or
            (row['changed'] and not path.startswith(SHIP.NEW_PREFIX)) or
            (path.startswith(SHIP.NEW_PREFIX) and
             not path[len(SHIP.NEW_PREFIX):].startswith(('inputs/','results/')))}


def verify_vendor(archive):
    prefix = SHIP.NEW_PREFIX+'rust/vendor/'
    lock = tomllib.loads(archive.read(SHIP.NEW_PREFIX+'rust/Cargo.lock').decode())
    packages = [row for row in lock['package'] if row.get('source','').startswith('registry+')]
    assert len(packages) == 22
    source_files = 0
    for package in packages:
        directory = prefix+package['name']+'/'
        checksum = json.loads(archive.read(directory+'.cargo-checksum.json'))
        assert checksum['package'] == package['checksum']
        for name, expected in checksum['files'].items():
            assert SHIP.sha(archive.read(directory+name)) == expected
            source_files += 1
    assert source_files == 865
    return {'registry_packages': 22, 'package_archive_checksums_match_lock': True,
            'vendored_source_files_rehashed': source_files,
            'vendored_members_including_checksum_manifests': source_files+22}


def verify_one(provider, kind, path):
    started = time.monotonic()
    expected = EXPECTED[kind]
    assert path.is_file(), 'Missing download: '+str(path)
    assert path.resolve() != expected['local'].resolve(), 'Download must be distinct from original local archive'
    assert path.stat().st_size == expected['bytes']
    actual_sha = file_sha(path)
    assert actual_sha == expected['sha256']
    assert file_sha(expected['local']) == expected['sha256']
    assert exact_files_equal(path, expected['local'])
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names)) == expected['entries'], 'Duplicate or unexpected ZIP entries'
        assert not any(info.is_dir() for info in archive.infolist())
        assert archive.testzip() is None
        manifest = json.loads(archive.read('PAYLOAD_SHA256.json'))
        assert manifest['source_commit'] == PUBLISHED_COMMIT
        assert manifest['task_git_tree'] == PUBLISHED_TASK
        assert set(names) == set(manifest['files']) | {'PAYLOAD_SHA256.json'}
        for name, identity in manifest['files'].items():
            data = archive.read(name)
            assert len(data) == identity['size']
            assert SHIP.sha(data) == identity['sha256']
        receipt = json.loads(archive.read('PACKAGE_RECEIPT.json'))
        assert receipt['kind'] == kind and receipt['schema'] == 'rei.delivery.package.v6'
        assert receipt['source_commit'] == PUBLISHED_COMMIT
        assert receipt['source_parent'] == SHIP.BASELINE_COMMIT
        assert receipt['task_git_tree'] == PUBLISHED_TASK
        assert receipt['frozen_source_plan_sha256'] == file_sha(PLAN_PATH)
        assert receipt['PRODUCTION_SCIENTIFIC_ADMISSION'] == 'NOT_ISSUED'
        included = {name for name in names if name.startswith(SHIP.TASK_PREFIX)}
        expected_included = expected_source_set(kind)
        assert included == expected_included
        assert len(included) == receipt['included_source_files'] == expected['source_files']
        source_rows = []
        for name in sorted(included):
            data = archive.read(name)
            original = SOURCE[name]
            assert len(data) == original['bytes'] and SHIP.sha(data) == original['sha256']
            assert SHIP.blob_sha(data) == original['blob_sha']
            mode = format(archive.getinfo(name).external_attr >> 16, 'o')
            assert mode == original['mode']
            source_rows.append({'path': name, 'mode': mode, 'blob_sha': SHIP.blob_sha(data)})
        if kind == 'C10':
            assert SHIP.tree_sha(source_rows) == PUBLISHED_TASK
        native_result = None
        extras = {name for name in names if name.startswith('archive_only/')}
        assert len(extras) == receipt['archive_only_files'] == expected['archive_only']
        if kind == 'C10':
            with zipfile.ZipFile(PLAN['prior_c10']) as prior:
                assert extras == {name for name in prior.namelist() if name.startswith('archive_only/')}
            native = json.loads(archive.read(SHIP.TASK_PREFIX+'contracts/NATIVE_INPUTS.json'))
            assert native['native_sha'] == SHIP.NATIVE and len(native['files']) == 153
            for name, identity in native['files'].items():
                data = archive.read('archive_only/runtime_base/native_original_35d9747/'+name)
                assert len(data) == identity['size'] and SHIP.sha(data) == identity['sha256']
            binary = archive.read('archive_only/runtime_base/blockmax_B1/positive_native.bin')
            assert len(binary) == 1045408 and SHIP.sha(binary) == SHIP.B1_SHA
            mapping = json.loads(archive.read('archive_only/B1_RESTORATION_MAP.json'))
            assert mapping['binary_sha256'] == SHIP.B1_SHA
            assert len(mapping['deduplicated_source_files']) == 161
            for row in mapping['deduplicated_source_files']:
                assert SHIP.sha(archive.read(row['source_archive_path'])) == row['sha256']
            layout = archive.read('archive_only/RESTORATION_LAYOUT.md').decode()
            assert PUBLISHED_COMMIT in layout and '1844 task files' in layout
            native_result = {'original_native_files': 153, 'native_manifest_identity': SHIP.NATIVE,
                             'B1_binary_bytes': len(binary), 'B1_binary_sha256': SHIP.B1_SHA,
                             'deduplicated_B1_source_files': 161, 'restoration_layout_source_binding': 'PASS'}
        vendor = verify_vendor(archive)
    return {'provider': provider, 'kind': kind, 'download_path': str(path.resolve()),
            'bytes': expected['bytes'], 'sha256': actual_sha, 'whole_byte_comparison': 'PASS',
            'zip_entries': expected['entries'], 'zip_crc': 'PASS',
            'exact_manifest_member_set': 'PASS', 'all_manifest_sizes_and_sha256': 'PASS',
            'included_source_files': len(included), 'source_blob_and_mode_identity': 'PASS',
            'source_task_tree': PUBLISHED_TASK, 'source_commit': PUBLISHED_COMMIT,
            'native_B1_restoration': native_result, 'vendor': vendor,
            'wall_seconds': time.monotonic()-started}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for provider in ['drive','dropbox']:
        for kind in ['c8','c10']:
            parser.add_argument('--'+provider+'-'+kind, type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assert not output.exists(), 'Do not overwrite an earlier verification receipt'
    assert SHIP.REPO not in output.parents, 'Write readback receipt outside frozen source first'
    paths = [getattr(args, provider+'_'+kind) for provider in ['drive','dropbox'] for kind in ['c8','c10']]
    assert len({path.resolve() for path in paths}) == 4, 'Four distinct provider download files are required'
    output.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    receipt = {'schema': 'rei.v6.four_provider_full_readback.v1',
               'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'source_commit': PUBLISHED_COMMIT, 'repository_root_tree': PUBLISHED_ROOT,
               'source_task_tree': PUBLISHED_TASK,
               'source_plan_sha256': file_sha(PLAN_PATH), 'helper_sha256': file_sha(Path(__file__)),
               'provider_provenance': 'Caller-supplied provider download files; this verifier performs no network operations.',
               'command': sys.argv, 'scientific_execution': 'NOT_RUN',
               'Git_or_upload_mutations': 'NOT_RUN', 'PRODUCTION_SCIENTIFIC_ADMISSION': 'NOT_ISSUED',
               'downloads': []}
    try:
        assert PLAN['source_task_tree'] == PUBLISHED_TASK
        for provider in ['drive','dropbox']:
            for kind in ['C8','C10']:
                receipt['downloads'].append(verify_one(provider,kind,getattr(args,provider+'_'+kind.lower())))
        receipt['status'] = 'PASS_FOUR_FULL_PROVIDER_READBACKS'
    except Exception as error:
        receipt['status'] = 'FAIL'
        receipt['error'] = type(error).__name__+': '+str(error)
        receipt['wall_seconds'] = time.monotonic()-started
        output.write_text(json.dumps(receipt,indent=2)+'\n')
        raise
    receipt['wall_seconds'] = time.monotonic()-started
    output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'status': receipt['status'], 'downloads': len(receipt['downloads']),
                      'receipt': str(output), 'receipt_sha256': file_sha(output),
                      'wall_seconds': receipt['wall_seconds']}))


if __name__ == '__main__':
    main()
