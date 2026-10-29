"""Deterministic archive of already completed no-IVP research and original bytes."""
from __future__ import annotations
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'REI_F4_BASS193_LI_CHARGE_JETS_20261030_FULL.zip'

def create():
    members=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name!='MANIFEST.json' and '__pycache__' not in p.parts and p.suffix!='.pyc')
    payload={str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in members}
    (ROOT/'MANIFEST.json').write_text(json.dumps({'schema':'REI_F4_LI_JETS_SOURCE_ARCHIVE_MANIFEST_V1','sha256':{n:v['sha256'] for n,v in payload.items()},'bytes':{n:v['bytes'] for n,v in payload.items()}},ensure_ascii=False,indent=2)+'\n')
    all_files=members+[ROOT/'MANIFEST.json']
    with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
     for p in all_files:
      rel=str(p.relative_to(ROOT));info=zipfile.ZipInfo('rei_f4_bass193_li_charge_jets_20261030/'+rel,date_time=(2026,10,30,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
      info.external_attr=((0o100755 if rel=='VERIFY.sh' else 0o100644)<<16)
      z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
    with zipfile.ZipFile(OUT) as z:assert z.testzip() is None
    return dict(zip=OUT.name,zip_bytes=OUT.stat().st_size,zip_sha256=hashlib.sha256(OUT.read_bytes()).hexdigest(),members=len(all_files),hashes=len(payload),manifest_sha256=hashlib.sha256((ROOT/'MANIFEST.json').read_bytes()).hexdigest())
if __name__=='__main__':print(json.dumps(create(),indent=2))
