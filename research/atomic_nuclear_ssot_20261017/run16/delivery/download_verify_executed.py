#!/usr/bin/env python3
"""One full GET of each already-uploaded backup, then read-only byte checks."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import platform
import sys
import time
import urllib.request

sys.dont_write_bytecode = True
sys.path.insert(0, '/tmp/rei_run16_repo/research/atomic_nuclear_ssot_20261017/run16/packaging')
from verify_archive import verify

EXPECTED_SHA = 'fd4d51fb205944b35bdc59a452be6d9b4c0c794c14aa9f5da404633cbc990a51'
config_path = Path('/tmp/rei_run16_remote_urls.json')
config_path.chmod(0o600)
configuration = json.loads(config_path.read_text())
root = Path('/tmp/rei_run16_delivery/downloads')
root.mkdir(parents=True, exist_ok=False)

def download(provider):
    item = configuration[provider]
    output = root / provider
    output.mkdir(exist_ok=False)
    path = output / item['filename']
    started = time.perf_counter()
    received = 0
    request = urllib.request.Request(item['url'], method='GET')
    with urllib.request.urlopen(request, timeout=30) as response, path.open('xb') as stream:
        status = response.status
        while True:
            part = response.read(256 * 1024)
            if not part:
                break
            received += len(part)
            if received > item['expected_bytes']:
                raise ValueError('download exceeds expected byte count')
            stream.write(part)
    if received != item['expected_bytes']:
        raise ValueError('download byte count mismatch')
    checked = verify(path, EXPECTED_SHA)
    if provider == 'dropbox':
        block_hashes = []
        with path.open('rb') as stream:
            while True:
                block = stream.read(4 * 1024 * 1024)
                if not block:
                    break
                block_hashes.append(hashlib.sha256(block).digest())
        content_hash = hashlib.sha256(b''.join(block_hashes)).hexdigest()
        if content_hash != item['provider_content_hash']:
            raise ValueError('Dropbox block content hash mismatch')
        checked['provider_content_hash'] = content_hash
        checked['provider_content_hash_verified'] = True
    checked.update({'provider': provider, 'remote_file_id': item['id'],
        'HTTP_GET_status': status, 'full_GET_requests': 1, 'HEAD_requests': 0,
        'download_wall_seconds': time.perf_counter() - started,
        'fresh_scientific_reexecution': False})
    with (output / 'DOWNLOAD_VERIFICATION.json').open('x') as stream:
        json.dump(checked, stream, indent=2, allow_nan=False)
        stream.write('\n')
    return checked

with ThreadPoolExecutor(max_workers=2) as pool:
    results = list(pool.map(download, ['google_drive', 'dropbox']))
receipt = {'schema': 'rei.run16.backup-download-verification.v1',
    'providers': results, 'exact_process_argv': sys.orig_argv,
    'environment': {'python': sys.version, 'platform': platform.platform()},
    'download_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'signed_URLs_omitted_from_durable_receipt': True,
    'scope': 'Upload readback byte/CRC/manifest/mode verification; no scientific recalculation'}
with (root / 'BACKUP_DOWNLOAD_VERIFICATION.json').open('x') as stream:
    json.dump(receipt, stream, indent=2, allow_nan=False)
    stream.write('\n')
print(json.dumps(receipt, indent=2, allow_nan=False))
