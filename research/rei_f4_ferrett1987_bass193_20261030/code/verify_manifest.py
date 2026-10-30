#!/usr/bin/env python3
import hashlib,json,pathlib,sys
r=pathlib.Path(__file__).resolve().parents[1]
manifest=json.loads((r/'MANIFEST.json').read_text())
assert manifest['schema']=='REI_F4_FERRETT1987_SOURCE_MANIFEST_V1'
for entry in manifest['files']:
 f=r/entry['path']
 if not f.is_file():raise SystemExit(f'MISSING:{entry["path"]}')
 data=f.read_bytes()
 if len(data)!=entry['bytes'] or hashlib.sha256(data).hexdigest()!=entry['sha256']:
  raise SystemExit('BYTE_MISMATCH:'+entry['path'])
print(f'MANIFEST_SHA {len(manifest["files"])}/{len(manifest["files"])} PASS')
