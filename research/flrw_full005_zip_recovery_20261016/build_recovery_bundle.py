#!/usr/bin/env python3
"""Assemble finalized full005 recovery bytes; no science, upload or Git mutation."""
import argparse
import base64
import datetime
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT.parent / 'artifacts'
BASE = '0e25846433170d0f420c4cda44a0bedbf02cd177'
REC = Path('research/flrw_full005_zip_recovery_20261016')
OLD = Path('research/flrw_full005_cli_repair_20261016')
POST = Path('research/flrw_full005_postprocess_20261015')
DIRECT = Path('research/ncp_direct_resume_20261016')
COV = Path('research/flrw_covariant_transport_20261015')
NAME = 'REI_FULL005_ZIP_RECOVERY_20261016_v2'
EXCLUDED = {'PACKAGE_RECEIPT.json', 'DELIVERY_RECEIPT.json'}
FIXED_ZIP_DATE = (2026, 10, 16, 0, 0, 0)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def emit(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def text_files(folder):
    return sorted(p.relative_to(ROOT) for p in (ROOT / folder).rglob('*')
                  if p.is_file() and p.name not in EXCLUDED
                  and '__pycache__' not in p.parts
                  and p.suffix in {'.json', '.md', '.log', '.txt', '.py'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root-ready', action='store_true',
                        help='Root explicitly confirmed ROOTREADY after final evidence and metadata')
    args = parser.parse_args()
    if not args.root_ready:
        parser.error('Wait for ROOTREADY; then build once with --root-ready')
    for required in ('CONTRACT.json', 'IMPLEMENTATION.json', 'INDEPENDENT_REVIEW.json',
                     'HANDOFF.json', 'NEXT_DAG.json', 'CODEX_HANDOFF_KO.md', 'RUNBOOK_KO.md'):
        if not (ROOT / REC / required).is_file():
            raise FileNotFoundError(REC / required)
    ART.mkdir(exist_ok=True)
    archive = ART / (NAME + '.zip')
    receipt_path = ART / (NAME + '_PACKAGE_RECEIPT.json')
    payload_path = ART / (NAME + '_git_payload.json')
    encoded_path = ART / (NAME + '.zip.b64')
    for path in (archive, receipt_path, payload_path, encoded_path):
        if path.exists():
            raise FileExistsError(f'Fresh v2 delivery output required: {path}')

    metadata = [COV / n for n in ('HANDOFF.json', 'LATEST_RESUME.json', 'NEXT_DAG.json')]
    metadata += [POST / 'HANDOFF.json', DIRECT / 'HANDOFF.json']
    recovery_files = text_files(REC)
    changed = sorted(set(recovery_files + metadata + [DIRECT / 'postprocess_ncp.py',
                                                     DIRECT / 'test_postprocess_zip_recovery.py']))
    runtime = [Path('AGENTS.md'), POST / 'postprocess_flrw.py', POST / 'watch_full005.py',
               POST / 'test_postprocess_cli.py']
    runtime += [p.relative_to(ROOT) for pattern in ('vendor/*.py', 'FULL005*.json', 'contracts/*.md')
                for p in (ROOT / POST).glob(pattern)]
    runtime += [POST / n for n in ('HANDOFF.json', 'POSTPROCESS_REVIEW.json', 'POSTPROCESS_REVIEW.md',
                                  'BINDING_GUARD_REPAIR_RECEIPT.json', 'BINDING_GUARD_TEST_ATTESTATION.json',
                                  'REUSE_PROVENANCE.json', 'RECONSTRUCTION_RECEIPT.json', 'VALIDATION_RECEIPT.json')]
    runtime += [DIRECT / n for n in ('ncp_resume.py', 'postprocess_ncp.py', 'backup_ncp.py',
                                    'test_postprocess_ncp.py', 'test_postprocess_zip_recovery.py',
                                    'INDEPENDENT_REVIEW.json',
                                    'HANDOFF.json', 'RUNBOOK_KO.md', 'CODEX_HANDOFF_KO.md')]
    selected = sorted(set(runtime + metadata + recovery_files + text_files(OLD)))
    source = {str(p): (ROOT / p).read_bytes() for p in selected}
    manifest = {
        'kind': 'RUNNABLE_PACKAGE_ONLY_RECOVERY_WITH_EXTERNAL_NATIVE_DATA',
        'base_commit_supplied': BASE,
        'members': [{'path': 'rei_bianchi/' + p, 'bytes': len(data), 'sha256': digest(data)}
                    for p, data in source.items()],
        'manifest_self_hash': 'Excluded to avoid recursion',
        'receipt_outside_bundle': str(REC / 'PACKAGE_RECEIPT.json'),
        'package_only_dependencies': ['Python 3 standard library'],
        'unchanged_renderer_dependencies_if_separately_authorized': ['NumPy', 'Matplotlib'],
        'automatic_installation': False,
        'native_raw_data': 'EXTERNAL_NOT_INCLUDED; existing NCP result and original campaign remain preserved',
        'solver_runs_by_packaging': 0,
        'scientific_admission': 'NOT_ISSUED_BY_PACKAGING',
        'old_docs': 'Historical CLI repair/direct instructions are superseded by recovery HANDOFF/CONTRACT',
    }
    source['ZIP_CONTENTS.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, allowZip64=True) as bundle:
        for name, data in source.items():
            info = zipfile.ZipInfo('rei_bianchi/' + name, date_time=FIXED_ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, data)
    with zipfile.ZipFile(archive) as bundle:
        bad = bundle.testzip()
    if bad is not None:
        raise RuntimeError('ZIP CRC failure: ' + bad)
    data = archive.read_bytes()
    encoded_path.write_text(base64.b64encode(data).decode('ascii'), encoding='ascii')
    emit(payload_path, {
        'repository_full_name': 'cosmosapjw-quantum/rei_bianchi',
        'base_commit_supplied': BASE, 'base_tree_sha': None,
        'base_tree_instruction': 'Root supplies actual existing base tree; never create from an empty tree.',
        'tree_elements': [{'path': str(p), 'mode': '100644', 'type': 'blob',
                           'content': source[str(p)].decode('utf-8')} for p in changed],
    })
    emit(receipt_path, {
        'schema': 'rei.full005_zip_recovery.package.v2',
        'archive': str(archive), 'repository_relative_archive': str(REC / archive.name),
        'archive_sibling_name': archive.name, 'bytes': len(data), 'sha256': digest(data),
        'zip_crc_check': 'PASS', 'zip_entry_date': list(FIXED_ZIP_DATE),
        'manifest': 'rei_bianchi/ZIP_CONTENTS.json',
        'manifest_sha256': digest(source['ZIP_CONTENTS.json']), 'member_count': len(source),
        'git_payload': str(payload_path), 'git_changed_paths': [str(p) for p in changed],
        'base64_file': str(encoded_path), 'base_commit_supplied': BASE,
        'built_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'raw_data': 'EXTERNAL_NOT_INCLUDED', 'tests_rerun_by_builder': False,
        'solver_runs': 0, 'uploads': 0,
        'actual_ncp_recovery': 'NOT_RUN_HERE',
        'scientific_admission': 'NOT_ISSUED_BY_PACKAGING',
        'publication_note': 'Root publishes this receipt beside archive at immutable final code commit; receipt is excluded from archive to avoid self-hash recursion.',
    })
    print(json.dumps({'archive': str(archive), 'receipt': str(receipt_path),
                      'payload': str(payload_path), 'base64': str(encoded_path),
                      'bytes': len(data), 'sha256': digest(data)}))


if __name__ == '__main__':
    main()
