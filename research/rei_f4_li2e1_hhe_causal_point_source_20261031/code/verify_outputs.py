from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
rows=json.loads((ROOT/'evidence'/'OUTPUT_SHA256.json').read_text())
for nm,a in rows.items():
 p=ROOT/'results'/nm
 assert p.exists() and p.stat().st_size==a['bytes'] and digest(p)==a['sha256'],nm
print('DETERMINISTIC_OUTPUT_PASS',len(rows))
