#!/usr/bin/env python3
"""Mechanical archive and member-byte verification; never imports science code."""
import hashlib
import json
import tarfile
from pathlib import Path

TASK = Path(__file__).resolve().parent
SOURCE = Path('/tmp/HE-E13C5-full-first2-20261011/research/e13c5_full_first2_20261011')
BACKUP = Path('/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/CR_PHYS03_20261010_RECOVERY')
ARCHIVE = BACKUP / 'BASS_HE_E13C5_FULL_FIRST2_REVIEWED_20261011.tar.gz'

def sha(stream):
    h = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        h.update(block)
    return h.hexdigest()

pins = json.loads((SOURCE / 'runs/EXEC01/START.json').read_text())['hashes']
files = {Path(p) for p in pins}
files.update(p for p in TASK.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
cover = SOURCE.parent / 'e13c5_first2_branch_cover_20261011'
files.update(p for p in cover.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
expected = {}
for p in sorted(files):
    with p.open('rb') as f:
        expected[str(p).lstrip('/')] = sha(f)
    if str(p) in pins:
        assert expected[str(p).lstrip('/')] == pins[str(p)], str(p)
assert (TASK / 'runs/EXEC01/PATHS.jsonl').stat().st_size == 292932850
assert expected[str(TASK / 'runs/EXEC01/PATHS.jsonl').lstrip('/')] == '175d8aa96d50965127ac61840991fc69e348e1acbb21e21cfed5eb7947441c94'
assert expected[str(TASK / 'runs/EXEC01/RESULTS.json').lstrip('/')] == '29dfaa5408cee99ccbefd25039f42bec80fec8268784cb81fa50920ce3449271'
assert not ARCHIVE.exists(), 'Do not overwrite a recovery package'
with tarfile.open(ARCHIVE, 'x:gz') as tar:
    for p in sorted(files):
        tar.add(p, arcname=str(p).lstrip('/'), recursive=False)
with tarfile.open(ARCHIVE, 'r:gz') as tar:
    actual = {}
    for member in tar:
        assert member.isfile()
        with tar.extractfile(member) as f:
            actual[member.name] = sha(f)
assert actual == expected
with ARCHIVE.open('rb') as f:
    archive_hash = sha(f)
receipt = {
    'archive': str(ARCHIVE), 'archive_sha256': archive_hash,
    'archive_bytes': ARCHIVE.stat().st_size,
    'member_count': len(expected), 'members_sha256': expected,
    'member_byte_verification': 'PASS', 'pinned_inputs': 23,
    'PATHS_bytes': 292932850, 'scientific_runs': 0,
    'publication': 'PENDING', 'backup_receipt_location': 'Compact Git task directory; receipt generated after archive verification'
}
(TASK / 'RECOVERY_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({k:v for k,v in receipt.items() if k != 'members_sha256'}))
