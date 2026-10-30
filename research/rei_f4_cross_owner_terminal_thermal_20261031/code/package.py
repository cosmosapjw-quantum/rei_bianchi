"""Create exact SHA manifests and source-inclusive lightweight deterministic ZIP."""
import hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
OUT=R.parent/'REI_F4_CROSS_OWNER_TERMINAL_THERMAL_20261031_FULL.zip'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def metadata(p):return {'sha256':sha(p),'size':p.stat().st_size}
outputs=sorted((R/'results').glob('*'))
res={str(p.relative_to(R)):metadata(p) for p in outputs if p.is_file()}
(R/'OUTPUT_SHA256.json').write_text(json.dumps({'schema':'REI_F4_OUTPUT_SHA_V1','files':res},indent=2,sort_keys=True)+'\n')
files=sorted(p for p in R.rglob('*') if p.is_file() and p.name not in ('MANIFEST.json',) and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts)
manifest={str(p.relative_to(R)):metadata(p) for p in files}
(R/'MANIFEST.json').write_text(json.dumps({'schema':'REI_F4_SOURCE_MASTER_SHA_V1','files':manifest},indent=2,sort_keys=True)+'\n')
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
 for p in sorted(p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts):
  name='REI_F4_CROSS_OWNER_TERMINAL_THERMAL_20261031/'+str(p.relative_to(R))
  zi=zipfile.ZipInfo(name,(2026,10,31,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=(0o644<<16)
  z.writestr(zi,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=8)
print('ZIP',OUT,OUT.stat().st_size,sha(OUT),'members',len(zipfile.ZipFile(OUT).namelist()))