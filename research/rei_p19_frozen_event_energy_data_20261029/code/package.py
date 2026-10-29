"""Reproducibly package the local physically scoped source-data deliverable."""
import hashlib,json,zipfile,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'REI_P19_FROZEN_EVENT_ENERGY_DATA_20261029_FULL.zip'

def build():
    src=Path('/mnt/data/REI_SAVED17_UVB_SOURCE_TANGENT_20261029_FULL.zip')
    ref=ROOT/'source_archive/REI_SAVED17_UVB_SOURCE_TANGENT_20261029_FULL.zip'
    ref.parent.mkdir(exist_ok=True,parents=True)
    if not ref.exists():shutil.copyfile(src,ref)
    all_files=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'transfer' not in p.parts and not p.name.endswith('.pyc') and p.name!='MANIFEST.json']
    files={p.relative_to(ROOT).as_posix():dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),size=p.stat().st_size) for p in sorted(all_files)}
    manifest={'schema':'REI_P19_FROZEN_EVENT_ENERGY_DATA_MANIFEST_V1',
              'kind':'source-based physical rate/event diagnostic, not a common REI/P19 solution',
              'parent_archive':dict(path='source_archive/REI_SAVED17_UVB_SOURCE_TANGENT_20261029_FULL.zip',**files['source_archive/REI_SAVED17_UVB_SOURCE_TANGENT_20261029_FULL.zip']),
              'payload':files,'payload_files':len(files),
              'original_dag':'33/88 working,28/88 central,4/7 physical-fast,delta0',
              'new_scoped_data_node':'1/1, not added to canonical DAG',
              'r6_c9':'NOT_RUN', 'no_new_ivp':True}
    (ROOT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    members={**{name:path for name,path in ((k,ROOT/k) for k in files)}, 'MANIFEST.json':ROOT/'MANIFEST.json'}
    with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        for name,p in sorted(members.items()):
            info=zipfile.ZipInfo(name,date_time=(2026,10,29,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o100644<<16)
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=7)
    with zipfile.ZipFile(OUT) as z:
        assert z.testzip() is None
        for name,detail in files.items():
            assert len(z.read(name))==detail['size'] and hashlib.sha256(z.read(name)).hexdigest()==detail['sha256']
    print(json.dumps(dict(archive=str(OUT),bytes=OUT.stat().st_size,sha256=hashlib.sha256(OUT.read_bytes()).hexdigest(),members=len(members),verified_payloads=len(files)),indent=2))
    return OUT
if __name__=='__main__':build()
