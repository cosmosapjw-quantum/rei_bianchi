#!/usr/bin/env python3
"""Materialize five pinned NCP07 members for a PHYS14 Git checkout.

The complete Drive/Dropbox PHYS14 snapshot already has these files. This command
only restores verified missing files and refuses to replace different content.
"""
import argparse
import hashlib
import json
import pathlib
import tempfile
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--archive', type=pathlib.Path, required=True)
    p.add_argument('--destination-root', type=pathlib.Path, default=ROOT)
    args = p.parse_args()
    contract = json.loads((ROOT/'INPUT_RESTORE.json').read_text())
    blob = args.archive.read_bytes()
    expected = contract['archive']
    if len(blob) != expected['bytes'] or sha(blob) != expected['sha256']:
        raise ValueError('Pinned archive size/SHA256 mismatch')
    destroot = args.destination_root.resolve()
    destroot.mkdir(parents=True, exist_ok=True)
    ready = []
    with zipfile.ZipFile(args.archive) as z:
        names = z.namelist()
        for row in contract['members']:
            rel = pathlib.PurePosixPath(row['destination_path'])
            if rel.is_absolute() or '..' in rel.parts:
                raise ValueError('Unsafe destination contract')
            dest = (destroot/pathlib.Path(rel)).resolve()
            if not dest.is_relative_to(destroot):
                raise ValueError('Destination escapes root')
            member = row['archive_member']
            if names.count(member) != 1:
                raise ValueError('Missing or ambiguous archive member')
            info = z.getinfo(member)
            if info.is_dir() or info.file_size != row['bytes']:
                raise ValueError('Archive member type/size mismatch')
            data = z.read(member)
            if len(data) != row['bytes'] or sha(data) != row['sha256']:
                raise ValueError('Archive member content mismatch')
            exists = dest.exists()
            if exists and (not dest.is_file() or dest.read_bytes() != data):
                raise ValueError('Existing input differs; no replacement performed: '+str(rel))
            ready.append((row,dest,data,exists))
    # All source members and existing destinations passed before the first write.
    reports=[]
    for row,dest,data,exists in ready:
        if not exists:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=dest.parent,prefix='.phys14-restore-',delete=False) as f:
                tmp=pathlib.Path(f.name)
                f.write(data)
            try:
                # A hard link is a create-only installation, even if another
                # process creates the destination after the initial check.
                dest.hardlink_to(tmp)
            finally:
                tmp.unlink()
        reports.append({'path':row['destination_path'],'bytes':len(data),'sha256':sha(data),
                        'status':'verified_existing' if exists else 'restored_missing'})
    print(json.dumps({'schema':'PHYS14_INPUT_RESTORE_RECEIPT_V1','archive_sha256':expected['sha256'],
                      'destination_root':str(destroot),'files':reports,'scientific_runs':0},indent=2))

if __name__ == '__main__':
    main()
