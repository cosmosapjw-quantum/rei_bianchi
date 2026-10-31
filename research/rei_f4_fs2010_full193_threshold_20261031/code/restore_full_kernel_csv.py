#!/usr/bin/env python3
"""Reconstitute the original 18,528-row physical CSV byte-exactly from Git-tracked xz.
No external dependencies. Emits an unchanged file only if the original is missing.
"""
from pathlib import Path
import lzma,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'evidence'/'KERNEL_TRANSPORT.json').read_text())
COMP=ROOT/META['git_transport_file']
RAW=ROOT/META['raw_file']
def sha(b):return hashlib.sha256(b).hexdigest()
compressed=COMP.read_bytes()
assert len(compressed)==META['transport_bytes'] and sha(compressed)==META['transport_sha256'],'CORRUPT_TRANSPORT'
data=lzma.decompress(compressed)
assert len(data)==META['raw_bytes'] and sha(data)==META['raw_sha256'],'CORRUPT_RAW'
assert data.count(b'\n')-1==META['rows'],'INCORRECT_ROW_COUNT'
if RAW.is_file():
    assert RAW.read_bytes()==data,'EXISTING_SOURCE_DIFFERS'
else:
    RAW.parent.mkdir(parents=True,exist_ok=True)
    RAW.write_bytes(data)
print('FULL193_KERNEL_RESTORED_BYTE_EXACT',META['rows'],META['raw_sha256'])
