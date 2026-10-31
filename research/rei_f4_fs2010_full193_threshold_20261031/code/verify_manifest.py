from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1]
files=json.loads((root/'MANIFEST.json').read_text())
assert files['schema']=='REI_F4_FS2010_FULL193_SOURCE_INCLUSIVE_V1'
for row in files['entries']:
 p=root/row['path']; assert p.is_file() and p.stat().st_size==row['bytes'],row['path']
 with p.open('rb') as f: assert hashlib.file_digest(f,'sha256').hexdigest()==row['sha256'],row['path']
print('SOURCE_INCLUSIVE_MANIFEST_PASS',len(files['entries']))
