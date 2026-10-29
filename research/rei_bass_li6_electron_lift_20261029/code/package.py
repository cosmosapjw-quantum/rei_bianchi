"""Deterministic source-only evidence archive (no executable science on import)."""
from pathlib import Path
import zipfile,hashlib,json
root=Path(__file__).resolve().parents[1]
archive=root.parent/'REI_BASS_LI6_ELECTRON_LIFT_20261029_FULL.zip'
parent=root/'source/PR265_PARENT_FULL.zip'
expected_parent='c1c277fbeaed026b3a7b4a913d9d9c94659639b0628a724394b5e6d3a7333740'
assert hashlib.sha256(parent.read_bytes()).hexdigest()==expected_parent
excluded={'reference_binary','TEST_FIRST.txt','TEST_STDOUT.txt','__pycache__'}
files=sorted(x for x in root.rglob('*') if x.is_file() and not any(p in excluded for p in x.parts))
files=[p for p in files if p.relative_to(root).as_posix()!='delivery/ARCHIVE_MANIFEST.json']
manifest={'schema':'REI_BASS_LI6_LIFT_ARCHIVE_MANIFEST_V1',
          'unit':'REI_BASS_LI6_ELECTRON_LIFT_20261029',
          'original_DAG':'working33/88; central28/88; physical_delta0',
          'stage_snapshot_semantics':'20 closeout-reconstructed JSON; source authority is exact GitHub individual stage commits/blobs in STAGE_LEDGER.json',
          'source_archive_parent_sha256':expected_parent,
          'payloads':{p.relative_to(root).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files}}
manifest_path=root/'delivery/ARCHIVE_MANIFEST.json'
manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
allfiles=files+[manifest_path]
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(allfiles):
    path=f'{root.name}/{p.relative_to(root).as_posix()}'
    info=zipfile.ZipInfo(path,date_time=(2026,10,29,0,0,0))
    info.compress_type=zipfile.ZIP_DEFLATED
    info.external_attr=0o644<<16
    z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  assert len(z.namelist())==len(allfiles)
  for name,v in manifest['payloads'].items():
    raw=z.read(root.name+'/'+name)
    assert len(raw)==v['bytes'] and hashlib.sha256(raw).hexdigest()==v['sha256'],name
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,
                  'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
                  'members':len(allfiles),'payload_sha_verified':len(files),'CRC':'PASS'},indent=2))
