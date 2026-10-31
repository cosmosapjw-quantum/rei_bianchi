from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
man=json.loads((root/'evidence/MANIFEST.json').read_text())
for item in man['files']:
 p=root/item['path']
 assert p.is_file(),('MISSING',item['path'])
 assert p.stat().st_size==item['bytes'],('SIZE',item['path'])
 h=hashlib.sha256(p.read_bytes()).hexdigest()
 assert h==item['sha256'],('SHA',item['path'])
print(f"MANIFEST={len(man['files'])}/{len(man['files'])}_PASS")
