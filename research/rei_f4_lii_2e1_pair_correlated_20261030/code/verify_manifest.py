from pathlib import Path
import json,hashlib
p=Path(__file__).resolve().parents[1]
m=json.loads((p/'MANIFEST.json').read_text())
for name,expected in m['files'].items():
    path=p/name
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
        raise SystemExit('MANIFEST_FAIL: '+name)
found={x.relative_to(p).as_posix() for x in p.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x.name!='MANIFEST.json'}
if found!=set(m['files']):
    raise SystemExit('MANIFEST_MISSING_EXTRA: '+str((found^set(m['files']))))
print(f'MANIFEST_PASS={len(found)}/{len(found)}')
