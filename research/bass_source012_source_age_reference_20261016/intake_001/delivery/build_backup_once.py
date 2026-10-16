#!/usr/bin/python3
"""Create and verify one private recovery archive from the frozen published selection."""
import hashlib
import json
import subprocess
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path('/home/cosmosapjw/Dropbox/bianchi/rei_bianchi')
CONTENT = '2c6a16f1b37412c822c8b63db5ed35416bd385ff'
ACQUISITION = 'eb2abcac4f44b7bc4ff532286953fcb4e353c7bb'
SUPPLIER = '553ce556d9f8662290c000ec675c7e6007c9d895'
NATIVE = '35d9747a0bbedcafdb568467ce7c1e7a25f965b6'
SELPATH = 'research/bass_source012_source_age_reference_20261016/intake_001/PUBLIC_SELECTION.json'
PRIVATE = Path('/home/cosmosapjw/REI_PRIVATE_SOURCE012_INPUTS_20261016')
ARCHIVE = Path('/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/REI_SOURCE012_INPUT_INTAKE_REFRESH005_20261016_v1.zip')
MAX_ARCHIVE = 32 * 1024 * 1024
t0 = time.monotonic()
git_calls = []

def sha(data): return hashlib.sha256(data).hexdigest()

def git_show(path):
    argv = ['git', 'show', f'{CONTENT}:{path}']
    p = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    git_calls.append({'path': path, 'exit_code': p.returncode, 'bytes': len(p.stdout), 'stderr': p.stderr.decode('utf-8', 'replace')[:300]})
    if p.returncode:
        raise RuntimeError(f'git show failed for {path}: {p.returncode}')
    return p.stdout

def main():
    if ARCHIVE.exists(): raise RuntimeError('create-only archive destination already exists')
    selection = json.loads(git_show(SELPATH))
    if selection.get('entry_count') != 40: raise RuntimeError('published selection count mismatch')
    selected = selection['entries']
    public_members = []
    for item in selected:
        path = item['path']; data = git_show(path)
        if len(data) != item['size_bytes'] or sha(data) != item['sha256']:
            raise RuntimeError(f'published selection mismatch: {path}')
        public_members.append({'archive_path': path, 'source_path': path, 'source_commit': CONTENT, 'size_bytes': len(data), 'sha256': sha(data), 'data': data})
    # The selection manifest is included as its own explicit member; it is excluded
    # from its own listed-hash set by design.
    selection_bytes = git_show(SELPATH)
    public_members.append({'archive_path': SELPATH, 'source_path': SELPATH, 'source_commit': CONTENT, 'size_bytes': len(selection_bytes), 'sha256': sha(selection_bytes), 'data': selection_bytes})
    private_files = sorted(p for p in PRIVATE.rglob('*') if p.is_file())
    if len(private_files) != 409: raise RuntimeError(f'private file count mismatch: {len(private_files)}')
    private_members = []
    for p in private_files:
        rel = p.relative_to(PRIVATE).as_posix()
        data = p.read_bytes()
        private_members.append({'archive_path': f'private/source012/{rel}', 'source_path': str(p), 'size_bytes': len(data), 'sha256': sha(data), 'data': data})
    private_bytes = sum(x['size_bytes'] for x in private_members)
    if private_bytes != 7396570: raise RuntimeError(f'private payload byte mismatch: {private_bytes}')
    entries = public_members + private_members
    manifest = {
        'schema': 'rei.source012_refresh005.backup_manifest.v1',
        'source_content_commit': CONTENT,
        'acquisition_base': ACQUISITION,
        'supplier_commit': SUPPLIER,
        'native_base_source_pin': NATIVE,
        'publication_status': {'push_exit_code': 0, 'remote_content_commit': CONTENT, 'draft_pr': 150},
        'public_selection_source': SELPATH,
        'public_selection_count': len(selected),
        'public_selection_self_member_included': True,
        'private_source_root': str(PRIVATE),
        'private_file_count': len(private_members),
        'private_bytes': private_bytes,
        'private_status': 'partial SOURCE012 capture; two static dependencies remain HOLD because bounded git pack mapping failed; no retry',
        'entries': [{k: v for k, v in x.items() if k != 'data'} for x in entries],
        'git_show_calls': git_calls,
        'manifest_self_hash_excluded': True,
    }
    mdata = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True).encode() + b'\n'
    entries.append({'archive_path': 'BACKUP_MANIFEST.json', 'source_path': 'generated during packaging', 'size_bytes': len(mdata), 'sha256': sha(mdata), 'data': mdata})
    # Create-only local ZIP; one verification pass checks CRC and every member SHA.
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ARCHIVE, mode='x', compression=zipfile.ZIP_DEFLATED, compresslevel=6, strict_timestamps=False) as zf:
        for e in entries:
            zf.writestr(e['archive_path'], e['data'])
    if ARCHIVE.stat().st_size > MAX_ARCHIVE: raise RuntimeError(f'archive exceeds 32 MiB: {ARCHIVE.stat().st_size}')
    with zipfile.ZipFile(ARCHIVE, 'r') as zf:
        bad = zf.testzip()
        if bad: raise RuntimeError(f'CRC failure: {bad}')
        names = zf.namelist()
        if len(names) != len(entries): raise RuntimeError('archive member count mismatch')
        for e in entries:
            blob = zf.read(e['archive_path'])
            if len(blob) != e['size_bytes'] or sha(blob) != e['sha256']:
                raise RuntimeError(f'archive member SHA mismatch: {e["archive_path"]}')
    receipt = {
        'status': 'LOCAL_ARCHIVE_CREATED_AND_VERIFIED',
        'archive': str(ARCHIVE),
        'archive_bytes': ARCHIVE.stat().st_size,
        'archive_sha256': sha(ARCHIVE.read_bytes()),
        'archive_member_count': len(entries),
        'public_selection_members_including_self': len(public_members),
        'private_member_count': len(private_members),
        'private_bytes': private_bytes,
        'git_show_call_count': len(git_calls),
        'wall_seconds': round(time.monotonic()-t0, 6),
        'archive_cap_bytes': MAX_ARCHIVE,
        'crc_and_member_sha_verification': 'PASS_ONCE',
    }
    print(json.dumps(receipt, sort_keys=True))
    return 0

if __name__ == '__main__':
    try: sys.exit(main())
    except Exception as e:
        print('BACKUP_FATAL: '+repr(e), file=sys.stderr)
        sys.exit(2)
