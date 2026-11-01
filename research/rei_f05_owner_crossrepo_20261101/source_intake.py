#!/usr/bin/env python3
"""Read-only source-backup intake for original REI F05 sibling physics.

No source-state mutation; original source bytes stay outside Git. Output is a
compact immutable identity and science-CI evidence binding only.
"""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path

HE_ARCHIVE_SHA="c49e6230091287f3cf7726683496e506db8498d2bdd7ad7cd6ab35ae31be1093"
REC_ARCHIVE_SHA="ef8ea9c0b36b54099732aa2f34e30ce4ad2bef225049a536e96112a8c69b4640"
PREVIEW_SHA="713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d"
INCREMENT_SHA="11df439390209bd48742ca9f4303c8743c9e14900289805e13d1ed489450a5dd"
HE_DERIVED_SHA="3e909db856366f6eec49c60cf0e105c98d0f04ab9bf59dd26720a6dcd7d26b70"
HE_RESULT_BLOB="08350a94f3c2517a4d3cfb7751f7bdea01721864"
REC_RESULT_BLOB="4a90fa30aa81d8aabc861adf192076dba268221e"
HE_PREFIX="BASS_HE/research/rei_f05_tick161_atomic_binding_20261101/"
REC_PREFIX="research/rec_rei_f05_tick161_thomson_capacity_20261101/"

def sha(raw:bytes)->str:
    return hashlib.sha256(raw).hexdigest()
def blob(raw:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
def pathsha(p:Path)->str:
    m=hashlib.sha256()
    with p.open("rb") as f:
        for x in iter(lambda:f.read(2**20),b""):m.update(x)
    return m.hexdigest()
def member(z:zipfile.ZipFile,name:str)->bytes:
    if name not in z.namelist(): raise AssertionError("MISSING_SOURCE_MEMBER:"+name)
    return z.read(name)
def check(cond:bool,detail:str):
    if not cond:raise AssertionError(detail)

def main(hepath:Path,recpath:Path,out:Path):
    heh=pathsha(hepath);rech=pathsha(recpath)
    check(heh==HE_ARCHIVE_SHA,"HE_SOURCE_ARCHIVE_MISMATCH")
    check(rech==REC_ARCHIVE_SHA,"REC_SOURCE_ARCHIVE_MISMATCH")
    files={}
    with zipfile.ZipFile(hepath) as he,zipfile.ZipFile(recpath) as rec:
        check(he.testzip() is None,"HE_ARCHIVE_CRC_FAILURE")
        check(rec.testzip() is None,"REC_ARCHIVE_CRC_FAILURE")
        groups=[
          ("he_original_preview",he,HE_PREFIX+"source_inputs/ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz",PREVIEW_SHA,None),
          ("he_original_increment",he,HE_PREFIX+"source_inputs/REI_ORIGINAL26_COMMON_PARENT_INCREMENT_46080.csv.gz",INCREMENT_SHA,None),
          ("he_latent_derived",he,HE_PREFIX+"results/ORIGINAL_REI_F05_TICK161_H_HE_LATENT_ENERGY_46080.csv.gz",HE_DERIVED_SHA,None),
          ("he_result",he,HE_PREFIX+"results/RESULT.json",None,HE_RESULT_BLOB),
          ("rec_original_preview",rec,REC_PREFIX+"source_inputs/ORIGINAL_REI_F05_TICK161_PHYSICAL_CANDIDATE_46080.csv.gz",PREVIEW_SHA,None),
          ("rec_result",rec,REC_PREFIX+"results/SCIENCE_RESULT.json",None,REC_RESULT_BLOB),
        ]
        for label,z,name,expected_sha,expected_blob in groups:
            data=member(z,name)
            digest=sha(data);gitblob=blob(data)
            if expected_sha:check(digest==expected_sha,label+"_SOURCE_BYTES_SHA_MISMATCH")
            if expected_blob:check(gitblob==expected_blob,label+"_GITHUB_BLOB_MISMATCH")
            files[label]={"zip_member":name,"size_bytes":len(data),"content_sha256":digest,"git_blob_sha1":gitblob}
        hedoc=json.loads(member(he,HE_PREFIX+"results/RESULT.json"))
        recdoc=json.loads(member(rec,REC_PREFIX+"results/SCIENCE_RESULT.json"))
        check(hedoc["output_sha256"]==HE_DERIVED_SHA,"HE_OWNER_RESULT_WRONG_OUTPUT")
        check(hedoc["source_preview_csv_sha256"]==PREVIEW_SHA,"HE_ORIGINAL_PREVIEW_SHA")
        check(hedoc["source_increment_csv_sha256"]==INCREMENT_SHA,"HE_ORIGINAL_INCREMENT_SHA")
        check(recdoc["source_gzip_sha256"]==PREVIEW_SHA,"REC_PREVIEW_SHA")
        check(hedoc["original_owner_head"]==recdoc["input_rei_source_head"]=="ea8d6bf94197392c69f939f03c1673ed3afe349c","MISMATCHED_ORIGINAL_REI_OWNER")
        check(hedoc["official_tick161"]=="NOT_ACCEPTED" and recdoc["original_worker_acceptance"]=="FAILED_UNCHANGED","NONAUTHORITATIVE_SOURCE_STATUS_MISMATCH")
        check(hedoc["sampled_original_physical_cells"]==recdoc["source_physical_cells"]==46080,"MISMATCHED_SPATIAL_GRID")
        check(hedoc["original_source_tar_sha256"]==recdoc["original_source_tar_sha256"]=="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b","ORIGINAL_26EVENT_SOURCE_SHA_MISMATCH")
    report={
      "schema":"REI_F05_OWNER_CROSS_REPO_BYTE_INTAKE_V1",
      "status":"BYTE_IDENTITY_PASS_FOR_SOURCE_SCOPED_CONSUMPTION",
      "original_rei_parent_pr":352,"original_rei_parent_head":"ea8d6bf94197392c69f939f03c1673ed3afe349c",
      "original_tick":"160/131072","tick161":"NONAUTHORITATIVE_PREVIEW_ONLY",
      "source_nodes":46080,"he_archive_sha256":heh,"he_archive_bytes":hepath.stat().st_size,
      "rec_archive_sha256":rech,"rec_archive_bytes":recpath.stat().st_size,
      "he_pr_head":"b3b4d95e93999e86a26a3c9719adb739d5865ce4",
      "rec_pr_head":"8c0170ba7d0b8a64b2acac981720e89efdf257ec",
      "original_archive_SHA256":"a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b",
      "original_state_array_SHA256":"cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01",
      "he_science_ci":{"id":41306955654,"result":"SUCCESS"},
      "rec_science_ci":{"id":41306413602,"result":"SUCCESS"},
      "rec_repository_verify":{"id":41306413466,"result":"FAIL_UNRELATED_EXISTING_TRAILING_WHITESPACE"},
      "source_member_identities":files,
      "three_lanes_are_one_dataset":True,
      "no_original_source_mutation":True,
      "production":"HOLD","canonical_delta":0,
      "unverified_claims":["ORIGINAL_TICK161_ACCEPTED","LINE_OF_SIGHT_TAU","PHYSICAL_HEAT_DEPOSITION_FROM_LATENT_ENERGY"]
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"result":report["status"],"members":{k:(v["size_bytes"],v["content_sha256"][:14]) for k,v in files.items()},
      "original_nodes":report["source_nodes"],"HE_ARCHIVE":heh,"REC_ARCHIVE":rech,"canonical_delta":0},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--he-zip",type=Path,required=True)
    p.add_argument("--rec-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    main(a.he_zip,a.rec_zip,a.out)
