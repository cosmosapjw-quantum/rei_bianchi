#!/usr/bin/env python3
"""Restore exact P8 sources from immutable P6 tree plus the committed delta.
No network calls, no source execution. Refuse mismatched inputs and overwrite.
"""
from __future__ import annotations
import argparse, base64, hashlib, json, lzma, shutil
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent

def digest(data: bytes) -> str: return hashlib.sha256(data).hexdigest()

def safe(name: str) -> Path:
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or not p.parts: raise ValueError('unsafe path')
    return Path(*p.parts)

def restore(base: Path, out: Path) -> dict:
    identity=json.loads((HERE/'PACKET_IDENTITY.json').read_text())
    packed=base64.b64decode(''.join((HERE/f'source_delta.part{i}').read_text().strip() for i in range(3)),validate=True)
    if digest(packed)!=identity['lzma_payload_sha256']: raise ValueError('compressed delta mismatch')
    data=lzma.decompress(packed,memlimit=268435456)
    if digest(data)!=identity['packet_json_sha256']:raise ValueError('decoded delta mismatch')
    p=json.loads(data)
    if out.exists():raise ValueError('output exists; choose a new output directory')
    for name,sha in p['base_sha256'].items():
        if digest((base/safe(name)).read_bytes())!=sha:raise ValueError('base mismatch: '+name)
    out.mkdir(parents=True)
    # Copy only manifest source files, never a target directory, secret or VCS data.
    for name in p['base_sha256']:
        q=out/safe(name);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(base/safe(name),q)
    for name,text in p['replacements_and_additions'].items():
        q=out/safe(name);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(text.encode('utf-8'))
    actual={q.relative_to(out).as_posix():digest(q.read_bytes()) for q in out.rglob('*') if q.is_file()}
    if actual!=p['complete_crate_sha256']:raise ValueError('restored crate manifest mismatch')
    return {'status':'EXACT_COMPLETE_CRATE_RESTORED','files':len(actual),'output':str(out),'base_commit':p['base_commit']}

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--base',type=Path,required=True);a.add_argument('--out',type=Path,required=True);v=a.parse_args()
    print(json.dumps(restore(v.base,v.out),indent=2))
