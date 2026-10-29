from pathlib import Path
import json,hashlib,sys
root=Path(__file__).resolve().parents[1]
m=json.loads((root/'MANIFEST.json').read_text())
for name,identity in m['files'].items():
 f=root/name
 if not f.is_file():raise FileNotFoundError(name)
 if len(f.read_bytes())!=identity['bytes'] or hashlib.sha256(f.read_bytes()).hexdigest()!=identity['sha256']:
  raise AssertionError('SOURCE_PAYLOAD_CHANGED:'+name)
print(f'MANIFEST {len(m["files"])}/{len(m["files"])} PASS')
