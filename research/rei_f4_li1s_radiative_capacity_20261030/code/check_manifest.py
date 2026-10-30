"""Verify all scientific payload hashes, not only ZIP archive CRC."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
M=json.loads((ROOT/'MANIFEST.json').read_text())
for rel,expected in M['members'].items():
    p=ROOT/rel
    if not p.is_file() or p.stat().st_size!=expected['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=expected['sha256']:
        raise RuntimeError('PAYLOAD_SHA_OR_SIZE_MISMATCH:'+rel)
expected=set(M['members'])|{'MANIFEST.json'}
seen={str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'delivery' not in p.parts}
assert seen==expected,(seen-expected,expected-seen)
print('PAYLOAD_SHA_PASS',len(M['members']))
