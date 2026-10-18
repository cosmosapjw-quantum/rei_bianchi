#!/usr/bin/env python3
"""Rebuild a frozen Unit5 ZIP and explicit compact Git payload; no simulation."""
import argparse, hashlib, json, re, shutil, zipfile
from pathlib import Path
IDENTITY = "1a2268e3da98ed47159cb738762a1a3d3d17bdcb6806e611cbd2bc3c0c6eaff7"
RESEARCH = Path("research/flrw_covariant_transport_20261015")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,default=Path(__file__).resolve().parents[3]);ap.add_argument("--output-dir",type=Path,required=True);args=ap.parse_args();src=args.source.resolve();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    if out==src or src in out.parents: raise RuntimeError("output must be outside source")
    selection=json.loads((src/RESEARCH/"UNIT5_SELECTION.json").read_text())
    for item in selection["file_hashes"]:
        p=src/item["path"]
        if not p.is_file() or p.stat().st_size!=item["bytes"] or sha(p)!=item["sha256"]: raise RuntimeError("frozen file mismatch: "+item["path"])
    b=src/"rust/rei_microphysics/src";driver=(b/"axbi_driver.rs").read_text();block=driver.split("pub fn compiled_identity()",1)[1].split(".join(",1)[0]
    refs=re.findall(r'include_str!\(\s*"([^"]+)"\s*\)',block)
    identity="\nAXBI_SOURCE_BOUNDARY\n".join((b/ref).read_text() for ref in refs)
    if hashlib.sha256(identity.encode()).hexdigest()!=IDENTITY: raise RuntimeError("compiled identity mismatch")
    files=sorted(p for p in src.rglob("*") if p.is_file() and "target" not in p.relative_to(src).parts and "__pycache__" not in p.relative_to(src).parts and p.name!="SOURCE_SHA256SUMS.txt")
    (src/"SOURCE_SHA256SUMS.txt").write_text("".join(sha(p)+"  "+p.relative_to(src).as_posix()+"\n" for p in files));files.append(src/"SOURCE_SHA256SUMS.txt");files.sort()
    target=out/"REI_FLRW_COVARIANT_UNIT5_OUTPUT_ALLOCATION_20261015.zip"
    if target.exists(): raise RuntimeError("fresh output ZIP required")
    with zipfile.ZipFile(target,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files:
            info=zipfile.ZipInfo(p.relative_to(src).as_posix(),date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(target) as z:
        if z.testzip() is not None: raise RuntimeError("ZIP CRC failure")
        for p in files:
            if hashlib.sha256(z.read(p.relative_to(src).as_posix())).hexdigest()!=sha(p): raise RuntimeError("ZIP readback mismatch")
    payload=out/"git_payload";payload.mkdir()
    for rel in selection["git_paths"]:
        p=payload/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/rel,p)
    (out/"GITHUB_UNIT5_PATHS.txt").write_text("\n".join(selection["git_paths"])+"\n")
    receipt={"status":"FROZEN_ZIP_AND_COMPACT_GIT_PAYLOAD_VERIFIED","zip_path":str(target),"zip_bytes":target.stat().st_size,"zip_sha256":sha(target),"zip_members":len(files),"git_payload_path":str(payload),"git_files":len(selection["git_paths"]),"git_payload_bytes":sum((src/rel).stat().st_size for rel in selection["git_paths"]),"source_identity_sha256":IDENTITY,"base_commit":selection["base_commit"],"base_tree":selection["base_tree"],"numerical_runs":0,"git_mutations":0}
    (out/"UNIT5_PACKAGE_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n");print(json.dumps(receipt))
if __name__=="__main__": main()
