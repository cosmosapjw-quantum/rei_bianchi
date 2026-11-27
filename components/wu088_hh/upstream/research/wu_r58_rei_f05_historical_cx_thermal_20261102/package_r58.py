#!/usr/bin/env python3
"""WU R58 small incremental source-linked ZIP and verified local Dropbox mirror.

Parent immutable WU R57 192MB source-inclusive archive already cold-restored
at Dropbox; DO NOT duplicate it while physical host disk is nearly full.
This R58 ZIP contains new 46080 real physical rows + code and original 47 Savin
rate pairs, but complete reproduction also needs exact parent referenced below.
"""
from pathlib import Path
import hashlib,json,zipfile,shutil
ROOT=Path(__file__).resolve().parent
OUT=Path("/home/cosmosapjw/archives/WU_R58_REI_F05_CX_HISTORY_THERMAL_20261102/WU_R58_INCREMENTAL_SOURCE_LINKED_20261102.zip")
MIRROR=Path("/home/cosmosapjw/Dropbox/WU088_HH_R58_CX_HISTORY_20261102")/OUT.name
SAVIN=Path("/home/cosmosapjw/research_backups/WU088_HH/R54_REI_F05_DI_GROUP_PHOTON_DEBIT_20261101/source_inputs/SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv")
REI367_AGGREGATE=Path("/home/cosmosapjw/worktrees/rei-f05-owner-accepted-trajectory-rhs-20261102/research/rei_f05_owner_accepted_trajectory_rhs_20261102/results/ORIGINAL_F05_4EPOCH_RHS_SCIENCE.json")
R57_PARENT=Path("/home/cosmosapjw/archives/WU_R57_REI_F05_NATIVE_RHS_DI_20261102/WU_R57_REI_F05_NATIVE_RHS_SOURCE_FULL_20261102.zip")
SAVIN_SHA="ba98ec463903f3589c6c68cd7d9e3b3bc637188bb5d25616addb2fb71ab689e8"
R57_SHA="ad3d9c99d14cfbd4d729c691d8766705812ff936cf15081a5870061f807d02ea"
PHYSICS_SHA="fee16aef885556d87fde68af3f30c64edd703f000ed4c86a9db3861a5edeb205"

def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def put(z,p,arc):
 info=zipfile.ZipInfo(arc,date_time=(2026,11,2,0,0,0))
 info.external_attr=0o644<<16
 info.compress_type=zipfile.ZIP_STORED if p.suffix in (".gz",".zip") else zipfile.ZIP_DEFLATED
 with p.open("rb") as src,z.open(info,"w") as dst:
  shutil.copyfileobj(src,dst,1<<20)
 return dict(file=arc,size=p.stat().st_size,sha256=sha(p))

def main():
 if sha(SAVIN)!=SAVIN_SHA or sha(R57_PARENT)!=R57_SHA or sha(ROOT/"results/R58_REI_F05_46080_HISTORY_CX_ENERGY.csv.gz")!=PHYSICS_SHA:
  raise ValueError("IMMUTABLE_SOURCE_SHAS_OR_R58_PHYSICS_CHANGED")
 included=sorted(f for f in ROOT.rglob("*") if f.is_file() and "__pycache__" not in f.parts and f.name not in ("package_r58.py","BACKUP_RECEIPT.json") and ".tmp" not in f.name)
 included.append(ROOT/"package_r58.py")
 OUT.parent.mkdir(parents=True,exist_ok=True)
 manifest=[]
 with zipfile.ZipFile(OUT,"w",allowZip64=True,compresslevel=6) as z:
  for p in included:manifest.append(put(z,p,"R58/"+str(p.relative_to(ROOT))))
  manifest.append(put(z,SAVIN,"PRIMARY_SAVIN47/"+SAVIN.name))
  manifest.append(put(z,REI367_AGGREGATE,"ORIGINAL_REI367_AGGREGATE/"+REI367_AGGREGATE.name))
  contract={
   "required_parent_source_full_archive":"WU_R57_REI_F05_NATIVE_RHS_SOURCE_FULL_20261102.zip",
   "required_parent_sha256":R57_SHA,
   "original_parent_remote_provider_id":"id:BSpOijBcT10AAAAAAEHcbg",
   "parent_source_complete":True,
   "R58_incremental_archive_is_not_independently_source_complete":True,
   "original_REI367_184320_RHS_SHA256":"5a1fe901809c9df2ce2f42aac81583f1021589958ec1799b07bfff6307ee3913",
   "original_REC195_184320_HHe_SHA256":"6674ca16ebb40607a47bed9f2eb32ed587f6a770b20bb1af6b3a988ff510259c",
   "original_WU_R57_DI_46080_SHA256":"d6c7068ef6b07319a8c7b4715a0c681941d6a2c3dbb068ccceb53e5b98b3100e",
   "SAVIN47_table_sha256":SAVIN_SHA,
   "contained_sources_manifest":manifest}
  info=zipfile.ZipInfo("INCREMENTAL_BACKUP_SOURCE_CONTRACT.json",date_time=(2026,11,2,0,0,0))
  info.compress_type=zipfile.ZIP_DEFLATED
  z.writestr(info,json.dumps(contract,sort_keys=True,indent=2)+"\n")
 with zipfile.ZipFile(OUT) as z:
  if z.testzip() is not None or len(z.namelist())!=len(manifest)+1:
   raise ValueError("ZIP_CRC_OR_MISSING_ITEM")
  with z.open("PRIMARY_SAVIN47/"+SAVIN.name) as f:
   if hashlib.sha256(f.read()).hexdigest()!=SAVIN_SHA:raise ValueError("ORIGINAL_MICROSCOPIC_SOURCE_CORRUPT")
 MIRROR.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(OUT,MIRROR)
 if sha(OUT)!=sha(MIRROR):raise ValueError("LOCAL_MIRROR_BYTES_CHANGED")
 result={
  "schema":"WU_R58_INCREMENTAL_SOURCE_LINKED_ARCHIVE_RECEIPT_V1",
  "archive_path":str(OUT),"archive_size":OUT.stat().st_size,
  "archive_sha256":sha(OUT),"zip_members":len(manifest)+1,"zip_crc":"PASS",
  "incomplete_without_parent_R57_source":True,
  "original_parent_complete_sha256":R57_SHA,
  "original_parent_Dropbox_id":"id:BSpOijBcT10AAAAAAEHcbg",
  "new_46080_cell_data_SHA256":PHYSICS_SHA,
  "original_Savin47_SHA256":SAVIN_SHA,
  "local_Dropbox_sync_path":str(MIRROR),"local_mirror_byte_identity":"PASS",
  "Dropbox_remote_ack":"NOT_VERIFIED","Dropbox_provider_cold_restore":"NOT_RUN",
  "GitHub_Draft_PR":"PENDING",
  "DAG":dict(WU="34/49",REI="28/88",working="33/88",fast="4/7",canonical_delta=0),
  "official_REI_tick161":"HOLD","production":"HOLD","owner_source_unchanged":True}
 (ROOT/"BACKUP_RECEIPT.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
 print(json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
