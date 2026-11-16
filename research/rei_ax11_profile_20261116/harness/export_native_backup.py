#!/usr/bin/env python3
"""Mechanical transfer only: hash and archive this one owned native job."""
from pathlib import Path
import sys,hashlib,json,tarfile,shutil,time
root=Path(sys.argv[1]); destination=Path(sys.argv[2])
assert (root/'STATUS.json').exists()
files=[]
for p in sorted(root.rglob('*')):
    if not p.is_file():continue
    rel=p.relative_to(root)
    if 'target' in rel.parts or 'test_temp' in rel.parts or p.name=='package_chunks.b64':continue
    if p.name.endswith('.tar.gz') or p.name=='EXPORT_MANIFEST.json':continue
    files.append(p)
receipts=json.loads((root/'NATIVE_JOB_RECEIPT.json').read_text())
for pin in receipts['binaries'].values():files.append(Path(pin['path']))
manifest={str(p.relative_to(root)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files}
(root/'EXPORT_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
files.append(root/'EXPORT_MANIFEST.json')
archive=root/'AX11_NATIVE_PROFILE_BUNDLE_v2.tar.gz'
assert not archive.exists()
with tarfile.open(archive,'w:gz') as t:
    for p in files:t.add(p,arcname=str(p.relative_to(root)),recursive=False)
assert not destination.exists()
destination.mkdir(parents=True)
copy=destination/archive.name;shutil.copyfile(archive,copy)
sha=hashlib.sha256(archive.read_bytes()).hexdigest()
assert hashlib.sha256(copy.read_bytes()).hexdigest()==sha
receipt={'archive_name':archive.name,'bytes':archive.stat().st_size,'sha256':sha,'files':len(files),
         'native_source':str(root),'backup_path':str(copy),'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
         'provider_sync_status':'PENDING_PROVIDER_VERIFICATION','source_original_modified':False}
(root/'BACKUP_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
(destination/'BACKUP_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
