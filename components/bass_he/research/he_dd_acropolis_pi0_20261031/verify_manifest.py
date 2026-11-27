"""Verify SHA-256 of exact pinned sources/code/data in the archive; not a scientific truth checker."""
import json,hashlib,sys
from pathlib import Path
root=Path(__file__).resolve().parent
m=json.loads((root/'MANIFEST_SHA256.json').read_text())
errors=[]
for rel,expected in m.items():
 p=root/rel
 if not p.is_file():errors.append((rel,'MISSING'));continue
 got=hashlib.sha256(p.read_bytes()).hexdigest()
 if got!=expected:errors.append((rel,got))
print('MANIFEST',len(m)-len(errors),'/',len(m),'PASS' if not errors else 'FAIL')
if errors:print(errors[:15]);sys.exit(1)
