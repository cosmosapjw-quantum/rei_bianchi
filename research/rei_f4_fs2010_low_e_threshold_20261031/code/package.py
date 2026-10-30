#!/usr/bin/env python3
"""Durable private source-inclusive proof/data packet with byte-locked originals."""
from pathlib import Path
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/(ROOT.name+'_FULL.zip')

def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def records(paths):return [{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]

def filtered():
 return sorted([p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.name not in ('MANIFEST.json','OUTPUT_SHA256.json')],key=lambda p:p.relative_to(ROOT).as_posix())
if __name__=='__main__':
 outputs=sorted([p for p in (ROOT/'results').rglob('*') if p.is_file() and p.suffix in ('.csv','.json','.png')],key=lambda p:p.as_posix())
 (ROOT/'evidence'/'OUTPUT_SHA256.json').write_text(json.dumps({'schema':'REI_F4_FS2010_LOW_E_OUTPUT_SHA256','outputs':records(outputs)},indent=2,sort_keys=True)+'\n')
 allp=filtered();allp.append(ROOT/'evidence'/'OUTPUT_SHA256.json')
 allp.sort(key=lambda p:p.relative_to(ROOT).as_posix())
 man={'schema':'REI_F4_FS2010_SOURCE_INCLUSIVE_V1','entries':records(allp)}
 (ROOT/'MANIFEST.json').write_text(json.dumps(man,indent=2,sort_keys=True)+'\n')
 with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in allp+[ROOT/'MANIFEST.json']:
   arc=ROOT.name+'/'+p.relative_to(ROOT).as_posix()
   info=zipfile.ZipInfo(arc,date_time=(2026,10,31,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o100644<<16)
   z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
 with zipfile.ZipFile(OUT) as z:assert z.testzip() is None
 print(json.dumps({'archive':str(OUT),'bytes':OUT.stat().st_size,'sha256':sha(OUT),'manifest_entries':len(allp),'zip_members':len(allp)+1,'result_outputs':len(outputs)},indent=2))
