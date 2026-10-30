from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1]
m=json.loads((root/'MANIFEST.json').read_text())
for n,expect in m['files'].items():
 p=root/n
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expect:raise SystemExit('MANIFEST_SHA_FAIL:'+n)
found={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name!='MANIFEST.json' and '__pycache__' not in p.parts}
assert found==set(m['files']),str(found^set(m['files']))
print(f'MANIFEST_PASS={len(found)}/{len(found)}')
