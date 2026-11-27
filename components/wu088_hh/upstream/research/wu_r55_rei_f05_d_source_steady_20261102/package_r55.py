#!/usr/bin/env python3
"""Deterministic source-inclusive R55 artifact archive and local Dropbox mirror.
Includes byte-exact protected original WU R54 complete ZIP without rewriting its contents.
Local mirror is not an independent remote Dropbox provider acknowledgement.
"""
from __future__ import annotations
import hashlib, json, os, shutil, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
ORIGINAL=Path("/home/cosmosapjw/Dropbox/WU088_HH_R54_REI_F05_DI_4GROUP_20261101/WU_R54_REI_F05_DI_4GROUP_PHOTON_CONSERVING_SOURCE_FULL_20261101.zip")
OUT=Path("/home/cosmosapjw/archives/WU_R55_REI_F05_D_STEADY_IC_20261102/WU_R55_SOURCE_FULL_20261102.zip")
MIRROR=Path("/home/cosmosapjw/Dropbox/WU088_HH_R55_REI_F05_DI_STEADY_20261102/WU_R55_SOURCE_FULL_20261102.zip")
EXPECTED_ORIGINAL="23cbf0b3e91f7e17fc915c06c025a9e55c6aac8b0ebeca6df7039bfe5fbb32ab"
EXPECTED_CSV="e670a9ac41e68596d9007ab33d1ba49404c1fdcd75ed0d668fc545d6af280022"

def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def add_file(z,source,arc):
 st=source.stat()
 info=zipfile.ZipInfo(arc, date_time=(2026,11,2,0,0,0))
 info.compress_type=zipfile.ZIP_STORED if source==ORIGINAL else zipfile.ZIP_DEFLATED
 info.external_attr=0o644<<16
 with source.open("rb") as f,z.open(info,"w") as w:shutil.copyfileobj(f,w,1<<20)
 return {"path":arc,"size":st.st_size,"sha256":sha(source)}

def main():
 assert sha(ORIGINAL)==EXPECTED_ORIGINAL,"SOURCE_R54_ARCHIVE_HAS_CHANGED"
 assert sha(ROOT/"results/R55_REI_F05_INITIAL_DI_PHYSICS_46080.csv.gz")==EXPECTED_CSV
 files=sorted(p for p in ROOT.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.name != "package_r55.py")
 # Include the complete source-inclusive protected R54 ZIP as a single immutable member.
 OUT.parent.mkdir(parents=True,exist_ok=True)
 manifest=[]
 with zipfile.ZipFile(OUT,"w",allowZip64=True,compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in files:manifest.append(add_file(z,p,"R55/"+str(p.relative_to(ROOT))))
  manifest.append(add_file(z,ORIGINAL,"IMMUTABLE_ORIGINAL_R54/"+ORIGINAL.name))
  info=zipfile.ZipInfo("R55_ARCHIVE_CONTENT_MANIFEST.json",date_time=(2026,11,2,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
  z.writestr(info,json.dumps(manifest,sort_keys=True,indent=2)+"\n")
 with zipfile.ZipFile(OUT) as z:
  errors=z.testzip()
  assert errors is None,("R55_ZIP_CRC_ERROR",errors)
  assert len(z.namelist())==len(manifest)+1
  with z.open("IMMUTABLE_ORIGINAL_R54/"+ORIGINAL.name) as f:
   h=hashlib.sha256()
   for b in iter(lambda:f.read(1<<20),b""):h.update(b)
   assert h.hexdigest()==EXPECTED_ORIGINAL
 MIRROR.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(OUT,MIRROR)
 assert sha(OUT)==sha(MIRROR)
 receipt={
  "schema":"WU_R55_LOCAL_SOURCE_FULL_BACKUP_RECEIPT_V1",
  "archive":str(OUT),"archive_size":OUT.stat().st_size,
  "archive_sha256":sha(OUT),
  "zip_members":len(manifest)+1,"zip_crc":"PASS",
  "R54_immutable_original_full_sha256":EXPECTED_ORIGINAL,
  "R55_full_data_sha256":EXPECTED_CSV,
  "local_dropbox_sync_mirror":str(MIRROR),
  "local_dropbox_mirror_byte_identity":"PASS",
  "dropbox_remote_provider_ack":"NOT_VERIFIED",
  "R55_source_free_github_draft_pr":"PENDING",
  "WU_DAG":"34/49","REI_central_DAG":"28/88",
  "original_tick161":"HOLD","original_production":"HOLD",
  "no_source_mutation":True,"no_main_merge":True}
 (ROOT/"BACKUP_RECEIPT.json").write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
 print(json.dumps(receipt,sort_keys=True))
if __name__=="__main__":main()
