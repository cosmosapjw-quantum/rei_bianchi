from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parents[1]
m=json.loads((p/'MANIFEST.json').read_text())
for name,expected in m['files'].items():
 f=p/name
 if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=expected:raise SystemExit('SHA_FAIL:'+name)
found={x.relative_to(p).as_posix() for x in p.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x.name!='MANIFEST.json'}
if found!=set(m['files']):raise SystemExit('MISSING_OR_EXTRA:'+str(found^set(m['files'])))
print('MANIFEST_PASS=%d/%d' %(len(found),len(found)))
