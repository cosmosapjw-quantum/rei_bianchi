#!/usr/bin/env python3
"""Create-only compact private evidence of full 8–16 warm P01 continuation.

The private ZIP is not for the public repository. Never alter input archives.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys, zipfile
from pathlib import Path
if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(250000)
from stage_cell import WORDS,DASH,PRIVATE_DATA_SHA,SOURCE_SHA,sha

def make(campaign,first,previous,public,dest):
    if dest.exists():raise ValueError("CREATE_ONLY_ARCHIVE_EXISTS")
    progress=json.loads((campaign/"CONTINUATION_PROGRESS.json").read_text())
    if progress["status"]!="COMPLETED_SELECTED_CELLS" or [x["cell"] for x in progress["results"]]!=list(range(9,17)):
        raise ValueError("NOT_NINE_COMPLETE_CERTIFICATES")
    chain=json.loads((campaign/"CHAIN_VALIDATION.json").read_text())
    if not chain["all_chain_checks_pass"] or chain["verified_source_cells"]!=16:
        raise ValueError("CHAIN_NOT_CERTIFIED")
    files={}
    def add(p,arc):
        if not p.is_file():raise FileNotFoundError(str(p))
        if arc in files:raise ValueError("DUPLICATE_ARCHIVE_ENTRY")
        files[arc]=p
    prefix="HE18_P01_16_CELLS"
    for name in ("P01_STATE.npz","emissivity.out","P01_INTERVAL.json","HH_P01_COMPARISON.json"):
        path=first/"inputs"/name
        if name in PRIVATE_DATA_SHA and sha(path)!=PRIVATE_DATA_SHA[name]:
            raise ValueError("ORIGINAL_INPUT_CHANGED:"+name)
        add(path,f"{prefix}/original_source_inputs/{name}")
    parent=first/"_c1_private/src/warm_source_reference.py"
    if sha(parent)!=SOURCE_SHA:raise ValueError("ORIGINAL_SOURCE_CHANGED")
    add(parent,f"{prefix}/original_source_inputs/warm_source_reference.py")
    for name in ("SEVEN_CELL_VALIDATION.json","SEVENTH_ENDPOINT_MEMORY.json"):
        add(previous/"results"/name,f"{prefix}/original_predecessor/{name}")
    add(campaign/"CONTINUATION_PROGRESS.json",f"{prefix}/campaign/CONTINUATION_PROGRESS.json")
    add(campaign/"CHAIN_VALIDATION.json",f"{prefix}/campaign/CHAIN_VALIDATION.json")
    if (campaign/"CHAIN_REPLAY_FINAL.json").exists():
        add(campaign/"CHAIN_REPLAY_FINAL.json",f"{prefix}/campaign/CHAIN_REPLAY_FINAL.json")
    for n in range(8,17):
        path=first if n==8 else campaign/f"HE18_MULTICELL_{n:02d}_20261015"
        relative=f"{prefix}/executed_cells/cell_{n:02d}"
        paths=[
          "inputs/CONTINUATION_BINDING.json","inputs/FIXED_REFERENCE.npz",
          "src/warm_interval.py","src/run_evaluations.py","src/assemble_certificate.py",
          "results/mid_jets.json","results/whole_jets.json",
          "results/CERTIFICATE.json","results/RESIDUAL_COUPLING.json",
          f"results/{WORDS[n].upper()}_CELL_VALIDATION.json",
          f"results/{DASH[n]}_ENDPOINT_MEMORY.json",
        ]
        for name in paths:add(path/name,f"{relative}/{name}")
        if (path/"results/CONTINUATION_SUMMARY.json").exists():
            add(path/"results/CONTINUATION_SUMMARY.json",f"{relative}/results/CONTINUATION_SUMMARY.json")
        for p in sorted((path/"evidence").glob("*")):
            if p.is_file() and p.suffix in (".stdout",".stderr",".json"):
                add(p,f"{relative}/evidence/{p.name}")
    for f in sorted(public.rglob("*")):
        if f.is_file() and "__pycache__" not in f.parts and f.suffix!=".pyc":
            add(f,f"{prefix}/public_code/{f.relative_to(public).as_posix()}")
    extra=[
      Path("/tmp/HE18_P01_REMAINING_CAMPAIGN_20261015.console.log"),
      Path("/tmp/HE18_P01_REMAINING_COVARIANT_XACT.stdout"),
      Path("/tmp/HE18_P01_REMAINING_COVARIANT_XACT.stderr"),
    ]
    for f in extra:
        if f.exists():add(f,f"{prefix}/campaign/{f.name}")
    entry={}
    for arc,p in files.items():
        h=hashlib.sha256()
        with p.open("rb") as stream:
            while chunk:=stream.read(1024*1024):
                h.update(chunk)
        entry[arc.removeprefix(prefix+"/")]=dict(bytes=p.stat().st_size,sha256=h.hexdigest())
    m=(json.dumps(dict(schema="he18.p01.16_cell_private_evidence.v1",
       source_commit="a5c958c414dea41216b445c05f58df837f05cacb",
       original_source_file_sha256=SOURCE_SHA,
       incoming_previous_BASS_HE_commit="a3eeff91eb9d0c2ba42d553cfda7eab7ecbc53ef",
       completed_source_saved_cells=16,
       source_scoped_conditional_not_EoR_physical_abundances=True,
       original_source_ODE_reruns=0,
       all_2904_photon_radii_verified_each_cell=True,
       independent_interval_backend_audit=False,files=entry),
       indent=2,sort_keys=True)+"\n").encode()
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("xb") as f:
        with zipfile.ZipFile(f,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
            for arc,p in files.items():z.write(p,arc)
            z.writestr(prefix+"/MANIFEST.json",m)
        f.flush();os.fsync(f.fileno())
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        assert z.read(prefix+"/MANIFEST.json")==m
        for name,meta in entry.items():
            # File payload integrity in archive, not just the current filesystem.
            digest=hashlib.sha256(z.read(prefix+"/"+name)).hexdigest()
            if digest!=meta["sha256"]:raise ValueError("ZIP_MEMBER_SHA_MISMATCH:"+name)
    return dict(schema="he18.p01.private_evidence_receipt.v1",
        filename=dest.name,bytes=dest.stat().st_size,sha256=sha(dest),
        manifest_files=len(entry),archive_members=len(entry)+1,
        archive_CRC_and_all_member_sha256="PASS",
        github_public_code_raw_input_separated=True,
        all_16_original_saved_cells_source_scoped=True,
        remote_upload_status="PENDING")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--campaign",type=Path,required=True)
    p.add_argument("--eighth",type=Path,required=True)
    p.add_argument("--previous-seven",type=Path,required=True)
    p.add_argument("--public",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    r=make(a.campaign,a.eighth,a.previous_seven,a.public,a.output)
    print(json.dumps(r,indent=2))
