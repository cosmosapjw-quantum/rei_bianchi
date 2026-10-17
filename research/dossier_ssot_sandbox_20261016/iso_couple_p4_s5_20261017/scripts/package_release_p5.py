#!/usr/bin/env python3
"""Stable source archive with SHA-256 payload manifest; never packages target/reproduced."""
from pathlib import Path
import hashlib,zipfile
R=Path(__file__).resolve().parents[1]
archive=R.parent/(R.name+'_FULL.zip')
items=sorted(p for p in R.rglob('*') if p.is_file() and not p.relative_to(R).parts[0] in ('reproduced','target') and p.name!='manifest.sha256')
lines=[hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(R).as_posix() for p in items]
(R/'manifest.sha256').write_text('\n'.join(lines)+'\n')
allfiles=items+[R/'manifest.sha256']
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(allfiles):
        name=R.name+'/'+p.relative_to(R).as_posix()
        info=zipfile.ZipInfo(name,date_time=(2026,10,17,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o644<<16)
        z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(allfiles)
sha=hashlib.sha256(archive.read_bytes()).hexdigest()
(archive.parent/(archive.name+'.sha256')).write_text(sha+'  '+archive.name+'\n')
print('ARCHIVE',archive.name,'bytes',archive.stat().st_size,'files',len(allfiles),'payload_hashes',len(items),'sha256',sha)
