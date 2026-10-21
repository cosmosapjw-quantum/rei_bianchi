#!/usr/bin/env python3
"""Check only immutable parent model and original 625 raw case files."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;P=HERE.parent;TASK=P.parents[2]
manifest=P/'PAYLOAD_MANIFEST.json';m=json.loads(manifest.read_text());prefix=P.relative_to(TASK).as_posix()
selected=[r for r in m['files'] if r['path'].startswith(prefix+'/results/pilot/cases/') or r['path'] in {prefix+'/'+s for s in ('pilot.py','SOURCE_ATTRIBUTION.json','vendor/canonical_fv.py','vendor/species_hierarchy.py','vendor/lrs_boltzmann.py','vendor/REI_BACKGROUND_FAMILY_LOCK.json')}]
assert len(selected)==2506,len(selected)
for row in selected:
 p=TASK/row['path'];data=p.read_bytes();assert len(data)==row['size_bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],row['path']
r={'status':'PASS_PARENT_AND_ORIGINAL_625_RAW_BYTE_IDENTICAL','checked_files':len(selected),'old_case_files':2500,'parent_model_files':6,'parent_manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'numerics_rerun':False}
out=HERE/'evidence/PARENT_IMMUTABILITY_CHECK.json';out.parent.mkdir(exist_ok=True)
if out.exists():raise FileExistsError(out)
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
