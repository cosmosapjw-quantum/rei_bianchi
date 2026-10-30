#!/usr/bin/env python3
import hashlib,json,pathlib,sys
R=pathlib.Path(__file__).resolve().parents[1]
m=json.loads((R/'MANIFEST.json').read_text())
for rel,info in m['files'].items():
 p=R/rel
 if not p.is_file():sys.exit(f'FILE_NOT_PRESENT:{rel}')
 v=p.read_bytes()
 if len(v)!=info['bytes'] or hashlib.sha256(v).hexdigest()!=info['sha256']:sys.exit(f'MANIFEST_SHA_MISMATCH:{rel}')
print(f"MANIFEST_PASS {len(m['files'])}/{len(m['files'])} source-inclusive file content SHA256")
