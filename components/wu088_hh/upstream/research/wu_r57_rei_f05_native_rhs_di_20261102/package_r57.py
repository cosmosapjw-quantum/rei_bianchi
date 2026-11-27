#!/usr/bin/env python3
"""WU R57 immutable source-inclusive archive + local Dropbox sync mirror.
Remote provider acknowledgement and cold restore require separate actual checks.
"""
from pathlib import Path
import hashlib,json,zipfile,shutil
ROOT=Path(__file__).resolve().parent
OUT=Path("/home/cosmosapjw/archives/WU_R57_REI_F05_NATIVE_RHS_DI_20261102/WU_R57_REI_F05_NATIVE_RHS_SOURCE_FULL_20261102.zip")
MIRROR=Path("/home/cosmosapjw/Dropbox/WU088_HH_R57_REI_F05_NATIVE_RHS_20261102")/OUT.name
R56=Path("/home/cosmosapjw/archives/WU_R56_REI_F05_ACCEPTED_HISTORY_20261102/WU_R56_FULL_ORIGINAL_SOURCE_20261102.zip")
SOURCE20=Path("/home/cosmosapjw/archives/rei_f05_owner_accepted_trajectory_rhs_20261102/private/ORIGINAL_F05_4EPOCH_46080_26EVENT_RHS.csv.gz")
SOURCE27=ROOT/"source_private/ORIGINAL_F05_4EPOCH_46080_26EVENT_RHS.csv.gz"
FULL=ROOT/"results/R57_ORIGINAL_NATIVE_RHS_HERMITE_DI_46080.csv.gz"
LOCKS={
R56:"8734353648c02d6c0bd0376f6ee7ca64cde7706070ebb71d179278508cc147e4",
SOURCE20:"5a1fe901809c9df2ce2f42aac81583f1021589958ec1799b07bfff6307ee3913",
SOURCE27:"d8d8ce4f3fea820a3b6cfe6bd5d1c4ac48e9f160612cde0ebe00ca04f32af37e",
FULL:"d6c7068ef6b07319a8c7b4715a0c681941d6a2c3dbb068ccceb53e5b98b3100e"}
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def item(z,src,name):
 info=zipfile.ZipInfo(name,date_time=(2026,11,2,0,0,0))
 info.external_attr=0o644<<16
 info.compress_type=zipfile.ZIP_STORED if src.suffix in (".gz",".zip",".npz") else zipfile.ZIP_DEFLATED
 with src.open("rb") as f,z.open(info,"w") as target:shutil.copyfileobj(f,target,1<<20)
 return dict(name=name,size=src.stat().st_size,sha256=sha(src))
def main():
 for path,expected in LOCKS.items():
  if sha(path)!=expected:raise ValueError("IMMUTABLE_PRIVATE_SOURCE_SHA_"+path.name)
 own=sorted(p for p in ROOT.rglob("*") if p.is_file() and
   "__pycache__" not in p.parts and ".pre_cone_repair" not in p.name and
   p.name not in ("package_r57.py","BACKUP_RECEIPT.json") and
   not p.is_relative_to(ROOT/"source_private"))
 own.append(ROOT/"package_r57.py")
 OUT.parent.mkdir(parents=True,exist_ok=True)
 report=[]
 with zipfile.ZipFile(OUT,"w",allowZip64=True,compresslevel=6) as z:
  for f in own: report.append(item(z,f,"R57/"+str(f.relative_to(ROOT))))
  report.append(item(z,R56,"ORIGINAL_R56_FULL/"+R56.name))
  report.append(item(z,SOURCE20,"ORIGINAL_REI367_20_FIELDS/"+SOURCE20.name))
  report.append(item(z,SOURCE27,"R57_ORIGINAL_SOURCE_27_FIELDS/"+SOURCE27.name))
  manifest=zipfile.ZipInfo("SOURCE_CONTENT_MANIFEST.json",date_time=(2026,11,2,0,0,0))
  manifest.compress_type=zipfile.ZIP_DEFLATED
  z.writestr(manifest,json.dumps(report,indent=2,sort_keys=True)+"\n")
 with zipfile.ZipFile(OUT,"r") as z:
  if z.testzip() is not None:raise ValueError("ARCHIVE_MEMBER_CRC")
  if len(z.namelist())!=len(report)+1:raise ValueError("ARCHIVE_ITEM_COUNT")
  for name,expected in (
      ("ORIGINAL_R56_FULL/"+R56.name,LOCKS[R56]),
      ("ORIGINAL_REI367_20_FIELDS/"+SOURCE20.name,LOCKS[SOURCE20]),
      ("R57_ORIGINAL_SOURCE_27_FIELDS/"+SOURCE27.name,LOCKS[SOURCE27])):
   h=hashlib.sha256()
   with z.open(name) as f:
    for block in iter(lambda:f.read(1<<20),b""):h.update(block)
   if h.hexdigest()!=expected:raise ValueError("ARCHIVE_ORIGINAL_BYTE_IDENTITY")
 MIRROR.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(OUT,MIRROR)
 if sha(OUT)!=sha(MIRROR):raise ValueError("DROPBOX_LOCAL_MIRROR_DIFFERENT")
 receipt={
  "schema":"WU_R57_ORIGINAL_SOURCE_INCLUSIVE_BACKUP_RECEIPT_V1",
  "archive":str(OUT),"archive_bytes":OUT.stat().st_size,"archive_sha256":sha(OUT),
  "archive_members":len(report)+1,"archive_zip_crc":"PASS",
  "original_REI367_source_SHA256":LOCKS[SOURCE20],
  "extended_original_REI367_27field_SHA256":LOCKS[SOURCE27],
  "original_R56_full_source_sha256":LOCKS[R56],
  "R57_full_46080_physics_sha256":LOCKS[FULL],
  "local_dropbox_sync_mirror":str(MIRROR),"local_mirror_byte_exact":"PASS",
  "Dropbox_remote_provider_ack":"NOT_VERIFIED",
  "Dropbox_provider_cold_restore":"NOT_RUN",
  "GitHub_source_free_draft":"PENDING",
  "DAG":dict(WU="34/49",REI_central="28/88",REI_working="33/88",FAST="4/7",delta=0),
  "source_owner_modified":False,"original_tick161":"HOLD","production":"HOLD"}
 (ROOT/"BACKUP_RECEIPT.json").write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
 print(json.dumps(receipt,sort_keys=True),flush=True)
if __name__=="__main__":main()
