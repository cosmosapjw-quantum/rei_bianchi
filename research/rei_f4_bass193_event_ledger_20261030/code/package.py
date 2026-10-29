from pathlib import Path
import json, hashlib, zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'REI_F4_BASS193_NATIVE_EVENT_DATA_20261030_FULL.zip'

def sha(b):return hashlib.sha256(b).hexdigest()
exclude={'source/MANIFEST.json'}
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink() and not p.is_relative_to(ROOT/'donor') and not p.is_relative_to(ROOT/'__pycache__') and not any(part=='__pycache__' for part in p.parts) and str(p.relative_to(ROOT)) not in exclude and not p.name.endswith('.pyc'))
manifest={'schema':'REI_F4_BASS193_NATIVE_EVENT_PACKAGE_V1',
          'source_archive_sha256':'19513fec19e53d5f2da8da50ba22aa066c634dee79ff94cff31d07b4cfb8f907',
          'original_BASS_saved_trajectory_sha256':'37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086',
          'files':[{'name':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in files]}
(ROOT/'source/MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
allfiles=files+[ROOT/'source/MANIFEST.json']
with zipfile.ZipFile(OUT,'w') as z:
    for p in allfiles:
        arc=str(Path(ROOT.name)/p.relative_to(ROOT))
        info=zipfile.ZipInfo(arc, date_time=(2026,10,30,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=(0o755 if p.suffix=='.sh' else 0o644)<<16
        z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
with zipfile.ZipFile(OUT) as z:
    assert z.testzip() is None
    for entry in manifest['files']:
        assert sha(z.read(str(Path(ROOT.name)/entry['name'])))==entry['sha256']
print(json.dumps(dict(filename=OUT.name,bytes=OUT.stat().st_size,sha256=sha(OUT.read_bytes()),members=len(allfiles),manifest=len(files),zip_crc='PASS',all_nested_payload_sha='PASS'),indent=2))
