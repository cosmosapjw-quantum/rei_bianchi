#!/usr/bin/env python3
"""Only validates sealed workspace manifest; no network, no science dispatch."""
import hashlib,json,pathlib,sys
root=pathlib.Path(__file__).resolve().parent
manifest=json.loads((root/'FILE_MANIFEST.json').read_text(encoding='utf-8'))
entries=manifest['payloads']
for rel,d in entries.items():
    p=root/rel
    if pathlib.Path(rel).is_absolute() or '..' in pathlib.Path(rel).parts or not p.is_file():
        raise SystemExit('PATH_INVALID '+rel)
    b=p.read_bytes()
    if len(b)!=d['size'] or hashlib.sha256(b).hexdigest()!=d['sha256']:
        raise SystemExit('CONTENT_MISMATCH '+rel)
actual={str(x.relative_to(root)) for x in root.rglob('*') if x.is_file() and x.name not in {'FILE_MANIFEST.json'} and not str(x.relative_to(root)).startswith('__pycache__')}
if actual!=set(entries):
    raise SystemExit('FILE_SET_MISMATCH new='+str(sorted(actual-set(entries)))+' missing='+str(sorted(set(entries)-actual)))
print('VERIFY_DELIVERY_PASS',len(entries),'files')
