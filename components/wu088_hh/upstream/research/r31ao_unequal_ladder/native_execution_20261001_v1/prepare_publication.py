"""Create an additive Git payload and package-only inventory from this snapshot.

The output payload belongs outside the source snapshot. Actual publication must
recheck the branch head and verify old/new entries against the remote tree.
"""
import argparse
import hashlib
import json
from pathlib import Path

ALLOWED_TEXT = {'.py', '.cpp', '.hpp', '.h', '.f90', '.c', '.json', '.md', '.sql', '.txt'}
MAX_TEXT_BYTES = 131072


def hash_file(data):
    return hashlib.sha256(data).hexdigest()


def blob_hash(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def prepare(root, repository, output):
    root, repository, output = root.resolve(), repository.resolve(), output.resolve()
    inventory = root / 'PUBLICATION_CONTENTS.json'
    if inventory.exists() or output.exists() or output.is_relative_to(repository):
        raise ValueError('create-only inventory and external payload required')
    entries, rows = [], []
    for path in sorted(root.rglob('*')):
        if not path.is_file() or any(x in path.parts for x in ('__pycache__', '.pytest_cache')) or path.suffix in ('.pyc', '.pyo'):
            continue
        if path.is_symlink():
            raise ValueError('publication source symlinks require an explicit policy')
        data = path.read_bytes()
        selected = path.suffix in ALLOWED_TEXT and len(data) <= MAX_TEXT_BYTES
        try:
            text = data.decode('utf-8') if selected else None
        except UnicodeDecodeError:
            selected, text = False, None
        relative = path.relative_to(repository).as_posix()
        row = {'path': relative, 'bytes': len(data), 'sha256': hash_file(data),
               'destination': 'GIT_AND_PACKAGE' if selected else 'PACKAGE_ONLY'}
        if selected:
            row['git_blob_sha1'] = blob_hash(data)
            entries.append({'path': relative, 'mode': '100644', 'type': 'blob', 'content': text})
        rows.append(row)
    document = {'schema': 'WU088_ADDITIVE_PUBLICATION_CONTENTS_V1',
                'base_commit': json.loads((root / 'SCOPE.json').read_text())['base_commit'],
                'selection': 'UTF-8 source/docs/JSON/SQL/TXT, each <=131072 bytes; generated inventory is the sole exception with a 1048576-byte cap; remaining payloads in delivery ZIP',
                'inventory_excludes_itself': True, 'full_remote_mirror': False,
                'git_selected_files_excluding_inventory': len(entries),
                'files': rows}
    data = (json.dumps(document, indent=2, sort_keys=True) + '\n').encode()
    if len(data) > 1048576:
        raise ValueError('generated inventory exceeds its explicit publication cap')
    inventory.write_bytes(data)
    entries.append({'path': inventory.relative_to(repository).as_posix(), 'mode': '100644',
                    'type': 'blob', 'content': data.decode()})
    output.write_text(json.dumps(entries, ensure_ascii=False, separators=(',', ':')))
    return {'selected_files': len(entries), 'all_snapshot_files_excluding_inventory': len(rows),
            'payload_bytes': output.stat().st_size, 'payload_sha256': hash_file(output.read_bytes())}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(Path(__file__).parent, args.repository, args.output), indent=2))
