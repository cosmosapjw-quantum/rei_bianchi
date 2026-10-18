#!/usr/bin/env python3
"""Restore nine exact source files, not execute source. Owner files already in Git."""
import base64, hashlib, json, lzma
from pathlib import Path, PurePosixPath
root=Path(__file__).resolve().parent
packed=base64.b64decode((root/'source.xz.b64').read_text(),validate=True)
assert hashlib.sha256(packed).hexdigest()=='48943e5fa0e3259f26ec1d3ff5540e30e3c23d71cd6b3d9d4c9b32c11eba5ba1'
p=json.loads(lzma.decompress(packed,memlimit=268435456))
for name,text in p['files'].items():
 path=PurePosixPath(name)
 assert not path.is_absolute() and '..' not in path.parts
 data=text.encode(); assert hashlib.sha256(data).hexdigest()==p['sha256'][name]
 target=root/name
 if target.exists(): assert target.read_bytes()==data, 'refuse mismatched overwrite: '+name
 else: target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
print('Restored',len(p['files']),'exact files; original two owner files already in Git.')
