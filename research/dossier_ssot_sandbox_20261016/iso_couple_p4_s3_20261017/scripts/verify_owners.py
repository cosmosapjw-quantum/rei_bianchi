from pathlib import Path
import json,hashlib,subprocess
R=Path(__file__).resolve().parents[1]
manifest=json.loads((R/'contracts/FROZEN_OWNER_SHA256.json').read_text())
p=R/'rei_iso_couple_p4_s3/owner_src'
assert len(manifest)==12, len(manifest)
for name,expected in manifest.items():
    assert hashlib.sha256((p/name).read_bytes()).hexdigest()==expected,name
print('12/12 frozen PR150 original owner byte SHA-256 PASS')
