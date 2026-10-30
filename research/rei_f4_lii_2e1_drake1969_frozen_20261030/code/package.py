#!/usr/bin/env python3
"""Source-inclusive research ZIP with minimal sha256 index; not production promotion."""
import pathlib,hashlib,zipfile,json
R=pathlib.Path(__file__).resolve().parents[1]
NAME='REI_F4_LII_2E1_SOURCE_SPECTRAL_ABSORPTION_20261030_FULL.zip'
exclude={'MANIFEST.json'}
entries={str(p.relative_to(R)):p for p in R.rglob('*') if p.is_file() and p.name not in exclude and '__pycache__' not in p.parts and not p.name.endswith('.pyc') and not p.name.endswith('.zip.part')}
manifest={'schema':'REI_2E1_CONTENT_MANIFEST_V1','source':'original PR282 plus frozen-data code and plots','files':{n:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for n,p in sorted(entries.items())}}
(R/'MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
entries['MANIFEST.json']=R/'MANIFEST.json'
out=R.parent/NAME
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for rel,p in sorted(entries.items()): z.write(p,arcname='REI_F4_LII_2E1_SOURCE_SPECTRAL_ABSORPTION_20261030/'+rel)
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
print(json.dumps({'zip':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'files':len(entries)},indent=2))
