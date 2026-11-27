#!/usr/bin/env python3
"""Tiny actual-byte transport controls; no production archive or science runs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import zipfile

import build_delivery as builder
import restore_transfer as restore


def main():
    started = time.monotonic()
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=base / 'FIXTURE_CONTROLS')
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(exist_ok=False)
    source_before = {name: restore.pin(base / name) for name in ('restore_transfer.py', 'build_delivery.py')}
    checks = {}
    try:
        restore.safe_relative('.')
    except ValueError:
        checks['standalone_dot_path_rejected'] = True
    else:
        checks['standalone_dot_path_rejected'] = False
    payload = output / 'MINI_FIXTURE'
    payload.mkdir()
    content = b'Preserve exact bytes\r\nE13C9 transport fixture\x00\xff\n'
    (payload / 'payload.bin').write_bytes(content)
    pins = {'payload.bin': restore.pin(payload / 'payload.bin')}
    restore.save(payload / 'PACKAGE_MANIFEST.json', {'schema': 'fixture-transport-v1', 'files': pins})
    package_manifest_pin = restore.pin(payload / 'PACKAGE_MANIFEST.json')
    archive = output / 'fixture.zip'
    builder.create_archive(payload, sorted(payload.iterdir()), archive)
    members = builder.verify_archived_payloads(archive, payload.name, pins, package_manifest_pin)
    checks['actual_builder_zip_payload_verification'] = members == 2
    raw = archive.read_bytes()
    sizes = [len(raw) // 2, len(raw) - len(raw) // 2]
    downloads = output / 'downloaded_parts'
    downloads.mkdir()
    logical_parts = []
    cursor = 0
    for index, size in enumerate(sizes, start=1):
        canonical = 'fixture.zip.part%03d' % index
        actual_name = canonical + ('.bin' if index == 2 else '')
        path = downloads / actual_name
        path.write_bytes(raw[cursor:cursor + size])
        cursor += size
        logical_parts.append({'index': index, 'canonical_name': canonical, **restore.pin(path)})
    selected = restore.select_parts(downloads, logical_parts)
    rebuilt = output / 'REASSEMBLED_FIXTURE.zip'
    restore.reassemble(selected, rebuilt, restore.pin(archive))
    extracted = output / 'extracted'
    extracted_receipt = restore.extract_verified(rebuilt, extracted, 'MINI_FIXTURE/PACKAGE_MANIFEST.json',
                                                 'MINI_FIXTURE/', 'fixture-transport-v1',
                                                 expected_manifest_pin=package_manifest_pin)
    checks['suffixed_part002_selected_by_actual_bytes'] = selected[1]['actual_path'].endswith('.part002.bin')
    checks['original_download_names_preserved'] = (downloads / 'fixture.zip.part002.bin').is_file() and not (downloads / 'fixture.zip.part002').exists()
    checks['ordered_complete_hash_matches'] = restore.pin(rebuilt) == restore.pin(archive)
    checks['actual_extracted_payload_matches'] = (extracted / 'MINI_FIXTURE/payload.bin').read_bytes() == content
    checks['all_fixture_payloads_verified'] = extracted_receipt['payload_files_verified'] == 1

    # Exercise the real production CLI's missing-piece failure before extraction.
    # Fixed production dependency pins are not weakened or replaced for a test.
    empty_downloads = output / 'empty_downloads'
    empty_downloads.mkdir()
    missing_bytes = b'not present'
    missing_pin = {'bytes': len(missing_bytes), 'sha256': hashlib.sha256(missing_bytes).hexdigest()}
    missing_transfer = {'schema': restore.TRANSFER_SCHEMA, 'package_root': restore.PACKAGE_ROOT,
                        'archive': {'canonical_name': 'missing.zip', **missing_pin},
                        'parts': [{'index': 1, 'canonical_name': 'missing.zip.part001', **missing_pin}],
                        'package_manifest': package_manifest_pin,
                        'dependencies': restore.DEPENDENCIES, 'prior_recovery': restore.PRIOR_RECOVERY,
                        'restore_helper': {'relative_path': 'restore_transfer.py', **source_before['restore_transfer.py']},
                        'new_NCP_heavy_tasks': 0}
    missing_manifest = output / 'MISSING_TRANSFER_MANIFEST.json'
    restore.save(missing_manifest, missing_transfer)
    missing_output = output / 'MISSING_PART_FIRST_FAILURE'
    command = [sys.executable, '-B', str(base / 'restore_transfer.py'), '--manifest', str(missing_manifest),
               '--manifest-sha256', restore.sha(missing_manifest), '--parts-dir', str(empty_downloads),
               '--output-dir', str(missing_output)]
    process = subprocess.run(command, capture_output=True, check=False, timeout=2)
    (output / 'MISSING_PART.stdout').write_bytes(process.stdout)
    (output / 'MISSING_PART.stderr').write_bytes(process.stderr)
    failure = restore.load_json((missing_output / 'FIRST_FAILURE.json').read_bytes())
    checks['missing_part_cli_exit_1'] = process.returncode == 1
    checks['missing_part_first_failure_preserved'] = failure['error_type'] == 'FileNotFoundError' and failure['stage'] == 'COMPLETE_ARCHIVE'
    checks['missing_part_no_extraction_or_science'] = (not (missing_output / 'package').exists()
        and failure['scientific_kernel_calls'] == failure['MPI_invocations'] == failure['NCP_execute_invocations'] == 0
        and failure['prior_restore_helper_invocations'] == failure['automatic_retries'] == 0)

    unsafe = output / 'UNSAFE_PATH_FIXTURE.zip'
    with zipfile.ZipFile(unsafe, 'x') as zipped:
        zipped.writestr('../outside.txt', b'blocked')
    try:
        restore.extract_verified(unsafe, output / 'unsafe_extracted', 'PACKAGE_MANIFEST.json', '', 'fixture-transport-v1')
    except ValueError as error:
        checks['unsafe_zip_path_rejected_before_extraction'] = str(error) == 'noncanonical relative path' and not (output / 'unsafe_extracted').exists()
    else:
        checks['unsafe_zip_path_rejected_before_extraction'] = False
    checks['helper_source_bytes_unchanged'] = source_before == {name: restore.pin(base / name) for name in source_before}
    if not all(checks.values()):
        raise AssertionError('transport fixture control failed: ' + json.dumps(checks))
    receipt = {'schema': 'bass-he-e13c9-transport-fixture-control-receipt-v1',
               'status': 'PASS_TINY_ACTUAL_BYTE_TRANSPORT_CONTROLS',
               'finished_utc': datetime.now(timezone.utc).isoformat(), 'checks': checks,
               'checks_passed': len(checks), 'checks_failed': 0, 'source_pins': source_before,
               'fixture_archive': restore.pin(archive), 'selected_parts': selected,
               'fixture_extraction': extracted_receipt,
               'expected_negative_control': {'command': command, 'returncode': process.returncode,
                   'first_failure': {'path': str(missing_output / 'FIRST_FAILURE.json'), **restore.pin(missing_output / 'FIRST_FAILURE.json')}},
               'scientific_kernel_calls': 0, 'MPI_invocations': 0, 'NCP_execute_invocations': 0,
               'production_complete_archives_built': 0, 'actual_E13C8_hydrations': 0,
               'automatic_retries': 0, 'elapsed_seconds': time.monotonic() - started,
               'scope_limit': 'tiny actual-byte builder/select/reassemble/extract controls and real CLI missing-part failure; not a production hydrate or scientific admission'}
    restore.save(output / 'TRANSPORT_CONTROL_RECEIPT.json', receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
