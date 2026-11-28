#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parent
manifest=json.loads((root/'MANIFEST_SHA256.json').read_text())
for rel,sha in manifest.items():
    f=root/rel
    assert f.is_file(),('MISSING',rel)
    digest=hashlib.sha256(f.read_bytes()).hexdigest()
    assert digest==sha,('SHA256_MISMATCH',rel,digest,sha)
print('MANIFEST_PASS',len(manifest))
