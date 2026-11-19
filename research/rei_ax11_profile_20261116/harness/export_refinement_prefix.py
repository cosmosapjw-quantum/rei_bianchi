#!/usr/bin/env python3
"""Mechanical backup of the bounded time/energy/angle prefixes, all raw states."""
from pathlib import Path
import json,hashlib,tarfile,shutil,sys,time
r=Path(sys.argv[1]);dest=Path(sys.argv[2]);assert dest.is_dir()
assert (r/'GRID_PREFLIGHT_STATUS.json').exists() and (r/'TIME_PREFLIGHT_STATUS.json').exists()
files=[]
for folder in ['time_preflight_inputs','time_preflight_results','grid_preflight_inputs','grid_preflight_results']:
 files.extend(p for p in (r/folder).rglob('*') if p.is_file())
for p in r.iterdir():
 if p.is_file() and (p.name.startswith(('TIME_PREFLIGHT_','GRID_PREFLIGHT_','ALLOCATION_AMENDMENT_')) or p.suffix=='.log' or p.name in ['native_time_preflight.py','native_grid_preflight.py','export_refinement_prefix.py']):files.append(p)
files=sorted(set(files));m={str(p.relative_to(r)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files}
manifest=r/'PREFIX_EXPORT_MANIFEST.json';assert not manifest.exists();manifest.write_text(json.dumps(m,indent=2)+'\n');files.append(manifest)
archive=r/'AX11_REFINEMENT_PREFIX_BUNDLE_v1.tar.gz';assert not archive.exists()
with tarfile.open(archive,'w:gz') as t:
 for p in files:t.add(p,arcname=str(p.relative_to(r)),recursive=False)
copy=dest/archive.name;assert not copy.exists();shutil.copyfile(archive,copy)
h=hashlib.sha256(archive.read_bytes()).hexdigest();assert hashlib.sha256(copy.read_bytes()).hexdigest()==h
receipt={'archive_name':archive.name,'bytes':archive.stat().st_size,'sha256':h,'files':len(files),'backup_path':str(copy),'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'base_source_binary_archive_sha256':'973ac67a0e1d156d153d8b40185837ada74812aa285d72db48a613ba5c7a2005','provider_sync':'PENDING_VERIFY'}
(r/'PREFIX_BACKUP_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');(dest/'PREFIX_BACKUP_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
