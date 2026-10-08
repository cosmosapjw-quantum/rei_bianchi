#!/usr/bin/env python3
"""Create and verify a compact local source/evidence package; no publication."""
from pathlib import Path
import hashlib, json, stat, zipfile

root = Path(__file__).resolve().parent
output = root.parent / 'REI_MIDPOINT_ACCEPTED_RECORD_SOURCE_ONLY_20261008.zip'
receipt = root.parent / 'REI_MIDPOINT_ACCEPTED_RECORD_SOURCE_ONLY_20261008.receipt.json'
prefix = 'REI_MIDPOINT_ACCEPTED_RECORD_SOURCE_ONLY_20261008'
assert (root/'evidence/TARGETED_REVIEW.md').is_file(), 'focused review required'
assert not output.exists(), 'preserve existing package'

def include(p):
    rel = p.relative_to(root)
    if p.is_symlink() or not p.is_file() or 'target' in rel.parts or '__pycache__' in rel.parts:
        return False
    if any(x.endswith('-store') or x == 'foreign-root' for x in rel.parts):
        return False
    return p.suffix in {'.rs', '.toml', '.lock', '.cfg', '.py', '.md', '.json', '.stdout', '.stderr', '.txt'} or p.name in {'stdout', 'stderr', 'READY'}

omitted = []
for p in sorted((root/'evidence').rglob('*')):
    if p.is_file() and not include(p):
        if p.is_symlink():
            omitted.append({'path':str(p.relative_to(root)), 'symlink_omitted':True})
        else:
            data = p.read_bytes()
            omitted.append({'path':str(p.relative_to(root)), 'bytes':len(data), 'sha256':hashlib.sha256(data).hexdigest()})
(root/'evidence/OMITTED_RUNTIME_IMAGES.json').write_text(json.dumps(omitted, indent=2))
files = [(p, p.read_bytes()) for p in sorted(root.rglob('*')) if include(p)]
manifest = [{'path':str(p.relative_to(root)), 'bytes':len(data), 'sha256':hashlib.sha256(data).hexdigest()} for p,data in files]

with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p,data in files:
        info = zipfile.ZipInfo(f'{prefix}/{p.relative_to(root)}', (2026,10,8,0,0,0))
        info.external_attr = (stat.S_IFREG | 0o644) << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info,data)
    info = zipfile.ZipInfo(f'{prefix}/PACKAGE_MANIFEST.json', (2026,10,8,0,0,0))
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    z.writestr(info,json.dumps(manifest,indent=2).encode())

with zipfile.ZipFile(output) as z:
    assert z.testzip() is None
    assert len(z.infolist()) == len(manifest)+1
    for item in manifest:
        data = z.read(f'{prefix}/{item["path"]}')
        assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
report = {'path':str(output.resolve()), 'bytes':output.stat().st_size, 'sha256':hashlib.sha256(output.read_bytes()).hexdigest(), 'members':len(manifest)+1, 'all_member_hashes_and_crc_verified':True, 'compiled_targets_excluded':True, 'runtime_binary_images_excluded':True, 'external_upload':False}
receipt.write_text(json.dumps(report,indent=2))
print(json.dumps(report))
