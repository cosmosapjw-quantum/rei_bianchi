from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
ref=json.loads((ROOT/'evidence/OUTPUT_SHA256.json').read_text())
for name,want in ref.items():
 p=ROOT/name
 assert p.is_file(),f'output missing: {name}'
 got=hashlib.sha256(p.read_bytes()).hexdigest()
 assert got==want,(name,want,got)
print('OUTPUT_REPLAY=%d/%d_EXACT' %(len(ref),len(ref)))
