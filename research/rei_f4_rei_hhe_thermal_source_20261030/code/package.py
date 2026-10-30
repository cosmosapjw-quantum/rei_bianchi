#!/usr/bin/env python3
"""Immutable, deterministic source-inclusive ZIP and SHA256 ledger."""
import hashlib,json,pathlib,zipfile,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
O=pathlib.Path('/mnt/data/REI_F4_REI_HHE_THERMAL_SOURCE_20261030_FULL.zip')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload():
    for x in sorted(ROOT.rglob('*')):
        if not x.is_file():continue
        n=x.relative_to(ROOT).as_posix()
        if '/__pycache__/' in '/'+n or n.endswith('.pyc'):continue
        if n in {'MANIFEST.json','OUTPUT_SHA256.json'}:continue
        yield n,x
if __name__=='__main__':
    outputs={n:digest(p) for n,p in payload() if n.startswith('results/')}
    (ROOT/'OUTPUT_SHA256.json').write_text(json.dumps({'schema':'REI_F4_PHYSFAST_OUTPUT_ID_V1','sha256':outputs},indent=2)+'\n')
    manifest={n:digest(p) for n,p in payload()}
    manifest['OUTPUT_SHA256.json']=digest(ROOT/'OUTPUT_SHA256.json')
    (ROOT/'MANIFEST.json').write_text(json.dumps({'schema':'REI_F4_PHYSFAST_MANIFEST_V1','sha256':dict(sorted(manifest.items()))},indent=2)+'\n')
    with zipfile.ZipFile(O,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for n,p in sorted(list(payload())+[('OUTPUT_SHA256.json',ROOT/'OUTPUT_SHA256.json'),('MANIFEST.json',ROOT/'MANIFEST.json')]):
            info=zipfile.ZipInfo('REI_F4_REI_HHE_THERMAL_SOURCE_20261030/'+n,date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644 << 16
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
    with zipfile.ZipFile(O) as z:
        if z.testzip() is not None:raise ValueError('ZIP_CRC')
        print('MANIFEST_FILES',len(manifest),'ZIP_ENTRIES',len(z.infolist()))
    print('MASTER_BYTES',O.stat().st_size,'MASTER_SHA256',digest(O))
