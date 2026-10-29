"""Byte manifest checker; data science/verification are separate from hash checks."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'MANIFEST.json'
obj=json.loads(p.read_text())
for name,expect in obj['sha256'].items():
 f=ROOT/name
 if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=expect:
  raise SystemExit('BAD_PAYLOAD_SHA '+name)
print(f'MANIFEST {len(obj["sha256"])}/{len(obj["sha256"])} PASS')
