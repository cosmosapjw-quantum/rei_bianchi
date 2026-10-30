from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
man=json.loads((ROOT/'MANIFEST.json').read_text());assert man['schema']=='REI_F4_20261031_SHA256_SOURCE_INCLUSIVE_MANIFEST_V1'
for a in man['entries']:
 p=ROOT/a['name'];assert p.exists() and p.stat().st_size==a['bytes'] and digest(p)==a['sha256'],a['name']
print('MANIFEST_PASS',len(man['entries']))
