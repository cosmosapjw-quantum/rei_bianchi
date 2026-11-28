"""Restore byte-pinned native inputs from the immutable archival package only.

No code from the archive is executed; physics, manifests, and input bytes are
not rewritten. Existing mismatches stop instead of being overwritten.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import tarfile
import tempfile

ARCHIVE_SHA='a70d320c7ead5f1fd93170c18f1f80ae5eb58a293a6045a0f728bb7ae2743205'
PREFIX='BASS_HE_HE29_RESUME_COMPLETE_20261018/research/he29_survival_budget_20261018/'
ROOT=Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def expected(root):
    result=json.loads((Path(root)/'provenance/INPUT_SHA256.json').read_text())
    if len(result)!=22:raise ValueError('HE29_INPUT_MANIFEST_COUNT')
    for name in result:
        path=PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or not name.startswith('inputs/'):
            raise ValueError('HE29_INPUT_MANIFEST_PATH')
    return result


def verify(root=ROOT):
    root=Path(root);items=expected(root)
    for name,sha in items.items():
        p=root/name
        if not p.is_file() or p.is_symlink() or digest(p.read_bytes())!=sha:
            raise ValueError('HE29_EXISTING_INPUT_MISMATCH: '+name)
    return len(items)


def restore(archive,root=ROOT):
    root=Path(root);archive=Path(archive)
    if digest(archive.read_bytes())!=ARCHIVE_SHA:raise ValueError('HE29_ARCHIVE_SHA')
    items=expected(root);payload={}
    with tarfile.open(archive,'r:gz') as tar:
        for member in tar:
            if not member.name.startswith(PREFIX):continue
            name=member.name[len(PREFIX):]
            if name not in items:continue
            if not member.isfile() or name in payload:raise ValueError('HE29_ARCHIVE_MEMBER')
            data=tar.extractfile(member).read()
            if digest(data)!=items[name]:raise ValueError('HE29_ARCHIVE_INPUT_SHA: '+name)
            payload[name]=data
    if set(payload)!=set(items):raise ValueError('HE29_ARCHIVE_INPUT_MISSING')
    # Check every pre-existing path before any write. Data is small and pinned.
    for name,data in payload.items():
        p=root/name
        if p.is_symlink() or (p.exists() and (not p.is_file() or p.read_bytes()!=data)):
            raise ValueError('HE29_EXISTING_INPUT_MISMATCH: '+name)
    for name,data in payload.items():
        p=root/name
        if p.exists():continue
        p.parent.mkdir(parents=True,exist_ok=True)
        fd,tmp=tempfile.mkstemp(prefix='.he29-input-',dir=p.parent)
        try:
            with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
            os.link(tmp,p)
        finally:Path(tmp).unlink(missing_ok=True)
    return verify(root)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--archive');ap.add_argument('--root',default=str(ROOT));a=ap.parse_args()
    count=restore(a.archive,a.root) if a.archive else verify(a.root)
    print('HE29 byte-verified native inputs:',count)
