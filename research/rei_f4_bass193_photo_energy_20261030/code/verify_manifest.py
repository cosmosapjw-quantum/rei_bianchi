from pathlib import Path
import hashlib,json,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'MANIFEST.json').read_text())
for e in manifest['files']:
    p=ROOT/e['path']
    if not p.is_file() or p.stat().st_size!=e['size'] or hashlib.sha256(p.read_bytes()).hexdigest()!=e['sha256']:
        raise SystemExit('MANIFEST_BYTE_MISMATCH:'+e['path'])
p=ROOT/'source/VIGILODE_BASS21_SAVED193_SOURCE_REPLAY_20261030_FULL.zip'
with zipfile.ZipFile(p) as z:
    if z.testzip() is not None:raise SystemExit('NESTED_SOURCE_CRC_FAILED')
print(f'MANIFEST PASS {len(manifest["files"])} files; source ZIP CRC PASS')
