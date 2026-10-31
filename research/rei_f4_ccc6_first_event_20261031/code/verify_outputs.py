from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
ref=json.loads((ROOT/'evidence/OUTPUT_SHA256.json').read_text())
for name,sha in ref.items():
    p=ROOT/name
    if not p.is_file():raise FileNotFoundError(p)
    got=hashlib.sha256(p.read_bytes()).hexdigest()
    if sha!=got:raise AssertionError((name,sha,got))
print('OUTPUT_SHA256_PASS',len(ref))
