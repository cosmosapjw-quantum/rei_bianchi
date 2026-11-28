import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parent
D=json.loads((BASE/'MANIFEST_SHA256.json').read_text())
for rel,h in D.items():
    fp=BASE/rel
    if not fp.is_file():raise SystemExit(f'MISSING {rel}')
    current=hashlib.sha256(fp.read_bytes()).hexdigest()
    if current!=h:raise SystemExit(f'HASH_FAIL {rel} {current} != {h}')
print('MANIFEST_PASS',len(D),'/',len(D))
