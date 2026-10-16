"""Check archived immutable payload identity before any replay modifies outputs."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
m=json.loads((root/'MANIFEST.json').read_text())
for rel,v in m['files'].items():
    data=(root/rel).read_bytes()
    actual=hashlib.sha256(data).hexdigest()
    if actual!=v['sha256'] or len(data)!=v['bytes']:
        raise SystemExit(f'CHECKSUM_FAILED:{rel}')
print(f"ARCHIVE_PAYLOAD_SHA_PASS files={len(m['files'])}")
