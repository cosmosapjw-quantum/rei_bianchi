from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
ZIP=ROOT.parent/'REI_P19_FROZEN_PROPER_TIME_EXPOSURE_20261030_FULL.zip'

def sha(d):return hashlib.sha256(d).hexdigest()
def build():
    entries={}
    for f in ROOT.rglob('*'):
        if not f.is_file() or '__pycache__' in f.parts or f.suffix in ('.pyc',):continue
        name=f.relative_to(ROOT).as_posix()
        if name in ('MANIFEST.json','results/PACKAGE_LOCAL_RECEIPT.json'):continue
        data=f.read_bytes()
        entries[name]={'bytes':len(data),'sha256':sha(data)}
    manifest={'schema':'REI_P19_FROZEN_EXPOSURE_MASTER_MANIFEST_V1','unit':'REI_P19_FROZEN_PROPER_TIME_EXPOSURE_20261030',
      'source_type':'snapshot-derived conditional exposure, not IVP/observational tau','parent_PR271_sha256':'c20b7a776e407c35dff99c32595f394ce0c9426c3469358a8b5d7f2750c68165',
      'members':entries,'member_sha_verified':len(entries),'unrun':['actual independent other-author R6/C9','physical coupled REI/P19 trajectory','Thomson tau & CMB','production']}
    (ROOT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    items=sorted(entries)+['MANIFEST.json']
    with zipfile.ZipFile(ZIP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as out:
        for name in items:
            info=zipfile.ZipInfo(name,(2020,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644<<16
            out.writestr(info,(ROOT/name).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(ZIP) as z:
        assert z.testzip() is None
        for name,d in entries.items():assert sha(z.read(name))==d['sha256']
        assert len(z.namelist())==len(entries)+1
    return {'path':str(ZIP),'bytes':ZIP.stat().st_size,'sha256':sha(ZIP.read_bytes()),'members':len(items),'payloads_checked':len(entries)}
if __name__=='__main__':print(json.dumps(build(),indent=2))
