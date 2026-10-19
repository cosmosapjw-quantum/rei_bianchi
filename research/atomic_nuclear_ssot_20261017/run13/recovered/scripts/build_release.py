"""Create the local recovery ZIP, excluding compiler caches and mutable replay."""
from pathlib import Path
import json,hashlib,zipfile,tarfile,io,base64
R=Path(__file__).resolve().parents[1];OUT=Path('/mnt/data');name='REI_ATOMIC_NUCLEAR_RUN08_RETARDED_JOINT_20261017.zip'
blocked={'.git','target','__pycache__','replay'}
items=[p for p in sorted(R.rglob('*')) if p.is_file() and not blocked.intersection(p.relative_to(R).parts) and p.name!='SHA256SUMS.txt' and p.suffix not in {'.pyc'}]
(R/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(R))+'\n' for p in items))
with zipfile.ZipFile(OUT/name,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for p in items+[R/'SHA256SUMS.txt']:z.write(p,str(p.relative_to(R)))
b=(OUT/name).read_bytes();sha=hashlib.sha256(b).hexdigest();drop=hashlib.sha256(b''.join(hashlib.sha256(b[i:i+4194304]).digest()for i in range(0,len(b),4194304))).hexdigest()
(OUT/(name+'.sha256')).write_text(sha+'  '+name+'\n')
meta={'archive':name,'bytes':len(b),'sha256':sha,'dropbox_content_hash':drop,'entries':len(items)+1,'payload_hashes':len(items)}
(OUT/'rei_run08/ARCHIVE_IDENTITY.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta,indent=2))
