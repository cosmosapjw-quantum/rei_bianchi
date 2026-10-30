#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,zipfile
root=Path(__file__).resolve().parents[1]
files=[f for f in root.rglob('*') if f.is_file() and f.relative_to(root).parts[0] not in ('delivery',) and f.name!='MANIFEST.json' and '__pycache__' not in str(f)]
files=sorted(files,key=lambda f:str(f.relative_to(root)))
manifest={'schema':'REI_F4_FERRETT1987_SOURCE_MANIFEST_V1','files':[{'path':f.relative_to(root).as_posix(),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files]}
(root/'MANIFEST.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
full=root.parent/'REI_F4_FERRETT1987_BASS193_20261030_FULL.zip'
with zipfile.ZipFile(full,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in files+[root/'MANIFEST.json']:
  info=zipfile.ZipInfo('REI_F4_FERRETT1987_BASS193_20261030/'+f.relative_to(root).as_posix(),date_time=(2026,10,30,20,0,0))
  info.compress_type=zipfile.ZIP_DEFLATED
  z.writestr(info,f.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
with zipfile.ZipFile(full) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(files)+1
print('ARCHIVE',full,'BYTES',full.stat().st_size,'SHA256',hashlib.sha256(full.read_bytes()).hexdigest(),'MANIFEST',len(files))
