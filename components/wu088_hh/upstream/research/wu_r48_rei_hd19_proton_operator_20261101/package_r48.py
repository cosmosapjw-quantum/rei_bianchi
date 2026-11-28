#!/usr/bin/env python3
"""Deterministic source-free original-physics WU R48 ZIP with per-member provenance."""
from __future__ import annotations
import hashlib,json,pathlib,zipfile
ROOT=pathlib.Path(__file__).resolve().parent
DEST=ROOT.parent/'WU_R48_HD19_REI_SOURCE_CONDITIONAL_FULL_20261101.zip'
ROOT_FILES=['r48_hd19_operator.py','wu_r47_source_adapter.py','test_r48.py','verify_r48.py','plot_science.py','package_r48.py','README_REPRODUCE.md','THEORY_AND_SCIENCE_KO.md','SELF_ADVERSARIAL_KO.md','NEXT_THREAD_HANDOFF_KO.md','INDEPENDENT_OUTPUT_AUDIT.json','CLEANROOM_REPLAY_VERIFIED.json','STAGE_LEDGER.json']
FILES=ROOT_FILES+[str(x.relative_to(ROOT)) for x in sorted((ROOT/'results').iterdir()) if x.is_file()]+[str(x.relative_to(ROOT)) for x in sorted((ROOT/'stages').glob('*.json'))]
FILES=sorted(FILES)

def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def main():
    original_raw=['HD.Rovibration.805a7aa5.radex','first_interval_r2_blocked_minimum_step.tar.gz','ORIGINAL_46080_STATES']
    if any(any(bad in f for bad in original_raw) for f in FILES):raise ValueError('source private accidentally bundled')
    manifest={'schema':'WU_R48_SOURCE_FREE_MEMBER_SHA256_V1','archive_kind':'DERIVED_RESULTS_CODE_PLOTS_NO_THIRD_PARTY_RAW',
     'private_required_original_source_SHA256':{'EMAA_RADEX':'b0db1613425e403889c3a74f6cd9e142c562a552f1ebf05e61cbf509cd429c94','REI_STATES':'48ad5c6f0922ad946a10a89ce17fefd2c7241ac956b6bac194892a42810312a7'},
     'source_free_members':{f:{'sha256':digest(ROOT/f),'size':(ROOT/f).stat().st_size} for f in FILES},
     'WU_canonical':'34/49','REI_central':'28/88','canonical_delta':0,'independent_author_R6_C9':'NOT_RUN'}
    (ROOT/'SOURCE_FREE_MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf8')
    allfiles=FILES+['SOURCE_FREE_MANIFEST.json']
    with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for f in allfiles:
            data=(ROOT/f).read_bytes()
            zi=zipfile.ZipInfo(f,(2020,1,1,0,0,0))
            zi.compress_type=zipfile.ZIP_STORED if f.endswith(('.gz','.png')) else zipfile.ZIP_DEFLATED
            zi.external_attr=0o644<<16
            z.writestr(zi,data,compress_type=zi.compress_type,compresslevel=6)
    with zipfile.ZipFile(DEST) as z:
        if z.testzip() is not None:raise ValueError('source-free ZIP CRC failed')
        actual=set(z.namelist())
        if actual!=set(allfiles):raise ValueError('ZIP membership mismatch')
        for f in FILES:
            data=z.read(f);p=manifest['source_free_members'][f]
            if len(data)!=p['size'] or hashlib.sha256(data).hexdigest()!=p['sha256']:
                raise ValueError('ZIP per-file hash mismatch '+f)
    stat={'file':str(DEST),'bytes':DEST.stat().st_size,'sha256':digest(DEST),'members':len(allfiles),
          'per_member_hash_checked':len(FILES),'ZIP_CRC':'PASS','no_original_raw':True,
          'WU_canonical':'34/49','REI_central':'28/88','delta':0}
    print(json.dumps(stat,indent=2))
if __name__=='__main__':main()
