"""Verify published data/science/source identity, not the truth of its physical hypotheses."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parents[2]
manifest=Path(__file__).resolve().parent/'MANIFEST_SHA256.json'
d=json.loads(manifest.read_text())
errors=[]
for rel,sha in d.items():
  p=root/rel # full ZIP-root workdir
  if not p.exists():errors.append(f'NOT_FOUND {rel}');continue
  observed=hashlib.sha256(p.read_bytes()).hexdigest()
  if observed!=sha:errors.append(f'MISMATCH {rel} {observed}')
print('FILE_MANIFEST',len(d)-len(errors),'/',len(d),'PASS' if not errors else 'FAIL')
for e in errors:print(e)
sys.exit(1 if errors else 0)
