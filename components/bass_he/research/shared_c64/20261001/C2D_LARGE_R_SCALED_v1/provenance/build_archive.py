"""Create and verify the complete immutable research archive once."""
import hashlib,io,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from mpi_batch import atomic_create,json_bytes
paths=[p for p in sorted(ROOT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and not p.name.startswith('.pending-') and p.name!='MANIFEST.json']
if any(p.is_symlink() for p in paths):raise RuntimeError('symlink payload rejected')
records={str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths}
manifest={'schema':1,'scope':'every archive payload except this manifest','files':records}
atomic_create(ROOT/'MANIFEST.json',json_bytes(manifest));paths.append(ROOT/'MANIFEST.json')
target=ROOT.with_suffix('.zip');buffer=io.BytesIO()
with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in paths:z.writestr(ROOT.name+'/'+str(p.relative_to(ROOT)),p.read_bytes())
atomic_create(target,buffer.getvalue());sha=hashlib.sha256(target.read_bytes()).hexdigest()
with zipfile.ZipFile(target) as z:
 if z.testzip() is not None:raise RuntimeError('archive CRC failure')
 if len(z.namelist())!=len(records)+1 or len(set(z.namelist()))!=len(z.namelist()):raise RuntimeError('archive member mismatch')
 for name,expected in records.items():
  raw=z.read(ROOT.name+'/'+name)
  if len(raw)!=expected['bytes'] or hashlib.sha256(raw).hexdigest()!=expected['sha256']:raise RuntimeError('archive payload mismatch: '+name)
atomic_create(target.with_suffix('.zip.sha256'),(sha+'  '+target.name+'\n').encode())
validation={'archive_path':str(target),'bytes':target.stat().st_size,'sha256':sha,'crc':'PASS','all_manifest_payloads':'PASS','payload_count':len(records),'member_count':len(records)+1,'scope':'local archive bytes; provider ACK is not a restored-download verification'}
atomic_create(ROOT.parent/'C2D_ARTIFACT_VALIDATION.json',json_bytes(validation));print(json.dumps(validation,indent=2))
