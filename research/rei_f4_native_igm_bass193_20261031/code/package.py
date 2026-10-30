"""Deterministic byte-identical source-inclusive archive; no published third-party PDFs in Git."""
from pathlib import Path
import hashlib,zipfile
ROOT=Path(__file__).resolve().parents[1]
NAME='REI_F4_NATIVE_REI_IGM193_20261031'
OUT=Path('/mnt/data')/(NAME+'_FULL.zip')
files=sorted([p for p in ROOT.rglob('*') if p.is_file() and p.name not in {'LOCAL_VERIFY.out','package.py'}])
# package itself included by separate explicit member
files += [Path(__file__)]
files=sorted(files)
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:
  info=zipfile.ZipInfo(NAME+'/'+p.relative_to(ROOT).as_posix(),date_time=(2026,10,31,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o644<<16)
  z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
with zipfile.ZipFile(OUT) as z:assert z.testzip() is None
sha=hashlib.sha256(OUT.read_bytes()).hexdigest()
print(f'zip={OUT}\nbytes={OUT.stat().st_size}\nSHA256={sha}\nfiles={len(files)}')
