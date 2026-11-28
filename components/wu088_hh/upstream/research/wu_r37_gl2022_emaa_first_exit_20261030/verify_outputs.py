"""Read immutable R37 generated-output SHA-256 ledger; source truths never rewritten."""
import hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
GIVEN=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'results'
manifest=json.loads((ROOT/'evidence/OUTPUT_SHA256.json').read_text())
for name, metadata in manifest['outputs'].items():
 path=GIVEN/name
 assert path.exists(),f'MISSING {name}'
 data=path.read_bytes()
 got=hashlib.sha256(data).hexdigest()
 assert len(data)==metadata['bytes'] and got==metadata['sha256'],f'MISMATCH {name}: {got}'
 if name.endswith('.csv'):
  assert data.count(b'\n')-1==metadata['rows'],f'ROWCOUNT MISMATCH {name}'
 print('PASS',name,metadata['bytes'],metadata['sha256'])
print('RESULT_SHA256_PASS',len(manifest['outputs']),'/',len(manifest['outputs']))
