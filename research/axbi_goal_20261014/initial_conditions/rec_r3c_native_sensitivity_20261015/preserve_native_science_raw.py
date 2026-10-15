"""Durable local-only immutable native raw source capsule.

Preserves six 8192-row source-output histories, their exact fresh IC,
and four long panel-256 independent histories outside tracked Git checkout.
Source data are NOT auto-published to GitHub; an exact SHA/CRC manifest is.
"""
from __future__ import annotations
import hashlib,json,gzip,tarfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
WORK=Path("/home/cosmosapjw/rec_theory_runs/REI_HYREC_IC_NATIVE_20261015")
DEST=WORK/"scientific_raw"
ARCHIVE=DEST/"REI_REC_HYREC_NATIVE_8192_20261015.tar.gz"
GROUPS=("science_8192step_p64","science_8192step_p256")
SUBSETS=("QZERO_BASELINE","QZERO_HYREC","QMINUS_HYREC","QPLUS_HYREC","QMINUS_BASELINE","QPLUS_BASELINE")

def sha(data):return hashlib.sha256(data).hexdigest()

def run():
    files=[]
    for group in GROUPS:
        root=HERE/group
        names=SUBSETS if group.endswith("p64") else SUBSETS[:4]
        for name in names:
            for ext in (".cfg",".csv"):
                path=root/(name+ext)
                if not path.is_file():raise FileNotFoundError(path)
                files.append(path)
        if group.endswith("p64"):
            files.append(root/"RUN_RESULTS.json")
    DEST.mkdir(parents=True,exist_ok=True)
    manifest=[]
    with ARCHIVE.open("wb") as handle:
        with gzip.GzipFile(fileobj=handle,filename="",mode="wb",compresslevel=7,mtime=0) as gz:
            with tarfile.open(fileobj=gz,mode="w",format=tarfile.PAX_FORMAT) as tf:
                for path in sorted(files,key=lambda x:x.relative_to(HERE).as_posix()):
                    name=path.relative_to(HERE).as_posix()
                    content=path.read_bytes()
                    info=tarfile.TarInfo(name)
                    info.size=len(content);info.mtime=0;info.uid=0;info.gid=0
                    info.uname="";info.gname="";info.mode=0o644
                    import io
                    tf.addfile(info,io.BytesIO(content))
                    manifest.append({"file":name,"size":len(content),"sha256":sha(content)})
    restored={}
    with tarfile.open(ARCHIVE,"r:gz") as tf:
        for m in tf:
            f=tf.extractfile(m)
            if f is None:raise RuntimeError("missing restored payload")
            restored[m.name]=sha(f.read())
    if {x["file"]:x["sha256"] for x in manifest}!=restored:
        raise RuntimeError("compressed archive independent payload SHA recovery mismatch")
    receipt={
        "schema":"rei.rec.native_raw_local_only_capsule.v1",
        "capsule_scope":"10 independently executed original native PR127 8192 accepted histories; no original REI signed production outputs",
        "capsule_local_only":True,
        "capsule_path":str(ARCHIVE),
        "capsule_size_bytes":ARCHIVE.stat().st_size,
        "capsule_sha256":sha(ARCHIVE.read_bytes()),
        "original_native_source_commit":"edddcd6ea9a135fcf18c7be8357b5e11fea87407",
        "source_donor_SHA256":"e393118248021e0a4ed79d7795f0d1ed2b6fb7377233f0f1c35c277e827f73a0",
        "payload_count":len(manifest),
        "payloads":manifest,
        "readback":"PASS_CONTENT_SHA256_FOR_ALL_TAR_MEMBERS",
        "not_published_to_github":True,
        "raw_exists_only_on_authorized_user_machine":True,
    }
    (HERE/"NATIVE_RAW_CAPSULE_RECEIPT.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:receipt[k] for k in ("capsule_path","capsule_sha256","capsule_size_bytes","payload_count","readback")},indent=2))
if __name__=="__main__":run()
