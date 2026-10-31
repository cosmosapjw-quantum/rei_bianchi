from pathlib import Path
import json,hashlib,zipfile
root=Path(__file__).resolve().parents[1]
ignore=lambda p: p.name.endswith(('.pyc','.so')) or '__pycache__' in p.parts or p.name in {'MANIFEST.json'}
files=sorted(p for p in root.rglob('*') if p.is_file() and not ignore(p))
entries=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
man={'schema':'REI_F4_CAUSAL_MEMORY_MANIFEST_V1','unit':root.name,'files':entries,'entry_count':len(entries),'parent_pr':305,'current_pr':306,'full_archive_source_original_private':True}
(root/'evidence/MANIFEST.json').write_text(json.dumps(man,indent=2,sort_keys=True)+'\n')
out=root.parent/(root.name+'_FULL.zip')
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in files+[root/'evidence/MANIFEST.json']:
  name=root.name+'/'+str(f.relative_to(root))
  zi=zipfile.ZipInfo(name,date_time=(2026,10,31,13,0,0))
  zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=0o100644<<16
  z.writestr(zi,f.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(entries)+1
print(json.dumps({'archive':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'manifest':len(entries)},indent=2))
