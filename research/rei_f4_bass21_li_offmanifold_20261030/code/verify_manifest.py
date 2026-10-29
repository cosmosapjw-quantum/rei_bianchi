"""Verify the immutable self-contained F4 archive contents, not theorem truth."""
import json,hashlib,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
man=json.loads((root/'MANIFEST.json').read_text())
for it in man['files']:
    path=root/it['path']
    if not path.is_file() or path.stat().st_size!=it['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest()!=it['sha256']:
        raise RuntimeError('MANIFEST_MISMATCH '+it['path'])
extra={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='MANIFEST.json'}-set(it['path'] for it in man['files'])
if extra: raise RuntimeError('UNDECLARED_FILES '+str(extra))
print('MANIFEST %d/%d PASS'%(len(man['files']),len(man['files'])))
