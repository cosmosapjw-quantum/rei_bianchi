#!/usr/bin/env python3
"""Reproducible, self-contained, content-identified source-only event-rate delivery.

Archival stage capsules are closeout reconstructions, *not* historical Git stage
bytes. Original stage commit SHA provenance is carried in STAGE_LEDGER.json.
No new IVPs or real native physical source rates are executed here.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT.parent/'REI_BASS_FULL_EVENT_RATE_COMPAT_20261029_FULL.zip'
UNIT='REI_BASS_FULL_EVENT_RATE_COMPAT_20261029'
STAGES=[
('R1',1,'PASS_SCOPED','c79768dbc4d69c1f9eebc2d54fb8d4246bc0e947'),
('R2',2,'PASS_SCOPED','d04dea4288e1fd07dd290f1eadd4ff0526eab888'),
('R3',3,'PASS_SCOPED','85a89c1e96825fde4d233359607dce8a103f6ba8'),
('R4',4,'PASS_SCOPED','32af11812a14a1da4840db7e110c1b940d015b4e'),
('R5',5,'PASS_SCOPED','282ccc6ceeb1cb26c0c5a3df8754ad4040cd2217'),
('R6',5,'HOLD_DISTINCT_AUTHOR','d49eb8081c3ae48b82a370db6fda38f6129327ee'),
('R7',6,'PASS_SCOPED','9efe8baa8b798c7b1c425259be7f22fdb4553aee'),
('R8',7,'PASS_SCOPED','2e062a54ce668bc539632b5247b7d511a7305a74'),
('R9',8,'PASS_SCOPED','ff8b7af835672b2ffdef5e82553b5b29c50da847'),
('R10',9,'PASS_SCOPED','cea6662803248530683681cbaf19e578b6a8a23d'),
('C1',10,'PASS_SCOPED','08f1a1a3792e04fc4d514cce87d7e8fdd9c19f58'),
('C2',11,'PASS_SCOPED','34366f0f5daabd772a1669d7ff4f663dc59caedb'),
('C3',12,'PASS_SCOPED','63ff231e9a126a9d5a4dc79d7e4eb87310c0516f'),
('C4',13,'PASS_SCOPED','c487c6de7d48ffb873851c6b65897b5405f73efd'),
('C5',14,'PASS_SCOPED','8c9233e8c816780901c277cb73c7932c9f4da09d'),
('C6',15,'PASS_SCOPED','0332676f73bee6906ee3c0223419b8d872522a23'),
('C7',16,'PASS_SCOPED','9935d63dface4847e97aa413792d21af4473b705'),
('C8',17,'PASS_SCOPED','5402d630f47029fddf930123a03c28c99c7a583b'),
('C9',17,'HOLD_DISTINCT_AUTHOR','99a7563b93c296285dee76a3a9036da58f24b784'),
('C10',18,'PASS_SCOPED','f993bbff5489ede894954ed210d02b7b6b2a04c2')]


def jdump(obj):return (json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode()

def sha(b):return hashlib.sha256(b).hexdigest()

def assemble():
    stage_dir=ROOT/'stages';stage_dir.mkdir(exist_ok=True)
    rows=[]
    for st,n,status,commit in STAGES:
        d={'unit':UNIT,'stage':st,'status':status,'scoped_completed':n,'scoped_total':20,
          'original_working':'33/88','original_central':'28/88','physical_fast':'4/7','physical_delta':0,
          'github_stage_commit_sha':commit,'stage_record_origin':'RECONSTRUCTED_AT_CLOSEOUT_NOT_ACTUAL_STAGE_GIT_BLOB',
          'backup':{'github_stage_commit':'ACK','per_stage_cloud_binary':'NOT_RUN'}}
        (stage_dir/(st+'.json')).write_bytes(jdump(d))
        rows.append(d)
    ledger={'schema':'REI_BASS_EVENT_RATE_STAGE_LEDGER_V1','unit':UNIT,'stage_commits':rows,
        'scoped_completed':18,'scoped_total':20,'original_working':'33/88','original_central':'28/88',
        'physical_fast':'4/7','physical_delta':0,'F4':'PARTIAL','L4_ready':False,
        'R6_different_author':'NOT_RUN','C9_different_author':'NOT_RUN','native_subagent':'NOT_EXPOSED',
        'NO_MORE_IVPs':True,'NO_MERGE':True,'original_budget':'CLOSED_NO_TRANSFER',
        'unknown_overhead':'UNKNOWN_NOT_ZERO','publication':'ACTUAL_20_GITHUB_STAGE_COMMITS_SEE_SHAS',
        'stage_json_in_this_zip':'CLOSEOUT_RECONSTRUCTIONS_NOT_BYTE_COPIES_FROM_GITHUB'}
    (ROOT/'STAGE_LEDGER.json').write_bytes(jdump(ledger))
    arch=ROOT/'source'/'archives';arch.mkdir(exist_ok=True)
    upstream=[('REI_BASS_LI6_ELECTRON_LIFT_20261029_FULL.zip','ae5a774d31ae1d6f67b2dfc592d5cbb42ebd466d4f415da2b7b0cd2a3d6b08e8'),
              ('BASS_TAU_SOURCE_ROW_SOURCE_20261029.zip','6a9c84ce076a3545a992f0b364d0fd67fe1063b7a33a290dbe77d44ecee98838'),
              ('REI_SAVED17_UVB_SOURCE_TANGENT_20261029_FULL.zip','f7c01af8e5d996d0f4e953626e494fb50877387061f4cf0fcbb9c168b203509e')]
    for filename,expected in upstream:
        src=ROOT.parent/filename;dat=src.read_bytes()
        assert sha(dat)==expected,(filename,sha(dat))
        (arch/filename).write_bytes(dat)
    source_files=sorted(x for x in ROOT.rglob('*') if x.is_file() and
       not any(part in {'__pycache__','_scratch_source_replay'} for part in x.relative_to(ROOT).parts) and
       x.relative_to(ROOT).as_posix() not in ('delivery/MANIFEST.json',))
    payload={x.relative_to(ROOT).as_posix():{'bytes':x.stat().st_size,'sha256':sha(x.read_bytes())} for x in source_files}
    manifest={'schema':'REI_BASS_EVENT_RATE_ZIP_MANIFEST_V1','unit':UNIT,'compression':'zip/deflate',
       'deterministic_date':'2026-10-29T00:00:00', 'payload_members':payload,'total_payload_members':len(payload),
       'source_original_archives_count':len(upstream),'R6_C9_author_review':'NOT_RUN',
       'physical_result':'SCOPED_SOURCE_RATE_ONLY','entire_full_rei_bass_adapter':'UNBOUND',
       'original_working':'33/88','original_central':'28/88','physical_fast':'4/7','new_IVPs':0}
    mp=ROOT/'delivery'/'MANIFEST.json';mp.parent.mkdir(exist_ok=True)
    mp.write_bytes(jdump(manifest))
    # Zip member names mirror local relative project paths to preserve VERIFY.sh.
    with ZipFile(OUTPUT,'w',compression=ZIP_DEFLATED,compresslevel=7,strict_timestamps=True) as z:
        for file in sorted(x for x in ROOT.rglob('*') if x.is_file() and
            not any(part in {'__pycache__','_scratch_source_replay'} for part in x.relative_to(ROOT).parts)):
            rel=file.relative_to(ROOT).as_posix()
            info=ZipInfo(rel,(2026,10,29,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=(0o755 if rel=='VERIFY.sh' else 0o644)<<16
            z.writestr(info,file.read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=7)
    with ZipFile(OUTPUT) as z:
        assert z.testzip() is None
        archived=json.loads(z.read('delivery/MANIFEST.json'))
        for rel,row in archived['payload_members'].items():
            data=z.read(rel)
            assert len(data)==row['bytes'] and sha(data)==row['sha256'],rel
        assert len(z.namelist())==archived['total_payload_members']+1
    record={'path':str(OUTPUT),'sha256':sha(OUTPUT.read_bytes()),'bytes':OUTPUT.stat().st_size,
            'members':len(payload)+1,'crc':'PASS','inner_sha':f'{len(payload)}/{len(payload)} PASS',
            'three_immutable_source_archives':True}
    (ROOT.parent/'REI_BASS_EVENT_RATE_PACKAGING_RECEIPT_20261029.json').write_bytes(jdump(record))
    print(json.dumps(record,ensure_ascii=False))

if __name__=='__main__':assemble()
