#!/usr/bin/env python3
"""Validate exact master archive payload bytes (not physics truth)."""
from pathlib import Path
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[1]
M=json.loads((ROOT/'MANIFEST.json').read_text())
assert M['schema']=='REI_F4_PHYSFAST_MASTER_SHA256_V1'
for row in M['entries']:
    f=ROOT/row['path'];assert f.is_file(),row['path']
    b=f.read_bytes()
    assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],row['path']
    if row['path'].startswith('source/') and row['path'].endswith('.zip'):
        with zipfile.ZipFile(f) as z:assert z.testzip() is None,row['path']
print(f"PASS manifest {len(M['entries'])}/{len(M['entries'])} byte and CRC source guard")
