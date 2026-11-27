#!/usr/bin/env python3
"""Manifest identity of original source+paper and generated artifact bytes.
Optional baseline SHA validation; has no authority to certify physical truth.
"""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
x=json.loads((ROOT/'MANIFEST_SHA256.json').read_text())
for name,expected in x['files'].items():
    actual=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    if actual!=expected:raise RuntimeError(f'MANIFEST_FAIL:{name} expected={expected} actual={actual}')
print('MANIFEST_SHA256',len(x['files']),'/',len(x['files']),'PASS')