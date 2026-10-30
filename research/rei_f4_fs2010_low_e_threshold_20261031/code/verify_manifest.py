from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
M=json.loads((ROOT/'MANIFEST.json').read_text());assert M['schema']=='REI_F4_FS2010_SOURCE_INCLUSIVE_V1'
for row in M['entries']:
 p=ROOT/row['path'];assert p.exists() and p.stat().st_size==row['bytes']
 with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['sha256'],row['path']
print('MANIFEST_PASS',len(M['entries']))
