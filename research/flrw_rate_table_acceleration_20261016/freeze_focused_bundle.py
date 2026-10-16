#!/usr/bin/env python3
"""Freeze the tested source and literal compile-time inputs for relocation."""
import hashlib,json,pathlib,re,shutil
unit=pathlib.Path(__file__).resolve().parent;repo=unit.parent.parent
destination=unit/'focused_bundle';source=repo/'rust/rei_microphysics'
queue=[p for p in (source/'src').glob('*.rs') if p.name!='joint_affine.rs']
queue += [source/'tests/rate_table.rs',source/'tests/lithium_rates.rs',unit/'probe/baseline_igm_thermal.rs']
seen=set();records=[]
while queue:
 path=queue.pop().resolve()
 if path in seen:continue
 seen.add(path)
 if not path.is_file() or not path.is_relative_to(repo):raise SystemExit(f'Missing/unexpected compile input: {path}')
 relative=path.relative_to(repo);target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
 data=path.read_bytes();records.append({'path':str(relative),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 if path.suffix=='.rs':
  text=data.decode()
  for included in re.findall(r'include_(?:str|bytes)!\(\s*"([^"]+)"',text):queue.append(path.parent/included)
(unit/'FOCUSED_SOURCE_FILES.json').write_text(json.dumps({'source_freeze':'current tested production bytes; see FRESH_SOURCE_COMPARISON and owned delta','omission':'joint_affine declaration/reexports only; unrelated later-stabilized float API','files':sorted(records,key=lambda x:x['path']),'total_bytes':sum(x['bytes'] for x in records)},indent=2)+'\n')
print(json.dumps({'files':len(records),'bytes':sum(x['bytes'] for x in records)}))
