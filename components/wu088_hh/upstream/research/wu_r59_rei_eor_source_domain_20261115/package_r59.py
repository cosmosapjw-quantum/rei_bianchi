#!/usr/bin/env python3
"""WU R59 compact source-linked ZIP; parent complete WU R57 archive is required.

No mutation to protected source. Verification distinguishes source archive,
Dropbox local mirror, remote provider metadata, and independent cold restore.
"""
from pathlib import Path
import hashlib,json,zipfile,shutil
ROOT=Path(__file__).resolve().parent
ZIP=Path("/home/cosmosapjw/archives/WU_R59_REI_EOR_DOMAIN_20261115/WU_R59_REI_EOR_SOURCE_LINKED_20261115.zip")
MIRROR=Path("/home/cosmosapjw/Dropbox/WU088_HH_R59_EOR_DOMAIN_20261115")/ZIP.name
PARENT=Path("/home/cosmosapjw/Dropbox/WU088_HH_R57_REI_F05_NATIVE_RHS_20261102/WU_R57_REI_F05_NATIVE_RHS_SOURCE_FULL_20261102.zip")
PARENT_SHA="ad3d9c99d14cfbd4d729c691d8766705812ff936cf15081a5870061f807d02ea"
SOURCES=[
(Path("/home/cosmosapjw/research_backups/WU088_HH/R57_REI_F05_NATIVE_RHS_DI_HISTORY_20261102/source_private/ORIGINAL_F05_4EPOCH_46080_26EVENT_RHS.csv.gz"),
 "F05_ORIGINAL_NATIVE_HHE/ORIGINAL_F05_4EPOCH_46080_26EVENT_RHS.csv.gz",
 "d8d8ce4f3fea820a3b6cfe6bd5d1c4ac48e9f160612cde0ebe00ca04f32af37e"),
(Path("/home/cosmosapjw/research_backups/WU088_HH/R54_REI_F05_DI_GROUP_PHOTON_DEBIT_20261101/source_inputs/canonical_time_resolved_forcing_nodes.csv"),
 "F05_PHOTON_17/canonical_time_resolved_forcing_nodes.csv",
 "9b33a16956d30d96576e7e189ab11ad67321fd6d2872b8ad68058f7aac3b5268"),
(Path("/home/cosmosapjw/research_backups/WU088_HH/R54_REI_F05_DI_GROUP_PHOTON_DEBIT_20261101/source_inputs/initial_material_state_z6.npz"),
 "F05_INITIAL_MATERIAL/initial_material_state_z6.npz",
 "7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d"),
(Path("/home/cosmosapjw/worktrees/bass-f08-source-support-20261115/research/bass_rei_f08_s0_continuous_native_20261102/results/SOURCE_LOCKED_REI_S0_CONTINUOUS_NATIVE_HHE_TRAJECTORY.csv.gz"),
 "F08_GAS_PHOTONS/SOURCE_LOCKED_REI_S0_CONTINUOUS_NATIVE_HHE_TRAJECTORY.csv.gz",
 "75a8e6b0f63db0f9972c15fc2e9580261574ac87f70167ab3343d667094e9843"),
]
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def put(z,src,arc):
    i=zipfile.ZipInfo(arc,date_time=(2026,11,15,0,0,0))
    i.external_attr=0o644<<16
    i.compress_type=zipfile.ZIP_STORED if src.suffix in (".gz",".npz",".zip") else zipfile.ZIP_DEFLATED
    with src.open("rb") as f,z.open(i,"w") as w:shutil.copyfileobj(f,w,1<<20)
    return {"archive_member":arc,"size_bytes":src.stat().st_size,"sha256":sha(src)}
def run():
    if sha(PARENT)!=PARENT_SHA:raise ValueError("REQUIRED_PARENT_R57_FULL_SOURCE_SHA_CHANGED")
    for p,arc,h in SOURCES:
        if sha(p)!=h:raise ValueError("SOURCE_SHA_CHANGED_"+arc)
    result=json.loads((ROOT/"results/R59_RESULTS.json").read_text())
    full=ROOT/"results"/result["files"]["46080_real_source_cells"]
    if sha(full)!=result["files"]["sha256"]:raise ValueError("R59_FULL_PHYSICAL_SOURCE_SHA")
    items=sorted(p for p in ROOT.rglob("*") if p.is_file() and "__pycache__" not in p.parts
                 and p.name not in ("package_r59.py","BACKUP_RECEIPT.json") and ".tmp" not in p.name)
    items.append(ROOT/"package_r59.py")
    ZIP.parent.mkdir(parents=True,exist_ok=True)
    manifest=[]
    with zipfile.ZipFile(ZIP,"w",allowZip64=True,compresslevel=6) as z:
        for p in items: manifest.append(put(z,p,"R59/"+str(p.relative_to(ROOT))))
        for p,arc,h in SOURCES:manifest.append(put(z,p,"SOURCES/"+arc))
        record={
            "schema":"WU_R59_IMMUTABLE_SOURCE_DEPENDENCY_V1",
            "source_inclusive_parent_required":True,
            "parent_source_zip_sha256":PARENT_SHA,
            "parent_Dropbox_provider_id":"id:BSpOijBcT10AAAAAAEHcbg",
            "original_REI_F05_184320_native_RHS_SHA256":
                "d8d8ce4f3fea820a3b6cfe6bd5d1c4ac48e9f160612cde0ebe00ca04f32af37e",
            "R59_replay_all_required_data_files_embedded":True,
            "original_REI_26event_reexecution_still_requires_upstream_parent_and_worker":True,
            "files":manifest,
            "new_WU_canonical_delta":0
        }
        i=zipfile.ZipInfo("SOURCE_AND_SHA256_MANIFEST.json",date_time=(2026,11,15,0,0,0))
        i.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(i,json.dumps(record,indent=2,sort_keys=True)+"\n")
    with zipfile.ZipFile(ZIP,"r") as z:
        if z.testzip() is not None or len(z.namelist())!=len(manifest)+1:raise ValueError("ZIP_CRC_MISMATCH")
        for p,arc,h in SOURCES:
            with z.open("SOURCES/"+arc) as reader:
                hnew=hashlib.sha256()
                for b in iter(lambda:reader.read(1<<20),b""):hnew.update(b)
                if hnew.hexdigest()!=h:raise ValueError("ZIP_SOURCE_MEMBER_SHA_"+arc)
    MIRROR.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ZIP,MIRROR)
    if sha(ZIP)!=sha(MIRROR):raise ValueError("LOCAL_DROPBOX_MIRROR_SHA")
    receipt={
        "schema":"WU_R59_SOURCE_LINKED_INCREMENTAL_BACKUP_RECEIPT_V1",
        "archive_path":str(ZIP),"archive_size_bytes":ZIP.stat().st_size,
        "archive_sha256":sha(ZIP),"zip_members":len(manifest)+1,"zip_crc":"PASS",
        "parent_source_complete_archive_sha256":PARENT_SHA,
        "parent_provider_id":"id:BSpOijBcT10AAAAAAEHcbg",
        "this_archive_embeds_all_R59_direct_physical_data_sources":True,
        "original_source_owner_Rei26event_replay_requires_R57_parent":True,
        "original_R59_full_46080_source_sha256":sha(full),
        "local_Dropbox_mirror":str(MIRROR),"local_mirror_byte_identical":"PASS",
        "remote_Dropbox_provider_ack":"NOT_VERIFIED",
        "provider_cold_restore":"NOT_RUN",
        "GitHub_Draft_PR":"PENDING",
        "DAG":{"WU":"34/49","REI_central":"28/88","working":"33/88","fast":"4/7","delta":0},
        "official_tick161":"HOLD","original_source_unchanged":True,
        "production":"HOLD"
    }
    (ROOT/"BACKUP_RECEIPT.json").write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    print(json.dumps(receipt,sort_keys=True),flush=True)
if __name__=="__main__":run()
