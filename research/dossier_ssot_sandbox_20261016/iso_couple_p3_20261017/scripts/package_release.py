#!/usr/bin/env python3
"""Deterministic sha manifest and restorable public/full ZIPs for ISO-COUPLE-P3."""
from pathlib import Path
import hashlib,json,shutil,zipfile,os
ROOT=Path(__file__).resolve().parents[1]
DEST=Path('/mnt/data/REI_ISO_COUPLE_P3_20261017')
SOURCE='REI_ISO_COUPLE_P3_20261017'
STAGING=Path('/mnt/data/rei_iso_p3_work/pkg_p3')
if STAGING.exists():shutil.rmtree(STAGING)
STAGING.mkdir(parents=True)
for typ in ('PUBLIC','FULL'):
 stage=STAGING/typ/SOURCE
 for sub in ('contracts','docs','evidence','scripts'):
  shutil.copytree(ROOT/sub,stage/sub)
 shutil.copytree(ROOT/'rust/rei_iso_couple_p3',stage/'rust/rei_iso_couple_p3',ignore=shutil.ignore_patterns('target','*.o','*.rlib','*.rmeta','*.d','.git'))
 shutil.copy2(ROOT/'README_KO.md',stage/'README_KO.md')
 if typ=='FULL':
  (stage/'inputs').mkdir()
  shutil.copy2('/mnt/data/REI_ISO_COUPLE_P2_20261017_FULL.zip',stage/'inputs/REI_ISO_COUPLE_P2_20261017_FULL.zip')
 # explicit binary-independent manifest
 paths=sorted(p for p in stage.rglob('*') if p.is_file())
 manifest={p.relative_to(stage).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in paths}
 (stage/'PAYLOAD_MANIFEST.json').write_text(json.dumps({'schema':'rei.iso.p3.payload.sha256.1','type':typ,'files':manifest},ensure_ascii=False,indent=2)+'\n')
 output=DEST.parent/f'{SOURCE}_{typ}.zip'
 with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(stage.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(stage.parent).as_posix())
 with zipfile.ZipFile(output) as z:
  assert z.testzip() is None
  assert len(z.namelist())==len(manifest)+1
 print(typ,output,output.stat().st_size,hashlib.sha256(output.read_bytes()).hexdigest(),'payload_files',len(manifest))
 report=DEST.parent/'REI_ISO_COUPLE_P3_20261017_PACKAGE_META.json'
 if report.exists():m=json.loads(report.read_text())
 else:m={}
 m[typ]={'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'bytes':output.stat().st_size,'payload_files':len(manifest),'local_verified_crc':True}
 report.write_text(json.dumps(m,indent=2)+'\n')
