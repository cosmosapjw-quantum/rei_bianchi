"""Reproducible public/private science packs from audited sandbox snapshot."""
from __future__ import annotations
import os, json, hashlib, zipfile
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
DIST=Path('/mnt/data')
INCLUDED_PREFIXES=('docs/','contracts/','rust/rei_ssot_reference/src/','scripts/')
INCLUDED_FILES={'README_KO.md','REIONIZATION_DOSSIER_V2_20261016.pdf','rust/rei_ssot_reference/Cargo.toml','rust/rei_ssot_reference/Cargo.lock'}
EVIDENCE={'evidence/CONTRACT_VALIDATION.json','evidence/CARGO_TEST_FINAL.stdout','evidence/CARGO_TEST_FINAL.stderr','evidence/CARGO_FMT_FINAL.stdout','evidence/CARGO_FMT_FINAL.stderr','evidence/CARGO_CLIPPY_FINAL.stdout','evidence/CARGO_CLIPPY_FINAL.stderr','evidence/STAGE1_RUN_RECEIPT.json'}

def included(private:bool):
    res=[]
    for p in ROOT.rglob('*'):
        if not p.is_file():continue
        rel=p.relative_to(ROOT).as_posix()
        if rel.startswith('rust/') and '/target/' in rel:continue
        if '__pycache__' in rel or rel.endswith('.pyc'):continue
        if rel.startswith('evidence/') and rel not in EVIDENCE:continue
        if rel.startswith('inputs/') and not private:continue
        if rel.startswith(INCLUDED_PREFIXES) or rel in INCLUDED_FILES or rel in EVIDENCE or (private and rel.startswith('inputs/')):res.append((rel,p))
    return sorted(res)

def main():
  for private in [False,True]:
    files=included(private)
    manifest={'schema':'rei.ssot.package.v1','created_utc':'2026-10-16T00:00:00Z','variant':'PRIVATE_FULL' if private else 'PUBLIC_DERIVATIVE','scientific_claim':'SCOPED_REFERENCE_ONLY_NOT_NATIVE_EOR','files':{r:{'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for r,p in files}}
    payload=json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True).encode()+b'\n'
    fn=DIST/f'REI_DOSSIER_SSOT_V2_20261016_{"PRIVATE_FULL" if private else "PUBLIC"}.zip'
    with zipfile.ZipFile(fn,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
      for rel,p in files:
        info=zipfile.ZipInfo(rel,(2026,10,16,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o644<<16; z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=8)
      info=zipfile.ZipInfo('PACKAGE_MANIFEST.json',(2026,10,16,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,payload)
    with zipfile.ZipFile(fn) as z:
      assert z.testzip() is None
      assert set(z.namelist())==set(manifest['files'])|{'PACKAGE_MANIFEST.json'}
      for r,entry in manifest['files'].items():assert hashlib.sha256(z.read(r)).hexdigest()==entry['sha256']
    print(json.dumps({'name':fn.name,'sha256':hashlib.sha256(fn.read_bytes()).hexdigest(),'size_bytes':fn.stat().st_size,'members':len(files)+1,'verified':True,'private':private},ensure_ascii=False))

if __name__=='__main__': main()