"""Reproducible, manifest-verified, archive construction for each phase.
No private original PR166 archive is embedded; provenance points to immutable SHA.
"""
from __future__ import annotations
import hashlib
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
COMMON=[
 'src/positive_reference.py','src/native_age_audit.py',
 'src/duhamel_diagnostics.py','tests/test_positive_reference.py',
 'tests/test_duhamel_diagnostics.py','results/native_age_summary.json',
 'README.md','THEORY_R5_KO.md','C6_C8_SCIENTIFIC_REPORT_KO.md',
 'contracts/NEXT_DAG_v2.json'
]
STAGES={
 'C6':['src/duhamel_diagnostics.py','src/positive_reference.py',
       'src/native_age_audit.py','tests/test_duhamel_diagnostics.py',
       'tests/test_positive_reference.py','results/native_age_summary.json',
       'evidence/c8_34tests_final.log'],
 'C8':COMMON+['src/run_duhamel_study.py','src/make_duhamel_figure.py',
             'results/duhamel_diagnostics.json', 'evidence/c8_study_stdout.log',
             'evidence/c8_34tests_final.log','figures/duhamel_refinement.png'],
 'C10':COMMON+['src/run_duhamel_study.py','src/make_duhamel_figure.py',
       'src/package_full.py','src/run_study.py','src/package_stage.py',
       'results/duhamel_diagnostics.json','results/native_age_audit.json',
       'results/positive_reference_study.json',
       'evidence/c8_study_stdout.log','evidence/c8_34tests_final.log',
       'evidence/WOLFRAM_CAS.wl','evidence/WOLFRAM_CAS_RESULT.txt',
       'evidence/study_stdout.log','evidence/test_results.log',
       'figures/duhamel_refinement.png','figures/positive_age_convergence.png',
       'figures/smooth_refinement.png','CODEX_NCP_HANDOFF_KO.md',
       'RESTORE_VERIFY.sh']
}

def package(stage:str, out:Path) -> dict:
    paths=sorted(set(STAGES[stage]))
    base='rei_source_age_positive_20261016/'
    manifest={'schema':'rei.positive_age.phase.v2','stage':stage,
        'science_claim':'CONDITIONAL_PRESCRIBED_OPACITY_ONLY',
        'original_native_pr166_head':'553ce556d9f8662290c000ec675c7e6007c9d895',
        'original_native_zip_sha256':'2ebab11829b793eb19a0b91e5d04a3a8637e346e456ac0931c372585ef7e21de',
        'files':{}}
    for rel in paths:
        p=ROOT/rel
        if not p.is_file():raise FileNotFoundError(p)
        b=p.read_bytes()
        manifest['files'][rel]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
    raw=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
    out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        for rel in paths+['PAYLOAD_MANIFEST.json']:
            data=raw if rel=='PAYLOAD_MANIFEST.json' else (ROOT/rel).read_bytes()
            info=zipfile.ZipInfo(base+rel, date_time=(2026,10,16,0,0,0))
            info.external_attr=0o644<<16
            info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=7)
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        for rel,entry in manifest['files'].items():
            assert hashlib.sha256(z.read(base+rel)).hexdigest()==entry['sha256']
    return {'stage':stage,'archive':out.name,'bytes':out.stat().st_size,
            'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
            'payload_count':len(paths),'zip_crc':'PASS','manifest':'PASS'}

if __name__=='__main__':
    import sys
    print(json.dumps(package(sys.argv[1],Path(sys.argv[2])),indent=2))
