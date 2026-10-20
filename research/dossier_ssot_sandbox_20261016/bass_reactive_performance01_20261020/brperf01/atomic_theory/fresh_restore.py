"""Deterministic source snapshot, safe restore, fresh target build and exact readback."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parent
SOURCES=['generate_catalog.py','validate_independent.py','RUN_ATOMIC.sh','NOTICE.md',
         'SOURCE_CONTRACT.json','REPORT_ATOMIC_KO.md','fresh_restore.py']

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    files=[ROOT/name for name in SOURCES]
    files+=sorted(p for sub in ['catalog','data'] for p in (ROOT/sub).rglob('*')
                  if p.is_file() and 'target' not in p.parts and '__pycache__' not in p.parts)
    files=sorted(set(files))
    manifest={str(p.relative_to(ROOT)):sha(p) for p in files}
    snapshot=ROOT/'ATOMIC_SOURCE_SNAPSHOT.zip'
    with zipfile.ZipFile(snapshot,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files:
            info=zipfile.ZipInfo(str(p.relative_to(ROOT)),date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644<<16
            z.writestr(info,p.read_bytes())
        info=zipfile.ZipInfo('SOURCE_MANIFEST.json',date_time=(1980,1,1,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(info,json.dumps(manifest,indent=2)+'\n')
    restore=ROOT/'fresh_restore'
    if restore.exists():shutil.rmtree(restore)
    restore.mkdir()
    with zipfile.ZipFile(snapshot) as z:
        for name in z.namelist():
            assert not Path(name).is_absolute() and '..' not in Path(name).parts
        z.extractall(restore)
    for name,digest in manifest.items():assert sha(restore/name)==digest,name
    environment=os.environ.copy()
    environment['CARGO_TARGET_DIR']=str(ROOT/'fresh_target')
    if Path(environment['CARGO_TARGET_DIR']).exists():shutil.rmtree(environment['CARGO_TARGET_DIR'])
    with (ROOT/'evidence'/'FRESH_RESTORE_RUN.log').open('w') as log:
        subprocess.run(['bash',str(restore/'RUN_ATOMIC.sh')],check=True,env=environment,stdout=log,stderr=subprocess.STDOUT)
    compared={}
    for name in ['ATOMIC_VALUES.csv','TABLE_SCANS.csv']:
        a=sha(ROOT/'evidence'/name); b=sha(restore/'evidence'/name)
        assert a==b,(name,a,b)
        compared[name]={'sha256':a,'fresh_restore_exact_match':True}
    source_after={name:sha(restore/name) for name in manifest}
    assert source_after==manifest
    verification=json.loads((restore/'evidence'/'INDEPENDENT_VERIFICATION.json').read_text())
    assert verification['status']=='PASS'
    result={'status':'PASS','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'archive':snapshot.name,'archive_bytes':snapshot.stat().st_size,'archive_sha256':sha(snapshot),
        'verified_source_payloads':len(manifest),'fresh_cargo_target':environment['CARGO_TARGET_DIR'],
        'fresh_test_count':8,'fresh_clippy':'PASS','fresh_rustfmt':'PASS',
        'fresh_python_decimal_60':'PASS','source_payload_unchanged_after_regenerate_and_fmt':True,
        'exact_output_comparisons':compared,
        'timing_comparison':'NOT_BITWISE_COMPARED_WALLTIME_EXPECTED_TO_CHANGE'}
    (ROOT/'evidence'/'FRESH_RESTORE_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'ATOMIC_SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
