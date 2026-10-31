#!/usr/bin/env python3
"""Restore four original computed CSVs byte-exact from committed XZ transports."""
from pathlib import Path
import hashlib,json,lzma
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'evidence/CSV_TRANSPORT.json').read_text())
for name,entry in manifest.items():
    xz=root/(name+'.xz')
    c=xz.read_bytes()
    assert len(c)==entry['xz_bytes'] and hashlib.sha256(c).hexdigest()==entry['xz_sha256'],('XZ SHA',name)
    data=lzma.decompress(c)
    assert len(data)==entry['raw_bytes'] and hashlib.sha256(data).hexdigest()==entry['raw_sha256'],('RAW SHA',name)
    out=root/name;out.write_bytes(data)
    print('RESTORED',name,entry['raw_bytes'])
