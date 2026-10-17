#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
h=json.loads((R/'contracts/FROZEN_OWNER_SHA256.json').read_text())
p=R/'rei_iso_couple_p4_s5/owner_src'
assert len(h)==12
for name,expect in h.items():
    assert hashlib.sha256((p/name).read_bytes()).hexdigest()==expect, name
print('12/12 immutable PR150 owner byte SHA-256 PASS')
