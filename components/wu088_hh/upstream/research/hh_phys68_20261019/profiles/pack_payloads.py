"""Deterministically preserve all genuine panel bytes in one Git-friendly archive."""
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
import hashlib,json

ROOT=Path(__file__).resolve().parent
files=sorted([*ROOT.glob("run_l28_t65/panel_*.json"),*ROOT.glob("run_l28_t65_completed/panel_*.json")])
if len(files)!=78:raise SystemExit(f"expected2original+76finalpanelenvelopes,found{len(files)}")
entries=[]
for path in files:
    data=path.read_bytes()
    entries.append({"path":path.relative_to(ROOT).as_posix(),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()})
manifest={"schema":"PHYS68_ALL_PANEL_BYTES_MANIFEST_V1","original_panels":2,"completed_panels":76,
          "entries":entries,"restoration":"extract into this profiles directory; REQUEST/CERTIFICATE files are already plain Git files",
          "scientific_reruns":0,"HH_R10":"OFF"}
target=ROOT/"PROFILE_PANEL_PAYLOADS_20261019.zip"
with ZipFile(target,"w",compression=ZIP_DEFLATED,compresslevel=9) as z:
    for path in files:
        info=ZipInfo(path.relative_to(ROOT).as_posix(),(2026,10,19,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o644<<16
        z.writestr(info,path.read_bytes())
    info=ZipInfo("PANEL_MANIFEST.json",(2026,10,19,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o644<<16
    z.writestr(info,json.dumps(manifest,sort_keys=True,indent=2)+"\n")
with ZipFile(target) as z:
    for entry in entries:
        data=z.read(entry["path"])
        if len(data)!=entry["bytes"] or hashlib.sha256(data).hexdigest()!=entry["sha256"]:
            raise SystemExit("packed bytes mismatch")
receipt={"schema":"PHYS68_PANEL_ARCHIVE_RECEIPT_V1","name":target.name,"bytes":target.stat().st_size,
         "sha256":hashlib.sha256(target.read_bytes()).hexdigest(),"verified_payloads":len(entries),
         "all_original_file_bytes_preserved":True,"solver_reruns":0,"HH_R10":"OFF"}
(ROOT/"PANEL_ARCHIVE_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt))
