"""Validate the sealed package bytes; not a scientific test."""
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parent
manifest=json.loads((root/'MANIFEST.json').read_text())
bad=[]
for name,item in manifest['files'].items():
    p=root/name
    if not p.is_file():
        bad.append(name+': missing')
        continue
    raw=p.read_bytes()
    if len(raw)!=item['bytes'] or hashlib.sha256(raw).hexdigest()!=item['sha256']:
        bad.append(name+': identity mismatch')
if bad:
    raise SystemExit('\n'.join(bad))
print(json.dumps({'manifest_payloads_checked':len(manifest['files']),
                  'byte_identity_verified':True,'scientific_validation':False}))
