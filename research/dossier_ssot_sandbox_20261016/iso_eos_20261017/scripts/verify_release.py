#!/usr/bin/env python3
"""Checks manifest bytes, loaded node/source contracts and test evidence classification."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'contracts/MANIFEST_SHA256.json').read_text())
for item in manifest['files']:
    p=root/item['path']; b=p.read_bytes()
    assert len(b)==item['size_bytes'],str(p)
    assert hashlib.sha256(b).hexdigest()==item['sha256'],str(p)
progress=json.loads((root/'contracts/DAG_PROGRESS.json').read_text())
contract=json.loads((root/'contracts/ISO_EOS_CONTRACT.json').read_text())
assert progress['node']=='ISO-EOS'
assert progress['ISO-COUPLE'].startswith('HOLD')
assert contract['stoichiometric_cx']['change']==[0,1,-1,-1,1,0,0,0,0,0,0,0,0]
print(f'RELEASE_MANIFEST_PASS files={len(manifest["files"])}; ISO_COUPLE=HOLD')
