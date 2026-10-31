from pathlib import Path
import json,hashlib,zipfile
R=Path(__file__).resolve().parents[1]
OUT=R.parent/(R.name+'_FULL.zip')
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def valid(p):
 name=p.relative_to(R).as_posix()
 if name.startswith(('.source_extract/','source/PR300_FULL_RESTORED/')):return False
 if name in ('run_full.log','run_full.pid','MANIFEST.json','evidence/OUTPUT_SHA256.json'):return False
 if '__pycache__' in p.parts or p.suffix=='.pyc':return False
 if name.startswith('source/') and name != 'source/PR300_FULL.zip': return False
 return True
def rec(p):return {'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
files=sorted((x for x in R.rglob('*') if (x.is_file() or x.is_symlink()) and valid(x)),key=lambda x:x.relative_to(R).as_posix())
results=sorted((x for x in (R/'results').rglob('*') if x.is_file()),key=lambda x:x.relative_to(R).as_posix())
(R/'evidence'/'OUTPUT_SHA256.json').write_text(json.dumps({'schema':'REI_F4_FS2010_FULL193_GENERATED_SHA_V1','outputs':[rec(p) for p in results]},indent=2,sort_keys=True)+'\n')
files.append(R/'evidence'/'OUTPUT_SHA256.json');files.sort(key=lambda x:x.relative_to(R).as_posix())
(R/'MANIFEST.json').write_text(json.dumps({'schema':'REI_F4_FS2010_FULL193_SOURCE_INCLUSIVE_V1','entries':[rec(p) for p in files]},indent=2,sort_keys=True)+'\n')
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files+[R/'MANIFEST.json']:
  zi=zipfile.ZipInfo(R.name+'/'+p.relative_to(R).as_posix(),date_time=(2026,10,31,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=(0o100644<<16)
  z.writestr(zi,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
with zipfile.ZipFile(OUT) as z:assert z.testzip() is None
print(json.dumps({'name':str(OUT),'size_bytes':OUT.stat().st_size,'sha256':sha(OUT),'manifest_entries':len(files),'results':len(results)},indent=2))
