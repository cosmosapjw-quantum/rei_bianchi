#!/usr/bin/env python3
"""Read newly backed-up provider bytes and compare original native identities.

Temporary download links are read from a private, untracked input file and
never written to the receipt. No automatic retries or native evolution.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import time
import urllib.error
import urllib.request


def verify(entry, expected, control_output):
    start = time.monotonic()
    result = {key: entry.get(key) for key in
              ['name', 'id', 'path', 'path_display', 'size', 'content_hash']}
    result['expected_native_sha256'] = expected['sha256']
    result['expected_native_bytes'] = expected['bytes']
    result['expected_dropbox_content_hash'] = expected['dropbox_content_hash']
    result['automatic_retries'] = 0
    result['status'] = 'PENDING'
    saved = None
    try:
        assert entry['size'] == expected['bytes'], 'PROVIDER_SIZE_MISMATCH'
        assert entry['content_hash'] == expected['dropbox_content_hash'], 'PROVIDER_HASH_MISMATCH'
        whole, blocks, count = hashlib.sha256(), hashlib.sha256(), 0
        is_control = entry['name'] == 'T1_CONTROL_SOURCE_PREFLIGHT_ANALYSIS.tar.gz'
        if is_control:
            saved = control_output.open('xb')
        with urllib.request.urlopen(entry['download_url'], timeout=45) as response:
            while True:
                block = bytearray()
                while len(block) < 4 * 1024 * 1024:
                    piece = response.read(4 * 1024 * 1024 - len(block))
                    if not piece:
                        break
                    block.extend(piece)
                if not block:
                    break
                whole.update(block)
                blocks.update(hashlib.sha256(block).digest())
                count += len(block)
                if saved:
                    saved.write(block)
        result.update(downloaded_bytes=count, downloaded_sha256=whole.hexdigest(),
                      downloaded_dropbox_content_hash=blocks.hexdigest())
        assert count == expected['bytes'], 'DOWNLOADED_SIZE_MISMATCH'
        assert whole.hexdigest() == expected['sha256'], 'DOWNLOADED_SHA256_MISMATCH'
        assert blocks.hexdigest() == expected['dropbox_content_hash'], 'DOWNLOADED_PROVIDER_HASH_MISMATCH'
        result['status'] = 'PROVIDER_BYTES_MATCH_NATIVE_ARCHIVE'
        if is_control:
            result['restored_control_archive'] = str(control_output)
    except Exception as error:
        result['status'] = 'VERIFICATION_FAILURE_PRESERVED'
        result['error_class'] = type(error).__name__
        if isinstance(error, AssertionError):
            result['error_contract'] = str(error)
        if isinstance(error, urllib.error.HTTPError):
            result['HTTP_status'] = error.code
    finally:
        if saved:
            saved.close()
    result['wall_s'] = time.monotonic() - start
    print(json.dumps({key: result[key] for key in ['name', 'status', 'wall_s']}), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('private_links', type=Path)
    parser.add_argument('native_backup_receipt', type=Path)
    parser.add_argument('output_receipt', type=Path)
    parser.add_argument('control_output', type=Path)
    args = parser.parse_args()
    assert not args.output_receipt.exists() and not args.control_output.exists()
    begin, cpu = time.monotonic(), time.process_time()
    entries = json.loads(args.private_links.read_text())['entries']
    source = json.loads(args.native_backup_receipt.read_text())
    expected = {record['archive_name']: record for record in source['archives']}
    assert len(entries) == len(expected) and {x['name'] for x in entries} == set(expected)
    results = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        tasks = [pool.submit(verify, entry, expected[entry['name']], args.control_output)
                 for entry in entries]
        for task in as_completed(tasks):
            results.append(task.result())
    passed = all(r['status'] == 'PROVIDER_BYTES_MATCH_NATIVE_ARCHIVE' for r in results)
    result = {'status': 'PROVIDER_BACKUP_BYTE_VERIFIED' if passed else 'PROVIDER_BACKUP_PARTIAL',
              'archives': sorted(results, key=lambda r: r['name']),
              'native_backup_receipt_sha256': hashlib.sha256(args.native_backup_receipt.read_bytes()).hexdigest(),
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'CPU_s': time.process_time() - cpu, 'wall_s': time.monotonic() - begin,
              'scientific_reexecution': False, 'new_evolution_starts': 0,
              'original_DAG': '10/17', 'expansion_DAG': '28/88'}
    args.output_receipt.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'status': result['status'], 'archives': len(results), 'wall_s': result['wall_s']}))
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
