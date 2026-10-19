"""Create-only RUN09 recovery archive; external receipts are not recursively sealed."""
from pathlib import Path
import hashlib, io, json, os, tarfile, zipfile
R=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('REI_DELIVERY_DIR','/mnt/data'))
name='REI_ATOMIC_NUCLEAR_RUN09_SOURCE_SUPPORT_20261017.zip'
archive=OUT/name
if archive.exists(): raise FileExistsError(f'Final archive already exists: {archive}')
exclude={'.git','target','__pycache__','replay'}
files=[]
for p in sorted(R.rglob('*')):
    rel=p.relative_to(R)
    if any(x in exclude for x in rel.parts): continue
    if p.is_symlink(): raise ValueError(f'Symlink excluded from recovery: {rel}')
    if p.is_file() and rel.as_posix()!='SHA256SUMS.txt':
        if p.suffix.lower() in {'.ttf','.otf','.woff','.woff2','.pem','.key'}:
            raise ValueError(f'Unexpected sensitive/binary asset: {rel}')
        files.append((p,rel.as_posix()))
manifest=''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+rel+'\n' for p,rel in files)
(R/'SHA256SUMS.txt').write_text(manifest)
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p,rel in files: z.write(p,rel)
    z.write(R/'SHA256SUMS.txt','SHA256SUMS.txt')
b=archive.read_bytes(); sha=hashlib.sha256(b).hexdigest()
OUT.joinpath(name+'.sha256').write_text(f'{sha}  {name}\n')
chunk_hashes=b''.join(hashlib.sha256(b[i:i+4194304]).digest() for i in range(0,len(b),4194304))
identity={'name':name,'bytes':len(b),'sha256':sha,'entries':len(files)+1,'payload_hashes':len(files),
 'git_blob_sha1':hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest(),
 'dropbox_content_hash':hashlib.sha256(chunk_hashes).hexdigest()}
OUT.joinpath('rei_run09/ARCHIVE_IDENTITY.json').write_text(json.dumps(identity,indent=2)+'\n')
print(json.dumps(identity,indent=2))
