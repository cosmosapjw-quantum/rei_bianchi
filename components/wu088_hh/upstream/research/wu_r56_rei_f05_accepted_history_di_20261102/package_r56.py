#!/usr/bin/env python3
"""WU R56 immutable, source-inclusive physics archive plus local Dropbox sync.
Only a local mirror is asserted until an independent provider cold download.
"""
from pathlib import Path
import hashlib,json,shutil,zipfile

HERE=Path(__file__).resolve().parent
ZIPPARENT=Path("/home/cosmosapjw/archives/WU_R56_REI_F05_ACCEPTED_HISTORY_20261102")
ZIP=ZIPPARENT/"WU_R56_FULL_ORIGINAL_SOURCE_20261102.zip"
MIRROR=Path("/home/cosmosapjw/Dropbox/WU088_HH_R56_REI_F05_ACCEPTED_HISTORY_20261102")/ZIP.name
R54=Path("/home/cosmosapjw/Dropbox/WU088_HH_R54_REI_F05_DI_4GROUP_20261101/WU_R54_REI_F05_DI_4GROUP_PHOTON_CONSERVING_SOURCE_FULL_20261101.zip")
REC=Path("/home/cosmosapjw/worktrees/rec-f05-accepted-trajectory-20261102/research/rec_f05_accepted_trajectory_20261102/results/ORIGINAL_F05_REPLAY_0_64_128_160_46080.csv.gz")
NATIVE={
    "tick64":Path("/home/cosmosapjw/archives/rei_f05_owner_original64_rust_20261101/private/FIRST64_CURRENT_RUNTIME_NONAUTHORITATIVE.state"),
    "tick128":Path("/home/cosmosapjw/archives/rec_f05_accepted_trajectory_20261102/run_002_pinned/private/ORIGINAL_REPLAY_TICK000128_NONAUTHORITATIVE.state"),
    "tick160":Path("/home/cosmosapjw/archives/rec_f05_accepted_trajectory_20261102/run_002_pinned/private/ORIGINAL_REPLAY_TICK000160_NONAUTHORITATIVE.state")}
LOCK={
    R54:"23cbf0b3e91f7e17fc915c06c025a9e55c6aac8b0ebeca6df7039bfe5fbb32ab",
    REC:"6674ca16ebb40607a47bed9f2eb32ed587f6a770b20bb1af6b3a988ff510259c",
    NATIVE["tick64"]:"aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425",
    NATIVE["tick128"]:"bbb349102194c86fb39a720a6695d9cb5845782b154da3448a433959fcc7f6a6",
    NATIVE["tick160"]:"74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6",
    HERE/"results/R56_ORIGINAL_REI_HISTORICAL_D_46080.csv.gz":"fd23177e302892373a6adba5ad5417c964c8f54535ea02967efbf3593cc13692"
}
def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def add_zip(z,source,arc):
    info=zipfile.ZipInfo(arc,date_time=(2026,11,2,0,0,0))
    info.external_attr=0o644<<16
    info.compress_type=zipfile.ZIP_STORED if source.suffix in (".gz",".npz",".zip") or source.name.endswith(".state") else zipfile.ZIP_DEFLATED
    with source.open("rb") as f,z.open(info,"w") as w:
        shutil.copyfileobj(f,w,length=1<<20)
    return dict(path=arc,bytes=source.stat().st_size,sha256=sha(source))
def main():
    for p,h in LOCK.items():
        if sha(p)!=h:raise ValueError("ORIGINAL_SOURCE_SHA_CHANGED_"+p.name)
    own=sorted(p for p in HERE.rglob("*") if p.is_file()
       and "__pycache__" not in p.parts and p.name not in ("BACKUP_RECEIPT.json","package_r56.py"))
    # Include generator in archive for executable restore. Generated outputs are already produced.
    own.append(HERE/"package_r56.py")
    ZIPPARENT.mkdir(parents=True,exist_ok=True)
    manifest=[]
    with zipfile.ZipFile(ZIP,"w",allowZip64=True,compresslevel=6) as z:
        for p in own:manifest.append(add_zip(z,p,"R56/"+str(p.relative_to(HERE))))
        manifest.append(add_zip(z,R54,"IMMUTABLE_ORIGINAL_R54/"+R54.name))
        manifest.append(add_zip(z,REC,"IMMUTABLE_REC195_HHE_184320/"+REC.name))
        for key,p in NATIVE.items():
            manifest.append(add_zip(z,p,"IMMUTABLE_REI_STATE/"+key+".state"))
        j=zipfile.ZipInfo("CONTENT_SHA256_MANIFEST.json",date_time=(2026,11,2,0,0,0))
        j.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(j,json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    with zipfile.ZipFile(ZIP) as z:
        assert z.testzip() is None,"ZIP_CRC_FAIL"
        assert len(z.namelist())==len(manifest)+1,"ZIP_ITEM_COUNT"
        for arc,target_sha in [
          ("IMMUTABLE_ORIGINAL_R54/"+R54.name,LOCK[R54]),
          ("IMMUTABLE_REC195_HHE_184320/"+REC.name,LOCK[REC]),
          ("IMMUTABLE_REI_STATE/tick160.state",LOCK[NATIVE["tick160"]])]:
            h=hashlib.sha256()
            with z.open(arc) as f:
                for b in iter(lambda:f.read(1<<20),b""):h.update(b)
            if h.hexdigest()!=target_sha:raise ValueError("ZIP_MEMBER_IDENTITY_"+arc)
    MIRROR.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ZIP,MIRROR)
    assert sha(ZIP)==sha(MIRROR),"LOCAL_MIRROR_SHA_FAIL"
    receipt=dict(schema="WU_R56_FULL_SOURCE_ARCHIVE_LOCAL_AND_SYNC_RECEIPT_V1",
        archive=str(ZIP),archive_size=ZIP.stat().st_size,
        archive_sha256=sha(ZIP),archive_zip_CRC="PASS",
        zip_members=len(manifest)+1,
        original_R54_SOURCE_FULL_SHA256=LOCK[R54],
        original_REC195_HHE184320_SHA256=LOCK[REC],
        original_REI_states_SHA256={k:LOCK[p] for k,p in NATIVE.items()},
        R56_46080_data_SHA256=LOCK[HERE/"results/R56_ORIGINAL_REI_HISTORICAL_D_46080.csv.gz"],
        local_Dropbox_sync_path=str(MIRROR),
        local_Dropbox_sync_byte_exact="PASS",
        Dropbox_provider_uploaded="NOT_YET_CHECKED",
        Dropbox_cold_restore="NOT_YET_CHECKED",
        Github_draft="NOT_YET_CHECKED",
        stages="R1-R10,C1-C10_LATEST_EVIDENCE",
        DAG=dict(WU="34/49",REI="28/88",working="33/88",fast="4/7",delta=0),
        original_tick161="HOLD",original_production="HOLD",source_owner_unchanged=True)
    (HERE/"BACKUP_RECEIPT.json").write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    print(json.dumps(receipt,sort_keys=True))
if __name__=="__main__":main()
