#!/usr/bin/env python3
from pathlib import Path
import json, hashlib, zipfile
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((ROOT/'MANIFEST.json').read_text())
for rec in m['files']:
    p=ROOT/rec['path']
    assert p.exists() and p.is_file(),rec
    assert p.stat().st_size==rec['bytes'],rec
    assert sha(p)==rec['sha256'],rec
assert len(m['files'])>=35
assert sha(ROOT/'source/PR289_full_source.zip')=='f5fa78b9087a60051bb7161d69ada6019f42cfa093674a2fc07c7ed9cc7cdd4f'
assert sha(ROOT/'source/Ferrett1987_LBL22068_user_source.pdf')=='7fbabb1fe8c77a2fb561c7900e198f40f4c16125dd12ac3d08505b997a93b6a9'
with zipfile.ZipFile(ROOT/'source/PR289_full_source.zip') as z:
    assert z.testzip() is None
print('MANIFEST',len(m['files']),'/',len(m['files']),'PASS; original PDF/source SHA PASS; nested ZIP CRC PASS')
