"""Deterministic minimal payload manifest and source-inclusive ZIP."""
import hashlib,json,zipfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/mnt/data/REI_F4_LI1S_RADIATIVE_PHOTON_20261030_FULL.zip')

def hash_file(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='MANIFEST.json' and 'delivery' not in p.parts)
def build():
    manifest={'schema':'REI_SOURCE_INCLUSIVE_MANIFEST_V1','root':ROOT.name,'members':{str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':hash_file(p)} for p in files()}}
    (ROOT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(files()+[ROOT/'MANIFEST.json']):
            info=zipfile.ZipInfo(f'{ROOT.name}/{p.relative_to(ROOT)}',date_time=(2026,10,30,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o644 << 16)
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(OUT) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(manifest['members'])+1
    print('ZIP',OUT,'bytes',OUT.stat().st_size,'sha256',hash_file(OUT),'payload',len(manifest['members']))
if __name__=='__main__':build()
