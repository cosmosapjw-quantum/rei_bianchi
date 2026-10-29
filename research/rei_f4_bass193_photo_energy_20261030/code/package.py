"""Deterministic source-inclusive ZIP; original donor source ZIP remains byte-identical."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[1]
OUT=R.parent/'REI_F4_BASS193_PHOTO_ENERGY_LEDGER_20261030_FULL.zip'
files=[]
for p in sorted(R.rglob('*')):
    if not p.is_file():continue
    rel=p.relative_to(R)
    if (rel.parts[0] in ('donor','__pycache__') or '__pycache__' in rel.parts or str(rel)=='MANIFEST.json' or p.suffix=='.pyc'):
        continue
    files.append({'path':str(rel),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
manifest={'schema':'REI_F4_BASS193_PHOTO_ENERGY_MANIFEST_V1','files':files,'count':len(files)}
(R/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
    for e in files:
        z.write(R/e['path'],arcname='rei_f4_bass193_photo_energy_20261030/'+e['path'])
    z.write(R/'MANIFEST.json',arcname='rei_f4_bass193_photo_energy_20261030/MANIFEST.json')
with zipfile.ZipFile(OUT) as z:
    assert z.testzip() is None
    for e in files:
        assert hashlib.sha256(z.read('rei_f4_bass193_photo_energy_20261030/'+e['path'])).hexdigest()==e['sha256']
print(json.dumps({'archive':str(OUT),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'bytes':OUT.stat().st_size,'members':len(files)+1,'payload_sha_pass':len(files),'crc':'PASS'}))
