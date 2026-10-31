#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1]
man=json.loads((root/'evidence/MANIFEST.json').read_text())
expected={r['path']:r for r in man['files']}
actual={p.relative_to(root).as_posix():p for p in root.rglob('*') if p.is_file() and p.name!='MANIFEST.json' and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts}
if set(actual)!=set(expected):raise AssertionError(('FILE_SET',sorted(set(actual)-set(expected)),sorted(set(expected)-set(actual))))
for name,path in actual.items():
 r=expected[name];assert path.stat().st_size==r['bytes'],('SIZE',name)
 assert hashlib.sha256(path.read_bytes()).hexdigest()==r['sha256'],('SHA256',name)
print(f"MANIFEST_VERIFIED {len(actual)}/{len(actual)}")
