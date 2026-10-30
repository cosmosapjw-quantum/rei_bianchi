#!/usr/bin/env python3
from pathlib import Path
import zipfile,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'REI_F4_FERRETT_DIRECT_R31_R32_20261030_FULL.zip'
FILES=sorted([p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in str(p) and p.suffix!='.pyc' and p.name!='MANIFEST.json'])
man={'schema':'REI_F4_FERRETT_DIRECT_R31_R32_SHA256_MANIFEST_V1','files':[]}
for p in FILES:
    b=p.read_bytes()
    man['files'].append({'path':p.relative_to(ROOT).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(ROOT/'MANIFEST.json').write_text(json.dumps(man,indent=2,sort_keys=True)+'\n')
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in FILES+[ROOT/'MANIFEST.json']:
        # Dates, names stable to support deterministic source archive identity.
        f=zipfile.ZipInfo((ROOT.name+'/'+p.relative_to(ROOT).as_posix()),date_time=(2026,10,30,0,0,0))
        f.compress_type=zipfile.ZIP_DEFLATED
        f.external_attr=(0o100644<<16)
        z.writestr(f,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
with zipfile.ZipFile(OUT) as z:
    assert z.testzip() is None
print(json.dumps({'master_zip':str(OUT),'bytes':OUT.stat().st_size,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'manifest_payload_files':len(FILES),'archive_members':len(FILES)+1},indent=2))
