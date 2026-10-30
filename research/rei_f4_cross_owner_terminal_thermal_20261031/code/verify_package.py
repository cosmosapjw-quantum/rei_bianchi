"""Deterministic exact-source and same-environment artifact verification."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def check(kind):
 data=json.loads((R/('MANIFEST.json' if kind=='manifest' else 'OUTPUT_SHA256.json')).read_text())
 entries=data['files']
 count=0
 for f,d in entries.items():
  p=R/f
  assert p.is_file(),f'MISSING:{f}'
  assert p.stat().st_size==d['size'],f'SIZE:{f}'
  assert sha(p)==d['sha256'],f'SHA256:{f}'
  count+=1
 print(f'{kind.upper()}_VERIFIED={count}/{len(entries)}')
if __name__=='__main__':
 if len(sys.argv)!=2 or sys.argv[1] not in ('manifest','outputs'):raise SystemExit('usage: verify_package.py manifest|outputs')
 check(sys.argv[1])
